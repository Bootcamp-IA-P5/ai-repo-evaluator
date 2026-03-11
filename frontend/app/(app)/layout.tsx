'use client';

import React, { useState } from 'react';
import { LayoutDashboard, FilePlus2, BookOpen, History } from 'lucide-react';
import { Sidebar } from '@/components/layout';
import { MainLayout } from '@/components/layout';
import type { SidebarItem } from '@/components/layout';

const NAV_ITEMS: SidebarItem[] = [
  {
    label: 'Panel',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Nueva Evaluación',
    href: '/new-evaluation',
    icon: FilePlus2,
  },
  {
    label: 'Rúbricas',
    href: '/rubrics',
    icon: BookOpen,
  },
  {
    label: 'Evaluaciones Pasadas',
    href: '/past-evaluations',
    icon: History,
  },
];

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <MainLayout
      onMenuClick={() => setMobileOpen(true)}
      sidebar={
        <Sidebar
          title="EvaluAI"
          items={NAV_ITEMS}
          mobileOpen={mobileOpen}
          onMobileClose={() => setMobileOpen(false)}
        />
      }
    >
      {children}
    </MainLayout>
  );
}
