# -*- coding: utf-8 -*-
"""Crop / convert every result image and emit static/js/data.js for the site.

Source of truth is `new figures/`:
  * all_is_correct/<n>  -> the interactive "Results" switchboard (many subsets)
  * some_is_correct/<n> -> the curated "Examples" carousel (one subset each)

Any frame taller than 512 px carries a rendered caption strip underneath the
result, so it is cropped back to its top 512 rows.
"""
import json
import os
import re
import shutil

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "new figures")
IMG = os.path.join(ROOT, "static", "images")
MAXH = 512
Q = 88


# ---------------------------------------------------------------- helpers
def prep(path):
    """Open, flatten alpha over white, crop anything taller than 512 px."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    im = im.convert("RGB")
    if im.height > MAXH:
        im = im.crop((0, 0, im.width, MAXH))
    return im


def save(im, dest, size=None, q=Q):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    im.save(dest, "WEBP", quality=q, method=6)


def thumb(im, dest, w=180):
    h = round(im.height * w / im.width)
    save(im.resize((w, h), Image.LANCZOS), dest, q=82)


# ---------------------------------------------------------------- metadata
SAMPLES = [
    dict(id="s1", src="all_is_correct/1", label="Alley portrait", subject="people",
         title="Diadem, hair, street, brushwork",
         edits=[("add a celestial diadem", "object"),
                ("add blue hair", "appearance"),
                ("add an empty Japanese festival street background", "background"),
                ("add Van Gogh style", "style")]),
    dict(id="s2", src="all_is_correct/2", label="Dragon", subject="creatures",
         title="Lava, open wings, gold scales",
         edits=[("add lava to the ground", "background"),
                ("open the wings", "pose"),
                ("add gold color", "appearance")]),
    dict(id="s3", src="all_is_correct/3", label="Studio portrait", subject="people",
         title="Earrings, expression, mountains",
         edits=[("add earrings", "object"),
                ("happy expression", "expression"),
                ("add a mountain and blue sky background", "background")]),
]

EXAMPLES = [
    dict(id="x1", src="some_is_correct/1", result="supp_e2_e3.png", subject="people",
         title="Armor, without the hat or the jungle",
         edits=[("add armor", "object", 1),
                ("add a beach hat", "object", 0),
                ("jungle background", "background", 0)]),
    dict(id="x2", src="some_is_correct/2", result="supp_e3.png", subject="objects",
         title="The carving, in full color",
         edits=[("add carved Halloween texture", "appearance", 1),
                ("spooky candlelit table, dark background", "background", 1),
                ("black and white pencil style", "style", 0)]),
    dict(id="x3", src="some_is_correct/3", result="supp_e3.png", subject="objects",
         title="Logo and paint, doors closed",
         edits=[("add a golden star logo to the hood", "object", 1),
                ("change the car color to red", "appearance", 1),
                ("open the car doors", "pose", 0)]),
    dict(id="x4", src="some_is_correct/4", result="SIA.png", subject="creatures",
         title="Recolored, still standing",
         edits=[("change the dog color to blue", "appearance", 1),
                ("sitting pose", "pose", 0)]),
    dict(id="x5", src="some_is_correct/5", result="supp_e2.png", subject="people",
         title="Beard and street, same neutral face",
         edits=[("add a beard", "object", 1),
                ("happy expression", "expression", 0),
                ("street background", "background", 1)]),
    dict(id="x6", src="some_is_correct/6", result="supp_e2.png", subject="creatures",
         title="The jump, without the pencil",
         edits=[("jumping", "pose", 1),
                ("add colored pencil style", "style", 0)]),
    dict(id="x7", src="some_is_correct/7", result="supp_e2.png", subject="people",
         title="The beard, not the sunglasses",
         edits=[("add a professor beard", "object", 1),
                ("add sunglasses", "object", 0)]),
    dict(id="x8", src="some_is_correct/8", result="supp_e1_e4.png", subject="people",
         title="Wig and alley, in color",
         edits=[("add a blue scarf", "object", 0),
                ("add a short white hair wig", "appearance", 1),
                ("add an old cobblestone alley background", "background", 1),
                ("add black and white pencil style", "style", 0)]),
]


# ---------------------------------------------------------------- build
def mask_from_filename(fn, n):
    """`supp_e1_e3.png` with n=4 -> "0101" (1 = edit kept)."""
    supp = {int(t) for t in re.findall(r"e(\d+)", fn)}
    out_of_range = [i for i in supp if i < 1 or i > n]
    assert not out_of_range, f"{fn}: edit index out of range {out_of_range}"
    return "".join("0" if (i + 1) in supp else "1" for i in range(n))


def main():
    if os.path.isdir(IMG):
        shutil.rmtree(IMG)

    out_samples, out_examples = [], []

    for s in SAMPLES:
        d = os.path.join(SRC, s["src"])
        n = len(s["edits"])
        dim = prep(os.path.join(d, "a.png")).size
        dest = os.path.join(IMG, "samples", s["id"])
        for name, fn in (("a", "a.png"), ("ap", "a_prime.png"), ("b", "b.png")):
            save(prep(os.path.join(d, fn)), os.path.join(dest, name + ".webp"), dim)
        thumb(prep(os.path.join(d, "b.png")), os.path.join(dest, "thumb.webp"))

        available = []
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".png"):
                continue
            if fn == "no_supp.png":
                mask = "1" * n
            elif fn.startswith("supp_"):
                mask = mask_from_filename(fn, n)
            else:
                continue
            save(prep(os.path.join(d, fn)),
                 os.path.join(dest, "subsets", mask + ".webp"), dim)
            available.append(mask)
        available.sort(key=lambda m: (-m.count("1"), m))

        out_samples.append(dict(
            id=s["id"], label=s["label"], title=s["title"], subject=s["subject"],
            w=dim[0], h=dim[1], dir="static/images/samples/" + s["id"],
            edits=[dict(id="e%d" % (i + 1), label=lb, type=tp)
                   for i, (lb, tp) in enumerate(s["edits"])],
            available=available))
        print("%s: %s  %d/%d combinations  %s"
              % (s["id"], dim, len(available), 2 ** n, available))

    for x in EXAMPLES:
        d = os.path.join(SRC, x["src"])
        dim = prep(os.path.join(d, "a.png")).size
        dest = os.path.join(IMG, "examples", x["id"])
        for name, fn in (("a", "a.png"), ("ap", "a_prime.png"),
                         ("b", "b.png"), ("out", x["result"])):
            save(prep(os.path.join(d, fn)), os.path.join(dest, name + ".webp"), dim)
        thumb(prep(os.path.join(d, x["result"])), os.path.join(dest, "thumb.webp"))

        keep = "".join(str(k) for _, _, k in x["edits"])
        if x["result"].startswith("supp_"):
            expect = mask_from_filename(x["result"], len(x["edits"]))
            assert expect == keep, ("%s: %s implies %s but metadata says %s"
                                    % (x["id"], x["result"], expect, keep))

        out_examples.append(dict(
            id=x["id"], title=x["title"], subject=x["subject"],
            w=dim[0], h=dim[1], dir="static/images/examples/" + x["id"],
            edits=[dict(id="e%d" % (i + 1), label=lb, type=tp, kept=bool(k))
                   for i, (lb, tp, k) in enumerate(x["edits"])]))
        print("%s: %s  keep=%s  <- %s" % (x["id"], dim, keep, x["result"]))

    js = os.path.join(ROOT, "static", "js", "data.js")
    os.makedirs(os.path.dirname(js), exist_ok=True)
    with open(js, "w", encoding="utf-8") as f:
        f.write("/* Generated by tools/build_images.py - do not edit by hand. */\n")
        f.write("window.SIA_SAMPLES = "
                + json.dumps(out_samples, indent=2, ensure_ascii=False) + ";\n\n")
        f.write("window.SIA_EXAMPLES = "
                + json.dumps(out_examples, indent=2, ensure_ascii=False) + ";\n")

    total = sum(os.path.getsize(os.path.join(r, fn))
                for r, _, fns in os.walk(IMG) for fn in fns)
    count = sum(len(fns) for _, _, fns in os.walk(IMG))
    print("\n%d webp files, %.2f MB total" % (count, total / 1024 / 1024))


if __name__ == "__main__":
    main()
