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
