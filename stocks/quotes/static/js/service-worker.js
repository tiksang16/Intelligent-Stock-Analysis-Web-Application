self.addEventListener('install', event => {
    console.log('Service worker installing...');
    //Add a call to skipWaiting here
    self.skipWaiting();
    event.waitUntil(
        //Caching
        caches.open("static").then(cache => {
            console.log('Service Worker: Caching Files');
            return cache.addAll([
                "./"
            ]);
        })
    )
});
  
self.addEventListener('activate', event => {
    console.log('Service worker activating...');
});

self.addEventListener('fetch', event => {
    console.log('Fetching:', event.request.url);
    //return caches response
    event.respondWith(
        caches.match(event.request).then(function(response) {
            if(response) {
                return response;
            } else {
                return fetch(event.request);
            }
        })
    );
});