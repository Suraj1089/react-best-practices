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
