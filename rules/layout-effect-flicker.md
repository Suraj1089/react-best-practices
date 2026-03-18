# DOM Sync & Effects

## effect-layout-flicker

### Why it matters
`useEffect` runs **asynchronously after** the browser has painted the screen. If your effect measures the DOM (e.g., gets the width of a container) and then triggers a state update based on that measurement, you are effectively forcing a double-render. The user will physically see:
1. First paint — the incorrect or unsized layout flashes on screen.
2. State update triggers a re-render.
3. Second paint — the corrected layout snaps into place.

This is visible as a **flash or flicker** and looks extremely unpolished. For DOM measurements that dictate layout, you must use `useLayoutEffect` — it runs **synchronously immediately after React mutates the DOM but strictly before the browser is allowed to paint**, completely eliminating the flicker.

### ❌ Wrong — flicker with useEffect
```jsx
function Tooltip({ targetRect, children }) {
  const tooltipRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    // 🐛 RUNS AFTER PAINT: User sees tooltip flash at 0,0 before moving!
    const rect = tooltipRef.current.getBoundingClientRect();
    setPosition({
      top: targetRect.bottom + 8,
      left: targetRect.left + (targetRect.width / 2) - (rect.width / 2)
    });
  }, [targetRect]);

  return (
    <div ref={tooltipRef} style={{ ...position, position: 'absolute' }}>
      {children}
    </div>
  );
}
```

### ✅ Right — no flicker with useLayoutEffect
```jsx
function Tooltip({ targetRect, children }) {
  const tooltipRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    // 🛠️ RUNS BEFORE PAINT: User only ever sees the final correctly calculated position
    const rect = tooltipRef.current.getBoundingClientRect();
    setPosition({
      top: targetRect.bottom + 8,
      left: targetRect.left + (targetRect.width / 2) - (rect.width / 2)
    });
  }, [targetRect]);

  return (/* ... */);
}
```

### When to use which
| Scenario | Hook |
|---|---|
| Fetching API data, setting up subscriptions, logging | `useEffect` |
| Measuring specific DOM nodes to adjust layout before showing the user | `useLayoutEffect` |
| Firing imperative animations that must start in exact sync with UI appearance | `useLayoutEffect` |
| Literally anything else that doesn't visibly mutate the DOM | `useEffect` |

---

## effect-ssr-ready

### Why it matters
`useLayoutEffect` does not run on the server during SSR (Next.js, Remix). Because it can't run on the server, React will emit a warning, and the layout measurement simply won't happen during the server render phase. This guarantees a mismatch between the server-rendered HTML and the first pass of the client HTML (hydration mismatch). 

### ✅ Pattern — isReady hydration gate for SSR
```jsx
function ResponsiveNav({ items }) {
  const navRef = useRef(null);
  const [isReady, setIsReady] = useState(false); // starts false on server
  const [visibleCount, setVisibleCount] = useState(items.length);

  useLayoutEffect(() => {
    // Now safe. Client-only execution.
    const width = navRef.current.getBoundingClientRect().width;
    setVisibleCount(calculateFit(width, items));
    setIsReady(true);
  }, [items]);

  // Server render strategy: hiding content completely (or rendering a skeleton)
  if (!isReady) {
    return <nav ref={navRef} style={{ visibility: 'hidden' }}>{items.map(renderItem)}</nav>;
  }

  return <nav ref={navRef}>{items.slice(0, visibleCount).map(renderItem)}</nav>;
}
```

### Alternative
Use `usehooks-ts` or the `react-use` library's `useIsomorphicLayoutEffect` hook, which automatically falls back to `useEffect` strictly on the server to simply suppress the annoying React SSR warning, while keeping the correct synchronous behavior in the client browser. 

---
**Related rules:** `ref-dom-access`
