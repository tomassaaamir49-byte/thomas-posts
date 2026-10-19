"""Builds an Instagram carousel (1080x1350 PNGs) from a JSON spec.

usage: python3 make_carousel.py spec.json outdir
"""
import json, sys, os, math, re
from PIL import Image, ImageDraw, ImageFont

FONT = os.environ.get("CAROUSEL_FONT",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "Cairo.ttf"))
W, H = 1080, 1350
M = 90  # side margin

NAVY = (11, 37, 69)
INK = (30, 50, 80)
BLUE = (30, 115, 232)
SKY = (232, 242, 255)
RED = (229, 57, 53)
WHITE = (255, 255, 255)
MUTED = (110, 130, 155)

NAME = "توماس سمير فوزي • طالب طب بشري"
USER = "@thomassamir_medical_student"
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]+")


def font(size, weight=700):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight, 0])
    return f


def wrap(draw, text, f, maxw, rtl=True):
    text = _EMOJI.sub("", text or "").strip()  # font has no emoji glyphs
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f, direction="rtl" if rtl else None) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def draw_block(draw, text, f, y, color, maxw=W - 2 * M, gap=1.45, align="right", right=W - M):
    lh = int(f.size * gap)
    for line in wrap(draw, text, f, maxw):
        tw = draw.textlength(line, font=f, direction="rtl")
        x = right - tw if align == "right" else (W - tw) / 2
        draw.text((x, y), line, font=f, fill=color, direction="rtl")
        y += lh
    return y


def block_height(draw, text, f, maxw=W - 2 * M, gap=1.45):
    return len(wrap(draw, text, f, maxw)) * int(f.size * gap)


def background(accent):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    # soft vertical gradient
    for y in range(H):
        t = y / H
        c = tuple(int(WHITE[i] * (1 - t) + SKY[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # decorative circles
    d.ellipse([W - 260, -200, W + 200, 260], fill=(214, 232, 255))
    d.ellipse([-180, H - 520, 220, H - 120], fill=(222, 237, 255))
    # top accent bar
    d.rectangle([0, 0, W, 14], fill=accent)
    return img, d


def footer(d):
    y = H - 150
    d.line([(M, y), (W - M, y)], fill=(200, 215, 235), width=2)
    f1, f2 = font(34, 700), font(32, 600)
    tw = d.textlength(NAME, font=f1, direction="rtl")
    d.text(((W - tw) / 2, y + 18), NAME, font=f1, fill=NAVY, direction="rtl")
    tw = d.textlength(USER, font=f2)
    d.text(((W - tw) / 2, y + 66), USER, font=f2, fill=BLUE)


def counter(d, i, n):
    txt = f"{i}/{n}".translate(AR_DIGITS)
    f = font(30, 700)
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([M - 10, 60, M + tw + 30, 112], radius=26, fill=WHITE, outline=(200, 215, 235), width=2)
    d.text((M + 10, 64), txt, font=f, fill=MUTED)


def tag(d, text, color, y=60):
    f = font(32, 800)
    tw = d.textlength(text, font=f, direction="rtl")
    d.rounded_rectangle([W - M - tw - 40, y, W - M, y + 56], radius=28, fill=color)
    d.text((W - M - tw - 20, y + 4), text, font=f, fill=WHITE, direction="rtl")


def slide_cover(s, i, n):
    accent = RED if s.get("alert") else BLUE
    img, d = background(accent)
    counter(d, i, n)
    if s.get("kicker"):
        tag(d, s["kicker"], accent)
    ft, fb = font(92, 900), font(46, 600)
    th = block_height(d, s["title"], ft, gap=1.3)
    bh = block_height(d, s.get("body", ""), fb) if s.get("body") else 0
    y = (H - 150 - th - bh - 60) / 2 + 40
    y = draw_block(d, s["title"], ft, y, NAVY, gap=1.3)
    d.rounded_rectangle([W - M - 160, y + 25, W - M, y + 37], radius=6, fill=accent)
    if s.get("body"):
        draw_block(d, s["body"], fb, y + 70, INK)
    # swipe hint
    f = font(38, 800)
    hint = "اسحب للشمال"
    tw = d.textlength(hint, font=f, direction="rtl")
    x0 = (W - tw - 80) / 2
    d.text((x0 + 80, H - 235), hint, font=f, fill=accent, direction="rtl")
    ay = H - 207
    d.line([(x0, ay), (x0 + 55, ay)], fill=accent, width=6)
    d.polygon([(x0 - 6, ay), (x0 + 18, ay - 16), (x0 + 18, ay + 16)], fill=accent)
    footer(d)
    return img


def slide_point(s, i, n):
    accent = RED if s.get("alert") else BLUE
    img, d = background(accent)
    counter(d, i, n)
    if s.get("kicker"):
        tag(d, s["kicker"], accent)
    ft, fb = font(82, 900), font(50, 600)
    inner = W - 2 * M - 110
    r = 90
    th = block_height(d, s["title"], ft, gap=1.35)
    bh = block_height(d, s.get("body", ""), fb, maxw=inner) if s.get("body") else 0
    total = (2 * r + 50 if s.get("num") is not None else 0) + th + (bh + 100 if bh else 0)
    y = max(170, (H - 170 - total) / 2 + 20)
    if s.get("num") is not None:
        cx = W - M - r
        d.ellipse([cx - r, y, cx + r, y + 2 * r], fill=accent)
        num = str(s["num"]).translate(AR_DIGITS)
        fn = font(120, 900)
        bb = d.textbbox((0, 0), num, font=fn)
        d.text((cx - (bb[0] + bb[2]) / 2, y + r - (bb[1] + bb[3]) / 2), num, font=fn, fill=WHITE)
        y += 2 * r + 50
    y = draw_block(d, s["title"], ft, y, NAVY, gap=1.35)
    y += 40
    if s.get("body"):
        d.rounded_rectangle([M, y, W - M, y + bh + 70], radius=36, fill=WHITE, outline=(205, 222, 245), width=3)
        d.rounded_rectangle([W - M - 14, y + 28, W - M - 2, y + bh + 42], radius=6, fill=accent)
        draw_block(d, s["body"], fb, y + 28, INK, maxw=inner, right=W - M - 55)
    footer(d)
    return img


def slide_cta(s, i, n):
    img, d = background(BLUE)
    counter(d, i, n)
    y = 200
    y = draw_block(d, s["title"], font(76, 900), y, NAVY, gap=1.35)
    if s.get("body"):
        y = draw_block(d, s["body"], font(44, 600), y + 20, INK)
    y += 50
    actions = s.get("actions", [
        ("تابعني", "عشان بوست طبي جديد كل يوم"),
        ("احفظ البوست", "هتحتاجه في وقت مش متوقع"),
        ("ابعته", "لحد بتحبه وخايف عليه"),
        ("اكتبلي في الكومنت", "عايز البوست الجاي عن إيه؟"),
    ])
    fa, fs = font(46, 800), font(36, 600)
    for a, sub in actions:
        d.rounded_rectangle([M, y, W - M, y + 130], radius=30, fill=WHITE, outline=(205, 222, 245), width=3)
        d.ellipse([W - M - 100, y + 35, W - M - 40, y + 95], fill=BLUE)
        cx, cy = W - M - 70, y + 65
        d.line([(cx - 14, cy), (cx - 4, cy + 11), (cx + 15, cy - 11)], fill=WHITE, width=7, joint="curve")
        tw = d.textlength(a, font=fa, direction="rtl")
        d.text((W - M - 130 - tw, y + 12), a, font=fa, fill=NAVY, direction="rtl")
        tw = d.textlength(sub, font=fs, direction="rtl")
        d.text((W - M - 130 - tw, y + 72), sub, font=fs, fill=MUTED, direction="rtl")
        y += 155
    src = s.get("source")
    if src:
        fs = font(28, 600)
        line = "المصدر: " + src
        tw = d.textlength(line, font=fs, direction="rtl")
        d.text(((W - tw) / 2, H - 200), line, font=fs, fill=MUTED, direction="rtl")
    footer(d)
    return img


def main(spec_path, outdir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    slides = spec["slides"]
    n = len(slides)
    paths = []
    spec_source = spec.get("source")
    for i, s in enumerate(slides, 1):
        if s["type"] == "cta" and spec_source and "source" not in s:
            s = dict(s, source=spec_source)
        fn = {"cover": slide_cover, "point": slide_point, "cta": slide_cta}[s["type"]]
        img = fn(s, i, n)
        p = os.path.join(outdir, f"slide_{i:02d}.jpg")  # Instagram publishing accepts JPEG
        img.convert("RGB").save(p, "JPEG", quality=92, optimize=True)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
