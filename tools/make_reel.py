"""Motion-graphics reel (1080x1920, ~30 s, 30 fps) from a JSON spec.

Every scene animates in: an icon badge pops in with a pulsing ring, the title
lines slide in from the right one after another, an accent bar grows under
them, the body lines rise and fade in, then everything fades out. Behind it,
soft blobs drift, a heartbeat line scrolls along the bottom and a progress bar
fills across the top. Name + username stay on screen. Original background
music (make_music.py) is mixed in.

usage: python3 make_reel.py spec.json out_dir
spec: {"scenes": [{"big": "title", "text": "body", "icon": "flame",
                   "kind": "hook|do|dont|alert|info|cta", "alert": true, "secs": 3.5}, ...],
       "source": "optional source name (printed on the last scene)"}
`icon` is a file name (without .svg) from assets/icons. `kind` is optional and
is guessed from the text (الصح / الغلط / ✅ / ❌) when missing.
"""
import io, json, math, os, re, subprocess, sys, tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_carousel as mc  # fonts, colours, wrap(), NAME, USER

ICONS = os.path.join(HERE, "..", "assets", "icons")
W, H = 1080, 1920
FPS = 30

BLUE = mc.BLUE
RED = mc.RED
GREEN = (34, 154, 92)
NAVY = mc.NAVY
INK = mc.INK
MUTED = mc.MUTED

KIND_COLOR = {"hook": BLUE, "do": GREEN, "dont": RED, "alert": RED, "info": BLUE, "cta": BLUE}
KIND_ICON = {"hook": "alert-circle", "do": "circle-check", "dont": "circle-x", "alert": "alert-triangle",
             "info": "bulb", "cta": "share"}

_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")


def clean(t):
    return re.sub(r"[ \t]+\n", "\n", _EMOJI.sub("", t or "")).strip()


def guess_kind(s, i, n):
    if s.get("kind"):
        return s["kind"]
    raw = (s.get("big") or "") + (s.get("text") or "")
    if i == n - 1:
        return "cta"
    if i == 0:
        return "hook"
    if "✅" in raw or "الصح" in raw:
        return "do"
    if "❌" in raw or "الغلط" in raw:
        return "dont"
    if i == 0:
        return "hook"
    return "alert" if s.get("alert") else "info"


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.9):
    x = clamp(x)
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def icon_img(name, size, color=(255, 255, 255)):
    import cairosvg
    path = os.path.join(ICONS, f"{name}.svg")
    if not os.path.exists(path):
        path = os.path.join(ICONS, "info-circle.svg")
    svg = open(path, encoding="utf-8").read()
    svg = svg.replace("currentColor", "#%02x%02x%02x" % color).replace('stroke-width="2"', 'stroke-width="1.7"')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def text_layer(text, f, color):
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = int(d.textlength(text, font=f, direction="rtl")) + 8
    im = Image.new("RGBA", (tw, int(f.size * 1.5)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 0), text, font=f, fill=color + (255,), direction="rtl")
    return im


def lines(text, f, maxw):
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    return [l for l in mc.wrap(d, text, f, maxw) if l.strip()]


def with_alpha(im, a):
    if a >= 0.999:
        return im
    r, g, b, al = im.split()
    return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))


def base_background():
    t = (np.arange(H) / H)[:, None, None]
    arr = np.array(mc.WHITE) * (1 - t) + np.array(mc.SKY) * t
    arr = np.broadcast_to(arr, (H, W, 3))
    return Image.fromarray(arr.astype("uint8")).convert("RGBA")


def blob(radius, color, alpha=130):
    s = radius * 2 + 160
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse([80, 80, s - 80, s - 80], fill=alpha)
    im = Image.new("RGBA", (s, s), color + (0,))
    im.putalpha(mask.filter(ImageFilter.GaussianBlur(55)))  # blur alpha only: no dark halo
    return im


def ecg_strip(color=(170, 196, 235), width=W * 2, height=160):
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pts, base, period = [], height * 0.6, 360
    for x in range(0, width + 1, 3):
        ph = (x % period) / period
        y = base
        if 0.40 < ph < 0.44:
            y -= (ph - 0.40) / 0.04 * 25
        elif 0.44 < ph < 0.47:
            y -= 25 - (ph - 0.44) / 0.03 * 110
        elif 0.47 < ph < 0.50:
            y += 85 - (ph - 0.47) / 0.03 * 85
        elif 0.58 < ph < 0.66:
            y -= math.sin((ph - 0.58) / 0.08 * math.pi) * 18
        pts.append((x, y))
    ImageDraw.Draw(im).line(pts, fill=color + (255,), width=5, joint="curve")
    return im


def footer_layer():
    im = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(mc.M, 0), (W - mc.M, 0)], fill=(200, 215, 235, 255), width=2)
    f1, f2 = mc.font(40, 700), mc.font(36, 600)
    tw = d.textlength(mc.NAME, font=f1, direction="rtl")
    d.text(((W - tw) / 2, 24), mc.NAME, font=f1, fill=NAVY + (255,), direction="rtl")
    tw = d.textlength(mc.USER, font=f2)
    d.text(((W - tw) / 2, 82), mc.USER, font=f2, fill=BLUE + (255,))
    return im


class Scene:
    def __init__(self, s, i, n):
        self.secs = float(s.get("secs", 3.5))
        self.kind = guess_kind(s, i, n)
        self.color = KIND_COLOR.get(self.kind, BLUE)
        if s.get("alert") and self.kind in ("hook", "info"):
            self.color = RED
        self.badge_r = 120
        self.icon = icon_img(s.get("icon") or KIND_ICON.get(self.kind, "info-circle"), 150)
        big, text = clean(s.get("big")), clean(s.get("text"))
        ft = mc.font(104 if self.kind == "hook" else 92, 900)
        fb = mc.font(58, 700)
        title_col = self.color if self.kind in ("hook", "dont", "alert") else NAVY
        self.title = [text_layer(l, ft, title_col) for l in lines(big, ft, W - 2 * mc.M)] if big else []
        self.body = [text_layer(l, fb, INK) for l in lines(text, fb, W - 2 * mc.M - 40)] if text else []
        self.t_lh, self.b_lh = int(ft.size * 1.25), int(fb.size * 1.45)
        self.cta = self.kind == "cta"
        self.cta_icons = [icon_img(n, 84, self.color) for n in ("send", "bookmark", "user-plus")] if self.cta else []
        self.cta_labels = [text_layer(t, mc.font(34, 700), NAVY) for t in ("ابعته", "احفظه", "تابعني")] if self.cta else []
        self.source = clean(s.get("source"))
        total = 2 * self.badge_r + 60 + len(self.title) * self.t_lh + (100 if self.body else 70) \
            + len(self.body) * self.b_lh + (210 if self.cta else 0)
        top, bottom = 200, H - 340
        self.y0 = top + max(0, (bottom - top - total) / 2)

    def draw(self, frame, t):
        out_a = 1.0 - clamp((t - (self.secs - 0.28)) / 0.28)
        y, cx = self.y0, W / 2
        k = ease_out_back(t / 0.45)
        r = self.badge_r * k
        if t > 0.35:
            ph = ((t - 0.35) % 1.2) / 1.2
            rr = self.badge_r * (1 + 0.55 * ph)
            ring = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse([cx - rr, y + self.badge_r - rr, cx + rr, y + self.badge_r + rr],
                                         outline=self.color + (int(150 * (1 - ph) * out_a),), width=6)
            frame.alpha_composite(ring)
        if r > 2:
            badge = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            ImageDraw.Draw(badge).ellipse([cx - r, y + self.badge_r - r, cx + r, y + self.badge_r + r],
                                          fill=self.color + (int(255 * out_a),))
            frame.alpha_composite(badge)
            isz = max(1, int(self.icon.width * k))
            frame.alpha_composite(with_alpha(self.icon.resize((isz, isz), Image.LANCZOS), out_a),
                                  (int(cx - isz / 2), int(y + self.badge_r - isz / 2)))
        y += 2 * self.badge_r + 60
        for i, im in enumerate(self.title):
            p = ease_out_cubic((t - 0.18 - i * 0.12) / 0.4)
            if p > 0:
                x = (W - im.width) / 2 + (1 - p) * 120
                frame.alpha_composite(with_alpha(im, p * out_a), (int(x), int(y + i * self.t_lh)))
        y += len(self.title) * self.t_lh
        if self.title:
            g = ease_out_cubic((t - 0.45) / 0.4)
            if g > 0:
                bar = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                ImageDraw.Draw(bar).rounded_rectangle([cx - 90 * g, y + 58, cx + 90 * g, y + 70], radius=6,
                                                      fill=self.color + (int(255 * out_a),))
                frame.alpha_composite(bar)
        y += 100 if self.body else 70
        for i, im in enumerate(self.body):
            p = ease_out_cubic((t - 0.55 - i * 0.12) / 0.45)
            if p > 0:
                frame.alpha_composite(with_alpha(im, p * out_a),
                                      (int((W - im.width) / 2), int(y + i * self.b_lh + (1 - p) * 50)))
        y += len(self.body) * self.b_lh
        if self.cta:
            y += 50
            n, gap = len(self.cta_icons), 260
            xs = [cx + (j - (n - 1) / 2) * gap for j in range(n)][::-1]
            for j, (ic, lb) in enumerate(zip(self.cta_icons, self.cta_labels)):
                k2 = ease_out_back((t - 0.9 - j * 0.18) / 0.4)
                if k2 <= 0:
                    continue
                rr = 62 * k2
                c = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                ImageDraw.Draw(c).ellipse([xs[j] - rr, y + 62 - rr, xs[j] + rr, y + 62 + rr],
                                          fill=(255, 255, 255, int(255 * out_a)),
                                          outline=self.color + (int(255 * out_a),), width=4)
                frame.alpha_composite(c)
                sz = max(1, int(ic.width * k2 * 0.75))
                frame.alpha_composite(with_alpha(ic.resize((sz, sz), Image.LANCZOS), out_a),
                                      (int(xs[j] - sz / 2), int(y + 62 - sz / 2)))
                frame.alpha_composite(with_alpha(lb, clamp(k2) * out_a), (int(xs[j] - lb.width / 2), int(y + 140)))
        if self.source:
            sl = text_layer("المصدر: " + self.source, mc.font(32, 600), MUTED)
            frame.alpha_composite(with_alpha(sl, clamp((t - 1.0) / 0.4) * out_a), (int((W - sl.width) / 2), H - 320))


def main(spec_path, outdir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    raw = spec["scenes"]
    if spec.get("source"):
        raw[-1] = dict(raw[-1], source=spec["source"])
    scenes = [Scene(s, i, len(raw)) for i, s in enumerate(raw)]
    total = sum(s.secs for s in scenes)
    nframes = int(round(total * FPS))

    bg = base_background()
    tint = lambda k: tuple(int(mc.SKY[i] * (1 - k) + BLUE[i] * k) for i in range(3))
    blobs = [(blob(260, tint(0.18)), 0.13, 0.10, 0.0), (blob(220, tint(0.10)), 0.85, 0.78, 2.0),
             (blob(180, tint(0.14)), 0.15, 0.62, 4.0)]
    ecg = ecg_strip(tuple(int(mc.SKY[i] * 0.55 + BLUE[i] * 0.45) for i in range(3)))
    foot = footer_layer()

    tmp = tempfile.mkdtemp()
    silent = os.path.join(tmp, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    starts = np.cumsum([0] + [s.secs for s in scenes])
    cover, rgb = None, None
    for fi in range(nframes):
        T = fi / FPS
        si = min(int(np.searchsorted(starts, T, side="right") - 1), len(scenes) - 1)
        sc, t = scenes[si], T - starts[si]
        fr = bg.copy()
        for b, bx, by, ph in blobs:
            fr.alpha_composite(b, (int(W * bx + math.sin(T * 0.6 + ph) * 60 - b.width / 2),
                                   int(H * by + math.cos(T * 0.5 + ph) * 50 - b.height / 2)))
        off = int((T * 220) % (ecg.width / 2))
        fr.alpha_composite(ecg.crop((off, 0, off + W, ecg.height)), (0, H - 470))
        sc.draw(fr, t)
        d = ImageDraw.Draw(fr)
        d.rectangle([0, 0, W, 14], fill=(220, 230, 245, 255))
        d.rectangle([W - int(W * (T / total)), 0, W, 14], fill=sc.color + (255,))
        fr.alpha_composite(foot, (0, H - 260))
        rgb = fr.convert("RGB")
        if si == 0 and cover is None and t >= sc.secs - 0.4:
            cover = rgb.copy()
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")

    import make_music
    from scipy.io import wavfile
    seed = sum(ord(c) for c in os.path.basename(os.path.normpath(outdir)))
    wav = os.path.join(tmp, "music.wav")
    wavfile.write(wav, make_music.SR, make_music.make(total + 0.5, seed))
    video = os.path.join(outdir, "reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", video], check=True)
    (cover or rgb).save(os.path.join(outdir, "cover.jpg"), "JPEG", quality=92)
    print(video)
    print(os.path.join(outdir, "cover.jpg"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
