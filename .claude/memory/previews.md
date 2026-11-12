# Previews

- Preview Artifact for the site: https://claude.ai/artifact/V6vx18thpwApfyVmnoZxFY
  (created by the account that set up this repo). To update it from a new session, publish
  with `url` set to this link. Read it first with the Artifact tool's `read` action, as
  the tool requires. If this session's account can't update it, create a new one, and
  replace the link here.
- It's private: other people (such as Benja, if they use their own account) can only open
  it once it's shared with them from the page's Share menu.
- How the preview script works (`.claude/scripts/sitetools.py preview`):
  - The home page becomes the Artifact's main page. The Artifact wraps it in its own
    skeleton, so the script strips `<html>`/`<head>`/`<body>` and adds a style that undoes
    the skeleton's reset (14px font, zero body margin), so the preview matches the real site.
  - The other pages are published as extra files and keep their full HTML. Links between
    pages are rewritten to relative paths.
  - Stylesheets, scripts, images and fonts are inlined as `<style>`, `<script>` and
    `data:` URIs. Linked non-HTML files (PDFs etc.) are copied and published as files.
- Limits: in the preview, links to other websites open in a new tab, and external scripts,
  fonts or images only load from the hosts Artifacts allow (Google Fonts, cdnjs, jsDelivr,
  unpkg). On the real site they work normally.
