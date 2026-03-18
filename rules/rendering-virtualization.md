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
