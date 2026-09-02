# -*- coding: utf-8 -*-
"""Downsample the camera-ready PDF into a web-sized static/pdfs/SIA_paper.pdf.

The submission PDF is ~70 MB because every figure is a full-resolution PNG.
Ghostscript re-encodes the images at 180 dpi JPEG, which keeps the text vector
and crisp while bringing the file down to a couple of megabytes.

    python tools/build_paper.py ../SIA_finalized2.pdf
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "pdfs", "SIA_paper.pdf")
DPI = 180
JPEG_Q = 82

GS_CANDIDATES = [
    "gswin64c", "gswin32c", "gs",
    r"C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe",
]


def find_gs():
    for cand in GS_CANDIDATES:
        found = shutil.which(cand) or (cand if os.path.exists(cand) else None)
        if found:
            return found
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = os.path.abspath(sys.argv[1])
    if not os.path.exists(src):
        sys.exit("no such file: " + src)

    gs = find_gs()
    if not gs:
        sys.exit("Ghostscript not found — install it or add gswin64c to PATH.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    subprocess.run([
        gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.7",
        "-dNOPAUSE", "-dQUIET", "-dBATCH", "-dDetectDuplicateImages=true",
        "-dDownsampleColorImages=true", "-dColorImageDownsampleType=/Bicubic",
        "-dColorImageResolution=%d" % DPI,
        "-dDownsampleGrayImages=true", "-dGrayImageDownsampleType=/Bicubic",
        "-dGrayImageResolution=%d" % DPI,
        "-dDownsampleMonoImages=true", "-dMonoImageDownsampleType=/Subsample",
        "-dMonoImageResolution=600",
        "-dAutoFilterColorImages=false", "-dColorImageFilter=/DCTEncode",
        "-dAutoFilterGrayImages=false", "-dGrayImageFilter=/DCTEncode",
        "-dJPEGQ=%d" % JPEG_Q,
        "-dEmbedAllFonts=true", "-dSubsetFonts=true", "-dCompressFonts=true",
        "-sOutputFile=" + OUT, src,
    ], check=True)

    print("%s -> %s  (%.1f MB -> %.1f MB)"
          % (os.path.basename(src), os.path.relpath(OUT, ROOT),
             os.path.getsize(src) / 1e6, os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()
