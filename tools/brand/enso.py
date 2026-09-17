"""Ensō cho trang 静, dựng bằng cách mô phỏng một cây bút lông cỡ lớn.

    python3 tools/brand/enso.py            # ghi assets/brand/enso.webp
    python3 tools/brand/enso.py 21         # thử một lần sinh ngẫu nhiên khác

Mỗi sợi lông mang lượng mực riêng. Khi còn nhiều mực, sợi để lại nét liền; mực
cạn dần thì nét tách thành vệt đứt quãng (掠れ, kasure). Sợi ở mép cạn trước nên
nét xơ dần từ ngoài vào, và vài sợi rời khỏi đám ở cuối nét.

Kết quả là ảnh mặt nạ: phần có mực nằm ở kênh alpha, còn màu do CSS tô bằng
mask-image. Nhờ vậy dark mode dùng lại đúng một file.

Cùng một seed luôn cho ra đúng một hình, nên chạy lại lúc nào cũng khớp.
"""
import math
import pathlib
import sys
import numpy as np
from PIL import Image, ImageDraw

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
rng = np.random.default_rng(SEED)
S = 3200                       # supersampled canvas; final image is S/2
OUT = S // 2
C = np.array([S * .5, S * .5])

TH0, SWEEP = math.radians(203), math.radians(338)     # start at ~10 o'clock, travel clockwise, leave a gap on the left
N_SAMPLES = 4200
N_BRISTLES = 340
N_CLUMPS = 16

def radius(th):
    return S * .352 * (1 + .0045 * np.sin(2 * th + .6) + .003 * np.sin(3 * th + 1.9))

def half_width(t):
    press = .022 * np.exp(-((t - .03) / .07) ** 2)                        # extra width where the tip presses down
    swell = .006 * np.sin(t * 7.3 + .4) + .004 * np.sin(t * 17.0 + 2.1)   # pressure never stays even
    return S * (.068 + press - .008 * t + swell)

def value_noise(t, length, r):
    n = int(1 / length) + 3
    knots = r.random(n)
    x = t / length
    i0 = np.clip(np.floor(x).astype(int), 0, n - 2)
    f = x - np.floor(x)
    f = f * f * (3 - 2 * f)
    return knots[i0] * (1 - f) + knots[i0 + 1] * f

def on_path(tt):
    th = TH0 + SWEEP * tt
    return C[0] + radius(th) * math.cos(th), C[1] + radius(th) * math.sin(th)

img = Image.new("L", (S, S), 0)
draw = ImageDraw.Draw(img)

# the tip lands: one rounded, convex head where ink soaks in
hw = float(half_width(np.array([.03]))[0]) * .56
(x0, y0), (x1, y1) = on_path(.036), on_path(.09)
draw.ellipse([x0 - hw, y0 - hw, x0 + hw, y0 + hw], fill=255)
draw.line([(x0, y0), (x1, y1)], fill=255, width=int(2 * hw))

clumps = np.linspace(-.92, .92, N_CLUMPS) + rng.normal(0, .04, N_CLUMPS)
for b in range(N_BRISTLES):
    o = float(np.clip(rng.choice(clumps) + rng.normal(0, .1), -1.05, 1.05))   # hairs gather in clumps
    edge = abs(o)
    width = rng.uniform(2.5, 6) + 4.5 * (1 - min(edge, 1)) * rng.random()
    ink0 = (1.05 + .3 * rng.random()) * (1 - .25 * min(edge, 1) ** 1.3)
    dep = .8 + 1.05 * min(edge, 1) ** 1.5 + .95 * rng.random() ** 2
    t_start = .07 * (1 - math.sqrt(max(0.0, 1 - min(o * o, 1)))) ** 1.2 + .003 * rng.random()   # rounded head
    t_end = 1 - .025 * rng.random() * min(edge, 1) + (.03 * rng.random() if rng.random() < .1 else 0)  # a few flying hairs

    t = np.linspace(t_start, t_end, N_SAMPLES)
    th = TH0 + SWEEP * t
    drift = .04 * (value_noise(t, .09, rng) - .5)
    splay = 1 + .12 * np.clip((t - .85) / .15, 0, 1)
    off = (o + drift) * splay * half_width(t)
    rr = radius(th) + off
    xs = C[0] + rr * np.cos(th)
    ys = C[1] + rr * np.sin(th)

    ink = ink0 - dep * t ** 1.6 + .4 * np.exp(-(t / .09) ** 2) + .12 * np.exp(-((t - .72) / .1) ** 2)
    streak = .66 * value_noise(t, rng.uniform(.008, .035), rng) + .34 * value_noise(t, rng.uniform(.0015, .005), rng)
    contact = streak < np.clip(ink, 0, 1.3)

    # draw each continuous run of contact as one polyline
    idx = np.flatnonzero(np.diff(np.concatenate(([0], contact.astype(np.int8), [0]))))
    for a, z in zip(idx[::2], idx[1::2]):
        if z - a < 3:
            continue
        draw.line(list(zip(xs[a:z].tolist(), ys[a:z].tolist())), fill=255, width=max(1, int(round(width))), joint="curve")

# ink spatter: sparse, near the heavy first part, some flecks stretched along the stroke
for _ in range(26):
    t = rng.beta(1.2, 4.5)
    th = TH0 + SWEEP * t
    d = half_width(t) * rng.uniform(1.04, 1.25) * (1 if rng.random() < .8 else -1)
    rr = radius(th) + d
    x, y = C[0] + rr * math.cos(th), C[1] + rr * math.sin(th)
    s_ = rng.uniform(1.2, 4.2)
    if rng.random() < .4:
        L = rng.uniform(8, 26); tx, ty = -math.sin(th), math.cos(th)
        draw.line([(x, y), (x + tx * L, y + ty * L)], fill=255, width=max(1, int(s_)))
    else:
        draw.ellipse([x - s_, y - s_, x + s_, y + s_], fill=255)

mask = img.resize((OUT, OUT), Image.LANCZOS)
OUT = pathlib.Path(__file__).resolve().parents[2] / "assets/brand"
OUT.mkdir(parents=True, exist_ok=True)
rgba = Image.new("RGBA", mask.size, (0, 0, 0, 0))
rgba.putalpha(mask)
rgba.resize((900, 900), Image.LANCZOS).save(OUT / "enso.webp", quality=82, method=6)
print(f"  assets/brand/enso.webp   {(OUT / 'enso.webp').stat().st_size / 1024:.1f} KB  (seed {SEED})")

