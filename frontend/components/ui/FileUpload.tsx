'use client';

import React, { useState, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils/cn';
import { Upload, File, X, AlertCircle } from 'lucide-react';

export interface FileUploadProps {
  label?: string;
  helperText?: string;
  error?: string;
  accept?: string;
  maxSize?: number; // in MB
  onFileSelect?: (file: File | null) => void;
  disabled?: boolean;
  className?: string;
}

/**
 * FileUpload component with drag & drop support
 * Displays file preview and validation feedback
 */
export const FileUpload: React.FC<FileUploadProps> = ({
  label,
  helperText,
  error,
  accept = '.pdf',
  maxSize = 10, // 10MB default
  onFileSelect,
  disabled = false,
  className,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const displayError = error || validationError;

  const handleFile = useCallback(
    (file: File | null) => {
      setValidationError(null);

      if (!file) {
        setSelectedFile(null);
        onFileSelect?.(null);
        return;
      }

      // Validate file type
      if (accept && !accept.split(',').some(
        (type) => file.name.toLowerCase().endsWith(type.trim().toLowerCase())
      )) {
        setValidationError(`Please upload a ${accept} file`);
        setSelectedFile(null);
        onFileSelect?.(null);
        return;
      }

      // Validate file size
      const maxSizeBytes = maxSize * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        setValidationError(`File size must be less than ${maxSize}MB`);
        setSelectedFile(null);
        onFileSelect?.(null);
        return;
      }

      setSelectedFile(file);
      onFileSelect?.(file);
    },
    [maxSize, accept, onFileSelect]
  );

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setValidationError(null);
    onFileSelect?.(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <label className="text-sm font-medium text-gray-700">{label}</label>
      )}

      <div
        onClick={handleClick}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-lg transition-colors cursor-pointer',
          'focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2',
          isDragging && !disabled && 'border-indigo-500 bg-indigo-50',
          displayError && 'border-red-300 bg-red-50',
          !displayError && !isDragging && 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed bg-gray-50'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileInputChange}
          disabled={disabled}
          className="sr-only"
          aria-describedby={displayError ? 'file-error' : helperText ? 'file-helper' : undefined}
        />

        {selectedFile ? (
          <div className="flex items-center gap-3 p-4">
            <div className="shrink-0 p-2 bg-indigo-100 rounded-lg">
              <File className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
            <button
              type="button"
              onClick={handleRemove}
              className="shrink-0 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Remove file"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <div className="p-3 mb-3 bg-gray-100 rounded-full">
              <Upload className="w-6 h-6 text-gray-500" />
            </div>
            <div className="mb-1 text-sm font-medium text-gray-700">
              Drop your PDF here, or{' '}
              <span className="text-indigo-600 hover:text-indigo-700">
                click to browse
              </span>
            </div>
            <p className="text-xs text-gray-500">
              Maximum file size: {maxSize}MB
            </p>
          </div>
        )}
      </div>

      {displayError && (
        <div className="flex items-start gap-2 text-sm text-red-600" id="file-error" role="alert">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{displayError}</span>
        </div>
      )}

      {!displayError && helperText && (
        <p id="file-helper" className="text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

FileUpload.displayName = 'FileUpload';
