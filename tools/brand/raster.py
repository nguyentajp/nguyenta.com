#!/usr/bin/env python3
"""Xuất các ảnh raster mà SVG không thay được.

    ./.venv/bin/python tools/brand/raster.py

  static/apple-touch-icon.png   180×180, biểu tượng khi lưu site ra màn hình iPhone
  static/favicon.ico            16 và 32px, cho trình duyệt tự tìm /favicon.ico
  assets/brand/og-vi.png        1200×630, ảnh hiện khi chia sẻ link (tiếng Việt)
  assets/brand/og-ja.png        1200×630, bản tiếng Nhật

Kamon được vẽ lại từ chính đường path trong marks.py, nên ảnh raster luôn khớp
với SVG. Cần Pillow và font gốc (tools/fonts/get-sources.py).
"""
from __future__ import annotations

import math
import pathlib
import re
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/brand"))
import marks  # noqa: E402  (cùng thư mục, cần sys.path ở trên)

SHOJI = "#f2f3ee"
SUMI = "#22251f"
CHIKUEI = "#5a6055"
FONT_SRC = ROOT / "tools/fonts/src"


# ── Đọc đường path SVG thành các đa giác ────────────────────────────────────
TOKEN = re.compile(r"[MLAQZ]|-?\d*\.?\d+(?:e-?\d+)?", re.I)


def arc_points(x1, y1, rx, ry, phi, large, sweep, x2, y2, steps=48):
    """Đổi cung SVG (dạng hai đầu mút) sang dạng tâm rồi lấy mẫu điểm.
    Công thức theo phụ lục F.6 của đặc tả SVG."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    cos_phi, sin_phi = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy
    scale = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if scale > 1:
        rx, ry = rx * math.sqrt(scale), ry * math.sqrt(scale)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    factor = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = factor * rx * y1p / ry, -factor * ry * x1p / rx
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    delta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi

    points = []
    for k in range(1, steps + 1):
        t = theta1 + delta * k / steps
        x = cos_phi * rx * math.cos(t) - sin_phi * ry * math.sin(t) + cx
        y = sin_phi * rx * math.cos(t) + cos_phi * ry * math.sin(t) + cy
        points.append((x, y))
    return points


def subpaths(d: str) -> list[list[tuple[float, float]]]:
    """Chỉ hỗ trợ các lệnh marks.py dùng: M L A Q Z (toạ độ tuyệt đối)."""
    tokens = TOKEN.findall(d)
    out, current, pos, i, cmd = [], [], (0.0, 0.0), 0, None

    def num():
        nonlocal i
        value = float(tokens[i])
        i += 1
        return value

    while i < len(tokens):
        if re.fullmatch(r"[MLAQZ]", tokens[i], re.I):
            cmd = tokens[i].upper()
            i += 1
        if cmd == "M":
            if current:
                out.append(current)
            pos = (num(), num())
            current = [pos]
            cmd = "L"          # các cặp số sau M là L ngầm định
        elif cmd == "L":
            pos = (num(), num())
            current.append(pos)
        elif cmd == "A":
            rx, ry, phi, large, sweep, x, y = (num() for _ in range(7))
            current += arc_points(*pos, rx, ry, phi, int(large), int(sweep), x, y)
            pos = (x, y)
        elif cmd == "Q":
            cx, cy, x, y = num(), num(), num(), num()
            for k in range(1, 17):
                t = k / 16
                current.append(((1 - t) ** 2 * pos[0] + 2 * (1 - t) * t * cx + t * t * x,
                                (1 - t) ** 2 * pos[1] + 2 * (1 - t) * t * cy + t * t * y))
            pos = (x, y)
        elif cmd == "Z":
            if current:
                out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def paint_svg(svg: str, size: int, ink: str, paper: str | None = None, supersample: int = 4) -> Image.Image:
    """Vẽ một SVG một màu của marks.py. Trong mỗi path, các subpath chồng nhau
    được XOR với nhau, đúng như fill-rule evenodd (gân lá là lỗ trên phiến)."""
    big = size * supersample
    scale = big / 100
    coverage = Image.new("1", (big, big), 0)
    for d in re.findall(r' d="([^"]+)"', svg):
        path_mask = Image.new("1", (big, big), 0)
        for poly in subpaths(d):
            layer = Image.new("1", (big, big), 0)
            ImageDraw.Draw(layer).polygon([(x * scale, y * scale) for x, y in poly], fill=1)
            path_mask = ImageChops.logical_xor(path_mask, layer)
        coverage = ImageChops.logical_or(coverage, path_mask)

    alpha = coverage.convert("L").resize((size, size), Image.LANCZOS)
    ink_layer = Image.new("RGBA", (size, size), ink)
    ink_layer.putalpha(alpha)
    if paper is None:
        return ink_layer
    base = Image.new("RGBA", (size, size), paper)
    return Image.alpha_composite(base, ink_layer)


# ── Các file xuất ra ─────────────────────────────────────────────────────────
def apple_touch_icon() -> None:
    size, pad = 180, 22
    icon = Image.new("RGBA", (size, size), SHOJI)
    kamon = paint_svg(marks.kamon(veins=False, gap=1.8), size - 2 * pad, SUMI)
    icon.alpha_composite(kamon, (pad, pad))
    icon.convert("RGB").save(ROOT / "static/apple-touch-icon.png", optimize=True)


def favicon_ico() -> None:
    svg = marks.kamon(veins=False, gap=1.4)
    frames = [paint_svg(svg, s, SUMI, supersample=8) for s in (32, 16)]
    frames[0].save(ROOT / "static/favicon.ico", sizes=[(32, 32), (16, 16)], append_images=frames[1:])


def og_image(lang: str) -> None:
    """Ảnh chia sẻ theo đúng lưới của site: kamon ở lề ghi chú 29,3%, chữ ở cột chữ."""
    width, height = 1200, 630
    image = Image.new("RGBA", (width, height), SHOJI)
    draw = ImageDraw.Draw(image)

    margin_x = int(width * 0.293)
    kamon_size = 210
    kamon = paint_svg(marks.kamon(), kamon_size, SUMI)
    image.alpha_composite(kamon, ((margin_x - kamon_size) // 2 + 20, (height - kamon_size) // 2))

    latin = ImageFont.truetype(str(FONT_SRC / "Literata[opsz,wght].ttf"), 96)
    latin.set_variation_by_axes([60, 450])       # opsz, wght
    title_y = height // 2 - 90
    draw.text((margin_x + 40, title_y), "Gen", font=latin, fill=SUMI)

    if lang == "vi":
        body = ImageFont.truetype(str(FONT_SRC / "Literata[opsz,wght].ttf"), 34)
        body.set_variation_by_axes([20, 400])
        lines = ["Ghi chép từ Osaka:", "học tập, đời sống, du lịch,", "suy nghĩ và nhật ký."]
        leading = 50
    else:
        body = ImageFont.truetype(str(FONT_SRC / "ShipporiMincho-Medium.ttf"), 34)
        lines = ["大阪から、", "学びと暮らしと旅の記録。"]
        leading = 58
    for index, line in enumerate(lines):
        draw.text((margin_x + 42, title_y + 140 + index * leading), line, font=body, fill=CHIKUEI)

    # Tên miền là chữ Latin nên luôn dùng Literata, kể cả trên ảnh tiếng Nhật
    domain = ImageFont.truetype(str(FONT_SRC / "Literata[opsz,wght].ttf"), 24)
    domain.set_variation_by_axes([20, 400])
    draw.text((margin_x + 42, height - 78), "nguyenta.com", font=domain, fill=CHIKUEI)
    image.convert("RGB").save(ROOT / f"assets/brand/og-{lang}.png", optimize=True)


def main() -> None:
    missing = [f for f in ("Literata[opsz,wght].ttf", "ShipporiMincho-Medium.ttf") if not (FONT_SRC / f).exists()]
    if missing:
        sys.exit(f"Thiếu font gốc {missing}. Chạy trước: python3 tools/fonts/get-sources.py")
    (ROOT / "static").mkdir(exist_ok=True)
    apple_touch_icon()
    favicon_ico()
    og_image("vi")
    og_image("ja")
    for name in ("static/apple-touch-icon.png", "static/favicon.ico", "assets/brand/og-vi.png", "assets/brand/og-ja.png"):
        print(f"  {name:<30} {(ROOT / name).stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
