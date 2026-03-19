# React Best Practices (Agent Skill)

An advanced AI Agent Skill designed to enforce rigorous, highly optimized architectural and performance best practices for React and Next.js code. 

When your autonomous AI agent or coding assistant writes, refactors, or reviews React code, this skill strictly curates its output to prevent novice-level mistakes (like stale closures, missing keys, useless renders, or anti-patterns) and promotes enterprise-grade solutions.

## 🎯 Features

It spans 12 highly critical React architectural categories:
1. **Closures & Stale State** (CRITICAL)
2. **Reconciliation & Keys** (CRITICAL)
3. **Server Components & RSC** (CRITICAL)
4. **Re-render Causes** (HIGH)
5. **Composition & Context** (HIGH)
6. **Suspense & Streaming** (HIGH)
7. **Bundle Optimization** (HIGH)
8. **Concurrent Features** (MEDIUM)
9. **Memoization Usage** (MEDIUM)
10. **Refs & Imperative APIs** (MEDIUM)
11. **DOM Sync & Effects** (MEDIUM)
12. **Rendering Performance** (MEDIUM)

## 📂 Project Structure

- `SKILL.md`: The manifest file that agents read to know exactly when to trigger this skill, the workflow to analyze user code, the failure modes to hunt for, and how to format their output notes. Designed for a 100/100 automated registry score.
- `AGENTS.md`: A comprehensively compiled, monolithic markdown file meant to be read entirely by an agent context window to get immediate context on all React best practices without needing multiple file reads. 
- `rules/`: A directory with deep-dive markdown files isolated by individual topics (e.g., `closure-stale-callback.md` or `server-components.md`). Each file highlights explicitly *Why it matters*, a `❌ Wrong` example, and a `✅ Right` implementation.
- `react-best-practices.skill`: A bundled, ready-to-use archive containing the completely packaged skill.

## 🚀 How Agents Evaluate Quality

This repository is optimized based on universal AI Agent Quality Scoring systems:
- **Discovery**: Explicit `globs` (`**/*.jsx`, etc.) and exact regex-level triggers.
- **Implementation**: Clear imperative steps, checking exactly what anti-patterns to scan.
- **Structure**: Includes proper Markdown segments like `Instructions`, `Examples`, and accurate YAML frontmatter mapping it to the `tool-wrapper` design pattern.
- **Expertise**: Heavily emphasizes real-world architectural traps rather than generic LLM-style generalizations.
