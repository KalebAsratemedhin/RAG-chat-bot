/**
 * Formats the app name by adding a space before capital letters
 * e.g., "CommunityWise" -> "Community Wise"
 */
export function formatAppName(name: string): string {
  return name.replace(/([a-z])([A-Z])/g, '$1 $2');
}

/**
 * Gets the app name from environment variable with fallback
 */
export function getAppName(): string {
  return process.env.NEXT_PUBLIC_APP_NAME || 'CommunityWise';
}

/**
 * Gets the formatted app name
 */
export function getFormattedAppName(): string {
  return formatAppName(getAppName());
}

