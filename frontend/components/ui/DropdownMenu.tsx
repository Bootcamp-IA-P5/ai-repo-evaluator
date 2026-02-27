'use client';

import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils/cn';
import { ChevronRight } from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DropdownMenuItem {
  /** Unique identifier for the item */
  key: string;
  /** Text label displayed in the menu */
  label: string;
  /** Optional icon rendered to the left of the label */
  icon?: React.ReactNode;
  /** When true, renders the item in red to indicate a destructive action */
  destructive?: boolean;
  /** When true, the item is non-interactive and visually dimmed */
  disabled?: boolean;
  /** Called when the item is clicked */
  onClick?: () => void;
}

export interface DropdownMenuGroup {
  /** Optional group header label */
  label?: string;
  items: DropdownMenuItem[];
}

export interface DropdownMenuProps {
  /** The element that triggers the dropdown (e.g. a ⋮ button) */
  trigger: React.ReactNode;
  /** One or more groups of menu items. Use multiple groups to add dividers. */
  groups: DropdownMenuGroup[];
  /** Horizontal alignment of the menu relative to the trigger */
  align?: 'left' | 'right';
  className?: string;
}

// ---------------------------------------------------------------------------
// DropdownMenu component
// ---------------------------------------------------------------------------

/**
 * DropdownMenu — a contextual action menu triggered by any element.
 *
 * Features:
 * - Renders via React portal to avoid z-index / overflow clipping issues
 * - Positions itself below the trigger, aligned left or right
 * - Closes on outside click and ESC keydown
 * - Supports item groups with optional labels and dividers between groups
 * - Supports icons, destructive (red) items, and disabled items
 * - Fully accessible: role="menu", role="menuitem", aria-expanded, keyboard navigation
 *
 * @example
 * // Three-dot menu for a rubric card
 * <DropdownMenu
 *   trigger={
 *     <button className="p-1 rounded hover:bg-gray-100">
 *       <MoreVertical className="w-5 h-5 text-gray-500" />
 *     </button>
 *   }
 *   align="right"
 *   groups={[
 *     {
 *       items: [
 *         { key: 'edit',   label: 'Edit rubric',   icon: <Pencil className="w-4 h-4" />, onClick: handleEdit },
 *         { key: 'duplicate', label: 'Duplicate',  icon: <Copy   className="w-4 h-4" />, onClick: handleDuplicate },
 *       ],
 *     },
 *     {
 *       items: [
 *         { key: 'delete', label: 'Delete rubric', icon: <Trash2 className="w-4 h-4" />, destructive: true, onClick: handleDelete },
 *       ],
 *     },
 *   ]}
 * />
 */
export const DropdownMenu: React.FC<DropdownMenuProps> = ({
  trigger,
  groups,
  align = 'right',
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [menuStyle, setMenuStyle] = useState<React.CSSProperties>({});
  const triggerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Reposition the menu whenever it opens
  useEffect(() => {
    if (!isOpen || !triggerRef.current) return;

    const rect = triggerRef.current.getBoundingClientRect();
    const top = rect.bottom + window.scrollY + 4;

    if (align === 'right') {
      setMenuStyle({
        position: 'absolute',
        top,
        right: window.innerWidth - rect.right - window.scrollX,
      });
    } else {
      setMenuStyle({
        position: 'absolute',
        top,
        left: rect.left + window.scrollX,
      });
    }
  }, [isOpen, align]);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        triggerRef.current?.contains(e.target as Node) ||
        menuRef.current?.contains(e.target as Node)
      ) return;
      setIsOpen(false);
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Close on ESC
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleItemClick = (item: DropdownMenuItem) => {
    if (item.disabled) return;
    item.onClick?.();
    setIsOpen(false);
  };

  const menu = isOpen ? (
    <div
      ref={menuRef}
      role="menu"
      aria-orientation="vertical"
      style={{ ...menuStyle, zIndex: 9999 }}
      className={cn(
        'w-52 bg-white border border-gray-200 rounded-lg shadow-lg py-1',
        className
      )}
    >
      {groups.map((group, groupIndex) => (
        <React.Fragment key={groupIndex}>
          {/* Divider between groups */}
          {groupIndex > 0 && (
            <div className="my-1 border-t border-gray-100" role="separator" />
          )}

          {/* Optional group label */}
          {group.label && (
            <div className="px-3 py-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              {group.label}
            </div>
          )}

          {/* Items */}
          {group.items.map((item) => (
            <button
              key={item.key}
              role="menuitem"
              type="button"
              disabled={item.disabled}
              onClick={() => handleItemClick(item)}
              className={cn(
                'w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors text-left',
                'focus:outline-none focus:bg-gray-50',
                item.destructive
                  ? 'text-red-600 hover:bg-red-50'
                  : 'text-gray-700 hover:bg-gray-50',
                item.disabled && 'opacity-40 cursor-not-allowed pointer-events-none'
              )}
            >
              {item.icon && (
                <span className="shrink-0">{item.icon}</span>
              )}
              <span className="flex-1">{item.label}</span>
              {item.disabled && (
                <ChevronRight className="w-4 h-4 opacity-40" aria-hidden="true" />
              )}
            </button>
          ))}
        </React.Fragment>
      ))}
    </div>
  ) : null;

  return (
    <>
      {/* Trigger wrapper */}
      <div
        ref={triggerRef}
        className="inline-block"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="menu"
        aria-expanded={isOpen}
      >
        {trigger}
      </div>

      {/* Portal-rendered menu */}
      {typeof document !== 'undefined' && menu
        ? createPortal(menu, document.body)
        : null}
    </>
  );
};

DropdownMenu.displayName = 'DropdownMenu';
