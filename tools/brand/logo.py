#!/usr/bin/env python3
"""Chữ "Gen" và logo ngang của Gen.

    ./.venv/bin/python tools/brand/logo.py      # ghi vào assets/brand/

  wordmark.svg  Chữ "Gen", dùng ở đầu trang và chân trang, đứng cạnh kamon.
  logo.svg      Kamon và chữ ghép sẵn thành một hình, cho những chỗ ngoài site
                (ảnh đại diện Facebook, in ấn) — nơi không có CSS của site để
                xếp hai thứ cạnh nhau.

Chữ lấy từ Shippori Mincho B1 SemiBold, chính bộ chữ site đang dùng cho tiêu
đề tiếng Nhật. Chữ Latin của một bộ minh triều Nhật mang đúng cái chất cần: nét
ngang mảnh, chân chữ bẹt và vuông, trục chữ thẳng đứng, chữ G không có gai.
Nhờ vậy logo và site là một bộ, không phải hai giọng khác nhau.

Chữ được cắt thành đường viền chứ không gọi font, vì hai lẽ. Bản Shippori gửi
tới người đọc chỉ chứa kana và chữ Hán (tools/fonts/build.py, scope "ja"), chữ
Latin đã bị cắt bỏ để nhẹ trang; muốn viết "Gen" bằng nó thì phải gửi thêm một
file font nữa cho mọi trang. Và chữ ở đây là hình, không phải chữ đọc được:
cắt thành đường viền thì không bao giờ có cảnh chữ nhảy font lúc trang mới tải.
Chỗ nào cần chữ cho máy đọc màn hình thì đặt chữ ẩn, xem masthead.html.

Font gốc theo giấy phép OFL và không nằm trong repo: chạy
`python3 tools/fonts/get-sources.py` để tải về trước.
"""
from __future__ import annotations

import pathlib
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from marks import bamboo_ring, ginkgo_leaf  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/brand"
FONT = ROOT / "tools/fonts/src/ShipporiMinchoB1-SemiBold.ttf"

WORD = "Gen"
CAP = 100.0        # chiều cao chữ hoa, tính trong hệ toạ độ của chính wordmark
TRACK = 0.012      # giãn chữ, tính theo chiều cao chữ hoa — logo cần thoáng hơn văn bản


def _font() -> TTFont:
    if not FONT.exists():
        sys.exit(f"Thiếu font gốc: {FONT}\nChạy: python3 tools/fonts/get-sources.py")
    return TTFont(FONT)


def wordmark() -> tuple[str, float, float]:
    """Chữ "Gen" thành đường viền. Trả về (path, bề ngang, chiều cao dưới đường chân chữ).

    Gốc toạ độ đặt ở mép trái NÉT MỰC và ở đường chân chữ, không phải ở mép ô
    chữ: khoảng trống hai bên do font quy định là để xếp chữ trong câu, còn ở
    đây phải tự căn bằng mắt cho khớp với kamon.
    """
    font = _font()
    upm = font["head"].unitsPerEm
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    cap_units = font["OS/2"].sCapHeight or upm * 0.7
    scale = CAP / cap_units
    track = TRACK * CAP / scale          # giãn chữ, đổi về đơn vị của font

    commands, pen_x = [], 0.0
    for index, char in enumerate(WORD):
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, 1, pen_x, 0)))
        commands.append(f'<path d="{pen.getCommands()}"/>')
        pen_x += hmtx[name][0] + (track if index + 1 < len(WORD) else 0)

    # Mép trái và mép phải của phần có mực, để cắt bỏ khoảng trống của font
    from fontTools.pens.boundsPen import BoundsPen

    bounds = BoundsPen(glyphs)
    pen_x = 0.0
    for index, char in enumerate(WORD):
        name = cmap[ord(char)]
        glyphs[name].draw(TransformPen(bounds, (1, 0, 0, 1, pen_x, 0)))
        pen_x += hmtx[name][0] + (track if index + 1 < len(WORD) else 0)
    x_min, y_min, x_max, _ = bounds.bounds

    # Lật trục y (font đi lên, SVG đi xuống) và đưa về hệ CAP
    body = "".join(commands)
    transform = f"translate({-x_min * scale:.2f} 0) scale({scale:.5f} {-scale:.5f})"
    return (f'<g transform="{transform}">{body}</g>',
            (x_max - x_min) * scale,
            -y_min * scale)


def kamon() -> str:
    """Kamon 竹輪に三つ銀杏 như đang dùng trên site: vòng tre ba đốt, ba lá bạch quả."""
    ring = f'<path class="ring" fill-rule="evenodd" d="{bamboo_ring()}"/>'
    leaves = "".join(
        f'<path class="leaf" fill-rule="evenodd" d="{ginkgo_leaf(angle)}"/>'
        for angle in (-90, 30, 150)
    )
    return ring + leaves


# Tỉ lệ khi ghép: chữ hoa cao bằng 44% đường kính kamon, và cách kamon một
# quãng bằng 22% đường kính. Hai số này chọn bằng mắt: chữ cao hơn thì át cái
# kamon, thấp hơn thì logo trông như kamon kéo lê một cái nhãn.
LOGO_CAP = 44.0
LOGO_GAP = 22.0


def logo() -> str:
    word, width, below = wordmark()
    scale = LOGO_CAP / CAP
    word_w, word_below = width * scale, below * scale

    # Chữ căn giữa theo khối chữ hoa, không theo đường chân chữ: phần đuôi chữ
    # thò xuống (chữ "e" tròn hơi lẹm) không được kéo lệch cả dòng chữ.
    baseline = 50 + LOGO_CAP / 2
    total = 100 + LOGO_GAP + word_w
    body = (
        kamon()
        + f'<g class="word" transform="translate({100 + LOGO_GAP:.2f} {baseline:.2f}) '
          f'scale({scale:.5f})">{word}</g>'
    )
    _ = word_below
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total:.1f} 100" role="img" '
        f'aria-label="Gen"><g fill="currentColor">{body}</g></svg>'
    )


def wordmark_svg() -> str:
    word, width, below = wordmark()
    height = CAP + below
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
        f'role="img" aria-label="Gen"><g fill="currentColor" '
        f'transform="translate(0 {CAP:.1f})">{word}</g></svg>'
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in {"wordmark.svg": wordmark_svg(), "logo.svg": logo()}.items():
        (OUT / name).write_text(content + "\n", encoding="utf-8")
        print(f"  {name:<14} {len(content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
