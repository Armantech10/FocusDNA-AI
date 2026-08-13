/**
 * FocusDNA API Base URL Resolver Helper.
 * In local dev: Returns process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
 * In Vercel unified deployment: Returns relative endpoint path when frontend & backend share domain.
 */
export function getApiUrl(path: string): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;

  if (!envUrl) {
    return cleanPath;
  }

  const cleanBase = envUrl.endsWith('/') ? envUrl.slice(0, -1) : envUrl;
  return `${cleanBase}${cleanPath}`;
}
