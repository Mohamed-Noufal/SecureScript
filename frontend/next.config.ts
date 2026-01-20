import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Removed 'output: export' to enable middleware for Clerk authentication
  images: {
    unoptimized: true
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.clerk.accounts.dev https://clerk.browser.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://img.clerk.com; connect-src 'self' https://*.clerk.accounts.dev https://clerk.browser.com https://fvqs7mpjm8.execute-api.us-east-1.amazonaws.com; worker-src 'self' blob:; frame-src 'self' https://*.clerk.accounts.dev;"
          }
        ],
      },
    ];
  },
};

export default nextConfig;
