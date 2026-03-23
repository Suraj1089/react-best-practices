# Full Stack Dev Skills

A curated compilation of advanced AI agent skills, best practice guidelines, and robust architectures across the modern full-stack development ecosystem. 

These modular configurations are designed to provide AI coding assistants with deep contextual awareness, enabling them to strictly adhere to idiomatic patterns, security practices, and performance optimisations.

## 🛠️ Available Skills

### 🐍 [Django Best Practices](./django-best-practices/)
Comprehensive rules and guidelines tailored to modern Django REST API and application development, covering:
- Advanced ORM usage, QuerySet optimisations, and Database Locks
- Architectural patterns (services, selectors)
- Security, Caching, and Asynchronous tasks (Celery/Channels)
- View structure, Serializers, and Testing methodologies

### ⚛️ [React Best Practices](./react-best-practices/)
Strict guidelines mapped to the latest advancements in the React and frontend ecosystem:
- React 19 patterns (Server Components, Suspense, Actions, Transitions)
- Idiomatic component design and decoupling state securely
- Strict typing (TypeScript) boundaries and performance optimisations
- Forms, Fetching architectures, and accessibility considerations

### 🕵️ [Change Critic](./change-critic/)
An AI review and reflection skill aimed at analysing, testing, and reviewing code diffs comprehensively before deployment. Provides robust critique formats and pre-commit checks.

## 🚀 How to Use

Each directory operates as an isolated skill module containing its own `SKILL.md` (or `README.md`). These can be imported directly into your preferred AI agent framework (e.g., OpenClaw, Google's DeepMind Assistants, Vercel v0, Cursor) to apply highly specialised constraints when generating or modifying code bases.

1. Navigate into any specific skill directory (e.g., `react-best-practices/`).
2. Read the `SKILL.md` for specific AI prompts and configuration steps.
3. Import the system descriptions or rules into your agent's custom instructions / context window.
