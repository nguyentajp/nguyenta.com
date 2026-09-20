#!/usr/bin/env python3
"""Logo ngang của Gen (combination mark): dấu hiệu bên trái, chữ ký bên phải.

    python3 tools/brand/logo.py            # ghi vào assets/brand/

Dấu hiệu là kamon đổi vòng: vòng tre 竹輪 nhường chỗ cho ensō 円相 — cùng vòng
tròn một nét của trang 凪. Ba lá bạch quả giữ nguyên hình, chỉ thu nhỏ lại, vì
nét ensō dày hơn vòng tre nhiều: bề ngang nét bằng khoảng một phần sáu bán
kính, để trông ra cọ lông chứ không thành cái nhẫn.

Ensō ở trang 凪 là ảnh raster (tools/brand/enso.py) mô phỏng từng sợi lông, có
vệt khô 掠れ. Ở đây phải dựng lại bằng vector: logo cần một màu và phải đọc
được ở cỡ nhỏ. Chiều quay và công thức méo bán kính giữ nguyên của bản cũ, nên
hai hình vẫn là một. Chỉ khe hở phải mở rộng hơn: bản raster có vệt khô làm
đuôi nét nhạt dần nên đầu và đuôi gần nhau vẫn không đụng; nét vector đặc kín,
để hẹp như cũ thì hai đầu chồm lên nhau thành cái mỏ chim.

Chữ ký có ba phương án, chưa chốt cái nào (README mục 11.7):

  logo-kanji.svg  元 — chữ trong tên 英元, cũng là chữ trên con dấu cuối bài.
  logo-kana.svg   ゲン — đọc tên theo lối katakana.
  logo-latin.svg  Gen — đúng cái tên đang hiện ở đầu trang, viết bằng cọ.

Cả ba đều vẽ tay bằng nét bút lông dựng từ điểm, không mượn font nào.
"""
from __future__ import annotations

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from marks import C, OUT, brush, ginkgo_leaf, p, sample_quad  # noqa: E402

# Ensō: lấy chiều quay và độ méo của tools/brand/enso.py, nhưng xoay điểm bắt
# đầu để khe hở rơi vào khoảng trống giữa lá trên và lá dưới-trái (ba lá hướng
# -90°, 30°, 150° nên ba khoảng trống ở 210°, 330°, 90°). Để khe ở chỗ cũ thì
# nó nằm ngay sau một cái lá, nhìn ra thành lá lọt qua chỗ vòng bị đứt.
ENSO_START, ENSO_SWEEP = 229.0, 322.0
ENSO_R = 40.0
LEAF_SCALE = 0.78          # lá thu nhỏ để lọt vào trong nét ensō dày


# ── Dấu hiệu: ensō + ba lá ──────────────────────────────────────────────────
def enso(steps: int = 72) -> str:
    """Một nét cọ quay theo chiều kim đồng hồ, hở một quãng bên trái.

    Bề ngang nét kể lại một lần đưa tay: cọ hạ dần chứ không ấn hết lực ngay
    (land), nặng nhất một quãng ngắn sau đó (press), rồi mỏng dần đều, và hai
    mươi phần trăm cuối thu về gần thành mũi nhọn lúc nhấc tay (lift). Hai bướu
    sin nhỏ là chỗ lực tay không bao giờ đều tuyệt đối.

    Chỗ land này là cái phải sửa mấy lần: cho cọ nặng ngay từ điểm đầu thì đầu
    nét thành một cục tròn bán kính bằng nửa bề ngang, chìa vào giữa vòng
    trông như cái vuốt chim. Bản raster không bị vì ở đó đầu nét là vệt mực
    loang, không phải hình tròn đặc.
    """
    points, widths = [], []
    for index in range(steps + 1):
        t = index / steps
        theta = math.radians(ENSO_START + ENSO_SWEEP * t)
        radius = ENSO_R * (1 + 0.0045 * math.sin(2 * theta + 0.6) + 0.003 * math.sin(3 * theta + 1.9))
        points.append((C + radius * math.cos(theta), C + radius * math.sin(theta)))

        press = 0.90 * math.exp(-((t - 0.18) / 0.11) ** 2)
        swell = 0.18 * math.sin(t * 7.3 + 0.4) + 0.12 * math.sin(t * 17.0 + 2.1)
        # brush() bịt hai đầu nét bằng nửa đường tròn bán kính bằng nửa bề
        # ngang, và cái cung ấy cong vào trong nét chứ không cong ra: để đầu
        # nét còn dày thì chóp nét bị khoét một vết khía chữ V, còn dày nữa
        # thì thành một cục tròn chìa ra như vuốt chim. Cách chữa rẻ nhất là
        # vào nét và kết nét từ gần như số không, để cái nắp nhỏ hơn một điểm
        # ảnh ở mọi cỡ. Cũng đúng với tay thật: vòng ensō quệt lấy đà mà vào,
        # rồi nhấc tay lên dần chứ không dừng phắt.
        k = min(t / 0.07, 1.0)
        land = 0.05 + 0.95 * k * k * (3 - 2 * k)
        j = min((1 - t) / 0.24, 1.0)
        lift = 0.05 + 0.95 * j * j * (3 - 2 * j)
        widths.append((5.3 - 1.1 * t + press + swell) * land * lift)

    return brush(points, widths)


def mark() -> str:
    ring = f'<path class="ring" d="{enso()}"/>'
    leaves = "".join(
        f'<path class="leaf" fill-rule="evenodd" '
        f'd="{ginkgo_leaf(angle, apex=7.0 * LEAF_SCALE, radius=34.6 * LEAF_SCALE, stalk=1.2 * LEAF_SCALE)}"/>'
        for angle in (-90, 30, 150)
    )
    return ring + leaves


# ── Dựng nét ────────────────────────────────────────────────────────────────
def line(a, b, steps: int = 4):
    return [(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps) for i in range(steps + 1)]


def arc(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, steps: int = 10):
    return [
        (cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
         cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
        for i in range(steps + 1)
    ]


def join(*runs):
    points: list[tuple[float, float]] = []
    for run in runs:
        points += run if not points else run[1:]
    return points


def taper(count: int, *stops: tuple[float, float]) -> list[float]:
    """Như marks.taper nhưng nội suy trơn hai đầu, để nét không gãy góc."""
    out = []
    for index in range(count):
        t = index / max(count - 1, 1)
        for (t0, w0), (t1, w1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0 or 1)
                out.append(w0 + (w1 - w0) * (k * k * (3 - 2 * k)))
                break
        else:
            out.append(stops[-1][1])
    return out


def placed(strokes: list[tuple[list, list]], box: tuple[float, float, float, float]) -> str:
    """Đặt một chữ (vẽ trong hệ 0–100) vào ô cho trước của logo, giữ tỉ lệ."""
    x0, y0, x1, y1 = box
    xs = [x for points, _ in strokes for x, _ in points]
    ys = [y for points, _ in strokes for _, y in points]
    scale = min((x1 - x0) / (max(xs) - min(xs)), (y1 - y0) / (max(ys) - min(ys)))
    dx = x0 + ((x1 - x0) - (max(xs) - min(xs)) * scale) / 2 - min(xs) * scale
    dy = y0 + ((y1 - y0) - (max(ys) - min(ys)) * scale) / 2 - min(ys) * scale
    return "".join(
        f'<path class="word" d="'
        + brush([(x * scale + dx, y * scale + dy) for x, y in points], [w * scale for w in widths])
        + '"/>'
        for points, widths in strokes
    )


# ── Chữ ký 1: 元 ────────────────────────────────────────────────────────────
def kanji_gen() -> list[tuple[list, list]]:
    """元 bốn nét, cùng bộ xương với con dấu cuối bài nhưng nét tương phản hơn.

    Con dấu là 古印体, nét gần như đều nhau vì phải chịu được cỡ nhỏ. Ở logo
    chữ lớn hơn nhiều nên cho phép đầu nét ấn đậm, cuối nét vuốt mỏng.
    """
    strokes = []
    # 一 nét ngang ngắn phía trên
    s = join(sample_quad((31.5, 25.5), (50, 22.8), (68.5, 23.4), 8))
    strokes.append((s, taper(len(s), (0, 5.4), (0.14, 3.4), (0.82, 3.0), (1, 4.2))))
    # 二 nét ngang dài
    s = join(sample_quad((14.0, 45.6), (50, 41.4), (86.0, 42.0), 10))
    strokes.append((s, taper(len(s), (0, 5.6), (0.10, 3.6), (0.86, 3.1), (1, 4.6))))
    # 儿 nét phẩy bên trái, vuốt nhọn dần
    s = join(line((40.6, 45.5), (40.2, 58)), sample_quad((40.2, 58), (39.8, 75), (16.0, 87), 10))
    strokes.append((s, taper(len(s), (0, 5.6), (0.22, 4.1), (0.68, 3.2), (1, 1.5))))
    # 儿 nét móc bên phải, hất lên ở cuối
    s = join(
        line((59.6, 45.5), (59.6, 76)),
        sample_quad((59.6, 76), (59.6, 86), (68.0, 86)),
        line((68.0, 86), (76.0, 86), 2),
        sample_quad((76.0, 86), (85.8, 86.6), (86.4, 76.0), 8),
    )
    strokes.append((s, taper(len(s), (0, 5.4), (0.38, 3.9), (0.62, 4.2), (0.84, 3.4), (1, 1.6))))
    return strokes


# ── Chữ ký 2: ゲン ──────────────────────────────────────────────────────────
def kana_gen() -> list[tuple[list, list]]:
    """ゲン: ケ ba nét, dấu đục hai nét, ン hai nét.

    ケ dễ vẽ nhầm thành カ. Khác nhau ở chỗ ケ chỉ có MỘT nét đổ dài: nét ngang
    nằm riêng, nét phẩy dài bắt đầu từ trên cao rồi cắt qua nét ngang mà đổ
    xuống trái. Vẽ nét ngang gập xuống rồi thêm một phẩy nữa là ra カ.
    """
    strokes = []
    # ケ nét 1: phẩy ngắn trên trái
    s = join(sample_quad((27.0, 11.0), (20.0, 19.0), (12.0, 29.0), 6))
    strokes.append((s, taper(len(s), (0, 4.4), (0.5, 3.2), (1, 1.5))))
    # ケ nét 2: nét ngang, nằm riêng một mình
    s = join(line((8.0, 30.0), (47.0, 26.5), 5))
    strokes.append((s, taper(len(s), (0, 4.8), (0.18, 3.4), (0.85, 3.2), (1, 4.0))))
    # ケ nét 3: phẩy dài, xuất phát trên nét ngang rồi cắt qua nó đổ xuống trái
    s = join(sample_quad((42.0, 17.0), (38.0, 43.0), (16.0, 63.0), 10))
    strokes.append((s, taper(len(s), (0, 5.0), (0.35, 3.8), (0.75, 3.2), (1, 1.4))))
    # Dấu đục 濁点: hai vạch ngắn trên phải
    for offset in (0.0, 9.5):
        s = join(line((58.0 + offset, 9.0), (53.0 + offset, 18.0), 3))
        strokes.append((s, taper(len(s), (0, 3.4), (1, 1.5))))
    # ン nét 1: chấm ngắn trên trái
    s = join(line((72.0, 28.0), (81.0, 33.0), 3))
    strokes.append((s, taper(len(s), (0, 4.0), (1, 1.7))))
    # ン nét 2: nét dài hất từ dưới trái lên phải
    s = join(sample_quad((71.0, 45.0), (88.0, 57.0), (105.0, 37.0), 10))
    strokes.append((s, taper(len(s), (0, 2.8), (0.3, 4.4), (0.72, 3.8), (1, 1.3))))
    return strokes


# ── Chữ ký 3: Gen ───────────────────────────────────────────────────────────
def latin_gen() -> list[tuple[list, list]]:
    """Gen viết bằng cọ: G một nét vòng rồi gạt ngang, e một nét, n hai nét."""
    strokes = []
    # G: một vòng mở bên phải — từ 1 giờ vòng ngược chiều kim đồng hồ qua đỉnh,
    # sang trái, xuống đáy, tới 5 giờ; rồi vuốt lên và gạt ngang vào trong.
    s = join(
        arc(25.0, 38.0, 19.0, 21.0, -28, -300, 20),
        line((34.3, 56.2), (42.5, 47.0), 2),
        line((42.5, 47.0), (42.0, 41.5), 2),
        line((42.0, 41.5), (28.0, 40.0), 3),
    )
    strokes.append((s, taper(len(s), (0, 3.0), (0.10, 4.6), (0.58, 4.0), (0.88, 3.0), (1, 1.4))))
    # e: vạch ngang rồi vòng kín
    s = join(
        line((54.0, 41.0), (72.0, 38.5), 3),
        arc(63.0, 44.0, 10.0, 9.5, -30, -180, 7),
        arc(63.0, 44.0, 10.0, 9.5, 180, 55, 8),
    )
    strokes.append((s, taper(len(s), (0, 2.6), (0.18, 4.0), (0.72, 3.4), (1, 1.4))))
    # n: thân đứng
    s = join(line((84.0, 34.0), (83.0, 53.5), 4))
    strokes.append((s, taper(len(s), (0, 4.2), (1, 2.6))))
    # n: vai vòng sang phải rồi đổ xuống
    s = join(
        sample_quad((83.4, 40.0), (87.0, 33.5), (94.0, 35.0), 5),
        sample_quad((94.0, 35.0), (99.5, 36.5), (99.0, 53.5), 6),
    )
    strokes.append((s, taper(len(s), (0, 3.0), (0.3, 4.0), (1, 2.6))))
    return strokes


# ── Ghép ────────────────────────────────────────────────────────────────────
GAP = 16.0            # khoảng hở giữa dấu hiệu và chữ ký
WORD_W, WORD_H = 122.0, 56.0


def lockup(strokes: list[tuple[list, list]], label: str) -> str:
    width = 100 + GAP + WORD_W
    body = mark() + placed(strokes, (100 + GAP, 50 - WORD_H / 2, 100 + GAP + WORD_W, 50 + WORD_H / 2))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} 100" role="img" '
        f'aria-label="{label}"><g fill="currentColor">{body}</g></svg>'
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "kamon-enso.svg": (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" '
            f'aria-label="Kamon của Gen trong vòng ensō"><g fill="currentColor">{mark()}</g></svg>'
        ),
        "logo-kanji.svg": lockup(kanji_gen(), "Gen — 元"),
        "logo-kana.svg": lockup(kana_gen(), "Gen — ゲン"),
        "logo-latin.svg": lockup(latin_gen(), "Gen"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content + "\n", encoding="utf-8")
        print(f"  {name:<18} {len(content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
