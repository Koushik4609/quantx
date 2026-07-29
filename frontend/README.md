# Frontend — QuantX Dashboard

Comprehensive frontend README for the QuantX dashboard and UI components. This document is intended to be long-form (suitable for printing) and covers project purpose, architecture, local development, component guidelines, styling, testing, build and deployment, performance, accessibility, i18n, observability, contributor guidelines, and appendices with examples and templates.

Table of contents

1. Introduction and Purpose
2. Project Structure
3. Design Principles
4. Tech Stack
5. Getting Started (Quick Start)
6. Local Development
7. Component Architecture and Conventions
8. State Management
9. Styling and Theming
10. Accessibility (a11y)
11. Internationalization (i18n)
12. Forms and Validation
13. Data Fetching and Caching
14. Real-time and WebSocket Integration
15. Routing and Navigation
16. Authentication and Authorization
17. Testing (Unit, Integration, E2E)
18. CI/CD and Deployment
19. Performance Optimization
20. Security
21. Observability and Monitoring
22. Release Process
23. Contributor Guidelines
24. Code Review Checklist
25. Common Patterns and Anti-Patterns
26. Migration Guide (to new versions)
27. Troubleshooting
28. Appendix A — Example Components
29. Appendix B — Example Configs and Env
30. Appendix C — Design Tokens and Tokens Reference
31. Appendix D — Accessibility Checklist
32. Appendix E — Useful Scripts and Tools
33. Appendix F — Glossary
34. Appendix G — Resources and Further Reading
35. Appendix H — License and Third-party Notices
36. Contact and Support

---

1. Introduction and Purpose

This frontend repository contains the dashboard and UI used to visualize backtests, live trading runs, metrics, and system status for QuantX. The goals for the frontend are:

- Provide intuitive, responsive visualizations of experiments and account state
- Be performant and accessible
- Support large datasets and real-time updates
- Serve as a monitoring and control plane for research and production

Audience: researchers, traders, developers, ops

---

2. Project Structure

A typical structure for the frontend lives under the `frontend/` folder. The following layout represents conventions used across the project:

- frontend/
  - public/                # static assets (favicon, static html)
  - src/
    - assets/              # images, fonts
    - components/          # reusable UI components
    - features/            # domain feature modules (dashboard, trades)
    - hooks/               # reusable React hooks
    - pages/               # top-level pages (routing targets)
    - services/            # API client wrappers & adapters
    - store/               # state management (Redux / Zustand / etc.)
    - styles/              # global styles, tokens, themes
    - utils/               # helper functions
    - tests/               # frontend tests that are not co-located
    - App.tsx              # root component
    - main.tsx             # entrypoint
  - package.json
  - tsconfig.json
  - vite.config.ts        # or webpack config
  - README.md

Notes:
- Keep components small and focused. Prefer composition over inheritance.
- Follow a feature-first decomposition when adding new pages.

---

3. Design Principles

- Predictability: Interactions should behave consistently.
- Discoverability: Key features should be easily discoverable.
- Resilience: UI should degrade gracefully when data or network is unavailable.
- Performance: Prioritize critical rendering paths and avoid jank.

Design tokens and theme variables are centralized to enable consistent styling across components and dark/light mode support.

---

4. Tech Stack

- Framework: React (17/18)
- Build: Vite (or Webpack if legacy)
- Language: TypeScript
- Styling: CSS Modules, Tailwind CSS, or Styled Components (project choice)
- State: Redux Toolkit or Zustand
- Data fetching: React Query (TanStack Query) or SWR
- Testing: Vitest / Jest for unit tests, React Testing Library, Playwright/Cypress for E2E
- Linting & formatting: ESLint, Prettier, TypeScript

---

5. Getting Started (Quick Start)

Prerequisites:
- Node 16+ or recommended LTS
- npm or yarn

Install dependencies:

```bash
cd frontend
npm ci
# or
# yarn install --frozen-lockfile
```

Run dev server:

```bash
npm run dev
```

Open http://localhost:5173 (or the console-provided URL)

Build for production:

```bash
npm run build
```

Serve production build locally:

```bash
npm run preview
```

---

6. Local Development

Branching and workflow
- Create feature branches: feature/<short-desc>
- Open PRs against develop/main

Environment variables
- Rename `.env.example` to `.env` and fill in values
- Common variables: VITE_API_URL, VITE_WS_URL, NODE_ENV

Dev tooling
- Use `pnpm`, `yarn`, or `npm` as the repo standard (choose one)
- Use `vite` for HMR
- Run type checks with `tsc --noEmit` as part of CI

Debugging
- Browser devtools: React DevTools, Redux DevTools
- Performance: Lighthouse, Chrome Performance tab

---

7. Component Architecture and Conventions

Component types
- Presentational components: pure UI, no side effects
- Container components: orchestrate data and state
- Hooks: encapsulate reusable logic

File naming
- Use PascalCase for components (SymbolList.tsx)
- Use .tsx extension for components that render JSX
- Keep related styles co-located next to components

Props and types
- Strictly type props using TypeScript interfaces
- Prefer `children` typing and explicit prop interfaces

Example component template

```tsx
import React from 'react'

export interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary'
}

export const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary' }) => {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  )
}
```

Storybook
- Use Storybook to document and browse components during development
- Stories provide examples and edge cases for each component

---

8. State Management

Patterns
- Local state with React.useState/useReducer for component state
- Global state using Redux Toolkit or Zustand
- Server-state and caching handled by React Query

Redux Toolkit suggestions
- Use createSlice for reducers
- Use RTK Query for auto-generated API hooks

Avoid putting server-state in Redux unless needed for cross-cutting concerns.

---

9. Styling and Theming

Approaches
- CSS Modules for encapsulation
- Tailwind for utility-first rapid styling
- Styled Components or Emotion for theme-able component styling

Design tokens
- Keep tokens in `src/styles/tokens.ts` or a JSON file
- Example tokens: colors, spacing, typography, radii, z-indexes

Theming
- Provide a ThemeProvider that maps tokens to CSS variables
- Implement accessible color contrast for both light and dark themes

---

10. Accessibility (a11y)

Goals
- Follow WCAG 2.1 AA where practical
- Keyboard navigability for all interactive elements
- Proper ARIA roles and labels

Checklist
- All buttons and links are reachable by keyboard
- Color is not the only cue for information
- Focus outlines visible and logical
- Semantic HTML is preferred (nav, main, header, footer)
- Images include `alt` text

Testing tools
- axe-core, eslint-plugin-jsx-a11y
- Manual testing with keyboard and screen readers (NVDA, VoiceOver)

---

11. Internationalization (i18n)

Implementation
- Use i18next or react-intl for translation management
- Extract strings into locale files (en.json, fr.json)

Runtime
- Support RTL (right-to-left) layout changes dynamically
- Format numbers and dates using `Intl` APIs

Localization workflow
- Keep keys stable and human-readable, avoid inline messages in code
- Use Crowdin or Lokalise for collaborative translation if needed

---

12. Forms and Validation

Libraries
- React Hook Form for performance and minimal rerenders
- Yup / Zod for schema validation

Pattern
- Keep forms controlled where necessary
- Use debounced validation for heavy checks (e.g., server-side validation)

Accessibility
- Associate labels with inputs
- Provide clear error messages and ARIA-live regions for screen readers

---

13. Data Fetching and Caching

Patterns
- Use React Query / TanStack Query for server-state with built-in caching
- Use query keys carefully to avoid stale data

Error handling
- Global error boundary for unexpected errors
- Retry strategies for transient failures

Optimistic updates
- Use optimistic updates for actions with quick perceived response
- Reconcile with server state when mutation completes

---

14. Real-time and WebSocket Integration

Use cases
- Live PnL updates, trade fills, market ticks

Implementation
- Keep WebSocket connection logic in `services/wsClient.ts`
- Reconnect with exponential backoff
- Throttle or debounce high-frequency updates before rendering

Security
- Authenticate WS connections using short-lived tokens (JWT)

---

15. Routing and Navigation

Libraries
- React Router v6 recommended

Best practices
- Maintain route definitions in a central `routes` file
- Use code-splitting (lazy + Suspense) for large pages
- Keep URLs meaningful and bookmarkable

---

16. Authentication and Authorization

Flow
- Use OAuth or token-based API authentication
- Store tokens in HttpOnly secure cookies (preferred) or in-memory

Role-based access
- Implement RBAC checks both on frontend and backend
- Hide UI elements based on permissions but always validate on server

Logout and token refresh
- Handle refresh tokens securely on server side where possible

---

17. Testing (Unit, Integration, E2E)

Unit tests
- Use Vitest/Jest and React Testing Library
- Test components for accessibility and edge cases

Integration tests
- Mock API responses and test flows across components

E2E
- Use Playwright or Cypress to test critical user journeys
- Automate smoke tests for deployments

Test data
- Use fixtures for stable tests
- Reset application state between tests

Coverage
- Enforce coverage thresholds in CI (e.g., 80% lines)

---

18. CI/CD and Deployment

CI pipeline
- Install, lint, type-check, run tests, build
- Example GitHub Actions:

```yaml
name: Frontend CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
        with:
          version: 7
      - run: pnpm install
      - run: pnpm test -- --coverage
      - run: pnpm build
```

Deployment
- Host static site on Netlify, Vercel, GitHub Pages, or S3+CloudFront
- Use separate builds for staging and production

Cache busting
- Use content-hash filename generation from the build process

---

19. Performance Optimization

Critical render path
- Minimize JavaScript and CSS for initial load
- Use server-side rendering (SSR) or prerendering if SEO or first-paint matters

Code splitting
- Split routes and heavy components

Lazy loading
- Defer images and charts not visible on initial load

Metric tracking
- Track LCP, CLS, FID in production using web-vitals

---

20. Security

Common practices
- Sanitize user input
- Protect against XSS, CSRF, and clickjacking
- Use CSP headers and secure cookies

Dependencies
- Keep npm packages updated
- Run automated dependency scans (Dependabot)

Secrets
- Never commit secrets; use secret managers in CI

---

21. Observability and Monitoring

Client telemetry
- Capture errors (Sentry), performance metrics, and usage events

Logging
- Centralize logs if running SSR or server-side APIs

Alerts
- Configure alerts for build failures, high error rates, or regressions

---

22. Release Process

Semantic versioning
- Use tags and changelogs for releases

Release steps
- Merge PR into main
- CI builds and tests
- Create release tag and artifacts

Rollback
- Keep previous build artifacts for quick rollback

---

23. Contributor Guidelines

How to contribute
- Fork, branch, open PR
- Include tests for new code
- Fill out PR template with testing and impact notes

Code of conduct
- Be respectful and inclusive in discussions

---

24. Code Review Checklist

Before approving PR
- Does code meet linting and type checks?
- Are new functions covered by tests?
- Are performance and accessibility considerations addressed?
- Is the change scope small and well-described?

---

25. Common Patterns and Anti-Patterns

Patterns
- Use hooks for stateful logic
- Use controlled inputs only when needed

Anti-patterns
- Mutating props
- Heavy computations inside render (useMemo/useCallback appropriately)

---

26. Migration Guide (to new versions)

Breaking changes
- Document breaking changes in CHANGELOG.md
- Provide migration steps and codemods where possible

Strategy
- Keep backward compatibility via feature flags

---

27. Troubleshooting

Common problems
- Dev server not starting: check Node version and clear cache
- Type errors: run `tsc --noEmit` to surface issues

Debugging tips
- Reproduce with minimal steps and share logs when opening issues

---

28. Appendix A — Example Components

1) Chart component (high-level)
- Use lightweight charting libraries like Recharts, Chart.js, or Apache ECharts
- Render many series efficiently by limiting DOM nodes

2) Trade Table
- Virtualize long lists with react-window / react-virtualized
- Support column resizing and sorting

3) Notifications
- Use a toast system for transient messages
- Persist critical alerts for visibility

4) Experiment Detail Page
- Show run metadata, PnL chart, positions, blotter, and logs

---

29. Appendix B — Example Configs and Env

.env.example

VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com/ws
VITE_APP_NAME=QuantX Dashboard

package.json scripts

- "dev": "vite"
- "build": "vite build"
- "preview": "vite preview"
- "test": "vitest"

---

30. Appendix C — Design Tokens Reference

tokens.json

{
  "colors": {
    "brand": "#1F6FEB",
    "background": "#FFFFFF",
    "surface": "#F3F4F6",
    "text": "#0F172A"
  },
  "spacing": { "xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32 },
  "radius": { "sm": 4, "md": 8, "lg": 16 }
}

---

31. Appendix D — Accessibility Checklist

- Contrast ratios meet WCAG AA
- All images have alt text
- Keyboard navigation works end-to-end
- Screen reader testing for key pages

---

32. Appendix E — Useful Scripts and Tools

- npm run lint
- npm run format
- npm run test:unit
- npm run test:e2e
- npm run storybook

---

33. Appendix F — Glossary

- PnL: Profit and Loss
- Blotter: list of executed trades
- Fill: match of an order to market liquidity

---

34. Appendix G — Resources and Further Reading

- React docs: https://reactjs.org/
- Vite docs: https://vitejs.dev/
- TypeScript docs: https://www.typescriptlang.org/
- Accessibility: https://www.w3.org/WAI/standards-guidelines/wcag/

---

35. Appendix H — License and Third-party Notices

This frontend may include third-party libraries. Consult the LICENSE and NOTICE files for details.

---

36. Contact and Support

For questions about the frontend, open an issue or discuss on the project's communication channels. Include reproduction steps, environment, and logs.

---

This README is intentionally verbose to form the basis of a long printable document. If you want, I can:
- Split this into multiple detailed markdown files under frontend/docs/
- Auto-generate Storybook stories for example components
- Add diagrams and screenshots

