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

Every image block is driven by a custom property in `:root`, shaped as
`clamp(floor, min(Nvh, Mvw), ceiling)`:

* `min(Nvh, Mvw)` takes whichever viewport dimension is scarcer, so a portrait
  tablet and a wide monitor both get a size that fits without a breakpoint.
* the ceiling is the **native pixel height of the source render** (512 px for
  the result crops, 1570 / 1088 for the two figure PDFs) — past it the browser
  is only upscaling.
* `--pair-h` and `--demo-h` are `calc()`ed from `--res-h` / `--wipe-h`, so the
  columns beside them stay level at every screen size.

Widths come from `calc(height * aspect-ratio)` with `max-width` clamping —
never `width: min(100%, ...)`, which is a circular percentage inside an
auto-sized grid track and silently collapses. `--wide` follows the viewport
too (`min(94vw, 1480px)`), so figures keep growing on large displays.

Below 760 px the layout is one column and these are pinned to the column width
instead, since there the column and not the viewport height is the constraint.

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
