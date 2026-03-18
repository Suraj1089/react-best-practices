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
