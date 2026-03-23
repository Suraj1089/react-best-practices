# React Best Practices — Full Reference

> Compiled from all rule files. Read this if you want every rule in one context window.
> For individual rules, read `rules/<rule-name>.md` directly.

---

# Bundle optimization

## bundle-lazy-loading

### Why it matters
The browser has to download, parse, and compile your JavaScript before the page becomes interactive. If you import a 500KB chart library and a settings modal at the top of your file, users pay for that download even if they never see those components. `React.lazy()` (or `next/dynamic`) splits those components into separate chunks that load only when needed.

### ❌ Wrong — monolithic bundle
```jsx
import HugeChartLibrary from './HugeChartLibrary';
import ComplexSettingsModal from './ComplexSettingsModal';

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      {/* User downloads both components on page load,
          even if they never open the settings modal */}
      <HugeChartLibrary />
      <button onClick={() => setShowSettings(true)}>Settings</button>
      {showSettings && <ComplexSettingsModal />}
    </div>
  );
}
```

### ✅ Right — split and load on demand
```jsx
// These files aren't downloaded until the component is rendered
const HugeChartLibrary = React.lazy(() => import('./HugeChartLibrary'));
const ComplexSettingsModal = React.lazy(() => import('./ComplexSettingsModal'));

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      <Suspense fallback={<SkeletonChart />}>
        <HugeChartLibrary />
      </Suspense>

      <button onClick={() => setShowSettings(true)}>Settings</button>
      
      {showSettings && (
        <Suspense fallback={<Spinner />}>
          <ComplexSettingsModal />
        </Suspense>
      )}
    </div>
  );
}
```

---

## bundle-tree-shaking-barrel

### Why it matters
Barrel files (`index.js` files that re-export everything from a folder) can prevent bundlers from tree-shaking. If you import one small button from a barrel that re-exports 5,000 components, the bundler may pull in all of them.

### ❌ Wrong — barrel import
```jsx
// Webpack may pull in every component in the ui/ folder
import { Button, Checkbox, HugeDatePicker } from '@/components/ui';
```

### ✅ Right — direct imports
```jsx
// Only imports the code you actually use
import Button from '@/components/ui/Button';
import Checkbox from '@/components/ui/Checkbox';
import HugeDatePicker from '@/components/ui/HugeDatePicker';
```

---
**Related rules:** `async-suspense-boundaries`


# Closures & stale state

## closure-understand

### Why it matters
When a function is created in JavaScript, it captures a snapshot of all the variables in its surrounding scope. This is a **closure**. In React, every render creates new function instances that close over the state and prop values from *that specific render*. The function keeps those values even after the render is done. Understanding this is key to debugging state issues in React.

---

## closure-stale-callback

### Why it matters
If a function is cached — via `useCallback` with an empty dep array, stored in a ref at init time, or passed to a `useEffect` that doesn't list it as a dependency — it captures the values from the render where it was created. Later state changes are invisible to it. This is a **stale closure**: your app silently uses outdated values.

### ❌ Wrong — empty dependency array freezes state
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // BUG: Empty deps mean `query` is always '' inside this callback
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

### ✅ Right — include all dependencies
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // Recreated whenever `query` changes, so it always has the current value
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
Sometimes you need a callback that is **reference-stable** (same function identity across renders, so memoized children don't re-render) but also reads the **latest** state when called. These goals conflict — unless you use a ref to bridge the gap.

### ✅ Pattern: stable wrapper + mutable ref
```jsx
function DataGrid({ onSelectionChange }) {
  const [selectedIds, setSelectedIds] = useState(new Set());

  // 1. Ref holds the latest callback
  const onSelectionChangeRef = useRef(onSelectionChange);

  // 2. Keep it in sync after every render
  useLayoutEffect(() => {
    onSelectionChangeRef.current = onSelectionChange;
  });

  // 3. Stable function that delegates to whatever's in the ref
  const handleSelect = useCallback((id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      
      // Always calls the latest onSelectionChange
      onSelectionChangeRef.current?.(next); 
      return next;
    });
  }, []); // Empty deps = same reference forever

  return <HeavyRowList onSelect={handleSelect} />;
}
```

### Notes
- The ref is updated in `useLayoutEffect`, which runs synchronously after render.
- The wrapper function reads `.current` at call time, so it always gets the latest logic.
- This is the pattern behind the experimental `useEffectEvent` RFC.

---
**Related rules:** `memo-react-memo`, `ref-no-overuse`


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


# Concurrent features & transitions

## rerender-transitions

### Why it matters
React 18 added concurrent rendering. By default, every `setState` call is urgent — React blocks the main thread until it finishes rendering, which locks up user input. `useTransition` lets you mark a state update as non-urgent. React will start rendering it in the background, but if the user types or clicks, React drops that background work to handle the interaction first. The result: no input lag.

### ❌ Wrong — blocking the main thread
```jsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    // Both updates are urgent. Rendering 1000 results
    // blocks the keystroke, so typing feels sluggish.
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
    // Urgent: the input updates immediately
    setQuery(e.target.value); 
    
    // Non-urgent: the list re-render happens in the background
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
`useTransition` requires direct access to the `setState` call so you can wrap it. `useDeferredValue` is for when you receive a prop from a parent and have no control over how it's set. It returns a "lagging" version of the value — the component keeps showing the old value while React computes the new one in the background.

### ✅ Pattern — deferring an incoming prop
```jsx
// SearchResults doesn't control `query`, it just receives it.
function SearchResults({ query }) {
  // React renders with the old deferredQuery while computing
  // the new one in the background
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  const results = highlyExpensiveFilter(data, deferredQuery);

  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      <HeavyResultGrid items={results} />
    </div>
  );
}
```

### When to use which?
- You have the `setState` call → use `useTransition`.
- You only have the prop → use `useDeferredValue`.

---
**Related rules:** `rerender-state-change`, `rendering-usetransition-loading`


# Context splitting

## context-splitting

### Why it matters
Any component that calls `useContext(SomeContext)` re-renders whenever that context's value changes. If you shove everything — theme, user, locale, feature flags — into one giant context object, then every consumer re-renders when *any* of those values changes, even if a given component only cares about one of them.

Split unrelated data into separate contexts. Components that read `UserContext` won't re-render when the theme changes, and vice versa.

### ❌ Wrong — monolithic context
```jsx
// One context for everything
const AppContext = createContext();

function AppProvider({ children }) {
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState(null);
  
  // When `theme` changes, every component that reads `user` also re-renders
  return (
    <AppContext.Provider value={{ theme, setTheme, user, setUser }}>
      {children}
    </AppContext.Provider>
  );
}

// Header only needs `user`, but re-renders on every theme toggle
function Header() {
  const { user } = useContext(AppContext);
  return <header>Welcome {user.name}</header>;
}
```

### ✅ Right — separate contexts by domain
```jsx
// Each domain gets its own context
const ThemeContext = createContext();
const UserContext = createContext();

function AppProviders({ children }) {
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState(null);

  return (
    <UserContext.Provider value={user}>
      <ThemeContext.Provider value={{ theme, setTheme }}>
        {children}
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
}

function Header() {
  // Now Header only re-renders when user data changes
  const user = useContext(UserContext);
  return <header>Welcome {user.name}</header>;
}
```

---
**Related rules:** `rerender-context`, `compose-children-prop`


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


# Memoization usage

Try composition first. `React.memo`, `useMemo`, and `useCallback` solve specific, measured performance problems — they're not defensive defaults. Adding them everywhere hurts performance because the comparison checks and memory allocation have their own cost.

---

## memo-react-memo

### Why it matters
`React.memo` wraps a component and tells React to skip re-rendering it when props haven't changed (checked with shallow `===`). Without it, any parent re-render cascades to the child, even if the child's props are identical.

### ✅ Usage
```jsx
// Chart is expensive to render. Wrapping it prevents unnecessary re-renders.
const ExpensiveDataGrid = React.memo(function ExpensiveDataGrid({ rows, columns }) {
  return <ComplexTableImplementation rows={rows} cols={columns} />;
});
```

### When to use it
- The component visibly lags the UI or shows up hot in the React Profiler.
- It re-renders often with unchanged props.
- Composition patterns (like `children`) don't work for the particular layout.

### When NOT to use it
- Wrapping every component by default.
- When the component receives new object/function references every render anyway (the memo comparison runs but always fails).
- When the component is lightweight (a simple `<Button />` or layout wrapper).

---

## memo-referential-equality

### Why it matters
`React.memo` uses **shallow equality**. Primitives (`string`, `number`, `boolean`) compare by value. Objects, arrays, and functions compare by **reference**. If you create an object or callback inside a component body, it gets a new reference every render, breaking `React.memo` on any child you pass it to.

### ❌ Wrong — new object reference every render
```jsx
function Dashboard() {
  const [count, setCount] = useState(0);

  // New object on every render — ExpensiveDataGrid's memo always fails
  const gridConfig = { theme: 'dark', sort: 'asc' }; 

  return <ExpensiveDataGrid config={gridConfig} />; 
}
```

### ✅ Right — stabilize references
```jsx
function Dashboard() {
  const [count, setCount] = useState(0);

  // Same reference across renders
  const gridConfig = useMemo(() => ({ theme: 'dark', sort: 'asc' }), []); 
  const onRowClick = useCallback((id) => openDetails(id), []); 

  // Now memo works — props haven't changed
  return <ExpensiveDataGrid config={gridConfig} onClick={onRowClick} />; 
}
```

---

## memo-usecallback-useless

### Why it matters
`useCallback` preserves a function's reference across renders. But if you pass that function to a DOM element (`<button>`) or a component that isn't wrapped in `React.memo`, the stable reference does nothing. The child re-renders anyway because its parent re-rendered.

### ❌ Useless useCallback
```jsx
function Form() {
  const [text, setText] = useState('');

  // Pointless. <button> is native DOM — it doesn't check props with React.memo.
  const onSubmit = useCallback(() => submitForm(), []);
  
  // Pointless. <Input> isn't wrapped in React.memo. It'll re-render regardless.
  const onChange = useCallback((val) => setText(val), []);

  return (
    <form onSubmit={onSubmit}>
      <Input onChange={onChange} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

**Rule of thumb:** `useCallback` only helps when the receiving component is wrapped in `React.memo`, or the function is used in a dependency array (like a downstream `useEffect`).

---

## memo-composition-trap

### Why it matters
Wrapping a component in `React.memo` while passing `children` doesn't work. JSX compiles children into `React.createElement(...)` inside the parent, so the children prop gets a new object reference every render. The memo comparison on `{ children }` fails every time.

### ❌ Wrong — memo broken by children
```jsx
const MemoizedCard = React.memo(function Card({ children }) {
  return <div className="card-ui">{children}</div>;
});

function Parent() {
  const [count, setCount] = useState(0);

  return (
    <MemoizedCard>
      {/* New element object every render */}
      <VeryExpensiveTree /> 
    </MemoizedCard>
  );
}
```

### ✅ Fix — memoize the children in the parent
```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // Freeze the JSX element reference
  const cachedChildren = useMemo(() => <VeryExpensiveTree />, []); 

  return <MemoizedCard>{cachedChildren}</MemoizedCard>;
}
```

Or use composition patterns (`compose-children-prop`) to avoid the problem entirely — no memoization needed.

---
**Related rules:** `rerender-parent`, `compose-children-prop`


# Reconciliation & keys

## recon-type-position

### Why it matters
React compares its internal fiber tree between renders. If a component element has the same **type** (same HTML tag or same component function) at the same **position** in the JSX tree as the previous render, React assumes it's the same instance. It reuses the component and **keeps its state and DOM focus**.

This causes bugs when you conditionally swap between two components that share the same root type.

### ❌ Wrong — shared position leaks state
```jsx
function App() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-box">
      {isLogin 
        // Both branches render an <Input /> at the first child position
        ? <Input placeholder="Username" /> 
        : <Input placeholder="Email Address" />
      }
      <button onClick={() => setIsLogin(!isLogin)}>Switch Mode</button>
    </div>
  );
}
```
**The bug:** A user types "John" in the Username field, clicks "Switch Mode", and "John" is still in the Email field. React reused the `<Input>` instance because the type and position didn't change.

### ✅ Right — use `key` to force a new instance
```jsx
{isLogin
  ? <Input key="login-username" placeholder="Username" />
  : <Input key="register-email" placeholder="Email Address" />
}
```
Different keys tell React these are separate components. It destroys the old one and mounts a fresh one.

---

## recon-key-identity

### Why it matters
The `key` prop isn't just an ESLint nag for lists. It's React's mechanism for tracking **identity**. A changed key tells React: "This is a different entity — destroy the old one and create a new one." A stable key tells React: "Same thing, just update its props."

### Key requirements
| Requirement | What goes wrong if you break it |
|---|---|
| Unique among siblings | State binds to the wrong list item |
| Stable across renders | Components unmount and remount constantly, losing scroll position and focus |
| Derived from data | Use `item.id`, not the array index (unless the list never reorders) |

### ❌ Wrong — unstable keys
```jsx
// Math.random() creates a new key every render — the whole list rebuilds
{users.map(user => <UserRow key={Math.random()} user={user} />)}

// Array index is dangerous if users can be reordered or deleted.
// Deleting index 0 makes index 1 become index 0, inheriting the wrong state.
{users.map((user, index) => <UserRow key={index} user={user} />)}
```

### ✅ Right — stable identity from data
```jsx
{users.map(user => <UserRow key={user.uuid} user={user} />)}
```

---

## recon-no-inline-definition

### Why it matters
Defining a component function inside another component's render body means React sees a brand-new function type every render. Since the type changed, React unmounts the old instance and mounts a new one — wiping all its state, tearing down effects, and causing flickering.

### ❌ Wrong — inline component definition
```jsx
function UserProfile() {
  const [clicks, setClicks] = useState(0);

  // New function reference every render — React treats it as a new component type
  function InnerBadge() {
    const [hovered, setHovered] = useState(false); // State resets every parent render
    return <span onMouseEnter={() => setHovered(true)}>Role</span>;
  }

  return (
    <div onClick={() => setClicks(c => c + 1)}>
      <InnerBadge /> 
    </div>
  );
}
```

### ✅ Right — define components at module level
```jsx
// Defined once. React reuses the same type.
function InnerBadge() {
  const [hovered, setHovered] = useState(false);
  return <span onMouseEnter={() => setHovered(true)}>Role</span>;
}

function UserProfile() {
  // ...
  return <InnerBadge />;
}
```

---

## recon-key-reset

### Why it matters
Sometimes you need to wipe a component's state completely — when routing to a different entity or switching data contexts. Instead of writing `useEffect` chains that manually reset each piece of state, change the component's `key`. React treats a key change as replacing the component entirely: unmount the old one, mount a fresh one.

### ✅ Pattern: key-driven reset
```jsx
// When activeChatId changes, the entire ChatPanel unmounts and
// remounts with clean state. No leftover messages from the previous chat.
<ChatPanel key={activeChatId} conversationId={activeChatId} />
```

### Notes
- This forces a full unmount/mount cycle, which is slower than a prop update. Use it for full resets, not minor updates.
- It's the clean alternative to "derived state" anti-patterns where effects watch props and manually reset state.

---
**Related rules:** `rerender-parent`, `rerender-derived-state-no-effect`


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


# Rendering performance

## rendering-virtualization

### Why it matters
React can diff and reconcile thousands of components quickly, but the browser struggles to lay out and paint thousands of actual DOM nodes. Virtualization (or "windowing") solves this by only rendering the items currently visible on screen. Off-screen items don't exist in the DOM at all.

### ❌ Wrong — rendering 10,000 DOM nodes
```jsx
function InvoiceList({ invoices }) {
  // All 10,000 rows exist in the DOM at once.
  // The browser bogs down on layout and paint.
  return (
    <div className="invoices-container">
      {invoices.map(invoice => <InvoiceRow key={invoice.id} data={invoice} />)}
    </div>
  );
}
```

### ✅ Right — virtualize with react-window
```jsx
import { FixedSizeList } from 'react-window';

function InvoiceList({ invoices }) {
  // Only ~10 DOM elements exist at a time, no matter how long the list is
  const Row = ({ index, style }) => (
    <div style={style}>
      <InvoiceRow data={invoices[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={500}
      width="100%"
      itemSize={50}
      itemCount={invoices.length}
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

## rendering-fragments

### Why it matters
Every extra `<div>` wrapper adds depth to the DOM tree. Deeply nested DOM trees make CSS layout calculations slower and create elements the browser has to manage for no reason. When a wrapper div has no styling or semantic purpose, replace it with a fragment (`<>...</>`).

### ❌ Wrong — pointless wrapper div
```jsx
function DashboardHeader() {
  // This div serves no styling or semantic purpose
  return (
    <div>
      <h1>Welcome</h1>
      <LogoutButton />
    </div>
  );
}
```

### ✅ Right — fragment instead
```jsx
function DashboardHeader() {
  // Groups elements without adding a DOM node
  return (
    <>
      <h1>Welcome</h1>
      <LogoutButton />
    </>
  );
}
```

---
**Related rules:** `recon-key-identity`


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


# Server Components & Server Actions

## server-components

### Why it matters
React Server Components (RSC) render on the server and stream the result to the client as serialized HTML and UI instructions. They ship **zero JavaScript** to the browser. By co-locating data fetching with the component that uses it, you avoid client-side fetch waterfalls and loading spinners.

### ❌ Wrong — everything is a Client Component
```jsx
'use client' // Forces the entire route to run on the client

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Client-side waterfall: user sees a skeleton while waiting
    fetch('/api/user-data').then(res => res.json()).then(setData);
  }, []);

  if (!data) return <Skeleton />;
  return <HeavyDashboard data={data} />;
}
```

### ✅ Right — async Server Component
```jsx
// No 'use client'. Runs on the server.
import { fetchUserData } from '@/db/queries'; 

export default async function DashboardPage() {
  // Direct await — no API route needed, no client JS shipped
  const data = await fetchUserData(); 

  return <HeavyDashboard data={data} />; 
}
```

---

## server-serialization

### Why it matters
When a Server Component passes props to a `'use client'` component, every prop crosses a network boundary and must be serializable. Passing an entire database row (50 columns, including sensitive fields) wastes bandwidth and risks leaking data the client shouldn't see.

### ❌ Wrong — passing the entire database record
```jsx
export default async function ProductPage({ id }) {
  // Full database row, including admin notes and internal IDs
  const rawDbProduct = await db.products.find(id); 

  // All 50 columns serialized and sent to the client
  return <ClientBuyButton product={rawDbProduct} />; 
}
```

### ✅ Right — pick only what the client needs
```jsx
export default async function ProductPage({ id }) {
  const rawDbProduct = await db.products.find(id); 

  // Only the 3 fields the button actually uses
  return (
    <ClientBuyButton 
      id={rawDbProduct.id} 
      price={rawDbProduct.price} 
      stockStatus={rawDbProduct.inStock} 
    />
  ); 
}
```

---

## server-auth-actions

### Why it matters
Server Actions (React 19) let you call server-side mutations directly from `<form action={...}>`. But they're effectively public API endpoints — anyone can call them. You have to authenticate and authorize on the server side, just like you would with any API route.

### ❌ Wrong — no authentication
```jsx
'use server'

export async function deleteUserAccount(userId) {
  // Anyone who finds this endpoint can delete any account
  await db.users.delete(userId);
}
```

### ✅ Right — authenticate before mutating
```jsx
'use server'
import { getSession } from '@/auth';

export async function deleteUserAccount(userId) {
  const session = await getSession();
  
  if (!session || session.user.id !== userId) {
    throw new Error('Unauthorized');
  }
  
  await db.users.delete(userId);
}
```

---
**Related rules:** `bundle-dynamic-imports`, `async-defer-await`


# Suspense & data streaming

## async-suspense-boundaries

### Why it matters
Without Suspense, React waits for every async operation to finish before showing anything. If your page has a fast query (user profile) and a slow one (billing history), the whole page stays blank until the slow query completes. `<Suspense>` lets you show the fast parts immediately while displaying a fallback for the parts still loading.

### ❌ Wrong — one slow query blocks everything
```jsx
// The entire page is blank until both queries finish
export default async function UserProfile() {
  const fastProfile = await getProfile();
  const extremelySlowBilling = await getBillingHistory(); 

  return (
    <div>
      <Header data={fastProfile} />
      <BillingTable data={extremelySlowBilling} />
    </div>
  );
}
```

### ✅ Right — stream fast content, suspend slow content
```jsx
export default async function UserProfile() {
  const fastProfile = await getProfile();

  return (
    <div>
      {/* Header shows up right away */}
      <Header data={fastProfile} />
      
      {/* Billing loads independently with a skeleton */}
      <Suspense fallback={<BillingTableSkeleton />}>
        <AsyncBillingWrapper />
      </Suspense>
    </div>
  );
}
```

---

## suspense-parallel-fetching

### Why it matters
When you `await` one query, then `await` another, they run in sequence. If each takes 500ms, the total is 1 second. If they don't depend on each other, fire both at the same time with `Promise.all` and finish in 500ms.

### ❌ Wrong — sequential queries
```jsx
async function AsyncStats() {
  // Second query doesn't start until the first one finishes
  const users = await db.users.count(); 
  const sales = await db.sales.sum();    

  return <Stats ui={users} sales={sales} />;
}
```

### ✅ Right — parallel queries
```jsx
async function AsyncStats() {
  // Both queries start at the same time
  const usersPromise = db.users.count();
  const salesPromise = db.sales.sum();
  
  // Wait for both to finish
  const [users, sales] = await Promise.all([usersPromise, salesPromise]);

  return <Stats ui={users} sales={sales} />;
}
```

---
**Related rules:** `server-components`, `server-serialization`


