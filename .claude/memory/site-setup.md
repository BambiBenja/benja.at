# Site setup

Jekyll site hosted on GitHub Pages at https://benja.at.

- **Gemfile** uses the `github-pages` gem so local builds match what GitHub Pages runs
  (Jekyll 3.x). `webrick` is added for `jekyll serve` on Ruby 3+.
- **No theme**: `_config.yml` has `theme: null`. Otherwise GitHub Pages silently applies
  `jekyll-theme-primer`. All styling comes from our own files.
- **Layout**: a single layout, `_layouts/default.html` (header, main, footer).
  Pages use `layout: default` in their front matter.
- **Stylesheet**: `assets/css/main.css`. It's named `main.css` for historical reasons,
  not because `style.css` would clash. (An early assumption that it clashed with the
  Primer theme turned out to be wrong.)
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
