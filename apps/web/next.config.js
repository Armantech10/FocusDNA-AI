/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL 
          ? `${process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '')}/api/:path*` 
          : 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/health',
        destination: process.env.NEXT_PUBLIC_API_URL 
          ? `${process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '')}/health` 
          : 'http://127.0.0.1:8000/health',
      },
    ];
  },
};

module.exports = nextConfig;
