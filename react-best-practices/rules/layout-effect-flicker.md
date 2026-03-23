# DOM sync & effects

## effect-layout-flicker

### Why it matters
`useEffect` runs **after** the browser has painted. If your effect measures the DOM (say, getting a container's width) and then calls `setState` based on that measurement, you get a double render. The user sees:

1. First paint — the element appears at position 0,0 (or some default).
2. The effect fires, updates state, and triggers a re-render.
3. Second paint — the element jumps to the correct position.

That jump is visible as a flash or flicker. For layout measurements that determine positioning, use `useLayoutEffect` instead — it runs **after** React updates the DOM but **before** the browser paints, so the user only ever sees the final result.

### ❌ Wrong — flicker with useEffect
```jsx
function Tooltip({ targetRect, children }) {
  const tooltipRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    // Runs AFTER paint: tooltip flashes at 0,0 before jumping to the right spot
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
    // Runs BEFORE paint: the user only sees the final position
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
| Fetching data, setting up subscriptions, logging | `useEffect` |
| Measuring DOM nodes to adjust positioning before the user sees it | `useLayoutEffect` |
| Starting animations that must sync with the initial paint | `useLayoutEffect` |
| Anything that doesn't visibly change the DOM | `useEffect` |

---

## effect-ssr-ready

### Why it matters
`useLayoutEffect` doesn't run on the server (Next.js, Remix). React emits a warning, and the measurement never happens during server rendering. This creates a hydration mismatch between the server HTML and the client's first render.

### ✅ Pattern — isReady gate for SSR
```jsx
function ResponsiveNav({ items }) {
  const navRef = useRef(null);
  const [isReady, setIsReady] = useState(false); // false on the server
  const [visibleCount, setVisibleCount] = useState(items.length);

  useLayoutEffect(() => {
    // Only runs on the client
    const width = navRef.current.getBoundingClientRect().width;
    setVisibleCount(calculateFit(width, items));
    setIsReady(true);
  }, [items]);

  if (!isReady) {
    return <nav ref={navRef} style={{ visibility: 'hidden' }}>{items.map(renderItem)}</nav>;
  }

  return <nav ref={navRef}>{items.slice(0, visibleCount).map(renderItem)}</nav>;
}
```

### Alternative
The `useIsomorphicLayoutEffect` hook from `usehooks-ts` or `react-use` automatically falls back to `useEffect` on the server, which suppresses the React SSR warning while keeping the synchronous behavior on the client.

---
**Related rules:** `ref-dom-access`
