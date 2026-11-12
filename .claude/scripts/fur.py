"""Malt das Reh-Fell für den Hintergrund der Seite (assets/images/rehfell.jpg).

Aufruf:  python3 .claude/scripts/fur.py assets/images/rehfell.jpg spots
("spots" für Kitz-Tupfen, "plain" für Fell ohne Tupfen.)
Braucht Python mit numpy und Pillow. Die Zahl in default_rng(7) ändern
ergibt ein anderes, ähnliches Fell.
"""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
rng = np.random.default_rng(7)
W, H = 1600, 1000
S = 2  # supersample
w, h = W*S, H*S
spots = len(sys.argv) > 2 and sys.argv[2] == "spots"

def flow(x, y):
    # gently swirling angle field, mostly pointing down-right
    a = 1.15
    a += 0.35*np.sin(x/(260*S) + 0.7) * np.cos(y/(330*S))
    a += 0.20*np.sin((x+y)/(140*S) + 2.0)
    a += 0.10*np.sin((x-2*y)/(80*S))
    return a

# undercoat: dark warm brown with soft blotches
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
base = np.zeros((h, w, 3), np.float32)
n = (np.sin(xx/(300*S))*np.cos(yy/(220*S)) + 0.5*np.sin((xx+yy)/(170*S)+1)) * 0.5
for c, v in enumerate((92, 48, 24)):
    base[..., c] = v + 18*n
img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
del yy, xx, base
d = ImageDraw.Draw(img)

palette = np.array([
    (120, 62, 30), (146, 78, 36), (168, 92, 42), (184, 104, 48),
    (196, 120, 60), (110, 56, 28), (82, 42, 22), (210, 140, 80),
], float)
weights = np.array([10, 16, 18, 14, 9, 8, 6, 3], float); weights /= weights.sum()

def strands(count, lenrange, width, lighten=0.0, region=None):
    xs = rng.uniform(-40*S, w+40*S, count); ys = rng.uniform(-40*S, h+40*S, count)
    ang = flow(xs, ys) + rng.normal(0, 0.12, count)
    L = rng.uniform(*lenrange, count)*S
    cols = palette[rng.choice(len(palette), count, p=weights)]
    cols = cols*(1+rng.normal(0, 0.07, (count, 1))) + lighten
    for i in range(count):
        x, y, a, l = xs[i], ys[i], ang[i], L[i]
        # slight curve: two segments
        mx, my = x + np.cos(a)*l*0.5, y + np.sin(a)*l*0.5
        a2 = a + rng.normal(0, 0.15)
        ex, ey = mx + np.cos(a2)*l*0.5, my + np.sin(a2)*l*0.5
        c = tuple(int(v) for v in np.clip(cols[i], 0, 255))
        d.line([(x, y), (mx, my), (ex, ey)], fill=c, width=width)

strands(int(sys.argv[3]) if len(sys.argv)>3 else 90000, (14, 30), 2*S//2+1)
strands(60000, (10, 24), S, lighten=10)
# a few light tips/highlights
strands(12000, (8, 18), S, lighten=45)

if spots:
    # fawn-style cream spots in loose rows following the flow
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)
    for row in range(-2, 12):
        y0 = row*115*S
        for k in range(24):
            if rng.random() < 0.35: continue
            x = k*95*S + rng.normal(0, 18*S) + (row % 2)*47*S
            y = y0 + x*0.35 + rng.normal(0, 10*S)
            y = y % (h + 200*S) - 100*S
            r = rng.uniform(10, 19)*S
            md.ellipse([x-r*1.3, y-r, x+r*1.3, y+r], fill=int(rng.uniform(110, 170)))
    mask = mask.filter(ImageFilter.GaussianBlur(5*S))
    cream = Image.new("RGB", (w, h), (236, 210, 170))
    img = Image.composite(cream, img, mask)
    d = ImageDraw.Draw(img)
    strands(40000, (10, 22), S, lighten=5)  # hair over the spots so they look furry

img = img.resize((W, H), Image.LANCZOS)
img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=40)).filter(ImageFilter.GaussianBlur(0.5))
img.save(sys.argv[1], quality=72, optimize=True, progressive=True)
