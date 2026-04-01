import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      { source: '/idsl/:path*', destination: 'http://backend:8000/idsl/:path*' },
      { source: '/twin/:path*', destination: 'http://backend:8000/twin/:path*' },
      { source: '/chat/:path*', destination: 'http://backend:8000/chat/:path*' },
    ];
  },
};

export default nextConfig;
