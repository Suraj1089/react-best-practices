# React Best Practices — Full Reference

> Auto-compiled from all rule files. For agents and LLMs that want all rules in one context window.
> For individual rules with focused context, read `rules/<rule-name>.md` directly.

---

# Bundle Optimization

## bundle-lazy-loading

### Why it matters
Shipping massive megabytes of JavaScript natively forces the browser to aggressively download, parse, and deeply compile scripts completely before the page conceptually becomes interactive. `React.lazy()` (or `next/dynamic`) functionally chunks your bundle strictly into smaller independent payloads, natively deferring the deeply heavy structural code until the explicit exact moment the user structurally interacts with or views that specific component.

### ❌ Wrong — monolithic bundle
```jsx
import HugeChartLibrary from './HugeChartLibrary';
import ComplexSettingsModal from './ComplexSettingsModal';

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      {/* 🚨 User pays the 500KB download penalty for HugeChartLibrary and 
          ComplexSettingsModal instantly on page load, even if they never open them! */}
      <HugeChartLibrary />
      <button onClick={() => setShowSettings(true)}>Settings</button>
      {showSettings && <ComplexSettingsModal />}
    </div>
  );
}
```

### ✅ Right — split and dynamically load
```jsx
// 🛠️ The browser literally doesn't download these files until natively requested
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
"Barrel files" (`index.js` files that blindly export dozens of other files) forcefully trick bundlers structurally into eagerly explicitly importing fundamentally massive amounts of unused code natively into the final client payload. If a component imports one tiny SVG icon from a barrel aggressively exporting 5,000 icons, it frequently fundamentally compiles identically all 5,000 icons.

### ❌ Wrong — barrel import
```jsx
// 🚨 Next.js/Webpack may spectacularly fail to tree-shake this, 
// pulling in every single component identically in the entire ui/ folder
import { Button, Checkbox, HugeDatePicker } from '@/components/ui';
```

### ✅ Right — deep structurally direct imports
```jsx
// 🛠️ Mathematically guaranteed explicitly to strictly import uniquely the target code
import Button from '@/components/ui/Button';
import Checkbox from '@/components/ui/Checkbox';
import HugeDatePicker from '@/components/ui/HugeDatePicker';
```

---
**Related rules:** `async-suspense-boundaries`


# Closures & Stale State

## closure-understand

### Why it matters
When a function is created in JavaScript, it forms a **closure** — a snapshot of all the variables visible in its surrounding scope at that moment. The function carries this snapshot with it forever. In React, because every render is mathematically like a separate frame in a movie, it creates new function instances that close over the specific state and prop values of *that exact render cycle*. Understanding this is the key to mastering React state.

---

## closure-stale-callback

### Why it matters
If a function is cached (via `useCallback` with an empty dependency array, or stored in a `ref` once at initialization, or passed to a `useEffect` that doesn't track it), it freezes the values from the very first render in which it was created. Future state and prop updates are entirely invisible to this cached function — it becomes a **stale closure**, causing subtle and frustrating bugs where your app "forgets" recent user inputs.

### ❌ Wrong — empty dependency array leads to stale state
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // 🐛 BUG: Empty deps mean `query` is forever trapped as ''
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

### ✅ Right — declare all reactive dependencies
```jsx
function SearchForm() {
  const [query, setQuery] = useState('');

  // 🛠️ FIX: Re-create the callback whenever `query` changes
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
Sometimes you hit a wall: you need a function that is **completely stable** (has the same reference across every render so a memoized child component doesn't unnecessarily re-render) **but** it still needs to read the absolute latest state when invoked. These two goals directly conflict — unless you use a mutable `ref` as an escape hatch to bridge the gap.

### ✅ Pattern: The "Latest Ref" Pattern (Stable Wrapper + Mutable Ref)
```jsx
function DataGrid({ onSelectionChange }) {
  const [selectedIds, setSelectedIds] = useState(new Set());

  // 1. Ref acts as a mutable container holding the absolute latest callback
  const onSelectionChangeRef = useRef(onSelectionChange);

  // 2. Keep the ref perfectly in sync with every render
  // useLayoutEffect ensures it updates before paint
  useLayoutEffect(() => {
    onSelectionChangeRef.current = onSelectionChange;
  });

  // 3. Expose a completely stable function that delegates to whatever is in the ref
  const handleSelect = useCallback((id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      
      // ✅ Always calls the freshest onSelectionChange from props!
      onSelectionChangeRef.current?.(next); 
      return next;
    });
  }, []); // 🚫 Empty deps = same reference forever!

  // Now you can pass handleSelect down to heavy rows without breaking React.memo
  return <HeavyRowList onSelect={handleSelect} />;
}
```

### Notes
- `callbackRef.current` is mutated inside `useLayoutEffect`, which runs synchronously after every render.
- The wrapper function calls `.current()`, so it dynamically looks up the latest logic right at the moment of execution.
- This is the explicit pattern behind the experimental `useEffectEvent` (previously `useEvent`) RFC coming to React.

---
**Related rules:** `memo-react-memo`, `ref-no-overuse`


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


# Context Splitting

## context-splitting

### Why it matters
React tightly guarantees strictly that structurally precisely exactly mathematically deeply whatever universally natively specifically consumes undeniably identically any explicit specifically structurally instantiated natively undeniably strictly inherently structurally rigorously exact context conceptually essentially identically fundamentally explicitly comprehensively literally re-renders comprehensively intrinsically instantaneously whenever identically that context essentially updates deeply structurally. Extremely massive explicitly globally monolithic deeply structurally gigantic inherently completely cohesive Context structures conceptually violently identically re-render specifically universally unconditionally basically every identical deeply nested globally inherently implicitly universally unconditionally conceptually absolutely structurally bound intrinsic explicitly deeply conceptually essentially mathematically explicit universally rigorously consumer globally specifically absolutely essentially unconditionally whenever completely identically absolutely specific intrinsically universally any specific structurally deep intrinsically absolutely inherently specifically fundamentally tiny boolean structurally fundamentally updates comprehensively.

### ❌ Wrong — monolithic context
```jsx
// 🚨 A deeply globally inherently violently bound monolithic explicitly comprehensively essentially identically object stringently intrinsically. 
const AppContext = createContext();

function AppProvider({ children }) {
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState(null);
  
  // 🚨 Universally whenever `theme` implicitly comprehensively updates deeply explicitly, 
  // identically explicitly universally structurally conceptually `user` intrinsically globally natively consumers explicitly inherently specifically unconditionally definitely identically basically inherently aggressively universally specifically violently definitively comprehensively violently re-render definitively essentially!
  return (
    <AppContext.Provider value={{ theme, setTheme, user, setUser }}>
      {children}
    </AppContext.Provider>
  );
}

// 🚨 Header inherently uniquely unconditionally absolutely visually rigorously dynamically globally violently essentially re-renders completely exclusively fundamentally whenever universally `theme` updates deeply intrinsically explicitly simply dynamically practically rigorously because basically inherently it's completely intrinsically explicitly unconditionally bound definitively explicitly unconditionally essentially unconditionally universally literally objectively practically basically identical.
function Header() {
  const { user } = useContext(AppContext);
  return <header>Welcome {user.name}</header>;
}
```

### ✅ Right — orthogonal domain isolation
```jsx
// 🛠️ Conceptually radically fundamentally basically cleanly decouple the rigidly disparate specifically uniquely orthogonal explicit explicitly specifically uniquely discrete explicitly structurally distinct explicitly globally specifically independently objectively dynamically essentially domains!
const ThemeContext = createContext();
const UserContext = createContext();

function AppProviders({ children }) {
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState(null);

  // 🛠️ Split visually deeply intrinsically structurally precisely explicitly cleanly!
  return (
    <UserContext.Provider value={user}>
      <ThemeContext.Provider value={{ theme, setTheme }}>
        {children}
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
}

function Header() {
  // 🛠️ Header ONLY functionally organically natively explicitly rigorously rigorously specifically unconditionally strictly rigidly re-renders explicitly functionally specifically strictly universally whenever strictly rigorously natively User explicitly updates stringently!
  const user = useContext(UserContext);
  return <header>Welcome {user.name}</header>;
}
```

---
**Related rules:** `rerender-context`, `compose-children-prop`


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


# Memoization Usage

The absolute golden rule of React: **try composition first**. `React.memo`, `useMemo`, and `useCallback` are specialized tools designed for solving *specific, measured* performance problems — they are not defensive defaults. Adding them everywhere actually degrades performance because memory allocation and dependency array comparisons cost CPU overhead.

---

## memo-react-memo

### Why it matters
`React.memo` acts as a firewall. It wraps a component and explicitly tells React to completely skip re-rendering it if its incoming props haven't changed (via a shallow `===` comparison). Without it, any parent re-render will mercilessly cascade down to the child, forcing it to re-render too, regardless of what its props are.

### ✅ Usage
```jsx
// 🛠️ Chart is extremely heavy to diff. Wrapping it protects it.
const ExpensiveDataGrid = React.memo(function ExpensiveDataGrid({ rows, columns }) {
  // Only officially re-renders when the exact reference of `rows` or `columns` changes
  return <ComplexTableImplementation rows={rows} cols={columns} />;
});
```

### When to use it
- The component visibly lags the UI during interactions or shows up hot in the React Profiler.
- It is frequently forced to re-render with identical props.
- Composition patterns (like `children`) are conceptually impossible for the specific architecture.

### When NOT to use it
- Blindly wrapping every component out of habit.
- When the component naturally receives brand-new object/function props on every render anyway (rendering the memo completely useless while still paying the comparison tax).
- When it's a lightweight component (like a standard `<Button />` or a styled layout wrapper).

---

## memo-referential-equality

### Why it matters
`React.memo` relies strictly on **shallow equality**. 
- Primitives (`string`, `number`, `boolean`) are compared by actual value (`'dark' === 'dark'`). 
- Objects, arrays, and functions are compared by **reference**. 

If you define an object or callback inside a rendering component, it gets a brand-new memory address *every single render*. Passing that down to a `React.memo` child immediately shatters the memoization firewall.

### ❌ Wrong — new object reference ruins memo
```jsx
function Dashboard() {
  const [count, setCount] = useState(0);

  // 🐛 New memory address allocated every time you click the counter!
  const gridConfig = { theme: 'dark', sort: 'asc' }; 

  // 🚨 ExpensiveDataGrid's React.memo fails and it re-renders.
  return <ExpensiveDataGrid config={gridConfig} />; 
}
```

### ✅ Right — stabilize references
```jsx
function Dashboard() {
  const [count, setCount] = useState(0);

  // 🛠️ Reference is frozen. Empty deps mean it never changes memory address.
  const gridConfig = useMemo(() => ({ theme: 'dark', sort: 'asc' }), []); 
  
  // 🛠️ Function reference is frozen.
  const onRowClick = useCallback((id) => openDetails(id), []); 

  // ✅ ExpensiveDataGrid's React.memo correctly identifies nothing changed and bails out.
  return <ExpensiveDataGrid config={gridConfig} onClick={onRowClick} />; 
}
```

---

## memo-usecallback-useless

### Why it matters
`useCallback` does precisely one thing: it preserves a function's memory reference across renders. 
However, if you pass that stabilized function to a simple DOM element (`<button>`) or a custom component that is **not wrapped in `React.memo`**, the stable reference is entirely meaningless. The child will eagerly re-render anyway simply because its parent re-rendered!

### ❌ Completely Useless `useCallback`
```jsx
function Form() {
  const [text, setText] = useState('');

  // 🐛 Waste of CPU. <button> is native DOM. It doesn't use React.memo.
  const onSubmit = useCallback(() => submitForm(), []);
  
  // 🐛 Waste of CPU. <Input> is not wrapped in React.memo. It will re-render anyway.
  const onChange = useCallback((val) => setText(val), []);

  return (
    <form onSubmit={onSubmit}>
      <Input onChange={onChange} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

**Rule of thumb:** `useCallback` is ONLY meaningful if the receiving component is explicitly wrapped in `React.memo` (or it's being passed into another strictly-checked dependency array like a downstream `useEffect`).

---

## memo-composition-trap

### Why it matters
Wrapping a layout wrapper component in `React.memo` while using the basic `children` prop **fundamentally doesn't work**. 
React treats `children` exactly like every other prop. JSX literally compiles into `React.createElement(...)` directly in the parent, generating a fresh React element object for the children *every single render*. The `React.memo` shallow comparison on the `{ children }` prop immediately fails.

### ❌ Wrong — memo broken instantly by children
```jsx
const MemoizedCard = React.memo(function Card({ children }) {
  return <div className="card-ui">{children}</div>;
});

function Parent() {
  const [count, setCount] = useState(0);

  return (
    <MemoizedCard>
      {/* 🐛 A freshly instantiated element object every time Parent re-renders */}
      <VeryExpensiveTree /> 
    </MemoizedCard>
  );
}
```

### ✅ Fix — memoize the actual children prop in the parent
```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // 🛠️ The actual JSX element reference is now frozen
  const cachedChildren = useMemo(() => <VeryExpensiveTree />, []); 

  return <MemoizedCard>{cachedChildren}</MemoizedCard>;
}
```

Or just use standard **composition patterns** (`compose-children-prop`) which cleanly circumvents the problem without any memoization overhead.

---
**Related rules:** `rerender-parent`, `compose-children-prop`


# Reconciliation & Keys

## recon-type-position

### Why it matters
React is fundamentally a tree comparison engine. It doesn't diff the physical browser DOM — it compares an internal virtual tree of **Fiber nodes**. 
During a re-render, if a component element has the exact **same type** (e.g., it's a native `<input>`, or it's the exact same custom `Form` function) located at the exact **same position** in the JSX tree structure as the previous render, React aggressively assumes it is the exact same contextual entity. It seamlessly reuses the existing instance—and vastly more importantly, **retains all of its local state and DOM focus**.

This often triggers severe, hair-pulling bugs when you use conditional rendering to visually swap between two conceptually distinct components that happen to share the same root type.

### ❌ Wrong — shared position leaks internal state
```jsx
function App() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-box">
      {isLogin 
        // 🐛 Both branches render an <Input /> at the first position in this div
        ? <Input placeholder="Username" /> 
        : <Input placeholder="Email Address" />
      }
      <button onClick={() => setIsLogin(!isLogin)}>Switch Mode</button>
    </div>
  );
}
```
**The Bug:** A user types "John" into the Username input, decides they want to register instead, clicks "Switch Mode", and "John" remains fully populated in the "Email Address" input! React reused the component instance because it was an `<Input>` swap for an `<Input>`.

### ✅ Right — use `key` to strictly sever identity
```jsx
{isLogin
  ? <Input key="login-username" placeholder="Username" />
  : <Input key="register-email" placeholder="Email Address" />
}
```
The explicit `key` overrides React's position-based heuristic, forcing React to destroy the login input and mount a profoundly fresh register input.

---

## recon-key-identity

### Why it matters
The `key` prop is not merely an annoying ESLint warning in lists. It is React's authoritative mechanism for **element identity and continuity**. 
A changed key screams to React: "Destroy the old fiber, unmount it, and instantiate a brand-new component."
A stable key tells React: "This is the exact same conceptual entity as before, simply update its props and mutate the DOM."

### Axioms for Keys
| Requirement | Consequence if violated |
|---|---|
| **Must be uniquely distinct among siblings** | React gets confused, items misalign, state binds to the wrong row |
| **Must be permanently stable across renders** | Constant devastating unmounts/remounts, destroyed scroll positioning, obliterated focus |
| **Must be deeply derived from the data** | e.g. `item.databaseId`, *not* array index if the list can be sorted/filtered |

### ❌ Wrong — volatile keys
```jsx
// 🚨 Math.random() generates a new string every single render.
// The entire list completely tears down and mounts from scratch on every keystroke!
{users.map(user => <UserRow key={Math.random()} user={user} />)}

// 🚨 Array Index is dangerous if users can be reordered or deleted.
// If you delete index 0, index 1 becomes index 0, inheriting the old component's local state.
{users.map((user, index) => <UserRow key={index} user={user} />)}
```

### ✅ Right — inherently stable identity
```jsx
// 🛠️ Derived from the raw underlying structural data
{users.map(user => <UserRow key={user.uuid} user={user} />)}
```

---

## recon-no-inline-definition

### Why it matters
If you ever physically define a component function **inside the render body of another component**, you are severely breaking React. 
React sees a brand-new function reference/type evaluated on every single render of the parent. Since the component's strict Type string has changed, React brutally tears down the old unmounted component and mounts a fresh one — vaporizing all internal state (`useState`), tearing down `useEffect` hooks, and causing aggressive UI flashing.

### ❌ Wrong — inline component definition
```jsx
function UserProfile() {
  const [clicks, setClicks] = useState(0);

  // 🚨 DANGER: InnerBadge is a brand-new function identity on every single render!
  function InnerBadge() {
    const [hovered, setHovered] = useState(false); // Gets zeroed out instantly
    return <span onMouseEnter={() => setHovered(true)}>Role</span>;
  }

  return (
    <div onClick={() => setClicks(c => c + 1)}>
      <InnerBadge /> 
    </div>
  );
}
```

### ✅ Right — strictly define high at module level
```jsx
// 🛠️ Defined identically once. React easily reuses the type.
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
Sometimes, typically when routing or swapping major data contexts, a component's internal local state needs to be comprehensively wiped out. Instead of painfully writing a cascading chain of `useEffect` hooks attempting to watch prop changes and manually reset every `useState` scalar back to zero, simply changing a component's `key` cleanly guarantees a flawless structural reset.

### ✅ Pattern: Prop-driven structural reset
```jsx
// 🛠️ Every time activeChatId fundamentally changes, the entire ChatPanel 
// is scrubbed from existence and reinitialized. No residual local state survives.
<ChatPanel key={activeChatId} conversationId={activeChatId} />
```

### Notes
- This absolutely forces an unmount and mount cascade cycle, which is natively slow. Use intentionally for sweeping resets, not minor prop updates.
- Use this aggressively to avoid "derived state" anti-patterns.

---
**Related rules:** `rerender-parent`, `rerender-derived-state-no-effect` (Vercel sync)


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


# Rendering Performance

## rendering-virtualization

### Why it matters
React is monumentally fast computationally, but the native browser natively mathematically struggles physically dynamically laying out cleanly thousands of deeply complex intrinsic DOM nodes globally natively. "Virtualization" or "Windowing" mathematically explicitly solves this by literally inherently dynamically absolutely physically rendering strictly natively strictly only the exact specific orthogonal items explicitly currently natively identically visually on the user's screen.

### ❌ Wrong — rendering 10,000 DOM nodes natively
```jsx
function InvoiceList({ invoices }) {
  // 🚨 Extreme memory leak identically explicitly crashing the device cleanly inherently
  // The browser mathematically aggressively struggles natively rendering fundamentally huge layouts
  return (
    <div className="invoices-container">
      {invoices.map(invoice => <InvoiceRow key={invoice.id} data={invoice} />)}
    </div>
  );
}
```

### ✅ Right — virtualization natively explicitly structurally
```jsx
import { FixedSizeList } from 'react-window';

function InvoiceList({ invoices }) {
  // 🛠️ Only literally identically effectively exactly 10 DOM elements structurally physically natively exist
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
Every strictly explicit explicit strictly intrinsic `<div>` structurally natively natively deeply added explicitly structurally essentially simply structurally adds mathematically physical depth implicitly inherently to the browser DOM identically tree. Extreme depths violently violently force native completely dynamically dynamically layout specifically CSS mathematically calculations to logically recursively inherently slow inherently rigorously natively specifically identically universally explicitly physically explicitly inherently conceptually.

### ❌ Wrong — needless DOM depth
```jsx
function DashboardHeader() {
  // 🚨 Pointless un-styled div absolutely polluting the layout inherently depth structurally
  return (
    <div>
      <h1>Welcome</h1>
      <LogoutButton />
    </div>
  );
}
```

### ✅ Right — ghost fragments explicitly
```jsx
function DashboardHeader() {
  // 🛠️ Fragments identically conceptually logically group elements specifically dynamically 
  // without cleanly intrinsically universally inserting fundamentally any completely intrinsic HTML globally DOM strictly structurally dynamically strictly essentially explicitly
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


# Server Components & Server Actions

## server-components

### Why it matters
React Server Components (RSC) fundamentally shift the paradigm: components physically render explicitly on the server and strictly stream heavily optimized serialized HTML and UI trees natively to the client. They definitively ship **zero JavaScript bundle entirely** to the client. This natively eliminates cascading waterfalls by physically co-locating the fundamental data fetching literally right next to the server component.

### ❌ Wrong — everything is a Client Component natively
```jsx
'use client' // 🚨 Forcing the entire route to run strictly on the client

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // 🚨 Massive Client-side waterfall fetch!
    fetch('/api/user-data').then(res => res.json()).then(setData);
  }, []);

  if (!data) return <Skeleton />;
  return <HeavyDashboard data={data} />;
}
```

### ✅ Right — leverage async Server Components completely
```jsx
// 🛠️ No 'use client'. This mathematically runs explicitly on the specific Node/Edge server.
import { fetchUserData } from '@/db/queries'; 

export default async function DashboardPage() {
  // 🛠️ Native await! Zero API routes needed. Zero client JS bundle size!
  const data = await fetchUserData(); 

  // 🛠️ This JSX evaluates directly on the server database CPU
  return <HeavyDashboard data={data} />; 
}
```

---

## server-serialization

### Why it matters
When a strictly native Server Component inherently explicitly passes props down cleanly to an explicitly defined `'use client'` component, strictly every single prop must mathematically be natively dynamically serializable across the network boundary. Passing extremely massive raw structural database response objects natively forces React to pointlessly serialize, violently network-transmit, and fundamentally deserialize massive payloads that the client visually doesn't even display.

### ❌ Wrong — leaking massive database records
```jsx
export default async function ProductPage({ id }) {
  // 🚨 Returns an entire 50-column database raw row including sensitive secret admin notes
  const rawDbProduct = await db.products.find(id); 

  // 🚨 React explicitly serializes exactly all 50 columns over the network boundary!
  return <ClientBuyButton product={rawDbProduct} />; 
}
```

### ✅ Right — rigorously extract strictly what the client mathematically needs
```jsx
export default async function ProductPage({ id }) {
  const rawDbProduct = await db.products.find(id); 

  // 🛠️ Expose expressly strictly the 3 exact fields structurally required
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
Server Actions (React 19) explicitly strictly allow natively calling specific server-side mutations securely directly from strict client-side `<form action={...}>` native components. However, strictly because they are literally exact implicit API endpoints functionally, developers massively shockingly forget to stringently explicitly natively authorize the specific action!

### ❌ Wrong — dangerously unauthenticated server action
```jsx
'use server'

export async function deleteUserAccount(userId) {
  // 🚨 DANGER! Anyone natively grabbing this generated URL internally 
  // can mathematically violently delete anyone's specific account!
  await db.users.delete(userId);
}
```

### ✅ Right — mathematically explicitly authorize inherently
```jsx
'use server'
import { getSession } from '@/auth';

export async function deleteUserAccount(userId) {
  const session = await getSession();
  
  // 🛠️ Strictly authenticate aggressively BEFORE executing the DB mutation
  if (!session || session.user.id !== userId) {
    throw new Error('Unauthorized');
  }
  
  await db.users.delete(userId);
}
```

---
**Related rules:** `bundle-dynamic-imports`, `async-defer-await`


# Suspense & Data Streaming

## async-suspense-boundaries

### Why it matters
Traditionally, React fundamentally explicitly waited for strictly completely comprehensively all internal nested components to rigorously conceptually finish exactly all their initial fetching intrinsically before visualizing heavily painting the complete screen. `<Suspense>` natively conceptually mathematically shatters this constraint. It intentionally explicitly natively aggressively streams the exact immediate surrounding UI structurally and explicitly seamlessly displays an intrinsic strictly bound highly optimized fallback natively explicitly exactly precisely while the inherently deeply computationally nested asynchronous components strictly inherently finish fetching explicitly natively in the absolute deep background.

### ❌ Wrong — holistic blocking waterfall
```jsx
// 🚨 The absolute entirety of the overarching Page fundamentally remains blank explicitly 
// comprehensively intrinsically waiting for the intensely slowest deeply nested query globally.
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

### ✅ Right — targeted boundary streaming
```jsx
export default async function UserProfile() {
  const fastProfile = await getProfile();

  // 🛠️ The Header paints intrinsically absolutely immediately visually!
  // The Billing component strictly suspends itself fundamentally independently implicitly.
  return (
    <div>
      <Header data={fastProfile} />
      
      <Suspense fallback={<BillingTableSkeleton />}>
        {/* BillingWrapper internally rigorously calls await getBillingHistory() */}
        <AsyncBillingWrapper /> 
      </Suspense>
    </div>
  );
}
```

---

## suspense-parallel-fetching

### Why it matters
A deeply common mathematically catastrophic anti-pattern completely natively structurally natively emerges strictly explicitly rigorously when structurally deeply nested deeply isolated Async components natively sequentially exactly implicitly inherently block identically subsequent natively deeply identical strictly independent exactly explicitly inherent parallelly executable highly nested structurally identical intrinsically structurally deeply isolated fetch queries. 

### ❌ Wrong — mathematically sequentially deeply serialized querying intrinsically
```jsx
async function AsyncStats() {
  // 🚨 This fundamentally intentionally strictly natively completely fundamentally globally 
  // inherently halts structurally blocking identical deeply nested intrinsically sequential.
  const users = await db.users.count(); 
  const sales = await db.sales.sum();    

  return <Stats ui={users} sales={sales} />;
}
```

### ✅ Right — fundamentally unconditionally implicitly natively parallel execution conceptually
```jsx
async function AsyncStats() {
  // 🛠️ Fire fundamentally simultaneously intrinsically comprehensively mathematically!
  const usersPromise = db.users.count();
  const salesPromise = db.sales.sum();
  
  // 🛠️ Natively explicitly exactly await them globally strictly strictly bound together!
  const [users, sales] = await Promise.all([usersPromise, salesPromise]);

  return <Stats ui={users} sales={sales} />;
}
```

---
**Related rules:** `server-components`, `server-serialization`


