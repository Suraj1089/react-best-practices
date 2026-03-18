# Composition Patterns

The absolute most overlooked React optimization tool is **component structure**. Before reaching for `useMemo`, `useCallback`, or `React.memo` (which all add cognitive overhead and run-time checks), you should actively consider whether a simple composition refactor can eliminate the performance problem entirely. Composition solves problems at the architectural level.

---

## compose-move-state-down

### Why it matters
State kept high up in a parent triggers re-renders on the entire component subtree whenever it changes. If that state is logically only used by a tiny portion of the UI (like a hover state or a modal toggle), you are burning CPU cycles rendering parents and siblings for no reason. Move the state into its own isolated component. Now only that specific component re-renders — the rest of the tree is safely bypassed.

### ❌ Wrong — state lives high, forcing broad re-renders
```jsx
function Dashboard() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // 🐛 High-level state

  return (
    <div className="layout">
      {/* Any toggle causes the ENTIRE Dashboard to re-render */}
      <button onClick={() => setIsSidebarOpen(o => !o)}>Toggle Menu</button>
      {isSidebarOpen && <Sidebar />}
      
      <main>
        {/* 🚨 This extremely heavy chart re-renders every time you toggle the sidebar! */}
        <VeryExpensiveWebGLChart data={complexData} /> 
      </main>
    </div>
  );
}
```

### ✅ Right — extract the stateful piece
```jsx
// 🛠️ Extract the toggle logic into an isolated shell
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
  // ✅ No state here! Dashboard only renders once.
  return (
    <div className="layout">
      <SidebarToggle />
      <main>
        <VeryExpensiveWebGLChart data={complexData} /> {/* Safely shielded */}
      </main>
    </div>
  );
}
```

---

## compose-children-prop

### Why it matters
When a component renders its `children` prop, those children are **not re-created** when the parent component's own internal state changes. React passes children down as props — and because those props were instantiated in the *outer* scope (which didn't re-render), the JSX element object references remain identical.

This acts as an invisible shield for heavy, static UI segments against a parent's frequent state updates (like scroll, drag, or animation state).

### ✅ Pattern — children as a composition shield
```jsx
// This component tracks scroll aggressively
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
      {/* 
        ✅ children won't re-render when scrollY changes! 
        Because the elements evaluating to 'children' were created outside.
      */}
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
Passing React component elements as named props (also known as the "slots" pattern) works exactly the same way as `children` — elements from the outer scope aren't affected by inner state. This unlocks highly flexible, decoupled layouts where the parent wrapper doesn't need to know any UI details, reducing prop drilling and coupling.

### ✅ Pattern — named component slots (props)
```jsx
// Layout completely decoupled from content
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

// Usage — full control of the inner areas without touching the TwoColumnLayout itself
function CRMApp() {
  return (
    <TwoColumnLayout
      leftContent={<ContactsSidebar data={contacts} />}
      rightContent={<ActiveConversation detail={currentChat} />}
    />
  );
}
```

### Performance clarification
Passing `<ContactsSidebar />` as a prop is **not** the same as calling its render function. What's passed is simply an inert React element object (`{ type: ContactsSidebar, props: ... }`). It only actively renders and runs its logic when the receiving component physically includes it in its JSX return. 

---
**Related rules:** `rerender-parent`, `memo-react-memo`
