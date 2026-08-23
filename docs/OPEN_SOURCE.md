# Open-source dependencies

| Dependency | Purpose | License | Limitation / fallback |
|---|---|---|---|
| Expo / React Native | Cross-platform application | MIT | Native capabilities differ by platform |
| FastAPI / Pydantic | Typed API and validation | MIT | Production deployment needs authentication and durable storage |
| OpenStreetMap data | Nearby support locations | ODbL | Community data may be incomplete; listings must be verified |
| Overpass API | OpenStreetMap point-of-interest query | AGPL server / OSM data terms | Public instances are rate-limited; results are cached/provider-swappable in production |
| Expo Location | Foreground device location | MIT | Permission-dependent; no result when denied |

MapLibre is the planned native map renderer. It is not bundled in the Expo Go build because it requires a native development build. The current cross-platform screen uses real OSM results and opens native/web directions without introducing a proprietary paid API.

No paid proprietary safety or location dependency is silently required.
