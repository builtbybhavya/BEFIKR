importScripts("/assets/baat-banao/recordings.js?v=2");
const CACHE = "befikr-shell-v55";
const SHELL = ["/", "/styles.css?v=38", "/app.js?v=35", "/manifest.webmanifest", "/assets/befikr-favicon.png?v=2", "/assets/befikr-icon-180.png?v=2", "/assets/befikr-icon-192.png?v=2", "/assets/befikr-icon-512.png?v=2", "/assets/befikr-icon-maskable-512.png?v=2", "/assets/baat-banao/incoming-ringtone.mp3", "/assets/baat-banao/recordings.js?v=2", "/assets/baat-banao/recordings.json", ...globalThis.BEFIKR_RECORDINGS.assets];
self.addEventListener("install", event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL))));
self.addEventListener("activate", event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))));
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/api/")) return;
  event.respondWith(fetch(event.request).then(response => {
    const copy = response.clone();
    if(response.status===200)caches.open(CACHE).then(cache => cache.put(event.request, copy)).catch(()=>{});
    return response;
  }).catch(() => caches.match(event.request).then(cached => cached || (event.request.mode === "navigate" ? caches.match("/") : Response.error()))));
});
