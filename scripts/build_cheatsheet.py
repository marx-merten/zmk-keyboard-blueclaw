#!/usr/bin/env python3
"""Generate a fancy, self-contained Blueclaw keymap cheat sheet (doc/cheatsheet.html).

Pipeline:
  config/blueclaw.keymap --(keymap-drawer parse, via Makefile)--> doc/keymap.yaml
  doc/keymap.yaml --(this script: categorise every key)--> annotated layers
  annotated layers --(keymap-drawer draw, per layer)--> inline SVGs
  SVGs + hand-written explainer sections --> doc/cheatsheet.html

The HTML ships both Catppuccin Latte (light, default) and Macchiato (dark)
themes with a toggle, and a print stylesheet. Run via `make cheatsheet`
(which uses `uv run --with pyyaml` so PyYAML is available).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "doc"
KEYMAP_YAML = DOC / "keymap.yaml"
INFO_JSON = ROOT / "config" / "blueclaw.json"
CONF = ROOT / "keymapper.conf"
OUT = DOC / "cheatsheet.html"

# Layer order matters (referenced by index in the keymap) + how you reach each.
# extra2/extra3/extra4 are empty placeholders and are intentionally omitted.
LAYERS = [
    ("Base", 0, "Default layer — always active."),
    ("symbols", 1, "Hold the <b>right thumb</b> (Space)."),
    ("numbers", 2, "Hold the <b>left-inner thumb</b> (Esc)."),
    ("Nav", 3, "Hold the <b>left-middle thumb</b> (Enter)."),
    ("sys", 4, "Hold <b>mo</b> on the inner lower-thumb key (momentary)."),
    ("f-keys", 5, "Hold <b>mo</b> on the outer lower-thumb key (momentary)."),
    ("layers", 6, "Hold <b>mo</b> on a middle lower-thumb key — Hyper shortcuts + a <code>&amp;to</code> layer switcher."),
    ("game", 7, "Toggle on with <code>&rarr; game</code> (<code>&amp;to 7</code>) from num / BIOS; <code>&amp;to 0</code> returns to Base."),
    ("mouse", 8, "Combo: <b>Space + Backspace</b> (right thumbs)."),
    ("BIOS", 12, "Combo: <b>Space + sys</b> key."),
]

# ---------------------------------------------------------------------------
# Key categorisation: map each parsed key to a CSS class used for colour-coding.
# ---------------------------------------------------------------------------
MODS = {
    "LCTRL", "RCTRL", "LEFT CONTROL", "RIGHT CONTROL", "LEFT ALT", "RIGHT ALT",
    "LEFT GUI", "RIGHT GUI", "LEFT SHIFT", "RIGHT SHIFT", "LEFT COMMAND",
    "RIGHT COMMAND", "MEH", "HYPER",
}
LAYER_HOLDS = {
    "Base", "symbols", "numbers", "Nav", "sys", "f-keys", "layers",
    "game", "mouse", "BIOS", "toggle",
}
MACRO_HOLDS = {"Zoom", "Pass1", "Pass2"}

GLYPH_CAT = {
    "mdi:arrow-up-bold": "nav", "mdi:arrow-down-bold": "nav",
    "mdi:arrow-left-bold": "nav", "mdi:arrow-right-bold": "nav",
    "mdi:menu": "nav",
    "mdi:keyboard-return": "special", "mdi:keyboard-tab": "special",
    "tabler:backspace": "special", "mdi:keyboard-caps": "special",
    "mdi:apple-keyboard-shift": "special",
    "tabler:copy": "special", "tabler:paste": "special",
    "mdi:cog": "system",
    "tabler:brackets-contain": "macro", "tabler:repeat": "macro",
    "tabler:math-equal-lower": "symbol", "tabler:math-equal-greater": "symbol",
}

MEDIA_WORDS = {
    "MUTE", "VOL DN", "VOL UP", "VOLUME UP", "VOLUME DOWN", "PLAY PAUSE", "PP",
    "PREV", "NEXT", "STOP", "BRI DN", "BRI UP", "LOCK",
}
NAV_WORDS = {"HOME", "END", "PG UP", "PG DN"}
SPECIAL_WORDS = {"ESC", "TAB", "ENTER", "DELETE", "DEL", "SPACE", "CAPSLOCK", "CAPS"}


def _glyph(text: str) -> str | None:
    m = re.fullmatch(r"\$\$([a-z]+:[a-z0-9-]+)\$\$", text or "")
    return m.group(1) if m else None


def categorise(key) -> str | None:
    """Return a CSS category class for a parsed keymap-drawer key, or None to
    leave the key as-is (transparent / held / explicitly-typed keys)."""
    if isinstance(key, str):
        tap, hold, typ = key, None, None
    else:
        tap, hold, typ = key.get("t", ""), key.get("h"), key.get("type")

    if typ in ("trans", "held", "ghost"):
        return None
    if tap == "" and not hold:
        return "blank"

    # Hold dominates: home-row mods / mod-taps vs layer access.
    if hold:
        if hold in MODS:
            return "mod"
        if hold in LAYER_HOLDS:
            return "layer"
        if hold in MACRO_HOLDS:
            return "macro"
        if hold == "WORD":
            return "special"

    g = _glyph(tap)
    if g:
        return GLYPH_CAT.get(g, "special")

    t = (tap or "").strip()
    if t in LAYER_HOLDS:
        return "layer"  # momentary &mo layer keys render as the bare layer name
    if re.fullmatch(r"[A-Za-z]", t):
        return "alpha"
    if re.fullmatch(r"[0-9]", t):
        return "num"
    if re.fullmatch(r"F[0-9]{1,2}", t):
        return "fn"
    if t in NAV_WORDS:
        return "nav"
    if t in MEDIA_WORDS:
        return "media"
    if t in SPECIAL_WORDS:
        return "special"
    if t.startswith(("BT ", "RGB ", "OUT ", "&bt_", "&sys_reset")) or t == "&bootloader":
        return "system"
    if t.startswith(("KVM", "Ctl+Sft", "&m_")) or t in {"->", "=>", "--", "++", "..\\"}:
        return "macro"
    if t == "&intelligent_shift":
        return "special"
    if t and re.fullmatch(r"[^\w\s]+", t):
        return "symbol"
    return "special"


def annotate(layer_keys):
    """Return a copy of a layer's key list with a `type` category attached."""
    out = []
    for key in layer_keys:
        cat = categorise(key)
        if cat is None:
            out.append(key)
            continue
        if isinstance(key, str):
            key = {"t": key} if key != "" else {"t": ""}
        else:
            key = dict(key)
        key["type"] = cat
        out.append(key)
    return out


# ---------------------------------------------------------------------------
# Render one layer to an inline <svg> string via keymap-drawer.
# ---------------------------------------------------------------------------
def draw_layer(annotated_doc: dict, layer: str, combos: bool) -> str:
    tmp = DOC / f".cheat_{layer}.yaml"
    tmp.write_text(yaml.safe_dump(annotated_doc, sort_keys=False, allow_unicode=True))
    cmd = [
        "uvx", "--from", "keymap-drawer", "keymap", "-c", str(CONF), "draw",
        "--select-layers", layer, "-j", str(INFO_JSON), str(tmp),
    ]
    if not combos:
        cmd.insert(cmd.index("draw") + 1, "--keys-only")
    res = subprocess.run(cmd, capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        raise SystemExit(f"keymap-drawer failed for layer {layer}")
    svg = res.stdout
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)  # strip XML decl for inlining
    return svg.strip()


# ---------------------------------------------------------------------------
# Theme palettes (Catppuccin) + CSS generation.
# ---------------------------------------------------------------------------
LATTE = dict(
    base="#eff1f5", mantle="#e6e9ef", crust="#dce0e8", text="#4c4f69",
    subtext0="#6c6f85", overlay0="#9ca0b0", surface0="#ccd0da",
    surface1="#bcc0cc", surface2="#acb0be", blue="#1e66f5", lavender="#7287fd",
    sapphire="#209fb5", teal="#179299", green="#40a02b", yellow="#df8e1d",
    peach="#fe640b", red="#d20f39", mauve="#8839ef", pink="#ea76cb",
)
MACCHIATO = dict(
    base="#24273a", mantle="#1e2030", crust="#181926", text="#cad3f5",
    subtext0="#a5adcb", overlay0="#6e738d", surface0="#363a4f",
    surface1="#494d64", surface2="#5b6078", blue="#8aadf4", lavender="#b7bdf8",
    sapphire="#7dc4e4", teal="#8bd5ca", green="#a6da95", yellow="#eed49f",
    peach="#f5a97f", red="#ed8796", mauve="#c6a0f6", pink="#f5bde6",
)

# category -> palette accent key
CAT_ACCENT = {
    "mod": "mauve", "layer": "green", "num": "blue", "symbol": "peach",
    "nav": "sapphire", "media": "teal", "fn": "yellow", "system": "red",
    "macro": "pink", "special": "lavender",
}
LEGEND = [
    ("alpha", "Letters"), ("mod", "Home-row mod"), ("layer", "Layer access"),
    ("num", "Numbers"), ("symbol", "Symbols"), ("nav", "Navigation"),
    ("media", "Media"), ("fn", "Function"), ("system", "System · BT · RGB"),
    ("macro", "Macros"), ("special", "Editing / special"),
    ("trans", "Transparent"),
]


def theme_css(name: str, p: dict, op: float) -> str:
    # Colour rules are scoped to `svg.keymap` (not `.kbd`) so they apply to the
    # inline thumbnails AND the cloned SVG shown in the zoom lightbox.
    rules = [f"""
.theme-{name} {{
  --bg:{p['base']}; --panel:{p['mantle']}; --panel2:{p['crust']};
  --text:{p['text']}; --muted:{p['subtext0']}; --border:{p['surface1']};
  --brand:{p['mauve']}; --brand2:{p['blue']}; --link:{p['blue']};
}}
.theme-{name} svg.keymap, .theme-{name} svg.keymap text {{ fill:{p['text']}; }}
.theme-{name} svg.keymap text.hold, .theme-{name} svg.keymap text.shifted {{ fill:{p['subtext0']}; }}
.theme-{name} svg.keymap text.trans {{ fill:{p['overlay0']}; }}
.theme-{name} svg.keymap rect.key {{ fill:{p['surface0']}; stroke:{p['surface2']}; }}
.theme-{name} svg.keymap rect.key.alpha {{ fill:{p['surface0']}; stroke:{p['surface2']}; }}
.theme-{name} svg.keymap rect.key.blank {{ fill:none; stroke:none; }}
.theme-{name} svg.keymap rect.held {{ fill:{p['red']}; fill-opacity:{op + .06:.2f}; stroke:{p['red']}; }}
.theme-{name} svg.keymap rect.combo {{ fill:{p['lavender']}; fill-opacity:{op:.2f}; stroke:{p['lavender']}; }}
.theme-{name} svg.keymap path.combo {{ stroke:{p['overlay0']}; }}
.theme-{name} .chip.alpha .sw {{ background:{p['surface0']}; border-color:{p['surface2']}; }}
.theme-{name} .chip.trans .sw {{ background:transparent; border-style:dashed; border-color:{p['overlay0']}; }}
"""]
    for cat, accent in CAT_ACCENT.items():
        c = p[accent]
        rules.append(
            f".theme-{name} svg.keymap rect.key.{cat} {{ fill:{c}; fill-opacity:{op:.2f}; stroke:{c}; }}\n"
            f".theme-{name} .chip.{cat} .sw {{ background:{c}; border-color:{c}; }}"
        )
    return "\n".join(rules)


def legend_html() -> str:
    chips = []
    for cat, label in LEGEND:
        chips.append(f'<span class="chip {cat}"><span class="sw"></span>{label}</span>')
    return '<div class="legend">' + "".join(chips) + "</div>"


# ---------------------------------------------------------------------------
# Static (theme-independent) CSS — layout & chrome, driven by CSS variables.
# ---------------------------------------------------------------------------
STATIC_CSS = """
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
  Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);
  line-height:1.5;transition:background .2s,color .2s}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.hero{position:sticky;top:0;z-index:20;backdrop-filter:saturate(140%) blur(8px);
  background:color-mix(in srgb,var(--panel) 86%,transparent);
  border-bottom:1px solid var(--border)}
.hero .wrap{display:flex;align-items:center;gap:16px;padding:14px 20px}
.hero h1{font-size:20px;margin:0;letter-spacing:.3px}
.hero .sub{color:var(--muted);font-size:13px;margin-left:2px}
.hero .spacer{flex:1}
.toc{display:flex;flex-wrap:wrap;gap:8px;font-size:13px}
.toc a{padding:5px 11px;border:1px solid var(--border);border-radius:999px;
  background:var(--panel);color:var(--text)}
.toc a:hover{border-color:var(--brand);text-decoration:none}
#themeToggle{cursor:pointer;border:1px solid var(--border);background:var(--panel);
  color:var(--text);border-radius:999px;padding:6px 13px;font-size:13px}
#themeToggle:hover{border-color:var(--brand)}
section{padding:34px 0 8px}
h2.sec{font-size:22px;margin:0 0 4px;display:flex;align-items:center;gap:10px}
.sec .hint{font-size:13px;color:var(--muted);font-weight:400}
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin:14px 0 4px}
.chip{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
.chip .sw{width:15px;height:15px;border-radius:4px;border:1.5px solid;display:inline-block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:18px;margin-top:18px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:14px;
  padding:16px 16px 10px;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.card .head{display:flex;align-items:baseline;gap:10px;margin-bottom:6px}
.badge{font-variant-numeric:tabular-nums;font-weight:700;font-size:12px;color:#fff;
  background:var(--brand);border-radius:7px;padding:2px 8px;line-height:1.4}
.card h3{margin:0;font-size:17px}
.card .how{font-size:12.5px;color:var(--muted);margin:0 0 8px}
.kbd{filter:drop-shadow(0 1px 1px rgba(0,0,0,.06));cursor:zoom-in;position:relative;
  border-radius:10px;transition:box-shadow .15s,outline-color .15s;outline:2px solid transparent}
.kbd:hover,.kbd:focus-visible{outline-color:var(--brand);outline-offset:3px}
.kbd:focus{outline-color:var(--brand);outline-offset:3px}
.kbd::after{content:"⤢ click to zoom";position:absolute;top:6px;right:8px;font-size:11px;
  color:var(--muted);background:color-mix(in srgb,var(--panel) 80%,transparent);
  border:1px solid var(--border);border-radius:6px;padding:1px 7px;opacity:0;transition:opacity .15s;
  pointer-events:none}
.kbd:hover::after,.kbd:focus-visible::after{opacity:1}
.kbd svg{width:100%;height:auto;display:block}
.kbd text.label{display:none}
/* lightbox / zoom overlay */
.lightbox{position:fixed;inset:0;z-index:100;display:none;align-items:center;justify-content:center;
  padding:24px;background:color-mix(in srgb,var(--bg) 28%,rgba(0,0,0,.72));
  -webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px)}
.lightbox.open{display:flex}
.lightbox .box{background:var(--panel);border:1px solid var(--border);border-radius:16px;
  padding:14px 18px 16px;max-width:97vw;max-height:95vh;display:flex;flex-direction:column;
  box-shadow:0 24px 70px rgba(0,0,0,.45)}
.lightbox .lb-head{display:flex;align-items:center;gap:10px;margin:0 0 8px}
.lightbox .lb-head .badge{background:var(--brand)}
.lightbox .lb-title{font-weight:600;font-size:16px}
.lightbox .lb-close{margin-left:auto;cursor:pointer;border:1px solid var(--border);
  background:var(--panel2);color:var(--text);border-radius:9px;font-size:18px;line-height:1;
  padding:5px 11px}
.lightbox .lb-close:hover{border-color:var(--brand)}
.lightbox .lb-body{overflow:auto}
.lightbox .lb-body svg{width:92vw;max-height:82vh;height:auto;display:block}
.lightbox .lb-body text.label{display:none}
table.ref{border-collapse:collapse;width:100%;margin-top:12px;font-size:14px}
table.ref th,table.ref td{border:1px solid var(--border);padding:7px 10px;text-align:left}
table.ref th{background:var(--panel2);font-weight:600}
table.ref tbody tr:nth-child(odd){background:var(--panel)}
kbd{font-family:SFMono-Regular,Consolas,Menlo,monospace;font-size:12.5px;
  background:var(--panel2);border:1px solid var(--border);border-bottom-width:2px;
  border-radius:5px;padding:1px 6px;white-space:nowrap}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.note{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--brand);
  border-radius:8px;padding:12px 14px;font-size:13.5px;color:var(--muted);margin-top:14px}
footer{margin:40px 0;padding-top:18px;border-top:1px solid var(--border);
  color:var(--muted);font-size:12.5px;text-align:center}
@media print{
  header.hero{position:static;backdrop-filter:none}
  .toc,#themeToggle,.kbd::after,.lightbox{display:none!important}
  .kbd{cursor:default;outline:none}
  .grid,.cols{grid-template-columns:1fr 1fr}
  .card,.note,table.ref{box-shadow:none;break-inside:avoid}
  section{padding:14px 0 4px}
  a{color:inherit}
}
"""


def card(layer, idx, how, svg):
    return f"""<article class="card" id="layer-{layer}">
  <div class="head"><span class="badge">{idx}</span><h3>{layer}</h3></div>
  <p class="how">{how}</p>
  <div class="kbd" data-title="{idx} · {layer}" tabindex="0" role="button"
       aria-label="Zoom {layer} layer">{svg}</div>
</article>"""


def build():
    data = yaml.safe_load(KEYMAP_YAML.read_text())
    layers_in = data.get("layers", {})

    # Annotate every layer once; reuse the annotated doc per render.
    annotated = {"layout": data.get("layout", {}),
                 "layers": {name: annotate(keys) for name, keys in layers_in.items()},
                 "combos": data.get("combos", [])}

    print("Rendering layers:", ", ".join(name for name, *_ in LAYERS), file=sys.stderr)
    cards = []
    for name, idx, how in LAYERS:
        if name not in annotated["layers"]:
            continue
        svg = draw_layer(annotated, name, combos=False)
        cards.append(card(name, idx, how, svg))

    combos_svg = draw_layer(annotated, "Base", combos=True)

    toc = "".join(
        f'<a href="#layer-{name}">{idx} · {name}</a>' for name, idx, *_ in LAYERS
    ) + '<a href="#homerow">Home-row mods</a><a href="#combos">Combos</a>' \
        '<a href="#thumbs">Thumbs &amp; layers</a><a href="#behaviors">Behaviors</a>'

    css = STATIC_CSS + theme_css("light", LATTE, 0.18) + theme_css("dark", MACCHIATO, 0.24)

    html = TEMPLATE.format(
        css=css,
        toc=toc,
        legend=legend_html(),
        cards="\n".join(cards),
        combos_svg=combos_svg,
    )
    OUT.write_text(html)
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(html) // 1024} KB)", file=sys.stderr)


TEMPLATE = """<!doctype html>
<html lang="en" class="theme-light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blueclaw — Keymap Guide &amp; Cheat Sheet</title>
<style>{css}</style>
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div>
      <h1>Blueclaw <span class="sub">keymap guide &amp; cheat sheet</span></h1>
    </div>
    <div class="spacer"></div>
    <nav class="toc">{toc}</nav>
    <button id="themeToggle" title="Toggle light / dark">🌙 Dark</button>
  </div>
</header>

<main class="wrap">
  <section id="legend-sec" style="padding-top:22px">
    <h2 class="sec">Legend <span class="hint">keys are tinted by function</span></h2>
    {legend}
    <div class="note">Each key shows its <b>tap</b> action large and centred; a
      smaller label <b>below</b> is the <b>hold</b> action (layer or modifier).
      <span style="color:var(--muted)">▽</span> means the key is transparent —
      it falls through to the layer beneath.</div>
  </section>

  <section id="layers">
    <h2 class="sec">Layers <span class="hint">10 active layers · referenced by index</span></h2>
    <div class="grid">
{cards}
    </div>
  </section>

  <section id="homerow">
    <h2 class="sec">Home-row mods <span class="hint">hold a home key for a modifier</span></h2>
    <p>Hold-tap on the home row: a quick tap types the letter, a longer hold (≈280&nbsp;ms,
       <i>balanced</i> flavour, positional) acts as a modifier. Tapping is protected by a
       175&nbsp;ms quick-tap and 150&nbsp;ms prior-idle requirement to avoid misfires while typing.</p>
    <div class="cols">
      <table class="ref"><thead><tr><th>Left hand</th><th>Modifier</th></tr></thead><tbody>
        <tr><td><kbd>A</kbd></td><td>Control</td></tr>
        <tr><td><kbd>R</kbd></td><td>Alt / Option</td></tr>
        <tr><td><kbd>S</kbd></td><td>GUI / Command</td></tr>
        <tr><td><kbd>T</kbd></td><td>Shift</td></tr>
      </tbody></table>
      <table class="ref"><thead><tr><th>Right hand</th><th>Modifier</th></tr></thead><tbody>
        <tr><td><kbd>N</kbd></td><td>Shift</td></tr>
        <tr><td><kbd>E</kbd></td><td>GUI / Command</td></tr>
        <tr><td><kbd>I</kbd></td><td>Alt / Option</td></tr>
        <tr><td><kbd>O</kbd></td><td>Control</td></tr>
      </tbody></table>
    </div>
    <div class="note">Bonus: holding <kbd>/</kbd> (right pinky) gives <b>MEH</b>
      (Ctrl + Alt + Shift) for app shortcuts.</div>
  </section>

  <section id="combos">
    <h2 class="sec">Combos <span class="hint">press keys together</span></h2>
    <div class="cols" style="align-items:start">
      <table class="ref"><thead><tr><th>Press together</th><th>Result</th></tr></thead><tbody>
        <tr><td><kbd>L</kbd> + <kbd>U</kbd></td><td>Esc</td></tr>
        <tr><td><kbd>Space</kbd> + <kbd>Backspace</kbd></td><td><b>mouse</b> layer (momentary)</td></tr>
        <tr><td><kbd>Space</kbd> + <kbd>sys</kbd></td><td><b>BIOS</b> layer (momentary)</td></tr>
      </tbody></table>
      <div class="kbd" data-title="Combos · Base" tabindex="0" role="button"
           aria-label="Zoom combos">{combos_svg}</div>
    </div>
  </section>

  <section id="thumbs">
    <h2 class="sec">Thumbs &amp; layer access</h2>
    <table class="ref"><thead><tr><th>Thumb / key</th><th>Tap</th><th>Hold</th></tr></thead><tbody>
      <tr><td>Left outer</td><td>Tab</td><td>Command</td></tr>
      <tr><td>Left middle</td><td>Enter</td><td><b>Nav</b> layer</td></tr>
      <tr><td>Left inner</td><td>Esc</td><td><b>numbers</b> layer</td></tr>
      <tr><td>Right inner</td><td>Shift</td><td>Caps Word (double-tap)</td></tr>
      <tr><td>Right middle</td><td>Space</td><td><b>symbols</b> layer</td></tr>
      <tr><td>Right outer</td><td>Backspace</td><td>—</td></tr>
      <tr><td>Lower thumb row</td><td colspan="2"><kbd>mo</kbd> momentary: <b>f-keys</b> · <b>layers</b> · <b>layers</b> · <b>sys</b></td></tr>
    </tbody></table>
    <div class="note">The <b>layers</b> layer doubles as a hub: hold it for Hyper
      (Ctrl+Alt+Shift+GUI) shortcuts on every letter, and tap its thumb keys
      (<code>&amp;to</code>) to jump straight to symbols / numbers / Nav / sys / f-keys.</div>
  </section>

  <section id="behaviors">
    <h2 class="sec">Smart behaviors</h2>
    <div class="cols">
      <table class="ref"><thead><tr><th>Mod-morph</th><th>Tap</th><th>With Shift / GUI</th></tr></thead><tbody>
        <tr><td>Grave-Esc</td><td>Esc</td><td>~ (Shift)</td></tr>
        <tr><td>Quote</td><td>'</td><td>` (Shift)</td></tr>
        <tr><td>Dot-comma</td><td>.</td><td>, (Shift)</td></tr>
        <tr><td>Left bracket</td><td>[</td><td>( (GUI)</td></tr>
        <tr><td>Right bracket</td><td>]</td><td>) (GUI)</td></tr>
      </tbody></table>
      <table class="ref"><thead><tr><th>Tap-dance</th><th>Tap</th><th>Double-tap</th></tr></thead><tbody>
        <tr><td>Intelligent Shift</td><td>Shift</td><td>Caps Word</td></tr>
      </tbody></table>
    </div>
  </section>

  <footer>
    Generated from <code>config/blueclaw.keymap</code> via keymap-drawer · Catppuccin
    Latte / Macchiato · run <code>make cheatsheet</code> to regenerate.
  </footer>
</main>

<div class="lightbox" id="lightbox" aria-modal="true" role="dialog">
  <div class="box">
    <div class="lb-head">
      <span class="badge" id="lbBadge"></span>
      <span class="lb-title" id="lbTitle"></span>
      <button class="lb-close" id="lbClose" title="Close (Esc)" aria-label="Close">✕</button>
    </div>
    <div class="lb-body" id="lbBody"></div>
  </div>
</div>

<script>
(function(){{
  var KEY='blueclaw-theme';
  var root=document.documentElement, btn=document.getElementById('themeToggle');
  function apply(t){{
    root.classList.remove('theme-light','theme-dark');
    root.classList.add('theme-'+t);
    btn.textContent = t==='dark' ? '☀ Light' : '🌙 Dark';
  }}
  var saved=localStorage.getItem(KEY);
  if(!saved){{ saved='light'; }}  // default light (also best for print)
  apply(saved);
  btn.addEventListener('click',function(){{
    var t=root.classList.contains('theme-dark')?'light':'dark';
    localStorage.setItem(KEY,t); apply(t);
  }});

  // click-to-zoom lightbox
  var lb=document.getElementById('lightbox'), lbBody=document.getElementById('lbBody'),
      lbTitle=document.getElementById('lbTitle'), lbBadge=document.getElementById('lbBadge');
  function open(el){{
    var title=el.getAttribute('data-title')||'';
    var parts=title.split(' · ');
    if(parts.length===2){{ lbBadge.textContent=parts[0]; lbBadge.style.display=''; lbTitle.textContent=parts[1]; }}
    else {{ lbBadge.style.display='none'; lbTitle.textContent=title; }}
    lbBody.innerHTML=el.innerHTML;            // clone the inline SVG
    lb.classList.add('open');
  }}
  function close(){{ lb.classList.remove('open'); lbBody.innerHTML=''; }}
  document.querySelectorAll('.kbd').forEach(function(el){{
    el.addEventListener('click',function(){{ open(el); }});
    el.addEventListener('keydown',function(e){{
      if(e.key==='Enter'||e.key===' '){{ e.preventDefault(); open(el); }}
    }});
  }});
  document.getElementById('lbClose').addEventListener('click',close);
  lb.addEventListener('click',function(e){{ if(e.target===lb) close(); }});
  document.addEventListener('keydown',function(e){{ if(e.key==='Escape') close(); }});
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
