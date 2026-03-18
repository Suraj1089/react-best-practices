# Concurrent Features & Transitions

## rerender-transitions

### Why it matters
React 18 introduced concurrent rendering. Normally, every state update is "urgent"—it interrupts the browser, freezes the UI until rendering completes, and explicitly blocks user input. `startTransition` or `useTransition` allows you to mark specific state updates as "non-urgent". React will begin rendering the update in the background, but if the user interacts (like typing in an input), React will instantaneously abandon the background render to handle the keystroke smoothly, natively eliminating input lag.

### ❌ Wrong — blocking the main thread natively
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    // 🚨 BOTH are urgent! Typing feels horribly sluggish
    // because rendering 1000 results blocks the keystroke.
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
    // 🛠️ Urgent: The controlled input strictly updates instantly
    setQuery(e.target.value); 
    
    // 🛠️ Non-urgent: The heavy list rendering happens in the background
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
While `useTransition` requires you to have direct structural access to the exact `setState` function to wrap it, `useDeferredValue` is strictly employed when you strictly receive a prop from above and you have completely zero control over how it is fundamentally set. It returns a explicitly delayed computationally "lagging" version of the prop, allowing the component to render the old value fluidly while React computes the profoundly new value deeply in the background.

### ✅ Pattern — deferring an incoming prop
```jsx
// 🛠️ SearchResults doesn't control `query`, it just receives it.
function SearchResults({ query }) {
  // 🛠️ React will instantly render with the OLD deferredQuery while it
  // computationally figures out the intense heavy rendering for the NEW query.
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  // Render the heavy list strictly using the lagging deferred value
  const results = highlyExpensiveFilter(data, deferredQuery);

  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      <HeavyResultGrid items={results} />
    </div>
  );
}
```

### When to use which?
- If you inherently have the strict `setState` access → Always prefer `useTransition`.
- If you strictly literally only have the raw prop variable → `useDeferredValue`.

---
**Related rules:** `rerender-state-change`, `rendering-usetransition-loading`
