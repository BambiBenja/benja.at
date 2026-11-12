# Design (Reh-Theme)

Benja's wishes (Nov 2026): deer ("Reh") theme; deer-fur background that stays fixed while
scrolling; fun but readable type. Second round of feedback (same month):

- Liked: the title wiggling on hover, the three-dot `<hr>`, the fur.
- Disliked: Fraunces ("country/Jäger/homestead"), the opaque cream card, rounded corners,
  the dashed seam, the brownish-orange headings, too many colours (green is out).
- Wants: clear, modern type, "like Broadway but less theatrical", fitting the fur; the
  text box translucent (they suggested light pink); a shape that is either plain or truly
  irregular (we went plain: square corners); colours dark brown, orange/yellow, pink/rosa
  only, with brown "clearly darker"; a menu icon top left/right.

Current state:

- **Background**: `assets/images/rehfell.jpg`, painted by `.claude/scripts/fur.py`
  (`spots` = fawn spots, current; `plain` = no spots). Fixed via `body::before
  { position: fixed }` (`background-attachment: fixed` doesn't work on iPhones).
- **Content box** (`main`): translucent light pink (`--kasten`, rgba alpha 0.66) with a 3px
  backdrop blur, square corners, soft shadow. Lower alpha shows more fur but costs contrast.
- **Fonts**, self-hosted in `assets/fonts/` (Google Fonts from Google's servers is a GDPR
  problem in Austria): Playfair Display 900 (title, headings, menu) and Jost (body, plus
  italic), from the npm `@fontsource-variable/*` packages, latin subset, OFL licences beside.
  Font comparison Artifact for Benja: https://claude.ai/artifact/23ZHRAqfi7wPiaAkHXoJEa
  (options A–G; source isn't in the repo, it was a one-off page).
- **Colours**: CSS variables at the top of `assets/css/style.css` with German comments:
  dunkelbraun (text, h1), orange (h2, bold, list dots), pink (h3, links, italic),
  gelb (menu highlight, text selection), rosa (title/footer on the fur), kasten.
- **Menu**: `<details class="menu">` fixed top right in `_layouts/default.html`, entries
  from `_data/menu.yml` (titel/link, German comments so Benja can add pages).
  `assets/js/menu.js` closes it on outside click or Esc.
- **Pages**: `traeume.md`, `fantasien.md`, `verzweiflungen.md` (placeholders), linked from
  the menu and from the bullets on the home page.
