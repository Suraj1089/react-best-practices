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
