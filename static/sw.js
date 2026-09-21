// Service Worker của nguyenta.com. Chỉ làm một việc: giữ sẵn trên máy người
// đọc những file KHÔNG BAO GIỜ đổi nội dung, để chuyển trang không phải hỏi
// lại máy chủ.
//
// Vì sao cần: GitHub Pages chỉ cho trình duyệt giữ file 10 phút (max-age=600)
// và không cho đổi. Quá 10 phút, mỗi lần chuyển trang trình duyệt lại hỏi máy
// chủ font còn dùng được không; trên mạng điện thoại lượt hỏi đó đủ lâu để chữ
// nháy từ font dự phòng sang font thật.
//
// File nào được giữ: file có mã băm trong tên, do Hugo và tools/fonts/build.py
// sinh ra: /fonts/p/*.<băm>.woff2, /css/*.<băm>.css, /js/*.<băm>.js, ảnh đã xử
// lý *_hu_<băm>.webp. Nội dung đổi thì tên đổi, nên giữ mãi không bao giờ cũ.
// HTML và mọi thứ khác đi thẳng ra mạng như không có Service Worker.
//
// Tắt khẩn cấp: thay toàn bộ file này bằng
//   self.addEventListener("install", () => self.skipWaiting());
//   self.addEventListener("activate", () => self.registration.unregister());
// rồi deploy; lần mở trang sau, máy người đọc tự gỡ nó đi.

const CACHE = "gen-immutable-v1";
const MAX_ENTRIES = 400;
const IMMUTABLE = /\.[0-9a-f]{12,}\.(?:woff2|css|js)$|_hu_[0-9a-f]{8,}\.(?:webp|jpe?g|png)$/;

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      for (const key of await caches.keys()) {
        if (key !== CACHE) await caches.delete(key);
      }
      await self.clients.claim();
    })(),
  );
});

// Bộ nhớ không phình mãi: quá MAX_ENTRIES thì bỏ những file cũ nhất (thứ tự
// keys() là thứ tự lúc cất vào)
async function trim(cache) {
  const keys = await cache.keys();
  for (const key of keys.slice(0, Math.max(0, keys.length - MAX_ENTRIES))) {
    await cache.delete(key);
  }
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || !IMMUTABLE.test(url.pathname)) return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE);
      const hit = await cache.match(request, { ignoreVary: true });
      if (hit) return hit;
      const response = await fetch(request);
      if (response.ok) {
        event.waitUntil(cache.put(request, response.clone()).then(() => trim(cache)));
      }
      return response;
    })(),
  );
});
