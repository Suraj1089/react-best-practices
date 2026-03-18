# Re-render Causes

## rerender-state-change

### Why it matters
Executing a `setState` or `dispatch` call flags a component immediately as "dirty" and dynamically schedules a broad re-render execution. Fundamentally, this re-render violently cascades **perpetually down** the component tree — virtually every single descended child embedded within that parent aggressively re-renders, recursively executing endlessly, strictly unless mechanically halted via a `React.memo` barrier.

```jsx
function MetricsDashboard() {
  const [toggle, setToggle] = useState(false); // ← Root State Source
  
  return (
    <div className="dashboard">
      <button onClick={() => setToggle(!toggle)}>Refresh Cache</button>
      {/* 🚨 This child component inexplicably re-renders even though it takes ZERO props */}
      <HighlyComplicatedMetricOverviewGraph /> 
    </div>
  );
}
```

---

## rerender-parent

### Why it matters
React's core default heuristic is unforgiving: strictly if a parent component triggers a re-render sequence, **every nested child absolutely re-renders** — wildly regardless of whether any of their actual explicit props structurally changed. React simply does not intelligently mathematically diff or monitor props for superficial changes automatically; it brutally re-evaluates the entire tree matrix. 

**The singular native React strategy to intercept this endless chain reaction is strictly wrapping the downstream child with `React.memo`.**

---

## rerender-context

### Why it matters
When you strictly subscribe to a Provider via `useContext(ThemeContext)`, that specific consumer component strictly re-renders every single time the precise object identity mathematically bound to the Context's exact **value** changes — even if the subscribing component natively only consumes a granularly unchanged tiny subset of that massive context object.

### Mitigation strategies
1. **Architectural Splitting:** Split large monolithic cohesive contexts strictly into tiny domain-focused providers (e.g. `ThemeContext`, `AuthContext`, `ModalContext`). (See `context-splitting`).
2. **Provider Memoization:** Rigorously wrap the exact context `value` literal object structurally with `useMemo` specifically inside the overarching Provider component to stabilize its reference cleanly.
3. **Atomic State Managers:** Adopt hyper-granular subscribing libraries implicitly like `Zustand` or `Jotai` which bypass standard Context structural limitations completely.

---

## rerender-props-myth

### Why it matters
The absolute most universally held misconception among developers: *"If my component's props don't actively change, the component natively won't re-render."*

**This is deeply factually false.** React does not watch or track props dynamically. A standard component cleanly re-renders solely because its explicit **parent** strictly re-rendered passing newly instantiated references, or its own internal local **state** forcefully changed. Props are frankly just an argument payload mechanically passed rapidly into the fresh execution function call.

The singular conditional exception is literally when a component is strictly wrapped in a `React.memo` barrier — which explicitly intercepts the flow, comprehensively checks the new props violently against the old props structurally (shallow equal), and definitively bails out of rendering if identically matched.

### Summary Reality Matrix

| Trigger Phase | Causes React to Re-render? |
|---|---|
| Native `setState` hook executed in component | ✅ Resoundingly Yes |
| Parent organically re-renders | ✅ Yes (Brutally, always, natively by default) |
| Active Context Provider value structurally changes | ✅ Yes (If explicitly subscribed via useContext) |
| Prop arguments strictly completely identical | ❌ No (But only assuming the parent itself did not re-render) |
| `React.memo` wrapper + completely structurally identical props | ❌ Cleanly Native Bailout (No) |
| `React.memo` wrapper + mutated props matrix | ✅ Resoundingly Yes |

---
**Related rules:** `memo-react-memo`, `compose-children-prop`
