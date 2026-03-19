# Closures & stale state

## closure-understand

### Why it matters
When a function is created in JavaScript, it captures a snapshot of all the variables in its surrounding scope. This is a **closure**. In React, every render creates new function instances that close over the state and prop values from *that specific render*. The function keeps those values even after the render is done. Understanding this is key to debugging state issues in React.

---

## closure-stale-callback

### Why it matters
If a function is cached — via `useCallback` with an empty dep array, stored in a ref at init time, or passed to a `useEffect` that doesn't list it as a dependency — it captures the values from the render where it was created. Later state changes are invisible to it. This is a **stale closure**: your app silently uses outdated values.

### ❌ Wrong — empty dependency array freezes state
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // BUG: Empty deps mean `query` is always '' inside this callback
  const onSubmit = useCallback((e) => {
    e.preventDefault();
    trackAnalytics('search_submitted', { query }); // always logs ''
    api.search(query); 
  }, []);

  return (
    <form onSubmit={onSubmit}>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button type="submit">Search</button>
    </form>
  );
}
```

### ✅ Right — include all dependencies
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // Recreated whenever `query` changes, so it always has the current value
  const onSubmit = useCallback((e) => {
    e.preventDefault();
    trackAnalytics('search_submitted', { query });
    api.search(query);
  }, [query]); 

  return (/* ... */);
}
```

---

## closure-ref-trick

### Why it matters
Sometimes you need a callback that is **reference-stable** (same function identity across renders, so memoized children don't re-render) but also reads the **latest** state when called. These goals conflict — unless you use a ref to bridge the gap.

### ✅ Pattern: stable wrapper + mutable ref
```jsx
function DataGrid({ onSelectionChange }) {
  const [selectedIds, setSelectedIds] = useState(new Set());

  // 1. Ref holds the latest callback
  const onSelectionChangeRef = useRef(onSelectionChange);

  // 2. Keep it in sync after every render
  useLayoutEffect(() => {
    onSelectionChangeRef.current = onSelectionChange;
  });

  // 3. Stable function that delegates to whatever's in the ref
  const handleSelect = useCallback((id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      
      // Always calls the latest onSelectionChange
      onSelectionChangeRef.current?.(next); 
      return next;
    });
  }, []); // Empty deps = same reference forever

  return <HeavyRowList onSelect={handleSelect} />;
}
```

### Notes
- The ref is updated in `useLayoutEffect`, which runs synchronously after render.
- The wrapper function reads `.current` at call time, so it always gets the latest logic.
- This is the pattern behind the experimental `useEffectEvent` RFC.

---
**Related rules:** `memo-react-memo`, `ref-no-overuse`
