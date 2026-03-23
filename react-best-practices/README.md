# React Best Practices (Agent Skill)

An agent skill that teaches AI coding assistants how to write better React and Next.js code.

When your agent writes, refactors, or reviews React code, this skill catches common mistakes — stale closures, missing keys, wasted renders, barrel file bloat — and steers toward patterns that actually work in production.

## What it covers

12 categories, ranked by how badly they bite you when ignored:

1. **Closures & Stale State** — cached callbacks that silently freeze old values
2. **Reconciliation & Keys** — React reusing the wrong component instances
3. **Server Components & RSC** — data fetching without shipping code to the client
4. **Re-render Causes** — why your tree keeps rendering when nothing changed
5. **Composition & Context** — solving performance problems with component structure, not memoization
6. **Suspense & Streaming** — loading states that don't block the whole page
7. **Bundle Optimization** — lazy loading and tree-shaking mistakes
8. **Concurrent Features** — `useTransition` and `useDeferredValue` for responsive UIs
9. **Memoization Usage** — when `React.memo` helps vs. when it's a waste
10. **Refs & Imperative APIs** — DOM access without fighting the framework
11. **DOM Sync & Effects** — `useLayoutEffect` vs `useEffect` and SSR gotchas
12. **Rendering Performance** — virtualization and avoiding unnecessary DOM depth

## Project structure

- `SKILL.md` — The manifest agents read to decide when to activate this skill and how to use it
- `AGENTS.md` — All rules compiled into one file, designed to fit in an agent's context window
- `rules/` — Individual deep-dive files per topic, each with a "why it matters" section, a wrong example, and a correct one
- `react-best-practices.skill` — Packaged archive of everything above

## Quality scoring

This skill is structured around four quality dimensions used by agent skill registries:

- **Discovery** — File globs (`**/*.jsx`, etc.) and trigger phrases tell agents exactly when to load this skill
- **Implementation** — Step-by-step workflow with specific failure modes to scan for, not vague advice
- **Structure** — Standard frontmatter, clear sections, and a `tool-wrapper` design pattern
- **Expertise** — Real architectural traps (stale closures, reconciliation bugs, waterfall fetching) instead of generic "write clean code" advice
