"""Story image (1080x1920 JPG) that teases a carousel and sends people to the profile.

Layout: an arrow + "اضغط على اسمي" pointing at the profile name (top-left in
Instagram/Facebook stories), a "بوست جديد" badge, the carousel cover as a card,
then a teaser line (curiosity hook) and "البوست كامل على البروفايل".

usage: POST_THEME=<theme> python3 make_story.py <cover.jpg> <out.jpg> "<teaser>"
The teaser should create curiosity without giving the answer, e.g.
"٦ علامات لازم كل أم وأب يعرفوها" or "خرافة رقم ٤ أغلبنا مصدقها".
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_carousel as mc

W, H = 1080, 1920


def centered(d, text, f, y, fill, maxw=W - 140):
    for line in mc.wrap(d, text, f, maxw):
        tw = d.textlength(line, font=f, direction="rtl")
        d.text(((W - tw) / 2, y), line, font=f, fill=fill, direction="rtl")
        y += int(f.size * 1.35)
    return y


def main(cover_path, out_path, teaser="الباقي هتلاقيه في البوست"):
    cover = Image.open(cover_path).convert("RGB")
    bg = cover.resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(45))).enhance(0.4)
    img = bg.copy()
    d = ImageDraw.Draw(img)

    # arrow pointing at the profile name (top-left of a story)
    fa = mc.font(38, 800)
    hint = "اضغط على اسمي"
    d.line([(150, 250), (115, 175)], fill=(255, 255, 255), width=8)
    d.polygon([(95, 150), (140, 168), (100, 196)], fill=(255, 255, 255))
    d.text((175, 238), hint, font=fa, fill=(255, 255, 255), direction="rtl")

    # badge
    f = mc.font(46, 900)
    t = "بوست جديد"
    tw = d.textlength(t, font=f, direction="rtl")
    bw = tw + 90
    bx = (W - bw) / 2
    d.rounded_rectangle([bx, 330, bx + bw, 420], radius=45, fill=mc.BLUE)
    d.text(((W - tw) / 2, 336), t, font=f, fill=(255, 255, 255), direction="rtl")

    # cover card
    cw = 760
    card = cover.resize((cw, int(cover.height * cw / cover.width)), Image.LANCZOS)
    cx, cy = (W - cw) // 2, 460
    sh = Image.new("RGBA", (cw + 100, card.height + 100), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([50, 50, cw + 50, card.height + 50], radius=40, fill=(0, 0, 0, 160))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    img.paste(sh, (cx - 50, cy - 30), sh)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width, card.height], radius=34, fill=255)
    img.paste(card, (cx, cy), mask)

    # teaser + call to action
    y = cy + card.height + 60
    y = centered(d, teaser, mc.font(58, 900), y, (255, 255, 255))
    y += 10
    cta = "البوست كامل على البروفايل"
    fc = mc.font(44, 800)
    tw = d.textlength(cta, font=fc, direction="rtl")
    pw = tw + 80
    px = (W - pw) / 2
    d.rounded_rectangle([px, y, px + pw, y + 84], radius=42, fill=(255, 255, 255))
    d.text(((W - tw) / 2, y + 8), cta, font=fc, fill=mc.NAVY, direction="rtl")
    f4 = mc.font(32, 600)
    tw = d.textlength(mc.USER, font=f4)
    d.text(((W - tw) / 2, y + 112), mc.USER, font=f4, fill=(215, 225, 240))
    img.save(out_path, "JPEG", quality=92)
    print(out_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "الباقي هتلاقيه في البوست")
