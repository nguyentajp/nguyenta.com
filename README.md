# nguyenta.com

Blog song ngữ Việt/Nhật của Gen (Trần Anh Nguyên, 英元), viết từ Osaka.

Site dựng bằng [Hugo](https://gohugo.io/), không dùng theme có sẵn. Bài viết
soạn ở máy bằng [Decap CMS](https://decapcms.org/) (giao diện `/admin` chạy
cùng `hugo server`), `git push` lên GitHub, GitHub Actions tự build và đưa lên
GitHub Pages.

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
Viết bằng CMS ở máy ──┐
                      ├──► git push lên GitHub ──► GitHub Actions build ──► nguyenta.com
Sửa file bằng editor ─┘        (repo)              (khoảng 2 phút)        (GitHub Pages)
```

- Mọi cách viết đều ghi file vào máy; bài lên site sau khi `git push` (xem [mục 2.2](#22-đưa-bài-lên-site)).
- Mỗi lần có commit mới trên nhánh `main`, site tự build lại. Ngoài ra site còn
  tự build mỗi ngày lúc **0:05 giờ Nhật**, để bài hẹn giờ tự hiện.

Từng mảnh trong sơ đồ trên là gì và vì sao cần, xem [mục 11](#11-kiến-trúc-kỹ-thuật).

---

## 2. Viết bài

### 2.1 Viết bằng CMS (ở máy)

CMS là giao diện có form để viết bài, chạy ngay trên máy, không cần đăng nhập
GitHub và không cần mạng. Mở **hai tab terminal** (⌘T) trong thư mục repo:

Tab 1, chạy site:

```bash
hugo server -D
```

Tab 2, chạy cầu nối để CMS ghi được file:

```bash
npx decap-server
```

1. Mở <http://localhost:1313/admin/> và bấm **Đăng nhập**. Nếu quên chạy
   `decap-server`, trang sẽ hiện một dòng nhắc ở trên cùng.
2. Chọn **Bài viết · Tiếng Việt** ở cột trái, bấm **＋ bài viết tiếng Việt**.
3. Điền form:

   | Ô | Ý nghĩa |
   |---|---|
   | Tiêu đề | Tên bài. Tên thư mục và URL của bài tự tạo từ tiêu đề, bỏ dấu: "Đường về nhà" → `nguyenta.com/bai-viet/duong-ve-nha/` |
   | Ngày đăng | Để giờ tương lai là **hẹn giờ đăng** (xem [2.4](#24-hẹn-giờ-đăng)) |
   | Bản nháp | **Bật**: bài chưa hiện trên site. **Tắt**: bài được đăng |
   | Mô tả ngắn | Một hai câu, hiện trong danh sách bài, khi chia sẻ link và trong kết quả tìm kiếm |
   | Danh mục | Chọn đúng một: Nhật ký, Sở thích, Đời sống, Chuyến đi, Suy nghĩ, Học tập |
   | Đã có bản tiếng Nhật | Để tắt lúc mới viết. Bật tay sau khi đăng xong bản dịch, để lọc ra bài chưa dịch (Lọc theo → Chưa có bản tiếng Nhật) |
   | Thẻ | Viết tự nhiên, có dấu, cách nhau bằng dấu phẩy: `osaka, mùa thu` |
   | Ảnh bìa | Không bắt buộc. Để trống thì lấy ảnh đầu tiên trong bài |
   | Nội dung | Thân bài. Nút **＋** để chèn Ảnh, Bộ ảnh, Video YouTube |

4. Bấm **Công bố** → **Công bố ngay**. Xem thử ngay ở <http://localhost:1313/>.
5. Đưa bài lên site theo [mục 2.2](#22-đưa-bài-lên-site).

> ⚠️ **Nút "Công bố" chỉ có nghĩa là lưu file vào máy.** Bài chưa lên mạng cho
> tới khi `git push`, và chỉ hiện trên site khi ô **Bản nháp** đã tắt.

Lọc bài theo trạng thái bằng nút **Lọc theo → Bản nháp / Đã đăng** phía trên
danh sách. Viết xong thì tắt cả hai tab terminal bằng **Ctrl + C** (phím
Control, không phải ⌘).

`/admin` chỉ có ở máy: bản trên nguyenta.com không có trang này (lý do ở
[mục 11.7](#117-những-quyết-định-đã-chọn-và-lý-do)).

### 2.2 Đưa bài lên site

Dù viết bằng CMS hay bằng editor, bài chỉ nằm trong máy cho tới khi đẩy lên
GitHub:

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

`git pull --rebase` ở đầu là để lấy về những thay đổi đã có trên GitHub (ví
dụ sửa từ máy khác), tránh bị từ chối lúc push (xem [mục 8](#8-xử-lý-lỗi-thường-gặp)).
Khoảng hai phút sau bài lên site.

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
<http://localhost:1313/>. Đưa lên site theo [mục 2.2](#22-đưa-bài-lên-site).

### 2.4 Hẹn giờ đăng

Đặt **Ngày đăng** trong tương lai và **tắt Bản nháp**. Hugo bỏ qua bài có ngày
trong tương lai, nên bài sẽ hiện ở lần build đầu tiên sau giờ đó. Site tự build mỗi ngày
lúc 0:05 giờ Nhật, nên bài hẹn lúc 9 giờ sáng thứ Hai sẽ hiện lúc 0:05 đêm thứ
Hai rạng sáng thứ Ba, hoặc sớm hơn nếu trong khoảng đó có commit nào khác.

Muốn bài hiện đúng giờ thì vào tab **Actions** trên GitHub, chọn **Deploy** →
**Run workflow** sau giờ đó.

**Ngày cập nhật.** Sửa nội dung đáng kể (thêm đoạn, sửa thông tin sai) thì
điền ô **Ngày cập nhật** trong CMS (trường `updated`), dưới tiêu đề bài sẽ hiện
"Cập nhật 21 tháng 9, 2026". Sửa lỗi chính tả thì để trống. Không điền gì thì
Google và sitemap vẫn biết ngày sửa cuối (lấy từ git), chỉ người đọc là không
thấy dòng đó.

### 2.5 Furigana (cách đọc trên chữ Hán)

Viết cách đọc trong ngoặc ngay sau chữ Hán, như viết tay. Lúc build, Hugo tự
đổi thành furigana nhỏ nằm trên chữ:

```
元（げん）という字には、始（はじ）まりという意味（いみ）がある。
```

- Chỉ đổi khi **trong ngoặc toàn hiragana hoặc katakana** và ngoặc đứng **sát
  ngay sau chữ Hán**. Ngoặc toàn góc `（）` (bộ gõ tiếng Nhật ra sẵn) hay nửa
  góc `()` đều được.
- Chữ có okurigana thì chỉ gắn cho phần chữ Hán: `食（た）べる`, không viết
  `食べる（たべる）` (cách này giữ nguyên ngoặc).
- Cụm chữ Hán dài mà chỉ muốn gắn cho một phần: đặt `｜` trước phần đó (gõ
  phím `|` khi đang bật bộ gõ tiếng Nhật): `日本語｜学習（がくしゅう）`.
- Ngoặc giải thích thường, có chữ Hán, chữ Latin hay dấu cách bên trong, như
  `東京（Tokyo）`, giữ nguyên.
- Dùng được trong cả bài tiếng Việt lẫn tiếng Nhật, và trang Giới thiệu. Trong
  tiêu đề, đoạn trích và RSS, ngoặc giữ nguyên dạng `元（げん）`.

Muốn giải nghĩa vài từ ngay trong bài, dùng khung từ vựng: mỗi dòng một từ,
nghĩa sau dấu gạch đứng, từ viết furigana được như trên.

```
{{< tu-vung >}}
書（か）き順（じゅん） | thứ tự nét viết
復習（ふくしゅう） | ôn tập
{{< /tu-vung >}}
```

Bài nào có furigana thì dưới dòng ngày đăng tự có một khung nhỏ để người đọc
chọn: **Hiện**, **Chạm để xem** (ẩn cách đọc, chạm hoặc rê chuột vào chữ mới
hiện, để tự kiểm tra) và **Tắt**. Trình duyệt nhớ lựa chọn cho các bài sau.

Mọi bài tiếng Nhật đều phải có furigana, không riêng bài học tiếng. Lệnh
`/dich` đã mang sẵn quy tắc này: gắn cách đọc ở lần xuất hiện đầu tiên của mỗi
từ trong bài, không gắn lại ở các lần sau, và không gắn trong tiêu đề hay
`description` (mấy chỗ đó không đi qua bộ đổi nên ngoặc sẽ hiện nguyên xi).

### 2.6 Kiểu trình bày

Mỗi bài chọn một kiểu ở ô **Kiểu trình bày** trong CMS (trường `variant` nếu
viết tay). Hai kiểu dùng chung font, màu, sidebar; chỉ khác phần đầu bài:

| Kiểu | `variant` | Hiển thị | Hợp với |
|---|---|---|---|
| Mặc định | để trống hoặc `default` | Tiêu đề, ảnh bìa ngay dưới tiêu đề, bài | Đa số bài |
| Sổ học | `study` | Như Mặc định, thêm khung **Trong bài này** liệt kê các mục (từ hai mục trở lên) | Bài học tiếng Nhật, ghi chép dài |

Cả hai ngôn ngữ đều **viết ngang**, không có chữ dọc ở đâu cả, để bố cục bản
Việt và bản Nhật giống nhau. (Hai kiểu cũ `photo` và `vertical` đã bỏ; bài nào
còn ghi hai giá trị đó thì tự hiện như Mặc định.)

Ảnh bìa luôn nằm **dưới tiêu đề**. Ảnh khác chèn ở chỗ nào trong bài cũng được:
trong CMS bấm **+ → Ảnh** tại vị trí muốn chèn, hoặc viết tay
`![Chú thích](ten-anh.jpg)` ngay dòng đó (mục 3).

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
| Nhỏ, ở giữa cột | Tối đa 20rem, cho mã QR hay hình nhỏ (`{class="narrow"}`) |

Trên điện thoại, ảnh nào cũng tràn sát hai mép màn hình, trừ cỡ nhỏ.

Viết bằng tay thì dùng cú pháp Markdown. Chú thích đặt trong dấu nháy kép, cỡ
ảnh đặt ở **dòng ngay bên dưới**:

```markdown
![Cầu Yodo lúc hoàng hôn](cau-yodo.jpg "Cầu Yodo, cuối tháng Chín")
{class="narrow"}
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
   danh mục sang tiếng Nhật (`chuyen-di` → `tabi`), đặt `draft: true`.
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
| Trang Về Nguyên (Gen) | CMS → **Trang**, hoặc `content/vi/about.md`, `content/ja/about.md` |
| Trang Về blog này | Mục đích, ý tưởng: CMS → **Trang** → **Về blog này**, hoặc `content/vi/blog.md`, `content/ja/blog.md`. Bảng màu: `data/palette.toml` (màu nhấn theo tiết khí thì ở `data/sekki.toml`). Lời dưới kamon, con dấu: `i18n` (`blog_*`) |
| Menu đầu trang, submenu Giới thiệu | `hugo.toml` → `menus.main` (mục con có `parent`). Submenu Danh mục tự liệt kê các danh mục |
| Menu nhỏ ở chân trang | `hugo.toml` → `menus.under` |
| Trang 404 | `hugo.toml` → `notFoundTitle`, `notFoundText`, `notFoundHome` (mỗi ngôn ngữ một bộ) |
| Ảnh chân dung ở sidebar | Thay file `assets/brand/avatar.jpg` (site tự cắt khung dọc 4:5 lấy phần giữa, nên dùng ảnh dọc, mặt ở giữa) |
| Trang Ủng hộ và khung Ủng hộ ở chân trang | `content/vi/support/index.md` (kèm ảnh mã QR), `content/ja/support/index.md`; lời trong khung ở `i18n` (`sidebar_support_text`). Xoá file thì khung tự ẩn |
| Lời giới thiệu ở sidebar | `hugo.toml` → `[languages.vi.params]` → `bio` (bản tiếng Nhật: `[languages.ja.params]`) |
| Tagline dưới tên blog và ở chân trang | `hugo.toml` → `tagline` (hai ngôn ngữ) |
| Email, mạng xã hội ở trang Liên hệ | `hugo.toml` → `[params]` → `email`, `[params.socials]` |
| Bài lớn ở đầu trang chủ | Trong CMS bật ô **Bài viết nổi bật** ở bài muốn đưa lên (trường `spotlight: true`), ảnh riêng ở ô **Ảnh bài viết nổi bật** (`spotlight_image`, để trống thì dùng ảnh bìa). Nhiều bài cùng bật thì bài mới nhất được chọn; không bài nào bật thì là bài mới nhất. Mỗi ngôn ngữ bật riêng |
| Số bài ở trang chủ | `hugo.toml` → `homeRecentCount` |
| Chữ của 24 tiết khí: lời giải thích (khung hiện khi rê chuột vào tên tiết khí), tên màu và câu "vì sao" ở trang Về blog này | CMS → **24 tiết khí** (mục riêng), hoặc `data/sekki_notes.yaml` |
| Màu nhấn của site (đổi theo tiết khí) | `tools/sekki_colors.py` — sửa sắc/độ tươi của tiết trong bảng `SEKKI`, chạy `./.venv/bin/python tools/sekki_colors.py --toml` rồi dán vào `data/sekki.toml`. Chạy không có `--toml` thì ra bảng kiểm tương phản. Đừng sửa tay mã màu trong `data/sekki.toml` |
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
tải font gốc → subset font toàn site → hugo --minify → font cho từng trang → soát HTML → Pagefind → GitHub Pages
```

Bước **soát HTML** (`tools/check.py`) tìm link nội bộ hỏng, id trùng, ảnh thiếu
chữ thay ảnh và trang không đúng một h1. Nó chỉ cảnh báo, không chặn deploy:
có lỗi thì dấu ✓ vẫn xanh nhưng trang tóm tắt của lần chạy hiện danh sách lỗi
màu vàng. Chạy ở máy sau khi build: `python3 tools/check.py public`.

Xem tiến trình ở tab **Actions** trên GitHub: dấu ✓ xanh là đã lên site, dấu ✗
đỏ là lỗi (xem [mục 8](#8-xử-lý-lỗi-thường-gặp)).

Build tay: tab **Actions** → **Deploy** → **Run workflow**.

### Chế độ bảo trì

Khi `maintenance = true` trong mục `[params]` của [hugo.toml](hugo.toml),
nguyenta.com chỉ hiện vòng ensō của trang 凪 với dòng "Nơi này đang được
dựng", có link sang bản tiếng Nhật. Workflow chỉ đưa lên trang đó, file CSS
và font, nên bài viết, ảnh, RSS, sitemap và chỉ mục tìm kiếm không
có trên mạng, đoán URL cũng không mở được. Máy tìm kiếm được báo là không
ghi nhận trang.

- **Mở blog:** đổi thành `maintenance = false`, commit. Vài phút sau site hiện đầy đủ.
- **Viết bài trong lúc bảo trì:** viết và push như thường. Bài nằm trong repo
  và xem được ở [bản xem trước](#114-bảo-trì-và-bản-xem-trước-ai-thấy-gì),
  nhưng người ngoài chưa đọc được cho tới khi mở blog.
- Trang **Về blog này** ([nguyenta.com/ve-blog/](https://nguyenta.com/ve-blog/),
  bản tiếng Nhật `/ja/about-blog/`, đường dẫn cũ `/concept/` tự chuyển sang)
  vẫn mở cho mọi người, nhờ dòng `maintenance_exempt: true` trong
  `content/vi/blog.md` và `content/ja/blog.md`. Lúc bảo trì trang này không có
  header và footer, vì menu khi đó dẫn tới các trang chưa mở.
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
Trên GitHub có commit mà máy chưa có, thường là thay đổi đẩy lên từ máy khác.
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
Hai bản phải có cùng `translationKey`. Xem ô **Mã nối bản dịch** trong CMS ở cả
hai bài (hoặc mở hai file, so dòng `translationKey`) — phải giống nhau tuyệt
đối.

**Nút "Kiểm tra Xem trước" trong CMS bấm không có gì xảy ra.**
Bình thường — nút này của Decap dùng cho "deploy preview" (mỗi lần lưu có một
bản build riêng để xem thử, kiểu Netlify), nhưng GitHub Pages không có tính
năng đó nên `show_preview_links: false` đã tắt trong `config.yml`. Decap vẫn
hiện nút (không ẩn được hoàn toàn) nhưng bấm vào không làm gì cả, không phải
lỗi. Muốn xem bài đang viết thật sự: mở `http://localhost:1313/` (chạy song
song `tools/dev.sh` hoặc `hugo server --buildDrafts`), site sẽ hiện cả bài
đang để Bản nháp.

---

## 9. Cấu trúc thư mục

```
content/vi/, content/ja/   Nội dung hai ngôn ngữ: bài viết (posts/), danh mục, các trang
layouts/                   Template HTML của Hugo; home.rss.xml là RSS (chỉ bài viết)
assets/css/main.css        Toàn bộ CSS, một file duy nhất
assets/js/                 site.js (lightbox, video, bản tin, tiết khí, đồng hồ…), search.js
assets/brand/              Kamon, con dấu 元, ảnh chân dung, ảnh chia sẻ
static/admin/              Decap CMS, chỉ dùng ở máy: config.yml (form), cms.js (nút chèn ảnh/video)
i18n/                      Chữ trên giao diện, theo ngôn ngữ
data/sekki.toml            24 tiết khí: ngày và mã màu nhấn
data/sekki_notes.yaml      Chữ của 24 tiết khí: lời giải thích, tên màu, câu "vì sao"
archetypes/posts.md        Mẫu cho bài mới tạo bằng hugo new
tools/fonts/               Tải và subset font (Literata, Shippori Mincho)
tools/brand/               Script vẽ kamon, favicon, con dấu, vòng ensō
tools/new-ja-draft.py      Tạo khung bản dịch tiếng Nhật (lệnh /dich gọi script này)
tools/preview/             Cấu hình Worker bản xem trước riêng (xem mục 11.4)
tools/kit/                 Mẫu thư bản tin cho Kit, cùng dáng với blog
tools/check.py             Soát HTML sau khi build (link hỏng, id trùng, alt, h1)
static/sw.js               Service Worker: giữ font, CSS, JS, ảnh có mã băm trên máy người đọc
tools/dev.sh               Chạy site ở máy kèm font và chỉ mục tìm kiếm
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
 Viết ở máy, git push ───►│ repo nguyentajp/nguyenta.com (mã nguồn) │
                          │        │ mỗi commit lên main           │
                          │        ▼                               │
                          │ GitHub Actions: build bằng Hugo        │
                          │        │                               │
                          │        ▼                               │
                          │ GitHub Pages: phục vụ file tĩnh ───────┼──► https://nguyenta.com
                          └────────────────────────────────────────┘       ▲
                                   │ cùng lúc, build bản đầy đủ             │ DNS (Hostinger):
                                   ▼ (secret CLOUDFLARE_API_TOKEN)          │ tên miền trỏ về GitHub
                          ┌────────────── Cloudflare ──────────────┐
                          │ Worker nguyenta-preview                │
                          │   site đầy đủ, có Cloudflare Access ───┼──► chỉ Gen xem được
                          └────────────────────────────────────────┘
```

Hai nửa độc lập với nhau: **GitHub** giữ mã nguồn và phục vụ site công khai;
**Cloudflare** chỉ giữ bản xem trước có khoá, việc GitHub Pages không làm
được. Cloudflare hỏng thì nguyenta.com vẫn chạy bình thường.

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
font, chạy Hugo, ghi font cho từng trang, lập chỉ mục tìm kiếm, rồi giao kết
quả cho GitHub Pages. Nhờ vậy chỉ cần `git push`, không phải tự build hay tự
upload gì. Cấu hình: [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

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
Google Fonts, nên trình duyệt người đọc không phải kết nối tới Google. Font
được cắt còn đúng những chữ site dùng, thay vì cả bộ vài MB: một bộ dùng
chung cho cả site (chữ Latin, tiếng Việt khoảng 110 KB; kana và chữ giao diện
tiếng Nhật khoảng 65 KB), tải một lần rồi Service Worker (`static/sw.js`) giữ
trên máy; bài tiếng Nhật thêm một file nhỏ chỉ gồm chữ Hán riêng của bài
(trung bình 16 KB). Chuyển trang vì vậy không tải lại font, chữ không nháy.

**Decap CMS** (`static/admin/`). Giao diện có form để viết bài ở `/admin`,
dùng ở máy. `npx decap-server` là cầu nối cho CMS ghi thẳng file vào thư mục
repo; "Công bố" trong CMS chỉ là lưu file. Trang `/admin` không được đưa lên
nguyenta.com (workflow xoá nó khi build), xem lý do ở mục 11.7.

**Cloudflare.** Công ty vận hành mạng máy chủ khắp thế giới. Ở đây chỉ dùng
hai dịch vụ miễn phí, **Workers** và **Access**, cho bản xem trước. Tài khoản đăng ký bằng
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
gọi bằng `npx wrangler@4` (ghim bản 4), và chạy **trong thư mục blog** vì
đường dẫn `--config` tính từ đó. Đăng nhập một lần bằng
`npx wrangler login`; quyền được lưu trong máy ở
`~/Library/Preferences/.wrangler/`.

### 11.3 Vì sao chỉ viết bài ở máy

Muốn CMS chạy trên web (`nguyenta.com/admin`), CMS phải được GitHub cho phép
ghi vào repo thay anh. GitHub chỉ cấp quyền đó qua một **GitHub OAuth App**,
và app phải chứng minh mình là thật bằng một **Client secret** (một mật khẩu
của app). Secret không được nằm trong trình duyệt hay repo public, mà GitHub
Pages lại chỉ phục vụ file tĩnh, nên cần thêm một máy chủ nhỏ giữ secret
(ví dụ một Cloudflare Worker) chỉ để làm bước đăng nhập.

Đã thử dựng phần này (tháng 9/2026) rồi bỏ: thêm một OAuth App, một secret
phải cất và thay khi lộ, một Worker phải giữ chạy, chỉ để đổi lấy việc viết
được từ điện thoại. Viết ở máy rồi `git push` đơn giản hơn nhiều và không có
gì để hỏng. Code Worker cũ vẫn còn trong lịch sử Git, ở commit `4f35d2c`
(thư mục `tools/cms-auth/`), nếu sau này muốn dựng lại.

### 11.4 Bảo trì và bản xem trước: ai thấy gì

| Địa chỉ | Ai xem được | Nội dung |
|---|---|---|
| `nguyenta.com` và mọi trang con | Mọi người | Lúc bảo trì: chỉ trang ensō "đang dựng" (xem [mục 7](#7-build-và-deploy)) |
| `nguyenta.com/ve-blog/` | Mọi người | Trang Về blog này (mục đích, ý tưởng, màu sắc), mở cả khi bảo trì |
| `nguyenta-preview.genblog.workers.dev` | Chỉ anh (Cloudflare Access) | Site đầy đủ, không bảo trì, không bài nháp |
| `localhost:1313/admin/` | Chỉ trên máy anh | CMS để viết bài |

Bản xem trước là Worker `nguyenta-preview` chỉ chứa file tĩnh
([tools/preview/wrangler.toml](tools/preview/wrangler.toml)). Nó được build
riêng với `maintenance = false` và địa chỉ gốc của chính nó, vào thư mục
`preview-public/` (không commit). Workflow tự làm việc này mỗi lần chạy, nhờ
secret `CLOUDFLARE_API_TOKEN` (mục 11.6); thiếu secret thì bước đó tự bỏ qua,
Cloudflare lỗi cũng không chặn nguyenta.com. Khi cần đẩy tay từ máy:

```bash
HUGO_PARAMS_MAINTENANCE=false HUGO_ENVIRONMENT=production hugo --minify --baseURL https://nguyenta-preview.genblog.workers.dev/ -d preview-public
```

```bash
rm -rf preview-public/admin
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
| Git qua HTTPS (`github.com`) | Lệnh `git push` / `git pull` trên máy | Đẩy bài lên repo, lấy thay đổi về |
| API cục bộ của `decap-server` (`localhost:8081`) | CMS ở máy | Đọc và ghi file bài viết trong thư mục repo |
| GitHub Pages API (qua lệnh `gh api`) | Dùng một lần khi dựng | Bật Pages với nguồn Actions, đặt tên miền, bật HTTPS |
| Cloudflare API (qua `wrangler`) | GitHub Actions, hoặc từ máy anh | Deploy Worker bản xem trước |
| YouTube (`youtube-nocookie.com`) | Trình duyệt người đọc, chỉ khi bấm phát | Phát video nhúng trong bài |

### 11.6 Tài khoản và bí mật nằm ở đâu

| Thứ | Nằm ở | Lộ hoặc mất thì làm gì |
|---|---|---|
| Tài khoản GitHub `nguyentajp` | — | Giữ bật xác thực hai lớp (2FA): tài khoản này ghi được cả site |
| Tài khoản Cloudflare | Email `nguyentajp1403@gmail.com` | Cũng là chìa khoá của bản xem trước (Access), nên giữ mật khẩu mạnh và 2FA |
| Cloudflare API token | GitHub › Settings › Secrets › `CLOUDFLARE_API_TOKEN` (chỉ quyền Workers Scripts: Edit) | Xoá token ở Cloudflare › My Profile › API Tokens, tạo token mới, `gh secret set CLOUDFLARE_API_TOKEN` |
| Quyền wrangler trên máy | `~/Library/Preferences/.wrangler/` | Thu hồi: `npx wrangler logout` |
| Tên miền | Hostinger | Nhớ gia hạn hằng năm; hết hạn là site mất |

### 11.7 Những quyết định đã chọn và lý do

- **Chỉ viết bài ở máy, không có CMS trên web**: CMS trên web cần OAuth App,
  Client secret và một máy chủ đăng nhập riêng (mục 11.3). Đổi lại chỉ được
  viết từ điện thoại, không đáng với số thứ phải giữ. `/admin` cũng bị gỡ khỏi
  nguyenta.com, vì để một trang đăng nhập không dùng được chỉ gây rối.
- **Nếu sau này muốn viết trên web**: dựng lại Worker trong commit `4f35d2c`,
  tạo OAuth App, thêm `base_url` vào `static/admin/config.yml`, và bỏ bước
  "Bỏ trang CMS" trong workflow.
- **Repo public**: bắt buộc để dùng GitHub Pages miễn phí. Muốn repo private
  thì phải trả GitHub Pro.
- **DNS để ở Hostinger**: Cloudflare chỉ cần cho bản xem trước, không cần giữ tên miền.
- **Bảo trì bằng cách lọc file khi deploy**, không chỉ đổi giao diện: đổi giao
  diện thôi thì đoán đúng URL, RSS hay sitemap vẫn đọc được bài.
- **Bản xem trước có Access** thay cho đường dẫn bí mật: đường dẫn bí mật thì
  ai có link là xem được; Access bắt đăng nhập thật.
- **Access policy "Cloudflare account members"**: không phải khai email riêng,
  và không ai ngoài chủ tài khoản vào được.
- **Worker thay cho Cloudflare Pages**: Cloudflare đã gộp Pages vào Workers;
  wrangler mới tạo project Pages kiểu cũ không được.

#### Giao diện — chốt ngày 20/9/2026

Đây là bản gốc của các quyết định về giao diện. Trước đây chúng chỉ nằm trong
khung chat nên không tra lại được, và Claude đã làm lệch một lần (七十二候).
Có quyết định mới thì ghi vào đây.

- **Trang tiếng Việt càng ít chữ Nhật và chữ Hán càng tốt.** Chỉ còn link
  chuyển ngôn ngữ (日本語). Đừng thêm chữ Hán trang trí vào trang tiếng Việt.
- **Bài viết nổi bật đứng đầu cả trang chủ lẫn trang Bài viết.** Không có
  nhãn "Spotlight", không chạy vòng, mỗi lúc đúng một bài.
- **Gọi là "Bài viết nổi bật"**, không gọi là Spotlight — kể cả nhãn trong
  CMS. Tên trường trong file bài vẫn là `spotlight`.
- **Mục "Gần đây" ở trang chủ giữ nguyên lưới ảnh to**, không đổi sang kiểu
  ảnh nhỏ ba dòng như trang Bài viết.
- **Trang Ảnh đã xoá hẳn**, không đặt link ở chân trang.
- **Giải thích 24 tiết khí chỉ hiện khi rê chuột vào tên tiết khí.** Không
  làm trang riêng để liệt kê.
- **Không làm 七十二候.** Claude từng tự đề xuất rồi ghi nhầm là đã duyệt;
  đã gỡ ở commit `402a743`. Đừng đề xuất lại.
- **Màu nhấn đổi theo 24 tiết khí thì giữ** — cái này có trong "Yêu cầu.md".
- **Vòng tre của kamon có ba vành đốt (節)**, không còn là ba cung tròn cách
  nhau bằng khe trống. Hồi vòng mang màu tre khô thì màu gánh phần "tre"; đổi
  sang màu mực thì hình phải tự nói được, nên đưa cái đốt vào. Favicon 16–32px
  vẫn dùng bản ba cung trơn vì ở cỡ đó vành đốt mảnh hơn một pixel.
- **Vòng tre của kamon mang màu mực 墨**, lá vẫn xanh đậm 常磐. Anh chọn mực
  trong bốn phương án đã đưa (vàng, mực, tre khô, xanh nhạt); trước đó là tre
  khô 枯竹 #9c8352. Đổi màu thì sửa `--kamon-ring` trong main.css VÀ
  `KAMON_COLORS` trong `tools/brand/marks.py`, rồi chạy lại `marks.py` và
  `raster.py` (favicon mang màu sẵn vì không đọc được CSS của trang).
- **Khung có nhãn đề (sidebar, Mục lục, Từ vựng, Ủng hộ) có nền riêng**, màu
  奉書 `--card`: sáng hơn nền trang một nấc chứ KHÔNG trắng tinh. Anh đã xem
  ba phương án (trong suốt / trắng tinh / trắng giấy) và chọn trắng giấy, vì
  trắng tinh sẽ là thứ sáng nhất site, sáng hơn cả màu giấy 障子.
- **Không làm trang chủ kiểu bìa (表紙).** Đã dựng bốn mẫu ngày 20/9, từ nhẹ
  tới đậm; anh xem rồi thấy màu mè. Đầu trang hiện tại đã đủ. Đừng đề xuất lại.

#### Bản tin — chốt ngày 21/9/2026

- **Dùng Kit (kit.com), không dùng Buttondown.** Buttondown free chỉ 100 người
  đăng ký; Kit free tới 10.000 người và gửi bao nhiêu số cũng được. Cả hai đều
  là form POST thẳng, không API key trong repo — nên đổi nhà chỉ là sửa bốn
  dòng trong `[params.newsletter]`. (JS gửi ngầm đang viết theo JSON của Kit;
  đổi nhà thì sửa cả `site.js` mục 8.)
- **Không cần tự gửi bài mới theo RSS.** Anh tự soạn và bấm gửi từng số cho
  những người đã đăng ký. Vì thế mức free của Kit là đủ, không phải trả tiền.
- **Không dùng Substack**, tuy nó vừa free vừa không giới hạn người: bài sẽ
  phải đăng bên đó nữa, tức là viết hai nơi và người đọc bị kéo sang sân của
  họ.

#### Giao diện điện thoại — làm lại ngày 22/9/2026

Nguyên tắc: điện thoại được thiết kế riêng, không phải bản máy tính thu nhỏ.
Mọi thứ về **một trục giữa** như đầu trang (bìa sổ).

- **Tiêu đề bài trong danh sách căn giữa** (bài nổi bật, lưới Gần đây, và
  danh sách trên điện thoại). Riêng danh sách trên màn hình rộng giữ ảnh nhỏ
  bên trái, chữ bám mép ảnh.
- **Đầu trang điện thoại:** ☰ và kính lúp ở hàng công cụ (ô tìm chữ bị cắt
  thành "Tìm tr…" nên bỏ); bốn mục menu vẫn nằm ngang, bấm một lần là tới;
  bảng Menu (☰) là bản đồ đầy đủ: logo, ô tìm, danh mục dạng ô bấm, trang con.
- **Sidebar khi nằm dưới nội dung** (tablet, điện thoại): nhãn đề ra giữa,
  bỏ khối Bài viết mới (trùng danh sách / bài liên quan ngay trên), danh mục
  và lưu trữ thành ô bấm xếp hàng.
- **Chân trang một cột:** căn giữa; bản tin lên ngay sau logo; hai cột link
  đứng cạnh nhau.
- **Ô bấm trên điện thoại cao ít nhất 40–44px.** Soát lại ngày 23/9 và sửa
  cho đủ: tên bài trên thanh dính (trước 21px), nút chuyển bài liên quan
  (32px), link thẻ cuối bài (24px), nút furigana dưới tiêu đề (30px). Hai nút
  🌐 và sáng/tối trên thanh dính trước đây dính sát nhau, nay chừa khe 8px.
  **Ngoại lệ có chủ ý:** hàng furigana *trong thanh dính* giữ 28px để thanh
  còn mảnh — vẫn trên mức tối thiểu 24px của WCAG 2.2 AA cho web.
- **Thanh tiêu đề dính** (kiểu thanh điều hướng iOS): tiêu đề lớn cuộn đi thì
  thanh mảnh trượt xuống: ☰ · tên bài (chạm để lên đầu) · 🌐 · sáng tối. 🌐
  chỉ mở khung chọn ngôn ngữ khi bấm. Không có kính lúp (ô tìm nằm trong ☰).
  Bài có furigana thêm hàng nút furigana; bài viết có vạch đã đọc tới đâu.
- **Menu là ngăn kéo trượt từ trái** (off-canvas), nền tối phía sau, chạm ra
  ngoài để đóng. Không có JS vẫn mở được (Popover API). Thứ tự trong ngăn:
  ô tìm · Giới thiệu (và trang con) · Bài viết · Danh mục · Mục lục · Liên
  hệ · công tắc ngôn ngữ và sáng tối · Thẻ, Nagi. Liên hệ là mục chính ở đây
  (ngoài hàng menu nó vẫn là link ở chân trang). Chỗ đang đứng: chữ màu nhấn
  và vạch màu nhấn bên trái, không gạch chân.
- **Máy cảm ứng không có menu con kiểu rê chuột** (iPad, điện thoại xoay
  ngang): bấm tên mục là tới trang; bản đồ đầy đủ trong ngăn ☰.
- **Trang Danh mục trên điện thoại:** hình nhỏ cạnh tên, danh sách bài trải
  hết bề ngang, ngày ở trên tên bài.
- **Đầu trang danh sách là tấm nhãn đề nền 白緑** (danh mục, thẻ, Bài viết,
  Mục lục, Tìm kiếm, Giới thiệu): tên mục cha chữ nhỏ, tiêu đề, một dòng
  "mô tả · số bài". Điện thoại: sát hai mép, nối liền dưới hàng menu.
- **Đoạn trích và thẻ mô tả bỏ cách đọc furigana** (秋（あき） → 秋); mở bài
  ra thì furigana vẫn đủ.
- **Chuyển trang mượt như app** (22/9): font dùng chung cho cả site (chữ
  Latin, tiếng Việt; kana và chữ giao diện tiếng Nhật), chỉ chữ Hán riêng của
  từng bài tiếng Nhật là file riêng; Service Worker (`static/sw.js`) giữ font,
  CSS, JS, ảnh có mã băm trên máy; Speculation Rules dựng sẵn trang khi chạm
  vào link. Trang đầu nặng hơn (~110 KB font thay vì ~45 KB), các trang sau
  gần như không tải font. Tắt khẩn cấp Service Worker: xem đầu `static/sw.js`.
- **Mọi đoạn chữ canh đều hai lề** (thân bài, danh sách, đoạn trích, lời dẫn
  đầu trang, mô tả màu và 24 tiết khí, chú thích trong khung, lời giới thiệu
  ở sidebar, bản tin, kết quả tìm kiếm). Tiếng Nhật giãn giữa ký tự (両端揃え).
  Khối căn giữa thì dòng cuối nằm giữa. Không canh đều: tiêu đề, tên bài,
  tagline, nhãn ngày tháng.
- **Khe chữ chênh nhau trên điện thoại là chấp nhận, không sửa nữa**
  (chốt 23/9). Cột trên điện thoại chỉ 37 ký tự nên canh đều làm khoảng trắng
  giữa từ chênh tới 2,97 lần (hẹp nhất 3,6px, rộng nhất 10,7px). Đã đo bốn
  cách chữa: `hyphens: auto` **vô tác dụng** với tiếng Việt (số liệu y hệt,
  trình duyệt không có bộ gạch nối tiếng Việt); lề 20→16px đỡ 17%; chữ
  18→17px đỡ 13% nhưng chữ nhỏ lại; gộp cả hai gần như vô ích (2,92×). Anh
  chọn giữ nguyên: sách tiếng Việt in cũng vậy, hợp chủ ý "trang sách".
  `text-wrap: pretty` đã bật sẵn. Đừng đề xuất lại, nhất là `hyphens: auto`.

#### Sau đợt review code — chốt ngày 21/9/2026

- **Link RSS nằm dưới ô đăng ký bản tin**, không ở hàng mạng xã hội.
- **Dòng "Cập nhật" chỉ hiện khi điền tay** (trường `updated`); ngày từ git
  chỉ dành cho máy (sitemap, Google).
- **Không làm nút chia sẻ / sao chép link cuối bài.** Đừng đề xuất lại.
- **Thống kê người đọc để sau**: khi làm thì dùng Cloudflare Web Analytics
  (tài khoản Cloudflare đã có, không cookie).

#### Logo — chốt ngày 21/9/2026

- **Tên blog ở đầu trang và chân trang là HÌNH chữ "Gen"**, cắt sẵn thành
  đường viền từ Shippori Mincho B1 SemiBold — chính bộ chữ site dùng cho tiêu
  đề tiếng Nhật, nên logo và site là một bộ. Chữ Latin của một bộ minh triều
  Nhật mang đúng chất Nhật mà vẫn đọc được với người Việt. Sinh bằng
  `tools/brand/logo.py`, nhúng qua `_partials/wordmark.html`.
- **Không dùng chữ Hán trong logo.** 元 và ゲン đã dựng thử ngày 21/9 rồi bỏ.
  Con dấu 元 cuối bài thì vẫn giữ — đó là con dấu, không phải logo.
- **Không dùng nét vẽ tay cho chữ.** Đã thử chữ thư pháp dựng bằng nét bút
  lông (元, ゲン, Gen); anh xem rồi thấy xấu. Chữ phải là typography. Đừng
  đề xuất lại.
- **Vòng tre của kamon giữ nguyên, không đổi sang ensō.** Đã dựng thử ensō
  vector thay vòng tre ngày 21/9; anh bác. Ensō vẫn chỉ dùng ở trang 凪 và
  trang bảo trì. Đừng đề xuất lại.
- **Chữ cắt thành đường viền, không gọi font.** Bản Shippori gửi tới người đọc
  đã cắt bỏ chữ Latin cho nhẹ trang (`tools/fonts/build.py`, scope "ja"), nên
  viết "Gen" bằng nó sẽ phải gửi thêm một file font cho mọi trang. Cắt thành
  đường viền còn tránh được cảnh chữ nhảy font lúc trang mới tải. Chữ cho máy
  đọc màn hình đặt ở thẻ `.visually-hidden` ngay cạnh.
- **`logo.svg` là bản ghép sẵn kamon + chữ**, dành cho chỗ ngoài site (ảnh đại
  diện Facebook, in ấn) nơi không có CSS của site để xếp hai thứ cạnh nhau.
  Trên site thì dùng hai mảnh rời, vì đầu trang còn cần vòng tre tự vẽ.

### 11.8 Đang làm dở

- [x] Workflow tự đẩy bản xem trước mỗi lần push (cần secret `CLOUDFLARE_API_TOKEN`).
- [x] Xoá bài thử `zz-thu-nghiem-anh`.
- [x] Thông tin chuyển khoản và mã VietQR ở trang Ủng hộ.
- [ ] Xoá bài demo: các thư mục trong `content/*/posts/` có `demo: true` trong
      front matter (ảnh bìa của chúng là ảnh vẽ tạm). Tìm bằng
      `grep -rl '^demo: true' content`. Chưa xoá thì workflow không cho mở blog.

      **Cách anh muốn làm (chốt 20/9):** cứ để nguyên bài demo trên bản xem
      trước cho dễ hình dung tổng thể, xong xuôi hết mới xoá một lượt. Vì thế
      MỌI bài do Claude viết đều phải mang dấu `demo: true`, kể cả mấy bài đầu
      tiên vốn gọi là "bài mẫu" — không thì lần dọn cuối sẽ bỏ sót. Dấu này
      không giấu bài khỏi bản xem trước; nó chỉ chặn bài lên nguyenta.com và
      giúp lệnh grep ở trên tìm thấy.
- [ ] Thay ảnh chân dung (`assets/brand/avatar.jpg`) và thêm ảnh bìa cho các bài.
- [x] Bản tin ở chân trang: đã nối với **Kit**, form `9940557` ("Gen's Blog
      Form"), auto-confirm. Ô đăng ký gửi thật. Đổi nhà sau này thì sửa bốn dòng
      `[params.newsletter]` trong `hugo.toml`; thông số của từng nhà ghi sẵn
      ngay trong file đó. Để trống `id` thì khối quay về giao diện mẫu.

      Gửi một số bản tin: vào kit.com → **Broadcasts** → soạn → gửi. Bản free
      không tự gửi theo RSS, mỗi bài anh tự soạn và bấm gửi.

      Form gửi thẳng sang Kit nên **không có API key nào trong repo**. Có JS thì
      gửi ngầm: người đọc ở lại trang, thấy lời cảm ơn ngay dưới ô
      (`news_done` / `news_fail` trong `i18n`). Không có JS hoặc mạng lỗi thì
      form POST như thường và dừng ở trang của Kit (câu trong form → Settings →
      General, đã đặt song ngữ).

      Form Kit bật **Auto-confirm new subscribers**: nhập email là thành người
      đăng ký, không có thư xác nhận (thư của Kit chỉ có bản tiếng Anh, không
      sửa được). Một form duy nhất cho cả hai tiếng.

      Thư bản tin mặc cùng dáng với blog nhờ mẫu `tools/kit/email-template.html`
      (Kit → Email Templates → Import code, đặt làm mặc định). Đổi màu site thì
      sửa cả mẫu này.

      Mức free của vài nhà, tra lại ngày 21/9/2026:

      | Nhà | Người đăng ký | Tự gửi bài mới theo RSS |
      |---|---|---|
      | Kit (kit.com) | 10.000 | không, phải tự soạn và bấm gửi |
      | Buttondown | 100 | không, trả tiền (~$9/tháng) mới có |
      | MailerLite | 250 | không |
      | Substack | không giới hạn | có, nhưng bài phải đăng bên đó |

      Không có nhà nào vừa free, vừa không giới hạn người, vừa tự gửi. Chỗ
      "không giới hạn" duy nhất là Substack, đổi lại bài phải nằm trên
      Substack — tức là viết hai nơi.
- [ ] Mở blog: `maintenance = false` trong `hugo.toml`.
- [ ] Sau khi mở blog: thống kê người đọc bằng Cloudflare Web Analytics.
