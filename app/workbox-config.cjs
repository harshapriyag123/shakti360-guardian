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
  navigateFallback: "/offline.html",
  navigateFallbackDenylist: [/^\/api\//],
  maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
  runtimeCaching: [
    { urlPattern: ({ request }) => request.mode === "navigate", handler: "NetworkFirst", options: { cacheName: "shakti360-pages-v3", networkTimeoutSeconds: 10, expiration: { maxEntries: 24, maxAgeSeconds: 86400 } } },
    { urlPattern: /^https:\/\/overpass-api\.de\//, handler: "NetworkOnly" }
  ]
};
