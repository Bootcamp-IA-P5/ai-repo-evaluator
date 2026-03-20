# UI Components Library

Reusable UI components library for the AI Repository Evaluator frontend. Built with React, TypeScript, and Tailwind CSS.

## Table of Contents

- [Installation](#installation)
- [Components](#components)
  - [Button](#button)
  - [Input](#input)
  - [Select](#select)
  - [Card](#card)
  - [Badge](#badge)
  - [FileUpload](#fileupload)
  - [Table](#table)
  - [SearchBar](#searchbar)
  - [StatCard](#statcard)
- [Layout Components](#layout-components)
  - [Sidebar](#sidebar)
  - [Container](#container)
  - [MainLayout](#mainlayout)

## Installation

All components are located in `components/ui/` and `components/layout/`. Import them as needed:

```tsx
import { Button, Input, Card } from '@/components/ui';
import { Sidebar, Container } from '@/components/layout';
```

## Components

### Button

A versatile button component with multiple variants, sizes, and loading states.

**Props:**
- `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg'
- `isLoading`: boolean
- `leftIcon`, `rightIcon`: React.ReactNode
- `fullWidth`: boolean

**Example:**
```tsx
import { Button } from '@/components/ui';
import { Plus } from 'lucide-react';

<Button variant="primary" size="md" leftIcon={<Plus />}>
  Create New
</Button>

<Button variant="outline" isLoading>
  Loading...
</Button>
```

### Input

Text input component with validation, icons, and helper text support.

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `leftIcon`, `rightIcon`: React.ReactNode
- `fullWidth`: boolean

**Example:**
```tsx
import { Input } from '@/components/ui';
import { Mail } from 'lucide-react';

<Input
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  leftIcon={<Mail className="w-5 h-5" />}
  helperText="We'll never share your email"
  fullWidth
/>

<Input
  label="Username"
  error="This field is required"
/>
```

### Select

Custom select component with Classroom-style design, search functionality, and descriptions.

**Props:**
- `label`: string
- `placeholder`: string
- `options`: SelectOption[]
- `value`: string
- `onChange`: (value: string) => void
- `error`: string
- `helperText`: string

**Example:**
```tsx
import { Select } from '@/components/ui';

const rubrics = [
  {
    value: 'fullstack',
    label: 'Full-Stack Web App',
    description: 'Comprehensive evaluation for full-stack web applications'
  },
  {
    value: 'ml',
    label: 'Machine Learning Project',
    description: 'Evaluation criteria for ML/AI projects'
  }
];

<Select
  label="Evaluation Rubric"
  placeholder="Select a rubric..."
  options={rubrics}
  value={selectedRubric}
  onChange={setSelectedRubric}
  fullWidth
/>
```

### Card

Flexible card container with sub-components for structured content.

**Props:**
- `variant`: 'default' | 'bordered' | 'elevated'
- `padding`: 'none' | 'sm' | 'md' | 'lg'
- `hoverable`: boolean

**Subcomponents:**
- `CardHeader`: Title, description, and action area
- `CardContent`: Main content area
- `CardFooter`: Footer with optional divider

**Example:**
```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui';

<Card variant="elevated">
  <CardHeader
    title="Full-Stack Web App"
    description="Comprehensive evaluation for full-stack applications"
    action={<Button size="sm">Edit</Button>}
  />
  <CardContent>
    <p>5 Criteria • Used 45 times</p>
  </CardContent>
  <CardFooter divided>
    <Button variant="outline" fullWidth>View Details</Button>
  </CardFooter>
</Card>
```

### Badge

Status indicator and label component with predefined variants.

**Props:**
- `variant`: 'success' | 'warning' | 'error' | 'info' | 'neutral'
- `size`: 'sm' | 'md' | 'lg'
- `dot`: boolean (shows colored dot indicator)

**Predefined Badges:**
- `CompletedBadge`
- `InProgressBadge`
- `ErrorBadge`
- `PendingBadge`

**Example:**
```tsx
import { Badge, CompletedBadge } from '@/components/ui';

<Badge variant="success" dot>Active</Badge>
<Badge variant="error" size="sm">Failed</Badge>
<CompletedBadge />
```

### FileUpload

Drag-and-drop file upload component with validation and preview.

**Props:**
- `label`: string
- `accept`: string (e.g., '.pdf')
- `maxSize`: number (in MB)
- `onFileSelect`: (file: File | null) => void
- `error`: string
- `helperText`: string

**Example:**
```tsx
import { FileUpload } from '@/components/ui';

<FileUpload
  label="Project Briefing (PDF)"
  accept=".pdf"
  maxSize={10}
  onFileSelect={(file) => console.log(file)}
  helperText="Maximum file size: 10MB"
/>
```

### Table

Composable table component with header, body, and footer sections.

**Components:**
- `Table`: Main table wrapper
- `TableHeader`, `TableBody`, `TableFooter`: Section components
- `TableRow`: Row component with hover support
- `TableHead`: Header cell (sortable option)
- `TableCell`: Data cell
- `TableEmpty`: Empty state message

**Example:**
```tsx
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableEmpty,
} from '@/components/ui';

<Table variant="default">
  <TableHeader>
    <TableRow>
      <TableHead sortable>Repository</TableHead>
      <TableHead>Score</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {data.length === 0 ? (
      <TableEmpty message="No evaluations found" colSpan={3} />
    ) : (
      data.map((item) => (
        <TableRow key={item.id} hoverable>
          <TableCell>{item.repo}</TableCell>
          <TableCell>{item.score}</TableCell>
          <TableCell><CompletedBadge /></TableCell>
        </TableRow>
      ))
    )}
  </TableBody>
</Table>
```

### SearchBar

Search input with debouncing and clear functionality.

**Props:**
- `onSearch`: (value: string) => void
- `onClear`: () => void
- `debounceMs`: number (default: 300)
- `fullWidth`: boolean

**Example:**
```tsx
import { SearchBar } from '@/components/ui';

<SearchBar
  placeholder="Search by repository or rubric..."
  onSearch={(query) => console.log(query)}
  debounceMs={500}
  fullWidth
/>
```

### StatCard

Metric display card with optional trend indicator.

**Props:**
- `title`: string
- `value`: string | number
- `icon`: LucideIcon
- `iconColor`: string
- `trend`: { value: string, isPositive: boolean, label?: string }

**Example:**
```tsx
import { StatCard } from '@/components/ui';
import { FileText } from 'lucide-react';

<StatCard
  title="Total Evaluations"
  value="127"
  icon={FileText}
  trend={{
    value: '+12%',
    isPositive: true,
    label: 'this month'
  }}
/>
```

## Layout Components

### Sidebar

Navigation sidebar with active state highlighting.

**Props:**
- `title`: string
- `subtitle`: string
- `items`: SidebarItem[] (label, href, icon, badge)

**Example:**
```tsx
import { Sidebar } from '@/components/layout';
import { LayoutDashboard, FileText, BookOpen, History } from 'lucide-react';

const navItems = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'New Evaluation', href: '/evaluate', icon: FileText },
  { label: 'Rubrics', href: '/rubrics', icon: BookOpen, badge: '3' },
  { label: 'Past Evaluations', href: '/history', icon: History },
];

<Sidebar
  title="AI Repository Evaluator"
  items={navItems}
/>
```

### Container

Content container with max-width control.

**Props:**
- `size`: 'sm' | 'md' | 'lg' | 'xl' | 'full'
- `centered`: boolean

**PageHeader Component:**
```tsx
import { Container, PageHeader } from '@/components/layout';
import { Button } from '@/components/ui';

<Container size="xl">
  <PageHeader
    title="Evaluation Rubrics"
    description="Manage evaluation criteria and scoring templates"
    action={<Button>Create Rubric</Button>}
  />
</Container>
```

### MainLayout

Main application layout combining sidebar and content area.

**Example:**
```tsx
import { MainLayout } from '@/components/layout';
import { Sidebar } from '@/components/layout';

<MainLayout sidebar={<Sidebar title="App" items={navItems} />}>
  {/* Page content */}
</MainLayout>
```

## Design Tokens

All components use consistent Tailwind CSS classes:

**Colors:**
- Primary: indigo (600, 700)
- Success: green (100, 600, 800)
- Warning: yellow (100, 600, 800)
- Error: red (100, 300, 500, 600, 800)
- Neutral: gray (50, 100, 200, 300, 400, 500, 600, 700, 900)

**Spacing:**
- Component padding: p-4, p-6, p-8
- Gap between elements: gap-2, gap-3, gap-4

**Typography:**
- Headers: text-xl, text-3xl (font-bold)
- Body: text-sm, text-base
- Labels: text-xs, text-sm (font-medium)

## Accessibility

All components follow accessibility best practices:
- Proper ARIA attributes
- Keyboard navigation support
- Focus indicators
- Screen reader compatibility
- Semantic HTML structure

## TypeScript

All components are fully typed with TypeScript:
- Exported prop interfaces
- Generic type support where applicable
- Strict type checking enabled
