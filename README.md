# Moonlake — Portfolio

Self-contained landing page for **Moonlake**, a Blender-native 3D asset-generation agent for game studios, indie devs, Roblox creators, and technical artists. Moonlake covers the stretch of production between idea and usable 3D world — props, environment kits, terrain dressing, modular assets, and procedural asset systems.

**Live:** https://jennifer-rong.github.io/moonlake-portfolio/portfolio.html · **Local:** open `portfolio.html` in any browser (all images are embedded — no server, no dependencies, works offline).

## Contents

| File | Purpose |
|---|---|
| `portfolio.html` | Built, shareable page (~6.9 MB, images embedded as base64) |
| `build_portfolio.py` | Generator — all page content, copy, and layout live here |
| `assets/` | Source renders (chibi + semi-realistic) and logo lockups |

## Rebuilding

Content and layout are edited in `build_portfolio.py`; it resizes the images in `assets/`, embeds them, and writes `portfolio.html`. To regenerate and publish:

```bash
python3 build_portfolio.py                              # rebuild portfolio.html
git add -A && git commit -m "Update portfolio" && git push   # GitHub Pages redeploys in ~1 min
```

Requires macOS — image resizing uses the built-in `sips`; no other dependencies.

## Notes

- Renders are labeled **Preview** — early example outputs, not production-ready Blender files.
- The page uses a near-monochrome editorial design; the carousel browses assets by style (semi-realistic / chibi) with a drag-to-switch control.
