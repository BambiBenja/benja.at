# Site setup

Jekyll site hosted on GitHub Pages at https://benja.at.

- **Gemfile** uses the `github-pages` gem so local builds match what GitHub Pages runs
  (Jekyll 3.x). `webrick` is added for `jekyll serve` on Ruby 3+.
- **No theme**: `_config.yml` has `theme: null`. Otherwise GitHub Pages silently applies
  `jekyll-theme-primer`. All styling comes from our own files.
- **Layout**: a single layout, `_layouts/default.html` (header, main, footer).
  Pages use `layout: default` in their front matter.
- **Stylesheet**: `assets/css/style.css`, linked from the layout. Light colors only: no
  automatic dark mode (turned off on purpose so color changes stay simple for Benja).
  Text and background colors are set on `body`. No full CSS reset (Markdown content relies
  on default spacing); only `box-sizing: border-box` and `img { max-width: 100% }`.
- **Pages**: `index.md` (home) and `404.md` (published as `/404.html`).
- **`exclude` in `_config.yml`**: setting it replaces Jekyll's default list, so `vendor/`
  and `.bundle/` are listed explicitly. Without that, a local `bundle install` into
  `vendor/` breaks the build. Files and folders starting with `.` (such as `.claude/`) are
  never published.
- **Custom domain**: the `CNAME` file contains `benja.at`. DNS and the Pages settings are
  managed on GitHub and at the domain registrar, not in this repo.

## Building locally

```bash
bundle install
bundle exec jekyll serve
```

In the Claude cloud container: install with `BUNDLE_PATH=vendor/bundle`, and build with
`bundle exec jekyll build` to check that the site still builds before pushing.

## Tooling (in `.claude/scripts/`)

- `build.sh`: installs the gems if needed and builds `_site/`.
- `check.sh`: builds, then validates HTML/CSS with vnu (Nu Html Checker, from the npm package
  `vnu-jar`, pinned in the script and installed to `~/.cache/benja-at-tools`; needs Java),
  then runs `sitetools.py links`. vnu's "trailing slash on void elements" notes are
  filtered out: the Markdown converter generates `<img ... />` and we can't change that.
- The Markdown converter (kramdown) repairs broken HTML inside `.md` files on its own
  (it closes tags and escapes stray ones), so the validator mostly finds problems in
  `.html` files and layouts.
- `sitetools.py`: `links` (broken internal links/images) and `preview` (see previews.md).- The "benja.at" cloud environment (personal, owned by the account that set up this repo) has a
  setup script that runs `bundle install` (with `BUNDLE_PATH=vendor/bundle`) and installs
  `vnu-jar` into `~/.cache/benja-at-tools`, so checks run straight away in new sessions. If
  you change the vnu version in `check.sh`, the setup script still installs the old one
  and `check.sh` installs the new one itself; update the setup script too if you can.
