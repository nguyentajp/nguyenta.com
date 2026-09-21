#!/usr/bin/env python3
"""Soát HTML đã build: link nội bộ hỏng, id trùng, ảnh thiếu alt, số h1.

    python3 tools/check.py public

Chạy SAU hugo. Không cần thư viện ngoài. In mỗi lỗi một dòng; trong GitHub
Actions in thành ::warning để hiện ở trang tóm tắt của lần build. Trả mã 1
nếu có lỗi (workflow để continue-on-error nên không chặn deploy).

Bỏ qua: trang chuyển hướng (alias), thư mục pagefind, link ra ngoài site.
Trang 404, trang 凪 không cần đúng một h1 theo kiểu thường nên vẫn soát, và
đều đã có h1 (có cái ẩn).
"""
from __future__ import annotations

import collections
import os
import pathlib
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

SITE_HOSTS = {"nguyenta.com", "nguyenta-preview.genblog.workers.dev"}
SKIP_DIRS = {"pagefind", "admin"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: collections.Counter[str] = collections.Counter()
        self.links: list[str] = []
        self.no_alt: list[str] = []
        self.h1 = 0
        self.redirect = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if "id" in a:
            self.ids[a["id"]] += 1
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            self.redirect = True
        if tag in ("a", "area") and a.get("href"):
            self.links.append(a["href"])
        if tag in ("img", "source", "script") and a.get("src"):
            self.links.append(a["src"])
        if tag == "link" and a.get("rel") in ("stylesheet", "icon", "preload", "apple-touch-icon"):
            self.links.append(a.get("href", ""))
        for part in a.get("srcset", "").split(","):
            url = part.strip().split(" ")[0]
            if url:
                self.links.append(url)
        if tag == "img" and "alt" not in a:
            self.no_alt.append(a.get("src", "?"))
        if tag == "h1":
            self.h1 += 1


def target_exists(root: pathlib.Path, page_rel: str, url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in ("mailto", "tel", "data", "javascript"):
        return True
    if parsed.netloc and parsed.netloc not in SITE_HOSTS:
        return True
    path = unquote(parsed.path)
    if not path:
        return True  # chỉ có #neo hoặc ?q=
    if not path.startswith("/"):
        path = os.path.normpath(os.path.join(os.path.dirname("/" + page_rel), path))
    target = root / path.lstrip("/")
    if target.is_dir():
        target = target / "index.html"
    return target.exists()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(sys.argv[1]).resolve()
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    problems: list[str] = []
    pages = 0

    for file in sorted(root.rglob("*.html")):
        rel = file.relative_to(root).as_posix()
        if rel.split("/")[0] in SKIP_DIRS:
            continue
        page = Page()
        page.feed(file.read_text(encoding="utf-8"))
        if page.redirect:
            continue
        pages += 1
        problems += [f"{rel}: id trùng #{i} ({n} lần)" for i, n in page.ids.items() if n > 1]
        problems += [f"{rel}: ảnh thiếu alt {src}" for src in page.no_alt]
        if page.h1 != 1:
            problems.append(f"{rel}: có {page.h1} thẻ h1 (cần đúng 1)")
        for url in sorted(set(page.links)):
            if not target_exists(root, rel, url):
                problems.append(f"{rel}: link hỏng {url}")

    for line in problems:
        print(f"::warning::{line}" if in_ci else line)
    print(f"Đã soát {pages} trang: {len(problems)} lỗi.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
