This is the source for the Website served at benja.at.
Benja will want to create that website together with you. Please help them through the process.
They do not currently know html/css/markdown, but may want to learn and edit things themselves.

Please be creative about getting input for the site from them.
If they seem to have trouble expressing something so that you understand what they want, maybe they can provide a drawing or a Canva sketch of what they'd like.
Or anything else you can think of.
They can also edit individual files through the github interface directly.

I suggest working only on the main branch, except if there is a real reason to do otherwise, because that will be less confusing for Benja to understand.

I suggest keeping documentation about how things are set up and memories inside this .claude folder in the repo.

## Checking changes

Run `.claude/scripts/check.sh` after every change to the site, before committing. It builds
the site, validates the HTML and CSS with the W3C Nu Html Checker, and reports links and
images that point to files that don't exist. It takes a few seconds (in a fresh container,
a minute or two the first time, to install the gems and the validator). Fix what it reports
before pushing: GitHub Pages takes a few minutes to publish, so it's much quicker to catch
mistakes here than on the live site.

Errors name files in `_site/`, the generated site. Fix them in the source: a layout in
`_layouts/`, the page's own `.md` or `.html` file, or the stylesheet in `assets/css/`.

Benja may edit files directly on GitHub. At the start of every session, `git pull` and run
the check. If it finds problems, look at the recent commits (`git log`, `git show`) to see
what changed, explain the problem to Benja in plain words, and offer to fix it, or to walk
them through fixing it themselves if they'd like to learn. Don't silently rewrite Benja's
changes. Also look over their recent changes for things the check can't catch, such as a
new page that nothing links to, or a very large photo that will make the page slow.

## Previewing changes

To show Benja the page you're working on before it's live (or before deciding to keep a
change), publish a preview as a claude.ai Artifact instead of waiting for GitHub Pages:

1. Run `python3 .claude/scripts/sitetools.py preview /about/`, giving the page's address on
   the site (`/` for the home page). It builds the site and writes the page, with its
   stylesheet and images built in, to `_preview/preview.html` (ignored by git).
2. Publish `_preview/preview.html` with the Artifact tool. Update the existing preview
   Artifact (its link is in [memory/previews.md](memory/previews.md)) rather than creating
   a new one each time.

## Memory

@memory/MEMORY.md
