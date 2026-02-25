import { type ClassValue, clsx } from 'clsx';

/**
 * Utility para combinar classNames de Tailwind CSS
 * Útil para componentes con estilos condicionales
 * 
 * @example
 * cn('text-base', isActive && 'font-bold', className)
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
