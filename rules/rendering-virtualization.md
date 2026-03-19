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
