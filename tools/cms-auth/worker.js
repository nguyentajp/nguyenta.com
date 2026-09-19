// Máy chủ đăng nhập cho Decap CMS ở nguyenta.com/admin.
//
// GitHub Pages chỉ phục vụ file tĩnh, không giữ được "client secret" của
// GitHub OAuth App. Worker này làm đúng một việc: đổi mã đăng nhập GitHub lấy
// token rồi trả token về cho cửa sổ CMS. Không lưu gì, không ghi log token.
//
//   /auth      CMS mở popup tới đây → chuyển sang trang đồng ý của GitHub
//   /callback  GitHub quay về đây → đổi code lấy token → gửi token cho CMS
//
// Biến môi trường (xem wrangler.toml):
//   GITHUB_CLIENT_ID      Client ID của OAuth App, không bí mật
//   GITHUB_CLIENT_SECRET  đặt bằng `npx wrangler secret put GITHUB_CLIENT_SECRET`
//   ALLOWED_ORIGINS       các trang được nhận token, cách nhau bằng dấu phẩy

const SCOPES = new Set(["public_repo", "repo"]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/auth") return auth(url, env);
    if (url.pathname === "/callback") return callback(request, url, env);
    return new Response("Not found", { status: 404 });
  },
};

function auth(url, env) {
  const scope = SCOPES.has(url.searchParams.get("scope")) ? url.searchParams.get("scope") : "public_repo";
  // state chống giả mạo: giá trị ngẫu nhiên vừa nằm trong cookie vừa đi qua
  // GitHub; lúc quay về hai giá trị phải khớp nhau.
  const state = crypto.randomUUID();
  const github = new URL("https://github.com/login/oauth/authorize");
  github.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  github.searchParams.set("redirect_uri", `${url.origin}/callback`);
  github.searchParams.set("scope", scope);
  github.searchParams.set("state", state);
  return new Response(null, {
    status: 302,
    headers: {
      Location: github.toString(),
      "Set-Cookie": `cms_state=${state}; Path=/callback; Max-Age=600; HttpOnly; Secure; SameSite=Lax`,
    },
  });
}

async function callback(request, url, env) {
  const cookie = request.headers.get("Cookie") || "";
  const saved = cookie.match(/(?:^|;\s*)cms_state=([^;]+)/)?.[1];
  const state = url.searchParams.get("state");
  const code = url.searchParams.get("code");
  if (!saved || saved !== state || !code) {
    return reply(env, "error", { message: "Phiên đăng nhập không hợp lệ. Hãy thử lại." });
  }

  const res = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "nguyenta-cms-auth" },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: `${url.origin}/callback`,
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!data.access_token) {
    return reply(env, "error", { message: data.error_description || "GitHub không trả về token." });
  }
  return reply(env, "success", { token: data.access_token, provider: "github" });
}

// Giao thức popup của Decap: popup báo "authorizing:github", CMS trả lời, rồi
// popup gửi kết quả về đúng origin vừa trả lời. Origin không nằm trong
// ALLOWED_ORIGINS thì không bao giờ nhận được token.
function reply(env, status, content) {
  const allowed = JSON.stringify((env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean));
  const message = JSON.stringify(`authorization:github:${status}:${JSON.stringify(content)}`);
  const html = `<!doctype html><meta charset="utf-8"><title>Đăng nhập</title>
<p>Đang hoàn tất đăng nhập…</p>
<script>
  const allowed = ${allowed};
  window.addEventListener("message", (event) => {
    if (!allowed.includes(event.origin)) return;
    window.opener.postMessage(${message}, event.origin);
  }, { once: false });
  if (window.opener) window.opener.postMessage("authorizing:github", "*");
</script>`;
  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Set-Cookie": "cms_state=; Path=/callback; Max-Age=0; HttpOnly; Secure; SameSite=Lax",
    },
  });
}
