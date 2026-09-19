#!/usr/bin/env python3
"""Tạo khung bản dịch tiếng Nhật cho một bài tiếng Việt.

Script chỉ làm phần máy móc: copy date, translationKey, ảnh bìa và kiểu
trình bày (variant), đổi slug
danh mục sang tiếng Nhật, đặt draft: true. Phần dịch do người (hoặc Claude
Code qua lệnh /dich) viết vào sau.

Bài tiếng Việt viết từ Decap CMS không có translationKey (form không hỏi,
cho gọn). Khi đó script lấy tên thư mục bài làm translationKey và ghi thêm
vào cả file tiếng Việt, để Hugo nối được hai bản với nhau.

    python3 tools/new-ja-draft.py content/vi/posts/<slug>/index.md
    python3 tools/new-ja-draft.py content/vi/posts/<slug>/index.md --slug ja-slug
"""
import argparse
import pathlib
import re
import sys

CATEGORIES = {
    "hoc-tap": "manabi",
    "doi-song": "kurashi",
    "du-lich": "tabi",
    "suy-nghi": "shisaku",
    "nhat-ky": "nikki",
}


FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def read_front_matter(text):
    """Đọc front matter YAML một cấp, không cần thư viện ngoài.

    Hiểu cả hai cách viết danh sách: một dòng như viết tay
        categories: ["nhat-ky"]
    và nhiều dòng như Decap CMS ghi ra
        categories:
          - nhat-ky
    Danh sách nhiều dòng được trả về dạng list, còn lại là chuỗi.
    """
    match = FRONT_MATTER_RE.match(text)
    if not match:
        sys.exit("Không thấy front matter YAML trong file nguồn.")
    fields = {}
    current = None
    for line in match.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        item = re.match(r"^\s+-\s*(.*)$", line)
        if kv:
            current = kv.group(1)
            fields[current] = kv.group(2).strip()
        elif item and current is not None:
            if not isinstance(fields[current], list):
                fields[current] = []
            fields[current].append(unquote(item.group(1)))
    return fields, match.group(2)


def unquote(value):
    """Bỏ dấu nháy bao quanh; chuỗi rỗng "" coi như không có."""
    return value.strip().strip('"').strip("'").strip() if isinstance(value, str) else value


def as_list(raw):
    if isinstance(raw, list):
        return raw
    return [unquote(item) for item in re.findall(r'"[^"]*"|\'[^\']*\'|[^,\[\]]+', raw or "") if item.strip(" ,")]


def add_translation_key(source, text, key):
    """Ghi translationKey vào file tiếng Việt, ngay trước dòng --- đóng front matter."""
    match = FRONT_MATTER_RE.match(text)
    head = re.sub(r"^translationKey:.*\n?", "", match.group(1), flags=re.M).rstrip("\n")
    source.write_text(f"---\n{head}\ntranslationKey: {key}\n---\n{match.group(2)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="file tiếng Việt, ví dụ content/vi/posts/abc/index.md")
    parser.add_argument("--slug", help="slug tiếng Nhật; mặc định lấy theo slug tiếng Việt")
    args = parser.parse_args()

    source = pathlib.Path(args.source)
    if not source.is_file():
        sys.exit(f"Không tìm thấy {source}")

    text = source.read_text()
    fields, _ = read_front_matter(text)
    key = unquote(fields.get("translationKey", "")) or source.parent.name
    slug = args.slug or unquote(fields.get("slug", "")) or source.parent.name
    cover = unquote(fields.get("cover", ""))
    variant = unquote(fields.get("variant", ""))
    target = pathlib.Path("content/ja/posts") / slug / "index.md"
    if target.exists():
        sys.exit(f"{target} đã tồn tại. Xoá nó trước, hoặc chọn --slug khác.")

    vi_categories = as_list(fields.get("categories", ""))
    ja_categories = [CATEGORIES.get(c, c) for c in vi_categories]
    unknown = [c for c in vi_categories if c not in CATEGORIES]
    date = unquote(fields.get("date", ""))
    title = unquote(fields.get("title", "")).replace('"', '\\"')

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        f'title: "{title}"   # TODO: dịch tiêu đề, xem STYLE.md mục 3\n'
        f"date: {date}\n"
        f"translationKey: {key}\n"
        f"slug: {slug}\n"
        + (f"cover: {cover}\n" if cover else "")
        + (f"variant: {variant}\n" if variant and variant != "default" else "")
        + 'description: ""   # TODO: dịch description\n'
        f"categories: [{', '.join(repr(c) for c in ja_categories).replace(chr(39), chr(34))}]\n"
        "tags: []   # TODO: dịch thẻ, tra GLOSSARY.md\n"
        "draft: true\n"
        "---\n\n"
        f"<!-- Bản dịch chưa viết. Nguồn: {source} -->\n"
    )

    if not unquote(fields.get("translationKey", "")):
        add_translation_key(source, text, key)
        print(f"Đã thêm translationKey: {key} vào {source}")

    print(f"Đã tạo {target}")
    print(f"  translationKey: {key}")
    print(f"  categories: {vi_categories} -> {ja_categories}")
    if unknown:
        print(f"  ⚠ danh mục chưa có trong bảng ánh xạ: {unknown}")
    print("Bước tiếp: mở Claude Code và chạy  /dich " + str(source))


if __name__ == "__main__":
    main()
