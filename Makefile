
LAYERS := Base symbols numbers     Nav     sys     f-keys    layers game    BIOS



doc: doc/layouts/keymap.png doc/layouts/keymap_combos.png $(LAYERS:%=doc/layouts/km_layer_%.png)

doc/layouts/%.png: doc/%.svg
	@mkdir -p doc/layouts
	convert -background lightgray -flatten $< $@

doc/keymap.svg: doc/keymap.yaml keymapper.conf config/blueclaw.json
	uvx --from keymap-drawer keymap -c keymapper.conf draw -j config/blueclaw.json --keys-only doc/keymap.yaml >doc/keymap.svg

doc/keymap_combos.svg: doc/keymap.yaml keymapper.conf config/blueclaw.json
	uvx --from keymap-drawer keymap -c keymapper.conf draw  --select-layers Base  -j config/blueclaw.json  doc/keymap.yaml >doc/keymap_combos.svg

doc/keymap.yaml: config/blueclaw.keymap keymapper.conf
	uvx --from keymap-drawer keymap -c keymapper.conf parse -z config/blueclaw.keymap  >doc/keymap.yaml

cheatsheet: doc/cheatsheet.html
doc/cheatsheet.html: doc/keymap.yaml keymapper.conf config/blueclaw.json scripts/build_cheatsheet.py
	uv run --with pyyaml python3 scripts/build_cheatsheet.py

rebuild: clean doc firmware

firmware: FORCE
	uvx --from git+ssh://git@github.com/marx-merten/zmk-buildenv zmkbuild build-docker  --module  .

clean: FORCE
	rm -rf build firmware doc/*

FORCE:
PerLayer: $(LAYERS:%=doc/km_layer_%.svg)


$(LAYERS:%=doc/km_layer_%.svg): doc/keymap.yaml keymapper.conf config/blueclaw.json
#	name := $()
	@echo "target: $(@:doc/km_layer_%.png=%)"
# uvx --from keymap-drawer keymap -c keymapper.conf draw -j config/blueclaw.json --keys-only --select-layers $(@:doc/km_layer_%.png=%) doc/keymap.yaml >$@
	uvx --from keymap-drawer keymap -c keymapper.conf draw  --select-layers  $(@:doc/km_layer_%.svg=%)   -j config/blueclaw.json --keys-only  doc/keymap.yaml  >$@
