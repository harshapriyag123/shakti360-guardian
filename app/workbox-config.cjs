module.exports = {
  globDirectory: "dist",
  // Route HTML is network-first so a deployment cannot strand users on an
  // old JavaScript bundle. Only the offline document is precached.
  globPatterns: ["**/*.{js,css,json,png,ico,woff2,ttf}", "offline.html"],
  globIgnores: ["sw.js"],
  swDest: "dist/sw.js",
  cleanupOutdatedCaches: true,
  clientsClaim: true,
  skipWaiting: true,
  maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
  runtimeCaching: [
    { urlPattern: ({ request, url }) => request.mode === "navigate" && !url.pathname.startsWith("/api/"), handler: "NetworkFirst", options: { cacheName: "shakti360-pages-v4", networkTimeoutSeconds: 10, expiration: { maxEntries: 24, maxAgeSeconds: 86400 }, precacheFallback: { fallbackURL: "/offline.html" } } },
    { urlPattern: /^https:\/\/overpass-api\.de\//, handler: "NetworkOnly" }
  ]
};
