# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal ZMK firmware configuration for the **Blueclaw** wireless split keyboard. There is essentially **no application code** — the "source" is a devicetree keymap (`config/blueclaw.keymap`) compiled against upstream ZMK into a flashable UF2 firmware image. The shield definition lives under `config/boards/shields/blueclaw/`.

## How the build works

- **`config/west.yml`** — west manifest pointing at `zmkfirmware/zmk` (revision `v0.3`).
- **`make firmware`** / **`make rebuild`** shell out to the external `zmk-buildenv` tool (`git+ssh://git@github.com/marx-merten/zmk-buildenv`), which wraps a Docker build with this repo as a ZMK module.
- **`make clean`** removes `build/`, `firmware/`, and `doc/*`.

`build/` (Zephyr/CMake artifacts) and `firmware/` (`*.uf2` outputs) are gitignored — don't edit them by hand. There are no unit tests; validate keymap changes by a successful build.

## Keymap structure (`config/blueclaw.keymap`)

This is the only file you'll normally edit. It's a ZMK devicetree keymap. Key things to know:

- **Layers (order matters — referenced by index):**
  `0 Base`, `1 symbols`, `2 numbers`, `3 Nav`, `4 sys`, `5 f-keys`, `6 layers`, `7 game`, `8 mouse`, `9 extra2`, `10 extra3`, `11 extra4`, `12 BIOS`.
  Bindings reference these numerically (`&mo 5`, `&lt 3 ENTER`, `&to 7`, `&tog 1`, …), so **renaming or reordering layers requires updating every numeric reference**. `extra2`/`extra3`/`extra4` are empty placeholders.
- **Home-row mods:** `hml` / `hmr` (left/right hold-tap behaviors, `balanced`, 280 ms term, 175 ms quick-tap, 150 ms prior-idle) implement home-row modifiers on `A R S T` / `N E I O`, with `hold-trigger-key-positions` allowlists. If you change the physical layout or move home-row keys, those position lists must be recomputed.
- **Behaviors:** mod-morphs `tldesc` (Esc/~), `lbr` (`[`/`(`), `rbr` (`]`/`)`), `btquote` (`'`/`` ` ``), `dotcom` (`.`/`,`); the `intelligent_shift` tap-dance (Shift / Caps Word on double-tap).
- **Combos:** `Space+Backspace` → `mouse` layer, `Space+sys` → `BIOS` layer, `L+U` → Esc.
- **Layout reference:** `config/blueclaw.json` defines the physical key positions and is the source of truth for key-position numbering, consumed by keymap-drawer.

## Secrets injection

Secret macros are kept out of the repo and injected at build time via a C-preprocessor indirection: `config/blueclaw.keymap` ends with `INJECT_SECRETS()`; `config/secrets.dtsi` (committed) defines it as a no-op then `#include`s `config/private_secrets.dtsi` if present; `private_secrets.dtsi` is **gitignored**. Never commit real secrets.

## Documentation / keymap diagrams

`make doc` regenerates SVG/PNG keymap visualizations into `doc/` and `doc/layouts/` using [`keymap-drawer`](https://github.com/caksoylar/keymap-drawer) (run via `uvx`, so `uv` must be installed) plus ImageMagick `convert` for PNG rasterization. The pipeline: parse `config/blueclaw.keymap` → `doc/keymap.yaml` → per-layer SVGs styled by `keymapper.conf` and positioned by `config/blueclaw.json`.

`make cheatsheet` builds a single self-contained, designed HTML guide at `doc/cheatsheet.html` via `scripts/build_cheatsheet.py` (run through `uv run --with pyyaml`). The script loads `doc/keymap.yaml`, **categorises every key** (letters / home-row mod / layer / number / symbol / nav / media / fn / system / macro / special) into a CSS `type` class, re-renders each layer through keymap-drawer with those classes, and inlines the SVGs into an HTML page with Catppuccin **Latte** (light, default) + **Macchiato** (dark) themes, a theme toggle, click-to-zoom lightbox, hand-written explainer sections (home-row mods, combos, thumb/layer-access map, mod-morphs/tap-dances), and a print stylesheet. Both `doc/cheatsheet.html` and all `make doc` output are gitignored generated artifacts; the generator and `keymapper.conf` are the tracked source. Editing key colours/categories happens in `scripts/build_cheatsheet.py` (categoriser + Catppuccin palettes), not in the keymap.
