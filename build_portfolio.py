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


def data_uri(path: pathlib.Path) -> str:
    return f"data:image/png;base64,{b64(path)}"


def main() -> None:
    prepare()
    images = {key: data_uri(BUILD / fname) for key, fname in IMAGE_FILES.items()}
    image_js = ",\n".join(f'    "{k}": "{v}"' for k, v in images.items())
    html = (
        TEMPLATE
        .replace("/*__IMAGES__*/", image_js)
        .replace("{{LOGO_DARK}}", data_uri(BUILD / "logo_dark.png"))
        .replace("{{LOGO_LIGHT}}", data_uri(BUILD / "logo_light.png"))
        .replace("{{HERO}}", data_uri(BUILD / "hero.png"))
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
<title>Moonlake — Robotics deployment with simulation & digital twins</title>
<link rel="icon" href="{{LOGO_DARK}}">
<style>
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
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Arial, sans-serif;
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
  .work { padding: 44px 0 0; }
  .work-head {
    display: flex; justify-content: space-between; align-items: flex-end;
    gap: 28px; flex-wrap: wrap; margin-bottom: 8px;
  }
  .work-head h2 {
    font-size: clamp(30px, 3.6vw, 46px); font-weight: 800;
    letter-spacing: -.035em; line-height: 1.02; margin: 12px 0 0; max-width: 18ch;
  }
  /* ---- credibility logo strip ---- */
  .logos { padding: 30px 0 4px; }
  .logos-label { font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--ink-3); margin: 0 0 18px; }
  .logos-row { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 44px; list-style: none; margin: 0; padding: 0; }
  .logos-row li { font-size: clamp(15px, 1.5vw, 21px); font-weight: 700; letter-spacing: -.01em; color: var(--ink-2); opacity: .82; }
  @media (max-width: 640px) { .logos-row { gap: 12px 26px; } }

  /* ---- results gallery (editorial) ---- */
  .gallery { margin-top: 26px; }
  .g-main { display: grid; grid-template-columns: 1.35fr 1fr; gap: clamp(24px, 4vw, 64px); align-items: stretch; }
  .g-stage {
    position: relative; margin: 0; border: 1px solid var(--hair); border-radius: 4px;
    background: var(--paper-2); overflow: hidden; aspect-ratio: 16 / 11;
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
  /* input inset — shows the source the output was generated from */
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
  /* thumbnail rail */
  .g-rail { display: flex; gap: 12px; margin-top: 26px; }
  .g-rail button {
    flex: 1 1 0; padding: 0; cursor: pointer; background: var(--paper-2);
    border: 1px solid var(--hair); border-radius: 3px; overflow: hidden;
    aspect-ratio: 16 / 10; transition: border-color .2s ease, opacity .2s ease; opacity: .55;
  }
  .g-rail button img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .g-rail button[aria-selected="true"] { opacity: 1; border-color: var(--ink); }
  .g-rail button:hover { opacity: 1; }
  @media (max-width: 820px) {
    .g-main { grid-template-columns: 1fr; gap: 22px; }
    .g-controls { margin-top: 22px; }
  }

  /* ---- process ---- */
  .process {
    padding: 52px 0; background: var(--paper-2);
    border-top: 1px solid var(--hair); border-bottom: 1px solid var(--hair); margin-top: 64px;
  }
  .process .kicker { display: block; margin-bottom: 14px; }
  .process h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; margin: 0 0 14px; max-width: 18ch; line-height: 1.02;
  }
  .process .sec-sub { margin: 0 0 28px; max-width: 60ch; }
  .steps { display: grid; grid-template-columns: repeat(4, 1fr); }
  .step {
    padding: 0 30px; border-left: 1px solid var(--hair);
    opacity: 0; transform: translateY(26px);
    transition: opacity .6s ease, transform .6s ease;
  }
  .step.in { opacity: 1; transform: none; }
  .step:first-child { padding-left: 0; border-left: 0; }
  .step .n { font-size: clamp(42px, 4.4vw, 66px); font-weight: 800; letter-spacing: -.04em; line-height: 1; }
  .step h4 { font-size: 18px; font-weight: 700; letter-spacing: -.01em; margin: 22px 0 8px; }
  .step p { font-weight: 400; color: var(--ink-2); font-size: 15px; margin: 0; }
  @media (max-width: 820px) { .steps { grid-template-columns: 1fr 1fr; gap: 44px 0; } .step:nth-child(3) { padding-left: 0; border-left: 0; } }
  @media (max-width: 480px) { .steps { grid-template-columns: 1fr; gap: 40px; } .step { padding-left: 0; border-left: 0; } }


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
  .caps { padding: 52px 0; }
  .caps .kicker { display: block; margin-bottom: 14px; }
  .caps h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; margin: 0; max-width: 22ch; line-height: 1.02;
  }
  .cap-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px;
    background: var(--hair); border: 1px solid var(--hair); margin-top: 40px;
  }
  .cap-item { background: var(--paper); padding: 30px; }
  .cap-item h4 { font-size: 17px; font-weight: 700; letter-spacing: -.01em; margin: 0 0 8px; }
  .cap-item h4::before {
    content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent); margin-right: 10px; vertical-align: middle; opacity: .55;
  }
  .cap-item p { font-weight: 400; color: var(--ink-2); font-size: 14px; margin: 0; line-height: 1.5; }
  @media (max-width: 820px) { .cap-grid { grid-template-columns: 1fr 1fr; } }
  @media (max-width: 520px) { .cap-grid { grid-template-columns: 1fr; } }

  /* ---- studio use cases ---- */
  .usecases { padding: 52px 0; border-top: 1px solid var(--hair); }
  .usecases .kicker { display: block; margin-bottom: 14px; }
  .usecases h2 {
    font-size: clamp(28px, 3.4vw, 44px); font-weight: 800;
    letter-spacing: -.035em; margin: 0 0 34px; max-width: 24ch; line-height: 1.02;
  }
  .uc-grid { display: grid; grid-template-columns: 1fr 1fr; column-gap: 56px; border-top: 1px solid var(--hair); }
  .uc {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 22px 0; border-bottom: 1px solid var(--hair);
    font-weight: 600; font-size: clamp(15px, 1.5vw, 18px); letter-spacing: -.01em;
  }
  .uc::before {
    content: ""; flex: 0 0 auto; width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent); margin-top: 9px; opacity: .6;
  }
  @media (max-width: 680px) { .uc-grid { grid-template-columns: 1fr; } }


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
    .step { opacity: 1; transform: none; }
  }
</style>
</head>
<body>

<div class="topbar">
  <div class="wrap">
    <a class="brand" href="#top" aria-label="Moonlake"><img src="{{LOGO_DARK}}" alt="Moonlake"></a>
    <nav>
      <a href="#examples">Lookbook</a>
      <a href="#capabilities">Capabilities</a>
      <a href="#how">How it works</a>
      <a href="mailto:studios@moonlake.ai">Contact</a>
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
        <p class="kicker">Moonlake — simulation &amp; digital twins for robotics OEMs</p>
        <h1>Accelerating robotics deployment with simulation and digital twins.</h1>
        <p class="lead">Moonlake helps robotics OEMs demo robots in customer spaces, validate deployments before install, and prep faster — turning real sites and assets into simulation-ready digital twins, scenes, and blend files.</p>
        <div class="actions">
          <a class="btn solid" href="#examples">See the lookbook</a>
          <a class="btn outline" href="mailto:studios@moonlake.ai">Contact</a>
        </div>
      </div>
    </div>
  </div>
</header>

<!-- credibility logo strip -->
<section class="logos">
  <div class="wrap">
    <p class="logos-label">Built by researchers &amp; engineers from</p>
    <ul class="logos-row">
      <li>NVIDIA</li>
      <li>DeepMind</li>
      <li>Anthropic</li>
      <li>Stanford</li>
      <li>Meta</li>
      <li>Waymo</li>
      <li>Autodesk</li>
      <li>AWS</li>
    </ul>
  </div>
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
    <p class="sec-sub">Input to output: a customer source — an image, video, or point cloud — turned into a simulation-ready asset, scene, and blend file. A growing lookbook of generated work.</p>

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
      <div class="g-rail" id="g-rail" role="tablist" aria-label="Results"></div>
    </div>
  </div>
</section>

<!-- 3. What Moonlake does -->
<section class="caps" id="capabilities">
  <div class="wrap">
    <span class="kicker">What Moonlake delivers</span>
    <h2>Outputs that de-risk every deployment.</h2>
    <p class="sec-sub">Moonlake turns the sources customers already have into simulation-ready assets, scenes, and blend files — connected to manufacturers and factories worldwide. You receive deliverables, not another tool to learn.</p>
    <div class="cap-grid" id="cap-grid"></div>
  </div>
</section>

<!-- 4. How it works -->
<section class="process" id="how">
  <div class="wrap">
    <span class="kicker">How it works</span>
    <h2>From your source to delivered assets.</h2>
    <p class="sec-sub">Send the inputs you already have — images, video, point clouds, or sensor data. Moonlake turns them into physically validated, simulation-ready assets and scenes.</p>
    <div class="steps" id="steps"></div>
  </div>
</section>

<!-- 5. Where it fits -->
<section class="usecases" id="usecases">
  <div class="wrap">
    <span class="kicker">Where it fits — robotics OEMs</span>
    <h2>For OEMs deploying robots into customer spaces.</h2>
    <div class="uc-grid" id="uc-grid"></div>
  </div>
</section>

<footer><div class="wrap foot">
  <span>© 2026 Moonlake — Simulation infrastructure for robotics deployment.</span>
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
   IMAGES — base64 data URIs, injected at build time
   ============================================================ */
const IMAGES = {
/*__IMAGES__*/
};

/* ============================================================
   CONFIG — data-driven content.
   `assets` drives the lookbook; each entry pairs a customer source
   (inImg) with the generated output, plus its deliverables.
   ============================================================ */
const assets = [
  {
    img: "twin_simrobot",
    inImg: "in_appliance",
    name: "Articulated appliance twin",
    desc: "A customer appliance and robot arm, reconstructed from a single product photo and calibrated in NVIDIA Newton — ready to demo and validate manipulation before anything ships.",
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
    desc: "A conveyor system rebuilt as a configurable, re-usable 3D asset with inferred structure — drop-in ready for line layouts and throughput simulation.",
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
    desc: "A full pick-and-place cell — robot, pallets, and racking — reconstructed and calibrated so the deployment can be validated against the real space before install.",
    source: "Factory photo / point cloud",
    engine: "NVIDIA Isaac Sim",
    output: "Validated work-cell twin",
    deliverables: ".blend · USD · validated",
    status: "Sim output",
  },
];

const capabilities = [
  { t: "Digital twins of customer spaces", d: "Turn a customer's real site into a sim-ready twin for demos and pre-deployment validation." },
  { t: "From the inputs you already have", d: "Images, video, point clouds, or sensor data — no special capture rig required." },
  { t: "Assets, scenes & blend files", d: "We deliver finished outputs — .blend and USD, sim-ready — not a tool to operate." },
  { t: "Articulation & physics inference", d: "Joints, articulation, and physical properties inferred for manipulable assets." },
  { t: "Physics-engine validated", d: "Calibrated and validated in NVIDIA Isaac, Newton, and MuJoCo." },
  { t: "Faster deployment prep", d: "Cut asset-creation and deployment-prep time from weeks to days." },
];

const pipeline = [
  { h: "You send a source", p: "An image, video, point cloud, or sensor data of the real asset or space." },
  { h: "We build it in 3D", p: "Reconstructed into 3D with inferred articulation and physics." },
  { h: "We calibrate & validate", p: "Calibrated in a physics engine — Isaac, Newton, or MuJoCo — until it's physically validated." },
  { h: "You receive deliverables", p: "Sim-ready assets, scenes, and blend files for demos, validation, and deployment prep." },
];

const useCases = [
  "Demoing robots in a customer's real space",
  "Pre-deployment visualization & validation",
  "Internal and customer-facing digital twins",
  "Faster deployment prep and asset creation",
  "Validating manipulation policies before install",
  "Connected to manufacturers & factories worldwide",
];

/* ============================================================
   RENDER
   ============================================================ */
const $ = (s) => document.querySelector(s);

/* ---- results gallery (editorial) ---- */
const gImg = $("#g-img");
const gStage = $("#g-stage");
const gRail = $("#g-rail");
let active = 0;

function renderGallery(i) {
  active = (i + assets.length) % assets.length;
  const a = assets[active];
  gImg.src = IMAGES[a.img];
  gImg.alt = a.name + " — generated output";
  const inset = $("#g-inset");
  if (a.inImg && IMAGES[a.inImg]) {
    $("#g-in-img").src = IMAGES[a.inImg];
    $("#g-in-img").alt = a.name + " — input source";
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
  [...gRail.children].forEach((b, k) => b.setAttribute("aria-selected", k === active));
}

function goTo(i) {
  gStage.classList.add("fade");
  setTimeout(() => { renderGallery(i); gStage.classList.remove("fade"); }, 170);
}

/* thumbnail rail */
gRail.innerHTML = assets.map((a, i) =>
  `<button role="tab" data-index="${i}" aria-selected="${i === 0}" aria-label="${a.name}"><img src="${IMAGES[a.img]}" alt="" draggable="false"></button>`).join("");
gRail.addEventListener("click", (e) => {
  const b = e.target.closest("button"); if (b) goTo(+b.dataset.index);
});
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

$("#cap-grid").innerHTML = capabilities
  .map((c) => `<div class="cap-item"><h4>${c.t}</h4><p>${c.d}</p></div>`).join("");

$("#steps").innerHTML = pipeline
  .map((s, i) => `<div class="step"><div class="n">${String(i + 1).padStart(2, "0")}</div><h4>${s.h}</h4><p>${s.p}</p></div>`).join("");

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
      `Company: ${company || "—"}`,
      `Email: ${email}`,
      "",
      message || "(no message provided)",
    ];
    const subject = `Moonlake pilot — ${name || "new inquiry"}`;
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
document.querySelectorAll(".step").forEach((el, i) => { el.dataset.i = i; io.observe(el); });

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
