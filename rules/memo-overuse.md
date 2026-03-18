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
