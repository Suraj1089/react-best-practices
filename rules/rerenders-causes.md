# Re-render causes

## rerender-state-change

### Why it matters
Calling `setState` or `dispatch` marks a component as dirty and schedules a re-render. That re-render cascades **down** the tree — every child re-renders too, unless stopped by a `React.memo` boundary.

```jsx
function MetricsDashboard() {
  const [toggle, setToggle] = useState(false);
  
  return (
    <div className="dashboard">
      <button onClick={() => setToggle(!toggle)}>Refresh Cache</button>
      {/* This child re-renders even though it takes zero props */}
      <HighlyComplicatedMetricOverviewGraph /> 
    </div>
  );
}
```

---

## rerender-parent

### Why it matters
When a parent re-renders, **every child re-renders** by default — regardless of whether any props actually changed. React doesn't automatically diff props. It just re-runs the child function. The only way to stop the cascade is `React.memo`.

---

## rerender-context

### Why it matters
When you call `useContext(SomeContext)`, that component re-renders whenever the context's `value` changes — even if you only read a small piece of a large context object.

### Ways to reduce unnecessary context renders
1. **Split contexts**: Separate unrelated data into different contexts (see `context-splitting`).
2. **Memoize the value**: Wrap the context `value` object in `useMemo` inside the provider.
3. **Use a state manager**: Libraries like Zustand or Jotai give you granular subscriptions without the re-render blast radius of Context.

---

## rerender-props-myth

### Why it matters
The most common React misconception: *"If my props don't change, my component won't re-render."*

**This is wrong.** React doesn't watch or diff props automatically. A component re-renders because its **parent re-rendered** or its own **state changed**. Props are just arguments passed into the function call.

The only exception is `React.memo`, which intercepts the re-render, checks old props against new props (shallow equality), and bails out if they match.

### When does a component re-render?

| Trigger | Re-renders? |
|---|---|
| `setState` called inside the component | Yes |
| Parent re-renders | Yes (always, by default) |
| Context value changes | Yes (if subscribed via `useContext`) |
| Props unchanged, parent didn't re-render | No |
| `React.memo` + unchanged props | No (skipped) |
| `React.memo` + changed props | Yes |

---
**Related rules:** `memo-react-memo`, `compose-children-prop`
