// Service Worker mínimo — su único trabajo es cumplir el requisito técnico
// que necesitan los navegadores para ofrecer "Instalar app". No cachea
// agresivamente para no complicar las actualizaciones futuras.
const CACHE_NOMBRE = "oraculo-astral-v1";

self.addEventListener("install", function (evento) {
  self.skipWaiting();
});

self.addEventListener("activate", function (evento) {
  self.clients.claim();
});

self.addEventListener("fetch", function (evento) {
  // Simplemente deja pasar todas las peticiones a la red normal —
  // no interceptamos nada, solo cumplimos el requisito de tener un
  // Service Worker activo para que "Agregar a pantalla de inicio" aparezca.
  evento.respondWith(fetch(evento.request).catch(function () {
    return caches.match(evento.request);
  }));
});
