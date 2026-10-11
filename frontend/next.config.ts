import type { NextConfig } from "next";

const requestedApiPort = Number(process.env.WEB_DEFENSE_API_PORT ?? "5000");
const apiPort = Number.isInteger(requestedApiPort) && requestedApiPort >= 1024 && requestedApiPort <= 65535
  ? requestedApiPort
  : 5000;

const nextConfig: NextConfig = {
  devIndicators: false,
  async headers() {
    return [{ source: "/:path*", headers: [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "same-origin" },
      { key: "X-Frame-Options", value: "DENY" },
      { key: "Content-Security-Policy", value: "object-src 'none'; base-uri 'none'; frame-ancestors 'none'" },
    ] }];
  },
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `http://127.0.0.1:${apiPort}/api/v1/:path*` }];
  },
};

export default nextConfig;
