# Suspense & data streaming

## async-suspense-boundaries

### Why it matters
Without Suspense, React waits for every async operation to finish before showing anything. If your page has a fast query (user profile) and a slow one (billing history), the whole page stays blank until the slow query completes. `<Suspense>` lets you show the fast parts immediately while displaying a fallback for the parts still loading.

### ❌ Wrong — one slow query blocks everything
```jsx
// The entire page is blank until both queries finish
export default async function UserProfile() {
  const fastProfile = await getProfile();
  const extremelySlowBilling = await getBillingHistory(); 

  return (
    <div>
      <Header data={fastProfile} />
      <BillingTable data={extremelySlowBilling} />
    </div>
  );
}
```

### ✅ Right — stream fast content, suspend slow content
```jsx
export default async function UserProfile() {
  const fastProfile = await getProfile();

  return (
    <div>
      {/* Header shows up right away */}
      <Header data={fastProfile} />
      
      {/* Billing loads independently with a skeleton */}
      <Suspense fallback={<BillingTableSkeleton />}>
        <AsyncBillingWrapper />
      </Suspense>
    </div>
  );
}
```

---

## suspense-parallel-fetching

### Why it matters
When you `await` one query, then `await` another, they run in sequence. If each takes 500ms, the total is 1 second. If they don't depend on each other, fire both at the same time with `Promise.all` and finish in 500ms.

### ❌ Wrong — sequential queries
```jsx
async function AsyncStats() {
  // Second query doesn't start until the first one finishes
  const users = await db.users.count(); 
  const sales = await db.sales.sum();    

  return <Stats ui={users} sales={sales} />;
}
```

### ✅ Right — parallel queries
```jsx
async function AsyncStats() {
  // Both queries start at the same time
  const usersPromise = db.users.count();
  const salesPromise = db.sales.sum();
  
  // Wait for both to finish
  const [users, sales] = await Promise.all([usersPromise, salesPromise]);

  return <Stats ui={users} sales={sales} />;
}
```

---
**Related rules:** `server-components`, `server-serialization`
