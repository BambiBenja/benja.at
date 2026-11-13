# Generated and downloaded assets

**Rule:** anything Claude generates for the site (images, textures, icons, data) gets its
generator committed to `.claude/scripts/`, and an entry below saying how to rebuild it.
Anything downloaded gets its exact source and command recorded below. Then a later session
can change or rebuild it instead of starting over. One-off previews for Benja (Artifacts)
are exempt unless their result ends up on the site.

## `assets/images/rehfell.jpg` (fur background)

- Made by `.claude/scripts/fur.py` (Python with numpy and Pillow; no network):
  `python3 .claude/scripts/fur.py assets/images/rehfell.jpg spots`
  (`plain` instead of `spots` = fur without fawn spots).
- Deterministic: fixed seed `default_rng(7)`; checked Nov 2026 that a rerun is
  byte-identical (numpy 2.5.3, Pillow 12.3.0; other versions may differ slightly).
- How it works, for tweaking: a dark-brown undercoat with soft blotches; three layers of
  short two-segment strands drawn along a swirling angle field (`flow()`: sums of sines,
  mostly pointing down-right), colours from `palette`/`weights`; for `spots`, a blurred
  mask of cream ellipses in loose diagonal rows (row/column spacing, skip chance and radius
  in the spots loop), then more strands over it so the spots look furry. Drawn at 2× and
  downscaled, lightly sharpened then blurred 0.5 px, JPEG quality 72 (~400 KB; fur detail
  doesn't compress much smaller).

## `assets/fonts/*` (self-hosted fonts)

- From npm (Fontsource), latin subset; licence files copied next to them:
  ```bash
  npm pack @fontsource/syncopate @fontsource/kedebideri
  ```
  (pack each separately: one failing name makes `npm pack` skip the rest). Unpack and copy
  `package/files/syncopate-latin-{400,700}-normal.woff2` → `syncopate-{400,700}.woff2`,
  `package/files/kedebideri-latin-{400,500,700}-normal.woff2` → `kedebideri-{400,500,700}.woff2`,
  and `package/LICENSE` → `LICENSE-syncopate.txt` / `LICENSE-kedebideri.txt`.
  Versions used: 5.3.0 of both packages.
