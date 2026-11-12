# benja.at

Personal website, built with [Jekyll](https://jekyllrb.com/) and hosted on GitHub Pages.

## Run locally

```bash
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.

## Check the site

```bash
.claude/scripts/check.sh
```

Builds the site and reports invalid HTML or CSS, and links or images that point to
files that don't exist. Needs Java and npm for the HTML/CSS validator.
