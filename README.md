# SIA: Selective Image Analogy — project page

Project page for **SIA: Selective Image Analogy**, SIGGRAPH Asia 2026.

**Live site:** <https://kianizadpanah.github.io/selective-image-analogy/>

Amirhossein Alimohammadi\*, Kian Izadpanah\*, Bardiya Kariminia, Yiorgos Chrysanthou,
Ali Mahdavi-Amiri — *\*equal contribution*

---

## Layout

```
index.html                  the whole page
static/
  css/style.css             all styles (light + dark, token-driven)
  js/data.js                GENERATED — sample/example metadata and image paths
  js/app.js                 switchboard, wipe comparison, lightbox, theme, nav
  figures/                  GENERATED — teaser + pipeline figures (webp + png)
  images/                   GENERATED — every result crop, as webp
  pdfs/SIA_paper.pdf        GENERATED — web-sized copy of the paper
  favicon.svg
new figures/                SOURCE — the authors' renders and figure PDFs
tools/                      the three build scripts
```

Everything under `static/images`, `static/figures`, `static/pdfs` and
`static/js/data.js` is generated. Edit the sources, then re-run the scripts.

## Rebuilding the assets

Requires Python with `Pillow` and `numpy`, plus `pdftoppm` (poppler or MiKTeX)
and Ghostscript for the two PDF steps.

```bash
python tools/build_images.py                  # results  -> static/images + static/js/data.js
python tools/build_figures.py                 # figure PDFs -> static/figures
python tools/build_paper.py ../SIA_finalized2.pdf   # 70 MB paper -> 1.6 MB web copy
```

`build_images.py` reads `new figures/`:

* `all_is_correct/<n>/` — one demonstration with **many** rendered subsets. It
  drives the interactive *Results* switchboard. `no_supp.png` is the full
  transfer; `supp_e1_e3.png` means edits 1 and 3 were suppressed. Filenames are
  translated into keep-masks (`"0101"` = keep e2 and e4) and the metadata
  asserts that each mask matches its declared edit list.
* `some_is_correct/<n>/` — one demonstration with a **single** rendered subset,
  used for the *More examples* carousel. The result file is usually
  `supp_*.png`; `no_supp.png` (a full transfer) and hand-named renders such as
  `SIA.png` are also accepted, and the build asserts the filename agrees with
  the kept/suppressed flags in the metadata.

Any frame taller than 512 px carries a rendered caption strip underneath the
result image, so the script crops every frame back to its top 512 rows. Edit
labels, titles, subject classes and edit types live in the `SAMPLES` /
`EXAMPLES` tables at the top of `build_images.py` — that is the one place to
change wording or add a new sample.

## Type

Same families the [TokenVerse](https://token-verse.github.io/) project page
uses: Google Sans for display type, falling back to Noto Sans exactly as it
does there, Noto Sans for text, and Castoro for the italic *A* / *A'* / *B* /
*B'* image variables. Monospace labels use the system mono stack.

## Sizing

Every image block is driven by one custom property in `:root`
(`--res-h`, `--pair-h`, `--wipe-h`, `--demo-h`, `--teaser-h`, `--arch-h`), each
a `clamp(min, Nvh, max)`. Widths follow from the stored aspect ratio, so the
interactive Results section lands inside a single screen on a 900px-tall
window and shrinks with the viewport rather than forcing a scroll. Change one
of those clamps to rescale a whole block.

## Local preview

```bash
python -m http.server 8000
# open http://127.0.0.1:8000
```

## Deployment

Already live and wired up: **Settings → Pages → Source** is set to
**GitHub Actions**, and `.github/workflows/pages.yml` runs on every push to
`main`. Nothing to click — push and the site updates in about a minute.

The workflow deletes `new figures/` and `tools/` from the artifact before
uploading, so the published site is ~9 MB rather than ~42 MB. Jekyll is off
(`.nojekyll`), so paths starting with `_` and the `static/` tree are served
verbatim.

## Two things to confirm before announcing

1. **BibTeX track.** `index.html` cites the paper as
   `@inproceedings{... booktitle = {SIGGRAPH Asia 2026 Conference Papers} ...}`.
   If it was accepted to the journal (TOG) track instead, switch it to
   `@article` with `journal = {ACM Transactions on Graphics}` plus volume,
   number and DOI.
2. **arXiv link.** The masthead has a ready-made arXiv button commented out
   right above the *Code* button. Uncomment it and drop in the identifier once
   the preprint is live.

## Credit

Page design adapted from the [Nerfies](https://nerfies.github.io) project page,
licensed [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).
