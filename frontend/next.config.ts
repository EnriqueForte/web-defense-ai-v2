import type { NextConfig } from "next";

const requestedApiPort = Number(process.env.WEB_DEFENSE_API_PORT ?? "5000");
const apiPort = Number.isInteger(requestedApiPort) && requestedApiPort >= 1024 && requestedApiPort <= 65535
  ? requestedApiPort
  : 5000;

const nextConfig: NextConfig = {
  devIndicators: false,
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `http://127.0.0.1:${apiPort}/api/v1/:path*` }];
  },
};

export default nextConfig;
