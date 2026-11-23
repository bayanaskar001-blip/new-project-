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
B = "/tmp/claude-0/-home-user-new-project-/72d83ebe-2a17-52b5-8f9f-dcdf689494a5/scratchpad/build/"
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_SMALL = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

PH = {k: Image.open(UP + v).convert("RGB") for k, v in {
    "read": "e4f536ec-image.jpg", "book": "e58bf32c-image.jpg", "kitchen": "acafdf5f-image.jpg",
    "laptop": "f87c14d0-image.jpg", "counter": "3d80ca09-image.jpg", "pizza": "d6e6f985-image.jpg",
    "studio": "1ab7ea95-image.jpg"}.items()}
PH = {k: ImageOps.exif_transpose(v) for k, v in PH.items()}

WORDS = json.load(open(B + "words.json"))
def ws(i): return WORDS[i][1]          # word start time
VOICE_END = 48.34
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

def pop(canvas, layer, cx, cy, t, t0, rot=0.0, blur_in=True, dur=0.16):
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
    paste_c(canvas, small("БАЯН", 22, col), W - 120, 196)

# ---------- scenes ----------
def scenes():
    S = []
    def add(t0, fn, photo=False): S.append((t0, fn, photo))

    # 1. привет
    def s1(c, t):
        card_in(c, "read", 520, 700, 400, 700, t, 0.0, rot=9)
        pop(c, fit_text("привет,", 900, 230), 600, 1250, t, ws(0))
    add(0.0, s1)

    # 2. меня зовут БАЯН
    def s2(c, t):
        card_in(c, "laptop", 400, 540, 760, 760, t, 1.5, rot=-6)
        pop(c, fit_text("меня", 500, 190), 330, 560, t, ws(1))
        pop(c, fit_text("зовут", 520, 190), 330, 1060, t, ws(2))
        if t >= ws(3):
            k = ease_out((t - ws(3)) / 0.22)
            lay = text_layer("баян", 620, RED, squeeze=0.9)
            paste_c(c, lay, W/2, 1480, (W*1.02/lay.width) * (1.3 - 0.3*k), 1, 0, (1-k)*18)
    add(1.5, s2)

    # 3. фотограф (на фото студии)
    def s3(c, t):
        pop(c, fit_text("фотограф", 940, 230, WHITE), W/2, 960, t, ws(5))
    add(ws(4) - 0.05, ("full", "studio", s3), True)

    def s3b(c, t):
        paste_c(c, small("и", 46), W/2, 700)
        pop(c, fit_text("SMM-", 800, 300), W/2, 880, t, ws(7))
        pop(c, fit_text("специалист", 960, 200), W/2, 1130, t, ws(8))
    add(ws(6), s3b)

    # 4. новые идеи + collage
    def s4(c, t):
        line1 = ["а", "ещё", "человек,", "у", "которого", "в", "голове"]
        line2 = ["постоянно", "появляются"]
        idx = [9, 10, 11, 12, 13, 14, 15]
        shown1 = " ".join(w for w, i in zip(line1, idx) if t >= ws(i))
        shown2 = " ".join(w for w, i in zip(line2, [16, 17]) if t >= ws(i))
        if shown1: paste_c(c, small(shown1, 44), W/2, 880 if t < ws(18) else 820)
        if shown2: paste_c(c, small(shown2, 44), W/2, 940 if t < ws(18) else 880)
        if t >= ws(18):
            card_in(c, "book", 260, 340, 230, 470, t, ws(18), rot=7)
            card_in(c, "counter", 360, 260, 800, 430, t, ws(18)+0.12, rot=-5)
            card_in(c, "pizza", 250, 330, 260, 1450, t, ws(18)+0.24, rot=-8)
            card_in(c, "kitchen", 270, 360, 820, 1430, t, ws(18)+0.36, rot=6)
        pop(c, fit_text("новые идеи", 980, 210), W/2, 1050, t, ws(18))
    add(ws(9) - 0.05, s4)

    # 5. снимаю фото и видео (клип)
    def s5(c, t):
        pop(c, fit_text("снимаю", 900, 200, WHITE), W/2, 560, t, ws(21))
        pop(c, fit_text("фото и видео", 960, 150, WHITE), W/2, 1500, t, ws(22))
    add(ws(20) - 0.05, ("clip", None, s5), True)

    # 6. помогаю бизнесам вести СОЦ-СЕТИ
    def s6(c, t):
        txt = " ".join(w for w, i in [("помогаю", 25), ("бизнесам", 26), ("вести", 27)] if t >= ws(i))
        paste_c(c, small(txt, 44), W/2, 470)
        card_in(c, "laptop", 560, 760, W/2, 1000, t, ws(25), rot=0)
        pop(c, fit_text("соц", 400, 190), 210, 640, t, ws(28))
        pop(c, fit_text("сети", 420, 190), 870, 1380, t, ws(29))
    add(ws(25) - 0.05, s6)

    # 7. запускаю рекламу
    def s7(c, t):
        paste_c(c, small("и запускаю", 46), W/2, 820)
        pop(c, fit_text("рекламу", 980, 260), W/2, 1000, t, ws(32))
    add(ws(30), s7)

    # 8. делюсь знаниями, обучаю
    def s8(c, t):
        txt = " ".join(w for w, i in [("делюсь", 33), ("своими", 34), ("знаниями", 35), ("и", 36)] if t >= ws(i))
        paste_c(c, small(txt, 46), W/2, 780)
        pop(c, fit_text("обучаю", 960, 270), W/2, 980, t, ws(37))
        txt2 = " ".join(w for w, i in [("тому,", 38), ("что", 39), ("люблю", 40), ("сама:", 41)] if t >= ws(i))
        if txt2: paste_c(c, small(txt2, 46), W/2, 1180)
    add(ws(33) - 0.05, s8)

    # 9. съёмке и продвижению
    def s9(c, t):
        card_in(c, "studio", 420, 560, 300, 620, t, ws(42), rot=-7)
        pop(c, fit_text("съёмке", 520, 170), 760, 560, t, ws(42))
        paste_c(c, small("и", 46), W/2, 990) if t >= ws(43) else None
        card_in(c, "laptop", 420, 560, 780, 1380, t, ws(44), rot=6)
        pop(c, fit_text("продви-", 520, 150), 300, 1300, t, ws(44))
        pop(c, fit_text("жению", 520, 150), 300, 1450, t, ws(44) + 0.15)
    add(ws(42) - 0.05, s9)

    # 10. моя жизнь — это ...
    def s10(c, t):
        paste_c(c, small("моя жизнь —" if t < ws(47) else "моя жизнь — это", 50), W/2, 960)
    add(ws(45) - 0.05, s10)
    flashes = [(48, "съёмки", "studio"), (49, "проекты", None), (50, "встречи", "laptop"),
               (51, "семья", None), (52, "и планы,", "counter")]
    for wi, word, ph in flashes:
        def sf(c, t, wi=wi, word=word, ph=ph):
            pop(c, fit_text(word, 960, 250, WHITE if ph else RED), W/2, 960, t, ws(wi), dur=0.1)
        if ph: add(ws(wi) - 0.03, ("full", ph, sf), True)
        else: add(ws(wi) - 0.03, sf)

    # 11. меняются прямо посреди дня
    def s11(c, t):
        txt = " ".join(w for w, i in [("которые", 54), ("иногда", 55), ("меняются", 56)] if t >= ws(i))
        paste_c(c, small(txt, 46), W/2, 760)
        pop(c, fit_text("прямо", 800, 220), W/2 - 120, 960, t, ws(57), rot=4)
        if t >= ws(58):
            jit = math.sin(t * 60) * 6 if t < ws(58) + 0.35 else 0
            pop(c, fit_text("посреди дня", 980, 190), W/2 + jit, 1180, t, ws(58), rot=-3)
    add(ws(54) - 0.05, s11)

    # 12. замедлиться (чтение)
    def s12(c, t):
        if t >= ws(60):
            paste_c(c, small("а когда хочется", 46, WHITE), W/2, 1350)
        pop(c, fit_text("замедлиться", 980, 170, WHITE), W/2, 1470, t, ws(63), dur=0.35)
    add(ws(60) - 0.05, ("full", "read", s12, 0.04, (0.6, 0.4)), True)

    # 13. беру книгу
    def s13(c, t):
        paste_c(c, small("я беру", 46), W/2, 400)
        card_in(c, "book", 560, 780, W/2, 980, t, ws(64) - 0.05, rot=-4)
        pop(c, fit_text("книгу", 700, 260), W/2 + 60, 1480, t, ws(66), rot=-6)
    add(ws(64) - 0.05, s13)

    # 14. или готовлю что-нибудь вкусное
    def s14(c, t):
        paste_c(c, small("или", 46), W/2, 420)
        card_in(c, "counter", 860, 580, W/2, 900, t, ws(67), rot=3)
        pop(c, fit_text("готовлю", 900, 220), W/2, 1400, t, ws(68))
    add(ws(67) - 0.03, s14)

    def s14b(c, t):
        paste_c(c, small("что-нибудь", 48, WHITE), W/2, 1300)
        pop(c, fit_text("вкусное", 960, 250, WHITE), W/2, 1470, t, ws(70))
    add(ws(69) - 0.03, ("full", "pizza", s14b), True)

    # 15. здесь будет про ...
    head = lambda c: paste_c(c, small("здесь будет про", 46), W/2, 330)
    def s15(c, t): head(c)
    add(ws(71) - 0.05, s15)
    topics = [(74, "работу", "studio", 6), (75, "обучение", "laptop", -6), (76, "личную жизнь", "kitchen", 5),
              (78, "книги", "book", -5), (79, "готовку", "pizza", 6), (80, "мечты", "read", -4)]
    for wi, word, ph, rot in topics:
        def st(c, t, wi=wi, word=word, ph=ph, rot=rot):
            head(c)
            card_in(c, ph, 560, 760, W/2, 940, t, ws(wi) - 0.03, rot=rot, dur=0.2)
            pop(c, fit_text(word, 980, 230), W/2, 1490, t, ws(wi), dur=0.1)
        add(ws(wi) - 0.03, st)

    # 16. и мой ПУ ... ТЬ
    def s16(c, t):
        paste_c(c, small("и мой", 46), W/2, 640)
        card_in(c, "counter", 620, 440, W/2, 960, t, ws(81) - 0.02, rot=0)
        pop(c, fit_text("пу", 300, 230), 140, 1000, t, ws(83))
        pop(c, fit_text("ть", 300, 230), 945, 1000, t, ws(83) + 0.12)
    add(ws(81) - 0.03, s16)

    # 17. не знаю, куда он меня приведёт (фото кухни)
    def s17(c, t):
        txt = " ".join(w for w, i in [("не", 84), ("знаю,", 85), ("куда", 86), ("он", 87), ("меня", 88), ("приведёт", 89)] if t >= ws(i))
        paste_c(c, small(txt, 50, WHITE), W/2, 960)
    add(ws(84) - 0.05, ("full", "kitchen", s17, 0.05, (0.5, 0.4), 0.35), True)

    # 18. предлагаю пройти его вместе)
    def s18(c, t):
        txt = " ".join(w for w, i in [("но", 90), ("предлагаю", 91), ("пройти", 92), ("его", 93)] if t >= ws(i))
        paste_c(c, small(txt, 46), W/2, 820)
        pop(c, fit_text("вместе)", 960, 260), W/2, 1000, t, ws(94), dur=0.45)
    add(ws(90) - 0.05, s18)

    # 19. подписывайся — будем знакомиться
    def s19(c, t):
        pop(c, fit_text("подписывайся", 980, 200), W/2, 860, t, ws(95))
        pop(c, fit_text("будем", 600, 160), W/2, 1060, t, ws(96))
        pop(c, fit_text("знакомиться", 960, 160), W/2, 1220, t, ws(97))
    add(ws(95) - 0.05, s19)

    # 20. small name
    def s20(c, t): paste_c(c, small("баян", 34), W/2, 960)
    add(VOICE_END - 0.4, s20)
    add(VOICE_END + 0.4, ("outro", None, None), True)
    return sorted(S, key=lambda s: s[0])

SC = scenes()

def frame(t):
    i = max(k for k, s in enumerate(SC) if s[0] <= t + 1e-6)
    t0, fn, photo = SC[i]
    t1 = SC[i+1][0] if i + 1 < len(SC) else TOTAL
    if isinstance(fn, tuple) and fn[0] == "outro":
        c = Image.new("RGBA", (W, H), DARK + (255,))
        k = (t - t0)
        grad = k < 1.4
        icon = ig_icon(220, WHITE, gradient=grad)
        sc = 1 + 0.06*math.sin(min(k, 1.4)/1.4*math.pi) if grad else 1
        paste_c(c, icon, W/2, 900, sc)
        paste_c(c, small("БАЯН", 52, WHITE), W/2, 1080)
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
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-ss", str(a), "-t", str(b - a), "-i", B + "audio.m4a",
                           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    for k in range(n):
        ff.stdin.write(frame(a + k / FPS).tobytes())
        if k % 150 == 0: print(f"{k}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
