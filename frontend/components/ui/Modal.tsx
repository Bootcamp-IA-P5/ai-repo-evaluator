'use client';

import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils/cn';
import { X } from 'lucide-react';
import { Button } from './Button';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl';

export interface ModalProps {
  /** Controls whether the modal is visible */
  isOpen: boolean;
  /** Called when the user closes the modal (ESC, backdrop click, or close button) */
  onClose: () => void;
  /** Modal window title shown in the header */
  title: string;
  /** Optional subtitle shown below the title */
  description?: string;
  /** Modal content */
  children: React.ReactNode;
  /** Footer area — typically action buttons */
  footer?: React.ReactNode;
  /** Controls the maximum width of the modal panel */
  size?: ModalSize;
  /** When true, clicking the backdrop does not close the modal */
  disableBackdropClose?: boolean;
  /** When true, pressing ESC does not close the modal */
  disableEscClose?: boolean;
  /** Additional class names for the modal panel */
  className?: string;
}

const SIZE_STYLES: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
};

/**
 * Modal / Dialog component rendered via a React portal.
 *
 * Features:
 * - Renders outside the component tree via createPortal to avoid z-index issues
 * - Closes on ESC keydown (configurable)
 * - Closes on backdrop click (configurable)
 * - Traps scroll on <body> while open
 * - Accessible: role="dialog", aria-modal, aria-labelledby, focus management
 * - Four size variants: sm, md, lg, xl
 * - Composable footer slot for action buttons
 *
 * @example
 * // Confirmation dialog
 * <Modal
 *   isOpen={showDelete}
 *   onClose={() => setShowDelete(false)}
 *   title="Delete rubric"
 *   description="This action cannot be undone."
 *   footer={
 *     <>
 *       <Button variant="outline" onClick={() => setShowDelete(false)}>Cancel</Button>
 *       <Button variant="danger" onClick={handleDelete}>Delete</Button>
 *     </>
 *   }
 * >
 *   <p>Are you sure you want to delete <strong>Full-Stack Web App</strong>?</p>
 * </Modal>
 *
 * @example
 * // Form overlay
 * <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Create rubric" size="lg">
 *   <RubricForm onSubmit={handleSubmit} />
 * </Modal>
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  size = 'md',
  disableBackdropClose = false,
  disableEscClose = false,
  className,
}) => {
  const panelRef = useRef<HTMLDivElement>(null);
  const titleId = `modal-title-${React.useId()}`;

  // Lock body scroll while the modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close on ESC keydown
  useEffect(() => {
    if (!isOpen || disableEscClose) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, disableEscClose, onClose]);

  // Move focus to the modal panel when it opens
  useEffect(() => {
    if (isOpen) {
      panelRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleBackdropClick = () => {
    if (!disableBackdropClose) onClose();
  };

  // Prevent clicks inside the panel from bubbling to the backdrop
  const handlePanelClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return createPortal(
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      aria-modal="true"
      role="dialog"
      aria-labelledby={titleId}
      onClick={handleBackdropClick}
    >
      {/* Semi-transparent overlay */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity"
        aria-hidden="true"
      />

      {/* Modal panel */}
      <div
        ref={panelRef}
        tabIndex={-1}
        onClick={handlePanelClick}
        className={cn(
          'relative w-full bg-white rounded-xl shadow-xl flex flex-col',
          'focus:outline-none',
          'max-h-[90vh]',
          SIZE_STYLES[size],
          className
        )}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 px-6 pt-6 pb-4 border-b border-gray-200">
          <div>
            <h2
              id={titleId}
              className="text-lg font-semibold text-gray-900"
            >
              {title}
            </h2>
            {description && (
              <p className="mt-1 text-sm text-gray-500">{description}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Body — scrollable if content overflows */}
        <div className="px-6 py-4 overflow-y-auto flex-1">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
};

Modal.displayName = 'Modal';

// ---------------------------------------------------------------------------
// ConfirmModal — a ready-made confirmation dialog built on top of Modal
// ---------------------------------------------------------------------------

export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description?: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  /** Use 'danger' for destructive actions like delete */
  confirmVariant?: 'primary' | 'danger';
  isLoading?: boolean;
}

/**
 * ConfirmModal — a pre-built confirmation dialog for destructive or
 * irreversible actions (e.g. deleting a rubric, cancelling an evaluation).
 *
 * @example
 * <ConfirmModal
 *   isOpen={showConfirm}
 *   onClose={() => setShowConfirm(false)}
 *   onConfirm={handleDelete}
 *   title="Delete rubric"
 *   message='Are you sure you want to delete "Full-Stack Web App"? This action cannot be undone.'
 *   confirmLabel="Delete"
 *   confirmVariant="danger"
 * />
 */
export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  isLoading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      description={description}
      size="sm"
      disableBackdropClose={isLoading}
      disableEscClose={isLoading}
      footer={
        <>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={confirmVariant}
            onClick={onConfirm}
            isLoading={isLoading}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-sm text-gray-700">{message}</p>
    </Modal>
  );
};

ConfirmModal.displayName = 'ConfirmModal';
