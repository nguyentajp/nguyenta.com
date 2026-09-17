#!/usr/bin/env python3
"""Tạo khung bản dịch tiếng Nhật cho một bài tiếng Việt.

Script chỉ làm phần máy móc: copy date và translationKey, đổi slug danh mục
sang tiếng Nhật, đặt draft: true. Phần dịch do người (hoặc Claude Code qua
lệnh /dich) viết vào sau.

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


def read_front_matter(text):
    """Đọc front matter YAML đơn giản: key: value, một cấp."""
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not match:
        sys.exit("Không thấy front matter YAML trong file nguồn.")
    fields = {}
    for line in match.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if kv:
            fields[kv.group(1)] = kv.group(2).strip()
    return fields, match.group(2)


def as_list(raw):
    return [item.strip().strip('"').strip("'") for item in re.findall(r'"[^"]*"|\'[^\']*\'|[^,\[\]]+', raw or "") if item.strip(" ,")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="file tiếng Việt, ví dụ content/vi/posts/abc/index.md")
    parser.add_argument("--slug", help="slug tiếng Nhật; mặc định lấy theo slug tiếng Việt")
    args = parser.parse_args()

    source = pathlib.Path(args.source)
    if not source.is_file():
        sys.exit(f"Không tìm thấy {source}")

    fields, _ = read_front_matter(source.read_text())
    key = fields.get("translationKey") or source.parent.name
    slug = args.slug or fields.get("slug", "").strip('"') or source.parent.name
    target = pathlib.Path("content/ja/posts") / slug / "index.md"
    if target.exists():
        sys.exit(f"{target} đã tồn tại. Xoá nó trước, hoặc chọn --slug khác.")

    vi_categories = as_list(fields.get("categories", ""))
    ja_categories = [CATEGORIES.get(c, c) for c in vi_categories]
    unknown = [c for c in vi_categories if c not in CATEGORIES]
    date = fields.get("date", "")
    title = fields.get("title", "").strip('"')

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        f'title: "{title}"   # TODO: dịch tiêu đề, xem STYLE.md mục 3\n'
        f"date: {date}\n"
        f"translationKey: {key}\n"
        f"slug: {slug}\n"
        'description: ""   # TODO: dịch description\n'
        f"categories: [{', '.join(repr(c) for c in ja_categories).replace(chr(39), chr(34))}]\n"
        "tags: []   # TODO: dịch thẻ, tra GLOSSARY.md\n"
        "draft: true\n"
        "---\n\n"
        f"<!-- Bản dịch chưa viết. Nguồn: {source} -->\n"
    )

    print(f"Đã tạo {target}")
    print(f"  translationKey: {key}")
    print(f"  categories: {vi_categories} -> {ja_categories}")
    if unknown:
        print(f"  ⚠ danh mục chưa có trong bảng ánh xạ: {unknown}")
    print("Bước tiếp: mở Claude Code và chạy  /dich " + str(source))


if __name__ == "__main__":
    main()
