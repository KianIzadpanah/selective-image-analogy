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
         title="Diadem, hair, lake, brushwork",
         edits=[("add a celestial diadem", "object"),
                ("add orange hair", "appearance"),
                ("add a lake shore with reflections background", "background"),
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
    dict(id="x8", src="some_is_correct/8", result="supp_e1_e4.png", subject="people",
         title="Wig and alley, in color",
         edits=[("add a blue scarf", "object", 0),
                ("add a short white hair wig", "appearance", 1),
                ("add an old cobblestone alley background", "background", 1),
                ("add black and white pencil style", "style", 0)]),
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
    dict(id="x3", src="some_is_correct/3", result="supp_e3.png", subject="objects",
         title="Logo and paint, doors closed",
         edits=[("add a golden star logo to the hood", "object", 1),
                ("change the car color to red", "appearance", 1),
                ("open the car doors", "pose", 0)]),
    # (x9 onwards follow; carousel order is set by EXAMPLE_ORDER below)
    dict(id="x9", src="some_is_correct/9", result="supp_e2.png", subject="people",
         title="Sunglasses, not the sad face",
         edits=[("add sunglasses", "object", 1),
                ("add a sad expression", "expression", 0),
                ("empty Japanese festival street background", "background", 1)]),
    dict(id="x10", src="some_is_correct/10", result="supp_e3.png", subject="people",
         title="Crown and necklace, calm face",
         edits=[("add an open-top crown", "object", 1),
                ("add a seamless gold necklace", "object", 1),
                ("add an angry expression", "expression", 0)]),
    dict(id="x11", src="some_is_correct/11", result="supp_e3.png", subject="people",
         title="Armor and hat, still at the beach",
         edits=[("add armor", "object", 1),
                ("add a beach hat", "object", 1),
                ("old cobblestone alley background", "background", 0)]),
    dict(id="x12", src="some_is_correct/12", result="no_supp.png", subject="people",
         title="All three edits, carried over",
         edits=[("add drop earrings", "object", 1),
                ("add a happy expression", "expression", 1),
                ("rolling green hills background", "background", 1)]),
    dict(id="x13", src="some_is_correct/13", result="supp_e3.png", subject="people",
         title="Beard and surprise, same path",
         edits=[("add a short beard", "object", 1),
                ("add a surprised expression", "expression", 1),
                ("lake shore with reflections background", "background", 0)]),
    dict(id="x14", src="some_is_correct/14", result="supp_e2.png", subject="people",
         title="Golden armor, no hat",
         edits=[("add golden armor", "object", 1),
                ("add a cowboy hat", "object", 0),
                ("add a rolling green hills background", "background", 1)]),
    dict(id="x15", src="some_is_correct/15", result="supp_e3.png", subject="creatures",
         title="Red shirt and sit, no painting",
         edits=[("add a red T-shirt", "object", 1),
                ("sitting pose", "pose", 1),
                ("add a minimalist painting style", "style", 0)]),
    dict(id="x16", src="some_is_correct/16", result="supp_e2_e4.png", subject="people",
         title="The scarf and the room, in color",
         edits=[("add a scarf", "object", 1),
                ("add a long blond hair wig", "appearance", 0),
                ("add a store interior background", "background", 1),
                ("add black and white pencil style", "style", 0)]),
    dict(id="x17", src="some_is_correct/17", result="supp_e4.png", subject="people",
         title="Crown, green hair and Paris, as a photo",
         edits=[("add an open-top crown without jewellery", "object", 1),
                ("add green hair", "appearance", 1),
                ("add a Paris background", "background", 1),
                ("add Van Gogh style", "style", 0)]),
    dict(id="x18", src="some_is_correct/18", result="supp_e2.png", subject="people",
         title="Armor and the stage, no hat",
         edits=[("add armor", "object", 1),
                ("add a beach hat", "object", 0),
                ("add an indoor music festival stage background", "background", 1)]),
    dict(id="x19", src="some_is_correct/19", result="no_supp.png", subject="people",
         title="Armor, hat and alley, all three",
         edits=[("add armor", "object", 1),
                ("add a beach hat", "object", 1),
                ("add an old cobblestone alley background", "background", 1)]),
    dict(id="x20", src="some_is_correct/20", result="supp_e3.png", subject="people",
         title="Earrings and a smile, still indoors",
         edits=[("add cluster earrings", "object", 1),
                ("add a happy expression", "expression", 1),
                ("add a peaceful countryside road background", "background", 0)]),
    dict(id="x21", src="some_is_correct/21", result="supp_e1.png", subject="people",
         title="The smile and the beach, no earrings",
         edits=[("add huggie earrings", "object", 0),
                ("add a happy expression", "expression", 1),
                ("add a sandy beach with ocean waves background", "background", 1)]),
    dict(id="x22", src="some_is_correct/22", result="no_supp.png", subject="people",
         title="Beard, surprise and the lake",
         edits=[("add a short beard", "object", 1),
                ("add a surprised expression", "expression", 1),
                ("add a lake shore with reflections background", "background", 1)]),
    dict(id="x23", src="some_is_correct/23", result="supp_e3.png", subject="people",
         title="Sweater and santa hat, same market",
         edits=[("add a sweater", "object", 1),
                ("add a santa hat", "object", 1),
                ("add a street background", "background", 0)]),
    dict(id="x24", src="some_is_correct/24", result="supp_e1.png", subject="objects",
         title="Red lamp in oils, no bench",
         edits=[("add a park metal bench", "object", 0),
                ("turn the lamp light red", "appearance", 1),
                ("add oil painting style", "style", 1)]),
    dict(id="x25", src="some_is_correct/25", result="no_supp.png", subject="creatures",
         title="Red shirt, sit and paint",
         edits=[("add a red T-shirt", "object", 1),
                ("sitting pose", "pose", 1),
                ("add a minimalist painting style", "style", 1)]),
    dict(id="x26", src="some_is_correct/26", result="supp_e1.png", subject="people",
         title="Wig, store and pencil, no scarf",
         edits=[("add a scarf", "object", 0),
                ("add a long blond hair wig", "appearance", 1),
                ("add a store interior background", "background", 1),
                ("add black and white pencil style", "style", 1)]),
    dict(id="x27", src="some_is_correct/27", result="supp_e1.png", subject="people",
         title="White wig in pencil, no scarf",
         edits=[("add a blue scarf", "object", 0),
                ("add a short white hair wig", "appearance", 1),
                ("add an old cobblestone alley background", "background", 1),
                ("add black and white pencil style", "style", 1)]),
    dict(id="x28", src="some_is_correct/28", result="supp_e1_e3.png", subject="people",
         title="Green hair in Van Gogh, same field",
         edits=[("add an open-top crown without jewellery", "object", 0),
                ("add green hair", "appearance", 1),
                ("add a Paris background", "background", 0),
                ("add Van Gogh style", "style", 1)]),
]


# Carousel order. The seven non-human samples (x2, x3, x4, x6, x15, x24, x25)
# take every fourth slot, so a run of portraits is never longer than three.
EXAMPLE_ORDER = [
    "x1", "x8", "x5", "x2",
    "x7", "x9", "x10", "x4",
    "x11", "x12", "x13", "x6",
    "x14", "x16", "x17", "x3",
    "x18", "x19", "x20", "x15",
    "x21", "x22", "x23", "x24",
    "x26", "x27", "x28", "x25",
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

    by_id = {x["id"]: x for x in EXAMPLES}
    assert set(by_id) == set(EXAMPLE_ORDER), (
        "EXAMPLE_ORDER disagrees with EXAMPLES: %s"
        % (set(by_id) ^ set(EXAMPLE_ORDER)))

    for x in [by_id[i] for i in EXAMPLE_ORDER]:
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
        elif x["result"] == "no_supp.png":
            expect = "1" * len(x["edits"])          # full transfer, nothing suppressed
        else:
            expect = keep                            # hand-named render, e.g. SIA.png
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
