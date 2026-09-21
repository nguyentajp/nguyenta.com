#!/usr/bin/env python3
"""Subset font: chỉ giữ lại đúng những chữ mà site thật sự dùng.

Font Nhật rất nặng. Đo thử với một đoạn tiếng Nhật khoảng 330 chữ:
cách chia sẵn của Google Fonts cần 28 file và 364 KB, còn subset đúng các ký
tự của trang đó chỉ 27 KB. Script này làm việc đó.

Hai chế độ:

    python3 tools/fonts/build.py --dev
        Quét toàn bộ content, i18n, data rồi ghi 5 file woff2 vào assets/fonts/.
        Dùng khi chạy `hugo server` ở máy.

    python3 tools/fonts/build.py --pages public
        Chạy SAU `hugo`. Với từng trang HTML, sinh subset riêng cho trang đó và
        thay khối @font-face trong <head>. Dùng trong GitHub Actions.

Font gốc lấy bằng tools/fonts/get-sources.py.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import sys

from fontTools import subset
from fontTools.otlLib import builder as otl
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "tools/fonts/src"

# Khối @font-face trong <head> mang id này; chế độ --pages thay ruột thẻ style.
# Không dùng comment CSS làm mốc vì Go html/template xoá comment trong <style>.
# hugo --minify bỏ dấu nháy quanh thuộc tính (id="gen-fonts" thành id=gen-fonts),
# nên các biểu thức dưới đây chấp nhận cả hai dạng.
STYLE_RE = re.compile(r'(<style[^>]*\bid=["\']?gen-fonts["\']?[^>]*>)(.*?)(</style>)', re.S)
CORE_RE = re.compile(r'data-fonts=["\']?core\b')
LANG_RE = re.compile(r'<html[^>]*\blang=["\']?([A-Za-z-]+)')
PRELOAD_RE = re.compile(r'<link\b[^>]*\brel=["\']?preload["\']?[^>]*\bas=["\']?font["\']?[^>]*>\s*', re.I)

# ── Bộ ký tự luôn có mặt, không phụ thuộc nội dung ───────────────────────────
# Nhờ vậy bài viết mới vẫn hiện đúng dù chưa chạy lại script.
def ranges(*pairs: tuple[int, int]) -> set[str]:
    out: set[str] = set()
    for start, end in pairs:
        out.update(chr(c) for c in range(start, end + 1))
    return out


# Không lấy trọn Latin Extended-A (U+0100–017F): 128 glyph cho tiếng Ba Lan,
# Séc, Thổ… mà site không dùng. Chỉ giữ đúng các ký tự tiếng Việt cần.
CORE_LATIN = ranges(
    (0x20, 0x7E),      # ASCII
    (0xA0, 0xFF),      # Latin-1: à â ê ô ...
    (0x1A0, 0x1B0),    # ơ ư (tiếng Việt)
    (0x300, 0x323),    # dấu tổ hợp
    (0x1EA0, 0x1EF9),  # toàn bộ dấu tiếng Việt: ạ ả ấ ầ ệ ộ ợ ự ỹ ...
    (0x2010, 0x2027),  # – — ‘ ’ “ ” …
    (0x2030, 0x203A),
) | set("ĂăĐđĨĩŨũŒœŠšŽžŸ") | set("€₫°±×÷•§¶†‡№")

CORE_JA = ranges(
    (0x3000, 0x303F),  # 、。「」『』〜 và khoảng trắng toàn chiều
    (0x3040, 0x309F),  # hiragana
    (0x30A0, 0x30FF),  # katakana
    (0xFF01, 0xFF60),  # ký tự toàn chiều: ！？（）：
    (0xFFE0, 0xFFE6),
)

CJK = [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0x20000, 0x2FA1F)]


def is_cjk(ch: str) -> bool:
    code = ord(ch)
    return any(start <= code <= end for start, end in CJK)


# ── Các face của site ────────────────────────────────────────────────────────
# scope quyết định bộ ký tự: "latin" cho chữ Latin và dấu tiếng Việt,
# "latin-display" và "ja-display" chỉ cho chữ trong tiêu đề, "ja" cho kana và
# kanji ở thân bài.
FACES = [
    # Literata là variable font hai trục. Trục opsz (optical size) chiếm khoảng
    # một nửa dung lượng file, nên ghim opsz = 20, mức trung gian giữa thân bài
    # 18px và tiêu đề. Trục wght giữ lại để vẫn có chữ đậm.
    # Đo thật: 2 trục 114 KB -> ghim opsz 58 KB.
    {
        "key": "literata-roman",
        "src": "Literata[opsz,wght].ttf",
        "family": "Gen Latin",
        "style": "normal",
        "weight": "380 620",
        "scope": "latin",
        "limit": {"wght": (380, 450, 620)},
        "pin": {"opsz": 20},
    },
    {
        "key": "literata-italic",
        "src": "Literata-Italic[opsz,wght].ttf",
        "family": "Gen Latin",
        "style": "italic",
        "weight": "380 620",
        "scope": "latin",
        "needs": "italic",
        "limit": {"wght": (380, 450, 620)},
        "pin": {"opsz": 20},
    },
    # Bản Literata cắt cho cỡ lớn, chỉ dùng cho tiêu đề từ khoảng 24px trở lên.
    # opsz càng cao thì nét thanh càng mảnh, khoảng chữ càng khít: đúng dáng chữ
    # người thiết kế vẽ riêng cho tiêu đề, thay vì phóng to chữ thân bài.
    # Ghim 60: so bằng mắt 20/40/60/72, mức 40 gần như không khác chữ thân bài,
    # 72 đẹp nhất ở cỡ lớn nhưng nét thanh hơi mảnh cho h2 26px trên màn hình
    # thường; 60 giữ gần trọn dáng 72 mà vẫn chắc nét. Chỉ subset đúng các chữ
    # có trong tiêu đề của trang nên file rất nhỏ.
    {
        "key": "literata-display",
        "src": "Literata[opsz,wght].ttf",
        "family": "Gen Latin Display",
        "style": "normal",
        "weight": "380 620",
        "scope": "latin-display",
        "limit": {"wght": (380, 450, 620)},
        "pin": {"opsz": 60},
    },
    {
        "key": "shippori-body",
        "src": "ShipporiMincho-Medium.ttf",
        "family": "Gen JP",
        "style": "normal",
        "weight": "500",
        "scope": "ja",
        "halt": True,
    },
    {
        "key": "shippori-display",
        "src": "ShipporiMinchoB1-SemiBold.ttf",
        "family": "Gen JP Display",
        "style": "normal",
        "weight": "600",
        "scope": "ja-display",
        "halt": True,
    },
]

# Giữ lại các feature cần dùng: kern, chữ ghép, palt cho tiêu đề tiếng Nhật,
# halt để trình duyệt thu gọn dấu câu tiếng Nhật đứng liền nhau. Site không
# có chữ viết dọc nên bỏ vert/vrt2 (dạng đứng của dấu câu) cho file nhẹ hơn.
LAYOUT_FEATURES = ["kern", "liga", "clig", "calt", "palt", "halt", "ccmp", "locl", "mark", "mkmk"]

# 約物の半角詰め. Shippori Mincho không có feature halt, nên khi hai dấu câu
# đứng liền nhau (」「, 。」) mỗi dấu vẫn chiếm trọn một ô, nhìn hở như chữ sắp
# vụng. Chrome dùng halt cho text-spacing-trim (mặc định bật), nên thêm halt với
# giá trị chuẩn theo JIS X 4051: dấu mở và dấu đóng chỉ còn nửa ô, dấu ở giữa
# ô (・：；) bỏ mỗi bên một phần tư.
HALT_OPENING = "「『（【〈《〔［｛〘〖"
HALT_CLOSING = "」』）】〉》〕］｝〙〗、。，．"
HALT_MIDDLE = "・：；"


def add_halt(font: TTFont) -> None:
    """Thêm feature halt vào bảng GPOS, giữ nguyên các feature đang có."""
    cmap = font.getBestCmap()
    half = font["head"].unitsPerEm // 2
    values = {}
    for chars, shift in ((HALT_OPENING, -half), (HALT_CLOSING, 0), (HALT_MIDDLE, -half // 2)):
        for char in chars:
            if glyph := cmap.get(ord(char)):
                values[glyph] = otl.buildValue({"XPlacement": shift, "XAdvance": -half})

    gpos = font["GPOS"].table
    assert getattr(gpos, "FeatureVariations", None) is None, "chưa hỗ trợ FeatureVariations"
    lookups = gpos.LookupList.Lookup
    lookups.append(otl.buildLookup(otl.buildSinglePos(values, font.getReverseGlyphMap())))
    gpos.LookupList.LookupCount = len(lookups)

    feature = ot.Feature()
    feature.FeatureParams = None
    feature.LookupListIndex = [len(lookups) - 1]
    feature.LookupCount = 1
    record = ot.FeatureRecord()
    record.FeatureTag = "halt"
    record.Feature = feature

    # Danh sách feature phải xếp theo tên (HarfBuzz tìm bằng tìm kiếm nhị phân),
    # nên chèn halt vào đúng chỗ rồi đánh lại số cho mọi LangSys trỏ tới.
    records = gpos.FeatureList.FeatureRecord + [record]
    order = sorted(range(len(records)), key=lambda i: records[i].FeatureTag)
    new_index = {old: new for new, old in enumerate(order)}
    gpos.FeatureList.FeatureRecord = [records[i] for i in order]
    gpos.FeatureList.FeatureCount = len(records)
    halt_index = new_index[len(records) - 1]
    for script in gpos.ScriptList.ScriptRecord:
        langsyses = [script.Script.DefaultLangSys] + [r.LangSys for r in script.Script.LangSysRecord]
        for langsys in filter(None, langsyses):
            langsys.FeatureIndex = sorted([new_index[i] for i in langsys.FeatureIndex] + [halt_index])
            langsys.FeatureCount = len(langsys.FeatureIndex)
            if langsys.ReqFeatureIndex != 0xFFFF:
                langsys.ReqFeatureIndex = new_index[langsys.ReqFeatureIndex]


# Bản font đã chuẩn bị (thu hẹp trục, thêm halt) được dựng một lần rồi dùng lại
# cho mọi trang.
_prepared: dict[str, pathlib.Path] = {}


def prepared_source(face: dict) -> pathlib.Path:
    """Thu hẹp, ghim trục của variable font và thêm halt nếu cần, trước khi subset."""
    source = SRC / face["src"]
    if not face.get("limit") and not face.get("pin") and not face.get("halt"):
        return source
    if face["key"] in _prepared:
        return _prepared[face["key"]]

    # recalcTimestamp=False: giữ nguyên ngày trong bảng head của font gốc. Mặc
    # định fontTools ghi giờ lúc build vào đó, nên mỗi lần build ra file khác
    # byte dù cùng nội dung, và build ở máy với build trên GitHub không khớp.
    font = TTFont(str(source), recalcTimestamp=False)
    if face.get("limit") or face.get("pin"):
        axes = dict(face.get("limit") or {})
        axes.update(face.get("pin") or {})
        instancer.instantiateVariableFont(font, axes, inplace=True, updateFontNames=False)
    if face.get("halt"):
        add_halt(font)
    cache_dir = SRC / ".prepared"
    cache_dir.mkdir(exist_ok=True)
    target = cache_dir / f"{face['key']}.ttf"
    font.save(str(target))
    font.close()
    _prepared[face["key"]] = target
    return target


def subset_font(source: pathlib.Path, chars: set[str], destination: pathlib.Path) -> int:
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = LAYOUT_FEATURES
    options.drop_tables += ["DSIG"]
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.notdef_outline = True
    options.recalc_bounds = True

    font = subset.load_font(str(source), options)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text="".join(sorted(chars)))
    subsetter.subset(font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    subset.save_font(font, str(destination), options)
    font.close()
    return destination.stat().st_size


ASCII = ranges((0x20, 0x7E))


def chars_for(scope: str, text_all: str, text_display: str, core: bool = True) -> set[str]:
    """Bộ ký tự cho một scope.

    core = True: thêm phần cốt lõi (toàn bộ dấu tiếng Việt, toàn bộ kana). Dùng
    cho chế độ --dev và cho những trang có chữ sinh ra động như trang tìm kiếm,
    vì lúc đó không biết trước sẽ hiện chữ nào.

    core = False: chỉ đúng ký tự trang đó dùng. Đây là chỗ tiết kiệm lớn nhất:
    trang tiếng Nhật từ khoảng 200 KB xuống vài chục KB.
    """
    if scope == "latin":
        found = {c for c in text_all if not is_cjk(c) and ord(c) < 0x3000}
        return (CORE_LATIN if core else ASCII) | found
    if scope == "latin-display":
        found = {c for c in text_display if not is_cjk(c) and ord(c) < 0x3000}
        return (CORE_LATIN if core else set()) | found
    if scope == "ja":
        found = {c for c in text_all if is_cjk(c) or 0x3000 <= ord(c) < 0x3100 or 0xFF00 <= ord(c) < 0xFFF0}
        return (CORE_JA if core else set()) | found
    if scope == "ja-display":
        found = {c for c in text_display if is_cjk(c) or 0x3000 <= ord(c) < 0x3100 or 0xFF00 <= ord(c) < 0xFFF0}
        return (CORE_JA if core else set()) | found
    raise ValueError(scope)


# ── Chế độ --dev: quét nguồn nội dung ────────────────────────────────────────
def collect_from_sources() -> tuple[str, str]:
    all_text: list[str] = []
    display_text: list[str] = []

    for path in sorted((ROOT / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        all_text.append(text)
        # Tiêu đề bài, description và các heading dùng font display
        for match in re.finditer(r'^(?:title|description):\s*"?(.*?)"?\s*$', text, re.M):
            display_text.append(match.group(1))
        for match in re.finditer(r"^#{1,3}\s+(.*)$", text, re.M):
            display_text.append(match.group(1))

    for name in ("i18n/vi.toml", "i18n/ja.toml", "data/sekki.toml", "hugo.toml"):
        path = ROOT / name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            all_text.append(content)
            display_text.append(content)

    return "".join(all_text), "".join(display_text)


def build_dev() -> None:
    all_text, display_text = collect_from_sources()
    out_dir = ROOT / "assets/fonts"
    report = []
    for face in FACES:
        chars = chars_for(face["scope"], all_text, display_text)
        size = subset_font(prepared_source(face), chars, out_dir / f"{face['key']}.woff2")
        report.append((face["key"], len(chars), size))

    print("Subset cho toàn site (dùng khi chạy hugo server ở máy):")
    total = 0
    for key, glyphs, size in report:
        total += size
        print(f"  {key:<20} {glyphs:>6} ký tự   {size / 1024:>7.1f} KB")
    print(f"  {'tổng':<20} {'':>6}          {total / 1024:>7.1f} KB")


# ── Chế độ --pages: subset riêng cho từng trang, chạy sau hugo ───────────────
TAG_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
# Thuộc tính mang chữ người đọc thấy được: alt, title, placeholder… và mọi
# data-* (JS lấy ra để hiện: lời nhắn bản tin, trạng thái tìm kiếm, chú thích
# ảnh phóng to). Giá trị có thể không có dấu nháy vì hugo --minify bỏ nháy.
ATTR_RE = re.compile(
    r'\b(?:alt|title|aria-label|placeholder|content|data-[\w-]+)'
    r'=(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+))',
    re.I,
)
HEADING_RE = re.compile(r"<h[1-3]\b[^>]*>(.*?)</h[1-3]>", re.S | re.I)
STRIP_RE = re.compile(r"<[^>]+>")


def page_text(markup: str) -> tuple[str, str]:
    body = TAG_RE.sub(" ", markup)
    visible = html.unescape(STRIP_RE.sub(" ", body))
    attrs = " ".join(html.unescape("".join(m)) for m in ATTR_RE.findall(body))
    headings = " ".join(html.unescape(STRIP_RE.sub(" ", m)) for m in HEADING_RE.findall(body))
    title = re.search(r"<title>(.*?)</title>", body, re.S | re.I)
    if title:
        headings += " " + html.unescape(title.group(1))
    return visible + " " + attrs, headings


def build_pages(public: pathlib.Path) -> None:
    font_dir = public / "fonts/p"
    cache: dict[tuple[str, str], str] = {}
    pages = sorted(public.rglob("*.html"))
    total_after = 0

    for page in pages:
        markup = page.read_text(encoding="utf-8")
        if not STYLE_RE.search(markup):
            continue
        all_text, display_text = page_text(markup)
        # Trang có chữ sinh ra động (trang tìm kiếm) tự khai báo cần bộ cốt lõi,
        # nhưng chỉ bộ cốt lõi của đúng ngôn ngữ trang đó: tìm bằng tiếng Việt
        # thì kết quả không bao giờ có kana.
        core = bool(CORE_RE.search(markup))
        lang = LANG_RE.search(markup)
        core_ja = core and bool(lang) and lang.group(1).startswith("ja")

        rules = []
        page_files: dict[str, str] = {}
        page_bytes = 0
        has_italic = bool(re.search(r"<(em|i)[ >]", markup))
        for face in FACES:
            if face.get("needs") == "italic" and not has_italic:
                continue          # không có chữ in nghiêng thì không cần face italic
            use_core = core_ja if face["scope"].startswith("ja") else core
            # Kết quả tìm kiếm hiện bằng chữ thân bài, không dùng font tiêu đề,
            # nên font tiêu đề không cần bộ cốt lõi ngay cả ở trang tìm kiếm
            if face["scope"] == "latin-display":
                use_core = False
            chars = chars_for(face["scope"], all_text, display_text, core=use_core)
            if not {c for c in chars if not c.isspace()}:
                continue          # trang tiếng Việt thường không có chữ Nhật nào
            digest = hashlib.sha256("".join(sorted(chars)).encode("utf-8")).hexdigest()[:12]
            key = (face["key"], digest)
            if key not in cache:
                name = f"{face['key']}.{digest}.woff2"
                size = subset_font(prepared_source(face), chars, font_dir / name)
                cache[key] = name
            name = cache[key]
            page_files[face["key"]] = name
            page_bytes += (font_dir / name).stat().st_size
            rules.append(
                "@font-face{"
                f"font-family:'{face['family']}';"
                f"font-style:{face['style']};"
                f"font-weight:{face['weight']};"
                "font-display:swap;"
                f"src:url(/fonts/p/{name}) format('woff2')"
                "}"
            )

        css = "".join(rules)
        # Preload đúng file subset của trang này, thay cho dòng preload trỏ tới
        # file toàn site mà Hugo sinh ra (nếu giữ, trình duyệt tải thừa một file
        # và file thật lại về muộn, chữ bị đổi font muộn làm bố cục xô lệch).
        # Font tiêu đề cũng preload: nó về muộn thì tiêu đề đổi độ rộng, có thể
        # xuống dòng khác và đẩy nội dung bên dưới (CLS).
        wanted = ["literata-roman", "literata-display"] + (["shippori-body"] if lang and lang.group(1).startswith("ja") else [])
        preload = "".join(
            f'<link rel=preload href=/fonts/p/{page_files[k]} as=font type=font/woff2 crossorigin>'
            for k in wanted if k in page_files
        )
        markup = PRELOAD_RE.sub("", markup)
        markup = STYLE_RE.sub(lambda m: preload + m.group(1) + css + m.group(3), markup, count=1)
        page.write_text(markup, encoding="utf-8")
        total_after += page_bytes

    print(f"Đã subset font riêng cho {len(pages)} trang.")
    print(f"  số file woff2 sinh ra: {len(cache)}")
    print(f"  tổng dung lượng font: {total_after / 1024:.1f} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dev", action="store_true", help="subset cho toàn site, ghi vào assets/fonts/")
    group.add_argument("--pages", metavar="DIR", help="subset riêng từng trang trong thư mục đã build")
    args = parser.parse_args()

    missing = [face["src"] for face in FACES if not (SRC / face["src"]).exists()]
    if missing:
        sys.exit(f"Thiếu font gốc: {missing}\nChạy trước: python3 tools/fonts/get-sources.py")

    if args.dev:
        build_dev()
    else:
        build_pages(pathlib.Path(args.pages))


if __name__ == "__main__":
    main()
