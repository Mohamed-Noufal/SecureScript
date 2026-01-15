import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Removed 'output: export' to enable middleware for Clerk authentication
  images: {
    unoptimized: true
  }
};

export default nextConfig;
