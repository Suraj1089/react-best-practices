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
