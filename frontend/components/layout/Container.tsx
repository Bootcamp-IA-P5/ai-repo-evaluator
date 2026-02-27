import React from 'react';
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          {description && (
            <p className="mt-2 text-base text-gray-600">{description}</p>
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
}

/**
 * MainLayout component combining sidebar and main content area
 */
export const MainLayout: React.FC<MainLayoutProps> = ({
  sidebar,
  children,
  className,
}) => {
  return (
    <div className={cn('flex h-screen bg-gray-50', className)}>
      {sidebar}
      <main className="flex-1 overflow-y-auto">
        <div className="flex justify-center w-full p-8">{children}</div>
      </main>
    </div>
  );
};

MainLayout.displayName = 'MainLayout';
