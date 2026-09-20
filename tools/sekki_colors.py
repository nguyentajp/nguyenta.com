#!/usr/bin/env python3
"""Sinh và kiểm bộ màu nhấn của 24 tiết khí.

Mỗi tiết khí có một màu nhấn, tên theo dấu mốc của mùa (hoa mai, lá non, lá
đỏ…). Màu đi một vòng bánh xe màu trong năm, nên người đọc quay lại sau vài
tuần thấy site đã ngả sang màu khác mà không thấy màu nào lạc ra ngoài.

Cách làm: giữ ĐỘ SÁNG cố định trong không gian OKLCh — bằng đúng độ sáng của
màu 銀杏 đang dùng (L 0,45 cho giao diện sáng; 0,81 cho giao diện tối) — rồi
chỉ đổi sắc và độ tươi. Vì thế hai mươi bốn màu cùng một sức nặng thị giác,
không màu nào nhảy ra trước, và màu nào cũng trầm như bảng màu washi của site.
Độ tươi giữ trong khoảng 0,04–0,10 (màu 銀杏 là 0,086); màu nào ra ngoài gamut
sRGB thì hạ độ tươi tới khi vào. Cuối cùng kiểm tương phản với nền: phải đạt
4,5 : 1 theo WCAG AA — với nền chính lẫn dải 白緑 của chân trang. Thực tế
cách làm này cho 5,4 : 1 trở lên, ngang màu 銀杏 vẫn dùng lâu nay.

    ./.venv/bin/python tools/sekki_colors.py          # bảng kiểm
    ./.venv/bin/python tools/sekki_colors.py --toml   # in ra để dán vào data/sekki.toml
"""

import argparse
import math

BG_LIGHT = "#f6f7f2"   # 障子
BG_DARK = "#171915"
# Chân trang và khung Ủng hộ nằm trên dải 白緑, không phải nền chính. Màu nhấn
# làm chữ ở đó (link rê chuột) nên phải đạt ngưỡng trên CẢ HAI nền.
BAND_LIGHT = "#dce3d6"
BAND_DARK = "#222720"
L_LIGHT = 0.45         # theo 銀杏 #6b4f0d
L_DARK = 0.81          # theo #e3c05e
FLOOR = 4.5            # WCAG AA cho chữ thường

# order: thứ tự trong năm (khớp data/sekki.toml). hue: OKLCh, độ. chroma: OKLCh.
SEKKI = [
    (1,  "立春", "Lập xuân",    "梅 hoa mai",           355, 0.085),
    (2,  "雨水", "Vũ thủy",     "霞 sương mù",          250, 0.045),
    (3,  "啓蟄", "Kinh trập",   "桃 hoa đào",            15, 0.085),
    (4,  "春分", "Xuân phân",   "桜 hoa anh đào",       340, 0.080),
    (5,  "清明", "Thanh minh",  "若葉 lá non",          130, 0.095),
    (6,  "穀雨", "Cốc vũ",      "牡丹 hoa mẫu đơn",     350, 0.095),
    (7,  "立夏", "Lập hạ",      "新竹 tre mới",         150, 0.090),
    (8,  "小満", "Tiểu mãn",    "紅花 hoa rum",          40, 0.100),
    (9,  "芒種", "Mang chủng",  "青梅 mai xanh",        115, 0.090),
    (10, "夏至", "Hạ chí",      "菖蒲 hoa diên vĩ",     295, 0.090),
    (11, "小暑", "Tiểu thử",    "蓮 hoa sen",           335, 0.085),
    (12, "大暑", "Đại thử",     "雷雨 mưa dông",        240, 0.085),
    (13, "立秋", "Lập thu",     "涼風 gió mát",         205, 0.075),
    (14, "処暑", "Xử thử",      "稲 lúa chín",           90, 0.090),
    (15, "白露", "Bạch lộ",     "露草 hoa thài lài",    265, 0.090),
    (16, "秋分", "Thu phân",    "萩 hoa thưu",          320, 0.085),
    (17, "寒露", "Hàn lộ",      "菊 hoa cúc",            80, 0.095),
    (18, "霜降", "Sương giáng", "紅葉 lá đỏ",            35, 0.100),
    (19, "立冬", "Lập đông",    "椿 hoa trà",            20, 0.095),
    (20, "小雪", "Tiểu tuyết",  "枯野 đồng cỏ khô",      60, 0.055),
    (21, "大雪", "Đại tuyết",   "雪 tuyết",             220, 0.040),
    (22, "冬至", "Đông chí",    "柚子 quả yuzu",         95, 0.095),
    (23, "小寒", "Tiểu hàn",    "芹 rau cần",           145, 0.085),
    (24, "大寒", "Đại hàn",     "蕗の薹 ngồng fuki",  110, 0.085),
]


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def oklch_to_rgb(L, C, h_deg):
    """OKLCh → sRGB, mỗi kênh 0..1. Trả kèm cờ cho biết màu có trong gamut."""
    h = math.radians(h_deg)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    inside = all(-1e-4 <= v <= 1 + 1e-4 for v in (r, g, bl))
    # Ba con số trên là ánh sáng thật (linear); màn hình nhận sRGB nên phải qua
    # gamma. Thiếu bước này thì màu nào cũng ra gần như đen.
    return [min(max(linear_to_srgb(v), 0.0), 1.0) for v in (r, g, bl)], inside


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)


def from_hex(s):
    s = s.lstrip("#")
    return [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def luminance(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb_a, rgb_b):
    la, lb = luminance(rgb_a), luminance(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def pick(L, chroma, hue, bg_hex):
    """Màu ở độ sáng L, hạ độ tươi tới khi vào gamut sRGB. Trả (hex, tương phản)."""
    C = chroma
    while C > 0:
        rgb, inside = oklch_to_rgb(L, C, hue)
        if inside:
            break
        C -= 0.002
    rgb, _ = oklch_to_rgb(L, C, hue)
    return to_hex(rgb), contrast(rgb, from_hex(bg_hex))


def build():
    rows = []
    for order, ja, vi, name, hue, chroma in SEKKI:
        light, c_light = pick(L_LIGHT, chroma, hue, BG_LIGHT)
        dark, c_dark = pick(L_DARK, chroma, hue, BG_DARK)
        b_light = contrast(from_hex(light), from_hex(BAND_LIGHT))
        b_dark = contrast(from_hex(dark), from_hex(BAND_DARK))
        rows.append((order, ja, vi, name, light, c_light, dark, c_dark, b_light, b_dark))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--toml", action="store_true", help="in ra dạng dán vào data/sekki.toml")
    args = ap.parse_args()
    rows = build()

    if args.toml:
        for order, ja, vi, name, light, _, dark, _, _, _ in rows:
            print(f'  # {name}')
            print(f'  accent_light = "{light}"')
            print(f'  accent_dark = "{dark}"')
        return

    print(f"{'':2} {'tiết':11} {'màu':23} {'sáng':9} {'nền':6} {'dải':6}"
          f" {'tối':9} {'nền':6} {'dải':6}")
    bad = 0
    for order, ja, vi, name, light, c_light, dark, c_dark, b_light, b_dark in rows:
        oks = [c_light >= FLOOR, b_light >= FLOOR, c_dark >= FLOOR, b_dark >= FLOOR]
        bad += oks.count(False)
        mark = lambda ok: "" if ok else " ✗"
        print(f"{order:2d} {vi:11} {name:23}"
              f" {light} {c_light:5.2f}{mark(oks[0])} {b_light:5.2f}{mark(oks[1])}"
              f" {dark} {c_dark:5.2f}{mark(oks[2])} {b_dark:5.2f}{mark(oks[3])}")
    print(f"\n{len(rows) * 2} màu × 2 nền, ngưỡng {FLOOR} : 1"
          f" — nền chính {BG_LIGHT}/{BG_DARK}, dải 白緑 {BAND_LIGHT}/{BAND_DARK}"
          f" — {'tất cả đều đạt' if bad == 0 else f'{bad} phép đo KHÔNG đạt'}")
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
