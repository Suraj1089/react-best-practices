# Concurrent features & transitions

## rerender-transitions

### Why it matters
React 18 added concurrent rendering. By default, every `setState` call is urgent — React blocks the main thread until it finishes rendering, which locks up user input. `useTransition` lets you mark a state update as non-urgent. React will start rendering it in the background, but if the user types or clicks, React drops that background work to handle the interaction first. The result: no input lag.

### ❌ Wrong — blocking the main thread
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    // Both updates are urgent. Rendering 1000 results
    // blocks the keystroke, so typing feels sluggish.
    setQuery(e.target.value); 
    setResults(heavyFilter(data, e.target.value)); 
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      <ExpensiveList items={results} />
    </>
  );
}
```

### ✅ Right — prioritize typing over the heavy render
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // Urgent: the input updates immediately
    setQuery(e.target.value); 
    
    // Non-urgent: the list re-render happens in the background
    startTransition(() => {
      setResults(heavyFilter(data, e.target.value)); 
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <span className="spinner" />}
      <ExpensiveList items={results} />
    </>
  );
}
```

---

## rerender-use-deferred-value

### Why it matters
`useTransition` requires direct access to the `setState` call so you can wrap it. `useDeferredValue` is for when you receive a prop from a parent and have no control over how it's set. It returns a "lagging" version of the value — the component keeps showing the old value while React computes the new one in the background.

### ✅ Pattern — deferring an incoming prop
```jsx
// SearchResults doesn't control `query`, it just receives it.
function SearchResults({ query }) {
  // React renders with the old deferredQuery while computing
  // the new one in the background
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  const results = highlyExpensiveFilter(data, deferredQuery);

  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      <HeavyResultGrid items={results} />
    </div>
  );
}
```

### When to use which?
- You have the `setState` call → use `useTransition`.
- You only have the prop → use `useDeferredValue`.

---
**Related rules:** `rerender-state-change`, `rendering-usetransition-loading`
