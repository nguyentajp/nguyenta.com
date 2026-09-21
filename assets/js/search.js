// Tìm kiếm bằng Pagefind. Chỉ tải trên trang Tìm kiếm.
// Pagefind tự chọn chỉ mục theo <html lang>, nên trang tiếng Nhật chỉ tìm trong
// bài tiếng Nhật. Kết quả hiện theo đúng kiểu danh sách bài của site.

const root = document.querySelector(".search");
const input = document.querySelector("#q");
const status = document.querySelector(".search-status");
const list = document.querySelector(".search-results");

const lang = document.documentElement.lang;
// Ngày trong chỉ mục là "2026-09-10", JS hiểu là 0 giờ UTC. Định dạng theo UTC
// để người đọc ở múi giờ phía tây (Mỹ…) không thấy lùi mất một ngày.
const dateFormat = new Intl.DateTimeFormat(lang, { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

let pagefind;
// Số thứ tự của lượt tìm mới nhất. Lượt cũ trả kết quả về muộn (kể cả sau khi
// người đọc đã xoá ô) thì bỏ, không vẽ đè lên.
let latest = 0;

async function load() {
  if (pagefind) return pagefind;
  // Đường dẫn tính lúc chạy nên công cụ đóng gói không cố tìm file này khi build.
  const url = new URL("/pagefind/pagefind.js", location.origin).href;
  pagefind = await import(url);
  await pagefind.options({ excerptLength: 24 });
  pagefind.init();
  return pagefind;
}

function render(results) {
  list.replaceChildren(
    ...results.map((result) => {
      const item = document.createElement("li");
      const entry = document.createElement("article");
      entry.className = "entry";

      const time = document.createElement("time");
      time.className = "entry-date";
      if (result.meta.date) {
        time.dateTime = result.meta.date;
        time.textContent = dateFormat.format(new Date(result.meta.date));
      }

      // h2: ngay dưới tiêu đề trang (h1), không có cấp nào xen giữa
      const title = document.createElement("h2");
      title.className = "entry-title";
      const link = document.createElement("a");
      link.href = result.url;
      link.textContent = result.meta.title;
      title.append(link);

      // Pagefind đã escape nội dung đoạn trích, chỉ chèn thêm thẻ <mark>.
      const excerpt = document.createElement("p");
      excerpt.className = "entry-excerpt";
      excerpt.innerHTML = result.excerpt;

      entry.append(time, title, excerpt);
      item.append(entry);
      return item;
    }),
  );
}

async function search(query) {
  const turn = ++latest;
  const trimmed = query.trim();
  // Giữ từ khoá trên URL để chia sẻ được một lượt tìm kiếm
  const url = new URL(location.href);
  if (trimmed) url.searchParams.set("q", trimmed);
  else url.searchParams.delete("q");
  history.replaceState(null, "", url);

  if (!trimmed) {
    status.textContent = "";
    list.replaceChildren();
    return;
  }

  status.textContent = root.dataset.loading;
  let response;
  let results;
  try {
    const engine = await load();
    response = await engine.debouncedSearch(trimmed, {}, 180);
    if (response === null || turn !== latest) return; // đã có lượt gõ mới hơn
    results = await Promise.all(response.results.slice(0, 20).map((r) => r.data()));
  } catch {
    // Không tải được chỉ mục (mạng rớt, hoặc chạy ở máy chưa có Pagefind)
    pagefind = undefined;
    if (turn === latest) status.textContent = root.dataset.error;
    return;
  }
  if (turn !== latest) return;
  status.textContent = results.length
    ? root.dataset.results.replace("__N__", response.results.length)
    : root.dataset.none;
  render(results);
}

input.addEventListener("input", () => search(input.value));
document.querySelector(".search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  search(input.value);
});

// Mở trang với ?q=... thì tìm ngay
const initial = new URLSearchParams(location.search).get("q");
if (initial) {
  input.value = initial;
  search(initial);
}
// Bắt đầu tải chỉ mục khi người đọc chạm vào ô tìm kiếm, để kết quả hiện nhanh
input.addEventListener("focus", load, { once: true });
