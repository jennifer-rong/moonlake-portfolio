#!/usr/bin/env python3
"""Generate a self-contained portfolio.html for Moonlake AI with base64-embedded renders.

Sales-forward single page: full-bleed wireframe hero (page paper is matched exactly
to the hero image's background so the banner is seamless), capability-led copy, and a
coverflow carousel where the focused asset is large and full-color while neighbors
recede (scaled down + faded). Near-monochrome paper base, heavy/thin type contrast.
"""
import base64
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"          # source PNGs (renders + logos)
BUILD = HERE / "_ml_build"        # resized, web-optimized intermediates

# key -> source filename in assets/. Renders are downscaled to 1400px max edge.
IMAGE_FILES = {
    "twin_simrobot": "twin_simrobot.png",
    "twin_conveyor": "twin_conveyor.png",
    "twin_cell": "twin_cell.png",
    "in_appliance": "in_appliance.png",
    "in_factory": "in_factory.png",
    "in_dock": "in_dock.png",
    "in_s6": "in_s6.png",
    "in_s6b": "in_s6b.png",
}
VIDEO_FILES = ["s6_output.mp4", "s6_left.mp4", "s7_sidebyside.mp4"]   # referenced (not base64)
LOGO_DARK_SRC = "Black Logo on White BG.png"          # black lockup -> light surfaces
LOGO_LIGHT_SRC = "moonlake_logo_white_transparent.png"  # white lockup -> dark surfaces
HERO_SRC = "hero_wireframes.png"                      # full-width hero banner
FAVICON_SRC = "site_icon.png"                         # exact Moonlake cube + crescent mark


def b64(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def resize(src: pathlib.Path, dst: pathlib.Path, max_edge: int) -> None:
    """Downscale via macOS `sips` (keeps aspect ratio)."""
    subprocess.run(
        ["sips", "-Z", str(max_edge), str(src), "--out", str(dst)],
        check=True, capture_output=True,
    )


def prepare() -> None:
    BUILD.mkdir(exist_ok=True)
    for fname in IMAGE_FILES.values():
        resize(ASSETS / fname, BUILD / fname, 1400)
    resize(ASSETS / LOGO_DARK_SRC, BUILD / "logo_dark.png", 800)
    resize(ASSETS / LOGO_LIGHT_SRC, BUILD / "logo_light.png", 800)
    resize(ASSETS / HERO_SRC, BUILD / "hero.png", 1800)
    resize(ASSETS / FAVICON_SRC, BUILD / "favicon.png", 256)
    # padded inputs are already at the video's aspect at native res; keep them sharp
    for f in ("in_s6.png", "in_s6b.png"):
        (BUILD / f).write_bytes((ASSETS / f).read_bytes())


def data_uri(path: pathlib.Path) -> str:
    return f"data:image/png;base64,{b64(path)}"


# Web fonts, embedded as base64 woff2: (family, weight, style, file)
FONT_FACES = [
    ("FK Grotesk SemiMono", "400", "normal", "FKGroteskSemiMono-Regular.woff2"),
    ("FK Grotesk SemiMono", "500", "normal", "FKGroteskSemiMono-Medium.woff2"),
    ("FK Grotesk SemiMono", "700", "normal", "FKGroteskSemiMono-Bold.woff2"),
    # STKSaga: used for the smaller description text
    ("STKSaga", "400", "normal", "STKSaga-Regular.woff2"),
    ("STKSaga", "500", "normal", "STKSaga-Medium.woff2"),
    ("STKSaga", "400", "italic", "STKSaga-Italic.woff2"),
]

# Credibility strip: (display name, simple-icons slug or None for name-only)
LOGO_ROW = [
    ("NVIDIA", "nvidia"),
    ("DeepMind", None),
    ("Anthropic", "anthropic"),
    ("Stanford", None),
    ("Meta", "meta"),
    ("Waymo", None),
    ("Autodesk", "autodesk"),
    ("AWS", "aws"),
]


def build_font_faces() -> str:
    faces = []
    for family, weight, style, fname in FONT_FACES:
        b = base64.b64encode((ASSETS / "fonts" / fname).read_bytes()).decode("ascii")
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:{style};"
            f"font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b}) format('woff2');}}"
        )
    return "\n".join(faces)


def build_logos() -> str:
    items = []
    for name, slug in LOGO_ROW:
        ic = ""
        if slug:
            svg = (ASSETS / "logos" / f"{slug}.svg").read_text(encoding="utf-8")
            ic = f'<span class="logo-ic" aria-hidden="true">{svg}</span>'
        items.append(f'<li>{ic}<span class="logo-tx">{name}</span></li>')
    one = "".join(items)
    # two identical copies -> seamless horizontal marquee (CSS animates -50%)
    return (
        f'<ul class="logos-row">{one}</ul>'
        f'<ul class="logos-row" aria-hidden="true">{one}</ul>'
    )


def main() -> None:
    prepare()
    images = {key: data_uri(BUILD / fname) for key, fname in IMAGE_FILES.items()}
    image_js = ",\n".join(f'    "{k}": "{v}"' for k, v in images.items())
    html = (
        TEMPLATE
        .replace("/*__IMAGES__*/", image_js)
        .replace("/*__FONTS__*/", build_font_faces())
        .replace("<!--__LOGOS__-->", build_logos())
        .replace("{{LOGO_DARK}}", data_uri(BUILD / "logo_dark.png"))
        .replace("{{LOGO_LIGHT}}", data_uri(BUILD / "logo_light.png"))
        .replace("{{HERO}}", data_uri(BUILD / "hero.png"))
        .replace("{{FAVICON}}", data_uri(BUILD / "favicon.png"))
    )
    out = HERE / "portfolio.html"
    out.write_text(html, encoding="utf-8")
    size_mb = out.stat().st_size / 1_048_576
    print(f"Wrote {out} ({size_mb:.2f} MB)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moonlake | Robotics simulation & digital twins</title>
<link rel="icon" type="image/png" href="{{FAVICON}}">
<style>
  /*__FONTS__*/
  :root {
    --paper: #f9f8f3;        /* matched exactly to the hero image background */
    --paper-2: #f1f0e9;
    --ink: #0d0d0e;
    --ink-2: #56524b;
    --ink-3: #918b80;
    --void: #000;
    --hair: #ddd8cc;
    --accent: #8d8b86;
    --maxw: 1280px;
    /* experiment: STKSaga for the smaller description copy */
    --font-desc: "STKSaga", "FK Grotesk SemiMono", -apple-system, sans-serif;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; scroll-padding-top: 90px; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "FK Grotesk SemiMono", "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Arial, sans-serif;
    font-size: 17px; line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "kern" 1;
  }
  .wrap { max-width: var(--maxw); margin: 0 auto; padding: 0 40px; }
  @media (max-width: 640px) { .wrap { padding: 0 22px; } }
  a { color: inherit; text-decoration: none; }
  img { display: block; }

  .kicker {
    font-size: 11px; font-weight: 700; letter-spacing: .28em;
    text-transform: uppercase; color: var(--ink-3);
  }
  .accent { color: var(--accent); }

  /* ---- top bar ---- */
  /* floating rounded glass pill */
  .topbar {
    position: fixed; top: 18px; left: 0; right: 0; z-index: 50; padding: 0 24px;
  }
  .topbar .wrap {
    display: flex; align-items: center; justify-content: space-between;
    height: 64px; padding: 0 16px 0 26px; max-width: var(--maxw); margin: 0 auto;
    border-radius: 999px;
    background: linear-gradient(180deg, rgba(255,255,255,.46), rgba(255,255,255,.14));
    backdrop-filter: saturate(180%) blur(36px);
    -webkit-backdrop-filter: saturate(180%) blur(36px);
    border: 1px solid rgba(255,255,255,.7);
    box-shadow:
      inset 0 1px 1.5px rgba(255,255,255,.98),
      inset 0 -3px 6px rgba(255,255,255,.30),
      inset 0 0 0 1px rgba(255,255,255,.12),
      0 16px 40px rgba(13,13,14,.13),
      0 3px 10px rgba(13,13,14,.07);
  }
  .brand img { height: 22px; }
  .topbar nav { display: flex; gap: 34px; }
  .topbar nav a {
    font-size: 11px; font-weight: 700; letter-spacing: .2em;
    text-transform: uppercase; color: var(--ink-2); transition: color .2s ease;
  }
  .topbar nav a:hover { color: var(--ink); }
  @media (max-width: 680px) { .topbar nav { display: none; } }

  /* ---- hero ---- */
  /* fills the viewport; copy bottom-aligned with a top floor so the
     headline always clears the fixed top bar */
  .hero {
    position: relative; border-bottom: 1px solid var(--hair);
    min-height: 100vh; min-height: 100svh;
    display: flex; flex-direction: column; justify-content: flex-end;
  }
  .hero-figure { position: absolute; inset: 0; line-height: 0; }
  .hero-figure img { width: 100%; height: 100%; object-fit: cover; object-position: right top; display: block; }
  /* live three.js geometry. the static PNG is hidden by default (no flash on load);
     it is only revealed if three.js can't run (reduced-motion, no JS, or CDN blocked). */
  .hero-fallback { opacity: 0; transition: opacity .6s ease; }
  .hero-figure.show-fallback .hero-fallback { opacity: 1; }
  @media (prefers-reduced-motion: reduce) { .hero-fallback { opacity: 1; } }
  .hero-canvas {
    position: absolute; inset: 0; width: 100%; height: 100%; display: block;
    opacity: 0; transition: opacity 1.2s ease; filter: blur(1.5px);
  }
  .hero-canvas.is-live { opacity: 1; }
  /* scrim grounds the copy: solid paper at the bottom-left fading up + right so the
     geometry stays visible top-right while the copy reads cleanly bottom-left */
  .hero::after {
    content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none;
    background:
      linear-gradient(to top, var(--paper) 24%, rgba(249,248,243,.74) 46%, rgba(249,248,243,0) 74%),
      linear-gradient(to right, rgba(249,248,243,.62) 0%, rgba(249,248,243,0) 52%);
  }
  .hero-copy { position: relative; z-index: 2; width: 100%; padding-top: clamp(100px, 14vh, 168px); padding-bottom: clamp(40px, 7vh, 88px); }
  .hero-copy .inner { max-width: var(--maxw); margin: 0 auto; padding: 0 40px; }
  .copy-block { max-width: 680px; }
  .hero .kicker { display: block; margin: 0 0 16px; }
  .hero h1 {
    font-size: clamp(40px, 6vw, 84px); line-height: .98;
    letter-spacing: -.04em; font-weight: 800; margin: 0; max-width: 17ch;
  }
  .hero-tagline {
    font-size: clamp(17px, 1.9vw, 26px); font-weight: 500; letter-spacing: -.01em;
    color: var(--ink-2); margin: 14px 0 0;
  }
  .hero-tagline .sep { color: var(--ink-3); margin: 0 10px; font-weight: 400; }
  .hero .lead {
    font-size: clamp(16px, 1.35vw, 19px); font-weight: 400;
    color: var(--ink-2); max-width: 54ch; margin: 26px 0 28px; line-height: 1.55;
  }

  /* ---- buttons (shared) ---- */
  .actions { display: flex; gap: 14px; flex-wrap: wrap; }
  .btn {
    position: relative; overflow: hidden;
    font-size: 12px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase;
    padding: 16px 30px; background: var(--paper); color: var(--ink); cursor: pointer;
    border: 1px solid transparent;
    transition: transform .25s ease, background .4s ease, border-color .4s ease, color .4s ease,
      box-shadow .4s ease, backdrop-filter .4s ease, -webkit-backdrop-filter .4s ease;
  }
  /* a light sweeps across the label on hover */
  .btn::before {
    content: ""; position: absolute; top: 0; left: -130%; width: 55%; height: 100%; z-index: 1;
    background: linear-gradient(100deg, transparent, rgba(255,255,255,.55) 50%, transparent);
    transform: skewX(-18deg); transition: left .6s cubic-bezier(.4,.05,.2,1); pointer-events: none;
  }
  .btn:hover::before { left: 150%; }
  .btn:hover { transform: translateY(-2px); }
  /* solid -> dark glass on hover */
  .btn.solid { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  .btn.solid:hover {
    background: rgba(255,255,255,.6); color: var(--ink); border-color: rgba(255,255,255,.85);
    backdrop-filter: blur(12px) saturate(170%); -webkit-backdrop-filter: blur(12px) saturate(170%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.95), 0 12px 30px rgba(13,13,14,.16);
  }
  /* outline -> lighter glass on hover */
  .btn.outline {
    background: linear-gradient(to bottom, rgba(255,255,255,.45), rgba(255,255,255,.14));
    color: var(--ink); border-color: var(--ink-3);
    backdrop-filter: blur(12px) saturate(170%);
    -webkit-backdrop-filter: blur(12px) saturate(170%);
    box-shadow: 0 1px 0 rgba(255,255,255,.7) inset, 0 6px 18px rgba(13,13,14,.06);
  }
  .btn.outline:hover {
    background: rgba(255,255,255,.6); color: var(--ink); border-color: rgba(255,255,255,.85);
    backdrop-filter: blur(12px) saturate(170%); -webkit-backdrop-filter: blur(12px) saturate(170%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.95), 0 12px 30px rgba(13,13,14,.16);
  }
  .btn.ghost { background: transparent; color: var(--paper); border-color: rgba(243,240,232,.32); }
  .btn.ghost:hover { background: rgba(243,240,232,.08); }

  /* ---- reusable section sub-copy ---- */
  .sec-sub {
    font-family: var(--font-desc);
    font-weight: 400; color: var(--ink-2); font-size: clamp(15px, 1.2vw, 17px);
    max-width: 66ch; margin: 16px 0 0; line-height: 1.55;
  }

  /* ---- section heads ---- */
  .work { min-height: calc(100vh - 90px); min-height: calc(100svh - 90px); display: flex; flex-direction: column; justify-content: center; padding: 40px 0 36px; }
  .work-head {
    display: flex; justify-content: space-between; align-items: flex-end;
    gap: 28px; flex-wrap: wrap; margin-bottom: 8px;
  }
  .work-head h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; line-height: 1.02; margin: 12px 0 0; max-width: 18ch;
  }
  /* ---- credibility logo marquee ---- */
  .logos { padding: 28px 0 0; }
  .logos-label { font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--ink-3); margin: 0 0 18px; }
  .marquee {
    position: relative; overflow: hidden; width: 100%;
    -webkit-mask-image: linear-gradient(to right, transparent 0, #000 9%, #000 91%, transparent 100%);
    mask-image: linear-gradient(to right, transparent 0, #000 9%, #000 91%, transparent 100%);
  }
  .marquee-track { display: flex; width: max-content; animation: logos-scroll 42s linear infinite; }
  .marquee:hover .marquee-track { animation-play-state: paused; }
  .logos-row { display: flex; align-items: center; gap: 68px; padding-right: 68px; list-style: none; margin: 0; }
  .logos-row li { display: inline-flex; align-items: center; gap: 13px; color: var(--ink-2); opacity: .9; flex: 0 0 auto; }
  .logo-ic { display: inline-flex; }
  .logo-ic svg { height: 30px; width: auto; fill: currentColor; display: block; }
  .logo-tx { font-size: clamp(20px, 2.2vw, 30px); font-weight: 700; letter-spacing: -.01em; white-space: nowrap; }
  @keyframes logos-scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  @media (prefers-reduced-motion: reduce) { .marquee-track { animation: none; } }
  @media (max-width: 760px) { .logo-ic svg { height: 24px; } .logos-row { gap: 48px; padding-right: 48px; } }

  /* ---- lookbook: input -> output flip cards ---- */
  .gallery { margin-top: 18px; }
  .g-main { display: grid; grid-template-columns: 1.5fr 1fr; gap: clamp(28px, 4vw, 64px); align-items: stretch; }
  .flip {
    position: relative; width: 100%; aspect-ratio: 1920 / 1040;
    perspective: 1700px; cursor: pointer; align-self: center;
  }
  .flip-inner {
    position: absolute; inset: 0; transform-style: preserve-3d;
    transition: transform .75s cubic-bezier(.4, .05, .2, 1);
  }
  .flip.flipped .flip-inner { transform: rotateY(180deg); }
  .flip-face {
    position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden;
    border: 1px solid var(--hair); border-radius: 6px; overflow: hidden; background: var(--paper-2);
  }
  .flip-back { transform: rotateY(180deg); }
  .flip-face img, .flip-face video { width: 100%; height: 100%; object-fit: cover; display: block; }
  #g-out-vid { display: none; }
  .flip-tag {
    position: absolute; top: 14px; left: 14px; z-index: 2;
    font-size: 10px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
    color: var(--ink-2); background: rgba(249,248,243,.92); padding: 6px 11px; border-radius: 2px;
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  }
  .flip-tag--out { color: var(--paper); background: rgba(13,13,14,.82); }
  /* faint curved-arrow affordance: clicking the card flips it */
  .flip-hint {
    position: absolute; bottom: 13px; right: 13px; z-index: 4; pointer-events: none;
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; line-height: 1; color: rgba(255,255,255,.92);
    background: rgba(13,13,14,.28); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    opacity: .6; transition: opacity .2s ease, background .2s ease;
  }
  .flip:hover .flip-hint { opacity: 1; background: rgba(13,13,14,.5); }
  /* single side-by-side video example (no flip): card matches the video aspect */
  .flip-single {
    position: absolute; inset: 0; z-index: 5; display: none;
    width: 100%; height: 100%; object-fit: cover; border-radius: 6px;
    border: 1px solid var(--hair); background: var(--paper-2);
  }
  .flip.is-single { cursor: default; aspect-ratio: 1440 / 1280; width: auto; height: clamp(300px, 50vh, 500px); justify-self: center; }
  .flip.is-single .flip-single { display: block; }
  .flip.is-single .flip-hint { display: none; }
  .flip:focus-visible { outline: 2px solid var(--ink); outline-offset: 4px; }
  /* caption column (right): title, description, specs, example nav */
  .g-caption { display: flex; flex-direction: column; }
  .g-caption h3 {
    font-size: clamp(22px, 2.4vw, 30px); font-weight: 800; letter-spacing: -.03em;
    line-height: 1.08; margin: 0;
  }
  #g-desc { font-family: var(--font-desc); font-size: 15px; line-height: 1.55; color: var(--ink-2); margin: 14px 0 0; max-width: 46ch; }
  .g-specs { margin: 22px 0 0; border-top: 1px solid var(--hair); }
  .g-specs .row { display: grid; grid-template-columns: 132px 1fr; gap: 16px; padding: 11px 0; border-bottom: 1px solid var(--hair); }
  .g-specs .k { font-size: 10px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--ink-3); align-self: center; }
  .g-specs .v { font-size: 14px; font-weight: 500; color: var(--ink); }
  /* example nav: arrows flank a counter */
  .g-nav { display: flex; align-items: center; gap: 18px; margin-top: auto; padding-top: 30px; }
  .g-arrow {
    width: 46px; height: 46px; border-radius: 50%; cursor: pointer; padding: 0;
    background: transparent; border: 1px solid var(--ink-3); color: var(--ink);
    font-size: 17px; line-height: 1; display: flex; align-items: center; justify-content: center;
    transition: background .2s ease, color .2s ease, border-color .2s ease, transform .15s ease;
  }
  .g-arrow:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  .g-arrow:active { transform: scale(.93); }
  .g-count { font-size: 13px; font-weight: 700; letter-spacing: .16em; color: var(--ink-3); min-width: 54px; text-align: center; }
  .g-count #g-num { color: var(--ink); }
  .g-count-sep { margin: 0 4px; opacity: .55; }
  @media (max-width: 820px) {
    .work { min-height: auto; display: block; padding: 96px 0 40px; }
    .gallery { margin-top: 14px; }
    .g-main { grid-template-columns: 1fr; gap: 24px; align-items: stretch; }
    .g-nav { margin-top: 22px; }
  }

  /* ---- process timeline ---- */
  .process {
    padding: 56px 0 60px; background: var(--paper-2);
    border-top: 1px solid var(--hair); border-bottom: 1px solid var(--hair); margin-top: 56px;
  }
  .process .kicker { display: block; margin-bottom: 14px; }
  .process h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; margin: 0 0 46px; max-width: 18ch; line-height: 1.02;
  }
  .timeline { position: relative; display: grid; grid-template-columns: repeat(4, 1fr); }
  /* one full-width rail from the first node centre to the last */
  .timeline::before {
    content: ""; position: absolute; top: 13px; left: 12.5%; right: 12.5%; height: 2px;
    background: var(--hair); z-index: 0;
  }
  .tl-step {
    position: relative; padding: 46px 14px 0; text-align: center;
    opacity: 0; transform: translateY(22px); transition: opacity .6s ease, transform .6s ease;
  }
  .tl-step.in { opacity: 1; transform: none; }
  .tl-node {
    position: absolute; top: 0; left: 50%; transform: translateX(-50%); z-index: 1;
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--ink); color: var(--paper); font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
  }
  .tl-step h4 { font-size: 16px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 7px; }
  .tl-step p { font-family: var(--font-desc); font-weight: 400; color: var(--ink-2); font-size: 13px; margin: 0 auto; line-height: 1.5; max-width: 26ch; }
  @media (max-width: 760px) {
    .timeline { grid-template-columns: 1fr; }
    .timeline::before { display: none; }
    .tl-step { padding: 0 0 30px 46px; text-align: left; }
    .tl-step:last-child { padding-bottom: 0; }
    .tl-node { left: 0; transform: none; }
    .tl-step::after { content: ""; position: absolute; top: 28px; left: 13px; width: 2px; height: calc(100% - 28px); background: var(--hair); }
    .tl-step:last-child::after { display: none; }
  }


  /* ---- CTA ---- */
  .cta { background: var(--void); color: var(--paper); }
  .cta .wrap { padding: 58px 40px; text-align: center; }
  .cta img { height: 104px; margin: 0 auto 26px; opacity: .95; }
  .cta h2 {
    font-size: clamp(34px, 5vw, 66px); font-weight: 800;
    letter-spacing: -.04em; line-height: .98; margin: 0 0 22px;
  }
  .cta p { font-weight: 400; color: #c2bcb0; max-width: 56ch; margin: 0 auto 30px; font-size: 17px; }
  .cta .actions { justify-content: center; }
  .cta-fine { font-size: 13px; color: #948e84; margin: 26px auto 0; max-width: 64ch; line-height: 1.5; }
  .cta-form { max-width: 540px; margin: 4px auto 0; text-align: left; display: grid; gap: 16px; }
  .cta-form .row { display: grid; gap: 16px; grid-template-columns: 1fr 1fr; }
  .cta-field { display: flex; flex-direction: column; gap: 7px; }
  .cta-field label { font-size: 11px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: #948e84; }
  .cta-form input, .cta-form textarea {
    background: rgba(255,255,255,.04); border: 1px solid #3a3a3c; color: var(--paper);
    padding: 13px 14px; font: inherit; font-size: 15px; border-radius: 2px; width: 100%;
  }
  .cta-form input::placeholder, .cta-form textarea::placeholder { color: #6f6a62; }
  .cta-form input:focus, .cta-form textarea:focus { outline: none; border-color: var(--paper); background: rgba(255,255,255,.07); }
  .cta-form textarea { resize: vertical; min-height: 96px; }
  .cta-form button.btn {
    width: 100%; justify-content: center; text-align: center; margin-top: 4px;
    background: var(--paper); color: var(--ink); border-color: var(--paper); cursor: pointer;
  }
  .cta-form button.btn:hover { background: #fff; }
  .cta-note { font-size: 13px; color: #6f6a62; margin: 14px auto 0; }
  @media (max-width: 560px) { .cta-form .row { grid-template-columns: 1fr; } }

  /* ---- footer ---- */
  .foot {
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    padding: 30px 0; font-size: 12px; letter-spacing: .04em; color: var(--ink-3);
  }
  .foot a:hover { color: var(--ink-2); }

  /* ---- capabilities ---- */
  .caps { min-height: 100vh; min-height: 100svh; display: flex; flex-direction: column; justify-content: center; padding: 48px 0 40px; }
  @media (min-width: 821px) and (max-height: 820px) { .caps { justify-content: flex-start; } }
  .caps .kicker { display: block; margin-bottom: 10px; }
  .caps h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; margin: 0; max-width: 22ch; line-height: 1.02;
  }
  /* metrics (claims, to validate) */
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); margin-top: 22px; border-top: 1px solid var(--hair); border-bottom: 1px solid var(--hair); }
  .stat { padding: 16px 28px 16px 0; }
  .stat + .stat { border-left: 1px solid var(--hair); padding-left: 28px; }
  .stat-num { font-size: clamp(26px, 3vw, 40px); font-weight: 700; letter-spacing: -.03em; line-height: 1; white-space: nowrap; }
  .stat-num .stat-to { color: var(--ink-3); font-weight: 500; margin: 0 2px; }
  .stat-lbl { margin-top: 7px; font-size: 13px; color: var(--ink-2); line-height: 1.35; }
  @media (max-width: 680px) { .stats { grid-template-columns: 1fr; } .stat { padding: 14px 0; } .stat + .stat { border-left: 0; border-top: 1px solid var(--hair); padding-left: 0; } }
  /* spec rows */
  .spec { margin-top: 18px; border-top: 1px solid var(--hair); }
  .spec-row {
    display: grid; grid-template-columns: 200px 1fr; gap: 12px 40px;
    padding: 13px 0; border-bottom: 1px solid var(--hair); align-items: start;
  }
  .spec-label { font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--ink-3); padding-top: 5px; }
  .spec-val { font-size: clamp(16px, 1.6vw, 20px); font-weight: 500; letter-spacing: -.01em; color: var(--ink); line-height: 1.5; }
  .spec-val .dot { color: var(--ink-3); margin: 0 8px; }
  @media (max-width: 680px) { .spec-row { grid-template-columns: 1fr; gap: 6px; padding: 20px 0; } .spec-label { padding-top: 0; } }

  /* ---- use cases (within capabilities) ---- */
  .uc-block { margin-top: 18px; }
  .uc-label { display: block; font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 4px; }
  .uc-grid { display: grid; grid-template-columns: 1fr 1fr; column-gap: 56px; border-top: 1px solid var(--hair); }
  .uc {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 11px 0; border-bottom: 1px solid var(--hair);
    font-weight: 400; font-size: clamp(14px, 1.4vw, 17px); letter-spacing: -.01em;
  }
  .uc::before {
    content: ""; flex: 0 0 auto; width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent); margin-top: 9px; opacity: .6;
  }
  @media (max-width: 680px) { .uc-grid { grid-template-columns: 1fr; } }
  @media (max-width: 820px) { .caps { min-height: auto; display: block; padding: 56px 0; } }


  .hidden { display: none !important; }

  @media (max-width: 860px) {
    .hero-copy { padding-top: 92px; }
    .slide { width: clamp(220px, 78vw, 420px); }
  }

  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    * { transition: none !important; }
    .tl-step { opacity: 1; transform: none; }
  }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>

<div class="topbar">
  <div class="wrap">
    <a class="brand" href="#top" aria-label="Moonlake"><img src="{{LOGO_DARK}}" alt="Moonlake"></a>
    <nav>
      <a href="#examples">Lookbook</a>
      <a href="#how">How it works</a>
      <a href="#capabilities">Capabilities</a>
    </nav>
  </div>
</div>

<header class="hero" id="top">
  <div class="hero-figure" id="hero-figure">
    <img class="hero-fallback" src="{{HERO}}" alt="Simulation-ready 3D geometry generated by Moonlake">
    <canvas class="hero-canvas" id="hero-canvas" aria-hidden="true"></canvas>
    <noscript><style>.hero-fallback{opacity:1}</style></noscript>
  </div>
  <div class="hero-copy">
    <div class="inner">
      <div class="copy-block">
        <p class="kicker">Moonlake - Accelerating robotics deployment</p>
        <h1>Accelerated Pipelines</h1>
        <p class="hero-tagline">Simulation <span class="sep">|</span> Digital Twins <span class="sep">|</span> Robotics</p>
        <p class="lead">Moonlake turns real sites and assets into simulation-ready digital twins and scenes. Demo robots in real spaces, validate deployments before install, and cut prep time.</p>
        <div class="actions">
          <a class="btn solid" href="mailto:studios@moonlake.ai?subject=Demo%20request">Book a Demo</a>
          <a class="btn outline" href="#how">How it works</a>
        </div>
      </div>
    </div>
  </div>
</header>

<!-- credibility logo strip -->
<section class="logos">
  <div class="wrap">
    <p class="logos-label">Researchers &amp; engineers from</p>
  </div>
  <div class="marquee"><div class="marquee-track"><!--__LOGOS__--></div></div>
</section>

<!-- 2. Lookbook -->
<section class="work" id="examples">
  <div class="wrap">
    <div class="work-head">
      <div>
        <span class="kicker">Lookbook</span>
        <h2>See the transformation.</h2>
      </div>
    </div>
    <p class="sec-sub">Flip each card to see a customer's real source become a simulation-ready twin.</p>

    <div class="gallery" id="gallery">
      <div class="g-main">
        <div class="flip" id="flip" role="button" tabindex="0" aria-label="Flip between input and output">
          <div class="flip-inner" id="flip-inner">
            <div class="flip-face flip-front">
              <span class="flip-tag">Input</span>
              <img id="g-in-img" alt="" draggable="false">
            </div>
            <div class="flip-face flip-back">
              <span class="flip-tag flip-tag--out">Output</span>
              <img id="g-out-img" alt="" draggable="false">
              <video id="g-out-vid" muted loop playsinline preload="metadata"></video>
            </div>
          </div>
          <span class="flip-hint" aria-hidden="true">&#10227;</span>
          <video id="g-sbs" class="flip-single" muted loop playsinline aria-hidden="true"></video>
        </div>

        <div class="g-caption">
          <h3 id="g-title"></h3>
          <p id="g-desc"></p>
          <dl class="g-specs" id="g-specs"></dl>
          <div class="g-nav">
            <button class="g-arrow" id="g-prev" aria-label="Previous example">&#8592;</button>
            <span class="g-count"><span id="g-num">01</span> <span class="g-count-sep">/</span> <span id="g-total">03</span></span>
            <button class="g-arrow" id="g-next" aria-label="Next example">&#8594;</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 3. How it works (service timeline) -->
<section class="process" id="how">
  <div class="wrap">
    <span class="kicker">How it works</span>
    <h2>From your source to delivered assets.</h2>
    <div class="timeline" id="steps"></div>
  </div>
</section>

<!-- 4. Capabilities & use cases -->
<section class="caps" id="capabilities">
  <div class="wrap">
    <span class="kicker">Capabilities</span>
    <h2>Built for deployment.</h2>
    <div class="stats">
      <div class="stat"><div class="stat-num">20%</div><div class="stat-lbl">less deployment time</div></div>
      <div class="stat"><div class="stat-num">100h <span class="stat-to">&rarr;</span> 20h</div><div class="stat-lbl">for detailed asset creation</div></div>
      <div class="stat"><div class="stat-num">60%</div><div class="stat-lbl">automated with internal tooling</div></div>
    </div>
    <div class="spec">
      <div class="spec-row">
        <div class="spec-label">Inputs</div>
        <div class="spec-val">Images<span class="dot">&middot;</span>Video<span class="dot">&middot;</span>Point clouds<span class="dot">&middot;</span>Sensor data</div>
      </div>
      <div class="spec-row">
        <div class="spec-label">Outputs</div>
        <div class="spec-val">Sim-ready assets &amp; scenes<span class="dot">&middot;</span>Articulated, physics-validated twins<span class="dot">&middot;</span>.blend &amp; USD files</div>
      </div>
      <div class="spec-row">
        <div class="spec-label">Engines</div>
        <div class="spec-val">NVIDIA Isaac<span class="dot">&middot;</span>Newton<span class="dot">&middot;</span>MuJoCo<span class="dot">&middot;</span>Unreal</div>
      </div>
    </div>
    <div class="uc-block">
      <span class="uc-label">For robotics OEMs</span>
      <div class="uc-grid" id="uc-grid"></div>
    </div>
  </div>
</section>

<footer><div class="wrap foot">
  <span>© 2026 Moonlake AI Inc.</span>
  <span><a href="https://moonlakeai.com">moonlakeai.com</a></span>
</div></footer>

<script>
/* ============================================================
   IMAGES: base64 data URIs, injected at build time
   ============================================================ */
const IMAGES = {
/*__IMAGES__*/
};

/* ============================================================
   CONFIG: data-driven content.
   `assets` drives the lookbook; each entry pairs a customer source
   (inImg) with the generated output, plus its deliverables.
   ============================================================ */
const assets = [
  {
    img: "twin_simrobot",
    video: "assets/s6_output.mp4",
    inImg: "in_s6",
    name: "Articulated appliance twin",
    desc: "A customer appliance reconstructed from a single product photo into an animated, physics-validated sim twin in NVIDIA Newton.",
    source: "Single product photo",
    engine: "NVIDIA Newton",
    output: "Animated, physics-validated twin",
    deliverables: ".blend · USD · sim-ready",
    status: "Sim output",
  },
  {
    img: "twin_conveyor",
    video: "assets/s6_left.mp4",
    inImg: "in_s6b",
    name: "Palletizing work cell",
    desc: "A live palletizing line reconstructed from a single camera feed into a physics-validated sim twin for pick-and-place validation.",
    source: "Camera feed",
    engine: "Isaac Sim / Newton",
    output: "Animated, physics-validated twin",
    deliverables: ".blend · USD · sim-ready",
    status: "Sim output",
  },
  {
    single: "assets/s7_sidebyside.mp4",
    name: "Reconstructed work cell",
    desc: "A robotic work cell rebuilt from a single capture. Layered point clouds reconstruct every object as an articulated, slider-controlled twin, exported to Isaac Sim. Input left, output right.",
    source: "Image / video capture",
    engine: "Isaac Sim / Blender",
    output: "Articulated scene twin",
    deliverables: ".blend · USD · articulated",
    status: "Input → output",
  },
];

const pipeline = [
  { h: "You send a source", p: "An image, video, point cloud, or sensor data of the real asset or space." },
  { h: "We build it in 3D", p: "Reconstructed into 3D with inferred articulation and physics." },
  { h: "We calibrate & QA", p: "Our engineers hand-check and physically validate every asset in Isaac, Newton, or MuJoCo." },
  { h: "You receive deliverables", p: "Sim-ready assets, scenes, and blend files for demos, validation, and deployment prep." },
];

const useCases = [
  "Demoing robots in a customer's real space",
  "Pre-deployment visualization & validation",
  "Internal and customer-facing digital twins",
  "Faster deployment prep and asset creation",
  "Validating manipulation policies before install",
  "Access to manufacturers & factories worldwide",
];

/* ============================================================
   RENDER
   ============================================================ */
const $ = (s) => document.querySelector(s);

/* ---- lookbook: input -> output flip cards ---- */
const flip = $("#flip");
const flipInner = $("#flip-inner");
const inImg = $("#g-in-img");
const outImg = $("#g-out-img");
const outVid = $("#g-out-vid");
const sbs = $("#g-sbs");
let active = 0;
let flipped = false;

function syncVideo() {
  const a = assets[active];
  if (a.single) { sbs.play().catch(() => {}); outVid.pause(); return; }
  sbs.pause();
  if (flipped && a.video) { outVid.play().catch(() => {}); }
  else { outVid.pause(); }
}

function setFlip(state) {
  flipped = state;
  flip.classList.toggle("flipped", flipped);
  flip.setAttribute("aria-pressed", String(flipped));
  syncVideo();
}

function renderGallery(i) {
  active = (i + assets.length) % assets.length;
  const a = assets[active];
  // single side-by-side video example (no flip)
  flip.classList.toggle("is-single", !!a.single);
  if (a.single) {
    if (sbs.getAttribute("src") !== a.single) sbs.src = a.single;
  } else {
    inImg.src = IMAGES[a.inImg];
    inImg.alt = a.name + " — input";
    if (a.video) {
      if (outVid.getAttribute("src") !== a.video) outVid.src = a.video;
      outVid.style.display = "block";
      outImg.style.display = "none";
    } else {
      outImg.src = IMAGES[a.img];
      outImg.alt = a.name + " — output";
      outImg.style.display = "block";
      outVid.style.display = "none";
    }
  }
  $("#g-title").textContent = a.name;
  $("#g-desc").textContent = a.desc;
  $("#g-num").textContent = String(active + 1).padStart(2, "0");
  $("#g-total").textContent = String(assets.length).padStart(2, "0");
  $("#g-specs").innerHTML = [
    ["Source", a.source],
    ["Output", a.output],
    ["Physics engine", a.engine],
    ["Deliverables", a.deliverables],
  ].map(([k, v]) => `<div class="row"><div class="k">${k}</div><div class="v">${v}</div></div>`).join("");
  syncVideo();
}

function goTo(i) {
  // every example starts on its input face -- snap back instantly (no flip spin),
  // which also means the instant input image shows right away (no blank while a video loads)
  if (flipped) {
    flipInner.style.transition = "none";
    setFlip(false);
    void flipInner.offsetWidth;   // force reflow so the reset isn't animated
    flipInner.style.transition = "";
  }
  renderGallery(i);
}

$("#g-prev").addEventListener("click", () => goTo(active - 1));
$("#g-next").addEventListener("click", () => goTo(active + 1));

flip.addEventListener("click", () => { if (!assets[active].single) setFlip(!flipped); });
flip.addEventListener("keydown", (e) => {
  if (assets[active].single) return;
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setFlip(!flipped); }
});

renderGallery(0);

$("#steps").innerHTML = pipeline
  .map((s, i) => `<div class="tl-step"><span class="tl-node">${String(i + 1).padStart(2, "0")}</span><h4>${s.h}</h4><p>${s.p}</p></div>`).join("");

$("#uc-grid").innerHTML = useCases.map((u) => `<div class="uc">${u}</div>`).join("");

/* ---- contact form -> opens email client with prefilled details ---- */
const contactForm = $("#contact-form");
if (contactForm) {
  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(contactForm);
    const name = (data.get("name") || "").trim();
    const company = (data.get("company") || "").trim();
    const email = (data.get("email") || "").trim();
    const message = (data.get("message") || "").trim();
    const lines = [
      `Name: ${name}`,
      `Company: ${company || "-"}`,
      `Email: ${email}`,
      "",
      message || "(no message provided)",
    ];
    const subject = `Moonlake pilot: ${name || "new inquiry"}`;
    const href = `mailto:studios@moonlake.ai?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
    window.location.href = href;
    const note = $("#cf-note");
    if (note) note.textContent = "Opening your email client… if nothing happens, write us at studios@moonlake.ai.";
  });
}

/* ---- sequential scroll-in for process steps ---- */
const io = new IntersectionObserver((entries) => {
  entries.forEach((en) => {
    if (en.isIntersecting) {
      const el = en.target;
      el.style.transitionDelay = (el.dataset.i * 0.12) + "s";
      el.classList.add("in");
      io.unobserve(el);
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll(".tl-step").forEach((el, i) => { el.dataset.i = i; io.observe(el); });

/* ---- arrow keys switch lookbook examples ---- */
document.addEventListener("keydown", (e) => {
  const tag = (document.activeElement && document.activeElement.tagName) || "";
  if (tag === "INPUT" || tag === "TEXTAREA") return;
  if (e.key === "ArrowLeft") goTo(active - 1);
  if (e.key === "ArrowRight") goTo(active + 1);
});
</script>

<script type="module">
/* ============================================================
   Hero geometry: one set of wireframe solids drifting through a
   viscous fluid. Each shape travels in depth (z) on its own cycle,
   so it moves nearer (clearer) and farther (fuzzier). A fat faint
   "halo" line plus a global blur feather the edges, like light
   leaking through the wireframes. Left-side shapes sit farther back
   and fainter so the headline stays readable. Falls back to the PNG
   on reduced-motion or any load failure.
   ============================================================ */
(async () => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const canvas = document.getElementById("hero-canvas");
  const figure = document.getElementById("hero-figure");
  const showFallback = () => figure && figure.classList.add("show-fallback");
  if (!canvas) return;
  if (reduce) { showFallback(); return; }

  let THREE, LineSegments2, LineSegmentsGeometry, LineMaterial;
  try {
    THREE = await import("three");
    ({ LineSegments2 } = await import("three/addons/lines/LineSegments2.js"));
    ({ LineSegmentsGeometry } = await import("three/addons/lines/LineSegmentsGeometry.js"));
    ({ LineMaterial } = await import("three/addons/lines/LineMaterial.js"));
  } catch (e) { showFallback(); return; }   // CDN blocked -> reveal static PNG

  const INK = 0x33333b;              // softened so the shapes never dominate the copy
  const NEAR = 2.2, FAR = -6;        // depth range mapped to clarity

  const solids = {
    ico1: new THREE.IcosahedronGeometry(1, 1),
    ico0: new THREE.IcosahedronGeometry(1, 0),
    dodeca: new THREE.DodecahedronGeometry(1),
    octa: new THREE.OctahedronGeometry(1),
    cube: new THREE.BoxGeometry(1.3, 1.3, 1.3),
  };
  const edges = {};
  for (const k in solids) edges[k] = new LineSegmentsGeometry().fromEdgesGeometry(new THREE.EdgesGeometry(solids[k], 1));

  const lmats = [];
  function line(k, lw, op) {
    const m = new LineMaterial({ color: INK, linewidth: lw, transparent: true, opacity: op, depthTest: false });
    lmats.push(m);
    return new LineSegments2(edges[k], m);
  }

  // one set of shapes spread across the width. dim = static dimming (left = fainter),
  // zc = depth centre, za = travel through depth.
  // fz is shared and pz is spread evenly (i * 2pi/5) so the shapes take TURNS
  // coming forward -- only one is ever near its peak at a time. zc is capped so
  // even at peak nothing gets huge; left shapes peak only to mid-depth.
  const FZ = 0.11;
  const defs = [
    { g: "dodeca", x: -3.3, y: 0.8,  s: 1.5,  dim: 0.5,  zc: -3.9, za: 2.2, rx: 0.05, ry: 0.04, fz: FZ, pz: 0.00, dx: 0.5,  dy: 0.4,  fdx: 0.08, fdy: 0.06, pdx: 0.5, pdy: 2.0, sh: 0.6 },
    { g: "ico1",   x: -1.5, y: -0.3, s: 1.7,  dim: 0.6,  zc: -3.2, za: 2.3, rx: 0.04, ry: 0.06, fz: FZ, pz: 1.26, dx: 0.45, dy: 0.45, fdx: 0.07, fdy: 0.09, pdx: 2.1, pdy: 0.7, sh: 1.4 },
    { g: "octa",   x: 0.6,  y: 1.4,  s: 1.0,  dim: 0.9,  zc: -2.0, za: 2.3, rx: 0.08, ry: 0.06, fz: FZ, pz: 2.51, dx: 0.5,  dy: 0.4,  fdx: 0.10, fdy: 0.07, pdx: 1.4, pdy: 3.0, sh: 2.2 },
    { g: "cube",   x: 2.1,  y: 0.1,  s: 1.0,  dim: 1.0,  zc: -1.5, za: 2.4, rx: 0.06, ry: 0.085, fz: FZ, pz: 3.77, dx: 0.45, dy: 0.42, fdx: 0.09, fdy: 0.08, pdx: 0.9, pdy: 1.2, sh: 0.9 },
    { g: "ico0",   x: 3.2,  y: 1.2,  s: 0.85, dim: 1.0,  zc: -1.3, za: 2.4, rx: 0.10, ry: 0.08, fz: FZ, pz: 5.03, dx: 0.40, dy: 0.40, fdx: 0.12, fdy: 0.10, pdx: 2.6, pdy: 0.3, sh: 1.8 },
  ];

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  const root = new THREE.Group();
  scene.add(root);
  const cam = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  cam.position.set(0, 0, 6);

  const shapes = defs.map((d) => {
    const group = new THREE.Group();
    const halo = line(d.g, 9, 0.12);   // fat faint line -> fuzzy glow
    const core = line(d.g, 1.7, 0.4);
    group.add(halo, core);
    group.scale.setScalar(d.s);
    group.userData = d;
    group._core = core.material; group._halo = halo.material;
    root.add(group);
    return group;
  });

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    cam.aspect = w / h; cam.updateProjectionMatrix();
    lmats.forEach((m) => m.resolution.set(w, h));
  }
  resize();
  window.addEventListener("resize", resize, { passive: true });

  let tx = 0, ty = 0, cx = 0, cy = 0;
  window.addEventListener("pointermove", (e) => {
    tx = (e.clientX / window.innerWidth - 0.5);
    ty = (e.clientY / window.innerHeight - 0.5);
  }, { passive: true });

  let visible = true;
  new IntersectionObserver((ents) => { visible = ents[0].isIntersecting; }, { threshold: 0 }).observe(canvas);

  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
  const clock = new THREE.Clock();
  const T0 = 8;                        // start mid-cycle so shapes begin spread out, not clustered
  function frame() {
    requestAnimationFrame(frame);
    if (!visible) return;
    const t = clock.getElapsedTime() + T0;
    cx += (tx - cx) * 0.02; cy += (ty - cy) * 0.02;     // viscous pointer lag
    for (const g of shapes) {
      const d = g.userData;
      const z = d.zc + d.za * Math.sin(t * d.fz + d.pz);
      const par = 2.2 + z * 0.25;                        // nearer shapes parallax more
      g.position.set(
        d.x + d.dx * Math.sin(t * d.fdx + d.pdx) + cx * par,
        d.y + d.dy * Math.cos(t * d.fdy + d.pdy) - cy * par,
        z
      );
      g.rotation.x = t * d.rx + 0.2 * Math.sin(t * d.fz + d.pz);
      g.rotation.y = t * d.ry + 0.2 * Math.cos(t * d.fz * 1.3 + d.pdx);
      const f = clamp01((z - FAR) / (NEAR - FAR));       // 0 far .. 1 near
      const shimmer = 0.78 + 0.22 * Math.sin(t * 0.6 + d.sh);
      g._core.opacity = (0.05 + 0.29 * f) * d.dim;       // near -> sharper core
      g._halo.opacity = (0.04 + 0.18 * (1 - f)) * d.dim * shimmer; // far -> fuzzy halo
    }
    renderer.render(scene, cam);
  }
  frame();

  requestAnimationFrame(() => { canvas.classList.add("is-live"); });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
