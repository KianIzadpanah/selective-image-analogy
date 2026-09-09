# SIA: Selective Image Analogy — project page

Project page for **SIA: Selective Image Analogy**, SIGGRAPH Asia 2026.

**Live site:** <https://selective-image-analogy.github.io/>

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

## Design system

Warm paper ground (`#F8F7F4`), deep-blue chrome (`#1E4F7F`), and the paper's
own green/red for retained vs suppressed edits. Blue is reserved for interface
furniture — links, eyebrows, focus rings — so it never competes with that
semantic pair. Every colour is a token in `:root`, mirrored under
`:root[data-theme="dark"]`.

Type is Source Serif 4 for display, Noto Sans for text and JetBrains Mono for
labels and code. Surfaces share three radii (6 / 10 / 14 px), a 1 px rule and
two soft shadows.

Figures and tables are framed, with the caption *inside* the frame under a
hairline — so caption text is always exactly as wide as the thing it
describes.

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

The site is served from the organization repo
[`selective-image-analogy/selective-image-analogy.github.io`](https://github.com/selective-image-analogy/selective-image-analogy.github.io),
which GitHub publishes at the domain root — so the relative `static/...` paths
work unchanged.

`.github/workflows/pages.yml` runs on every push to `main` (and can be run by
hand from the Actions tab). **Settings -> Pages -> Source** is **GitHub
Actions**. The workflow deletes `new figures/` and `tools/` from the artifact
before uploading, so the published site is ~9 MB rather than ~42 MB. Jekyll is
off (`.nojekyll`), so paths starting with `_` and the `static/` tree are served
verbatim.

If Pages is ever re-enabled from a branch instead, it will publish the *whole*
repository, sources included; flipping Source back to GitHub Actions and
re-running the workflow fixes it.

### Remotes

```
site    selective-image-analogy/selective-image-analogy.github.io   <- the live site
origin  KianIzadpanah/selective-image-analogy                       <- the original repo
```

Push to `site` to publish. `origin` still serves an older copy of the page at
`kianizadpanah.github.io/selective-image-analogy`; every canonical/OG URL in
`index.html` points at the new domain, so search engines will settle on it, but
the old page can be turned off in that repo's Pages settings whenever you like.

## Loose ends

1. **BibTeX track.** `index.html` cites the paper as
   `@inproceedings{... booktitle = {SIGGRAPH Asia 2026 Conference Papers} ...}`.
   If it was accepted to the journal (TOG) track instead, switch it to
   `@article` with `journal = {ACM Transactions on Graphics}` plus volume,
   number and DOI.
2. **arXiv and Code buttons** in the masthead are inert `<span class="btn
   pending">` placeholders. Turn each back into an `<a href="...">` once the
   preprint and the repo are public.
3. **The paper PDF** is still at `static/pdfs/SIA_paper.pdf` but nothing links
   to it. Add a button back to the masthead when it should be public.
4. **Studio portrait** reads *combination n / 7* rather than 8 because
   `all_is_correct/3` has no `no_supp.png`. Render that full transfer and the
   build picks it up.

## Credit

Layout and typography take their cue from the
[Nerfies](https://nerfies.github.io) and
[HairPort](https://deepmancer.github.io/HairPort/) project pages. Released
under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).
