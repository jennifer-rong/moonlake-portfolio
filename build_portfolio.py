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
}
VIDEO_FILES = ["s6_output.mp4"]                       # referenced (not base64) outputs
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
    # in_s6 is already padded to the video's aspect at native res; keep it sharp
    (BUILD / "in_s6.png").write_bytes((ASSETS / "in_s6.png").read_bytes())


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
    background: linear-gradient(to bottom, rgba(255,255,255,.55), rgba(249,248,243,.30));
    backdrop-filter: saturate(200%) blur(30px);
    -webkit-backdrop-filter: saturate(200%) blur(30px);
    border: 1px solid rgba(255,255,255,.6);
    box-shadow:
      inset 0 1px 1px rgba(255,255,255,.95),
      inset 0 -2px 4px rgba(255,255,255,.35),
      0 12px 34px rgba(13,13,14,.12),
      0 2px 8px rgba(13,13,14,.06);
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
  /* live three.js geometry; layered canvases give depth-of-field (farther = blurrier) */
  .hero-fallback { transition: opacity .9s ease; }
  .hero-figure.is-live .hero-fallback { opacity: 0; }
  .hero-scene { position: absolute; inset: 0; opacity: 0; transition: opacity 1.4s ease; }
  .hero-scene.is-live { opacity: 1; }
  .hero-layer { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
  .hero-layer--back { filter: blur(13px); opacity: .42; }
  .hero-layer--mid  { filter: blur(4.5px); opacity: .78; }
  .hero-layer--front { filter: blur(0); opacity: 1; }
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
    font-size: clamp(36px, 5.2vw, 74px); line-height: .99;
    letter-spacing: -.035em; font-weight: 800; margin: 0 0 20px; max-width: 17ch;
  }
  .hero .lead {
    font-size: clamp(16px, 1.35vw, 19px); font-weight: 400;
    color: var(--ink-2); max-width: 54ch; margin: 0 0 28px; line-height: 1.55;
  }

  /* ---- buttons (shared) ---- */
  .actions { display: flex; gap: 14px; flex-wrap: wrap; }
  .btn {
    font-size: 12px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase;
    padding: 16px 30px; background: var(--paper); color: var(--ink); cursor: pointer;
    border: 1px solid transparent;
    transition: transform .2s ease, background .2s ease, border-color .2s ease, color .2s ease;
  }
  .btn:hover { transform: translateY(-2px); }
  .btn.solid { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  .btn.solid:hover { background: #000; }
  .btn.outline {
    background: linear-gradient(to bottom, rgba(255,255,255,.45), rgba(255,255,255,.14));
    color: var(--ink); border-color: var(--ink-3);
    backdrop-filter: blur(12px) saturate(170%);
    -webkit-backdrop-filter: blur(12px) saturate(170%);
    box-shadow: 0 1px 0 rgba(255,255,255,.7) inset, 0 6px 18px rgba(13,13,14,.06);
  }
  .btn.outline:hover {
    border-color: var(--ink);
    background: linear-gradient(to bottom, rgba(255,255,255,.6), rgba(255,255,255,.24));
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
  .work { min-height: calc(100vh - 90px); min-height: calc(100svh - 90px); display: flex; flex-direction: column; padding: 28px 0 26px; }
  .work > .wrap { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
  .work-head {
    display: flex; justify-content: space-between; align-items: flex-end;
    gap: 28px; flex-wrap: wrap; margin-bottom: 8px;
  }
  .work-head h2 {
    font-size: clamp(30px, 3.6vw, 46px); font-weight: 800;
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
  .gallery { margin-top: 16px; flex: 1 1 0; min-height: 0; display: flex; flex-direction: column; justify-content: center; }
  .flip {
    position: relative; width: min(100%, 96vh); max-height: 60vh; margin: 0 auto;
    aspect-ratio: 1920 / 1040; perspective: 1700px; cursor: pointer;
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
  .flip-hint {
    position: absolute; bottom: 14px; right: 14px; z-index: 4; pointer-events: none;
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
    color: var(--paper); background: rgba(13,13,14,.8); padding: 8px 13px; border-radius: 100px;
    transition: background .2s ease;
  }
  .flip-hint-ic { font-size: 13px; line-height: 1; }
  .flip:hover .flip-hint { background: var(--ink); }
  .flip:focus-visible { outline: 2px solid var(--ink); outline-offset: 4px; }
  /* example tabs replace the old prev/next arrows */
  .g-tabs { display: grid; grid-template-columns: repeat(3, 1fr); width: 100%; max-width: 820px; margin: 22px auto 0; border-top: 1px solid var(--hair); }
  .g-tab {
    display: flex; align-items: baseline; gap: 11px; text-align: left;
    background: none; border: 0; border-top: 2px solid transparent; margin-top: -1px;
    padding: 13px 16px 13px 0; cursor: pointer; color: var(--ink-3);
    transition: color .2s ease, border-color .2s ease; font: inherit;
  }
  .g-tab:hover { color: var(--ink-2); }
  .g-tab.is-active { color: var(--ink); border-top-color: var(--ink); }
  .g-tab-n { font-size: 13px; font-weight: 800; letter-spacing: .08em; }
  .g-tab-name { font-size: 13px; font-weight: 500; line-height: 1.2; }
  /* active example copy */
  .g-info { width: 100%; max-width: 820px; margin: 16px auto 0; }
  #g-desc { font-family: var(--font-desc); font-size: 15px; line-height: 1.55; color: var(--ink-2); margin: 0; max-width: 66ch; }
  .g-specline { font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-3); margin: 11px 0 0; }
  @media (max-width: 820px) {
    .work { min-height: auto; display: block; padding: 96px 0 40px; }
    .work > .wrap { display: block; }
    .gallery { flex: none; display: block; }
    .flip { width: 100%; max-height: none; }
    .g-tabs, .g-info { max-width: none; }
    .g-tab-name { display: none; }
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
    font-size: clamp(26px, 3vw, 38px); font-weight: 800;
    letter-spacing: -.035em; margin: 0; max-width: 22ch; line-height: 1.04;
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
    <div class="hero-scene" id="hero-scene" aria-hidden="true">
      <canvas class="hero-layer hero-layer--back"></canvas>
      <canvas class="hero-layer hero-layer--mid"></canvas>
      <canvas class="hero-layer hero-layer--front"></canvas>
    </div>
  </div>
  <div class="hero-copy">
    <div class="inner">
      <div class="copy-block">
        <p class="kicker">Moonlake - Accelerating robotics deployment</p>
        <h1>Accelerated pipelines for simulation, digital twins, and robotics.</h1>
        <p class="lead">Moonlake turns real sites and assets into simulation-ready digital twins, scenes, and blend files. OEMs use them to demo robots in customer spaces and validate deployments before install.</p>
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
        <h2>Input, transformed.</h2>
      </div>
    </div>
    <p class="sec-sub">Flip each card to see a customer's real source become a simulation-ready twin.</p>

    <div class="gallery" id="gallery">
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
        <span class="flip-hint" id="flip-hint"><span class="flip-hint-ic">&#8635;</span> <span id="flip-hint-tx">Flip to output</span></span>
      </div>

      <div class="g-tabs" id="g-tabs" role="tablist" aria-label="Examples"></div>

      <div class="g-info">
        <p id="g-desc"></p>
        <p class="g-specline" id="g-specline"></p>
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
    <h2>From inputs to validated twins.</h2>
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
  <span>© 2026 Moonlake. Simulation infrastructure for robotics deployment.</span>
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
    inImg: "in_dock",
    name: "Modular conveyor line",
    desc: "A conveyor system rebuilt as a configurable 3D asset with inferred structure, ready for line layouts and throughput simulation.",
    source: "Site photo",
    engine: "Isaac Sim / Newton",
    output: "Procedural, editable asset",
    deliverables: ".blend · USD · configurable",
    status: "Sim output",
  },
  {
    img: "twin_cell",
    inImg: "in_factory",
    name: "Pick-and-place work cell",
    desc: "A pick-and-place cell (robot, pallets, and racking) reconstructed and calibrated for validation against the real space before install.",
    source: "Factory photo / point cloud",
    engine: "NVIDIA Isaac Sim",
    output: "Validated work-cell twin",
    deliverables: ".blend · USD · validated",
    status: "Sim output",
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
const inImg = $("#g-in-img");
const outImg = $("#g-out-img");
const outVid = $("#g-out-vid");
const hintTx = $("#flip-hint-tx");
let active = 0;
let flipped = false;

function syncVideo() {
  const a = assets[active];
  if (flipped && a.video) { outVid.play().catch(() => {}); }
  else { outVid.pause(); }
}

function setFlip(state) {
  flipped = state;
  flip.classList.toggle("flipped", flipped);
  flip.setAttribute("aria-pressed", String(flipped));
  hintTx.textContent = flipped ? "Flip to input" : "Flip to output";
  syncVideo();
}

function renderGallery(i) {
  active = (i + assets.length) % assets.length;
  const a = assets[active];
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
  $("#g-desc").textContent = a.desc;
  $("#g-specline").textContent = [a.source, a.engine, a.deliverables].join("  ·  ");
  document.querySelectorAll(".g-tab").forEach((t, k) => t.classList.toggle("is-active", k === active));
  syncVideo();
}

function goTo(i) {
  setFlip(false);                 // each new example starts on its input face
  renderGallery(i);
}

$("#g-tabs").innerHTML = assets.map((a, i) =>
  `<button class="g-tab" role="tab" data-i="${i}"><span class="g-tab-n">${String(i + 1).padStart(2, "0")}</span><span class="g-tab-name">${a.name}</span></button>`).join("");
$("#g-tabs").addEventListener("click", (e) => {
  const b = e.target.closest(".g-tab");
  if (b) goTo(+b.dataset.i);
});

flip.addEventListener("click", () => setFlip(!flipped));
flip.addEventListener("keydown", (e) => {
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
   Hero geometry: live three.js wireframes drifting as if through
   a viscous fluid. Three stacked canvases (back/mid/front) get
   increasing CSS blur -> real depth-of-field (farther = blurrier).
   Falls back to the static PNG on reduced-motion or any failure.
   ============================================================ */
(async () => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene = document.getElementById("hero-scene");
  const figure = document.getElementById("hero-figure");
  if (reduce || !scene) return;

  let THREE, LineSegments2, LineSegmentsGeometry, LineMaterial;
  try {
    THREE = await import("three");
    ({ LineSegments2 } = await import("three/addons/lines/LineSegments2.js"));
    ({ LineSegmentsGeometry } = await import("three/addons/lines/LineSegmentsGeometry.js"));
    ({ LineMaterial } = await import("three/addons/lines/LineMaterial.js"));
  } catch (e) { return; }            // CDN blocked -> keep PNG

  const INK = 0x16161b;
  const canvases = scene.querySelectorAll("canvas");

  // geometry recipes (clean convex solids -> crisp facet edges, not busy)
  const geo = {
    ico1: new THREE.IcosahedronGeometry(1, 1),
    ico0: new THREE.IcosahedronGeometry(1, 0),
    dodeca: new THREE.DodecahedronGeometry(1),
    octa: new THREE.OctahedronGeometry(1),
    cube: new THREE.BoxGeometry(1.35, 1.35, 1.35),
  };

  function makeShape(g, o) {
    const group = new THREE.Group();
    const fill = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
      color: INK, transparent: true, opacity: 0.045, depthWrite: false,
    }));
    const lsg = new LineSegmentsGeometry().fromEdgesGeometry(new THREE.EdgesGeometry(g, 1));
    const lmat = new LineMaterial({
      color: INK, linewidth: o.lw, transparent: true, opacity: o.lo,
    });
    const seg = new LineSegments2(lsg, lmat);
    group.add(fill, seg);
    group.position.set(o.x, o.y, 0);
    group.scale.setScalar(o.s);
    group.userData = o.m;            // motion params
    group._lmat = lmat;
    return group;
  }

  // depth bands: each its own canvas + scene + camera; CSS blurs them
  const bands = [
    { canvas: canvases[0], par: 0.30, shapes: [
        { g: "ico1", x: 1.2, y: 0.55, s: 2.25, lw: 2.4, lo: 0.9,
          m: { rx: 0.045, ry: 0.06, ax: 0.18, ay: 0.22, fx: 0.13, fy: 0.11, px: 0.0, py: 1.3,
               dx: 0.34, dy: 0.26, dz: 0.5, fdx: 0.12, fdy: 0.09, fdz: 0.07, pdx: 0.5, pdy: 2.1 } },
      ] },
    { canvas: canvases[1], par: 0.7, shapes: [
        { g: "dodeca", x: 2.35, y: 1.2, s: 1.05, lw: 2.2, lo: 0.92,
          m: { rx: 0.07, ry: 0.05, ax: 0.25, ay: 0.2, fx: 0.17, fy: 0.14, px: 1.1, py: 0.3,
               dx: 0.3, dy: 0.28, dz: 0.4, fdx: 0.16, fdy: 0.12, fdz: 0.1, pdx: 2.0, pdy: 0.7 } },
        { g: "cube", x: -0.15, y: 1.15, s: 0.82, lw: 2.2, lo: 0.85,
          m: { rx: 0.06, ry: 0.085, ax: 0.2, ay: 0.26, fx: 0.12, fy: 0.16, px: 2.4, py: 1.0,
               dx: 0.32, dy: 0.24, dz: 0.45, fdx: 0.13, fdy: 0.15, fdz: 0.09, pdx: 0.9, pdy: 3.0 } },
      ] },
    { canvas: canvases[2], par: 1.2, shapes: [
        { g: "octa", x: 2.75, y: -0.05, s: 0.8, lw: 2.6, lo: 1.0,
          m: { rx: 0.09, ry: 0.07, ax: 0.28, ay: 0.24, fx: 0.19, fy: 0.15, px: 0.6, py: 2.2,
               dx: 0.28, dy: 0.3, dz: 0.5, fdx: 0.18, fdy: 0.14, fdz: 0.12, pdx: 1.4, pdy: 0.2 } },
        { g: "ico0", x: 0.75, y: 1.7, s: 0.6, lw: 2.6, lo: 1.0,
          m: { rx: 0.11, ry: 0.08, ax: 0.3, ay: 0.26, fx: 0.21, fy: 0.18, px: 3.0, py: 0.9,
               dx: 0.26, dy: 0.26, dz: 0.4, fdx: 0.2, fdy: 0.17, fdz: 0.13, pdx: 2.6, pdy: 1.7 } },
      ] },
  ];

  const layers = bands.map((b) => {
    const renderer = new THREE.WebGLRenderer({ canvas: b.canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    const sc = new THREE.Scene();
    const root = new THREE.Group();
    sc.add(root);
    const cam = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    cam.position.set(0, 0, 6);
    const objs = b.shapes.map((o) => {
      const grp = makeShape(geo[o.g], o);
      grp.userData.base = grp.position.clone();
      root.add(grp);
      return grp;
    });
    return { renderer, sc, cam, root, objs, par: b.par };
  });

  function resize() {
    const w = scene.clientWidth, h = scene.clientHeight;
    if (!w || !h) return;
    layers.forEach((L) => {
      L.renderer.setSize(w, h, false);
      L.cam.aspect = w / h; L.cam.updateProjectionMatrix();
      L.objs.forEach((g) => g._lmat.resolution.set(w, h));
    });
  }
  resize();
  window.addEventListener("resize", resize, { passive: true });

  // viscous pointer follow: target set on move, position eased very slowly
  let tx = 0, ty = 0, cx = 0, cy = 0;
  window.addEventListener("pointermove", (e) => {
    tx = (e.clientX / window.innerWidth - 0.5);
    ty = (e.clientY / window.innerHeight - 0.5);
  }, { passive: true });

  // only animate while the hero is on screen
  let visible = true;
  new IntersectionObserver((ents) => { visible = ents[0].isIntersecting; },
    { threshold: 0 }).observe(scene);

  const clock = new THREE.Clock();
  function frame() {
    requestAnimationFrame(frame);
    if (!visible) return;
    const t = clock.getElapsedTime();
    cx += (tx - cx) * 0.022;          // heavy damping -> fluid lag
    cy += (ty - cy) * 0.022;
    layers.forEach((L) => {
      L.objs.forEach((g) => {
        const m = g.userData, b = m.base;
        g.rotation.x = t * m.rx + m.ax * Math.sin(t * m.fx + m.px);
        g.rotation.y = t * m.ry + m.ay * Math.cos(t * m.fy + m.py);
        g.rotation.z = m.ax * 0.4 * Math.sin(t * m.fx * 0.7 + m.py);
        g.position.x = b.x + m.dx * Math.sin(t * m.fdx + m.pdx);
        g.position.y = b.y + m.dy * Math.cos(t * m.fdy + m.pdy);
        g.position.z = m.dz * Math.sin(t * m.fdz);
      });
      L.root.position.x = cx * L.par;
      L.root.position.y = -cy * L.par;
      L.renderer.render(L.sc, L.cam);
    });
  }
  frame();

  // reveal the live scene, fade out the PNG
  requestAnimationFrame(() => { scene.classList.add("is-live"); figure.classList.add("is-live"); });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
