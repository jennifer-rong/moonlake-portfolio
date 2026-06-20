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
}
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


def data_uri(path: pathlib.Path) -> str:
    return f"data:image/png;base64,{b64(path)}"


# Web font: FK Grotesk SemiMono, embedded as base64 woff2 (weight -> file)
FONT_WEIGHTS = [
    ("400", "FKGroteskSemiMono-Regular.woff2"),
    ("500", "FKGroteskSemiMono-Medium.woff2"),
    ("700", "FKGroteskSemiMono-Bold.woff2"),
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
    for weight, fname in FONT_WEIGHTS:
        b = base64.b64encode((ASSETS / "fonts" / fname).read_bytes()).decode("ascii")
        faces.append(
            "@font-face{font-family:'FK Grotesk SemiMono';font-style:normal;"
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

  /* ---- results gallery (editorial) ---- */
  .gallery { margin-top: 12px; flex: 1 1 0; min-height: 0; }
  .g-main { display: grid; grid-template-columns: 1.35fr 1fr; grid-template-rows: 1fr; gap: clamp(24px, 4vw, 64px); align-items: stretch; height: 100%; }
  .g-stage {
    position: relative; margin: 0; border: 1px solid var(--hair); border-radius: 4px;
    background: var(--paper-2); overflow: hidden; min-height: 0;
    cursor: zoom-in; touch-action: pan-y; user-select: none; -webkit-user-select: none;
  }
  .g-stage img { width: 100%; height: 100%; object-fit: cover; display: block; -webkit-user-drag: none; transition: opacity .3s ease; }
  .g-stage.fade img { opacity: 0; }
  .g-tag {
    position: absolute; top: 14px; left: 14px; z-index: 2;
    font-size: 10px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
    color: var(--ink-2); background: rgba(249,248,243,.9); padding: 5px 10px; border-radius: 2px;
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  }
  .g-zoom {
    position: absolute; bottom: 14px; right: 14px; z-index: 2;
    font-size: 10px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
    color: var(--ink-2); background: rgba(249,248,243,.9); padding: 5px 10px; border-radius: 2px;
    opacity: 0; transition: opacity .25s ease; pointer-events: none;
  }
  .g-stage:hover .g-zoom { opacity: 1; }
  /* input inset: shows the source the output was generated from */
  .g-inset {
    position: absolute; bottom: 14px; left: 14px; z-index: 2; margin: 0;
    width: 30%; max-width: 172px; border: 1px solid rgba(13,13,14,.18); border-radius: 3px;
    overflow: hidden; box-shadow: 0 6px 18px rgba(13,13,14,.28); background: var(--paper);
  }
  .g-inset img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; display: block; }
  .g-inset figcaption {
    position: absolute; top: 0; left: 0; font-size: 9px; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: var(--paper); background: rgba(13,13,14,.82); padding: 3px 7px;
  }
  .g-inset.hide { display: none; }
  /* caption column */
  .g-caption { display: flex; flex-direction: column; }
  .g-index { font-size: 12px; font-weight: 700; letter-spacing: .14em; color: var(--ink-3); }
  .g-index .g-sep { margin: 0 5px; opacity: .6; }
  .g-caption h3 {
    font-size: clamp(22px, 2.4vw, 30px); font-weight: 800; letter-spacing: -.03em;
    line-height: 1.08; margin: 14px 0 0;
  }
  #g-desc { font-size: 15px; line-height: 1.55; color: var(--ink-2); margin: 14px 0 0; max-width: 46ch; }
  .g-specs { margin: 22px 0 0; border-top: 1px solid var(--hair); }
  .g-specs .row { display: grid; grid-template-columns: 128px 1fr; gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--hair); }
  .g-specs .k { font-size: 10px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--ink-3); align-self: center; }
  .g-specs .v { font-size: 14px; font-weight: 500; color: var(--ink); }
  .g-controls { display: flex; gap: 10px; margin-top: auto; padding-top: 26px; }
  .g-arrow {
    width: 46px; height: 46px; border-radius: 50%; cursor: pointer;
    background: var(--paper); border: 1px solid var(--ink-3); color: var(--ink);
    font-size: 20px; line-height: 1; display: flex; align-items: center; justify-content: center;
    transition: background .2s ease, color .2s ease, border-color .2s ease;
  }
  .g-arrow:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  @media (max-width: 820px) {
    .work { min-height: auto; display: block; padding: 96px 0 40px; }
    .work > .wrap { display: block; }
    .gallery { flex: none; }
    .g-main { grid-template-columns: 1fr; grid-template-rows: auto; gap: 22px; height: auto; }
    .g-stage { aspect-ratio: 16 / 11; }
    .g-controls { margin-top: 22px; }
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
  .tl-step p { font-weight: 400; color: var(--ink-2); font-size: 13px; margin: 0 auto; line-height: 1.5; max-width: 26ch; }
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
    font-weight: 600; font-size: clamp(14px, 1.4vw, 17px); letter-spacing: -.01em;
  }
  .uc::before {
    content: ""; flex: 0 0 auto; width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent); margin-top: 9px; opacity: .6;
  }
  @media (max-width: 680px) { .uc-grid { grid-template-columns: 1fr; } }
  @media (max-width: 820px) { .caps { min-height: auto; display: block; padding: 56px 0; } }


  /* ---- lightbox ---- */
  .lb {
    position: fixed; inset: 0; z-index: 100; display: none;
    background: rgba(243,240,232,.97); align-items: center; justify-content: center; padding: 5vw;
    opacity: 0; transition: opacity .2s ease;
  }
  .lb.open { display: flex; opacity: 1; }
  .lb-inner { max-width: 92vw; text-align: center; }
  .lb img { max-width: 90vw; max-height: 74vh; object-fit: contain; }
  .lb .cap { color: var(--ink); margin-top: 24px; }
  .lb .cap h3 { margin: 0 0 6px; font-size: 20px; font-weight: 800; letter-spacing: -.02em; }
  .lb .cap p { margin: 0; color: var(--ink-3); font-size: 12px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
  .lb button {
    position: absolute; border: 1px solid var(--hair); background: rgba(13,13,14,.04);
    color: var(--ink); cursor: pointer; line-height: 1;
  }
  .lb .close { top: 26px; right: 28px; width: 44px; height: 44px; font-size: 22px; }
  .lb .nav { top: 50%; transform: translateY(-50%); width: 48px; height: 48px; font-size: 24px; }
  .lb .nav.prev { left: 26px; } .lb .nav.next { right: 26px; }

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
  <div class="hero-figure">
    <img src="{{HERO}}" alt="Simulation-ready 3D geometry generated by Moonlake">
  </div>
  <div class="hero-copy">
    <div class="inner">
      <div class="copy-block">
        <p class="kicker">Moonlake - Accelerating robotics deployment</p>
        <h1>Accelerated pipelines for simulation, digital twins, and robotics.</h1>
        <p class="lead">Moonlake turns real sites and assets into simulation-ready digital twins, scenes, and blend files. OEMs use them to demo robots in customer spaces and validate deployments before install.</p>
        <div class="actions">
          <a class="btn solid" href="#examples">Assets and Scenes</a>
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
        <h2>Assets &amp; scenes Moonlake delivers.</h2>
      </div>
    </div>
    <p class="sec-sub">Each example is a customer source (image, video, or point cloud) turned into a simulation-ready asset, scene, and blend file.</p>

    <div class="gallery" id="gallery">
      <div class="g-main">
        <figure class="g-stage" id="g-stage">
          <span class="g-tag" id="g-tag"></span>
          <figure class="g-inset" id="g-inset">
            <img id="g-in-img" alt="" draggable="false">
            <figcaption>Input</figcaption>
          </figure>
          <img id="g-img" alt="" draggable="false">
          <span class="g-zoom" aria-hidden="true">Click to enlarge</span>
        </figure>
        <div class="g-caption">
          <div class="g-index"><span id="g-num">01</span> <span class="g-sep">/</span> <span id="g-total">03</span></div>
          <h3 id="g-title"></h3>
          <p id="g-desc"></p>
          <dl class="g-specs" id="g-specs"></dl>
          <div class="g-controls">
            <button class="g-arrow" id="g-prev" aria-label="Previous result">&#8249;</button>
            <button class="g-arrow" id="g-next" aria-label="Next result">&#8250;</button>
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

<div class="lb" id="lightbox" aria-hidden="true">
  <button class="close" id="lb-close" aria-label="Close">&times;</button>
  <button class="nav prev" id="lb-prev" aria-label="Previous">&#8249;</button>
  <button class="nav next" id="lb-next" aria-label="Next">&#8250;</button>
  <div class="lb-inner">
    <img id="lb-img" alt="">
    <div class="cap"><h3 id="lb-title"></h3><p id="lb-sub"></p></div>
  </div>
</div>

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
    inImg: "in_appliance",
    name: "Articulated appliance twin",
    desc: "A customer appliance and robot arm reconstructed from a single product photo and calibrated in NVIDIA Newton for manipulation testing.",
    source: "Single product photo",
    engine: "NVIDIA Newton",
    output: "Articulated, sim-ready twin",
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
  { h: "We calibrate & validate", p: "Calibrated and physically validated in Isaac, Newton, or MuJoCo." },
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

/* ---- results gallery (editorial) ---- */
const gImg = $("#g-img");
const gStage = $("#g-stage");
let active = 0;

function renderGallery(i) {
  active = (i + assets.length) % assets.length;
  const a = assets[active];
  gImg.src = IMAGES[a.img];
  gImg.alt = a.name + " output";
  const inset = $("#g-inset");
  if (a.inImg && IMAGES[a.inImg]) {
    $("#g-in-img").src = IMAGES[a.inImg];
    $("#g-in-img").alt = a.name + " input";
    inset.classList.remove("hide");
  } else {
    inset.classList.add("hide");
  }
  $("#g-tag").textContent = a.status;
  $("#g-num").textContent = String(active + 1).padStart(2, "0");
  $("#g-total").textContent = String(assets.length).padStart(2, "0");
  $("#g-title").textContent = a.name;
  $("#g-desc").textContent = a.desc;
  $("#g-specs").innerHTML = [
    ["Source", a.source],
    ["Output", a.output],
    ["Physics engine", a.engine],
    ["Deliverables", a.deliverables],
  ].map(([k, v]) => `<div class="row"><div class="k">${k}</div><div class="v">${v}</div></div>`).join("");
}

function goTo(i) {
  gStage.classList.add("fade");
  setTimeout(() => { renderGallery(i); gStage.classList.remove("fade"); }, 170);
}

$("#g-prev").addEventListener("click", () => goTo(active - 1));
$("#g-next").addEventListener("click", () => goTo(active + 1));

/* drag / swipe on the stage; click (no drag) enlarges */
let dragging = false, dragMoved = false, startX = 0;
gStage.addEventListener("pointerdown", (e) => {
  dragging = true; dragMoved = false; startX = e.clientX;
  try { gStage.setPointerCapture(e.pointerId); } catch (err) {}
});
gStage.addEventListener("pointermove", (e) => {
  if (dragging && Math.abs(e.clientX - startX) > 8) dragMoved = true;
});
function endStageDrag(e) {
  if (!dragging) return;
  dragging = false;
  const dx = (e ? e.clientX : startX) - startX;
  if (dx <= -50) goTo(active + 1);
  else if (dx >= 50) goTo(active - 1);
}
gStage.addEventListener("pointerup", endStageDrag);
gStage.addEventListener("pointercancel", endStageDrag);
gStage.addEventListener("click", () => { if (!dragMoved) openLb(active); });

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

/* ---- lightbox ---- */
const lb = $("#lightbox");
let current = 0;
function openLb(i) {
  current = i;
  const a = assets[i];
  $("#lb-img").src = IMAGES[a.img];
  $("#lb-img").alt = a.name;
  $("#lb-title").textContent = a.name;
  $("#lb-sub").textContent = `${a.status} · ${a.engine} · ${a.output}`;
  lb.classList.add("open");
  lb.setAttribute("aria-hidden", "false");
}
function closeLb() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); }
function step(d) {
  const n = assets.length;
  const next = (current + d + n) % n;
  renderGallery(next);   // keep the gallery in sync with the lightbox
  openLb(next);
}
$("#lb-close").addEventListener("click", closeLb);
$("#lb-prev").addEventListener("click", () => step(-1));
$("#lb-next").addEventListener("click", () => step(1));
lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
document.addEventListener("keydown", (e) => {
  if (!lb.classList.contains("open")) return;
  if (e.key === "Escape") closeLb();
  if (e.key === "ArrowLeft") step(-1);
  if (e.key === "ArrowRight") step(1);
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
