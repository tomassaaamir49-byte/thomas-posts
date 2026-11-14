"""Brand carousel renderer (1080x1350 JPGs) — follows brand/style-guide.html (brand system v1).

usage: POST_SERIES=<youth|parents|older|general|quiz|emergency> python3 make_carousel.py spec.json outdir

The colours and fonts are FIXED (ink on paper, teal brand, one series accent per post).
Variety comes from the cover layout and the slide types, not from colours.

Spec:
  "series": youth | parents | older | general | quiz | emergency   (POST_SERIES env overrides; falls back to "audience")
  Every slide except the face cover and the closing takes an illustration:
    "icon": a Tabler outline icon name (assets/icons/tabler/<name>.svg, e.g. heart, ambulance, lungs, toilet,
            droplet, zzz, scale, stethoscope, phone-call, armchair, steering-wheel-off, baby-carriage, school)
    "icon2" (optional): a small companion icon that completes the meaning (e.g. heart + clock = "sudden").
  slides (7-9):
    cover      layout: classic (DEFAULT, the original look the user wants) | face | numeral | question | alert
               kicker (who it is for), title (use \n for lines; last line is highlighted on the face cover),
               body (optional), badge (optional, else the series name)
               numeral: "num" (the big number) ; question: "statement" ; alert: "band" (red band text)
    point      kicker (badge), num (optional), title, body
               alert:true  -> red-flag slide (red band = kicker, title, body or items)
    redflags   kicker (band text), title (optional), items [..]
    myth       myth (crossed out), title (the fact headline), body
    data       kicker, title (the takeaway), bars [{"label","value","pct" 0-100,"hi":true}], source
    answer     kicker, verdict "صح"|"غلط", title, body       (quiz answers)
    checklist  kicker, title, items [3-5]      (the save slide, tint ground)
    cta        title, body                      (closing, ink ground, photo avatar, source)
"""
import json, sys, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FD = os.path.join(ROOT, "fonts")
W, H = 1080, 1350
M = 80            # side margin
TOP = 96          # top margin
FOOT = 150        # footer zone height
TITLE_TOP = 200

# ---- brand colours (fixed) ----
INK = (15, 36, 48)
PAPER = (244, 246, 243)
WHITE = (255, 255, 255)
TEAL = (11, 110, 106)
TINT = (221, 237, 234)
MINT = (127, 209, 195)
MUTE = (78, 95, 102)
LINE = (201, 214, 210)
BODY = (38, 64, 75)
BODY_ON_INK = (211, 226, 224)
MUTE_ON_INK = (184, 203, 203)
MYTH_BG = (233, 236, 234)
MYTH_TXT = (94, 110, 115)
RED = (194, 53, 43)
RED_TINT = (246, 222, 219)

SERIES = {  # accent on paper, accent on ink, label
    "youth":     ((63, 67, 201),  (172, 175, 255), "سلسلة الشباب"),
    "parents":   ((166, 73, 22),  (242, 180, 143), "سلسلة الأهالي"),
    "older":     (TEAL,           MINT,            "صحتك بالدنيا"),
    "general":   (TEAL,           MINT,            "معلومة طبية"),
    "quiz":      (TEAL,           MINT,            "صح ولا غلط؟"),
    "emergency": (RED,            (255, 154, 144), "علامات طوارئ"),
}
_SER = os.environ.get("POST_SERIES", "general")
ACC, ACC_INK, SER_LABEL = SERIES.get(_SER, SERIES["general"])

# legacy names used by make_story.py / make_reel.py
NAVY = INK
BLUE = ACC
SKY = TINT
MUTED = MUTE

NAME = "توماس سمير فوزي · طالب طب بشري"
USER = "@thomassamir_medical_student"
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")
PHOTO = os.environ.get("POST_PHOTO", os.path.join(ROOT, "assets", "thomas.jpg"))

# ---- fonts: Alexandria (display, weight >= 700 headings) + IBM Plex Sans Arabic (body) ----
_PLEX = {400: "IBMPlexSansArabic-Regular.ttf", 500: "IBMPlexSansArabic-Medium.ttf",
         600: "IBMPlexSansArabic-SemiBold.ttf", 700: "IBMPlexSansArabic-Bold.ttf"}
_fcache = {}


def _alex(size, weight):
    f = ImageFont.truetype(os.path.join(FD, "Alexandria.ttf"), size)
    try:
        vals = []
        for a in f.get_variation_axes():
            n = a.get("name", b"")
            n = n.decode() if isinstance(n, bytes) else str(n)
            vals.append(max(a["minimum"], min(a["maximum"], weight)) if n.lower() in ("weight", "wght") else a.get("default", a["minimum"]))
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def display(size, weight=800):
    k = ("d", size, weight)
    if k not in _fcache:
        _fcache[k] = _alex(size, weight)
    return _fcache[k]


def text_font(size, weight=500):
    k = ("t", size, weight)
    if k not in _fcache:
        w = min(_PLEX, key=lambda x: abs(x - weight))
        _fcache[k] = ImageFont.truetype(os.path.join(FD, _PLEX[w]), size)
    return _fcache[k]


def font(size, weight=700):
    """Legacy helper: heavy weights -> Alexandria, the rest -> IBM Plex."""
    return display(size, min(weight, 800)) if weight >= 800 else text_font(size, weight)


def clean(t):
    return _EMOJI.sub("", t or "").strip()


def wrap(draw, text, f, maxw, rtl=True):
    lines = []
    for para in clean(text).split("\n"):
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
    # avoid a lonely last word when the paragraph wrapped
    if len(lines) >= 2 and len(lines[-1].split()) == 1 and len(lines[-2].split()) >= 3:
        prev = lines[-2].split()
        cand = " ".join(prev[:-1]), prev[-1] + " " + lines[-1]
        if draw.textlength(cand[1], font=f, direction="rtl") <= maxw:
            lines[-2:] = list(cand)
    return lines


def text_h(f, lines, lh):
    return 0 if not lines else (len(lines) - 1) * int(f.size * lh) + f.size


def draw_lines(d, lines, f, y, color, lh, right=W - M, colors=None):
    for k, line in enumerate(lines):
        tw = d.textlength(line, font=f, direction="rtl")
        d.text((right - tw, y), line, font=f, fill=(colors[k] if colors else color), direction="rtl")
        y += int(f.size * lh)
    return y - int(f.size * lh) + f.size if lines else y


def draw_block(d, text, f, y, color, maxw=W - 2 * M, gap=1.45, align="right", right=W - M):
    """Legacy helper kept for make_reel.py."""
    lh = int(f.size * gap)
    for line in wrap(d, text, f, maxw):
        tw = d.textlength(line, font=f, direction="rtl")
        x = right - tw if align == "right" else (W - tw) / 2
        d.text((x, y), line, font=f, fill=color, direction="rtl")
        y += lh
    return y


def block_height(d, text, f, maxw=W - 2 * M, gap=1.45):
    return len(wrap(d, text, f, maxw)) * int(f.size * gap)


# ---------- furniture ----------
PHOTO_BG = os.environ.get("POST_PHOTO_BG", "1") != "0"   # Thomas's photo behind every slide (user request 2026-11-14)
_bg_cache = {}


def _photo_frame():
    """Thomas's photo filling the 1080x1350 frame, face around y=560 (behind the content)."""
    if "frame" in _bg_cache:
        return _bg_cache["frame"]
    ph = _photo()
    if ph is None:
        _bg_cache["frame"] = None
        return None
    ph = ph.resize((W, int(ph.height * W / ph.width)), Image.LANCZOS)
    off = max(H - ph.height, min(0, 560 - int(ph.height * 0.27)))
    fr = Image.new("RGB", (W, H), PAPER)
    fr.paste(ph, (0, off))
    _bg_cache["frame"] = fr
    return fr


def canvas(ground):
    """Slide ground. With PHOTO_BG the photo sits under a veil of the ground colour so text stays crisp."""
    img = Image.new("RGB", (W, H), ground)
    fr = _photo_frame() if PHOTO_BG else None
    if fr is not None:
        veil = 0.86 if ground != INK else 0.84
        img = Image.blend(fr, img, veil)
    return img, ImageDraw.Draw(img)


def band(img, box, color, alpha=0.88):
    """Semi-opaque colour band, so the background photo still reads through it."""
    x0, y0, x1, y1 = [int(v) for v in box]
    reg = img.crop((x0, y0, x1, y1))
    img.paste(Image.blend(reg, Image.new("RGB", reg.size, color), alpha), (x0, y0))


def badge(d, text, fill, y=56, txt=WHITE):
    f = text_font(30, 600)
    tw = d.textlength(text, font=f, direction="rtl")
    d.rounded_rectangle([W - M - tw - 44, y, W - M, y + 58], radius=10, fill=fill)
    d.text((W - M - tw - 22, y + 7), text, font=f, fill=txt, direction="rtl")


def mark(d, i, n, color=MUTE, y=64):
    t = f"{i} / {n}".translate(AR_DIGITS)
    d.text((M, y), t, font=text_font(30, 600), fill=color, direction="rtl")


def footer(d, i, n, dark=False, label=NAME, acc=None):
    acc = acc or (ACC_INK if dark else ACC)
    y = H - 56 - 34
    f = text_font(28, 600)
    tw = d.textlength(label, font=f, direction="rtl")
    d.text((W - M - tw, y), label, font=f, fill=(WHITE if dark else INK), direction="rtl")
    seg, gap = 30, 8
    total = n * seg + (n - 1) * gap
    x0 = M
    for k in range(n):
        # RTL: slide 1 is the rightmost segment
        idx = n - 1 - k
        x = x0 + k * (seg + gap)
        on = idx == i - 1
        col = acc if on else ((47, 71, 83) if dark else LINE)
        d.rounded_rectangle([x, y + 16, x + seg, y + 24], radius=4, fill=col)


def acc_line(d, y, color, w=120):
    d.rounded_rectangle([W - M - w, y, W - M, y + 6], radius=3, fill=color)
    return y + 6


def swipe(d, y, color, text="اسحب للشمال"):
    f = text_font(34, 700)
    tw = d.textlength(text, font=f, direction="rtl")
    d.text((W - M - tw, y), text, font=f, fill=color, direction="rtl")
    lx = W - M - tw - 24
    d.rounded_rectangle([lx - 74, y + 26, lx, y + 31], radius=2, fill=color)
    d.polygon([(lx - 86, y + 28), (lx - 64, y + 15), (lx - 64, y + 41)], fill=color)
    return y + 50


def _photo():
    if not (PHOTO and os.path.exists(PHOTO)):
        return None
    return Image.open(PHOTO).convert("RGB")


def avatar(img, cx, cy, r, ring):
    ph = _photo()
    if ph is None:
        return
    s = ph.width
    crop = ph.crop((int(s * 0.18), int(ph.height * 0.12), int(s * 0.82), int(ph.height * 0.12) + int(s * 0.64)))
    crop = crop.resize((2 * r, 2 * r), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9], fill=ring)
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=WHITE)
    m = Image.new("L", crop.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * r, 2 * r], fill=255)
    img.paste(crop, (cx - r, cy - r), m)


# ---------- illustrations (Tabler outline icons, MIT, in assets/icons/tabler) ----------
ICON_DIRS = [os.path.join(ROOT, "assets", "icons", "tabler"), os.path.join(ROOT, "assets", "icons")]


def icon_img(name, size, color, stroke=1.6):
    import io
    import cairosvg
    path = next((os.path.join(dd, f"{name}.svg") for dd in ICON_DIRS if os.path.exists(os.path.join(dd, f"{name}.svg"))), None)
    if path is None:
        print(f"warning: icon '{name}' not found", file=sys.stderr)
        return None
    svg = open(path, encoding="utf-8").read()
    svg = svg.replace("currentColor", "#%02x%02x%02x" % color)
    svg = re.sub(r'stroke-width="[0-9.]+"', f'stroke-width="{stroke}"', svg)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def mix(a, b, t):
    return tuple(int(a[k] * (1 - t) + b[k] * t) for k in range(3))


def spot(img, cx, cy, r, name, name2=None, acc=None, ground=PAPER):
    """Spot illustration: tinted disc + big line icon (+ optional small companion icon)."""
    if not name:
        return
    acc = acc or ACC
    d = ImageDraw.Draw(img)
    # dashed outer ring
    rr = r + 22
    for a in range(0, 360, 12):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a, a + 6, fill=mix(ground, acc, 0.45), width=4)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(ground, acc, 0.14))
    ic = icon_img(name, int(r * 1.25), acc, 1.5)
    if ic is not None:
        img.paste(ic, (int(cx - ic.width / 2), int(cy - ic.height / 2)), ic)
    if name2:
        sr = int(r * 0.42)
        sx, sy = int(cx - r * 0.72), int(cy + r * 0.66)
        d.ellipse([sx - sr - 6, sy - sr - 6, sx + sr + 6, sy + sr + 6], fill=acc)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=WHITE)
        ic2 = icon_img(name2, int(sr * 1.25), INK, 1.8)
        if ic2 is not None:
            img.paste(ic2, (int(sx - ic2.width / 2), int(sy - ic2.height / 2)), ic2)


def vcenter(total, top=170, bottom=H - FOOT - 40):
    return max(top, top + (bottom - top - total) / 2)


# ---------- covers ----------
def cover_face(s, i, n):
    img, d = canvas(INK)
    fk, ft, fb = text_font(36, 600), display(100, 800), text_font(42, 500)
    kl = wrap(d, s.get("kicker", ""), fk, W - 2 * M) if s.get("kicker") else []
    tl = wrap(d, s["title"], ft, W - 2 * M)
    bl = wrap(d, s.get("body", ""), fb, W - 2 * M) if s.get("body") else []
    y = 190
    y_text_end = y + (text_h(fk, kl, 1.4) + 24 if kl else 0) + text_h(ft, tl, 1.3) + (28 + text_h(fb, bl, 1.5) if bl else 0) + 40 + 50
    top = int(min(max(H * 0.44, y_text_end + 30), 780))
    ph = _photo()
    if ph is not None:
        sc = W / ph.width
        ph = ph.resize((W, int(ph.height * sc)), Image.LANCZOS)
        off = -int((ph.height - (H - top)) * 0.08)
        region = Image.new("RGB", (W, H - top), INK)
        region.paste(ph, (0, off))
        img.paste(region, (0, top))
        # fades: ink into the photo at the top, darker behind the footer
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        fade = 160
        for yy in range(top, top + fade):
            a = int(150 * (1 - (yy - top) / fade))
            od.line([(0, yy), (W, yy)], fill=INK + (a,))
        start = int(H * 0.8)
        for yy in range(start, H):
            a = int(225 * (yy - start) / (H - start))
            od.line([(0, yy), (W, yy)], fill=INK + (a,))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
    badge(d, s.get("badge", SER_LABEL), ACC)
    mark(d, i, n, MUTE_ON_INK)
    if kl:
        y = draw_lines(d, kl, fk, y, ACC_INK, 1.4) + 24
    hl = s.get("highlight_line", len(tl) - 1 if len(tl) > 1 else -1)
    cols = [MINT if k == hl else WHITE for k in range(len(tl))]
    y = draw_lines(d, tl, ft, y, WHITE, 1.3, colors=cols)
    if bl:
        y = draw_lines(d, bl, fb, y + 28, BODY_ON_INK, 1.5)
    swipe(d, y + 40, WHITE)
    footer(d, i, n, dark=True)
    return img


def cover_numeral(s, i, n):
    img, d = canvas(PAPER)
    badge(d, s.get("badge", SER_LABEL), ACC)
    mark(d, i, n)
    num = str(s.get("num", "")).translate(AR_DIGITS)
    fn = display(440, 800)
    bb = d.textbbox((0, 0), num, font=fn)
    nw = bb[2] - bb[0]
    ny = 150
    d.text((W - M - bb[2], ny - bb[1] + 20), num, font=fn, fill=ACC)
    num_bottom = ny + 20 + (bb[3] - bb[1])
    right = W - M - nw - 40
    maxw = right - M
    fk, ft = text_font(34, 600), display(84, 800)
    kl = wrap(d, s.get("kicker", ""), fk, maxw) if s.get("kicker") else []
    tl = wrap(d, s["title"], ft, maxw)
    blk = (text_h(fk, kl, 1.4) + 18 if kl else 0) + text_h(ft, tl, 1.25)
    y = max(190, num_bottom - blk - 10)
    if kl:
        y = draw_lines(d, kl, fk, y, ACC, 1.4, right=right) + 18
    draw_lines(d, tl, ft, y, INK, 1.25, right=right)
    y = max(num_bottom, y) + 90
    if s.get("body"):
        fb = text_font(44, 500)
        y = draw_lines(d, wrap(d, s["body"], fb, W - 2 * M), fb, y, BODY, 1.55) + 40
    swipe(d, y + 10, ACC)
    avatar(img, M + 70, int(y + 35), 62, ACC)
    footer(d, i, n)
    return img


def cover_question(s, i, n):
    img, d = canvas(PAPER)
    badge(d, s.get("badge", SERIES["quiz"][2]), ACC)
    mark(d, i, n)
    fk, ft = text_font(36, 600), display(92, 800)
    y = 190
    if s.get("kicker"):
        y = draw_lines(d, wrap(d, s["kicker"], fk, W - 2 * M), fk, y, ACC, 1.4) + 20
    y = draw_lines(d, wrap(d, s["title"], ft, W - 2 * M), ft, y, INK, 1.3) + 60
    fs = display(58, 700)
    sl = wrap(d, s.get("statement", ""), fs, W - 2 * M - 110)
    ch = text_h(fs, sl, 1.35) + 100
    d.rounded_rectangle([M, y, W - M, y + ch], radius=24, fill=WHITE)
    draw_lines(d, sl, fs, y + 50, INK, 1.35, right=W - M - 55)
    y += ch + 26
    bw = (W - 2 * M - 24) / 2
    fc = display(60, 800)
    for k, (lab, bg, fg) in enumerate([("غلط", RED_TINT, RED), ("صح", TINT, TEAL)]):
        x1 = W - M - k * (bw + 24)
        d.rounded_rectangle([x1 - bw, y, x1, y + 120], radius=20, fill=bg)
        tw = d.textlength(lab, font=fc, direction="rtl")
        d.text((x1 - bw / 2 - tw / 2, y + 18), lab, font=fc, fill=fg, direction="rtl")
    y += 120 + 34
    swipe(d, y, ACC, "جاوب واسحب")
    footer(d, i, n)
    return img


def red_band(d, text, i, n):
    d.rectangle([0, 0, W, 150], fill=RED)
    f = display(46, 800)
    tw = d.textlength(text, font=f, direction="rtl")
    d.text((W - M - tw, 44), text, font=f, fill=WHITE, direction="rtl")
    mark(d, i, n, WHITE, y=58)


def cover_alert(s, i, n):
    img, d = canvas(PAPER)
    red_band(d, s.get("band", SERIES["emergency"][2]), i, n)
    fk, ft, fb = text_font(36, 600), display(100, 800), text_font(44, 500)
    tw_max = W - 2 * M - (360 if s.get("icon") else 0)
    kl = wrap(d, s.get("kicker", ""), fk, W - 2 * M) if s.get("kicker") else []
    tl = wrap(d, s["title"], ft, tw_max)
    bl = wrap(d, s.get("body", ""), fb, W - 2 * M) if s.get("body") else []
    total = (text_h(fk, kl, 1.4) + 22 if kl else 0) + text_h(ft, tl, 1.3) + 40 + 6 + (34 + text_h(fb, bl, 1.5) if bl else 0) + 40 + 50
    y = vcenter(total, top=250)
    if kl:
        y = draw_lines(d, kl, fk, y, RED, 1.4) + 22
    th = text_h(ft, tl, 1.3)
    spot(img, M + 160, int(y + th / 2), 140, s.get("icon"), s.get("icon2"), RED)
    d = ImageDraw.Draw(img)
    y = draw_lines(d, tl, ft, y, INK, 1.3) + 40
    y = acc_line(d, y, RED)
    if bl:
        y = draw_lines(d, bl, fb, y + 34, BODY, 1.5)
    swipe(d, y + 40, RED)
    avatar(img, M + 70, int(y + 65), 62, RED)
    footer(d, i, n, acc=RED)
    return img


def cover_classic(s, i, n):
    """The original cover look (user request 2026-11-14): light ground, big dark headline on top,
    Thomas clearly visible in the lower half, pill kicker, underline, swipe hint, centred name footer."""
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    for yy in range(H):
        d.line([(0, yy), (W, yy)], fill=mix(WHITE, PAPER, yy / H))
    ph = _photo()
    if ph is not None:
        ph = ph.resize((W, int(ph.height * W / ph.width)), Image.LANCZOS)
        layer = Image.new("RGB", (W, H), PAPER)
        layer.paste(ph, (0, 900 - int(ph.height * 0.27)))
        mask = Image.new("L", (W, H))
        md = ImageDraw.Draw(mask)
        for yy in range(H):
            if yy < 560:
                a = 238
            elif yy < 760:
                a = int(238 - (yy - 560) / 200 * 205)
            elif yy < 1120:
                a = 33
            else:
                a = int(33 + (yy - 1120) / 230 * 200)
            md.line([(0, yy), (W, yy)], fill=a)
        img = Image.composite(img, layer, mask)
        d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=ACC)
    # counter pill (top-left) and kicker pill (top-right)
    t = f"{i}/{n}".translate(AR_DIGITS)
    fc = text_font(30, 700)
    tw = d.textlength(t, font=fc)
    d.rounded_rectangle([M, 60, M + tw + 40, 112], radius=26, fill=WHITE, outline=LINE, width=2)
    d.text((M + 20, 64), t, font=fc, fill=MUTE)
    if s.get("kicker"):
        fk = display(36, 800)
        kw = d.textlength(clean(s["kicker"]), font=fk, direction="rtl")
        d.rounded_rectangle([W - M - kw - 44, 58, W - M, 118], radius=30, fill=ACC)
        d.text((W - M - kw - 22, 62), clean(s["kicker"]), font=fk, fill=WHITE, direction="rtl")
    ft, fb = display(96, 800), text_font(46, 600)
    y = draw_lines(d, wrap(d, s["title"], ft, W - 2 * M), ft, 160, INK, 1.3)
    d.rounded_rectangle([W - M - 160, y + 30, W - M, y + 42], radius=6, fill=ACC)
    yb = y + 42
    if s.get("body"):
        yb = draw_lines(d, wrap(d, s["body"], fb, W - 2 * M), fb, y + 75, BODY, 1.45)
    # swipe hint
    f = display(40, 800)
    hint = "اسحب للشمال"
    hw = d.textlength(hint, font=f, direction="rtl")
    hy = yb + 36
    d.text((W - M - hw, hy), hint, font=f, fill=ACC, direction="rtl")
    x0 = W - M - hw - 90
    ay = hy + 30
    d.line([(x0, ay), (x0 + 55, ay)], fill=ACC, width=6)
    d.polygon([(x0 - 6, ay), (x0 + 18, ay - 16), (x0 + 18, ay + 16)], fill=ACC)
    # centred footer like the original
    fy = H - 150
    d.line([(M, fy), (W - M, fy)], fill=LINE, width=2)
    f1, f2 = text_font(36, 700), text_font(32, 600)
    nw = d.textlength(NAME, font=f1, direction="rtl")
    d.text(((W - nw) / 2, fy + 16), NAME, font=f1, fill=INK, direction="rtl")
    uw = d.textlength(USER, font=f2)
    d.text(((W - uw) / 2, fy + 66), USER, font=f2, fill=ACC)
    return img


def slide_cover(s, i, n):
    lay = s.get("layout") or "classic"
    return {"classic": cover_classic, "face": cover_face, "numeral": cover_numeral, "question": cover_question, "alert": cover_alert}[lay](s, i, n)


# ---------- inner slides ----------
def slide_point(s, i, n):
    if s.get("alert"):
        return slide_redflags(s, i, n)
    img, d = canvas(PAPER)
    if s.get("kicker"):
        badge(d, s["kicker"], ACC)
    mark(d, i, n)
    fn, ft, fb = display(220, 800), display(76, 700), text_font(44, 500)
    tl = wrap(d, s["title"], ft, W - 2 * M)
    bl = wrap(d, s.get("body", ""), fb, W - 2 * M) if s.get("body") else []
    has_num = s.get("num") is not None
    ic = s.get("icon")
    row = 330 if ic else (230 if has_num else 0)
    total = row + text_h(ft, tl, 1.38) + 40 + 6 + (40 + text_h(fb, bl, 1.6) if bl else 0)
    y = vcenter(total, top=170)
    if ic:
        r = 135
        cx = M + r + 22 if has_num else W - M - r - 22
        spot(img, cx, int(y + r + 22), r, ic, s.get("icon2"))
        d = ImageDraw.Draw(img)
    if has_num:
        num = str(s["num"]).translate(AR_DIGITS)
        bb = d.textbbox((0, 0), num, font=fn)
        top_n = y + (row - (bb[3] - bb[1])) / 2 if ic else y
        d.text((W - M - bb[2], top_n - bb[1]), num, font=fn, fill=ACC)
    if ic or has_num:
        y += (row if ic else (d.textbbox((0, 0), str(s["num"]).translate(AR_DIGITS), font=fn)[3] - d.textbbox((0, 0), str(s["num"]).translate(AR_DIGITS), font=fn)[1])) + 50
    y = draw_lines(d, tl, ft, y, INK, 1.38) + 40
    y = acc_line(d, y, ACC)
    if bl:
        draw_lines(d, bl, fb, y + 40, BODY, 1.6)
    footer(d, i, n)
    return img


def slide_redflags(s, i, n):
    img, d = canvas(PAPER)
    red_band(d, s.get("kicker", "الطوارئ فورًا لو"), i, n)
    ft, fi, fb = display(70, 700), text_font(50, 600), text_font(44, 500)
    ic = s.get("icon")
    tl = wrap(d, s.get("title", ""), ft, W - 2 * M - (300 if ic else 0)) if s.get("title") else []
    items = s.get("items") or []
    il = [wrap(d, it, fi, W - 2 * M - 50) for it in items]
    bl = wrap(d, s.get("body", ""), fb, W - 2 * M) if (s.get("body") and not items) else []
    total = (text_h(ft, tl, 1.38) + 56 if tl else 0) + sum(text_h(fi, l, 1.4) + 44 for l in il) + (text_h(fb, bl, 1.6) if bl else 0)
    if ic:
        total += 120
    y = vcenter(total, top=240)
    if ic:
        r = 115
        th = max(text_h(ft, tl, 1.38), 2 * r) if tl else 2 * r
        spot(img, M + r + 22, int(y + th / 2), r, ic, s.get("icon2"), RED)
        d = ImageDraw.Draw(img)
        if tl:
            draw_lines(d, tl, ft, y + (th - text_h(ft, tl, 1.38)) / 2, INK, 1.38)
        y += th + 60
    elif tl:
        y = draw_lines(d, tl, ft, y, INK, 1.38) + 56
    for l in il:
        d.rounded_rectangle([W - M - 20, y + 22, W - M, y + 42], radius=4, fill=RED)
        y = draw_lines(d, l, fi, y, INK, 1.4, right=W - M - 50) + 44
    if bl:
        draw_lines(d, bl, fb, y, BODY, 1.6)
    footer(d, i, n, acc=RED)
    return img


def slide_myth(s, i, n):
    img, d = canvas(PAPER)
    split = int(H * 0.42)
    band(img, [0, 0, W, split], MYTH_BG, 0.9)
    d = ImageDraw.Draw(img)
    mark(d, i, n)
    fl = text_font(32, 700)

    def label(y, txt, col):
        d.ellipse([W - M - 18, y + 14, W - M, y + 32], fill=col)
        tw = d.textlength(txt, font=fl, direction="rtl")
        d.text((W - M - 32 - tw, y), txt, font=fl, fill=col, direction="rtl")
        return y + 60

    fm = display(62, 700)
    ml = wrap(d, s.get("myth", ""), fm, W - 2 * M)
    mh = 60 + text_h(fm, ml, 1.3)
    y = max(150, split - 50 - mh)
    y = label(y, "الخرافة", RED)
    for line in ml:
        tw = d.textlength(line, font=fm, direction="rtl")
        d.text((W - M - tw, y), line, font=fm, fill=MYTH_TXT, direction="rtl")
        bb = d.textbbox((W - M - tw, y), line, font=fm, direction="rtl")
        cy = (bb[1] + bb[3]) // 2 + 4
        d.line([(bb[0], cy), (bb[2], cy)], fill=RED, width=5)
        y += int(fm.size * 1.3)
    y = split + 60
    y = label(y, "الحقيقة", TEAL)
    ft, fb = display(68, 700), text_font(44, 500)
    ic = s.get("icon")
    if ic:
        spot(img, M + 115, split + 150, 100, ic, s.get("icon2"), TEAL)
        d = ImageDraw.Draw(img)
    y = draw_lines(d, wrap(d, s["title"], ft, W - 2 * M - (260 if ic else 0)), ft, y, INK, 1.38) + 30
    if s.get("body"):
        draw_lines(d, wrap(d, s["body"], fb, W - 2 * M), fb, y, BODY, 1.6)
    footer(d, i, n)
    return img


def slide_answer(s, i, n):
    img, d = canvas(PAPER)
    ok = s.get("verdict", "صح") == "صح"
    col, bg = (TEAL, TINT) if ok else (RED, RED_TINT)
    if s.get("kicker"):
        badge(d, s["kicker"], ACC)
    mark(d, i, n)
    fv, ft, fb = display(64, 800), display(72, 700), text_font(44, 500)
    tl = wrap(d, s["title"], ft, W - 2 * M)
    bl = wrap(d, s.get("body", ""), fb, W - 2 * M) if s.get("body") else []
    total = 130 + 50 + text_h(ft, tl, 1.38) + (36 + text_h(fb, bl, 1.6) if bl else 0)
    y = vcenter(total, top=180)
    if s.get("icon"):
        spot(img, M + 120, int(y + 60), 105, s["icon"], s.get("icon2"), col)
        d = ImageDraw.Draw(img)
    v = "الإجابة: " + s.get("verdict", "صح")
    tw = d.textlength(v, font=fv, direction="rtl")
    d.rounded_rectangle([W - M - tw - 70, y, W - M, y + 120], radius=20, fill=bg)
    d.text((W - M - 35 - tw, y + 18), v, font=fv, fill=col, direction="rtl")
    y += 170
    y = draw_lines(d, tl, ft, y, INK, 1.38)
    if bl:
        draw_lines(d, bl, fb, y + 36, BODY, 1.6)
    footer(d, i, n)
    return img


def slide_data(s, i, n):
    img, d = canvas(PAPER)
    badge(d, s.get("kicker", "بالأرقام"), ACC)
    mark(d, i, n)
    ft, fl = display(72, 700), text_font(36, 600)
    ic = s.get("icon")
    tl = wrap(d, s["title"], ft, W - 2 * M - (260 if ic else 0))
    bars = s.get("bars", [])
    th = max(text_h(ft, tl, 1.38), 220 if ic else 0)
    total = th + 70 + len(bars) * 140 + 60
    y = vcenter(total, top=180)
    if ic:
        spot(img, M + 112, int(y + th / 2), 95, ic, s.get("icon2"))
        d = ImageDraw.Draw(img)
    draw_lines(d, tl, ft, y + (th - text_h(ft, tl, 1.38)) / 2, INK, 1.38)
    y += th + 70
    for b in bars:
        lab, val = clean(b.get("label", "")), clean(str(b.get("value", ""))).translate(AR_DIGITS)
        tw = d.textlength(lab, font=fl, direction="rtl")
        d.text((W - M - tw, y), lab, font=fl, fill=INK, direction="rtl")
        d.text((M, y), val, font=fl, fill=INK, direction="rtl")
        y += 60
        d.rounded_rectangle([M, y, W - M, y + 48], radius=10, fill=(227, 233, 231))
        pw = max(48, (W - 2 * M) * float(b.get("pct", 50)) / 100)
        d.rounded_rectangle([W - M - pw, y, W - M, y + 48], radius=10, fill=(ACC if b.get("hi") else (157, 179, 176)))
        y += 80
    src = s.get("source")
    if src:
        f = text_font(28, 600)
        line = "المصدر: " + src
        tw = d.textlength(line, font=f, direction="rtl")
        d.text((W - M - tw, y + 10), line, font=f, fill=MUTE, direction="rtl")
    footer(d, i, n)
    return img


def slide_checklist(s, i, n):
    img, d = canvas(TINT)
    badge(d, s.get("kicker", "احفظها"), ACC)
    mark(d, i, n)
    ft, fi = display(72, 700), text_font(42, 600)
    ic = s.get("icon")
    tl = wrap(d, s.get("title", "الخلاصة في صورة واحدة"), ft, W - 2 * M - (190 if ic else 0))
    rows = [wrap(d, it, fi, W - 2 * M - 140) for it in s.get("items", [])]
    rh = [text_h(fi, r, 1.4) + 52 for r in rows]
    th = max(text_h(ft, tl, 1.38), 160 if ic else 0)
    total = th + 50 + sum(rh) + 22 * (len(rows) - 1)
    y = vcenter(total, top=180)
    if ic:
        spot(img, M + 82, int(y + th / 2), 66, ic, None, ACC, TINT)
        d = ImageDraw.Draw(img)
    draw_lines(d, tl, ft, y + (th - text_h(ft, tl, 1.38)) / 2, INK, 1.38)
    y += th + 50
    for r, h in zip(rows, rh):
        if y + h > H - FOOT - 10:
            break
        d.rounded_rectangle([M, y, W - M, y + h], radius=18, fill=WHITE)
        cx, cy = W - M - 58, y + h / 2
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=ACC)
        d.line([(cx - 12, cy + 1), (cx - 3, cy + 10), (cx + 13, cy - 9)], fill=WHITE, width=7, joint="curve")
        bb = d.textbbox((0, 0), "علامة", font=fi, direction="rtl")
        ink_h = (len(r) - 1) * int(fi.size * 1.4) + (bb[3] - bb[1])
        draw_lines(d, r, fi, y + (h - ink_h) / 2 - bb[1], INK, 1.4, right=W - M - 112)
        y += h + 22
    footer(d, i, n)
    return img


def slide_cta(s, i, n):
    img, d = canvas(INK)
    mark(d, i, n, MUTE_ON_INK)
    avatar(img, W - M - 110, 300, 104, MINT)
    d = ImageDraw.Draw(img)
    ft, fb, ff = display(76, 700), text_font(44, 500), text_font(44, 700)
    y = 470
    y = draw_lines(d, wrap(d, s["title"], ft, W - 2 * M), ft, y, WHITE, 1.38) + 34
    if s.get("body"):
        y = draw_lines(d, wrap(d, s["body"], fb, W - 2 * M), fb, y, BODY_ON_INK, 1.55) + 40
    y = acc_line(d, y, MINT) + 40
    y = draw_lines(d, ["تابعني عشان معلومة طبية كل يوم"], ff, y, WHITE, 1.4) + 30
    if s.get("source"):
        f = text_font(28, 600)
        draw_lines(d, wrap(d, "المصدر: " + s["source"], f, W - 2 * M), f, y, MUTE_ON_INK, 1.4)
    footer(d, i, n, dark=True, label=USER, acc=MINT)
    return img


TYPES = {"cover": slide_cover, "point": slide_point, "redflags": slide_redflags, "myth": slide_myth,
         "answer": slide_answer, "data": slide_data, "checklist": slide_checklist, "cta": slide_cta}


def main(spec_path, outdir):
    global ACC, ACC_INK, SER_LABEL, BLUE
    spec = json.load(open(spec_path, encoding="utf-8"))
    ser = os.environ.get("POST_SERIES") or spec.get("series") or spec.get("audience") or "general"
    ACC, ACC_INK, SER_LABEL = SERIES.get(ser, SERIES["general"])
    BLUE = ACC
    os.makedirs(outdir, exist_ok=True)
    slides = spec["slides"]
    n = len(slides)
    paths = []
    for i, s in enumerate(slides, 1):
        if s["type"] == "cta" and spec.get("source") and "source" not in s:
            s = dict(s, source=spec["source"])
        img = TYPES[s["type"]](s, i, n)
        p = os.path.join(outdir, f"slide_{i:02d}.jpg")
        img.convert("RGB").save(p, "JPEG", quality=92, optimize=True)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
