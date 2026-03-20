import React from 'react';
import { cn } from '@/lib/utils/cn';

// Base Table component
export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  variant?: 'default' | 'bordered' | 'striped';
}

export const Table = React.forwardRef<HTMLTableElement, TableProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variantStyles = {
      default: '',
      bordered: '[&_td]:border [&_th]:border',
      striped: '[&_tbody_tr:nth-child(odd)]:bg-gray-50',
    };

    return (
      <div className="w-full overflow-auto">
        <table
          ref={ref}
          className={cn('w-full text-sm text-left', variantStyles[variant], className)}
          {...props}
        />
      </div>
    );
  }
);

Table.displayName = 'Table';

// Table Header
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  // Extends HTMLAttributes with no additional props
}

export const TableHeader = React.forwardRef<HTMLTableSectionElement, TableHeaderProps>(
  ({ className, ...props }, ref) => {
    return (
      <thead
        ref={ref}
        className={cn('bg-gray-50 border-b border-gray-200', className)}
        {...props}
      />
    );
  }
);

TableHeader.displayName = 'TableHeader';

// Table Body
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  // Extends HTMLAttributes with no additional props
}

export const TableBody = React.forwardRef<HTMLTableSectionElement, TableBodyProps>(
  ({ className, ...props }, ref) => {
    return (
      <tbody
        ref={ref}
        className={cn('[&_tr:last-child]:border-0', className)}
        {...props}
      />
    );
  }
);

TableBody.displayName = 'TableBody';

// Table Footer
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface TableFooterProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  // Extends HTMLAttributes with no additional props
}

export const TableFooter = React.forwardRef<HTMLTableSectionElement, TableFooterProps>(
  ({ className, ...props }, ref) => {
    return (
      <tfoot
        ref={ref}
        className={cn('bg-gray-50 border-t border-gray-200 font-medium', className)}
        {...props}
      />
    );
  }
);

TableFooter.displayName = 'TableFooter';

// Table Row
export interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  hoverable?: boolean;
}

export const TableRow = React.forwardRef<HTMLTableRowElement, TableRowProps>(
  ({ className, hoverable = false, ...props }, ref) => {
    return (
      <tr
        ref={ref}
        className={cn(
          'border-b border-gray-200 transition-colors',
          hoverable && 'hover:bg-gray-50',
          className
        )}
        {...props}
      />
    );
  }
);

TableRow.displayName = 'TableRow';

// Table Head Cell
export interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  sortable?: boolean;
}

export const TableHead = React.forwardRef<HTMLTableCellElement, TableHeadProps>(
  ({ className, sortable = false, children, ...props }, ref) => {
    return (
      <th
        ref={ref}
        className={cn(
          'px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider',
          sortable && 'cursor-pointer select-none hover:bg-gray-100',
          className
        )}
        {...props}
      >
        {children}
      </th>
    );
  }
);

TableHead.displayName = 'TableHead';

// Table Cell
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  // Extends TdHTMLAttributes with no additional props
}

export const TableCell = React.forwardRef<HTMLTableCellElement, TableCellProps>(
  ({ className, ...props }, ref) => {
    return (
      <td
        ref={ref}
        className={cn('px-4 py-3 text-gray-900', className)}
        {...props}
      />
    );
  }
);

TableCell.displayName = 'TableCell';

// Empty State Component
export interface TableEmptyProps {
  message?: string;
  colSpan?: number;
}

export const TableEmpty: React.FC<TableEmptyProps> = ({
  message = 'No data available',
  colSpan = 1,
}) => {
  return (
    <TableRow>
      <TableCell colSpan={colSpan} className="text-center py-12 text-gray-500">
        {message}
      </TableCell>
    </TableRow>
  );
};

TableEmpty.displayName = 'TableEmpty';
