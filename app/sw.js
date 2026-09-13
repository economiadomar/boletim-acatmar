/* Service worker do app do VI Fórum ACATMAR */
var CACHE='forum-acatmar-v28';
var SHELL=['./','index.html','app.css?v=28','app.js?v=28','lib/qrcode.min.js','lib/jspdf.umd.min.js','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png','media/hero.jpg','media/emblema-v2.jpg','media/ifsc-continente.jpg','../media/logos/acatmar-branca.png','media/logos/prefeitura-florianopolis.png','media/logos/acatmar.png','media/logos/mundo-mar.png','media/logos/safeboat.png','media/logos/personal-boat-v2.png','media/logos/ifsc.png','media/logos/marina-escola.png','media/logos/okean.svg','media/logos/veleiros-da-ilha.png','media/logos/fortur.png','media/logos/capitania-sc.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return Promise.all(SHELL.map(function(u){return c.add(u).catch(function(){});}));}).then(function(){return self.skipWaiting();}));});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==CACHE;}).map(function(k){return caches.delete(k);}));}).then(function(){return self.clients.claim();}));});
self.addEventListener('fetch',function(e){
  var req=e.request;if(req.method!=='GET')return;
  var url=new URL(req.url);
  if(url.origin!==location.origin){ // fontes e externos: cache oportunista
    e.respondWith(caches.match(req).then(function(r){return r||fetch(req).then(function(res){if(res.ok&&/fonts\.(googleapis|gstatic)\.com/.test(url.host)){var cl=res.clone();caches.open(CACHE).then(function(c){c.put(req,cl);});}return res;}).catch(function(){return r;});}));return;}
  if(/forum\.json/.test(url.pathname)||req.mode==='navigate'||/\/app\/(index\.html)?$/.test(url.pathname)||/\/app\/(app\.js|app\.css|sw\.js)$/.test(url.pathname)){ // dados, página e código: rede primeiro // dados: rede primeiro, cache como reserva
    e.respondWith(fetch(req).then(function(res){var cl=res.clone();caches.open(CACHE).then(function(c){c.put(url.pathname,cl);});return res;}).catch(function(){return caches.match(url.pathname,{ignoreSearch:true}).then(function(r){return r||caches.match(req,{ignoreSearch:true});});}));return;}
  e.respondWith(caches.match(req,{ignoreSearch:false}).then(function(r){return r||fetch(req).then(function(res){if(res.ok&&(/\.(png|jpg|jpeg|webp|svg|css|js)(\?|$)/.test(url.pathname+url.search)||url.pathname.endsWith('/'))){var cl=res.clone();caches.open(CACHE).then(function(c){c.put(req,cl);});}return res;});}).catch(function(){if(req.mode==='navigate')return caches.match('index.html');}));
});
