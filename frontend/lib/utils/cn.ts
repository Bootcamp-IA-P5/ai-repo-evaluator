import { type ClassValue, clsx } from 'clsx';

/**
 * Utility to combine Tailwind CSS classNames
 * Useful for components with conditional styles
 * 
 * @example
 * cn('text-base', isActive && 'font-bold', className)
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
