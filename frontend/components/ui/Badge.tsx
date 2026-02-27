import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
}

/**
 * Badge component for status indicators and labels
 * Supports multiple color variants and optional status dot
 */
export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      className,
      variant = 'neutral',
      size = 'md',
      dot = false,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center gap-1.5 font-medium rounded-full';

    const variantStyles = {
      success: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800',
      info: 'bg-blue-100 text-blue-800',
      neutral: 'bg-gray-100 text-gray-800',
    };

    const sizeStyles = {
      sm: 'text-xs px-2 py-0.5',
      md: 'text-sm px-2.5 py-1',
      lg: 'text-base px-3 py-1.5',
    };

    const dotColors = {
      success: 'bg-green-500',
      warning: 'bg-yellow-500',
      error: 'bg-red-500',
      info: 'bg-blue-500',
      neutral: 'bg-gray-500',
    };

    return (
      <span
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className={cn('w-2 h-2 rounded-full', dotColors[variant])}
            aria-hidden="true"
          />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

// Predefined badge variants for common use cases

export const CompletedBadge: React.FC<{ className?: string }> = ({ className }) => (
  <Badge variant="success" dot className={className}>
    completed
  </Badge>
);

export const InProgressBadge: React.FC<{ className?: string }> = ({ className }) => (
  <Badge variant="info" dot className={className}>
    in progress
  </Badge>
);

export const ErrorBadge: React.FC<{ className?: string }> = ({ className }) => (
  <Badge variant="error" dot className={className}>
    error
  </Badge>
);

export const PendingBadge: React.FC<{ className?: string }> = ({ className }) => (
  <Badge variant="warning" dot className={className}>
    pending
  </Badge>
);
