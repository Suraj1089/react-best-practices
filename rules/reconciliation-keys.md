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
