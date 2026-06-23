/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }],
  },
  // Ensure the snapshot file ships with the /api/check serverless function.
  experimental: {
    outputFileTracingIncludes: {
      "/api/check": ["./data/snapshot.json"],
    },
  },
};

export default nextConfig;
