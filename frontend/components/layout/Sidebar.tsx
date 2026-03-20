'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { LucideIcon, X } from 'lucide-react';

export interface SidebarItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: string | number;
}

export interface SidebarProps {
  title: string;
  subtitle?: string;
  items: SidebarItem[];
  className?: string;
  /** Mobile: whether the sidebar drawer is open */
  mobileOpen?: boolean;
  /** Mobile: callback to close the sidebar drawer */
  onMobileClose?: () => void;
}

/**
 * Sidebar navigation component with active state highlighting.
 * On desktop it sits in the normal flow; on mobile it slides in as a drawer.
 */
export const Sidebar: React.FC<SidebarProps> = ({
  title,
  subtitle,
  items,
  className,
  mobileOpen = false,
  onMobileClose,
}) => {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          // Layout
          'w-80 h-screen bg-white border-r border-gray-200 flex flex-col',
          // Mobile: fixed drawer that slides in/out
          'fixed inset-y-0 left-0 z-50',
          'transform transition-transform duration-300 ease-in-out',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
          // Desktop: back to normal flow, always visible
          'md:relative md:translate-x-0 md:z-auto',
          className
        )}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-start justify-between gap-2">
          <div className="min-w-0">
            <Link href="/dashboard" onClick={onMobileClose} className="inline-flex items-center">
              <Image
                src="/evaluAI.webp"
                alt={title}
                width={140}
                height={44}
                priority
                className="h-9 w-auto object-contain"
              />
            </Link>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
            )}
          </div>
          {/* Close button — mobile only */}
          <button
            className="md:hidden shrink-0 p-1 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            onClick={onMobileClose}
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {items.map((item) => {
            const Icon = item.icon;
            // Match exact path OR any sub-path (e.g. /past-evaluations/42 → /past-evaluations active).
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onMobileClose}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <Icon className="w-5 h-5 shrink-0" />
                <span className="flex-1">{item.label}</span>
                {item.badge && (
                  <span
                    className={cn(
                      'px-2 py-0.5 text-xs font-medium rounded-full',
                      isActive
                        ? 'bg-indigo-200 text-indigo-800'
                        : 'bg-gray-200 text-gray-700'
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

Sidebar.displayName = 'Sidebar';
