/* JOURNEY LENS — simple service worker */
const CACHE = 'jl-v1';
const SHELL = [
  '/',
  '/index.html',
  '/offline.html',
  '/assets/story.css',
  '/assets/story.js',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(SHELL); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (ks) { return Promise.all(ks.map(function (k) { if (k !== CACHE) return caches.delete(k); })); })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== location.origin) return; // fonts, youtube thumbs, etc. -> network

  // Navigations: network first, fall back to cache, then offline page
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(function (r) { var cp = r.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); return r; })
        .catch(function () { return caches.match(req).then(function (r) { return r || caches.match('/offline.html'); }); })
    );
    return;
  }

  // Static assets: cache first, update in background
  e.respondWith(
    caches.match(req).then(function (cached) {
      return cached || fetch(req).then(function (r) {
        if (r && r.ok) { var cp = r.clone(); caches.open(CACHE).then(function (c) { c.put(req, cp); }); }
        return r;
      }).catch(function () { return cached; });
    })
  );
});
