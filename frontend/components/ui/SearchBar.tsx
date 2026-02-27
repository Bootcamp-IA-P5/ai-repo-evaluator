'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils/cn';
import { Search, X } from 'lucide-react';

export interface SearchBarProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  onSearch?: (value: string) => void;
  onClear?: () => void;
  debounceMs?: number;
  fullWidth?: boolean;
}

/**
 * SearchBar component with debounced input and clear functionality
 * Optimized for searching large datasets without excessive re-renders
 */
export const SearchBar = React.forwardRef<HTMLInputElement, SearchBarProps>(
  (
    {
      className,
      onSearch,
      onClear,
      debounceMs = 300,
      fullWidth = false,
      placeholder = 'Search...',
      disabled,
      ...props
    },
    ref
  ) => {
    const [value, setValue] = useState('');
    const [debouncedValue, setDebouncedValue] = useState('');

    // Debounce the search value
    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, debounceMs);

      return () => {
        clearTimeout(handler);
      };
    }, [value, debounceMs]);

    // Trigger search when debounced value changes
    useEffect(() => {
      onSearch?.(debouncedValue);
    }, [debouncedValue, onSearch]);

    const handleClear = () => {
      setValue('');
      setDebouncedValue('');
      onClear?.();
    };

    return (
      <div className={cn('relative', fullWidth && 'w-full', className)}>
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Search className="w-5 h-5" />
        </div>

        <input
          ref={ref}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            'w-full pl-10 pr-10 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg',
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
            'transition-colors'
          )}
          aria-label="Search"
          {...props}
        />

        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Clear search"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
    );
  }
);

SearchBar.displayName = 'SearchBar';
