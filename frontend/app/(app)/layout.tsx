import React from 'react';
import { LayoutDashboard, FilePlus2, BookOpen, History } from 'lucide-react';
import { Sidebar } from '@/components/layout';
import { MainLayout } from '@/components/layout';
import type { SidebarItem } from '@/components/layout';

const NAV_ITEMS: SidebarItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'New Evaluation',
    href: '/new-evaluation',
    icon: FilePlus2,
  },
  {
    label: 'Rubrics',
    href: '/rubrics',
    icon: BookOpen,
  },
  {
    label: 'Past Evaluations',
    href: '/past-evaluations',
    icon: History,
  },
];

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MainLayout
      sidebar={
        <Sidebar
          title="AI Repository Evaluator"
          items={NAV_ITEMS}
        />
      }
    >
      {children}
    </MainLayout>
  );
}
