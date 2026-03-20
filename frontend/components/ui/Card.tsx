import React from 'react';
import { cn } from '@/lib/utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

/**
 * Flexible Card container component
 * Used for grouping content with consistent styling
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'default',
      padding = 'md',
      hoverable = false,
      children,
      ...props
    },
    ref
  ) => {
    const variantStyles = {
      default: 'bg-white border border-gray-200',
      bordered: 'bg-white border-2 border-gray-300',
      elevated: 'bg-white shadow-md',
    };

    const paddingStyles = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    const hoverStyles = hoverable
      ? 'transition-shadow hover:shadow-lg cursor-pointer'
      : '';

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg',
          variantStyles[variant],
          paddingStyles[padding],
          hoverStyles,
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card sub-components for better composition

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  description,
  action,
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn('flex items-start justify-between mb-4', className)}
      {...props}
    >
      <div className="flex-1">
        {title && (
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        )}
        {description && (
          <p className="mt-1 text-sm text-gray-500">{description}</p>
        )}
        {children}
      </div>
      {action && <div className="ml-4">{action}</div>}
    </div>
  );
};

CardHeader.displayName = 'CardHeader';

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  // Extends HTMLAttributes with no additional props
}

export const CardContent: React.FC<CardContentProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('text-gray-700', className)} {...props}>
      {children}
    </div>
  );
};

CardContent.displayName = 'CardContent';

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  divided?: boolean;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  divided = false,
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        'mt-4',
        divided && 'pt-4 border-t border-gray-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

CardFooter.displayName = 'CardFooter';
