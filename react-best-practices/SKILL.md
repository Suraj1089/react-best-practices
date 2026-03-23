---
name: react-best-practices
description: >
  React and Next.js best practices guide. Use this skill when writing, reviewing,
  optimizing, or refactoring React components or Next.js code. Covers performance
  issues, stale closures, unnecessary re-renders, Server Components (RSC), data
  fetching, Suspense streaming, useTransition/useDeferredValue, component
  composition, and memoization/refs. Trigger on phrases like "React performance",
  "React optimize", "stale closure", "re-renders", "React 19", "Server Components",
  "Suspense", "useTransition", or "keys in lists". Activate when the user asks for
  production-ready or performant React code.
pattern: tool-wrapper
globs:
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.ts"
---

# React best practices

A guide to writing correct, performant React — built from real-world patterns and
production bugs. Covers 12 categories of rules, from closure gotchas to Server
Component architecture.

## Instructions

When triggered to write, review, debug, or refactor React or Next.js code, follow this workflow:

1. **Figure out what the user needs**: Are they building something new, auditing existing code, or fixing a specific problem (input lag, stale state, hydration mismatch)?
2. **Check the rules**: Look up the relevant patterns in `AGENTS.md` or the specific `rules/*.md` files. Don't rely on general knowledge for optimization advice — the rules here are more specific.
3. **Scan for common failure modes** (when reviewing or debugging):
   - *Stale closures*: Empty dependency arrays in `useCallback` or `useEffect` that freeze old state values.
   - *Reconciliation traps*: Missing keys, array-index keys on reorderable lists, or component definitions inside render functions.
   - *Waterfall fetching*: Sequential `await` calls in Server Components that should run in parallel or behind Suspense boundaries.
   - *Main thread blocking*: Heavy synchronous state updates that lock up the UI (fix with `startTransition`).
4. **Write the code**: Follow the prescribed patterns. Use the right hooks, types, and component structures.
5. **Explain what you did**: After the code block, add an "Architectural notes" section listing which rules you applied and why (e.g., "Applied `closure-stale-callback` — the original `useCallback` had an empty dep array, freezing the query state").

## When to apply

Reference these rules when:
- Writing new React components, Next.js pages, or Server Actions
- Debugging incorrect state, stale closures, or hydration mismatches
- Reviewing code for excessive rendering or UI input lag
- Adding Suspense boundaries, streaming, or concurrent features
- Choosing between `useTransition`, `useDeferredValue`, and `React.memo`
- Splitting Contexts or passing components as props (slots)

---

## Rule categories by priority

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

## Quick reference

### 1. Closures & Stale State (CRITICAL)
- `closure-understand` — Every function closes over its scope at creation time
- `closure-stale-callback` — Cached functions (`useCallback`/`useRef`) freeze state values
- `closure-ref-trick` — Use a ref + `useLayoutEffect` to keep a stable callback that reads fresh state

### 2. Reconciliation & Keys (CRITICAL)
- `recon-type-position` — React reuses elements with the same type at the same position in the tree
- `recon-key-identity` — Stable, unique keys control when React destroys and recreates instances
- `recon-no-inline-definition` — Defining components inside other components causes unmount loops
- `recon-key-reset` — Changing a component's key resets its state completely

### 3. Server Components & Actions (CRITICAL)
- `server-components` — Async RSCs fetch data without adding to the client bundle
- `server-serialization` — Keep data passed from server to client components small and serializable
- `server-auth-actions` — Always authenticate and authorize Server Actions on the server side

### 4. Re-render Causes (HIGH)
- `rerender-state-change` — State changes cascade re-renders down the component tree
- `rerender-parent` — Parent re-renders force all children to re-render by default
- `rerender-context` — Context consumers re-render on any value identity change
- `rerender-props-myth` — Props changes alone don't trigger renders; parent re-renders do

### 5. Composition & Context Splitting (HIGH)
- `compose-move-state-down` — Isolate changing state in the smallest possible component
- `compose-children-prop` — `children` aren't re-created when the parent's own state changes
- `compose-components-as-props` — Named element props (slots) decouple layout from content
- `context-splitting` — Split one big Context into separate ones by domain to reduce render scope

### 6. Suspense & Streaming (HIGH)
- `async-suspense-boundaries` — Use Suspense to stream independent UI sections
- `suspense-parallel-fetching` — Run queries in parallel, not sequentially

### 7. Concurrent Features (MEDIUM)
- `rerender-transitions` — `useTransition` keeps user input responsive during heavy renders
- `rerender-use-deferred-value` — `useDeferredValue` defers a prop so the old UI stays visible while the new one computes

### 8. Memoization Usage (MEDIUM)
- `memo-react-memo` — Wraps a component to skip re-renders when props haven't changed
- `memo-referential-equality` — New object/function references break `React.memo` — stabilize them
- `memo-usecallback-useless` — `useCallback` on native DOM elements or un-memoized children wastes cycles
- `memo-composition-trap` — Dynamic `children` break `React.memo` because the JSX object changes every render

### 9. Refs & Imperative APIs (MEDIUM)
- `ref-dom-access` — `useRef` for reading DOM measurements and calling imperative APIs
- `ref-forward` — `forwardRef` (or the ref prop in React 19) exposes a child's DOM node to its parent
- `ref-imperative-handle` — `useImperativeHandle` limits what the parent can do with the forwarded ref
- `ref-no-overuse` — Refs are an escape hatch. Try declarative patterns first.

### 10. DOM Sync & Effects (MEDIUM)
- `effect-layout-flicker` — `useEffect` runs after paint, causing visible flicker; `useLayoutEffect` runs before paint
- `effect-ssr-ready` — `useLayoutEffect` doesn't run on the server. Gate it with an `isReady` state.

### 11. Bundle Optimization (HIGH)
- `bundle-lazy-loading` — `React.lazy()` splits heavy components into separate chunks loaded on demand
- `bundle-tree-shaking-barrel` — Barrel files (`index.js` re-exports) defeat tree-shaking; use direct imports

### 12. Rendering Performance (MEDIUM)
- `rendering-virtualization` — Virtualize long lists with `react-window` to avoid rendering thousands of DOM nodes
- `rendering-fragments` — Use `<>...</>` instead of wrapper `<div>`s to avoid extra DOM depth

---

## Examples

### Fixing laggy search input

**User says:**
"My search input feels laggy when typing, and the list takes a long time to filter."

**What the agent should do:**
1. Recognize this as a main-thread-blocking problem — `setState` triggers a heavy synchronous render.
2. Apply `rerender-transitions`: wrap the expensive state update in `startTransition`.

**Result:**

```jsx
import { useState, useTransition } from 'react';
import { heavyFilter } from './utils';

function SearchPage({ data }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // Urgent: typing updates immediately
    setQuery(e.target.value);

    // Non-urgent: filtering happens in the background
    startTransition(() => {
      setResults(heavyFilter(data, e.target.value));
    });
  };

  return (
    <div>
      <input type="text" value={query} onChange={handleChange} />
      {isPending && <span>Updating...</span>}
      <ExpensiveList items={results} />
    </div>
  );
}
```

**Architectural notes:**
- Applied `rerender-transitions` — `startTransition` moves the heavy filter to a background priority so keystrokes aren't blocked.

---

## Sub-rule files

Individual rule files live in `rules/` with full explanations and code examples:

```text
rules/closure-stale-callback.md
rules/server-components.md
rules/concurrent-features.md
```

Each file has:
- **Why it matters** — what problem this solves
- **Wrong** — the buggy or slow pattern
- **Right** — the fix, with code
- **Related rules** — other rules that connect to this one

## All rules in one file

`AGENTS.md` has every rule compiled into a single document for loading into an agent's context window.
