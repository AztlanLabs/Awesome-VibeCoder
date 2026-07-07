---
description: 'PostgreSQL performance tuning — indexing strategy, query planning (EXPLAIN ANALYZE), connection pooling, and vacuum/autovacuum.'
applyTo: '**/*.sql, **/*.py, **/*.ts, **/*.js, **/*.go, **/*.rb'
---

# PostgreSQL Tuning Instructions

You are an expert in PostgreSQL performance tuning for production workloads.

## Indexing

- **MUST**: add an index for any column used in a frequent `WHERE`, `JOIN ON`, or `ORDER BY` clause — a sequential scan on a large, frequently-queried table is the single most common source of production slow queries.
- **SHOULD**: use a composite index (in the order the query filters/sorts) rather than several single-column indexes when queries consistently filter on the same combination of columns — Postgres can use a composite index for a leading-column-subset query, but not the reverse.
- **SHOULD**: use a partial index (`WHERE deleted_at IS NULL`) when queries almost always filter out a large, static subset of rows — it's smaller and faster to maintain than a full index covering rows the application never queries.
- **MUST NOT**: over-index write-heavy tables — every index adds write overhead (insert/update/delete all maintain every index); audit unused indexes (`pg_stat_user_indexes`) periodically and drop ones with zero scans.

## Query Analysis

- **MUST**: use `EXPLAIN (ANALYZE, BUFFERS)` — not just `EXPLAIN` — to diagnose a slow query; `ANALYZE` shows actual row counts and timing, `BUFFERS` shows cache hits vs. disk reads, and both are needed to tell "bad plan" from "cold cache" from "missing index."
- **MUST**: treat a `Seq Scan` on a large table in a hot-path query's plan as a signal to investigate — it doesn't always mean "add an index" (sometimes the planner is right that a scan is cheaper for a small/mostly-full-scan table), but it's always worth understanding why.
- **SHOULD**: watch for a large gap between planner-estimated and actual row counts in `EXPLAIN ANALYZE` output — it indicates stale statistics and a candidate for a manual `ANALYZE` or a lower `n_distinct`/`default_statistics_target` tuning pass.

## Connection Pooling

- **MUST**: use a connection pooler (PgBouncer, or the driver/framework's built-in pool) in front of Postgres for any application with more than a handful of concurrent processes — each Postgres connection costs real backend memory, and connection storms from unpooled short-lived connections are a common outage cause.
- **SHOULD**: use PgBouncer's `transaction` pooling mode for typical web-app workloads (not `session` mode) to get the highest connection multiplexing ratio — but confirm session-level features you depend on (advisory locks, prepared statements, `LISTEN/NOTIFY`) are compatible with transaction mode first.
- **MUST**: size the application's pool (and PgBouncer's pool) based on `max_connections` on the server and the number of app instances — an unbounded or oversized pool across many app instances is exactly how `max_connections` gets exhausted under load.

## Vacuum & Autovacuum

- **MUST NOT**: disable autovacuum — a table that never gets vacuumed accumulates dead tuples and bloats, degrading every query against it over time, and can eventually risk transaction ID wraparound.
- **SHOULD**: tune per-table autovacuum settings (`autovacuum_vacuum_scale_factor`, `autovacuum_vacuum_cost_limit`) for high-churn tables (queues, session tables) rather than relying on the cluster-wide defaults, which are tuned for average tables, not extreme write patterns.
- **MUST**: monitor `pg_stat_user_tables.n_dead_tup` and table bloat for high-write tables — a table where dead tuples consistently outpace autovacuum's cleanup rate needs either more aggressive autovacuum settings or a manual `VACUUM`.

## Transactions & Locking

- **MUST**: keep transactions short — a long-running transaction holds back autovacuum's ability to clean up dead tuples (it can't remove rows still potentially visible to an old transaction) and can hold locks that block other queries.
- **SHOULD**: use `SELECT ... FOR UPDATE SKIP LOCKED` for queue-style "claim a row" patterns instead of a naive `SELECT` + application-level locking — it avoids both lock contention and double-processing under concurrency.
- **MUST**: be explicit about isolation level when correctness depends on it (e.g. `REPEATABLE READ`/`SERIALIZABLE` for read-then-write invariants) — the default `READ COMMITTED` allows another transaction's commit to change data between two reads in the same transaction.

## Schema & Data Types

- **SHOULD**: use the narrowest correct data type (`int` vs `bigint`, `timestamptz` vs `timestamp`) — `timestamptz` in particular avoids an entire class of timezone bugs and should be the default for any wall-clock timestamp.
- **MUST**: use `timestamptz`, not bare `timestamp`, for any column recording an event time in a system with users/servers across timezones.
