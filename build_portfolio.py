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
    "rune_signpost": "assetrender1.png",
    "rose_cluster": "assetrender6.png",
    "ivy_lantern": "assetrender7.png",
    "bee_skep": "assetrender8.png",
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
<title>Moonlake — AI agents for game-ready 3D asset workflows</title>
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
  /* ---- coverflow carousel ---- */
  .carousel { position: relative; margin-top: 20px; }
  .viewport {
    overflow: hidden; padding: 34px 0 38px; cursor: grab; touch-action: pan-y;
    user-select: none; -webkit-user-select: none;
  }
  .viewport.dragging, .viewport.dragging .slide { cursor: grabbing; }
  .track {
    display: flex; align-items: center; gap: 0;
    will-change: transform; transition: transform .62s cubic-bezier(.22,.61,.36,1);
  }
  /* overlapping cards: neighbours tuck behind the focused card */
  .slide {
    flex: 0 0 auto; width: clamp(238px, 35vw, 392px);
    margin: 0 clamp(-72px, -5vw, -44px);
    transform: scale(.82); z-index: 1;
    transition: transform .62s cubic-bezier(.22,.61,.36,1);
    cursor: grab;
  }
  .slide.active { transform: scale(1); z-index: 3; }
  /* the card itself: render on top, details below */
  .card {
    position: relative;
    background: var(--paper); border: 1px solid var(--hair); border-radius: 18px;
    overflow: hidden; box-shadow: 0 10px 28px rgba(13,13,14,.10);
    transition: box-shadow .5s ease, border-color .5s ease;
  }
  /* solid paper veil dims neighbours without making the card see-through */
  .card::after {
    content: ""; position: absolute; inset: 0; z-index: 5; pointer-events: none;
    background: var(--paper); opacity: .58; transition: opacity .5s ease;
  }
  .slide.active .card { box-shadow: 0 26px 60px rgba(13,13,14,.24); border-color: var(--ink-3); }
  .slide.active .card::after { opacity: 0; }
  .card-media { position: relative; aspect-ratio: 1 / 1; background: var(--paper-2); }
  .card-media img {
    width: 100%; height: 100%; object-fit: contain; display: block;
    -webkit-user-drag: none; user-select: none; -webkit-user-select: none;
  }
  .card-info { padding: 15px 17px 18px; text-align: left; }
  .card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .card-name { font-size: 16px; font-weight: 800; letter-spacing: -.01em; line-height: 1.15; margin: 0; }
  .card-tris {
    flex: 0 0 auto; font-size: 11px; font-weight: 700; letter-spacing: .06em;
    padding: 5px 11px; border-radius: 999px; background: var(--ink); color: var(--paper); white-space: nowrap;
  }
  .card-desc {
    margin: 9px 0 0; font-size: 13px; line-height: 1.5; color: var(--ink-2);
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  }
  /* enlarge button — top-right corner of the focused card's image */
  .preview-btn {
    position: absolute; top: 10px; right: 10px; z-index: 3;
    display: flex; align-items: center; justify-content: center;
    width: 34px; height: 34px; padding: 0;
    border: 1px solid var(--hair); border-radius: 50%;
    background: rgba(249,248,243,.85); color: var(--ink); cursor: pointer;
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    opacity: 0; pointer-events: none;
    transition: opacity .4s ease, background .2s ease, color .2s ease, border-color .2s ease;
  }
  .preview-btn svg { display: block; }
  .slide.active .preview-btn { opacity: 1; pointer-events: auto; }
  .preview-btn:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  .viewport.dragging .track { transition: none; }
  /* drag affordance */
  .drag-hint {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    margin-top: 14px; font-size: 11px; font-weight: 700; letter-spacing: .2em;
    text-transform: uppercase; color: var(--ink-3); user-select: none;
    transition: opacity .4s ease;
  }
  .drag-hint.hide { opacity: 0; pointer-events: none; }
  .drag-hint .arw { font-size: 15px; line-height: 1; }
  @keyframes nudge { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(5px); } }
  .drag-hint .arw.r { animation: nudge 1.6s ease-in-out infinite; }
  .drag-hint .arw.l { animation: nudge 1.6s ease-in-out infinite reverse; }
  @media (prefers-reduced-motion: reduce) { .drag-hint .arw { animation: none; } }
  .card-media .badge {
    position: absolute; top: 10px; left: 10px; z-index: 2;
    font-size: 9px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
    color: var(--ink-2); background: rgba(249,248,243,.85); padding: 4px 8px; border-radius: 999px;
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    opacity: 0; transition: opacity .4s ease;
  }
  .slide.active .card-media .badge { opacity: 1; }

  /* nav arrows */
  .car-btn {
    position: absolute; top: 50%; transform: translateY(-50%); z-index: 5;
    width: 52px; height: 52px; border-radius: 50%; cursor: pointer;
    background: var(--paper); border: 1px solid var(--hair); color: var(--ink);
    font-size: 22px; line-height: 1; display: flex; align-items: center; justify-content: center;
    transition: background .2s ease, transform .2s ease, border-color .2s ease;
  }
  .car-btn:hover { border-color: var(--ink-3); transform: translateY(-50%) scale(1.06); }
  .car-btn.prev { left: 6px; } .car-btn.next { right: 6px; }
  @media (max-width: 560px) { .car-btn { width: 42px; height: 42px; font-size: 18px; } }

  /* dots */
  .car-dots { display: flex; gap: 10px; justify-content: center; margin-top: 20px; }
  .car-dots button {
    width: 9px; height: 9px; border-radius: 50%; padding: 0; cursor: pointer;
    border: 1px solid var(--ink-3); background: transparent; transition: background .2s ease, transform .2s ease;
  }
  .car-dots button[aria-current="true"] { background: var(--accent); border-color: var(--accent); transform: scale(1.15); }

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
      <a href="#examples">Examples</a>
      <a href="#capabilities">Capabilities</a>
      <a href="#how">How it works</a>
      <a href="#pilot">Contact</a>
    </nav>
  </div>
</div>

<header class="hero" id="top">
  <div class="hero-figure">
    <img src="{{HERO}}" alt="Wireframe 3D geometry generated by the Moonlake agent">
  </div>
  <div class="hero-copy">
    <div class="inner">
      <div class="copy-block">
        <p class="kicker">Moonlake — Blender 3D asset agent</p>
        <h1>AI agents for game-ready 3D asset workflows.</h1>
        <p class="lead">Moonlake helps game teams turn environment and prop briefs into 3D asset directions, starting with stylized non-character assets for Blender-based workflows.</p>
        <div class="actions">
          <a class="btn solid" href="#pilot">Contact</a>
          <a class="btn outline" href="#examples">View examples</a>
        </div>
      </div>
    </div>
  </div>
</header>

<!-- 2. Example asset carousel -->
<section class="work" id="examples">
  <div class="wrap">
    <div class="work-head">
      <div>
        <span class="kicker">Render previews</span>
        <h2>Example asset outputs.</h2>
      </div>
    </div>
    <p class="sec-sub">A selection of game-ready asset previews, each listed with its triangle count. More directions are on the way.</p>
    <div class="carousel">
      <div class="viewport"><div class="track" id="track"></div></div>
      <button class="car-btn prev" id="car-prev" aria-label="Previous asset">&#8249;</button>
      <button class="car-btn next" id="car-next" aria-label="Next asset">&#8250;</button>
      <div class="drag-hint" id="drag-hint"><span class="arw l">&#8249;</span> Drag or swipe to browse <span class="arw r">&#8250;</span></div>
      <div class="car-dots" id="car-dots"></div>
    </div>
  </div>
</section>

<!-- 3. What Moonlake generates -->
<section class="caps" id="capabilities">
  <div class="wrap">
    <span class="kicker">What Moonlake generates</span>
    <h2>Built for game asset and world-building tasks.</h2>
    <p class="sec-sub">Moonlake focuses on the part of game production between idea and usable 3D world: props, environment kits, terrain dressing, modular assets, and procedural asset systems.</p>
    <div class="cap-grid" id="cap-grid"></div>
  </div>
</section>

<!-- 4. How it works -->
<section class="process" id="how">
  <div class="wrap">
    <span class="kicker">How it works</span>
    <h2>From brief to editable asset direction.</h2>
    <p class="sec-sub">Start with a natural language brief, reference image, or style target. Moonlake generates visual outputs and structured asset concepts that can be refined toward Blender-based game production workflows.</p>
    <div class="steps" id="steps"></div>
  </div>
</section>

<!-- 5. Studio use cases -->
<section class="usecases" id="usecases">
  <div class="wrap">
    <span class="kicker">Studio use cases</span>
    <h2>For small teams building more world than they have time for.</h2>
    <div class="uc-grid" id="uc-grid"></div>
  </div>
</section>

<!-- 7. Pilot CTA -->
<section class="cta" id="pilot">
  <div class="wrap">
    <img src="{{LOGO_LIGHT}}" alt="Moonlake">
    <h2>Try Moonlake for your<br>asset workflow.</h2>
    <p>We're working with game teams to evaluate real environment and asset-generation tasks. Bring us a brief, reference, or workflow bottleneck, and we'll explore how Moonlake can help.</p>
    <form class="cta-form" id="contact-form">
      <div class="row">
        <div class="cta-field">
          <label for="cf-name">Name</label>
          <input id="cf-name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="cta-field">
          <label for="cf-company">Studio / company</label>
          <input id="cf-company" name="company" type="text" autocomplete="organization">
        </div>
      </div>
      <div class="cta-field">
        <label for="cf-email">Work email</label>
        <input id="cf-email" name="email" type="email" autocomplete="email" required>
      </div>
      <div class="cta-field">
        <label for="cf-msg">What are you working on?</label>
        <textarea id="cf-msg" name="message" placeholder="Tell us about the asset or environment workflow you'd like to test."></textarea>
      </div>
      <button class="btn" type="submit">Send message</button>
      <p class="cta-note" id="cf-note" role="status"></p>
    </form>
    <p class="cta-fine">Best fit for teams working on props, environment assets, modular kits, terrain dressing, or procedural world-building workflows.</p>
  </div>
</section>


<footer><div class="wrap foot">
  <span>© 2026 Moonlake — AI agents for 3D game asset workflows.</span>
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
   `assets` drives the carousel; each entry is one render preview,
   listed with its triangle count.
   ============================================================ */
const assets = [
  {
    img: "rune_signpost",
    name: "Runed Wayfinding Signpost",
    desc: "A weathered wooden signpost with stacked directional planks, hand-carved runes, and faint glowing glyphs, set into a mossy rock-and-root base.",
    brief: "Fantasy wooden signpost: several pointing plank signs with carved runic lettering and subtle glowing glyphs, on a worn post anchored in a mossy rock base with exposed roots.",
    use: "Fantasy RPG wayfinding / crossroads marker / forest or village path set dressing",
    style: "Stylized realism, weathered wood, fantasy, hand-painted detail",
    tris: "13k",
    status: "Preview",
  },
  {
    img: "rose_cluster",
    name: "Blooming Rose Cluster",
    desc: "A soft cluster of dusty-pink roses nestled in pale sage leaves, forming a low rounded bush.",
    brief: "Stylized rose bush: dome of clustered pink roses with sculpted petals and muted green foliage; cozy, hand-painted finish.",
    use: "Cozy sim / garden biome / fairy-tale set dressing / Roblox decoration",
    style: "Chibi, cozy, pastel, soft stylized florals",
    tris: "9k",
    status: "Preview",
  },
  {
    img: "ivy_lantern",
    name: "Ivy Shepherd's Lantern",
    desc: "An ornate cream lantern hanging from a curved wrought-iron shepherd's hook wrapped in trailing ivy.",
    brief: "Hanging garden lantern: cream filigree lantern on a curved metal shepherd's-hook pole with climbing ivy leaves; soft fantasy garden detail.",
    use: "Cozy RPG path / garden biome / fairy-village lighting prop",
    style: "Chibi, cozy fantasy, pastel, soft stylized",
    tris: "9k",
    status: "Preview",
  },
  {
    img: "bee_skep",
    name: "Honeybee Skep Hive",
    desc: "A rounded woven bee skep with dripping honey, a small entrance hole, and bees buzzing around clusters of tiny flowers.",
    brief: "Stylized bee skep: stacked coiled-straw dome with honey drips, a round entrance, scattered bees, and small dried flowers; warm cozy palette.",
    use: "Cozy sim / farming game / meadow biome / Roblox apiary prop",
    style: "Chibi, cozy, warm pastel, soft stylized nature",
    tris: "9k",
    status: "Preview",
  },
];

const capabilities = [
  { t: "Props & environment assets", d: "Standalone set pieces and background props for dressing scenes." },
  { t: "Modular kits", d: "Tileable, snap-together pieces for building out larger structures." },
  { t: "Style-consistent variants", d: "Multiple takes on an asset that hold a single visual language." },
  { t: "Terrain dressing assets", d: "Rocks, foliage, and scatter detail for grounding environments." },
  { t: "Procedural scatter systems", d: "Rules for distributing assets across a scene at world scale." },
  { t: "Blender-first workflows", d: "Outputs aimed at Blender-based pipelines and DCC handoff." },
];

const pipeline = [
  { h: "Describe the asset or workflow", p: "Start from a natural-language brief, a reference image, or a style target." },
  { h: "Generate asset directions", p: "Moonlake returns visual outputs and structured asset concepts to react to." },
  { h: "Iterate with constraints", p: "Refine against production constraints — style, scope and direction." },
  { h: "Move toward production", p: "Carry the chosen direction toward Blender-based game production." },
];

const useCases = [
  "Indie teams prototyping environments",
  "Roblox studios producing themed worlds",
  "Technical artists generating prop variants",
  "Environment artists exploring style directions",
  "Small teams building vertical slices",
  "Teams experimenting with procedural world-building workflows",
];

/* ============================================================
   RENDER
   ============================================================ */
const $ = (s) => document.querySelector(s);

/* ---- coverflow carousel ---- */
const track = $("#track");
const dotsWrap = $("#car-dots");
let active = 0;
let slides = [];
let dots = [];

function currentTX() {
  // translate the track so the active slide sits in the middle of the viewport
  const vw = track.parentElement.clientWidth;
  const s = slides[active];
  return -(s.offsetLeft + s.offsetWidth / 2 - vw / 2);
}
function center() { track.style.transform = `translateX(${currentTX()}px)`; }

function go(i) {
  active = (i + slides.length) % slides.length;
  slides.forEach((s, k) => {
    s.classList.toggle("active", k === active);
    s.style.zIndex = String(slides.length - Math.abs(k - active)); // focused card on top, neighbours tuck behind symmetrically
  });
  dots.forEach((d, k) => d.setAttribute("aria-current", k === active));
  center();
}

let dragMoved = false;
track.addEventListener("click", (e) => {
  if (dragMoved) { dragMoved = false; return; }   // ignore the click that ends a drag
  if (e.target.closest(".preview-btn")) { openLb(active); return; }  // Enlarge button
  const s = e.target.closest(".slide");
  if (!s) return;
  const i = +s.dataset.index;
  if (i !== active) go(i);   // side slide -> focus (use the Enlarge button to zoom the active one)
});
dotsWrap.addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (b) go(+b.dataset.index);
});
$("#car-prev").addEventListener("click", () => go(active - 1));
$("#car-next").addEventListener("click", () => go(active + 1));

/* ---- drag / swipe to browse ---- */
const viewport = track.parentElement;
const dragHint = $("#drag-hint");
let dragging = false, startX = 0, dragDX = 0, baseTX = 0;

viewport.addEventListener("pointerdown", (e) => {
  if (e.target.closest(".preview-btn")) return;   // let the enlarge button receive its click
  if (slides.length < 2) return;
  dragging = true; dragMoved = false;
  startX = e.clientX; dragDX = 0; baseTX = currentTX();
  viewport.classList.add("dragging");
  viewport.setPointerCapture(e.pointerId);
  if (dragHint) dragHint.classList.add("hide");
});
viewport.addEventListener("pointermove", (e) => {
  if (!dragging) return;
  dragDX = e.clientX - startX;
  if (Math.abs(dragDX) > 6) dragMoved = true;
  track.style.transform = `translateX(${baseTX + dragDX}px)`;
});
function endDrag(e) {
  if (!dragging) return;
  dragging = false;
  viewport.classList.remove("dragging");
  if (dragMoved) {
    const threshold = Math.min(220, viewport.clientWidth * 0.22);
    if (dragDX <= -threshold) go(active + 1);
    else if (dragDX >= threshold) go(active - 1);
    else center();   // snap back to current slide
  } else {
    // a tap (no drag) — jump to whichever card was clicked
    const el = e ? document.elementFromPoint(e.clientX, e.clientY) : null;
    const s = el && el.closest(".slide");
    if (s) { const i = +s.dataset.index; if (i !== active) go(i); else center(); }
    else center();
  }
  dragDX = 0;
}
viewport.addEventListener("pointerup", endDrag);
viewport.addEventListener("pointercancel", endDrag);

function buildCarousel() {
  track.innerHTML = assets.map((a, i) => `
    <div class="slide${i === 0 ? " active" : ""}" data-index="${i}">
      <div class="card">
        <div class="card-media">
          <span class="badge">${a.status}</span>
          <button class="preview-btn" type="button" aria-label="Enlarge ${a.name}"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="20" y1="20" x2="16.65" y2="16.65"></line></svg></button>
          <img src="${IMAGES[a.img]}" alt="${a.name} — render preview" loading="lazy" draggable="false">
        </div>
        <div class="card-info">
          <div class="card-head">
            <h4 class="card-name">${a.name}</h4>
            <span class="card-tris">${a.tris} tris</span>
          </div>
          <p class="card-desc">${a.desc}</p>
        </div>
      </div>
    </div>`).join("");
  dotsWrap.innerHTML = assets
    .map((_, i) => `<button data-index="${i}" aria-current="${i === 0}" aria-label="Asset ${i + 1}"></button>`).join("");
  slides = [...track.querySelectorAll(".slide")];
  dots = [...dotsWrap.querySelectorAll("button")];
  const hint = $("#drag-hint");
  if (hint) hint.classList.toggle("hide", slides.length < 2);
  go(0);
}

buildCarousel();
window.addEventListener("load", center);
window.addEventListener("resize", center);

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
  $("#lb-sub").textContent = `${a.status} · ${a.tris} tris · ${a.style}`;
  lb.classList.add("open");
  lb.setAttribute("aria-hidden", "false");
}
function closeLb() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); }
function step(d) {
  const n = assets.length;
  const next = (current + d + n) % n;
  go(next);          // keep the carousel in sync with the lightbox
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
