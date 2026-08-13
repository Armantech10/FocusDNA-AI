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
    // If request comes from local app navigation, auto-provision session cookie
    const referer = request.headers.get('referer');
    if (referer && (referer.includes('localhost') || referer.includes('127.0.0.1'))) {
      const response = NextResponse.next();
      response.cookies.set('focusdna-session', 'active', { path: '/', maxAge: 86400, sameSite: 'lax' });
      return response;
    }

    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|css|js)$).*)'],
};
