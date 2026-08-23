module.exports = {
  globDirectory: "dist",
  globPatterns: ["**/*.{js,css,html,json,png,ico,woff2,ttf}"],
  globIgnores: ["sw.js"],
  swDest: "dist/sw.js",
  cleanupOutdatedCaches: true,
  clientsClaim: true,
  skipWaiting: true,
  navigateFallback: "/offline.html",
  navigateFallbackDenylist: [/^\/api\//],
  maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
  runtimeCaching: [{ urlPattern: /^https:\/\/overpass-api\.de\//, handler: "NetworkOnly" }]
};
