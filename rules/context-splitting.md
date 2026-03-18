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
