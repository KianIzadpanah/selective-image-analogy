# -*- coding: utf-8 -*-
"""Render `new figures/Teaser.pdf` and `Architecture.pdf` into web figures.

Needs `pdftoppm` (poppler / MiKTeX) on PATH. Writes static/figures/<stem>.webp,
<stem>.png and <stem>-1x.webp, trimmed of their surrounding white margin.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "new figures")
OUT = os.path.join(ROOT, "static", "figures")
DPI = 110

FIGURES = [
    ("Teaser.pdf", "teaser", 2400),
    ("Architecture.pdf", "architecture", 2600),
]


def trim(im, tol=246, pad=6):
    """Crop the surrounding near-white margin, keeping a few pixels of air."""
    a = np.asarray(im.convert("RGB"))
    nz = (a < tol).any(axis=2)
    rows = np.where(nz.any(axis=1))[0]
    cols = np.where(nz.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return im
    return im.crop((
        max(int(cols.min()) - pad, 0),
        max(int(rows.min()) - pad, 0),
        min(int(cols.max()) + 1 + pad, im.width),
        min(int(rows.max()) + 1 + pad, im.height),
    ))


def render(pdf, tmp):
    stem = os.path.join(tmp, "page")
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(DPI), "-f", "1", "-l", "1", pdf, stem],
        check=True)
    pages = sorted(f for f in os.listdir(tmp) if f.startswith("page"))
    if not pages:
        raise RuntimeError("pdftoppm produced no output for " + pdf)
    return os.path.join(tmp, pages[0])


def main():
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm not found on PATH — install poppler-utils or MiKTeX.")
    os.makedirs(OUT, exist_ok=True)

    for name, stem, target_w in FIGURES:
        pdf = os.path.join(SRC, name)
        tmp = tempfile.mkdtemp(prefix="siafig-")
        try:
            im = trim(Image.open(render(pdf, tmp)).convert("RGB"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        if im.width > target_w:
            im = im.resize((target_w, round(im.height * target_w / im.width)),
                           Image.LANCZOS)

        im.save(os.path.join(OUT, stem + ".webp"), "WEBP", quality=90, method=6)
        im.save(os.path.join(OUT, stem + ".png"), "PNG", optimize=True)
        im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(
            os.path.join(OUT, stem + "-1x.webp"), "WEBP", quality=88, method=6)

        kb = lambda ext: os.path.getsize(os.path.join(OUT, stem + ext)) // 1024
        print("%s: %dx%d  webp=%dKB  png=%dKB"
              % (stem, im.width, im.height, kb(".webp"), kb(".png")))


if __name__ == "__main__":
    main()
