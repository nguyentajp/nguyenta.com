// JavaScript của cả site. Mỗi việc một khối, việc nào không có phần tử tương
// ứng trên trang thì bỏ qua:
//   1. Kamon tự vẽ khi vào trang chủ lần đầu trong phiên
//   2. Lightbox: bấm ảnh để xem lớn, Esc hoặc bấm nền để đóng, ← → để chuyển
//   3. Video YouTube: chỉ tải iframe khi người đọc bấm phát
//   4. Trang 凪: Esc hoặc chạm vào đâu cũng quay lại trang trước
//   5. Furigana: nút chọn hiện, chạm để xem, tắt
//   6. Nút giao diện sáng tối
//   7. Hàng ngang cuộn (Bài viết liên quan): nút ‹ ›
//   8. Ô đăng ký bản tin ở chân trang (giao diện mẫu, chưa gửi đi đâu)
//   9. Khung giải thích tiết khí: mở khi rê chuột (máy tính có chuột)
//  10. Đồng hồ Osaka và TP.HCM ở chân trang

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

// ── 4. Trang 凪 ─────────────────────────────────────────────────────────────
// Link "Quay lại" trỏ về trang chủ, nên không có JS vẫn ra được. Có JS thì
// quay lại đúng bài người đọc vừa rời đi, nếu họ tới từ chính site này. Trang
// bảo trì và trang 404 mượn giao diện 凪 nhưng không có data-leave, nên bỏ qua.
(() => {
  const nagi = document.querySelector(".nagi[data-leave]");
  if (!nagi) return;

  const leave = () => {
    let cameFromHere = false;
    try {
      cameFromHere = new URL(document.referrer).origin === location.origin;
    } catch {
      // Không có referrer (mở thẳng link): về trang chủ.
    }
    if (cameFromHere && history.length > 1) history.back();
    else location.href = nagi.dataset.leave;
  };

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") leave();
  });

  nagi.addEventListener("click", (event) => {
    event.preventDefault();
    leave();
  });
})();

// ── 5. Furigana ─────────────────────────────────────────────────────────────
// Chế độ nằm ở <html data-furigana>, CSS dựa vào đó để hiện hoặc ẩn. Đoạn
// script trong head.html đã đặt sẵn lựa chọn cũ; ở đây chỉ đổi và lưu lại
// cho các bài sau.
(() => {
  const root = document.documentElement;
  const buttons = [...document.querySelectorAll("[data-furigana-mode]")];
  if (buttons.length === 0) return;

  const KEY = "gen-furigana";
  const sync = () => {
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.furiganaMode === root.dataset.furigana));
    });
  };
  sync();

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      root.dataset.furigana = button.dataset.furiganaMode;
      try {
        localStorage.setItem(KEY, button.dataset.furiganaMode);
      } catch {
        // Không lưu được (cửa sổ riêng tư): chế độ vẫn đúng trong bài này.
      }
      document.querySelectorAll("ruby.is-shown").forEach((ruby) => ruby.classList.remove("is-shown"));
      sync();
    });
  });

  // Chế độ "chạm để xem": chạm vào một chữ để hiện hoặc ẩn cách đọc của chữ đó.
  // Trên máy tính, rê chuột là hiện (CSS lo).
  document.querySelector(".post-body")?.addEventListener("click", (event) => {
    if (root.dataset.furigana !== "tap") return;
    event.target.closest("ruby")?.classList.toggle("is-shown");
  });
})();

// ── 6. Giao diện sáng tối ───────────────────────────────────────────────────
// Mặc định theo cài đặt của máy. Bấm nút thì sang bên kia; nếu bên đó trùng
// với cài đặt của máy thì xoá lựa chọn đã lưu, để site lại tự theo máy (người
// đọc đổi máy sang tối lúc đêm thì site cũng tối theo).
(() => {
  const button = document.querySelector(".theme-toggle");
  if (!button) return;

  const root = document.documentElement;
  const KEY = "gen-theme";
  const system = matchMedia("(prefers-color-scheme: dark)");
  const metas = document.querySelectorAll('meta[name="theme-color"]');
  const systemScheme = () => (system.matches ? "dark" : "light");

  // data-scheme cho CSS chọn biểu tượng; nhãn nút nói việc sẽ xảy ra khi bấm;
  // màu thanh địa chỉ trên điện thoại đi theo lựa chọn nếu có.
  const render = () => {
    const chosen = root.dataset.theme;
    const scheme = chosen || systemScheme();
    root.dataset.scheme = scheme;
    const label = scheme === "dark" ? button.dataset.labelLight : button.dataset.labelDark;
    button.setAttribute("aria-label", label);
    button.title = label;
    metas.forEach((meta) => {
      if (!chosen) meta.media = `(prefers-color-scheme: ${meta.dataset.scheme})`;
      else meta.media = meta.dataset.scheme === chosen ? "all" : "not all";
    });
  };

  button.addEventListener("click", () => {
    const next = root.dataset.scheme === "dark" ? "light" : "dark";
    const followSystem = next === systemScheme();
    // Tạm tắt hiệu ứng đổi màu khi rê chuột, để cả trang đổi màu cùng lúc thay
    // vì menu và link phai chậm theo sau nền
    root.classList.add("is-switching-theme");
    requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove("is-switching-theme")));
    if (followSystem) delete root.dataset.theme;
    else root.dataset.theme = next;
    try {
      if (followSystem) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, next);
    } catch {
      // Không lưu được (cửa sổ riêng tư): giao diện vẫn đổi trong trang này.
    }
    render();
  });

  system.addEventListener("change", render);
  render();
})();

// ── 7. Hàng ngang cuộn ──────────────────────────────────────────────────────
// Hàng vẫn cuộn được bằng vuốt, bàn di chuột hay Shift + lăn chuột khi không
// có JS. JS chỉ thêm hai nút ‹ ›, hiện khi hàng dài hơn khung, mỗi lần bấm
// trượt đúng một khung.
(() => {
  document.querySelectorAll("[data-rail]").forEach((rail) => {
    const track = rail.querySelector(".rail-track");
    const nav = rail.querySelector(".rail-nav");
    if (!track || !nav) return;
    const [prev, next] = nav.querySelectorAll("button");
    const reduce = matchMedia("(prefers-reduced-motion: reduce)");

    const update = () => {
      const max = track.scrollWidth - track.clientWidth;
      nav.hidden = max <= 1;
      prev.disabled = track.scrollLeft <= 1;
      next.disabled = track.scrollLeft >= max - 1;
    };

    nav.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-step]");
      if (!button) return;
      track.scrollBy({
        left: Number(button.dataset.step) * track.clientWidth,
        behavior: reduce.matches ? "auto" : "smooth",
      });
    });

    track.addEventListener("scroll", update, { passive: true });
    new ResizeObserver(update).observe(track);
    update();
  });
})();

// ── 8. Bản tin ──────────────────────────────────────────────────────────────
// Hai trạng thái, do params.newsletter.id trong hugo.toml quyết định.
//  - Có dịch vụ: JS gửi ngầm sang Kit (Kit mở CORS, trả JSON), người đọc ở lại
//    trang và thấy lời nhắn ngay dưới ô. Mạng lỗi thì gửi form như thường, sang
//    trang của Kit. Không có JS thì form cũng POST thẳng như thế.
//  - Chưa có (data-news-mock): footer.html khoá fieldset để không JS thì không
//    bấm gửi được; có JS thì mở khoá cho xem giao diện, bấm Đăng ký chỉ hiện
//    dòng "chưa mở", email không được gửi hay lưu ở đâu cả.
(() => {
  const form = document.querySelector("[data-news]");
  if (!form) return;
  const mock = form.hasAttribute("data-news-mock");
  const email = form.querySelector("#news-email");
  if (mock) form.querySelector("fieldset").disabled = false;

  // Trình duyệt báo lỗi ô nhập bằng ngôn ngữ của MÁY ("Please fill out this
  // field."), không theo ngôn ngữ trang. Thay bằng câu tiếng Việt / tiếng Nhật
  // lấy từ data-msg-* (i18n, đặt ở _partials/footer.html).
  const say = () => {
    email.setCustomValidity("");
    if (email.validity.valueMissing) {
      email.setCustomValidity(form.dataset.msgRequired);
    } else if (email.validity.typeMismatch) {
      email.setCustomValidity(form.dataset.msgInvalid);
    }
  };
  // invalid: lúc trình duyệt sắp hiện bóng nhắn. input: xoá lời nhắn cũ đi,
  // không thì ô cứ ở trạng thái sai dù người đọc đã sửa.
  email.addEventListener("invalid", say);
  email.addEventListener("input", say);

  const status = form.querySelector(".news-status");
  if (mock) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      status.hidden = false;
    });
    return;
  }

  const fieldset = form.querySelector("fieldset");
  const show = (text) => {
    status.textContent = text;
    status.hidden = false;
  };
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    fieldset.disabled = true;
    let result;
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });
      result = await response.json();
    } catch {
      // Không tới được Kit từ đây (mạng, chặn quảng cáo…): gửi như form thường.
      // form.submit() không phát lại sự kiện submit nên không lặp.
      form.submit();
      return;
    }
    fieldset.disabled = false;
    if (result.status === "failed") {
      show(form.dataset.msgFail);
      email.focus();
    } else {
      show(form.dataset.msgDone);
      form.reset();
    }
  });
})();

// ── 9. Tiết khí ─────────────────────────────────────────────────────────────
// Khung giải thích là popover của HTML: bấm tên tiết khí là mở, không cần JS,
// và khung nằm giữa màn hình (điện thoại, bàn phím). Với chuột, JS mở khung
// ngay khi rê vào tên, đặt sát dưới tên, rời chuột thì đóng; bấm vào tên thì
// khung ở lại cho tới khi bấm ra ngoài hoặc Esc.
(() => {
  const button = document.querySelector("[data-sekki]");
  const note = document.getElementById("sekki-note");
  if (!button || !note) return;

  const GAP = 8;
  const EDGE = 12;
  let timer;
  let pinned = false;

  const isOpen = () => note.matches(":popover-open");
  const anchored = () => note.classList.contains("is-anchored");

  // Dưới tên tiết khí, căn giữa theo tên; sát mép màn hình thì dịch vào trong,
  // thiếu chỗ bên dưới thì lật lên trên
  const place = () => {
    const rect = button.getBoundingClientRect();
    const width = note.offsetWidth;
    const height = note.offsetHeight;
    const x = Math.max(EDGE, Math.min(rect.left + rect.width / 2 - width / 2, innerWidth - width - EDGE));
    let y = rect.bottom + GAP;
    if (y + height > innerHeight - EDGE) y = Math.max(EDGE, rect.top - GAP - height);
    note.style.setProperty("--x", `${x}px`);
    note.style.setProperty("--y", `${y}px`);
  };

  const open = () => {
    clearTimeout(timer);
    if (isOpen()) return;
    note.classList.add("is-anchored");
    note.showPopover();
    place();
  };

  const closeSoon = () => {
    clearTimeout(timer);
    if (pinned) return;
    timer = setTimeout(() => {
      if (anchored() && isOpen()) note.hidePopover();
    }, 250);
  };

  const mouse = (handler) => (event) => {
    if (event.pointerType === "mouse") handler();
  };

  button.addEventListener("pointerenter", mouse(open));
  button.addEventListener("pointerleave", mouse(closeSoon));
  note.addEventListener("pointerenter", mouse(() => clearTimeout(timer)));
  note.addEventListener("pointerleave", mouse(closeSoon));

  // Khung đang mở do rê chuột: bấm vào tên là ghim lại, không đóng
  button.addEventListener("click", (event) => {
    if (!anchored() || !isOpen()) return;
    event.preventDefault();
    clearTimeout(timer);
    pinned = true;
  });

  note.addEventListener("toggle", (event) => {
    if (event.newState !== "closed") return;
    note.classList.remove("is-anchored");
    pinned = false;
  });

  addEventListener("scroll", () => {
    if (anchored() && isOpen()) place();
  }, { passive: true });
})();

// ── 10. Đồng hồ hai thành phố ───────────────────────────────────────────────
// Blog viết từ Osaka, người đọc phần lớn ở Việt Nam: hai nơi cách nhau hai
// tiếng. Giờ tính ngay trên máy người đọc bằng Intl, không gọi ra ngoài, không
// cần biết họ đang ở đâu. Hàng đồng hồ ẩn sẵn trong HTML nên không có JS thì
// không có hàng này, chứ không hiện ra ô trống. Đổi số đúng lúc sang phút mới,
// để hai thành phố nhảy cùng một nhịp.
{
  const row = document.querySelector("[data-clock]");
  const clocks = row ? [...row.querySelectorAll("[data-clock-tz]")] : [];

  if (clocks.length) {
    const lang = document.documentElement.lang || "vi";
    const formats = new Map(
      clocks.map((el) => [
        el,
        new Intl.DateTimeFormat(lang, {
          timeZone: el.dataset.clockTz,
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
      ]),
    );

    const tick = () => {
      const now = new Date();
      for (const [el, format] of formats) {
        // Một số máy trả về "24:05" lúc nửa đêm; đổi lại thành "00:05".
        const time = format.format(now).replace(/^24:/, "00:");
        el.textContent = time;
        el.dateTime = time;
      }
    };

    tick();
    row.hidden = false;
    setTimeout(() => {
      tick();
      setInterval(tick, 60000);
    }, (60 - new Date().getSeconds()) * 1000);
  }
}
