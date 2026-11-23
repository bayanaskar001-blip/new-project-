"""Kinetic-typography intro in the @cookisha_ template style, 1080x1920 @30fps.
Usage: python3 render.py <out.mp4> [start_s end_s]  (range = preview render)"""
import json, math, subprocess, sys, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
BG = (246, 244, 247)
RED = (214, 18, 46)
INK = (20, 20, 22)
WHITE = (255, 255, 255)
DARK = (58, 58, 60)
UP = "/root/.claude/uploads/72d83ebe-2a17-52b5-8f9f-dcdf689494a5/"
import os
B = os.path.dirname(os.path.abspath(__file__)) + "/"
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_SMALL = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

PH = {k: Image.open(UP + v).convert("RGB") for k, v in {
    "read": "e4f536ec-image.jpg", "book": "e58bf32c-image.jpg", "kitchen": "acafdf5f-image.jpg",
    "laptop": "f87c14d0-image.jpg", "counter": "3d80ca09-image.jpg", "pizza": "d6e6f985-image.jpg",
    "studio": "1ab7ea95-image.jpg", "tea": "0428ee83-image.jpg", "tether": "1cb0695a-image.jpg",
    "bag": "4379cbad-image.jpg", "lookbook": "81c72a33-image.jpg", "cat": "2e81a2dc-image.jpg", "case": "a48e47dc-image.jpg"}.items()}
PH = {k: ImageOps.exif_transpose(v) for k, v in PH.items()}

WORDS = json.load(open(B + "words.json"))
def ws(i): return WORDS[i][1]          # word start time
VOICE_END = WORDS[-1][2] + 0.8
TOTAL = VOICE_END + 3.2

# ---------- clip frames ----------
def load_clip():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", UP + "13efae5d-copy_6FFC01B9-3FF3-4ECF-B04F-4C02811666C2.mov",
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return [Image.frombuffer("RGB", (W, H), raw[i*W*H*3:(i+1)*W*H*3]) for i in range(n)]
CLIP = load_clip()

# ---------- helpers ----------
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back_out(x, s=1.7):
    x = min(max(x, 0), 1); x -= 1; return x * x * ((s + 1) * x + s) + 1

@functools.lru_cache(maxsize=512)
def text_layer(txt, size, color, font=F_BLACK, squeeze=0.84, track=-0.055):
    """Render tight, horizontally-condensed text to an RGBA layer."""
    f = ImageFont.truetype(font, size)
    tr = int(size * track)
    widths = [f.getlength(c) for c in txt]
    w = int(sum(widths) + tr * (len(txt) - 1) + size)
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (w, asc + desc + size // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = size // 2
    for c, cw in zip(txt, widths):
        d.text((x, size // 8), c, font=f, fill=color + (255,))
        x += cw + tr
    img = img.crop(img.getbbox())
    if squeeze != 1:
        img = img.resize((max(1, int(img.width * squeeze)), img.height), Image.LANCZOS)
    return img

def small(txt, size=40, color=INK):
    return text_layer(txt, size, color, F_SMALL, 1.0, -0.01)

def fit_text(txt, max_w, size, color=RED):
    lay = text_layer(txt, size, color)
    if lay.width > max_w:
        lay = text_layer(txt, int(size * max_w / lay.width), color)
    return lay

def paste_c(canvas, layer, cx, cy, scale=1.0, alpha=1.0, rot=0.0, blur=0.0):
    if layer is None or alpha <= 0: return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width*scale)), max(1, int(layer.height*scale))), Image.BILINEAR)
    if rot: layer = layer.rotate(rot, Image.BICUBIC, expand=True)
    if blur > 0.3: layer = layer.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer = layer.copy(); layer.putalpha(a)
    canvas.alpha_composite(layer, (int(cx - layer.width/2), int(cy - layer.height/2)))

EVENTS = set()

def pop(canvas, layer, cx, cy, t, t0, rot=0.0, blur_in=True, dur=0.16):
    if t >= t0: EVENTS.add(("pop", round(t0, 3)))
    """Template-style word entrance: scale down from 1.25 with a quick blur."""
    if t < t0: return
    k = ease_out((t - t0) / dur)
    paste_c(canvas, layer, cx, cy, 1.25 - 0.25*k, min(1, 0.2 + k), rot, (1-k)*14 if blur_in else 0)

@functools.lru_cache(maxsize=64)
def card(name, w, h, radius=34):
    src = PH[name] if name in PH else name
    im = ImageOps.fit(src, (w, h), Image.LANCZOS, centering=(0.5, 0.45)).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w-1, h-1), radius, fill=255)
    im.putalpha(m)
    pad = 40
    out = Image.new("RGBA", (w + pad*2, h + pad*2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad+14, pad+w, pad+h+14), radius, fill=(0, 0, 0, 70))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(im, (pad, pad))
    return out

def card_in(canvas, name, w, h, cx, cy, t, t0, rot=0.0, dur=0.28):
    if t >= t0: EVENTS.add(("whoosh", round(t0 - 0.12, 3)))
    if t < t0: return
    k = back_out((t - t0) / dur)
    paste_c(canvas, card(name, w, h), cx, cy, 0.55 + 0.45*k, min(1, (t-t0)/0.08), rot)

@functools.lru_cache(maxsize=16)
def _base(name, focus):
    return ImageOps.fit(PH[name], (int(W*1.08), int(H*1.08)), Image.LANCZOS, centering=focus)
def _zoom(name, focus, z):
    b = _base(name, focus)
    cw, ch = int(b.width / z), int(b.height / z)
    l, tp = (b.width - cw)//2, (b.height - ch)//2
    return b.crop((l, tp, l+cw, tp+ch)).resize((W, H), Image.BILINEAR)

def darken(img, a=0.22):
    return Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), a)

# ---------- watermark / icon ----------
@functools.lru_cache(maxsize=8)
def ig_icon(size, color, gradient=False):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lw = int(s * 0.085)
    d.rounded_rectangle((lw, lw, s-lw, s-lw), int(s*0.28), outline=color+(255,), width=lw)
    r = s * 0.22; c = s/2
    d.ellipse((c-r, c-r, c+r, c+r), outline=color+(255,), width=lw)
    d.ellipse((s*0.70, s*0.21, s*0.79, s*0.30), fill=color+(255,))
    if gradient:
        g = Image.new("RGBA", (s, s))
        gp = g.load()
        for y in range(s):
            for x in range(0, s):
                u = (x + (s - y)) / (2*s)
                a, b_, cc = (254, 218, 117), (214, 41, 118), (79, 91, 213)
                if u < 0.5: k = u/0.5; col = tuple(int(a[i]+(b_[i]-a[i])*k) for i in range(3))
                else: k = (u-0.5)/0.5; col = tuple(int(b_[i]+(cc[i]-b_[i])*k) for i in range(3))
                gp[x, y] = col + (255,)
        g.putalpha(im.getchannel("A")); im = g
    return im.resize((size, size), Image.LANCZOS)

def watermark(canvas, on_photo):
    col = WHITE if on_photo else (200, 198, 204)
    paste_c(canvas, ig_icon(46, col), W - 120, 150)
    paste_c(canvas, small("@BAYANA_ASKAR", 20, col), W - 120, 196)

# ---------- scenes ----------
def scenes():
    S = []
    def add(t0, fn, photo=False): S.append((t0, fn, photo))
    def acc(c, pairs, y, size=46, color=INK, t=0):
        txt = " ".join(w for w, i in pairs if t >= ws(i))
        if txt: paste_c(c, small(txt, size, color), W/2, y)

    def meme(c, t, txt, y, t0, x=W/2, color=(95, 95, 100), size=42):
        pop(c, small(txt, size, color), x, y, t, t0, dur=0.14)

    # 1. привет
    def s1(c, t):
        card_in(c, "read", 520, 700, 400, 700, t, 0.0, rot=9)
        pop(c, fit_text("привет,", 900, 230), 600, 1250, t, ws(0))
    add(0.0, s1)

    # 2. меня зовут БАЯН
    def s2(c, t):
        card_in(c, "laptop", 400, 540, 760, 760, t, ws(1) - 0.08, rot=-6)
        pop(c, fit_text("меня", 500, 190), 330, 560, t, ws(1))
        pop(c, fit_text("зовут", 520, 190), 330, 1060, t, ws(2))
        if t >= ws(3):
            EVENTS.add(("boom", ws(3)))
            k = ease_out((t - ws(3)) / 0.22)
            lay = text_layer("баян", 620, RED, squeeze=0.9)
            paste_c(c, lay, W/2, 1480, (W*1.02/lay.width) * (1.3 - 0.3*k), 1, 0, (1-k)*18)
    add(ws(1) - 0.08, s2)

    # 3. фотограф
    def s3(c, t): pop(c, fit_text("фотограф,", 940, 230, WHITE), W/2, 960, t, ws(5))
    add(ws(4) - 0.05, ("full", "tether", s3, 0.07, (0.5, 0.55)), True)

    # 4. SMM-специалист
    def s4(c, t):
        pop(c, fit_text("SMM-", 800, 300), W/2, 880, t, ws(6))
        pop(c, fit_text("специалист", 960, 200), W/2, 1130, t, ws(7))
    add(ws(6) - 0.03, s4)

    # 5. миллион идей
    def s5(c, t):
        up = t >= ws(15)
        if not up:
            acc(c, [("и", 8), ("человек,", 9), ("у", 10), ("которого", 11)], 900, t=t)
            acc(c, [("в", 12), ("голове", 13), ("всегда", 14)], 960, t=t)
        if up:
            card_in(c, "book", 260, 340, 230, 470, t, ws(15), rot=7)
            card_in(c, "counter", 360, 260, 800, 430, t, ws(15)+0.1, rot=-5)
            card_in(c, "pizza", 250, 330, 260, 1470, t, ws(15)+0.2, rot=-8)
            card_in(c, "kitchen", 270, 360, 820, 1450, t, ws(15)+0.3, rot=6)
        pop(c, fit_text("миллион", 900, 230), W/2, 1020, t, ws(15))
        pop(c, fit_text("идей", 600, 230), W/2, 1290, t, ws(16))
        meme(c, t, "мой мозг в 3 ночи:", 860, ws(15) - 0.02, color=INK, size=46)
    add(ws(8) - 0.03, s5)

    # 6. снимаю фото и видео (клип)
    def s6(c, t):
        pop(c, fit_text("снимаю", 900, 200, WHITE), W/2, 560, t, ws(18))
        pop(c, fit_text("фото и видео", 960, 150, WHITE), W/2, 1500, t, ws(19))
    add(ws(17) - 0.05, ("clip", None, s6), True)

    # 7. помогаю бизнесам развивать свои СТРА-НИЦЫ
    def s7(c, t):
        acc(c, [("помогаю", 22), ("бизнесам", 23), ("развивать", 24), ("свои", 25)], 470, t=t)
        card_in(c, "lookbook", 560, 760, W/2, 1000, t, ws(22), rot=0)
        pop(c, fit_text("стра", 420, 190), 220, 640, t, ws(26))
        pop(c, fit_text("ницы", 440, 190), 860, 1380, t, ws(26) + 0.16)
    add(ws(22) - 0.05, s7)

    # 8. и запускаю рекламу
    def s8(c, t):
        card_in(c, "case", 560, 720, W/2, 760, t, ws(27) - 0.03, rot=-4)
        paste_c(c, small("и запускаю", 46), W/2, 1260)
        pop(c, fit_text("рекламу", 980, 260), W/2, 1440, t, ws(29))
        meme(c, t, "таргет mode: on", 1610, ws(29) + 0.45)
    add(ws(27) - 0.03, s8)

    # 9. а ещё обучаю других тому, что умею сама
    def s9(c, t):
        acc(c, [("а", 30), ("ещё", 31)], 780, t=t)
        pop(c, fit_text("обучаю", 960, 270), W/2, 980, t, ws(32))
        acc(c, [("других", 33), ("тому,", 34), ("что", 35), ("умею", 36), ("сама", 37)], 1180, t=t)
        meme(c, t, "(иногда даже себя)", 1290, ws(37) + 0.4)
    add(ws(30) - 0.05, s9)

    # 10. мне нравится создавать / пробовать новое
    def s10(c, t):
        acc(c, [("мне", 38), ("нравится", 39)], 420, t=t)
        card_in(c, "studio", 520, 700, W/2, 900, t, ws(40) - 0.05, rot=-5)
        pop(c, fit_text("создавать,", 960, 210), W/2, 1450, t, ws(40))
    add(ws(38) - 0.05, s10)
    def s10b(c, t):
        pop(c, fit_text("пробовать", 960, 230), W/2, 860, t, ws(41), dur=0.1)
        pop(c, fit_text("новое", 700, 260), W/2, 1100, t, ws(42), rot=-4)
    add(ws(41) - 0.03, s10b)

    # 11. из маленькой идеи ... БОЛЬШОЕ
    def s11(c, t):
        acc(c, [("и", 43), ("наблюдать,", 44), ("как", 45), ("из", 46), ("маленькой", 47), ("идеи", 48)], 420, t=t)
        acc(c, [("постепенно", 49), ("рождается", 50)], 480, t=t)
        if t >= ws(47):
            g = ease_out((t - ws(47)) / (ws(51) - ws(47)))   # card grows from tiny to big
            paste_c(c, card("counter", 760, 540), W/2, 1000, 0.25 + 0.75*g, min(1, (t - ws(47))/0.1), -4 + 4*g)
    add(ws(43) - 0.05, s11)
    def s11b(c, t):
        pop(c, fit_text("что-то", 600, 150), W/2, 760, t, ws(51))
        if t >= ws(52):
            EVENTS.add(("boom", ws(52)))
            k = ease_out((t - ws(52)) / 0.25)
            lay = text_layer("большое", 620, RED, squeeze=0.9)
            paste_c(c, lay, W/2, 1000, (W*1.04/lay.width) * (1.35 - 0.35*k), 1, 0, (1-k)*18)
    add(ws(51) - 0.03, s11b)

    # 12. но моя жизнь — это не только работа
    def s12(c, t):
        acc(c, [("но", 53), ("моя", 54), ("жизнь", 55), ("— это", 56)], 760, t=t)
        pop(c, fit_text("не только", 960, 200), W/2, 960, t, ws(57))
        pop(c, fit_text("работа", 900, 250), W/2, 1180, t, ws(59), rot=-3)
        if t >= ws(59) + 0.35:   # hand-drawn strike-through
            k = ease_out((t - ws(59) - 0.35) / 0.2)
            d = ImageDraw.Draw(c); x0 = W/2 - 330
            d.line((x0, 1200, x0 + 660*k, 1165), fill=INK + (255,), width=14)
    add(ws(53) - 0.05, s12)

    # 13. я люблю читать книги
    def s13(c, t):
        paste_c(c, small("я люблю", 50, WHITE), W/2, 1300)
        pop(c, fit_text("читать книги", 980, 170, WHITE), W/2, 1440, t, ws(62))
    add(ws(60) - 0.05, ("full", "tea", s13, 0.05, (0.5, 0.6)), True)

    # 14. готовить что-нибудь вкусное
    def s14(c, t):
        card_in(c, "counter", 860, 580, W/2, 860, t, ws(64) - 0.05, rot=3)
        pop(c, fit_text("готовить", 900, 230), W/2, 1380, t, ws(64))
    add(ws(64) - 0.05, s14)
    def s14b(c, t):
        paste_c(c, small("что-нибудь", 48, WHITE), W/2, 1300)
        pop(c, fit_text("вкусное", 960, 250, WHITE), W/2, 1470, t, ws(66))
    add(ws(65) - 0.03, ("full", "pizza", s14b), True)

    # 15. и находить время для близких
    def s15(c, t):
        acc(c, [("и", 67), ("находить", 68), ("время", 69), ("для", 70)], 1300, 50, WHITE, t)
        pop(c, fit_text("близких", 900, 240, WHITE), W/2, 1470, t, ws(71), dur=0.3)
    add(ws(67) - 0.03, ("full", "kitchen", s15, 0.05, (0.5, 0.4), 0.3), True)

    # 16. в этом блоге ... вдохновляет
    def s16(c, t):
        acc(c, [("в", 72), ("этом", 73), ("блоге", 74), ("я", 75), ("хочу", 76), ("делиться", 77)], 760, t=t)
        acc(c, [("всем,", 78), ("что", 79), ("меня", 80)], 820, t=t)
        pop(c, fit_text("вдохновляет", 980, 210), W/2, 1000, t, ws(81))
    add(ws(72) - 0.05, s16)
    head = lambda c: paste_c(c, small("в этом блоге:", 46), W/2, 330)
    topics = [(82, [("работой,", 82)], "studio", 6), (83, [("обычными", 83), ("днями,", 84)], "bag", -6),
              (85, [("мыслями,", 85)], "laptop", 5), (86, [("мечтами", 86)], "read", -5),
              (87, [("и новыми", 87), ("начинаниями", 89)], "counter", 4)]
    for wi, lines, ph, rot in topics:
        def st(c, t, wi=wi, lines=lines, ph=ph, rot=rot):
            head(c)
            card_in(c, ph, 560, 720, W/2, 880, t, ws(wi) - 0.03, rot=rot, dur=0.2)
            for j, (w, wj) in enumerate(lines):
                pop(c, fit_text(w, 980, 200), W/2, 1400 + j*190, t, ws(wj), dur=0.1)
            if wi == 86: meme(c, t, "(и вишлистом на 40 пунктов)", 1580, ws(86) + 0.05)
        add(ws(wi) - 0.03, st)

    # 17. честно?
    def s17(c, t):
        jit = math.sin(t * 55) * 7 if t < ws(90) + 0.3 else 0
        card_in(c, "cat", 600, 800, W/2, 800, t, ws(90) - 0.05, rot=3)
        pop(c, fit_text("честно?", 960, 290), W/2 + jit, 1470, t, ws(90), rot=-4)
        meme(c, t, "кот тоже не знает", 1660, ws(90) + 0.55)
    add(ws(90) - 0.05, s17)

    # 18. я пока не знаю, к чему всё это приведёт (клип)
    def s18(c, t):
        acc(c, [("я", 91), ("пока", 92), ("не", 93), ("знаю,", 94)], 900, 54, WHITE, t)
        acc(c, [("к", 95), ("чему", 96), ("всё", 97), ("это", 98), ("приведёт", 99)], 980, 54, WHITE, t)
    add(ws(91) - 0.05, ("clip", None, s18), True)

    # 19. но мне интересно узнать)
    def s19(c, t):
        acc(c, [("но", 100), ("мне", 101)], 780, t=t)
        pop(c, fit_text("интересно", 960, 240), W/2, 960, t, ws(102))
        pop(c, fit_text("узнать)", 900, 260), W/2, 1180, t, ws(103), dur=0.45)
    add(ws(100) - 0.05, s19)

    def s20(c, t): paste_c(c, small("bayana_askar", 34), W/2, 960)
    add(VOICE_END - 0.3, s20)
    add(VOICE_END + 0.4, ("outro", None, None), True)
    return sorted(S, key=lambda s: s[0])

SC = scenes()

def frame(t):
    i = max(k for k, s in enumerate(SC) if s[0] <= t + 1e-6)
    t0, fn, photo = SC[i]
    t1 = SC[i+1][0] if i + 1 < len(SC) else TOTAL
    if isinstance(fn, tuple): EVENTS.add(("chime" if fn[0] == "outro" else "swish", round(t0, 3)))
    if isinstance(fn, tuple) and fn[0] == "outro":
        c = Image.new("RGBA", (W, H), DARK + (255,))
        k = (t - t0)
        grad = k < 1.4
        icon = ig_icon(220, WHITE, gradient=grad)
        sc = 1 + 0.06*math.sin(min(k, 1.4)/1.4*math.pi) if grad else 1
        paste_c(c, icon, W/2, 900, sc)
        paste_c(c, small("@BAYANA_ASKAR", 52, WHITE), W/2, 1080)
        return c.convert("RGB")
    if isinstance(fn, tuple):
        kind, ph, draw = fn[0], fn[1], fn[2]
        if kind == "clip":
            bg = CLIP[min(int((t - t0) * FPS), len(CLIP) - 1)]
        else:
            zoom = fn[3] if len(fn) > 3 else 0.07
            focus = fn[4] if len(fn) > 4 else (0.5, 0.5)
            bg = _zoom(ph, focus, 1 + zoom * min(max((t-t0)/max(t1-t0, .1), 0), 1))
        bg = darken(bg, fn[5] if len(fn) > 5 else 0.18)
        c = bg.convert("RGBA")
    else:
        draw = fn
        c = Image.new("RGBA", (W, H), BG + (255,))
    draw(c, t)
    watermark(c, photo)
    return c.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        for tt in [float(x) for x in sys.argv[3:]]:
            frame(tt).resize((540, 960)).save(f"{out}_{tt:05.2f}.jpg", quality=80)
        sys.exit()
    a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, TOTAL)
    n = int((b - a) * FPS)
    tmpv = B + "_video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    for k in range(n):
        ff.stdin.write(frame(a + k / FPS).tobytes())
        if k % 150 == 0: print(f"{k}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    import sfx
    sfx.build(EVENTS, TOTAL, B + "_sfx.wav")
    # voice on top, effects underneath; trim to the rendered range
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", B + "voice.mp3", "-i", B + "_sfx.wav",
                    "-filter_complex",
                    f"[1:a]aformat=channel_layouts=stereo,loudnorm=I=-15:TP=-2,apad[v];"
                    f"[2:a]aformat=channel_layouts=stereo,volume=0.9[s];"
                    f"[v][s]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,"
                    f"atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    os.remove(tmpv); os.remove(B + "_sfx.wav")
