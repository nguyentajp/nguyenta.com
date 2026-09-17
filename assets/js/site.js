// Chuyển động duy nhất của cả site: kamon tự vẽ khi vào trang chủ lần đầu
// trong mỗi phiên. Lần thứ hai trở đi, kamon hiện sẵn.
// Người đọc bật prefers-reduced-motion thì CSS tự tắt phần animation.
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
