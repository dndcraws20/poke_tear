"""Clean booster-pack art: strip the background (flood fill from the edges, so white inside the
art survives), tight-crop, pad 2%, fit to a max height and save as PNG with transparency.

    python tools/cleanpack.py <in> <out.png> [--tol 34] [--height 1000] [--keep-alpha]

Use --keep-alpha for images that already carry a proper alpha channel (just crops + resizes).
"""
import sys, argparse
from collections import deque
from PIL import Image, ImageFilter

def bg_color(im):
    w, h = im.size
    px = im.load()
    samples = [px[x, y] for x in (0, 1, w - 2, w - 1) for y in (0, 1, h - 2, h - 1)]
    r = sorted(s[0] for s in samples)[len(samples) // 2]
    g = sorted(s[1] for s in samples)[len(samples) // 2]
    b = sorted(s[2] for s in samples)[len(samples) // 2]
    return (r, g, b)

def strip_background(im, tol):
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    bg = bg_color(im)
    def near(p):
        return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) <= tol * 3
    mask = bytearray(w * h)  # 1 = background
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near(px[x, y]) and not mask[y * w + x]:
                mask[y * w + x] = 1; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if near(px[x, y]) and not mask[y * w + x]:
                mask[y * w + x] = 1; q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not mask[ny * w + nx] and near(px[nx, ny]):
                mask[ny * w + nx] = 1; q.append((nx, ny))
    alpha = Image.frombytes("L", (w, h), bytes(255 - m * 255 for m in mask))
    # soften the cut edge by a pixel so it doesn't look razor-jagged
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(alpha)
    return im

def crop_pad_fit(im, height, pad=0.02):
    bbox = im.getchannel("A").point(lambda a: 255 if a > 24 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    p = int(max(w, h) * pad)
    canvas = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    canvas.paste(im, (p, p), im)
    if canvas.height > height:
        canvas = canvas.resize((round(canvas.width * height / canvas.height), height), Image.LANCZOS)
    return canvas

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--tol", type=int, default=34)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--keep-alpha", action="store_true")
    a = ap.parse_args()
    im = Image.open(a.src)
    im = im.convert("RGBA") if a.keep_alpha else strip_background(im, a.tol)
    out = crop_pad_fit(im, a.height)
    out.save(a.dst, "PNG", optimize=True)
    print(a.dst, out.size)
