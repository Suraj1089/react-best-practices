# Closures & Stale State

## closure-understand

### Why it matters
When a function is created in JavaScript, it forms a **closure** — a snapshot of all the variables visible in its surrounding scope at that moment. The function carries this snapshot with it forever. In React, because every render is mathematically like a separate frame in a movie, it creates new function instances that close over the specific state and prop values of *that exact render cycle*. Understanding this is the key to mastering React state.

---

## closure-stale-callback

### Why it matters
If a function is cached (via `useCallback` with an empty dependency array, or stored in a `ref` once at initialization, or passed to a `useEffect` that doesn't track it), it freezes the values from the very first render in which it was created. Future state and prop updates are entirely invisible to this cached function — it becomes a **stale closure**, causing subtle and frustrating bugs where your app "forgets" recent user inputs.

### ❌ Wrong — empty dependency array leads to stale state
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // 🐛 BUG: Empty deps mean `query` is forever trapped as ''
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

### ✅ Right — declare all reactive dependencies
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // 🛠️ FIX: Re-create the callback whenever `query` changes
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
Sometimes you hit a wall: you need a function that is **completely stable** (has the same reference across every render so a memoized child component doesn't unnecessarily re-render) **but** it still needs to read the absolute latest state when invoked. These two goals directly conflict — unless you use a mutable `ref` as an escape hatch to bridge the gap.

### ✅ Pattern: The "Latest Ref" Pattern (Stable Wrapper + Mutable Ref)
```jsx
function DataGrid({ onSelectionChange }) {
  const [selectedIds, setSelectedIds] = useState(new Set());

  // 1. Ref acts as a mutable container holding the absolute latest callback
  const onSelectionChangeRef = useRef(onSelectionChange);

  // 2. Keep the ref perfectly in sync with every render
  // useLayoutEffect ensures it updates before paint
  useLayoutEffect(() => {
    onSelectionChangeRef.current = onSelectionChange;
  });

  // 3. Expose a completely stable function that delegates to whatever is in the ref
  const handleSelect = useCallback((id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      
      // ✅ Always calls the freshest onSelectionChange from props!
      onSelectionChangeRef.current?.(next); 
      return next;
    });
  }, []); // 🚫 Empty deps = same reference forever!

  // Now you can pass handleSelect down to heavy rows without breaking React.memo
  return <HeavyRowList onSelect={handleSelect} />;
}
```

### Notes
- `callbackRef.current` is mutated inside `useLayoutEffect`, which runs synchronously after every render.
- The wrapper function calls `.current()`, so it dynamically looks up the latest logic right at the moment of execution.
- This is the explicit pattern behind the experimental `useEffectEvent` (previously `useEvent`) RFC coming to React.

---
**Related rules:** `memo-react-memo`, `ref-no-overuse`
