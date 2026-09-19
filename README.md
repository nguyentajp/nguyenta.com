# nguyenta.com

Blog song ngữ Việt/Nhật của Gen (Trần Anh Nguyên, 英元), viết từ Osaka.

Site dựng bằng [Hugo](https://gohugo.io/), không dùng theme có sẵn. Bài viết
soạn qua [Decap CMS](https://decapcms.org/) tại `/admin`, GitHub Actions tự
build và đưa lên GitHub Pages.

---

## Mục lục

1. [Site hoạt động thế nào](#1-site-hoạt-động-thế-nào)
2. [Viết bài](#2-viết-bài)
3. [Ảnh và video](#3-ảnh-và-video)
4. [Dịch sang tiếng Nhật](#4-dịch-sang-tiếng-nhật)
5. [Sửa những thứ hay đổi](#5-sửa-những-thứ-hay-đổi)
6. [Chạy site ở máy](#6-chạy-site-ở-máy)
7. [Build và deploy](#7-build-và-deploy)
8. [Xử lý lỗi thường gặp](#8-xử-lý-lỗi-thường-gặp)
9. [Cấu trúc thư mục](#9-cấu-trúc-thư-mục)
10. [Nâng cấp phiên bản](#10-nâng-cấp-phiên-bản)
11. [Kiến trúc kỹ thuật](#11-kiến-trúc-kỹ-thuật): GitHub, Cloudflare, Worker là gì và vì sao dùng

---

## 1. Site hoạt động thế nào

Khác WordPress ở chỗ: **không có database, không có PHP**. Mỗi bài là một file
văn bản (Markdown) nằm trong repo. Hugo đọc các file đó và sinh ra toàn bộ site
thành HTML tĩnh.

```
Viết bài ở /admin ──┐
                    ├──► commit lên GitHub ──► GitHub Actions build ──► nguyenta.com
Sửa file ở máy ─────┘        (repo)              (khoảng 2 phút)        (GitHub Pages)
```

- Viết trên `nguyenta.com/admin`: CMS tự commit, bạn không cần làm gì thêm.
- Viết ở máy: sửa file rồi tự `git push` (xem [mục 2.2](#22-viết-ở-máy-không-cần-mạng)).
- Mỗi lần có commit mới trên nhánh `main`, site tự build lại. Ngoài ra site còn
  tự build mỗi ngày lúc **0:05 giờ Nhật**, để bài hẹn giờ tự hiện.

Từng mảnh trong sơ đồ trên là gì và vì sao cần, xem [mục 11](#11-kiến-trúc-kỹ-thuật).

---

## 2. Viết bài

### 2.1 Viết trên nguyenta.com/admin

1. Mở <https://nguyenta.com/admin/>, bấm **Đăng nhập bằng GitHub**.
2. Chọn **Bài viết · Tiếng Việt** ở cột trái, bấm **＋ bài viết tiếng Việt**.
3. Điền form:

   | Ô | Ý nghĩa |
   |---|---|
   | Tiêu đề | Tên bài. Tên thư mục và URL của bài tự tạo từ tiêu đề, bỏ dấu: "Đường về nhà" → `nguyenta.com/bai-viet/duong-ve-nha/` |
   | Ngày đăng | Để giờ tương lai là **hẹn giờ đăng** (xem [2.4](#24-hẹn-giờ-đăng)) |
   | Bản nháp | **Bật**: bài chưa hiện trên site. **Tắt**: bài được đăng |
   | Mô tả ngắn | Một hai câu, hiện trong danh sách bài, khi chia sẻ link và trong kết quả tìm kiếm |
   | Danh mục | Chọn đúng một: Học tập, Đời sống, Du lịch, Suy nghĩ, Nhật ký |
   | Thẻ | Viết tự nhiên, có dấu, cách nhau bằng dấu phẩy: `osaka, mùa thu` |
   | Ảnh bìa | Không bắt buộc. Để trống thì lấy ảnh đầu tiên trong bài |
   | Nội dung | Thân bài. Nút **＋** để chèn Ảnh, Bộ ảnh, Video YouTube |

4. Bấm **Công bố** → **Công bố ngay**.

> ⚠️ **Nút "Công bố" chỉ có nghĩa là lưu.** Chữ "Đã công bố" ở góc trên chỉ
> cho biết bài đã được lưu vào repo. Bài có hiện trên site hay không là do ô
> **Bản nháp** quyết định. Muốn đăng bài: tắt Bản nháp rồi bấm Công bố. Khoảng
> hai phút sau bài lên site.

Lọc bài theo trạng thái bằng nút **Lọc theo → Bản nháp / Đã đăng** phía trên
danh sách.

### 2.2 Viết ở máy (không cần mạng)

Dùng chính giao diện CMS, nhưng ghi thẳng vào file trên máy. Mở **hai tab
terminal** (⌘T) trong thư mục repo:

Tab 1, chạy site:

```bash
hugo server -D
```

Tab 2, chạy cầu nối để CMS ghi được file:

```bash
npx decap-server
```

Rồi mở <http://localhost:1313/admin/> và bấm **Đăng nhập**. Nếu quên chạy
`decap-server`, trang sẽ hiện một dòng nhắc ở trên cùng.

Viết xong thì tắt cả hai bằng **Ctrl + C** (phím Control, không phải ⌘) trong
từng tab.

Viết ở máy thì CMS chỉ ghi file, **không** commit. Đưa bài lên site bằng:

```bash
git pull --rebase
```

```bash
git add content/
```

```bash
git commit -m "Viết bài: đường về nhà"
```

```bash
git push
```

`git pull --rebase` ở đầu là để lấy về những bài bạn đã viết trên
nguyenta.com/admin, tránh bị GitHub từ chối lúc push (xem [mục 8](#8-xử-lý-lỗi-thường-gặp)).

### 2.3 Viết bằng tay trong editor

Tạo bài mới từ mẫu có sẵn (tên thư mục viết không dấu, nối bằng gạch ngang):

```bash
hugo new content content/vi/posts/duong-ve-nha/index.md
```

Mở file vừa tạo, sửa phần front matter (giữa hai dòng `---`). Mỗi dòng trong
mẫu đều có ghi chú. Lưu ý:

- `title` được mẫu điền tạm là "duong ve nha". Hãy viết lại cho đúng.
- Tiêu đề có dấu hai chấm `:` thì **phải** đặt trong dấu nháy kép:
  `title: "Osaka: mùa thu"`.
- `draft: true` là bản nháp. Đổi thành `false` để đăng.

Xem thử ở máy bằng `hugo server -D` (cờ `-D` để hiện cả bài nháp) rồi mở
<http://localhost:1313/>.

### 2.4 Hẹn giờ đăng

Đặt **Ngày đăng** trong tương lai và **tắt Bản nháp**. Hugo bỏ qua bài có ngày
trong tương lai, nên bài sẽ hiện ở lần build đầu tiên sau giờ đó. Site tự build mỗi ngày
lúc 0:05 giờ Nhật, nên bài hẹn lúc 9 giờ sáng thứ Hai sẽ hiện lúc 0:05 đêm thứ
Hai rạng sáng thứ Ba, hoặc sớm hơn nếu trong khoảng đó có commit nào khác.

Muốn bài hiện đúng giờ thì vào tab **Actions** trên GitHub, chọn **Deploy** →
**Run workflow** sau giờ đó.

---

## 3. Ảnh và video

Mỗi bài là một thư mục. Ảnh của bài nằm **cùng thư mục** với `index.md`:

```
content/vi/posts/duong-ve-nha/
├── index.md
├── bo-song.jpg
└── cau-yodo.jpg
```

Upload ảnh trong CMS thì ảnh tự vào đúng chỗ này.

### Hugo tự làm gì với ảnh

- Sinh nhiều cỡ WebP (420 → 1800px). Trình duyệt tự chọn cỡ vừa màn hình.
- **Không bao giờ gửi ảnh gốc** tới người đọc, nên thông tin EXIF (máy ảnh,
  toạ độ GPS) trong ảnh gốc không lộ ra ngoài.
- Bấm vào ảnh là mở bản lớn (lightbox). Phím ← → để chuyển ảnh, Esc để đóng.
- Trang **Ảnh** tự gom ảnh của mọi bài đã đăng.

### Nên chuẩn bị ảnh thế nào

- JPEG, cạnh dài khoảng **2000–2400px**. Site không dùng ảnh lớn hơn 1800px.
  Ảnh điện thoại (4000px, 3–5 MB) nên thu nhỏ trước khi upload, vì mọi ảnh đã
  commit sẽ nằm mãi trong lịch sử repo.
- Tên file không dấu, nối bằng gạch ngang: `cau-yodo.jpg`.
- Luôn điền **Mô tả ảnh** (alt): tả ngắn ảnh có gì, cho người dùng trình đọc
  màn hình.

### Chèn ảnh

Trong CMS: nút **＋ → Ảnh**, chọn ảnh, điền mô tả, chú thích, và **cỡ ảnh**:

| Cỡ | Hiển thị |
|---|---|
| Rộng bằng cột chữ | Mặc định |
| Rộng | Lấn sang khoảng trống bên phải |
| Tràn hết khung | Rộng hết chiều ngang khung trang |

Trên điện thoại, ảnh nào cũng tràn sát hai mép màn hình.

Viết bằng tay thì dùng cú pháp Markdown. Chú thích đặt trong dấu nháy kép, cỡ
ảnh đặt ở **dòng ngay bên dưới**:

```markdown
![Cầu Yodo lúc hoàng hôn](cau-yodo.jpg "Cầu Yodo, cuối tháng Chín")
{class="wide"}
```

### Bộ ảnh (gallery)

Trong CMS: nút **＋ → Bộ ảnh**, chọn 2 hoặc 3 cột rồi thêm từng ảnh.

Viết bằng tay: mỗi dòng một file, chú thích sau dấu gạch đứng `|`:

```markdown
{{< gallery cols="3" >}}
minoo-1.jpg | Thác Minoo đầu tháng Mười
minoo-2.jpg
minoo-3.jpg
{{< /gallery >}}
```

Hoặc lấy mọi ảnh khớp một mẫu tên. Viết một dòng thì **phải** kết thúc bằng `/>`:

```markdown
{{< gallery cols="2" match="minoo-*.jpg" />}}
```

### Video YouTube

Trong CMS: nút **＋ → Video YouTube**, dán nguyên link YouTube vào.

Viết bằng tay:

```markdown
{{< youtube id="dQw4w9WgXcQ" title="Chú thích dưới video" >}}
```

Thêm `start="90"` để video bắt đầu từ giây thứ 90. Trước khi người đọc bấm phát,
trang chỉ hiện ảnh thumbnail (do chính nguyenta.com phục vụ), nên không có gì
gửi tới Google. Khi bấm phát, video dùng youtube-nocookie.com.

---

## 4. Dịch sang tiếng Nhật

Dịch bằng Claude Code, mở trong thư mục repo:

```
/dich content/vi/posts/duong-ve-nha/index.md
```

Lệnh này:

1. Đọc [STYLE.md](STYLE.md) (văn phong です/ます) và [GLOSSARY.md](GLOSSARY.md)
   (bảng thuật ngữ).
2. Tạo `content/ja/posts/<slug-romaji>/index.md`, copy ngày đăng, ảnh bìa, đổi
   danh mục sang tiếng Nhật (`du-lich` → `tabi`), đặt `draft: true`.
3. Ghi `translationKey` vào **cả hai bản** để nút chuyển ngôn ngữ nối đúng bài.
4. Viết bản dịch.

Đọc lại bản dịch trong CMS ở mục **Bài viết · Tiếng Nhật**, rồi tắt Bản nháp và
bấm Công bố.

Ảnh dùng chung: bản tiếng Nhật không cần upload lại ảnh, cứ ghi đúng tên file
như bản tiếng Việt.

---

## 5. Sửa những thứ hay đổi

| Muốn sửa | Ở đâu |
|---|---|
| Trang Giới thiệu | CMS → **Trang**, hoặc `content/vi/about.md`, `content/ja/about.md` |
| Ảnh chân dung ở sidebar | Thay file `assets/brand/avatar.jpg` (ảnh gì cũng được, site tự cắt vuông) |
| Lời giới thiệu ở sidebar | `hugo.toml` → `[languages.vi.params]` → `bio` (bản tiếng Nhật: `[languages.ja.params]`) |
| Dòng nhỏ dưới tên blog | `hugo.toml` → `tagline` (hai ngôn ngữ) |
| Email, mạng xã hội ở trang Liên hệ | `hugo.toml` → `[params]` → `email`, `[params.socials]` |
| Số bài ở trang chủ | `hugo.toml` → `homeRecentCount` |
| Chữ trên giao diện (nút, nhãn) | `i18n/vi.toml`, `i18n/ja.toml` |
| Màu, cỡ chữ, khoảng cách | `assets/css/main.css`, phần **1. Token** ở đầu file |

---

## 6. Chạy site ở máy

### Cài lần đầu

```bash
brew install hugo
```

```bash
python3 -m venv .venv
```

```bash
./.venv/bin/pip install -r tools/fonts/requirements.txt
```

```bash
python3 tools/fonts/get-sources.py
```

Lệnh cuối tải font gốc (khoảng 25 MB) về `tools/fonts/src/` và kiểm tra mã
SHA256. Font gốc không nằm trong repo vì quá nặng.

### Hằng ngày

```bash
tools/dev.sh
```

Lệnh này subset font theo nội dung hiện có, dựng chỉ mục tìm kiếm, rồi mở
`hugo server` kèm bài nháp tại <http://localhost:1313/>. Sửa file nào, trình
duyệt tự tải lại.

`hugo server -D` cũng chạy được, nhưng ô tìm kiếm sẽ không có kết quả mới, và
chữ mới (ví dụ một chữ Hán chưa từng dùng) có thể hiện bằng font hệ thống. Chạy
lại `tools/dev.sh` là đủ.

---

## 7. Build và deploy

### Tự động

Không cần làm gì. Mỗi commit lên `main` (kể cả từ CMS) đều chạy workflow
[.github/workflows/deploy.yml](.github/workflows/deploy.yml):

```
tải font gốc → subset font toàn site → hugo --minify → subset font từng trang → Pagefind → GitHub Pages
```

Xem tiến trình ở tab **Actions** trên GitHub: dấu ✓ xanh là đã lên site, dấu ✗
đỏ là lỗi (xem [mục 8](#8-xử-lý-lỗi-thường-gặp)).

Build tay: tab **Actions** → **Deploy** → **Run workflow**.

### Chế độ bảo trì

Khi `maintenance = true` trong mục `[params]` của [hugo.toml](hugo.toml),
nguyenta.com chỉ hiện vòng ensō của trang 静 với dòng "Nơi này đang được
dựng", có link sang bản tiếng Nhật. Workflow chỉ đưa lên trang đó, file CSS,
font và `/admin`, nên bài viết, ảnh, RSS, sitemap và chỉ mục tìm kiếm không
có trên mạng, đoán URL cũng không mở được. Máy tìm kiếm được báo là không
ghi nhận trang.

- **Mở blog:** đổi thành `maintenance = false`, commit. Vài phút sau site hiện đầy đủ.
- **Viết bài trong lúc bảo trì:** CMS ở `/admin` vẫn dùng được. Bài được lưu
  vào repo nhưng chưa ai đọc được, cho tới khi mở blog.
- Trang [nguyenta.com/concept/](https://nguyenta.com/concept/) (bản mẫu thiết
  kế, `layouts/concept.html`) vẫn mở cho mọi người, nhờ dòng
  `maintenance_exempt: true` trong `content/vi/concept.md`.
- `hugo server` ở máy luôn hiện site đầy đủ. Lời nhắn nằm ở `maint_line`
  trong `i18n/vi.toml` và `i18n/ja.toml`.

### Build production ở máy

Để xem site giống hệt bản trên mạng, hoặc đo Lighthouse. Đo trên `hugo server`
không chính xác. Đang bật chế độ bảo trì thì bản build này cũng chỉ ra trang
bảo trì; muốn xem cả site thì build bằng `hugo --minify -e development`.

```bash
hugo --minify
```

```bash
./.venv/bin/python tools/fonts/build.py --pages public
```

```bash
npx --yes pagefind@1.5.2 --site public
```

Rồi phục vụ thư mục `public/`:

```bash
npx --yes serve@14 public -l 4173
```

và mở <http://localhost:4173/>.

---

## 8. Xử lý lỗi thường gặp

### CMS

**Ở máy, CMS báo `Repo "nguyentajp/nguyenta.com" not found`.**
Chưa chạy `decap-server`, nên CMS chuyển sang đăng nhập GitHub thật. Mở thêm
một tab terminal, chạy `npx decap-server`, tải lại trang.

**Form đang hiện nội dung của bài khác.**
Hiếm gặp, xảy ra khi chuyển thẳng từ bài này sang bài kia. Đừng bấm Công bố.
Quay về danh sách bằng mũi tên ← rồi tải lại trang (⌘R).

**Danh sách bài thiếu bài vừa viết, hoặc còn bài đã xoá.**
CMS nhớ tạm danh sách trong trình duyệt. Tải lại trang (⌘R).

### Bài không hiện trên site

Kiểm tra theo thứ tự:

1. **Bản nháp** còn bật? (`draft: true`)
2. **Ngày đăng** ở tương lai? Bài sẽ hiện ở lần build sau giờ đó, xem [2.4](#24-hẹn-giờ-đăng).
3. Tab **Actions** trên GitHub có dấu ✗ đỏ? Bấm vào để xem lỗi, xem mục dưới.
4. Trình duyệt đang giữ trang cũ? Tải lại bằng ⌘⇧R.

### Build lỗi (dấu ✗ đỏ trong Actions, hoặc lỗi khi chạy hugo ở máy)

Tìm dòng bắt đầu bằng `ERROR`. Hugo thường ghi kèm tên file và số dòng bị lỗi.

**`mapping value is not allowed in this context`**
Front matter có dấu hai chấm chưa đặt trong nháy, thường ở tiêu đề:

```yaml
title: Đường về: một buổi chiều      # ❌
title: "Đường về: một buổi chiều"    # ✅
```

**`shortcode "gallery" must be closed or self-closed`**
Gallery viết một dòng thì phải kết thúc bằng `/>`:

```markdown
{{< gallery cols="2" match="minoo-*.jpg" />}}
```

**`WARN Không tìm thấy ảnh "..." trong bài "..."`**
Đây là cảnh báo, không làm build dừng, nhưng ảnh sẽ không hiện. Tên file trong
bài không khớp file nào trong thư mục bài. Kiểm tra chính tả và đuôi file:
`.jpg` khác `.jpeg` (chữ hoa hay thường thì không sao).

### Git

**`git push` bị từ chối: `! [rejected] main -> main (fetch first)`**
Trên GitHub có commit mà máy chưa có, thường là bài viết từ nguyenta.com/admin.
Lấy về trước rồi push lại:

```bash
git pull --rebase
```

```bash
git push
```

### Chạy ở máy

**`port 1313 already in use`**
Đang có một `hugo server` khác chạy. Hugo tự chọn cổng khác và in ra dòng
`Web Server is available at http://localhost:xxxxx/`. Dùng đúng địa chỉ đó,
hoặc tắt server cũ bằng Ctrl + C trong tab của nó.

**Chữ trên trang hiện bằng font khác, hoặc tìm kiếm không có bài mới.**
Chạy lại `tools/dev.sh`.

**URL của bài có dấu tiếng Việt, hoặc không như ý.**
URL lấy từ ô `slug` trong front matter; không có `slug` thì lấy tên thư mục của
bài. Sửa `slug` (không dấu, nối bằng gạch ngang).

**Nút chuyển ngôn ngữ không trỏ tới bản dịch.**
Hai bản phải có cùng `translationKey`. Mở hai file, so dòng `translationKey`.

---

## 9. Cấu trúc thư mục

```
content/vi/, content/ja/   Nội dung hai ngôn ngữ: bài viết (posts/), danh mục, các trang
layouts/                   Template HTML của Hugo
assets/css/main.css        Toàn bộ CSS, một file duy nhất
assets/js/                 JavaScript: lightbox, video, tìm kiếm, kamon
assets/brand/              Kamon, con dấu 元, ảnh chân dung, ảnh chia sẻ
static/admin/              Decap CMS: config.yml (form), cms.js (nút chèn ảnh/video)
i18n/                      Chữ trên giao diện, theo ngôn ngữ
data/sekki.toml            24 tiết khí, hiện trong dòng thông tin của bài
archetypes/posts.md        Mẫu cho bài mới tạo bằng hugo new
tools/fonts/               Tải và subset font (Literata, Shippori Mincho)
tools/brand/               Script vẽ kamon, favicon, con dấu, vòng ensō
tools/new-ja-draft.py      Tạo khung bản dịch tiếng Nhật (lệnh /dich gọi script này)
tools/cms-auth/            Worker Cloudflare cho đăng nhập CMS (xem mục 11.3)
tools/preview/             Cấu hình Worker bản xem trước riêng (xem mục 11.4)
.github/workflows/         Build và deploy tự động
hugo.toml                  Cấu hình site, có ghi chú từng mục
STYLE.md, GLOSSARY.md      Văn phong và thuật ngữ khi dịch
```

Thư mục `public/`, `preview-public/` và `resources/` do Hugo sinh ra, không commit.

---

## 10. Nâng cấp phiên bản

Mọi công cụ đều ghim đúng phiên bản, để build hôm nay và build năm sau ra cùng
một kết quả. Muốn nâng cấp thì sửa ở những chỗ sau, rồi chạy thử ở máy trước
khi push.

| Công cụ | Sửa ở đâu |
|---|---|
| Hugo | `HUGO_VERSION` trong `.github/workflows/deploy.yml`; ở máy chạy `brew upgrade hugo` cho khớp |
| Pagefind | `PAGEFIND_VERSION` trong workflow, và số phiên bản trong `tools/dev.sh` |
| Decap CMS | Số phiên bản **và** mã `integrity` trong `static/admin/index.html` (có lệnh tính mã ghi ngay trong file) |
| Font | `tools/fonts/fonts.lock.json` (commit của repo google/fonts và SHA256 từng file) |
| Thư viện Python | `tools/fonts/requirements.txt` |

---

## 11. Kiến trúc kỹ thuật

Mục này ghi lại site được ghép từ những mảnh nào, mỗi mảnh là gì, vì sao cần
nó, và vì sao chọn cách này chứ không phải cách khác. Đọc lại khi quên, hoặc
trước khi định thay đổi một mảnh nào đó.

### 11.1 Toàn cảnh

```
                          ┌──────────────── GitHub ────────────────┐
 Viết ở /admin ──────────►│ repo nguyentajp/nguyenta.com (mã nguồn) │
   (Decap CMS)            │        │ mỗi commit lên main           │
       ▲                  │        ▼                               │
       │ đăng nhập        │ GitHub Actions: build bằng Hugo        │
       │                  │        │                               │
       │                  │        ▼                               │
       │                  │ GitHub Pages: phục vụ file tĩnh ───────┼──► https://nguyenta.com
       │                  └────────────────────────────────────────┘       ▲
       │                                                                   │ DNS (Hostinger):
       │                  ┌────────────── Cloudflare ──────────────┐       │ tên miền trỏ về GitHub
       └──────────────────┤ Worker nguyenta-cms-auth (công khai)   │
                          │   đổi mã GitHub lấy token cho CMS      │
                          │                                        │
                          │ Worker nguyenta-preview                │
                          │   site đầy đủ, có Cloudflare Access ───┼──► chỉ Gen xem được
                          └────────────────────────────────────────┘
```

Hai nửa độc lập với nhau: **GitHub** giữ mã nguồn và phục vụ site công khai;
**Cloudflare** chỉ làm hai việc phụ mà GitHub Pages không làm được (đăng nhập
CMS và bản xem trước có khoá). Cloudflare hỏng thì nguyenta.com vẫn chạy, chỉ
không đăng nhập CMS được.

### 11.2 Từng mảnh là gì, vì sao cần

**Git và GitHub (repo).** Git lưu mọi phiên bản của mọi file; GitHub là nơi
cất repo trên mạng. Mỗi bài viết là một file, nên lịch sử bài viết chính là
lịch sử Git: sửa nhầm thì quay lại được, không cần sao lưu database như
WordPress. Repo để **public** vì GitHub Pages miễn phí chỉ chạy với repo public.
Hệ quả: ai cũng đọc được mã nguồn và cả bài nháp đã commit. File cá nhân
(`Yêu cầu.md`) nằm trong `.gitignore` nên không bị đẩy lên.

**Hugo.** Chương trình biến thư mục `content/` (Markdown) thành site HTML tĩnh.
Site tĩnh không có PHP, không có database, nên không có gì để hack hay để cập
nhật bảo mật, tải rất nhanh và lưu trữ miễn phí.

**GitHub Actions.** Máy ảo miễn phí của GitHub, tự chạy mỗi khi có commit lên
`main` và mỗi ngày lúc 0:05 giờ Nhật. Nó làm đúng các bước như ở máy: tải
font, chạy Hugo, cắt font theo từng trang, lập chỉ mục tìm kiếm, rồi giao kết
quả cho GitHub Pages. Nhờ vậy viết trên điện thoại qua `/admin` là đủ, không
cần mở máy tính. Cấu hình: [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

**GitHub Pages.** Dịch vụ phục vụ file tĩnh miễn phí của GitHub, đặt ở nhiều
máy chủ khắp thế giới. Nguồn build đặt là **GitHub Actions** (Settings › Pages),
tên miền riêng là `nguyenta.com`, bật **Enforce HTTPS**.

**Tên miền và DNS (Hostinger).** Tên miền `nguyenta.com` mua ở Hostinger và
DNS vẫn quản lý ở đó. DNS là "danh bạ" đổi tên miền thành địa chỉ IP:

| Bản ghi | Tên | Giá trị | Ý nghĩa |
|---|---|---|---|
| A ×4 | `@` | `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` | `nguyenta.com` trỏ về máy chủ GitHub Pages |
| CNAME | `www` | `nguyentajp.github.io` | `www.nguyenta.com` đi theo GitHub, GitHub tự chuyển về `nguyenta.com` |

Có 4 bản ghi A vì GitHub Pages chạy trên 4 cụm máy chủ. Trình duyệt nhận cả 4,
cụm nào trục trặc thì tự thử cụm khác, nên site không sập theo một máy.
**Không** chuyển DNS sang Cloudflare: không cần, và chuyển thì phải làm lại
toàn bộ phần này.

**HTTPS.** Chứng chỉ do Let's Encrypt cấp, GitHub tự xin và tự gia hạn. Không
phải làm gì.

**Pagefind.** Công cụ tìm kiếm chạy hoàn toàn trong trình duyệt: lúc build nó
lập chỉ mục mọi bài, người đọc gõ tìm thì trình duyệt tải từng mảnh chỉ mục
nhỏ. Không cần máy chủ tìm kiếm, không gửi từ khoá của người đọc đi đâu.

**Font tự host** (`tools/fonts/`). Font nằm ngay trên nguyenta.com, không gọi
Google Fonts, nên trình duyệt người đọc không phải kết nối tới Google. Mỗi
trang chỉ chứa đúng những chữ nó dùng (khoảng 35 KB tiếng Việt, 66 KB tiếng
Nhật) thay vì cả bộ font vài MB.

**Decap CMS** (`static/admin/`). Giao diện viết bài ở `/admin`. Nó không có
máy chủ riêng: chạy trong trình duyệt, đọc và ghi file thẳng vào repo qua
GitHub API bằng tài khoản GitHub của anh. "Công bố" trong CMS thực chất là
một commit.

**GitHub OAuth App** (`nguyenta.com CMS`, trong GitHub › Settings › Developer
settings › OAuth Apps). Là "giấy phép" để Decap xin GitHub cho phép ghi vào
repo thay anh. App có hai giá trị: **Client ID** (công khai) và **Client
secret** (bí mật tuyệt đối, ai có nó có thể giả làm app này).

**Cloudflare.** Công ty vận hành mạng máy chủ khắp thế giới. Ở đây chỉ dùng
hai dịch vụ miễn phí: **Workers** và **Access**. Tài khoản đăng ký bằng
`nguyentajp1403@gmail.com`.

**Cloudflare Workers.** Đoạn code nhỏ chạy trên máy chủ Cloudflare, gọi tới là
chạy, không phải thuê hay bảo trì máy chủ. Gói miễn phí cho 100.000 lượt gọi
mỗi ngày, blog cá nhân dùng không hết. Mỗi Worker có địa chỉ dạng
`<tên-worker>.genblog.workers.dev` (`genblog` là subdomain của tài khoản, đặt
một lần, đổi thì mọi địa chỉ Worker đổi theo).

**Cloudflare Access.** Lớp khoá đặt trước một Worker: ai vào cũng phải đăng
nhập trước, chỉ người được cho phép mới qua. Đang dùng policy **Cloudflare
account members**: chỉ người đăng nhập được tài khoản Cloudflare này, tức là
anh.

**wrangler.** Công cụ dòng lệnh của Cloudflare để deploy Worker từ máy. Luôn
gọi bằng `npx wrangler@4` (ghim bản 4). Đăng nhập một lần bằng
`npx wrangler login`; quyền được lưu trong máy ở
`~/Library/Preferences/.wrangler/`.

### 11.3 Vì sao CMS cần một Worker để đăng nhập

GitHub chỉ đưa quyền ghi repo (token) cho ai chứng minh được mình là app hợp
lệ, bằng cách gửi kèm **Client secret**. Secret không được nằm trong trình
duyệt hay trong repo public, vì ai xem mã nguồn trang cũng thấy. GitHub Pages
chỉ phục vụ file tĩnh, không có chỗ nào chạy code phía máy chủ để giữ secret.
Worker `nguyenta-cms-auth` chính là chỗ đó: nó giữ secret, và chỉ làm đúng
một việc là đổi mã đăng nhập lấy token.

Một lần đăng nhập diễn ra như sau:

1. Anh bấm **Đăng nhập bằng GitHub** ở `nguyenta.com/admin`. CMS mở một cửa sổ
   nhỏ tới `nguyenta-cms-auth.genblog.workers.dev/auth`.
2. Worker tạo một chuỗi ngẫu nhiên (`state`), cất vào cookie, rồi chuyển cửa sổ
   sang trang "Authorize" của GitHub.
3. Anh đồng ý. GitHub quay lại `/callback` của Worker, kèm một mã dùng một lần
   (`code`) và chuỗi `state`.
4. Worker so `state` với cookie (chống trang lạ giả mạo lượt đăng nhập), rồi
   gửi `code` + Client ID + Client secret cho GitHub, nhận về token.
5. Worker trao token cho cửa sổ `/admin`, và chỉ trao cho đúng
   `https://nguyenta.com` (biến `ALLOWED_ORIGINS`). Cửa sổ nhỏ đóng lại.
6. Từ đó CMS dùng token gọi GitHub API để đọc và commit bài.

Worker không lưu token, không ghi log. Token nằm trong trình duyệt của anh.
Quyền xin là `public_repo`: chỉ ghi được repo public, không đụng tới repo
private nào của anh. Mã nguồn: [tools/cms-auth/worker.js](tools/cms-auth/worker.js),
khoảng 60 dòng, tự viết để đọc hiểu được hết thay vì dùng code của người khác.

Deploy lại sau khi sửa: `npx wrangler@4 deploy --config tools/cms-auth/wrangler.toml`.

### 11.4 Bảo trì và bản xem trước: ai thấy gì

| Địa chỉ | Ai xem được | Nội dung |
|---|---|---|
| `nguyenta.com` và mọi trang con | Mọi người | Lúc bảo trì: chỉ trang ensō "đang dựng" (xem [mục 7](#7-build-và-deploy)) |
| `nguyenta.com/concept/` | Mọi người | Bản mẫu thiết kế, mở cả khi bảo trì |
| `nguyenta.com/admin/` | Mọi người mở được, chỉ anh đăng nhập được | CMS |
| `nguyenta-preview.genblog.workers.dev` | Chỉ anh (Cloudflare Access) | Site đầy đủ, không bảo trì, không bài nháp |
| `nguyenta-cms-auth.genblog.workers.dev` | Công khai, **không được** bật Access | Máy chủ đăng nhập CMS |

Bản xem trước là Worker `nguyenta-preview` chỉ chứa file tĩnh
([tools/preview/wrangler.toml](tools/preview/wrangler.toml)). Nó được build
riêng với `maintenance = false` và địa chỉ gốc của chính nó, vào thư mục
`preview-public/` (không commit). Hiện đang đẩy tay từ máy:

```bash
HUGO_PARAMS_MAINTENANCE=false HUGO_ENVIRONMENT=production hugo --minify --baseURL https://nguyenta-preview.genblog.workers.dev/ -d preview-public
```

```bash
npx wrangler@4 deploy --config tools/preview/wrangler.toml
```

> ⚠️ Không bao giờ tắt Access của `nguyenta-preview`, và không đẩy bản đầy đủ
> lên Worker nào chưa có Access: nội dung sẽ lộ ra cho bất kỳ ai có địa chỉ.

### 11.5 Các API đang dùng

API là "cửa" để chương trình nói chuyện với một dịch vụ, thay cho việc bấm
chuột trên web.

| API | Ai gọi | Để làm gì |
|---|---|---|
| GitHub REST API (`api.github.com`) | Decap CMS, trong trình duyệt | Đọc danh sách bài, commit bài mới, tải ảnh lên repo |
| GitHub OAuth (`github.com/login/oauth/authorize`, `/access_token`) | Worker `nguyenta-cms-auth` | Xin anh đồng ý, rồi đổi mã một lần lấy token |
| `window.postMessage` | Cửa sổ đăng nhập ↔ trang `/admin` | Trao token giữa hai cửa sổ trình duyệt, chỉ cho origin `nguyenta.com` |
| GitHub Pages API (qua lệnh `gh api`) | Dùng một lần khi dựng | Bật Pages với nguồn Actions, đặt tên miền, bật HTTPS |
| Cloudflare API (qua `wrangler`) | Từ máy anh | Deploy hai Worker, cất Client secret |
| YouTube (`youtube-nocookie.com`) | Trình duyệt người đọc, chỉ khi bấm phát | Phát video nhúng trong bài |

### 11.6 Tài khoản và bí mật nằm ở đâu

| Thứ | Nằm ở | Lộ hoặc mất thì làm gì |
|---|---|---|
| Tài khoản GitHub `nguyentajp` | — | Giữ bật xác thực hai lớp (2FA): tài khoản này ghi được cả site |
| Client secret của OAuth App | Secret của Worker `nguyenta-cms-auth` trên Cloudflare, **không** có trong repo | GitHub › OAuth App › Generate a new client secret, xoá secret cũ, chạy lại `npx wrangler@4 secret put GITHUB_CLIENT_SECRET --config tools/cms-auth/wrangler.toml` |
| Client ID | `tools/cms-auth/wrangler.toml` | Công khai, không sao |
| Tài khoản Cloudflare | Email `nguyentajp1403@gmail.com` | Cũng là chìa khoá của bản xem trước (Access), nên giữ mật khẩu mạnh và 2FA |
| Quyền wrangler trên máy | `~/Library/Preferences/.wrangler/` | Thu hồi: `npx wrangler logout` |
| Tên miền | Hostinger | Nhớ gia hạn hằng năm; hết hạn là site mất |

### 11.7 Những quyết định đã chọn và lý do

- **Cloudflare Worker cho đăng nhập CMS**, không dùng Netlify: Worker miễn
  phí, không bắt chuyển site hay DNS, và code đủ ngắn để tự đọc hiểu.
- **Tự viết Worker** thay vì dùng bản có sẵn trên mạng: không phải tin code
  của người lạ trong khâu cầm token ghi repo.
- **Repo public**: bắt buộc để dùng GitHub Pages miễn phí. Muốn repo private
  thì phải trả GitHub Pro.
- **DNS để ở Hostinger**: Cloudflare chỉ cần cho Worker, không cần giữ tên miền.
- **Bảo trì bằng cách lọc file khi deploy**, không chỉ đổi giao diện: đổi giao
  diện thôi thì đoán đúng URL, RSS hay sitemap vẫn đọc được bài.
- **Bản xem trước có Access** thay cho đường dẫn bí mật: đường dẫn bí mật thì
  ai có link là xem được; Access bắt đăng nhập thật.
- **Access policy "Cloudflare account members"**: không phải khai email riêng,
  và không ai ngoài chủ tài khoản vào được.
- **Worker thay cho Cloudflare Pages**: Cloudflare đã gộp Pages vào Workers;
  wrangler mới tạo project Pages kiểu cũ không được.

### 11.8 Đang làm dở

- [ ] Điền Client ID vào `tools/cms-auth/wrangler.toml`, cất Client secret,
      deploy lại Worker, thử đăng nhập `nguyenta.com/admin`.
- [ ] Cho workflow tự đẩy bản xem trước mỗi lần push: cần một Cloudflare API
      token chỉ có quyền deploy Worker, cất trong GitHub › Settings › Secrets.
- [ ] Xoá bài thử `content/vi/posts/zz-thu-nghiem-anh/` (chỉ có ở máy).
- [ ] Mở blog: `maintenance = false` trong `hugo.toml`.
