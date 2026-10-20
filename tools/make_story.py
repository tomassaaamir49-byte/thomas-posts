"""Story image (1080x1920 JPG) that promotes a carousel post.

Puts the carousel cover on a blurred, darkened copy of itself, with a
"بوست جديد" badge on top and "شوفه على البروفايل" + name/username under it.

usage: POST_THEME=<theme> python3 make_story.py posts/<date>-am/slide_01.jpg posts/<date>-am/story.jpg
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_carousel as mc

W, H = 1080, 1920


def main(cover_path, out_path):
    cover = Image.open(cover_path).convert("RGB")
    bg = cover.resize((W, int(cover.height * W / cover.width))).resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.45)
    img = bg.copy()
    d = ImageDraw.Draw(img)
    # card
    cw = 820
    card = cover.resize((cw, int(cover.height * cw / cover.width)), Image.LANCZOS)
    cx, cy = (W - cw) // 2, 330
    shadow = Image.new("RGBA", (cw + 80, card.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([40, 40, cw + 40, card.height + 40], radius=40, fill=(0, 0, 0, 150))
    img.paste(shadow.filter(ImageFilter.GaussianBlur(25)), (cx - 40, cy - 20), shadow.filter(ImageFilter.GaussianBlur(25)))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width, card.height], radius=36, fill=255)
    img.paste(card, (cx, cy), mask)
    # badge
    f = mc.font(48, 900)
    t = "بوست جديد"
    tw = d.textlength(t, font=f, direction="rtl")
    bw, bh = tw + 90, 92
    bx = (W - bw) / 2
    d.rounded_rectangle([bx, 190, bx + bw, 190 + bh], radius=46, fill=mc.BLUE)
    d.text(((W - tw) / 2, 196), t, font=f, fill=(255, 255, 255), direction="rtl")
    # call to action
    y = cy + card.height + 70
    f2 = mc.font(56, 900)
    t2 = "شوفه على البروفايل"
    tw = d.textlength(t2, font=f2, direction="rtl")
    d.text(((W - tw) / 2, y), t2, font=f2, fill=(255, 255, 255), direction="rtl")
    f3, f4 = mc.font(38, 700), mc.font(34, 600)
    tw = d.textlength(mc.NAME, font=f3, direction="rtl")
    d.text(((W - tw) / 2, y + 100), mc.NAME, font=f3, fill=(235, 235, 235), direction="rtl")
    tw = d.textlength(mc.USER, font=f4)
    d.text(((W - tw) / 2, y + 156), mc.USER, font=f4, fill=(210, 220, 235))
    img.save(out_path, "JPEG", quality=92)
    print(out_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
