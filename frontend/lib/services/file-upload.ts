/**
 * File upload service — handles briefing PDF uploads to the backend.
 *
 * Sends multipart/form-data requests to POST /api/v1/evaluations/briefings,
 * which is proxied by the Next.js route handler to the FastAPI backend.
 */

export interface UploadResponse {
  success: boolean;
  message?: string;
  data?: {
    file_path: string;
    file_name?: string;
    file_size?: number;
  };
  errors?: string[];
}

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validates a file before uploading it.
 *
 * @param file - The file to validate
 * @param maxSizeMB - Maximum allowed size in megabytes
 * @param allowedExtensions - Array of allowed extensions (e.g. ['.pdf'])
 */
export function validateFile(
  file: File,
  maxSizeMB: number,
  allowedExtensions: string[],
): ValidationResult {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!allowedExtensions.includes(ext)) {
    return {
      isValid: false,
      error: `Only ${allowedExtensions.join(', ')} files are allowed.`,
    };
  }

  const maxBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxBytes) {
    return {
      isValid: false,
      error: `File size must be less than ${maxSizeMB}MB. Current size: ${formatFileSize(file.size)}.`,
    };
  }

  return { isValid: true };
}

/**
 * Formats a byte count into a human-readable string (e.g. "2.3 MB").
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

/**
 * Uploads a PDF briefing file to the backend via the Next.js proxy.
 *
 * The backend stores the file and returns its server-side path, which is then
 * sent as `briefing_path` when creating an evaluation.
 */
export async function uploadBriefingFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/v1/evaluations/briefings', {
    method: 'POST',
    body: formData,
  });

  const json = await res.json().catch(() => ({ success: false, message: 'Invalid response from server' }));

  if (!res.ok) {
    return {
      success: false,
      message: json.message ?? json.detail ?? 'Upload failed',
      errors: json.errors,
    };
  }

  return json as UploadResponse;
}
