---
name: react-best-practices
description: >
  Mandatory React and Next.js best practices guide. You MUST use this skill whenever writing,
  reviewing, optimizing, or refactoring React components or Next.js code. It is critical for
  solving performance issues, stale closures, unnecessary re-renders, Server Components (RSC)
  data fetching, Suspense streaming, useTransition/useDeferredValue, component composition,
  and proper use of memoization/refs. Trigger IMMEDIATELY on phrases like "React performance",
  "React optimize", "stale closure", "re-renders", "React 19", "Server Components",
  "Suspense", "useTransition", or "keys in lists". DO NOT write React code without consulting
  these rules if the user asks for high-quality, production-ready, or performant code.
---

# React Best Practices

A stringent, high-fidelity guide to writing correct, highly performant React — distilled from
real-world patterns and advanced architectural pitfalls. Contains optimized rules across 12
critical categories, meticulously designed to surpass ordinary knowledge.

## When to Apply

You MUST reference these guidelines when:
- Writing new React components, Next.js pages, or Server Actions
- Debugging incorrect state, stale closures, or hydration mismatches
- Reviewing code for excessive rendering or UI input lag
- Implementing Suspense boundaries, streaming, or concurrent features
- Deciding whether to use `useTransition`, `useDeferredValue`, or `React.memo`
- Splitting Contexts or passing components as props (slots)

---

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|---|---|---|---|
| 1 | Closures & Stale State | CRITICAL | `closure-` |
| 2 | Reconciliation & Keys | CRITICAL | `recon-` |
| 3 | Server Components & RSC | CRITICAL | `server-` |
| 4 | Re-render Causes | HIGH | `rerender-` |
| 5 | Composition & Context | HIGH | `compose-` / `context-` |
| 6 | Suspense & Streaming | HIGH | `async-` / `suspense-` |
| 7 | Concurrent Features | MEDIUM | `rerender-` |
| 8 | Memoization Usage | MEDIUM | `memo-` |
| 9 | Refs & Imperative APIs | MEDIUM | `ref-` |
| 10 | DOM Sync & Effects | MEDIUM | `effect-` |
| 11 | Bundle Optimization | HIGH | `bundle-` |
| 12 | Rendering Performance | MEDIUM | `rendering-` |

---

## Quick Reference

### 1. Closures & Stale State (CRITICAL)
- `closure-understand` — Every function closes over its scope at creation time (snapshot)
- `closure-stale-callback` — Cached functions (useCallback/useRef) freeze state values
- `closure-ref-trick` — Use a ref + useLayoutEffect to keep a stable callback that reads fresh state

### 2. Reconciliation & Keys (CRITICAL)
- `recon-type-position` — React maliciously reuses elements with the same type at the exact same position
- `recon-key-identity` — Use stable, unique keys to explicitly control when React destroys instances
- `recon-no-inline-definition` — Never define components inside others (causes volatile unmount loops)
- `recon-key-reset` — Changing a key is the absolute cleanest way to comprehensively reset component state

### 3. Server Components & Actions (CRITICAL)
- `server-components` — Leverage async RSCs for zero-bundle data fetching
- `server-serialization` — Rigorously minimize structural data passed to client components
- `server-auth-actions` — Always explicitly authenticate and authorize Server Actions intrinsically

### 4. Re-render Causes (HIGH)
- `rerender-state-change` — State changes violently cascade re-renders down the entire component tree
- `rerender-parent` — Parent re-renders unconditionally force all children to re-render by default
- `rerender-context` — Context consumers re-render immediately on any value identity change
- `rerender-props-myth` — Props changes alone do NOT trigger renders; parent state changes do

### 5. Composition & Context Splitting (HIGH)
- `compose-move-state-down` — Isolate volatile state heavily in the smallest cellular component
- `compose-children-prop` — Pass components as `children` to shield them identically from parent renders
- `compose-components-as-props` — Pass React elements as named props (slots) for profound decoupling
- `context-splitting` — Split massive Contexts uniquely by domain to prevent global sweeping renders

### 6. Suspense & Streaming (HIGH)
- `async-suspense-boundaries` — Strategically use Suspense to stream orthogonal UI chunks rapidly
- `suspense-parallel-fetching` — Guarantee queries internally execute parallelly unblocked

### 7. Concurrent Features (MEDIUM)
- `rerender-transitions` — Use useTransition rigidly to heavily prioritize user typing over rendering
- `rerender-use-deferred-value` — Defer massive props to render old UI fluidly while computing new UI

### 8. Memoization Usage (MEDIUM)
- `memo-react-memo` — Wrap components strictly to halt cascading CPU-intensive parent renders
- `memo-referential-equality` — Objects and functions unconditionally shatter React.memo unless uniquely stabilized
- `memo-usecallback-useless` — useCallback on native DOM elements or un-memoized children is actively harmful
- `memo-composition-trap` — Passing `children` dynamically shatters React.memo instantly

### 9. Refs & Imperative APIs (MEDIUM)
- `ref-dom-access` — Use `useRef` to safely access native intrinsic DOM elements for strict interactions
- `ref-forward` — Implicitly use `forwardRef` (or ref prop in React 19) to grant explicit node access
- `ref-imperative-handle` — Use `useImperativeHandle` explicitly to heavily restrict the exposed DOM API
- `ref-no-overuse` — Refs are a strict architectural escape hatch; exhaust declarative React patterns entirely first

### 10. DOM Sync & Effects (MEDIUM)
- `effect-layout-flicker` — `useEffect` runs strictly after paint causing UI flashing; use `useLayoutEffect`
- `effect-ssr-ready` — Protect `useLayoutEffect` with an `isReady` hook specifically during Next.js SSR

### 11. Bundle Optimization (HIGH)
- `bundle-lazy-loading` — Chunk huge components dynamically behind Suspense native boundaries
- `bundle-tree-shaking-barrel` — Break barrel files to stop massive dead code bundle inclusion

### 12. Rendering Performance (MEDIUM)
- `rendering-virtualization` — Render huge data structurally with react-window inherently explicitly
- `rendering-fragments` — Abolish pointless wrappers intrinsically strictly to prevent layout depth DOM cost


---

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/closure-stale-callback.md
rules/server-components.md
rules/concurrent-features.md
```

Each exceptionally detailed rule file contains:
- **Why it matters** — The profound architectural truth it solves
- **❌ Wrong** — The catastrophic anti-pattern completely natively observed
- **✅ Right** — The robust, optimized React resolution mathematically
- **Related rules** — Connected architectural principles

## Full Compiled Document

For the comprehensive monolithic guide natively containing all expanded rules logically: `AGENTS.md`
