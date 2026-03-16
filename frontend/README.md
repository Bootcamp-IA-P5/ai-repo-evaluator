<div align="center">

# EvaluAI Frontend

### AI-powered repository evaluation interface with rubric-driven workflows

![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black?style=for-the-badge&logo=next.js)
![React](https://img.shields.io/badge/React-19.2.3-20232A?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

## Table of Contents

- [Product Overview](#product-overview)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Tech Stack](#tech-stack)
- [Pages and User Flows](#pages-and-user-flows)
- [UI System and Components](#ui-system-and-components)
- [API Integration and Proxy Strategy](#api-integration-and-proxy-strategy)
- [Data and AI Configuration Flow](#data-and-ai-configuration-flow)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Run and Build](#run-and-build)
- [Docker Setup](#docker-setup)
- [Responsive Design Guidelines](#responsive-design-guidelines)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Product Overview

EvaluAI Frontend is the presentation and interaction layer for the repository evaluation platform.

It enables users to:
- Create evaluations from GitHub repositories.
- Upload briefing documents (PDF).
- Select AI provider/model or use server defaults.
- Review historical evaluations with filtering and CSV export.
- Inspect detailed AI findings and markdown-based summaries.
- Manage rubrics, criteria, and scoring levels.

---

## Architecture at a Glance

```mermaid
flowchart LR
  U[User Browser] --> N[Next.js App Router]
  N --> UI[Pages + Components]
  N --> P[/api/v1 Proxy Route Handler]
  P --> B[FastAPI Backend]
  B --> DB[(PostgreSQL)]
  B --> AI[Gemini / Groq / OpenAI]
```

### Why this architecture?

- Browser always talks to `localhost:3000`.
- Backend calls are proxied server-side via `app/api/v1/[...path]/route.ts`.
- Reduces CORS complexity and avoids leaking internal Docker hostnames.

---

## Tech Stack

| Category | Tools |
|---|---|
| Framework | Next.js 16.1.6 (App Router) |
| UI Runtime | React 19.2.3 |
| Language | TypeScript 5 |
| Styling | Tailwind CSS v4 |
| Markdown | react-markdown + remark-gfm |
| HTTP | Native `fetch` (main) + Axios client abstraction |
| Charts | Recharts |
| Icons | Lucide React |

---

## Pages and User Flows

### Main Routes

| Route | Purpose | File |
|---|---|---|
| `/` | Redirect entry point | `app/page.tsx` |
| `/dashboard` | KPIs, recent evaluations, summary cards | `app/(app)/dashboard/page.tsx` |
| `/new-evaluation` | Create evaluation flow | `app/(app)/new-evaluation/page.tsx` |
| `/rubrics` | Rubric CRUD and criteria-level editing | `app/(app)/rubrics/page.tsx` |
| `/past-evaluations` | Search/filter/export historical evaluations | `app/(app)/past-evaluations/page.tsx` |
| `/past-evaluations/[id]` | Detailed report and findings analysis | `app/(app)/past-evaluations/[id]/page.tsx` |
| `/components-demo` | Internal UI showcase | `app/components-demo/page.tsx` |

### Navigation Layout

- App shell is mounted in `app/(app)/layout.tsx`.
- `Sidebar` provides desktop navigation + mobile drawer behavior.
- `MainLayout` handles responsive top bar and content container.

---

## UI System and Components

### Design Goals

- Consistent visual language.
- Reusable components with typed props.
- Fast page assembly with minimal duplication.
- Responsive-first behavior for mobile and desktop.

### UI Components (`components/ui`)

| Component | Role |
|---|---|
| `Alert` | Feedback banners (success/error/info) |
| `Badge` | Status labels and semantic tags |
| `Button` | Variants, sizes, loading states |
| `Card` | Section containers and composable layout |
| `DropdownMenu` | Action menus |
| `FileUpload` | PDF upload interaction |
| `Input` | Text input with validation helpers |
| `MarkdownRenderer` | Safe rendering for AI-generated markdown |
| `Modal` | Dialog interactions |
| `RubricBuilder` | Criteria and levels creation/editing |
| `SearchBar` | Query input with UX helpers |
| `Select` | Controlled select/dropdown |
| `StatCard` | KPI visualization blocks |
| `Table` | Reusable tabular data composition |
| `Textarea` | Multiline input |

### Layout Components (`components/layout`)

| Component | Role |
|---|---|
| `MainLayout` | Application shell |
| `Sidebar` | Main navigation |
| `PageHeader` | Consistent page title/description/actions |
| `Container` | Width and spacing control |

For deep component usage examples, see `components/UI_COMPONENTS.md`.

---

## API Integration and Proxy Strategy

### Core principle

All frontend pages call relative routes (`/api/v1/...`) and do **not** call backend host directly from the browser.

### Proxy layer

- File: `app/api/v1/[...path]/route.ts`
- Handles request forwarding to `BACKEND_URL`.
- Preserves methods and body for redirect-safe behavior (`307/308`).
- Applies header filtering and safe redirect validation.

### API client utilities

- `lib/api/client.ts` contains Axios client setup.
- Most current page calls use native `fetch`.
- Shared file upload logic lives in `lib/services/file-upload.ts`.

---

## Data and AI Configuration Flow

### New Evaluation Flow

1. Fetch available rubrics.
2. Upload briefing PDF (`/api/v1/evaluations/briefings`).
3. Build payload with:
   - `rubric_id`
   - `repo_url`
   - `briefing_path`
   - optional `ai_provider` + `ai_model`
4. Optionally attach `X-API-Key` if user provides BYOK key.
5. Submit evaluation request.

### AI Provider Options in UI

- Default server config (empty provider/model)
- Gemini
- Groq
- OpenAI

Behavior:
- Empty provider/model => backend defaults.
- Custom provider/model => frontend includes both values.
- API key is optional at UI level, backend rules decide final validation.

---

## Project Structure

```text
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (app)/
│   │   ├── layout.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── new-evaluation/page.tsx
│   │   ├── rubrics/page.tsx
│   │   ├── past-evaluations/page.tsx
│   │   └── past-evaluations/[id]/page.tsx
│   ├── api/v1/[...path]/route.ts
│   └── components-demo/page.tsx
├── components/
│   ├── layout/
│   └── ui/
├── lib/
│   ├── api/client.ts
│   ├── services/file-upload.ts
│   └── utils/
├── hooks/
├── public/
├── types/
├── next.config.ts
├── package.json
└── README.md
```

---

## Environment Variables

Start from example file:

```bash
cp .env.example .env
```

### Supported variables

| Variable | Scope | Description | Default |
|---|---|---|---|
| `BACKEND_URL` | Server-side only | Upstream FastAPI URL for proxy route | `http://backend:8000` |

### Security notes

- Do not persist API keys in frontend env files.
- BYOK keys are entered at runtime by users.
- Keep sensitive values out of Git commits.

---

## Run and Build

### Prerequisites

- Node.js 20+
- npm 10+

### Development

```bash
npm install
npm run dev
```

### Production build

```bash
npm run build
npm run start
```

### Linting

```bash
npm run lint
```

---

## Docker Setup

### Development image

- File: `Dockerfile.dev`
- Uses `node:20-slim`
- Exposes port `3000`
- Supports hot reload with mounted volumes

### Production image

- File: `Dockerfile.prod`
- Multi-stage build
- Next.js standalone output
- Non-root runtime user
- Built-in container healthcheck

### Important env reload tip

When environment variables change, recreate containers:

```bash
docker compose -f docker-compose.dev.yml up -d --force-recreate frontend
```

---

## Responsive Design Guidelines

The frontend is optimized for both desktop and narrow mobile widths.

### What is covered

- Sidebar drawer and mobile top navigation.
- Adaptive paddings across dashboard/list/detail pages.
- Wrapped badges and metadata rows.
- Markdown hardening for:
  - long links
  - long code snippets
  - markdown tables in narrow viewports

### Recommended manual checks

- Viewport: 320x824
- Pages: dashboard, past evaluations list, evaluation detail
- Validate no clipped text and no horizontal overflow except intentional code/table scroll

---

## Troubleshooting

### 1) Backend appears unreachable

Symptoms:
- Proxy returns 502.

Checks:
- Backend container is up.
- `BACKEND_URL` is correct.
- Backend route `/api/v1/...` responds.

### 2) Changes not visible in browser

Actions:
1. Hard refresh: `Ctrl+Shift+R`
2. Restart frontend container
3. Recreate container if env changed

### 3) AI evaluation returns provider auth errors

Checks:
- Provider key validity in backend runtime env
- Conflicting duplicate env keys
- Whether a custom `X-API-Key` is overriding server key

---

## Contributing

1. Branch from `development`.
2. Keep code typed and component-driven.
3. Reuse existing UI primitives before creating new ones.
4. Run lint before opening PR.
5. Include screenshots for UI changes.

---

<div align="center">

### Built for maintainability, speed, and a reliable AI-evaluation workflow.

</div>
