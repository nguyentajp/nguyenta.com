#!/usr/bin/env python3
"""Dựng các dấu hiệu nhận diện của Gen thành SVG một màu.

    python3 tools/brand/marks.py            # ghi vào assets/brand/

Ba thứ được sinh ra:

  kamon.svg   竹輪に三つ銀杏 — ba lá bạch quả trong vòng tre ba đốt.
              Vòng tre là thân rễ chạy ngầm; ba lá mọc từ một điểm ở tâm.
  hanko.svg   落款印 chữ 元 theo lối 古印体, đóng ở cuối mỗi bài.
  favicon.svg Bản kamon giản lược cho cỡ 16–32px: bỏ gân lá và khe đốt.

Hình dựng bằng cung tròn và đường Bézier, không lấy mẫu từng điểm, nên file chỉ
khoảng 2 KB và nét vẫn trơn ở mọi cỡ. Toạ độ tính trong hệ 100×100, tâm (50,50).

Ensō của trang 静 là ảnh raster, dựng riêng bằng tools/brand/enso.py.
"""
from __future__ import annotations

import math
import pathlib

C = 50.0
OUT = pathlib.Path(__file__).resolve().parents[2] / "assets/brand"


def p(x: float, y: float) -> str:
    """Toạ độ rút gọn: bỏ số 0 vô nghĩa để path ngắn nhất có thể."""
    return f"{x:.1f}".rstrip("0").rstrip(".") + " " + f"{y:.1f}".rstrip("0").rstrip(".")


def polar(angle_deg: float, radius: float) -> tuple[float, float]:
    a = math.radians(angle_deg)
    return C + radius * math.cos(a), C + radius * math.sin(a)


# ── Vòng tre 竹輪 ─────────────────────────────────────────────────────────────
def arc_band(start: float, end: float, r_out: float, r_in: float) -> str:
    """Một dải cung tròn, từ góc start tới góc end, dày r_out − r_in."""
    big = 1 if end - start > 180 else 0
    return (
        f"M{p(*polar(start, r_out))}"
        f"A{r_out} {r_out} 0 {big} 1 {p(*polar(end, r_out))}"
        f"L{p(*polar(end, r_in))}"
        f"A{r_in} {r_in} 0 {big} 0 {p(*polar(start, r_in))}Z"
    )


def bamboo_ring(nodes=(-30, 90, 210), r_out: float = 47.2, r_in: float = 42.8,
                node_span: float = 3.0, node_out: float = 49.5, node_in: float = 40.6,
                slit: float = 0.9, plain_gap: float | None = None) -> str:
    """Vòng tre ba đốt: ba đoạn thân, mỗi chỗ nối là một vành đốt phình ra.

    Vành đốt (節) chính là thứ làm người xem nhận ra đây là tre. Bản đầu chỉ có
    ba cung tròn cách nhau bằng khe trống; hồi đó vòng mang màu tre khô nên màu
    gánh phần "tre". Khi vòng đổi sang màu mực thì chỉ còn lại một vòng tròn
    đứt nét, nên phải đưa cái đốt vào hình.

    node_out là chỗ rộng nhất nên nó quyết định cỡ vòng: phải ≤ 49,5 vì khung
    là 100×100, tâm (50,50), chừa nửa đơn vị cho nét khỏi chạm mép.

    plain_gap: bỏ vành đốt, quay lại ba cung cách nhau bằng khe. Dùng cho
    favicon, vì ở cỡ 16px vành đốt mảnh hơn một pixel, vẽ ra chỉ thành vệt bẩn.
    """
    ns = sorted(nodes)
    parts = []
    for index, node in enumerate(ns):
        nxt = ns[index + 1] if index + 1 < len(ns) else ns[0] + 360
        if plain_gap is not None:
            half = plain_gap / 2
            parts.append(arc_band(node + half, nxt - half, r_out, r_in))
            continue
        # vành đốt, rồi đoạn thân tới sát vành đốt kế tiếp
        parts.append(arc_band(node - node_span, node + node_span, node_out, node_in))
        parts.append(arc_band(node + node_span + slit, nxt - node_span - slit, r_out, r_in))
    return "".join(parts)


# ── Lá bạch quả 銀杏 ──────────────────────────────────────────────────────────
def ginkgo_leaf(angle: float, apex: float = 7.0, radius: float = 34.6, spread: float = 46.0,
                notch: float = 0.18, stalk: float = 1.2, veins: bool = True) -> str:
    """Một lá bạch quả hướng ra ngoài: cuống mảnh, phiến xoè, khấc ở giữa mép ngoài.

    Mép ngoài là hai cung tròn gặp nhau ở khấc; hai bên phiến là đường Bézier
    bậc hai lõm vào, thuôn dần về cuống như lá thật.
    """
    rad = math.radians(angle)
    axis = (math.cos(rad), math.sin(rad))
    perp = (-axis[1], axis[0])

    def at(along: float, across: float) -> tuple[float, float]:
        return (C + axis[0] * along + perp[0] * across, C + axis[1] * along + perp[1] * across)

    def blade(deg: float, scale: float = 1.0) -> tuple[float, float]:
        a = math.radians(deg)
        return at(apex + radius * scale * math.cos(a), radius * scale * math.sin(a))

    # Mép ngoài: hai cung cùng bán kính, cùng tâm ở cuống, gặp nhau tại khấc chữ V.
    notch_half = 7.0
    tip_right = blade(spread)
    tip_left = blade(-spread)
    shoulder_right = blade(notch_half)
    shoulder_left = blade(-notch_half)
    notch_point = at(apex + radius * (1 - notch), 0)
    control_right = at(apex + radius * 0.42, radius * math.sin(math.radians(spread)) * 0.30)
    control_left = at(apex + radius * 0.42, -radius * math.sin(math.radians(spread)) * 0.30)

    path = (
        f"M{p(*at(0, stalk))}"
        f"L{p(*at(apex, stalk))}"                                       # cuống, cạnh phải
        f"Q{p(*control_right)} {p(*tip_right)}"                         # mép phải lõm vào
        f"A{radius} {radius} 0 0 0 {p(*shoulder_right)}"                # cung ngoài, nửa phải
        f"L{p(*notch_point)}"                                           # vào khấc
        f"L{p(*shoulder_left)}"                                         # ra khỏi khấc
        f"A{radius} {radius} 0 0 0 {p(*tip_left)}"                      # cung ngoài, nửa trái
        f"Q{p(*control_left)} {p(*at(apex, -stalk))}"                   # mép trái lõm vào
        f"L{p(*at(0, -stalk))}Z"                                        # cuống, cạnh trái
    )
    if not veins:
        return path

    # Gân lá: nét trắng mảnh toả từ cuống ra mép, làm lỗ bằng fill-rule evenodd.
    for deg in (-31, -17, -6, 6, 17, 31):
        a = math.radians(deg)
        inner = at(apex + 10 * math.cos(a), 10 * math.sin(a))
        outer = at(apex + radius * 0.86 * math.cos(a), radius * 0.86 * math.sin(a))
        nx, ny = outer[0] - inner[0], outer[1] - inner[1]
        length = math.hypot(nx, ny)
        wx, wy = -ny / length * 0.34, nx / length * 0.34
        path += (
            f"M{p(inner[0] + wx * 0.3, inner[1] + wy * 0.3)}"
            f"L{p(outer[0] + wx, outer[1] + wy)}"
            f"L{p(outer[0] - wx, outer[1] - wy)}"
            f"L{p(inner[0] - wx * 0.3, inner[1] - wy * 0.3)}Z"
        )
    return path


def kamon(veins: bool = True, plain_gap: float | None = None, animated: bool = False) -> str:
    """Kamon dạng nhiều path: vòng tre và ba lá tách riêng.

    Bản animated dùng cho trang chủ: vòng tre hiện dần nhờ mask là một đường
    tròn nét liền có stroke-dasharray, ba lá lớn dần từ tâm ra.
    """
    ring = f'<path class="ring" fill-rule="evenodd" d="{bamboo_ring(plain_gap=plain_gap)}"/>'
    leaves = "".join(
        f'<path class="leaf" style="--delay:{0.75 + index * 0.16:.2f}s" fill-rule="evenodd" '
        f'd="{ginkgo_leaf(angle, veins=veins)}"/>'
        for index, angle in enumerate((-90, 30, 150))
    )
    if not animated:
        return svg(ring + leaves, "Kamon của Gen")

    mask = (
        '<defs><mask id="gen-ring-draw" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
        '<circle class="ring-mask" cx="50" cy="50" r="45" fill="none" stroke="#fff" stroke-width="11" '
        'pathLength="1" transform="rotate(-90 50 50)"/></mask></defs>'
    )
    return svg(mask + f'<g mask="url(#gen-ring-draw)">{ring}</g>' + leaves, "Kamon của Gen", "kamon-draw")


# ── Con dấu 落款印 chữ 元, lối 古印体 ─────────────────────────────────────────
def brush(points: list[tuple[float, float]], widths: list[float]) -> str:
    """Nét bút lông: đầu nét đậm, cuối nét thu nhỏ, hai đầu tròn."""
    left, right = [], []
    for index, (x, y) in enumerate(points):
        x0, y0 = points[max(index - 1, 0)]
        x1, y1 = points[min(index + 1, len(points) - 1)]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length * widths[index], dx / length * widths[index]
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))

    path = "M" + p(*left[0]) + "".join("L" + p(*q) for q in left[1:])
    path += f"A{widths[-1]} {widths[-1]} 0 0 1 {p(*right[-1])}"
    path += "".join("L" + p(*q) for q in reversed(right[:-1]))
    path += f"A{widths[0]} {widths[0]} 0 0 1 {p(*left[0])}Z"
    return path


def taper(count: int, *stops: tuple[float, float]) -> list[float]:
    out = []
    for index in range(count):
        t = index / max(count - 1, 1)
        for (t0, w0), (t1, w1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                out.append(w0 + (w1 - w0) * ((t - t0) / (t1 - t0 or 1)))
                break
        else:
            out.append(stops[-1][1])
    return out


def sample_quad(a, control, b, steps: int = 6):
    return [
        ((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * control[0] + t * t * b[0],
         (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * control[1] + t * t * b[1])
        for t in (i / steps for i in range(steps + 1))
    ]


def rounded_square(x0: float, y0: float, x1: float, y1: float, r: float, clockwise: bool = True) -> str:
    sweep = 1 if clockwise else 0
    if clockwise:
        corners = [
            (f"M{p(x0 + r, y0)}", f"L{p(x1 - r, y0)}", f"A{r} {r} 0 0 {sweep} {p(x1, y0 + r)}"),
            ("", f"L{p(x1, y1 - r)}", f"A{r} {r} 0 0 {sweep} {p(x1 - r, y1)}"),
            ("", f"L{p(x0 + r, y1)}", f"A{r} {r} 0 0 {sweep} {p(x0, y1 - r)}"),
            ("", f"L{p(x0, y0 + r)}", f"A{r} {r} 0 0 {sweep} {p(x0 + r, y0)}"),
        ]
    else:
        corners = [
            (f"M{p(x0 + r, y0)}", f"A{r} {r} 0 0 {sweep} {p(x0, y0 + r)}", f"L{p(x0, y1 - r)}"),
            ("", f"A{r} {r} 0 0 {sweep} {p(x0 + r, y1)}", f"L{p(x1 - r, y1)}"),
            ("", f"A{r} {r} 0 0 {sweep} {p(x1, y1 - r)}", f"L{p(x1, y0 + r)}"),
            ("", f"A{r} {r} 0 0 {sweep} {p(x1 - r, y0)}", f"L{p(x0 + r, y0)}"),
        ]
    return "".join("".join(part) for part in corners) + "Z"


def hanko() -> str:
    """Dấu vuông 朱文: viền bo góc nhẹ, chữ 元 nét bút lông bốn nét."""
    frame = rounded_square(3.4, 3.4, 96.6, 96.6, 8.5) + rounded_square(9.8, 9.8, 90.2, 90.2, 3.8, clockwise=False)

    scale = 0.9
    def T(point):
        return (50 + (point[0] - 50) * scale, 53 + (point[1] - 53) * scale)

    def line(a, b, steps: int = 4):
        return [(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps) for i in range(steps + 1)]

    def join(*runs):
        points: list[tuple[float, float]] = []
        for run in runs:
            points += run if not points else run[1:]
        return [T(q) for q in points]

    strokes = []
    # 一 nét ngang ngắn phía trên
    s1 = join(sample_quad((31.5, 25.5), (50, 23.4), (68.5, 23.6)))
    strokes.append(brush(s1, taper(len(s1), (0, 4.9), (0.16, 3.6), (0.85, 3.3), (1, 3.6))))
    # 二 nét ngang dài
    s2 = join(sample_quad((15.5, 44.8), (50, 41.8), (84.5, 42.0), 8))
    strokes.append(brush(s2, taper(len(s2), (0, 4.9), (0.12, 3.7), (0.88, 3.4), (1, 3.8))))
    # 儿 nét phẩy bên trái
    s3 = join(line((40.6, 45.5), (40.3, 59)), sample_quad((40.3, 59), (40.1, 74), (18.5, 85), 8))
    strokes.append(brush(s3, taper(len(s3), (0, 5.0), (0.25, 3.9), (0.7, 3.3), (1, 2.3))))
    # 儿 nét móc bên phải
    s4 = join(
        line((59.4, 45.5), (59.4, 75)),
        sample_quad((59.4, 75), (59.4, 84), (67, 84)),
        line((67, 84), (75.5, 84), 2),
        sample_quad((75.5, 84), (84.2, 84.6), (84.6, 76.5), 6),
    )
    strokes.append(brush(s4, taper(len(s4), (0, 4.8), (0.4, 3.7), (0.6, 3.9), (0.8, 3.5), (1, 2.4))))

    return svg(
        f'<path fill-rule="evenodd" d="{frame}"/>' + "".join(f'<path d="{d}"/>' for d in strokes),
        "Dấu 元 của Gen",
    )


def svg(body: str, label: str, classes: str = "") -> str:
    attr = f' class="{classes}"' if classes else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"{attr} role="img" '
        f'aria-label="{label}"><g fill="currentColor">{body}</g></svg>'
    )


# Màu của kamon (vòng, lá): vòng màu mực 墨 như con dấu đóng lên giấy, lá xanh
# đậm 常磐. Hai màu tách vòng và lá ra khỏi nhau, để ba lá trong vòng tròn
# không giống biểu tượng phóng xạ. Trên site, màu do CSS tô (main.css:
# --kamon-ring, --kamon-leaf); favicon không đọc được CSS của trang nên mang
# màu sẵn, kèm bản cho thanh tab tối — ở đó giấy tối nên nét mực sáng lên.
KAMON_COLORS = {"light": ("#22251f", "#2e5538"), "dark": ("#daddd3", "#8fbf95")}


def favicon() -> str:
    """Cỡ favicon: gân lá và vành đốt nhỏ hơn một pixel nên bỏ đi cho nét sạch."""
    (ring_l, leaf_l), (ring_d, leaf_d) = KAMON_COLORS["light"], KAMON_COLORS["dark"]
    style = (
        f"<style>.ring{{fill:{ring_l}}}.leaf{{fill:{leaf_l}}}"
        f"@media (prefers-color-scheme:dark){{.ring{{fill:{ring_d}}}.leaf{{fill:{leaf_d}}}}}</style>"
    )
    return kamon(veins=False, plain_gap=1.4).replace("<g ", style + "<g ", 1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "kamon.svg": kamon(),
        "kamon-draw.svg": kamon(animated=True),
        "favicon.svg": favicon(),
        "hanko.svg": hanko(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content + "\n", encoding="utf-8")
        print(f"  {name:<14} {len(content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
