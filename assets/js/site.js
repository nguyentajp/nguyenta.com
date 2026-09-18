// JavaScript của cả site. Chỉ bốn việc, việc nào không có phần tử tương ứng
// trên trang thì bỏ qua:
//   1. Kamon tự vẽ khi vào trang chủ lần đầu trong phiên
//   2. Lightbox: bấm ảnh để xem lớn, Esc hoặc bấm nền để đóng, ← → để chuyển
//   3. Video YouTube: chỉ tải iframe khi người đọc bấm phát
//   4. Trang 静: Esc hoặc chạm vào đâu cũng quay lại trang trước

// ── 1. Kamon ────────────────────────────────────────────────────────────────
// Lần thứ hai trở đi trong cùng phiên, kamon hiện sẵn. Người đọc bật
// prefers-reduced-motion thì CSS tự tắt phần animation.
(() => {
  const kamon = document.querySelector(".kamon-draw");
  if (!kamon) return;

  const KEY = "gen-kamon-drawn";
  let drawn = false;
  try {
    drawn = sessionStorage.getItem(KEY) === "1";
  } catch {
    // Trình duyệt chặn sessionStorage (cửa sổ riêng tư): vẽ như lần đầu.
  }
  if (drawn) return;

  kamon.classList.add("is-drawing");
  try {
    sessionStorage.setItem(KEY, "1");
  } catch {
    // Không lưu được thì thôi, chuyển động vẫn chạy đúng một lần trong trang này.
  }
})();

// ── 2. Lightbox ─────────────────────────────────────────────────────────────
// Mỗi ảnh là một link <a class="zoom"> trỏ tới bản lớn, nên không có JS vẫn
// xem được. JS chỉ chặn cú bấm và mở ảnh trong <dialog> thay vì sang trang mới.
(() => {
  const dialog = document.querySelector("dialog.lightbox");
  const links = [...document.querySelectorAll("a.zoom")];
  if (!dialog || links.length === 0) return;

  const img = dialog.querySelector("img");
  const caption = dialog.querySelector("figcaption");
  let current = 0;

  dialog.classList.toggle("is-single", links.length === 1);

  const show = (index) => {
    current = (index + links.length) % links.length;
    const link = links[current];
    const thumb = link.querySelector("img");
    img.src = link.href;
    const w = Number(link.dataset.w) || 3;
    const h = Number(link.dataset.h) || 2;
    img.width = w;
    img.height = h;
    // CSS dùng tỉ lệ này để ảnh vừa khít màn hình, dọc hay ngang đều không bị cắt
    img.style.setProperty("--ratio", w / h);
    img.alt = thumb ? thumb.alt : "";
    caption.textContent = link.dataset.caption || "";
    caption.hidden = !link.dataset.caption;
  };

  links.forEach((link, index) => {
    link.addEventListener("click", (event) => {
      // Ctrl/Cmd + bấm: để trình duyệt mở tab mới như link thường
      if (event.metaKey || event.ctrlKey || event.shiftKey) return;
      event.preventDefault();
      show(index);
      dialog.showModal();
      dialog.focus(); // Tab vẫn đi tới các nút như thường
    });
  });

  dialog.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (button?.dataset.step) show(current + Number(button.dataset.step));
    else if (button?.hasAttribute("data-close") || event.target === dialog) dialog.close();
  });

  dialog.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") show(current - 1);
    if (event.key === "ArrowRight") show(current + 1);
    // <dialog> vốn tự đóng khi bấm Esc, nhưng viết rõ ra để không phụ thuộc
    // vào từng trình duyệt: đây là yêu cầu bắt buộc của lightbox.
    if (event.key === "Escape") dialog.close();
  });

  // Đóng xong thì bỏ ảnh lớn ra khỏi bộ nhớ và trả focus về đúng ảnh vừa xem
  dialog.addEventListener("close", () => {
    img.removeAttribute("src");
    links[current].focus();
  });
})();

// ── 3. Video YouTube ────────────────────────────────────────────────────────
// Nút phát là link tới YouTube, nên không có JS vẫn xem được. Có JS thì thay
// khung thumbnail bằng iframe ngay tại chỗ, dùng tên miền youtube-nocookie.
(() => {
  document.querySelectorAll(".video-frame").forEach((frame) => {
    const play = frame.querySelector(".video-play");
    if (!play) return;

    play.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey) return;
      event.preventDefault();

      const params = new URLSearchParams({ autoplay: "1", rel: "0" });
      if (frame.dataset.start) params.set("start", frame.dataset.start);

      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube-nocookie.com/embed/${frame.dataset.video}?${params}`;
      iframe.title = frame.dataset.title || play.textContent.trim();
      iframe.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      iframe.allowFullscreen = true;
      frame.replaceChildren(iframe);
      frame.classList.add("is-playing");
      iframe.focus();
    });
  });
})();

// ── 4. Trang 静 ─────────────────────────────────────────────────────────────
// Link "Quay lại" trỏ về trang chủ, nên không có JS vẫn ra được. Có JS thì
// quay lại đúng bài người đọc vừa rời đi, nếu họ tới từ chính site này.
(() => {
  const sei = document.querySelector(".sei");
  if (!sei) return;

  const leave = () => {
    let cameFromHere = false;
    try {
      cameFromHere = new URL(document.referrer).origin === location.origin;
    } catch {
      // Không có referrer (mở thẳng link): về trang chủ.
    }
    if (cameFromHere && history.length > 1) history.back();
    else location.href = sei.dataset.home;
  };

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") leave();
  });

  sei.addEventListener("click", (event) => {
    event.preventDefault();
    leave();
  });
})();
