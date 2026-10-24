# moistlab-site

Source for [moistlab.dev](https://moistlab.dev): notes on learning IT security, in a grey theme with the MoistRex mascot.

A small static-site builder, no framework. Notes are Markdown, `build.py` turns them into plain HTML in `docs/`, and GitHub Pages serves that folder.

## Add a note

1. Copy `src/posts/_template.md` to `src/posts/YYYY-MM-DD-short-name.md` and fill it in (Goal, Steps, Snag, Next time).
2. `python3 build.py` (needs `pip install markdown`).
3. Commit and push. Pages publishes `docs/`.

Files starting with `_` are templates and are not built.

## Layout

- `src/posts/` notes, `src/pages/` plain pages, `src/assets/` css, fonts, images
- `docs/` the built site (generated, committed because Pages serves it)

Fonts: JetBrains Mono (SIL Open Font License), subset to Latin and served from the site itself. No scripts, no trackers, no third-party requests.
