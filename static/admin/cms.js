// Các nút chèn trong ô "Nội dung" của Decap CMS: Ảnh, Bộ ảnh, Video YouTube.
//
// Mỗi nút là một form nhỏ. Khi lưu, form được ghi thành đúng cú pháp mà
// template của site đọc được (xem layouts/_markup/render-image.html và
// layouts/_shortcodes/). Khi mở lại bài, pattern đọc ngược cú pháp đó thành
// form, nên người viết không phải nhớ cú pháp nào.

// ── Nhắc chạy decap-server khi viết bài ở máy ─────────────────────────────
// Mở /admin ở localhost mà decap-server chưa chạy thì Decap lặng lẽ chuyển
// sang đăng nhập GitHub thật, rồi báo lỗi "Repo not found" rất khó hiểu. Ở
// đây kiểm tra trước và hiện một dòng nhắc bằng tiếng Việt.
if (["localhost", "127.0.0.1"].includes(location.hostname)) {
  fetch("http://localhost:8081/api/v1", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "info" }),
  }).catch(() => {
    const note = document.createElement("div");
    note.setAttribute("role", "alert");
    note.style.cssText =
      "position:fixed;inset:0 0 auto;z-index:99999;padding:12px 16px;background:#6b4f0d;color:#fff;" +
      "font:15px/1.5 system-ui,sans-serif;text-align:center";
    note.innerHTML =
      "Chưa chạy <b>decap-server</b>, nên CMS sẽ đòi đăng nhập GitHub. " +
      "Mở thêm một terminal, chạy <code style=\"background:#0003;padding:1px 6px;border-radius:4px\">npx decap-server</code> " +
      "rồi tải lại trang này.";
    document.body.append(note);
  });
}

// Chuỗi đặt trong dấu nháy kép của Markdown hoặc shortcode: thoát dấu nháy
const quote = (text) => String(text ?? "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
const unquote = (text) => String(text ?? "").replace(/\\(["\\])/g, "$1");

// Đọc các thuộc tính key="value" trong một shortcode
const readAttrs = (text) => {
  const attrs = {};
  for (const [, key, value] of String(text).matchAll(/(\w+)="((?:[^"\\]|\\.)*)"/g)) {
    attrs[key] = unquote(value);
  }
  return attrs;
};

const SIZES = [
  { label: "Rộng bằng cột chữ", value: "normal" },
  { label: "Rộng: lấn ra hai bên cột chữ", value: "wide" },
  { label: "Tràn hết khung", value: "full" },
];

// Ảnh lẻ có thêm cỡ nhỏ đặt giữa cột, cho mã QR hay hình nhỏ; bộ ảnh thì không
const IMAGE_SIZES = [
  SIZES[0],
  { label: "Nhỏ, ở giữa cột (mã QR, hình nhỏ)", value: "narrow" },
  ...SIZES.slice(1),
];

// ── Ảnh ────────────────────────────────────────────────────────────────────
// Thay nút Ảnh mặc định của Decap (cùng id "image") để có thêm ô chọn cỡ ảnh.
//   ![mô tả](anh.jpg "chú thích")
//   {class="wide"}
CMS.registerEditorComponent({
  id: "image",
  label: "Ảnh",
  fields: [
    { name: "src", label: "Ảnh", widget: "image", choose_url: false },
    {
      name: "alt",
      label: "Mô tả ảnh",
      widget: "string",
      required: false,
      hint: "Tả ngắn ảnh có gì, cho người dùng trình đọc màn hình và khi ảnh không tải được.",
    },
    { name: "caption", label: "Chú thích dưới ảnh", widget: "string", required: false },
    { name: "size", label: "Cỡ ảnh", widget: "select", default: "normal", options: IMAGE_SIZES },
  ],
  pattern: /^!\[([^\]\n]*)\]\(([^\s)]+)(?:\s+"((?:[^"\\\n]|\\.)*)")?\)(?:\n\{class="(narrow|wide|full)"\})?$/,
  fromBlock: (match) => ({
    alt: match[1],
    src: match[2],
    caption: unquote(match[3] || ""),
    size: match[4] || "normal",
  }),
  toBlock: ({ src = "", alt = "", caption = "", size = "normal" }) => {
    const title = caption ? ` "${quote(caption)}"` : "";
    const attr = size && size !== "normal" ? `\n{class="${size}"}` : "";
    return `![${String(alt).replace(/[\[\]\n]/g, "")}](${src}${title})${attr}`;
  },
  toPreview: ({ src = "", alt = "" }) => `<img src="${src}" alt="${quote(alt)}">`,
});

// ── Bộ ảnh ─────────────────────────────────────────────────────────────────
//   {{< gallery cols="3" >}}
//   anh-1.jpg | chú thích
//   anh-2.jpg
//   {{< /gallery >}}
CMS.registerEditorComponent({
  id: "gallery",
  label: "Bộ ảnh",
  fields: [
    {
      name: "cols",
      label: "Số cột",
      widget: "select",
      default: "2",
      options: [
        { label: "2 cột", value: "2" },
        { label: "3 cột", value: "3" },
      ],
      hint: "Trên điện thoại luôn là một cột.",
    },
    { name: "size", label: "Độ rộng", widget: "select", default: "normal", options: SIZES },
    {
      name: "images",
      label: "Các ảnh",
      label_singular: "ảnh",
      widget: "list",
      collapsed: false,
      fields: [
        { name: "src", label: "Ảnh", widget: "image", choose_url: false },
        { name: "caption", label: "Chú thích", widget: "string", required: false },
      ],
    },
  ],
  pattern: /^\{\{<\s*gallery\b([^>]*?)\s*>\}\}\n([\s\S]*?)\n?\{\{<\s*\/gallery\s*>\}\}$/,
  fromBlock: (match) => {
    const attrs = readAttrs(match[1]);
    const images = match[2]
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [src, ...rest] = line.split("|");
        return { src: src.trim(), caption: rest.join("|").trim() };
      });
    return { cols: attrs.cols || "2", size: attrs.class || "normal", images };
  },
  toBlock: ({ cols = "2", size = "normal", images = [] }) => {
    const attrs = [`cols="${cols}"`];
    if (size === "wide" || size === "full") attrs.push(`class="${size}"`);
    const lines = (images || [])
      .filter((item) => item && item.src)
      .map((item) => (item.caption ? `${item.src} | ${String(item.caption).replace(/\n/g, " ")}` : item.src));
    return `{{< gallery ${attrs.join(" ")} >}}\n${lines.join("\n")}\n{{< /gallery >}}`;
  },
  toPreview: ({ images = [] }) => `<p>Bộ ảnh: ${(images || []).length} ảnh</p>`,
});

// ── Video YouTube ──────────────────────────────────────────────────────────
//   {{< youtube id="dQw4w9WgXcQ" title="chú thích" start="90" >}}
// Người viết dán nguyên link YouTube cũng được: mã video được tách ra ở đây.
const youtubeId = (input) => {
  const text = String(input || "").trim();
  const found =
    text.match(/(?:youtube\.com\/(?:watch\?(?:.*&)?v=|shorts\/|embed\/|live\/)|youtu\.be\/)([\w-]{11})/) ||
    text.match(/^([\w-]{11})$/);
  return found ? found[1] : text;
};

CMS.registerEditorComponent({
  id: "youtube",
  label: "Video YouTube",
  fields: [
    {
      name: "id",
      label: "Link hoặc mã video",
      widget: "string",
      hint: "Dán nguyên link, ví dụ https://www.youtube.com/watch?v=dQw4w9WgXcQ hoặc https://youtu.be/dQw4w9WgXcQ",
    },
    { name: "title", label: "Chú thích dưới video", widget: "string", required: false },
    {
      name: "start",
      label: "Bắt đầu từ giây thứ",
      widget: "number",
      value_type: "int",
      min: 0,
      required: false,
    },
  ],
  pattern: /^\{\{<\s*youtube\b([^>]*?)\s*\/?>\}\}$/,
  fromBlock: (match) => {
    const attrs = readAttrs(match[1]);
    // Cách viết gọn {{< youtube dQw4w9WgXcQ >}}: mã video là tham số đầu tiên
    const positional = match[1].trim().match(/^([\w-]{11})\b/);
    return {
      id: attrs.id || (positional ? positional[1] : ""),
      title: attrs.title || "",
      start: attrs.start ? Number(attrs.start) : undefined,
    };
  },
  toBlock: ({ id = "", title = "", start }) => {
    const attrs = [`id="${youtubeId(id)}"`];
    if (title) attrs.push(`title="${quote(title)}"`);
    if (start) attrs.push(`start="${Number(start)}"`);
    return `{{< youtube ${attrs.join(" ")} >}}`;
  },
  toPreview: ({ id = "" }) => `<p>Video YouTube: ${youtubeId(id)}</p>`,
});
