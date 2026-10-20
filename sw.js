const C="studentai-v6",A=["./","index.html","css/style.css","js/content.js","js/data.js","js/features.js","js/api.js","js/app.js","manifest.webmanifest"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(A)));self.skipWaiting()});
self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))));
self.addEventListener("fetch",e=>{const r=e.request,u=new URL(r.url);if(r.method!=="GET")return;
 if(u.origin===location.origin){e.respondWith(fetch(r).then(x=>{const c=x.clone();caches.open(C).then(k=>k.put(r,c));return x}).catch(()=>caches.match(r).then(x=>x||caches.match("index.html"))));return}
 if(/(^|\.)esm\.run$|cdn\.jsdelivr\.net$|fonts\.(googleapis|gstatic)\.com$/.test(u.host)){e.respondWith(caches.match(r).then(x=>x||fetch(r).then(y=>{const c=y.clone();caches.open(C).then(k=>k.put(r,c));return y})))}});
