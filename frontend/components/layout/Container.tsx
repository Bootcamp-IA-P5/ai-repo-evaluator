import React from 'react';
import { Menu } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  centered?: boolean;
}

/**
 * Container component for consistent page layout and max-width control
 */
export const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ className, size = 'xl', centered = true, children, ...props }, ref) => {
    const sizeStyles = {
      sm: 'max-w-2xl',
      md: 'max-w-4xl',
      lg: 'max-w-6xl',
      xl: 'max-w-7xl',
      full: 'max-w-full',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'w-full',
          sizeStyles[size],
          centered && 'mx-auto',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Container.displayName = 'Container';

export interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

/**
 * PageHeader component for consistent page titles and descriptions
 */
export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  action,
  className,
}) => {
  return (
    <div className={cn('mb-8', className)}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">{title}</h1>
          {description && (
            <p className="mt-2 text-sm md:text-base text-gray-600">{description}</p>
          )}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
    </div>
  );
};

PageHeader.displayName = 'PageHeader';

export interface MainLayoutProps {
  sidebar?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  /** Mobile: callback triggered when the hamburger button is pressed */
  onMenuClick?: () => void;
  /** Mobile: title shown in the top bar */
  mobileTitle?: string;
}

/**
 * MainLayout component combining sidebar and main content area.
 * On mobile, renders a top bar with a hamburger button to open the sidebar drawer.
 */
export const MainLayout: React.FC<MainLayoutProps> = ({
  sidebar,
  children,
  className,
  onMenuClick,
  mobileTitle = 'AI Repository Evaluator',
}) => {
  return (
    <div className={cn('flex h-screen bg-gray-50', className)}>
      {sidebar}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Mobile top bar — hidden on md+ */}
        <header className="md:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-200 shrink-0">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="text-base font-semibold text-gray-900 truncate">{mobileTitle}</span>
        </header>
        <main className="flex-1 overflow-y-auto w-full">
          <div className="p-4 md:p-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

MainLayout.displayName = 'MainLayout';
