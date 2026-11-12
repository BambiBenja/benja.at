#!/usr/bin/env python3
"""Helpers for working on the built site in _site/.

Commands:
  links    Report links, images, stylesheets and scripts that point to files
           that don't exist in the built site.
  preview  Turn the built site into a preview that can be published as a
           claude.ai Artifact: every page becomes one self-contained HTML file
           (stylesheets, scripts, images and fonts inlined), and links between
           pages are rewritten so they work inside the Artifact.

Run .claude/scripts/build.sh first (the preview command does it for you unless
--no-build is given). Uses only the Python standard library.
"""

import argparse
import base64
import html
import json
import mimetypes
import os
import posixpath
import re
import shutil
import subprocess
import sys

REPO = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
).stdout.strip()
SITE = os.path.join(REPO, "_site")

EXTRA_TYPES = {
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".ico": "image/x-icon",
}

# Attributes whose value is a URL, per tag.
URL_ATTRS = {
    "a": ["href"],
    "link": ["href"],
    "img": ["src", "srcset"],
    "source": ["src", "srcset"],
    "script": ["src"],
    "video": ["src", "poster"],
    "audio": ["src"],
}

TAG_RE = re.compile(r"<(a|link|img|source|script|video|audio)\b([^>]*)>", re.I)
ATTR_RE = re.compile(r"""([\w:-]+)\s*=\s*("([^"]*)"|'([^']*)')""")
CSS_URL_RE = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""")


def is_external(url):
    """True for URLs that don't point into the site (other sites, mailto:, #anchors...)."""
    return (
        not url
        or url.startswith("#")
        or url.startswith("//")
        or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) is not None
    )


def split_url(url):
    """Split 'path?query#fragment' into (path, '?query#fragment')."""
    m = re.match(r"([^?#]*)(.*)", url)
    return m.group(1), m.group(2)


def resolve(url, from_file):
    """Map a URL found in `from_file` (path relative to _site) to a file in _site.

    Returns the file's path relative to _site, or None if it doesn't exist.
    Handles the same forms GitHub Pages does: /dir/ -> /dir/index.html and
    /page -> /page.html.
    """
    path, _ = split_url(html.unescape(url))
    if path.startswith("/"):
        target = path.lstrip("/")
    else:
        target = posixpath.join(posixpath.dirname(from_file), path)
    target = posixpath.normpath(target)
    if target == "." or target.startswith(".."):
        target = "" if target == "." else target
    candidates = [target, posixpath.join(target, "index.html"), target + ".html"]
    for c in candidates:
        if c and not c.startswith("..") and os.path.isfile(os.path.join(SITE, c)):
            return c
    if target == "" and os.path.isfile(os.path.join(SITE, "index.html")):
        return "index.html"
    return None


def site_files(ext=None):
    for root, _, files in os.walk(SITE):
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(root, name), SITE).replace(os.sep, "/")
            if ext is None or rel.endswith(ext):
                yield rel


def read(rel):
    with open(os.path.join(SITE, rel), encoding="utf-8") as f:
        return f.read()


def srcset_urls(value):
    return [part.strip().split()[0] for part in value.split(",") if part.strip()]


def urls_in_tag(tag, attrs):
    for name in URL_ATTRS.get(tag.lower(), []):
        if name in attrs:
            if name == "srcset":
                yield from srcset_urls(attrs[name])
            else:
                yield attrs[name]


def parse_attrs(text):
    return {m.group(1).lower(): (m.group(3) if m.group(3) is not None else m.group(4))
            for m in ATTR_RE.finditer(text)}


# ---------------------------------------------------------------- links


def cmd_links(_args):
    if not os.path.isdir(SITE):
        sys.exit("error: _site/ doesn't exist; run .claude/scripts/build.sh first")
    problems = []
    for page in site_files(".html"):
        for m in TAG_RE.finditer(read(page)):
            tag, attrs = m.group(1), parse_attrs(m.group(2))
            for url in urls_in_tag(tag, attrs):
                if not is_external(url) and resolve(url, page) is None:
                    problems.append(f"{page}: <{tag}> points to '{url}', which doesn't exist")
    for css in site_files(".css"):
        for m in CSS_URL_RE.finditer(read(css)):
            url = m.group(2)
            if not is_external(url) and resolve(url, css) is None:
                problems.append(f"{css}: url({url}) points to a file that doesn't exist")
    for p in problems:
        print(p)
    if problems:
        print(f"{len(problems)} broken link(s) or missing file(s).")
        return 1
    print("No broken links or missing files.")
    return 0


# ---------------------------------------------------------------- preview

# Published as the Artifact's main page, the home page is wrapped in a
# skeleton with its own small reset (14px font, zero body margin, ...).
# Undo it, so the page falls back to browser defaults like the real site.
# Declared before the site's own CSS, so the site's rules still win.
UNDO_ARTIFACT_RESET = (
    "<style>/* preview: undo the Artifact page reset */"
    ":root{color-scheme:normal}body{margin:revert;font:revert}img{max-width:revert}"
    "</style>"
)


def data_uri(rel):
    ext = posixpath.splitext(rel)[1].lower()
    mime = EXTRA_TYPES.get(ext) or mimetypes.guess_type(rel)[0] or "application/octet-stream"
    with open(os.path.join(SITE, rel), "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


class Previewer:
    def __init__(self, out, home, title):
        self.out = out
        self.home = home
        self.title = title
        self.warnings = []
        self.extra_files = set()  # non-HTML files that pages link to (PDFs etc.)

    def warn(self, msg):
        self.warnings.append(msg)

    def inline_css_urls(self, css, css_file):
        def repl(m):
            url = m.group(2)
            if is_external(url):
                return m.group(0)
            target = resolve(url, css_file)
            if target is None:
                self.warn(f"{css_file}: url({url}) not found")
                return m.group(0)
            return f'url("{data_uri(target)}")'

        if "@import" in css:
            self.warn(f"{css_file}: @import isn't inlined; the imported file won't load in the preview")
        return CSS_URL_RE.sub(repl, css)

    def link_target(self, url, page):
        """New href for an internal link, relative to the page's own location."""
        path, rest = split_url(url)
        if path == "":
            return url  # '?x' or '#x' on the same page
        target = resolve(url, page)
        if target is None:
            self.warn(f"{page}: link to '{url}' not found")
            return url
        if not target.endswith(".html"):
            self.extra_files.add(target)
        rel = posixpath.relpath(target, posixpath.dirname(page) or ".")
        return rel + rest

    def rewrite_tag(self, m, page):
        tag, attr_text = m.group(1), m.group(2)
        lower = tag.lower()
        attrs = parse_attrs(attr_text)

        if lower == "link" and "stylesheet" in attrs.get("rel", "").lower().split():
            href = attrs.get("href", "")
            if is_external(href):
                return m.group(0)
            target = resolve(href, page)
            if target is None:
                self.warn(f"{page}: stylesheet '{href}' not found")
                return m.group(0)
            media = f' media="{attrs["media"]}"' if "media" in attrs else ""
            return f"<style{media}>\n{self.inline_css_urls(read(target), target)}\n</style>"

        def replace_attr(name, new_value):
            nonlocal attr_text
            attr_text = re.sub(
                rf"""(\b{re.escape(name)}\s*=\s*)("[^"]*"|'[^']*')""",
                lambda a: a.group(1) + '"' + new_value.replace('"', "&quot;") + '"',
                attr_text,
                count=1,
                flags=re.I,
            )

        for name in URL_ATTRS.get(lower, []):
            if name not in attrs:
                continue
            value = attrs[name]
            if lower == "a" or (lower == "link" and name == "href"
                                and "icon" not in attrs.get("rel", "").lower()):
                if not is_external(value):
                    replace_attr(name, self.link_target(value, page))
                continue
            if lower == "script":
                continue  # handled in rewrite_scripts
            if name == "srcset":
                parts = []
                for part in value.split(","):
                    bits = part.strip().split(None, 1)
                    if not bits:
                        continue
                    url = bits[0]
                    if not is_external(url):
                        target = resolve(url, page)
                        if target:
                            url = data_uri(target)
                        else:
                            self.warn(f"{page}: image '{bits[0]}' not found")
                    parts.append(" ".join([url] + bits[1:]))
                replace_attr(name, ", ".join(parts))
                continue
            if not is_external(value):
                target = resolve(value, page)
                if target is None:
                    self.warn(f"{page}: '{value}' not found")
                else:
                    replace_attr(name, data_uri(target))
        return f"<{tag}{attr_text}>"

    def rewrite_scripts(self, text, page):
        def repl(m):
            attrs = parse_attrs(m.group(1))
            src = attrs.get("src", "")
            if is_external(src):
                return m.group(0)
            target = resolve(src, page)
            if target is None:
                self.warn(f"{page}: script '{src}' not found")
                return m.group(0)
            kind = f' type="{attrs["type"]}"' if "type" in attrs else ""
            code = read(target).replace("</script", "<\\/script")
            return f"<script{kind}>\n{code}\n</script>"

        return re.sub(r"<script\b([^>]*\bsrc\s*=[^>]*)>\s*</script>", repl, text, flags=re.I)

    def rewrite_inline_styles(self, text, page):
        def repl(m):
            return m.group(1) + self.inline_css_urls(m.group(2), page) + m.group(3)

        return re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", repl, text, flags=re.I | re.S)

    def as_main_page(self, text):
        """Strip the document wrapper: the Artifact adds its own skeleton."""
        head = re.search(r"<head\b[^>]*>(.*?)</head>", text, re.I | re.S)
        body = re.search(r"<body\b([^>]*)>(.*?)</body>", text, re.I | re.S)
        if not head or not body:
            self.warn(f"{self.home}: no <head>/<body> found; published as is")
            return text
        head_html = head.group(1)
        head_html = re.sub(r"<meta\s+charset[^>]*>\s*", "", head_html, flags=re.I)
        head_html = re.sub(r"<meta\s+name=[\"']viewport[\"'][^>]*>\s*", "", head_html, flags=re.I)
        head_html = re.sub(r"<title>.*?</title>\s*", "", head_html, flags=re.I | re.S)
        lang = re.search(r"<html\b[^>]*\blang=[\"']([^\"']+)", text, re.I)
        set_attrs = []
        if lang:
            set_attrs.append(f"document.documentElement.lang={json.dumps(lang.group(1))};")
        for name, value in parse_attrs(body.group(1)).items():
            set_attrs.append(f"document.body.setAttribute({json.dumps(name)},{json.dumps(value)});")
        script = f"<script>{''.join(set_attrs)}</script>\n" if set_attrs else ""
        return (
            f"<title>{html.escape(self.title)}</title>\n"
            f"{UNDO_ARTIFACT_RESET}\n{head_html.strip()}\n{script}{body.group(2).strip()}\n"
        )

    def page(self, rel):
        text = read(rel)
        text = self.rewrite_scripts(text, rel)
        text = self.rewrite_inline_styles(text, rel)
        text = TAG_RE.sub(lambda m: self.rewrite_tag(m, rel), text)
        if rel == self.home:
            text = self.as_main_page(text)
        dest = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(text)
        return dest


def cmd_preview(args):
    if not args.no_build:
        subprocess.run([os.path.join(REPO, ".claude/scripts/build.sh")], check=True)
    if not os.path.isfile(os.path.join(SITE, args.home)):
        sys.exit(f"error: _site/{args.home} doesn't exist")

    out = os.path.abspath(args.out)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    title = args.title
    if title is None:
        config = open(os.path.join(REPO, "_config.yml"), encoding="utf-8").read()
        m = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", config, re.M)
        title = f"{m.group(1) if m else 'Site'} preview"

    p = Previewer(out, args.home, title)
    files = {}
    for rel in site_files(".html"):
        dest = p.page(rel)
        if rel != args.home:
            files[rel] = dest
    for rel in sorted(p.extra_files):
        dest = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(SITE, rel), dest)
        files[rel] = dest

    main = os.path.join(out, args.home)
    manifest = {"file_path": main, "files": files}
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    limit = 15 * 1024 * 1024
    for path in [main, *files.values()]:
        size = os.path.getsize(path)
        if size > limit:
            p.warn(f"{os.path.relpath(path, out)} is {size / 1e6:.1f} MB; "
                   "the Artifact limit is 16 MB per page (15 MB per other file)")

    for w in p.warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(json.dumps(manifest, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("links", help="report broken internal links and missing files")
    pv = sub.add_parser("preview", help="build a self-contained Artifact preview")
    pv.add_argument("--out", default=os.path.join(REPO, "_preview"),
                    help="output folder (default: _preview/ in the repo, which git ignores)")
    pv.add_argument("--home", default="index.html",
                    help="page to publish as the Artifact's main page (default: index.html)")
    pv.add_argument("--title", help="Artifact title (default: '<site title> preview')")
    pv.add_argument("--no-build", action="store_true", help="use the existing _site/")
    args = parser.parse_args()
    sys.exit(cmd_links(args) if args.command == "links" else cmd_preview(args))


if __name__ == "__main__":
    main()
