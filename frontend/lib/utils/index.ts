/**
 * General utility functions
 */

/**
 * Formats a date to a readable string
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

/**
 * Formats a percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Truncates text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Validates a GitHub repository URL
 * Only accepts URLs with github.com hostname and exactly owner/repo structure
 */
export function isValidGitHubUrl(url: string): boolean {
  try {
    const parsedUrl = new URL(url);
    if (parsedUrl.hostname !== 'github.com' && parsedUrl.hostname !== 'www.github.com') {
      return false;
    }
    const pathSegments = parsedUrl.pathname.split('/').filter(Boolean);
    return pathSegments.length === 2 && pathSegments.every(seg => seg.length > 0);
  } catch {
    return false;
  }
}

/**
 * Extracts owner and repo from a GitHub URL
 * Returns null if the URL is not a valid GitHub repository URL
 */
export function parseGitHubUrl(url: string): { owner: string; repo: string } | null {
  if (!isValidGitHubUrl(url)) {
    return null;
  }
  try {
    const parsedUrl = new URL(url);
    const pathSegments = parsedUrl.pathname.split('/').filter(Boolean);
    return {
      owner: pathSegments[0],
      repo: pathSegments[1].replace(/\.git$/, ''),
    };
  } catch {
    return null;
  }
}
