'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils/cn';
import { ChevronDown, Check } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

export interface SelectProps {
  label?: string;
  placeholder?: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  disabled?: boolean;
  className?: string;
}

/**
 * Custom Select component with Classroom-style design
 * Features dropdown with search, descriptions, and keyboard navigation
 */
export const Select: React.FC<SelectProps> = ({
  label,
  placeholder = 'Select an option...',
  options,
  value,
  onChange,
  error,
  helperText,
  fullWidth = false,
  disabled = false,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputId = `select-${React.useId()}`;
  const hasError = Boolean(error);

  const selectedOption = options.find((opt) => opt.value === value);

  // Filter options based on search term
  const filteredOptions = options.filter(
    (option) =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      option.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionValue: string) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setSearchTerm('');
  };

  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
      setSearchTerm('');
    }
  };

  return (
    <div
      ref={containerRef}
      className={cn('flex flex-col gap-1.5 relative', fullWidth && 'w-full', className)}
    >
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

      {/* Select trigger button */}
      <button
        type="button"
        id={inputId}
        onClick={toggleDropdown}
        disabled={disabled}
        className={cn(
          'flex items-center justify-between px-4 py-2.5 text-left bg-white border rounded-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-offset-0',
          'disabled:bg-gray-50 disabled:cursor-not-allowed disabled:text-gray-500',
          hasError
            ? 'border-red-300 focus:ring-red-500'
            : isOpen
            ? 'border-indigo-500 ring-2 ring-indigo-500'
            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
        )}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className={selectedOption ? 'text-gray-900' : 'text-gray-400'}>
          {selectedOption?.label || placeholder}
        </span>
        <ChevronDown
          className={cn(
            'w-5 h-5 text-gray-400 transition-transform',
            isOpen && 'transform rotate-180'
          )}
        />
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg top-full">
          {/* Search input */}
          <div className="p-2 border-b border-gray-200">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              autoFocus
            />
          </div>

          {/* Options list */}
          <div className="max-h-60 overflow-y-auto" role="listbox">
            {filteredOptions.length === 0 ? (
              <div className="px-4 py-6 text-center text-gray-500">
                No options found
              </div>
            ) : (
              filteredOptions.map((option) => {
                const isSelected = option.value === value;
                
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => !option.disabled && handleSelect(option.value)}
                    disabled={option.disabled}
                    className={cn(
                      'w-full px-4 py-3 text-left transition-colors flex items-start gap-3',
                      'hover:bg-indigo-50 focus:bg-indigo-50 focus:outline-none',
                      'disabled:opacity-50 disabled:cursor-not-allowed',
                      isSelected && 'bg-indigo-50'
                    )}
                    role="option"
                    aria-selected={isSelected}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900">{option.label}</div>
                      {option.description && (
                        <div className="mt-0.5 text-sm text-gray-500">
                          {option.description}
                        </div>
                      )}
                    </div>
                    {isSelected && (
                      <Check className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* Error or helper text */}
      {hasError && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {!hasError && helperText && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

Select.displayName = 'Select';
