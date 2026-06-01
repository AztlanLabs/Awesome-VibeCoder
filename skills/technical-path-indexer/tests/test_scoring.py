from __future__ import annotations

import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from python.models import DirectoryNode, LinkedFileEdge, ReferenceEdge, RouteNode
from python.scoring import compute_path_scores


class ScoringTests(unittest.TestCase):
    def test_path_scores_use_path_level_evidence_instead_of_full_file_score_rollups(self) -> None:
        directories = [
            DirectoryNode(path=".", file_count=1, direct_file_count=1, total_size=10, entrypoint_count=0, config_count=0),
            DirectoryNode(path="src", file_count=2, direct_file_count=2, total_size=20, entrypoint_count=1, config_count=0),
            DirectoryNode(path="docs", file_count=1, direct_file_count=1, total_size=5, entrypoint_count=0, config_count=0),
        ]
        routes = [RouteNode(source="src/app/page.tsx", route="/app", kind="filesystem-nextjs-app")]
        references = [
            ReferenceEdge(source="src/app/page.tsx", target="src/lib/util.ts", kind="import"),
            ReferenceEdge(source="docs/readme.md", target="src/lib/util.ts", kind="markdown-link"),
        ]
        linked_files = [LinkedFileEdge(left="src/app/page.tsx", right="src/app/page.css", rule="same-stem", evidence="fixture")]

        scores = {score.path: score for score in compute_path_scores(directories, routes, references, linked_files)}

        self.assertIn("route_ownership", scores["src"].reasons)
        self.assertIn("linked_files", scores["src"].reasons)
        self.assertNotIn("linked_files", scores["docs"].reasons)


if __name__ == "__main__":
    unittest.main()