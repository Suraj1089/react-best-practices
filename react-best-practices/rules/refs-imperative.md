# Refs & imperative APIs

## ref-dom-access

### Why it matters
`useRef` creates a mutable object (`{ current: initialValue }`) that persists across renders without triggering re-renders when changed. When you pass a ref to a JSX element, React fills `.current` with the underlying DOM node.

### ✅ Basic DOM access
```jsx
function SearchBox() {
  const searchInputRef = useRef(null);

  const handleGlobalShortcut = () => {
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

### When refs are appropriate for DOM access
- Focus management: `.focus()`, `.blur()`, `.click()`
- Scroll control: `.scrollIntoView()`
- Layout measurement: `.getBoundingClientRect()`
- Media: video `.play()` and `.pause()`
- Third-party library integration: WebGL, D3, or other non-React libraries that need a DOM node

---

## ref-forward

### Why it matters
By default, you can't pass a `ref` prop to a custom function component — React strips it. For a parent to access a DOM node inside a child component, the child must opt in using `forwardRef`.

### ✅ Using forwardRef
```jsx
// The child explicitly wires the ref to its internal input
const FancyInput = forwardRef(function FancyInput(props, ref) {
  return (
    <div className="fancy-wrapper">
      <input ref={ref} className="fancy-internal-input" {...props} />
    </div>
  );
});

// Parent can now focus the input inside FancyInput
function CommandPalette() {
  const commandRef = useRef(null);
  
  useEffect(() => {
    commandRef.current?.focus();
  }, []);

  return <FancyInput ref={commandRef} placeholder="Enter command" />;
}
```

> **React 19 note:** In React 19+, `ref` is a regular prop — `forwardRef` is deprecated. You destructure it directly: `function FancyInput({ ref, children })`.

---

## ref-imperative-handle

### Why it matters
Forwarding a raw DOM ref gives the parent full access to the node — it could mutate styles, read values, or call any DOM method. `useImperativeHandle` lets you expose a limited, controlled API instead.

### ✅ Controlled API surface
```jsx
const SecureTextInput = forwardRef(function SecureTextInput(props, ref) {
  const internalInputRef = useRef(null);

  // Only expose these two methods to the parent
  useImperativeHandle(ref, () => ({
    focus() {
      internalInputRef.current?.focus();
    },
    triggerJiggleAnimation() {
      internalInputRef.current?.classList.add('error-jiggle');
      setTimeout(() => internalInputRef.current?.classList.remove('error-jiggle'), 500);
    }
    // Parent cannot access .value, .style, or .parentNode
  }));

  return <input ref={internalInputRef} type="password" {...props} />;
});
```

---

## ref-no-overuse

### Why it matters
React is built around declarative rendering — you describe what the UI should look like given the current state, and React figures out the DOM changes. Refs are an escape hatch for things React can't do declaratively. Reach for declarative patterns first.

### Prefer declarative approaches
| Imperative (escape hatch) | Declarative (preferred) |
|---|---|
| `modalRef.current.style.display = 'block'` | `isOpen && <Modal />` |
| `inputRef.current.value = 'John'` | `<input value={name} onChange={...} />` |
| `videoRef.current.play()` | `<VideoPlayer isPlaying={true} />` wrapper |

Refs are valid for: focus management, scroll positioning, WebGL/canvas setup, animation sequencing, and bridging vanilla JS libraries. Don't use them to change layout or content that React should control.

---
**Related rules:** `effect-layout-flicker`
