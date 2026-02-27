import React from 'react';
import { cn } from '@/lib/utils/cn';
import { AlertCircle } from 'lucide-react';

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  /** Number of visible text rows (default: 4) */
  rows?: number;
  /** When true, the textarea grows with its content up to maxRows */
  autoResize?: boolean;
  /** Maximum rows when autoResize is enabled */
  maxRows?: number;
}

/**
 * Textarea component — multi-line text input with the same API as Input.
 *
 * Features:
 * - Label, error message, and helper text support
 * - Error state with red border and AlertCircle icon
 * - Optional auto-resize: grows with content, up to maxRows
 * - Fully accessible: aria-invalid, aria-describedby
 * - Consistent visual style with the Input component
 *
 * @example
 * // Basic usage
 * <Textarea
 *   label="Criteria description"
 *   placeholder="Describe what this criterion evaluates..."
 *   rows={4}
 *   fullWidth
 * />
 *
 * // With validation error
 * <Textarea
 *   label="Justification"
 *   error="This field is required"
 *   fullWidth
 * />
 *
 * // Auto-resize (grows with content, max 10 rows)
 * <Textarea
 *   label="Notes"
 *   autoResize
 *   maxRows={10}
 *   fullWidth
 * />
 */
export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      fullWidth = false,
      rows = 4,
      autoResize = false,
      maxRows,
      id,
      disabled,
      onChange,
      ...props
    },
    ref
  ) => {
    const generatedId = React.useId();
    const textareaId = id || `textarea-${generatedId}`;
    const hasError = Boolean(error);

    // Internal ref for auto-resize
    const innerRef = React.useRef<HTMLTextAreaElement | null>(null);

    // Merged ref: supports both callback refs and object refs forwarded from the parent
    const resolvedRef = React.useMemo(() => {
      return (instance: HTMLTextAreaElement | null) => {
        innerRef.current = instance;
        if (typeof ref === 'function') {
          ref(instance);
        } else if (ref) {
          (ref as React.MutableRefObject<HTMLTextAreaElement | null>).current = instance;
        }
      };
    }, [ref]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      if (autoResize && innerRef.current) {
        // Reset height first so shrinking works correctly
        innerRef.current.style.height = 'auto';

        const lineHeight = parseInt(
          window.getComputedStyle(innerRef.current).lineHeight || '24',
          10
        );
        const maxHeight = maxRows ? lineHeight * maxRows : Infinity;
        const newHeight = Math.min(innerRef.current.scrollHeight, maxHeight);

        innerRef.current.style.height = `${newHeight}px`;
        innerRef.current.style.overflowY =
          maxRows && innerRef.current.scrollHeight > maxHeight
            ? 'auto'
            : 'hidden';
      }

      onChange?.(e);
    };

    const textareaStyles = cn(
      'block px-4 py-2.5 text-gray-900 bg-white border rounded-lg transition-colors',
      'focus:outline-none focus:ring-2 focus:ring-offset-0',
      'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
      'resize-y',
      autoResize && 'resize-none overflow-hidden',
      hasError
        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
      fullWidth ? 'w-full' : '',
      className
    );

    return (
      <div className={cn('flex flex-col gap-1.5', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={textareaId}
            className="text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}

        <div className="relative">
          <textarea
            ref={resolvedRef}
            id={textareaId}
            rows={rows}
            disabled={disabled}
            className={textareaStyles}
            aria-invalid={hasError}
            aria-describedby={
              hasError
                ? `${textareaId}-error`
                : helperText
                ? `${textareaId}-helper`
                : undefined
            }
            onChange={handleChange}
            {...props}
          />

          {hasError && (
            <div className="absolute right-3 top-3 text-red-500">
              <AlertCircle className="w-5 h-5" aria-hidden="true" />
            </div>
          )}
        </div>

        {hasError && (
          <p
            id={`${textareaId}-error`}
            className="text-sm text-red-600"
            role="alert"
          >
            {error}
          </p>
        )}

        {!hasError && helperText && (
          <p id={`${textareaId}-helper`} className="text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
