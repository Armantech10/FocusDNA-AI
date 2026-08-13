import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_ROUTES = [
  '/dashboard',
  '/onboarding',
  '/settings',
  '/focus',
  '/analytics',
  '/focusdna',
  '/insights',
  '/activity',
  '/privacy',
  '/recommendations',
  '/history'
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Never intercept static assets or Next.js internal chunks
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') ||
    pathname === '/favicon.ico'
  ) {
    return NextResponse.next();
  }
  
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname === route || pathname.startsWith(`${route}/`));

  // 2. Check for auth session cookie
  const sessionToken = request.cookies.get('sb-access-token')?.value || 
                       request.cookies.get('focusdna-session')?.value ||
                       request.cookies.get('sb-localhost-auth-token')?.value;

  if (isProtectedRoute && !sessionToken) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|css|js)$).*)'],
};
