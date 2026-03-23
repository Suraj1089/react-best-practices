# Composition patterns

The most overlooked React optimization tool is **component structure**. Before reaching for `useMemo`, `useCallback`, or `React.memo`, consider whether rearranging your components can solve the problem. Composition fixes performance at the architecture level — no runtime overhead, no dependency arrays, no comparison checks.

---

## compose-move-state-down

### Why it matters
State in a parent triggers re-renders for the entire subtree. If that state only affects a small part of the UI (like a sidebar toggle), you're re-rendering everything else for no reason. Extract the stateful piece into its own component. Now only that component re-renders.

### ❌ Wrong — state lives high, everything re-renders
```jsx
function Dashboard() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="layout">
      {/* Toggling the sidebar re-renders the entire Dashboard */}
      <button onClick={() => setIsSidebarOpen(o => !o)}>Toggle Menu</button>
      {isSidebarOpen && <Sidebar />}
      
      <main>
        {/* This heavy chart re-renders every time the sidebar toggles */}
        <VeryExpensiveWebGLChart data={complexData} /> 
      </main>
    </div>
  );
}
```

### ✅ Right — extract the stateful piece
```jsx
function SidebarToggle() {           
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsOpen(o => !o)}>Toggle Menu</button>
      {isOpen && <Sidebar />}
    </>
  );
}

function Dashboard() {
  // No state here. Dashboard renders once.
  return (
    <div className="layout">
      <SidebarToggle />
      <main>
        <VeryExpensiveWebGLChart data={complexData} />
      </main>
    </div>
  );
}
```

---

## compose-children-prop

### Why it matters
When a component renders its `children`, those children are **not re-created** when the parent's own state changes. The children were instantiated in the outer scope (which didn't re-render), so their JSX element references stay the same. This shields heavy content from a parent's frequent state updates.

### ✅ Pattern — children as a shield
```jsx
// This component updates state on every scroll event
function ScrollProgressTracker({ children }) {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="scroll-container">
      <div className="progress-bar" style={{ width: `${scrollY / 10}%` }} />
      {/* children don't re-render when scrollY changes */}
      <div className="content">{children}</div>
    </div>
  );
}

// Usage:
function App() {
  return (
    <ScrollProgressTracker>
      <VeryExpensiveContentTree /> 
    </ScrollProgressTracker>
  );
}
```

---

## compose-components-as-props

### Why it matters
Passing React elements as named props (the "slots" pattern) works the same way as `children` — elements from the outer scope aren't affected by the inner component's state. This gives you flexible, decoupled layouts without prop drilling.

### ✅ Pattern — named slots
```jsx
// Layout doesn't know or care what goes in each pane
function TwoColumnLayout({ leftContent, rightContent }) {
  const [isResizing, setIsResizing] = useState(false);
  
  return (
    <div className={`split-view ${isResizing ? 'resizing' : ''}`}>
      <div className="pane-left">{leftContent}</div>
      <div className="resizer" onMouseDown={() => setIsResizing(true)} />
      <div className="pane-right">{rightContent}</div>
    </div>
  );
}

// Usage — content is defined outside, unaffected by resize state
function CRMApp() {
  return (
    <TwoColumnLayout
      leftContent={<ContactsSidebar data={contacts} />}
      rightContent={<ActiveConversation detail={currentChat} />}
    />
  );
}
```

### A subtle point
Passing `<ContactsSidebar />` as a prop doesn't call its render function. It passes an inert element object (`{ type: ContactsSidebar, props: ... }`). The component only renders when the receiving layout includes it in its return.

---
**Related rules:** `rerender-parent`, `memo-react-memo`
