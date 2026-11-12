# Design (Reh-Theme)

Benja's wishes (Nov 2026): deer ("Reh") theme; deer-fur background that stays fixed while
scrolling; a font that is fun but readable and not too playful; text in brown, orange,
green and pink ("am besten alles").

- **Background**: `assets/images/rehfell.jpg`, a fur texture painted by
  `.claude/scripts/fur.py` (no photo, so no licence questions). `spots` = fawn spots
  (current), `plain` = plain fur. ~400 KB; fur detail doesn't compress much smaller.
  Fixed via `body::before { position: fixed }` rather than `background-attachment: fixed`,
  which doesn't work on iPhones.
- **Content** sits on a cream card (`main`) with a dashed pink "seam".
- **Fonts**, self-hosted in `assets/fonts/` (not loaded from Google: Google Fonts from
  Google's servers is a GDPR problem in Austria): Fraunces (headings and site title, with
  the SOFT and WONK axes for the fun look) and Nunito (body, plus italic). Both from the
  npm packages `@fontsource-variable/fraunces` / `nunito`, latin subset, OFL licences next
  to the files.
- **Colours** are CSS variables at the top of `assets/css/style.css`, with German
  comments so Benja can change them: braun (text), orange (h1, bold), grün (h2, links),
  pink (h3, italic, link hover), creme (card).
- `<hr>` (`---` in Markdown) shows as three coloured dots; list markers are coloured per level.
