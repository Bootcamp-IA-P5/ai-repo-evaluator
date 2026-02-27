# AI Repo Evaluator - Frontend

Frontend for the AI-powered repository evaluation assistant for the AI bootcamp.

## 🚀 Technologies

- **[Next.js 16.1.6](https://nextjs.org/)** - React framework with App Router
- **[TypeScript](https://www.typescriptlang.org/)** - Typed JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Axios](https://axios-http.com/)** - HTTP client
- **[Lucide React](https://lucide.dev/)** - Icons
- **[Recharts](https://recharts.org/)** - Charts

## 📁 Project Structure

```
frontend/
├── app/                     # Next.js App Router
│   ├── layout.tsx          # Main layout
│   ├── page.tsx            # Home page
│   ├── components-demo/    # UI components showcase
│   └── globals.css         # Global styles
├── components/             # React components
│   ├── ui/                # Reusable UI components (Button, Input, Select, etc.)
│   ├── layout/            # Layout components (Sidebar, Container, etc.)
│   └── forms/             # Form components
├── lib/                   # Utilities and configurations
│   ├── api/              # API client and endpoints
│   └── utils/            # Utility functions
├── types/                # Shared TypeScript types
├── hooks/                # Custom React Hooks
├── public/               # Static files
└── .env.local           # Environment variables (do not commit)
```

## 🎨 UI Components Library

A comprehensive set of reusable UI components built with React, TypeScript, and Tailwind CSS.

### Available Components

#### Basic Components
- **Button** - Multiple variants (primary, secondary, outline, ghost, danger), sizes, and loading states
- **Input** - Text input with validation, icons, and helper text
- **Select** - Custom dropdown with Classroom-style design and search functionality
- **Badge** - Status indicators with color variants and optional dot
- **Card** - Flexible container with header, content, and footer sections
- **FileUpload** - Drag-and-drop file upload with validation
- **Table** - Composable table with header, body, and footer
- **SearchBar** - Search input with debouncing and clear functionality
- **StatCard** - Metric display card with optional trend indicators

#### Layout Components
- **Sidebar** - Navigation sidebar with active state highlighting
- **Container** - Content container with max-width control
- **PageHeader** - Page title and description component
- **MainLayout** - Main application layout structure

### Usage Example

```tsx
import { Button, Input, Select, Card, Badge } from '@/components/ui';
import { Sidebar, Container, PageHeader } from '@/components/layout';
import { Plus } from 'lucide-react';

// Button with icon
<Button variant="primary" leftIcon={<Plus />}>
  Create New
</Button>

// Input with validation
<Input
  label="Repository URL"
  placeholder="https://github.com/user/repo"
  error="Invalid URL"
  fullWidth
/>

// Custom Select with search
<Select
  label="Select Rubric"
  options={rubricOptions}
  value={selected}
  onChange={setSelected}
  fullWidth
/>
```

For complete documentation and examples, see:
- **[UI Components Documentation](./components/UI_COMPONENTS.md)** - Comprehensive component guide
- **[Components Demo](/components-demo)** - Live interactive showcase (run dev server)

## 🛠️ Installation

### Prerequisites

- Node.js 20.x LTS
- npm 10.x

### Steps

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your values:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run in development mode**
   ```bash
   npm run dev
   ```
   The application will be available at [http://localhost:3000](http://localhost:3000)

## 📜 Available Scripts

```bash
npm run dev      # Run development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run linter
```

## 🔌 Backend Integration

The frontend communicates with the FastAPI backend via Axios.

- **Base URL**: Configured in `NEXT_PUBLIC_API_URL`
- **API Client**: `lib/api/client.ts`

### Main endpoints (example)

```typescript
import apiClient from '@/lib/api/client';

// Get rubrics
const rubrics = await apiClient.get('/api/rubrics');

// Evaluate repository
const evaluation = await apiClient.post('/api/evaluate', {
  rubricId,
  repositoryUrl,
  // ...
});
```

## 🎨 Styling with Tailwind CSS

Use Tailwind classes directly in components:

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Hello world!
</div>
```

For conditional styles, use the `cn` utility:

```tsx
import { cn } from '@/lib/utils/cn';

<div className={cn(
  'base-styles',
  isActive && 'active-styles',
  className
)}>
  Content
</div>
```

## 📊 Using Recharts

Simple chart example:

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const data = [
  { name: 'Criteria 1', score: 80 },
  { name: 'Criteria 2', score: 95 },
];

<BarChart width={500} height={300} data={data}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="score" fill="#8884d8" />
</BarChart>
```

## 🔧 Development

### Create a new component

```bash
# UI Component
touch components/ui/Button.tsx

# Form Component
touch components/forms/EvaluationForm.tsx
```

### Add TypeScript types

Edit `types/index.ts` to add new shared types.

### Custom Hooks

Create custom hooks in the `hooks/` folder:

```typescript
// hooks/useEvaluation.ts
export function useEvaluation() {
  // Your logic here
}
```

## 🐳 Docker

The Dockerfile will be created and managed by the backend team.

Expected configuration:
- **Port**: 3000
- **Base image**: `node:20-slim`

## 📝 Notes

- Environment variables must have the `NEXT_PUBLIC_` prefix to be available in the client
- Do not commit `.env.local` to the repository (already in `.gitignore`)
- Use TypeScript for all new components

## 🤝 Contributing

1. Create branch from `develop`
2. Make changes
3. Commit following conventional commits
4. Create pull request

## 📧 Contact

**Project Team**: ai-repo-evaluator@company.com
