# Refs & Imperative APIs

## ref-dom-access

### Why it matters
`useRef` instantiates a persistent, mutable object container (`{ current: initialValue }`) that seamlessly persists completely intact across the entire lifespan of a component without ever violently triggering a re-render when mutated. Passing a `ref` directly to a JSX intrinsic element seamlessly hands you the raw underlying browser DOM node.

### ✅ Basic DOM access
```jsx
function SearchBox() {
  const searchInputRef = useRef(null);

  const handleGlobalShortcut = () => {
    // 🛠️ Raw interaction bypassing React's render cycle
    searchInputRef.current?.focus(); 
  };

  return (
    <div className="search-container">
      <input 
        ref={searchInputRef} 
        type="search" 
        placeholder="Cmd+K to search" 
      />
      <button onClick={handleGlobalShortcut}>Focus field</button>
    </div>
  );
}
```

### Valid Uses for Raw Refs
- Imperative interactions: `.focus()`, `.blur()`, `.click()`, or scrolling via `.scrollIntoView()`.
- Imperative layout parsing: `.getBoundingClientRect()` or retrieving exact DOM geometric offsets.
- Synchronous media control: Video `.play()` or `.pause()`.
- Bridging non-React code boundaries like instantiating WebGL canvases or heavy D3.js charting wrappers.

---

## ref-forward

### Why it matters
React intentionally protects component encapsulation. By default, you absolutely cannot pass a `ref` prop down into a custom function component — React forcibly strips it to prevent abusive external coupling. For a parent component to rightfully interact with an underlying DOM node strictly controlled by a child, the child inherently needs to grant explicit permission using `forwardRef`.

### ✅ Using forwardRef
```jsx
// 🛠️ The child deliberately intercepts the 'ref' and wires it down
const FancyInput = forwardRef(function FancyInput(props, ref) {
  return (
    <div className="fancy-wrapper">
      <input ref={ref} className="fancy-internal-input" {...props} />
    </div>
  );
});

// Parent retains authoritarian access
function CommandPalette() {
  const commandRef = useRef(null);
  
  useEffect(() => {
    commandRef.current?.focus(); // Focuses the internal `input`, not the `div` wrapper
  }, []);

  return <FancyInput ref={commandRef} placeholder="Enter command" />;
}
```

> **Note on React 19:** In React 19+, `ref` is fully unleashed as a standard, regular prop argument — `forwardRef` is formally deprecated and no longer structurally required. You simply access it via `({ ref, children })`. 

---

## ref-imperative-handle

### Why it matters
Directly handing out a raw DOM node ref blindly grants the parent chaotic, totalizing access — it can aggressively call hazardous DOM methods, forcefully mutate classNames, or hijack styles. `useImperativeHandle` lets you artfully restrict and govern the exact API surface intentionally exposed back to the parent component.

### ✅ Controlled API surface
```jsx
const SecureTextInput = forwardRef(function SecureTextInput(props, ref) {
  const internalInputRef = useRef(null);

  // 🛠️ Only hand these specific safe actions directly to the parent
  useImperativeHandle(ref, () => ({
    focus() {
      internalInputRef.current?.focus();
    },
    triggerJiggleAnimation() {
      internalInputRef.current?.classList.add('error-jiggle');
      setTimeout(() => internalInputRef.current?.classList.remove('error-jiggle'), 500);
    }
    // 🛡️ The parent has absolutely zero access to .value, .style, or .parentNode
  }));

  return <input ref={internalInputRef} type="password" {...props} />;
});
```

---

## ref-no-overuse

### Why it matters
React is explicitly built strictly around **declarative** state modeling — your code rigorously describes identically what the UI state should look like uniformly given the current data, and React calculates mathematically how to alter the DOM globally to match it. Refs are an **emergency escape hatch** meant strictly for interactions React simply cannot fluently accomplish declaratively.

### 🚫 Prefer Declarative Data Flows
| Imperative (Escape Hatch Nightmare) | Declarative (React Mastery) |
|---|---|
| `modalRef.current.style.display = 'block'` | `isOpen && <Modal />` or `className={isOpen ? 'block' : 'hidden'}` |
| `inputRef.current.value = 'John'` | `<input value={name} onChange={...} />` |
| `videoRef.current.play()` | Define standard components using a `isPlaying={true}` abstracted wrapper |

Refs are totally valid and explicitly encouraged for: strict focus management, intricate scroll-positioning math, WebGL engines, tight animation sequencing, and bridging vanilla JS packages. Never drastically alter the actual layout elements imperatively.

---
**Related rules:** `effect-layout-flicker`
