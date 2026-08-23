import type { ReactNode } from "react";
import { ScrollViewStyleReset, useServerDocumentContext } from "expo-router/html";

const registerWorker = `if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) { window.addEventListener('load', function () { var refreshing = false; navigator.serviceWorker.addEventListener('controllerchange', function () { if (refreshing) return; refreshing = true; location.reload(); }); navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' }).then(function (registration) { registration.update(); }).catch(function () {}); }); }`;
export default function Root({ children }: { children: ReactNode }) {
  const { bodyAttributes, bodyNodes, htmlAttributes, headNodes } = useServerDocumentContext();
  return <html lang="en" {...htmlAttributes}><head><meta charSet="utf-8" /><meta httpEquiv="X-UA-Compatible" content="IE=edge" /><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" /><meta name="theme-color" content="#0A4D3A" /><meta name="description" content="Shakti360 Guardian — personal safety without permanent surveillance." /><meta name="apple-mobile-web-app-capable" content="yes" /><meta name="apple-mobile-web-app-status-bar-style" content="default" /><link rel="manifest" href="/manifest.json" /><link rel="apple-touch-icon" href="/shakti360-icon.png" /><ScrollViewStyleReset />{headNodes}<script dangerouslySetInnerHTML={{ __html: registerWorker }} /></head><body {...bodyAttributes}>{children}{bodyNodes}</body></html>;
}
