export type Counter = {
  readonly count: number;
  readonly doubled: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
};

export function createCounter(initial = 0): Counter {
  let count = $state(initial);
  let doubled = $derived(count * 2);

  $effect(() => {
    console.log('[counter] count =', count, 'doubled =', doubled);
  });

  return {
    get count() {
      return count;
    },
    get doubled() {
      return doubled;
    },
    increment() {
      count += 1;
    },
    decrement() {
      count -= 1;
    },
    reset() {
      count = 0;
    },
  };
}

export function demonstrate(): void {
  const counter = createCounter(2);
  counter.increment();
  counter.increment();
  console.assert(counter.count === 4, 'expected 4');
  console.assert(counter.doubled === 8, 'expected 8');
  counter.reset();
  console.assert(counter.count === 0, 'expected reset to 0');
}