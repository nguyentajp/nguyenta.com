#!/usr/bin/env python3
"""Sinh và kiểm bộ màu nhấn của 24 tiết khí.

Mỗi tiết khí một màu nhấn, lấy từ một thứ có thật của tiết đó: hoa đang nở,
đồng đang chín, thời tiết ngoài trời, tục lệ trong nhà.

Luật xếp màu — MÀU PHẢI ĐÚNG MÙA, chứ không phải đi cho đủ một vòng bánh xe màu:

    xuân   hồng hoa (mơ, đào, anh đào, sương giăng), rồi xanh lá non
    hạ     đỏ và các màu nóng: đỏ, cam, vàng chín
    thu    vàng lúa, vàng lá, nâu đất, đỏ sậm
    đông   các màu lạnh: xám tuyết, xanh băng, xanh chàm, tím than

Không có ngoại lệ. Mỗi tiết đứng đúng chỗ màu của vật mang tên nó (tía tô đỏ
tía nhất, quả hồng cam nhất), và tên gọi màu ở data/sekki_notes.yaml dùng tên
màu truyền thống của Nhật (紅梅色, 萌黄, 緋, 柿色, 藍…) mỗi khi có.

Cách làm: giữ ĐỘ SÁNG cố định trong không gian OKLCh — bằng đúng độ sáng của
màu 銀杏 đang dùng (L 0,45 cho giao diện sáng; 0,81 cho giao diện tối) — rồi
chỉ đổi sắc và độ tươi. Vì thế hai mươi bốn màu cùng một sức nặng thị giác,
không màu nào nhảy ra trước, và màu nào cũng trầm như bảng màu washi của site.
Độ tươi ở mức 0,02–0,11: nhóm màu xám (sương, tuyết, cỏ lau) thấp, nhóm màu của
hoa và lá cao; màu nào ra ngoài gamut sRGB thì hạ độ tươi tới khi vào.

Hai phép kiểm, cả hai đều chặn (thoát mã 1):

  1. Tương phản với nền ≥ 4,5 : 1 (WCAG AA), với nền chính lẫn dải 白緑 của
     chân trang, ở cả hai giao diện.
  2. Hai tiết liền kề phải phân biệt được: khoảng cách ΔE (OKLab, ×100) ≥ 3,5
     ở cả hai giao diện. Cùng độ sáng và độ tươi thấp thì các sắc rất dễ trùng
     nhau; bản trước có cặp chỉ cách 1,5, mắt thường coi là một màu.

Các cặp xa nhau trong năm (hoa mơ đầu xuân và hoa bỉ ngạn giữa thu đều đỏ
hồng) vẫn có thể gần nhau; đó là điều luật "đúng mùa" kéo theo.

Cách dùng (chạy từ thư mục gốc repo):

    ./.venv/bin/python tools/sekki_colors.py           # bảng kiểm
    ./.venv/bin/python tools/sekki_colors.py --write   # sinh lại mã màu trong data/sekki.toml
    ./.venv/bin/python tools/sekki_colors.py --check   # như bảng kiểm, không in bảng (CI dùng)

Bảng kiểm cũng báo nếu data/sekki.toml không khớp với bảng SEKKI dưới đây,
tức là có ai đó sửa tay mã màu hoặc sửa bảng mà chưa chạy --write.
"""

import argparse
import math
import re
from pathlib import Path

BG_LIGHT = "#f6f7f2"   # 障子
BG_DARK = "#171915"
# Chân trang và khung Ủng hộ nằm trên dải 白緑, không phải nền chính. Màu nhấn
# làm chữ ở đó (link rê chuột) nên phải đạt ngưỡng trên CẢ HAI nền.
BAND_LIGHT = "#dce3d6"
BAND_DARK = "#222720"
L_LIGHT = 0.45         # theo 銀杏 #6b4f0d
L_DARK = 0.81          # theo #e3c05e
FLOOR = 4.5            # WCAG AA cho chữ thường
STEP = 3.5             # ΔE tối thiểu giữa hai tiết liền kề
TOML = Path(__file__).resolve().parent.parent / "data" / "sekki.toml"

# order: thứ tự trong năm (khớp data/sekki.toml). hue: OKLCh, độ. chroma: OKLCh.
# Cột name chỉ là nhãn cho người đọc bảng; chữ hiện trên site nằm ở
# data/sekki_notes.yaml.
SEKKI = [
    # ── Xuân: hồng hoa, rồi xanh lá ────────────────────────────────────────
    (1,  "立春", "Lập xuân",    "紅梅色 hoa mơ đỏ",       9, 0.090),
    (2,  "雨水", "Vũ thủy",     "霞の藤鼠 sương giăng", 291, 0.026),
    (3,  "啓蟄", "Kinh trập",   "桃色 hoa đào",         340, 0.105),
    (4,  "春分", "Xuân phân",   "桜鼠 hoa anh đào",     342, 0.037),
    (5,  "清明", "Thanh minh",  "萌黄 mầm non",         122, 0.109),
    (6,  "穀雨", "Cốc vũ",      "茶畑の緑 đồi chè",     155, 0.088),
    # ── Hạ: đỏ và các màu nóng ─────────────────────────────────────────────
    (7,  "立夏", "Lập hạ",      "緋鯉 cờ cá chép",       24, 0.104),
    (8,  "小満", "Tiểu mãn",    "麦藁色 lúa mạch chín",  87, 0.070),
    (9,  "芒種", "Mang chủng",  "梅の実 quả mơ chín",    68, 0.098),
    (10, "夏至", "Hạ chí",      "夕焼け ráng chiều",     47, 0.107),
    (11, "小暑", "Tiểu thử",    "赤紫蘇 tía tô đỏ",     350, 0.103),
    (12, "大暑", "Đại thử",     "炎天の朱 trời lửa",     36, 0.091),
    # ── Thu: vàng lúa, vàng lá, nâu đất, đỏ sậm ────────────────────────────
    (13, "立秋", "Lập thu",     "灯籠の飴色 đèn hoa đăng", 70, 0.079),
    (14, "処暑", "Xử thử",      "稲穂 lúa ngả màu",     111, 0.079),
    (15, "白露", "Bạch lộ",     "芒の白茶 cỏ lau",       78, 0.025),
    (16, "秋分", "Thu phân",    "彼岸花 hoa bỉ ngạn",     1, 0.108),
    (17, "寒露", "Hàn lộ",      "柿色 quả hồng",         50, 0.090),
    (18, "霜降", "Sương giáng", "紅葉 lá phong đỏ",      20, 0.081),
    # ── Đông: các màu lạnh ─────────────────────────────────────────────────
    (19, "立冬", "Lập đông",    "鉛色 gió bấc",         270, 0.054),
    (20, "小雪", "Tiểu tuyết",  "雪雲の鼠 mây tuyết",   228, 0.021),
    (21, "大雪", "Đại tuyết",   "雪の影の藍 bóng tuyết", 244, 0.104),
    (22, "冬至", "Đông chí",    "紫紺 ngân hà đông",    292, 0.099),
    (23, "小寒", "Tiểu hàn",    "氷色 băng",            197, 0.067),
    (24, "大寒", "Đại hàn",     "凍空の青 trời rét cóng", 229, 0.088),
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


def rgb_to_oklab(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def delta_e(hex_a, hex_b):
    """Khoảng cách màu trong OKLab, nhân 100: dưới ~2 mắt thường coi là một màu."""
    return math.dist(rgb_to_oklab(from_hex(hex_a)), rgb_to_oklab(from_hex(hex_b))) * 100


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)


def from_hex(s):
    s = s.lstrip("#")
    return [int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def luminance(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex_a, hex_b):
    la, lb = luminance(from_hex(hex_a)), luminance(from_hex(hex_b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def pick(L, chroma, hue):
    """Màu ở độ sáng L, hạ độ tươi tới khi vào gamut sRGB. Trả mã hex."""
    C = chroma
    while C > 0:
        rgb, inside = oklch_to_rgb(L, C, hue)
        if inside:
            break
        C -= 0.002
    return to_hex(oklch_to_rgb(L, C, hue)[0])


def build():
    """Mỗi tiết một dict; tương phản đo trên mã hex đã làm tròn, đúng thứ hiện ra."""
    rows = []
    for order, ja, vi, name, hue, chroma in SEKKI:
        light = pick(L_LIGHT, chroma, hue)
        dark = pick(L_DARK, chroma, hue)
        rows.append(dict(
            order=order, ja=ja, vi=vi, name=name, light=light, dark=dark,
            c_light=contrast(light, BG_LIGHT), b_light=contrast(light, BAND_LIGHT),
            c_dark=contrast(dark, BG_DARK), b_dark=contrast(dark, BAND_DARK),
        ))
    # Khoảng cách tới tiết kế tiếp; tiết cuối nối vòng về tiết đầu
    for i, row in enumerate(rows):
        nxt = rows[(i + 1) % len(rows)]
        row["step_light"] = delta_e(row["light"], nxt["light"])
        row["step_dark"] = delta_e(row["dark"], nxt["dark"])
    return rows


def toml_drift(rows):
    """Tên các tiết mà mã màu trong data/sekki.toml khác với bảng SEKKI."""
    text = TOML.read_text(encoding="utf-8")
    drift = []
    for row in rows:
        m = re.search(r'ja = "%s".*?accent_light = "([^"]*)".*?accent_dark = "([^"]*)"' % row["ja"],
                      text, re.S)
        if not m or (m.group(1), m.group(2)) != (row["light"], row["dark"]):
            drift.append(row["ja"])
    return drift


def write_toml(rows):
    text = TOML.read_text(encoding="utf-8")
    for row in rows:
        # Ghép theo chữ Hán: thứ tự trong toml là theo NGÀY (bắt đầu 小寒), không theo order
        text, n = re.subn(
            r'(ja = "%s".*?accent_light = ")[^"]*(".*?accent_dark = ")[^"]*(")' % row["ja"],
            lambda m: m.group(1) + row["light"] + m.group(2) + row["dark"] + m.group(3),
            text, count=1, flags=re.S)
        if n != 1:
            raise SystemExit(f"không tìm thấy {row['ja']} trong {TOML.name}")
    TOML.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Sinh và kiểm màu nhấn 24 tiết khí")
    ap.add_argument("--write", action="store_true", help="ghi mã màu vào data/sekki.toml")
    ap.add_argument("--check", action="store_true", help="chỉ kiểm, không in bảng")
    args = ap.parse_args()
    rows = build()

    if args.write:
        write_toml(rows)
        print(f"đã ghi {len(rows)} tiết vào {TOML.relative_to(TOML.parent.parent)}")

    if not args.check:
        print(f"{'':2} {'tiết':11} {'màu':24} {'sáng':9} {'nền':5} {'dải':5} {'ΔE':4}"
              f" {'tối':9} {'nền':5} {'dải':5} {'ΔE':4}")
        for r in rows:
            def flag(ok):
                return "" if ok else " ✗"
            print(f"{r['order']:2d} {r['vi']:11} {r['name']:24}"
                  f" {r['light']} {r['c_light']:4.1f}{flag(r['c_light'] >= FLOOR)}"
                  f" {r['b_light']:4.1f}{flag(r['b_light'] >= FLOOR)}"
                  f" {r['step_light']:4.1f}{flag(r['step_light'] >= STEP)}"
                  f" {r['dark']} {r['c_dark']:4.1f}{flag(r['c_dark'] >= FLOOR)}"
                  f" {r['b_dark']:4.1f}{flag(r['b_dark'] >= FLOOR)}"
                  f" {r['step_dark']:4.1f}{flag(r['step_dark'] >= STEP)}")

    low = sum(min(r[k] for k in ("c_light", "b_light", "c_dark", "b_dark")) < FLOOR for r in rows)
    close = sum(min(r["step_light"], r["step_dark"]) < STEP for r in rows)
    drift = toml_drift(rows)
    print(f"\n{len(rows)} tiết: tương phản ≥ {FLOOR} : 1 trên nền chính "
          f"{BG_LIGHT}/{BG_DARK} và dải 白緑 {BAND_LIGHT}/{BAND_DARK} — "
          f"{'đạt' if not low else f'{low} tiết KHÔNG đạt'}; "
          f"hai tiết liền kề ΔE ≥ {STEP} — {'đạt' if not close else f'{close} cặp KHÔNG đạt'}; "
          f"data/sekki.toml — {'khớp' if not drift else 'LỆCH ở ' + ', '.join(drift) + ' (chạy --write)'}")
    if low or close or drift:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
