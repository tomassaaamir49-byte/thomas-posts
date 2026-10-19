"""Builds a silent ~30s vertical Instagram reel (1080x1920 MP4) from a JSON spec.

Each scene is a full-screen text card that stays on screen 3-4 seconds, with a
gentle zoom so the frame is never static. Name + username stay on screen.

usage: python3 make_reel.py spec.json out_dir
spec: {"scenes": [{"text": "...", "big": "optional big line", "alert": true, "secs": 3.5}, ...],
       "cover": {"title": "...", "sub": "..."}}
"""
import json, os, re, sys, subprocess, tempfile
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_carousel as mc

W, H = 1080, 1920
FPS = 30


def bg(accent):
    img = Image.new("RGB", (W, H), mc.WHITE)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(mc.WHITE[i] * (1 - t) + mc.SKY[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    d.ellipse([W - 300, -240, W + 240, 300], fill=(214, 232, 255))
    d.ellipse([-220, H - 640, 260, H - 160], fill=(222, 237, 255))
    d.rectangle([0, 0, W, 16], fill=accent)
    return img, d


def centered(d, text, f, y, color, maxw=W - 2 * mc.M, gap=1.35):
    lh = int(f.size * gap)
    for line in mc.wrap(d, text, f, maxw):
        tw = d.textlength(line, font=f, direction="rtl")
        d.text(((W - tw) / 2, y), line, font=f, fill=color, direction="rtl")
        y += lh
    return y


def footer(d):
    y = H - 260
    d.line([(mc.M, y), (W - mc.M, y)], fill=(200, 215, 235), width=2)
    f1, f2 = mc.font(40, 700), mc.font(36, 600)
    tw = d.textlength(mc.NAME, font=f1, direction="rtl")
    d.text(((W - tw) / 2, y + 24), mc.NAME, font=f1, fill=mc.NAVY, direction="rtl")
    tw = d.textlength(mc.USER, font=f2)
    d.text(((W - tw) / 2, y + 82), mc.USER, font=f2, fill=mc.BLUE)


_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]+")


def clean(t):
    """The Arabic font has no emoji glyphs, so strip them from on-screen text."""
    return re.sub(r"[ \t]+\n", "\n", _EMOJI.sub("", t or "")).strip()


def scene_img(s, i, n):
    accent = mc.RED if s.get("alert") else mc.BLUE
    img, d = bg(accent)
    # progress dots
    dot = 18
    total = n * (dot + 14) - 14
    x = (W - total) / 2
    for k in range(n):
        col = accent if (n - 1 - k) <= i else (205, 220, 240)  # fills right-to-left
        d.ellipse([x, 90, x + dot, 90 + dot], fill=col)
        x += dot + 14
    fb, ft = mc.font(118, 900), mc.font(64, 700)
    big, text = clean(s.get("big")), clean(s.get("text", ""))
    hb = mc.block_height(d, big, fb, gap=1.25) if big else 0
    ht = mc.block_height(d, text, ft, gap=1.4) if text else 0
    y = (H - 260 - hb - ht - (50 if big and text else 0)) / 2
    if big:
        y = centered(d, big, fb, y, accent if s.get("alert") else mc.NAVY, gap=1.25)
        y += 50
    if text:
        centered(d, text, ft, y, mc.NAVY, gap=1.4)
    footer(d)
    return img


def main(spec_path, outdir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    scenes = spec["scenes"]
    tmp = tempfile.mkdtemp()
    parts = []
    for i, s in enumerate(scenes):
        p = os.path.join(tmp, f"s{i:02d}.png")
        scene_img(s, i, len(scenes)).save(p)
        secs = float(s.get("secs", 3.5))
        frames = int(secs * FPS)
        out = os.path.join(tmp, f"s{i:02d}.mp4")
        # slow zoom-in, quick fade in/out between scenes
        vf = (f"scale=2160:-1,zoompan=z='min(1.0+0.0007*on,1.06)':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
              f"fade=t=in:st=0:d=0.25,fade=t=out:st={secs - 0.25}:d=0.25,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", p, "-vf", vf,
                        "-t", str(secs), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                        "-r", str(FPS), out], check=True)
        parts.append(out)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    video = os.path.join(outdir, "reel.mp4")
    # Instagram wants an audio track to exist; add silent AAC
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "64k", "-shortest",
                    "-movflags", "+faststart", video], check=True)
    # cover image = first scene
    cover = os.path.join(outdir, "cover.jpg")
    scene_img(scenes[0], 0, len(scenes)).convert("RGB").save(cover, "JPEG", quality=92)
    print(video)
    print(cover)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
