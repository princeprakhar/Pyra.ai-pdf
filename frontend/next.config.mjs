import { dirname } from "path";
import { fileURLToPath } from "url";

/** Fix `__dirname` for ES modules */
const __dirname = dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*", // FastAPI backend
      },
    ];
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": `${__dirname}/src`, // Fix __dirname issue
    };
    return config;
  },
};

export default nextConfig;
