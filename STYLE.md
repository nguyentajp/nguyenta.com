# STYLE.md — quy ước văn phong của nguyenta.com

File này là bản chốt về giọng văn. Mỗi lần dịch, Claude Code phải đọc file này
trước khi viết câu đầu tiên, để bản dịch của tháng sau vẫn giống bản dịch của
tháng trước. Bảng thuật ngữ nằm ở [GLOSSARY.md](GLOSSARY.md).

## 1. Tiếng Nhật

### Thể văn: です/ます

Toàn bộ thân bài dùng **敬体 (です・ます)**. Không trộn だ／である trong cùng một
bài.

```
✅ 夕方になると風の匂いが変わります。
❌ 夕方になると風の匂いが変わる。
```

Ba trường hợp được phép không theo です/ます:

| Trường hợp | Cách viết |
|---|---|
| Tiêu đề bài, tiêu đề mục | 体言止め: 「竹の葉が鳴る部屋で」 |
| Câu trích dẫn của người khác | giữ nguyên lời gốc |
| Chú thích ảnh ngắn | 体言止め: 「箕面の紅葉、十一月」 |

### Nhân xưng và cách gọi người đọc

- Tự gọi mình là **私**. Không dùng 僕, 俺.
- **Không dùng あなた**. Tiếng Nhật thường bỏ chủ ngữ; nếu thật cần thì viết
  「みなさん」.
- Không dùng 〜ですね, 〜でしょう? liên tục để bắt chuyện. Một bài nhiều nhất một
  lần.

### Giọng: 淡々と, giữ chừng mực

Blog này đề cao sự yên tĩnh, nên câu văn tránh phóng đại và tránh khẳng định
quá chắc.

- Nên dùng: 〜のだと思います / 〜かもしれません / 〜ような気がします
- Nhưng không lạm dụng: một đoạn chỉ một lần giảm nhẹ, nếu không văn thành
  rụt rè.
- Không dùng すごく, めっちゃ, 超. Không dùng ！ và ？ trong thân bài, trừ khi
  trích lời thoại.

### Kanji và kana

Viết kanji ở mức 常用漢字. Các từ sau **luôn viết kana** (開く):

| Viết kana | Không viết |
|---|---|
| こと、もの、とき、ところ、ため、ほう | 事、物、時、所、為、方 |
| できる | 出来る |
| すべて | 全て |
| たくさん | 沢山 |
| ある（〜である の意） | 有る |
| いろいろ | 色々 |
| 〜していく、〜してくる | 〜して行く、〜して来る |
| ください | 下さい（動詞の補助として） |

### Dấu câu và ký hiệu

- Dấu chấm phẩy: **。、** (không dùng ．，)
- Ngoặc kép: **「」**; sách và tác phẩm dùng **『』**
- Ba chấm: **……** (hai ký tự), không dùng ...
- **Không chèn dấu cách thủ công** giữa chữ Nhật và chữ Latin. CSS đã lo việc
  này bằng `text-autospace`, chèn tay sẽ ra khoảng trắng đôi.

```
✅ 2026年9月、Osakaにて。
❌ 2026年9月、 Osaka にて。
```

- Số: viết bằng chữ số nửa chiều rộng (半角): 3日, 15分, 2026年
- Ngày: **2026年9月18日**. Không dùng 和暦 (令和8年).

### Đoạn văn

Mỗi đoạn 2–4 câu. Không thụt đầu dòng một chữ (行頭一字下げ) vì đây là web;
khoảng cách giữa các đoạn đã đủ tách ý.

## 2. Tiếng Việt

### Xưng hô

- Tự gọi là **tôi**.
- Với người đọc: **không gọi trực tiếp**. Nếu buộc phải gọi thì dùng "bạn",
  không dùng "các bạn", "mọi người".

### Mức độ trang trọng: trung tính

Viết như khi kể cho một người bạn đọc nhiều sách: không suồng sã, không lên gân.

- Không viết tắt kiểu chat: ko, dc, j, vs.
- Không dùng từ tiếng Anh khi tiếng Việt có từ tương đương tự nhiên. Giữ
  nguyên khi đó là thuật ngữ (front matter, commit, shortcode).
- Không emoji trong thân bài.
- Hạn chế dấu chấm than. Một bài nhiều nhất một dấu.

### Dấu câu

- Ngoặc kép cong: **“ ”**. Cấu hình Hugo đã tắt `typographer`, nên dấu nào
  anh gõ là dấu đó hiện lên, không bị tự đổi.
- Ba chấm: **…** (một ký tự), không gõ ba dấu chấm rời.
- Không có dấu cách trước dấu phẩy, dấu chấm, dấu hai chấm.
- Tên riêng Nhật viết theo romaji **không dấu trường**: Osaka, Kyoto, Minoo,
  Midosuji. Tra bảng trong GLOSSARY.md trước khi viết.

## 3. Quy tắc dịch Việt → Nhật

### Nguyên tắc chung

1. **Dịch nghĩa và nhịp, không dịch từng chữ.** Một câu dài tiếng Việt có thể
   thành hai câu tiếng Nhật, và ngược lại.
2. **Không thêm ý mới, không bỏ ý.** Nếu một câu không dịch được trọn vẹn thì
   để lại ghi chú (xem dưới) chứ không tự ý cắt.
3. **Độ dài:** bản tiếng Nhật thường ngắn hơn bản tiếng Việt khoảng 10–20% ký
   tự. Nếu dài hơn hẳn, tức là đang dịch quá sát chữ.
4. **Tiêu đề** không dịch máy móc. Ưu tiên tiêu đề nghe tự nhiên trong tiếng
   Nhật, miễn giữ đúng hình ảnh trung tâm của bài.

### Câu đùa

Dịch sát nghĩa thường làm câu đùa chết. Thứ tự ưu tiên:

1. Tìm một cách nói tiếng Nhật gây cảm giác tương đương.
2. Nếu không có, viết lại câu cho tự nhiên và **bỏ phần gây cười**, rồi để ghi
   chú cho người biên tập.
3. **Không bao giờ giải thích câu đùa** trong bài dịch.

### Thành ngữ

1. Ưu tiên thành ngữ hoặc 四字熟語 tiếng Nhật có nghĩa gần.
2. Không có thì diễn giải ngắn bằng lời thường, tối đa một câu.
3. Không dịch nguyên văn hình ảnh nếu tiếng Nhật không dùng hình ảnh đó
   ("nước đổ lá khoai" không dịch thành 里芋の葉に水).

### Chi tiết văn hóa chỉ một bên hiểu

Thêm **một cụm giải thích rất ngắn ngay trong câu**, không dùng chú thích chân
trang, không mở ngoặc dài.

```
✅ テトの前、ベトナムの旧正月の前は、どの家も花を買います。
❌ テトの前は、どの家も花を買います。（テトとはベトナムの旧正月のことで…）
```

Chiều ngược lại cũng vậy: khi viết tiếng Việt về chuyện Nhật, giải thích gọn
trong câu ("lễ Obon, dịp người Nhật về quê thăm mộ").

### Ghi chú cho người biên tập

Khi không chắc, để lại ghi chú ngay trong file bản dịch:

```markdown
<!-- HỎI: câu đùa về "ăn cơm nhà" không dịch được, tạm viết trung tính -->
```

Cấu hình Hugo đặt `unsafe = false`, nên các ghi chú dạng HTML comment **không
hiện ra trang web**. Anh xoá chúng sau khi biên tập.

### Những thứ giữ nguyên, không dịch

- Tên các key trong front matter, và giá trị của `translationKey`, `date`
- Tên file ảnh và mọi shortcode: `{{< gallery >}}`, `{{< youtube >}}`
- Số liệu, tên thương hiệu, tên ga tàu
- Đoạn code trong khối ```

## 4. Checklist trước khi đăng bản dịch

- [ ] Toàn bài một thể です/ます, không lẫn だ/である
- [ ] Không còn ghi chú `<!-- HỎI: ... -->`
- [ ] Tên riêng và thuật ngữ khớp GLOSSARY.md
- [ ] Không có dấu cách thủ công giữa chữ Nhật và chữ Latin
- [ ] `translationKey` giống hệt bản tiếng Việt
- [ ] `categories` đã đổi sang slug tiếng Nhật (xem bảng trong GLOSSARY.md)
- [ ] `description` đã dịch, không để trống
- [ ] Đổi `draft: true` thành `draft: false` khi đã hài lòng
