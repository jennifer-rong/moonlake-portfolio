# Moonlake — Portfolio

A single self-contained page for **Moonlake**, a Blender-native 3D asset-generation agent for game studios, indie devs, Roblox creators, and technical artists.

## View it

**Live:** https://jennifer-rong.github.io/moonlake-portfolio/portfolio.html

Or open `portfolio.html` locally in any browser — it's fully self-contained (all images are embedded), no server or dependencies needed.

## Editing

The page is generated from `build_portfolio.py`, which embeds the source images in `assets/` as base64 data URIs into `portfolio.html`. To regenerate after changing content or swapping renders:

```bash
python3 build_portfolio.py
```

Requires macOS (`sips` is used for image resizing — no other dependencies).

### Files
- `portfolio.html` — the built, shareable page
- `build_portfolio.py` — generator (content + layout live here)
- `assets/` — source render and logo images
