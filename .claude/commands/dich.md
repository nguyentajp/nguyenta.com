---
description: Dịch nháp một bài từ tiếng Việt sang tiếng Nhật, đặt draft true
argument-hint: <đường dẫn file tiếng Việt, ví dụ content/vi/posts/abc/index.md>
---

Dịch bài `$ARGUMENTS` từ tiếng Việt sang tiếng Nhật.

## Trước khi dịch, đọc đủ ba thứ này

1. `STYLE.md` — quy ước văn phong. Bắt buộc: thân bài dùng thể です/ます.
2. `GLOSSARY.md` — bảng thuật ngữ và bảng ánh xạ danh mục.
3. File nguồn tiếng Việt.

Nếu trong bài có từ chưa có trong `GLOSSARY.md` mà sẽ còn dùng lại về sau (tên
riêng, địa danh, khái niệm), **thêm vào GLOSSARY.md trước**, rồi mới dịch.

## Các bước

1. Tạo khung file đích:

   ```bash
   python3 tools/new-ja-draft.py $ARGUMENTS --slug <slug-tiếng-nhật>
   ```

   Slug tiếng Nhật viết bằng romaji, không dấu, dùng gạch ngang, ví dụ
   `take-no-ha-ga-naru-heya-de`. Script tự copy `date`, `translationKey`, và
   đổi slug danh mục sang tiếng Nhật.

2. Viết bản dịch vào file vừa tạo:
   - `title`: tiêu đề tự nhiên trong tiếng Nhật, không dịch máy móc.
   - `description`: dịch, không để trống.
   - `tags`: dịch theo GLOSSARY.md.
   - Thân bài: dịch theo đúng STYLE.md mục 3.
   - Giữ nguyên mọi shortcode, tên file ảnh, số liệu, khối code.
   - `draft: true` giữ nguyên. Chỉ chủ blog mới đổi thành `false`.

3. Chỗ nào không chắc thì để ghi chú ngay trong file:

   ```markdown
   <!-- HỎI: ... -->
   ```

4. Kiểm tra bản dịch build được:

   ```bash
   hugo --quiet -D
   ```

## Báo cáo lại cho chủ blog

Sau khi dịch, báo ngắn gọn bằng tiếng Việt:

- Đường dẫn file đã tạo.
- Những chỗ đã xử lý đặc biệt: câu đùa, thành ngữ, chi tiết văn hóa cần thêm
  giải thích ngắn.
- Danh sách ghi chú `<!-- HỎI: -->` đang chờ chủ blog quyết.
- Từ mới đã thêm vào GLOSSARY.md.
- Nhắc chạy `hugo server -D` để xem bản nháp, và đổi `draft: false` khi hài lòng.

**Không tự ý đổi `draft: false`. Không sửa file tiếng Việt gốc.**
