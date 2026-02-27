'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils/cn';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  X,
} from 'lucide-react';

export type AlertVariant = 'success' | 'error' | 'warning' | 'info';

export interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
  /** Icon to show. Set to false to hide the icon entirely. */
  icon?: React.ReactNode | false;
  /** Additional action element rendered below the message (e.g. a link or button) */
  action?: React.ReactNode;
}

const VARIANT_STYLES: Record<AlertVariant, string> = {
  success: 'bg-green-50 border-green-300 text-green-900',
  error:   'bg-red-50   border-red-300   text-red-900',
  warning: 'bg-yellow-50 border-yellow-300 text-yellow-900',
  info:    'bg-blue-50  border-blue-300  text-blue-900',
};

const TITLE_STYLES: Record<AlertVariant, string> = {
  success: 'text-green-800',
  error:   'text-red-800',
  warning: 'text-yellow-800',
  info:    'text-blue-800',
};

const MESSAGE_STYLES: Record<AlertVariant, string> = {
  success: 'text-green-700',
  error:   'text-red-700',
  warning: 'text-yellow-700',
  info:    'text-blue-700',
};

const DISMISS_STYLES: Record<AlertVariant, string> = {
  success: 'text-green-500 hover:text-green-700 hover:bg-green-100',
  error:   'text-red-500   hover:text-red-700   hover:bg-red-100',
  warning: 'text-yellow-500 hover:text-yellow-700 hover:bg-yellow-100',
  info:    'text-blue-500  hover:text-blue-700  hover:bg-blue-100',
};

const DEFAULT_ICONS: Record<AlertVariant, React.ReactNode> = {
  success: <CheckCircle className="w-5 h-5 text-green-500" aria-hidden="true" />,
  error:   <XCircle     className="w-5 h-5 text-red-500"   aria-hidden="true" />,
  warning: <AlertTriangle className="w-5 h-5 text-yellow-500" aria-hidden="true" />,
  info:    <Info         className="w-5 h-5 text-blue-500"  aria-hidden="true" />,
};

/**
 * Alert component for displaying inline feedback messages.
 *
 * Supports four severity variants (success, error, warning, info),
 * an optional dismiss button, a custom action slot, and full
 * keyboard/screen-reader accessibility via role="alert".
 *
 * @example
 * // Basic usage
 * <Alert variant="success" message="Evaluation submitted successfully." />
 *
 * // With title and dismiss
 * <Alert
 *   variant="error"
 *   title="Something went wrong"
 *   message="Could not reach the API. Please try again."
 *   dismissible
 *   onDismiss={() => setError(null)}
 * />
 *
 * // With a call-to-action
 * <Alert
 *   variant="info"
 *   message="Your session will expire in 5 minutes."
 *   action={<button className="underline text-sm">Extend session</button>}
 * />
 */
export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  message,
  dismissible = false,
  onDismiss,
  className,
  icon,
  action,
}) => {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  const handleDismiss = () => {
    setVisible(false);
    onDismiss?.();
  };

  // Allow callers to hide the icon by passing icon={false}
  const resolvedIcon = icon === false ? null : (icon ?? DEFAULT_ICONS[variant]);

  return (
    <div
      role="alert"
      aria-live="polite"
      className={cn(
        'flex gap-3 rounded-lg border p-4',
        VARIANT_STYLES[variant],
        className
      )}
    >
      {/* Left icon */}
      {resolvedIcon && (
        <div className="flex-shrink-0 mt-0.5">{resolvedIcon}</div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <p className={cn('text-sm font-semibold', TITLE_STYLES[variant])}>
            {title}
          </p>
        )}
        <p className={cn('text-sm', title && 'mt-1', MESSAGE_STYLES[variant])}>
          {message}
        </p>
        {action && <div className="mt-2">{action}</div>}
      </div>

      {/* Dismiss button */}
      {dismissible && (
        <div className="flex-shrink-0">
          <button
            type="button"
            onClick={handleDismiss}
            className={cn(
              'rounded-full p-1 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1',
              DISMISS_STYLES[variant]
            )}
            aria-label="Dismiss alert"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  );
};

Alert.displayName = 'Alert';
