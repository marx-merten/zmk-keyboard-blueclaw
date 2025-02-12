
LAYERS := default Symbols Num     Nav     sys     func    locking game    cfg



doc: doc/keymap.svg doc/keymap_combos.svg $(LAYERS:%=doc/km_layer_%.svg) doc/layouts/keymap.png doc/layouts/keymap_combos.png $(LAYERS:%=doc/layouts/km_layer_%.png)

doc/keymap.svg: doc/keymap.yaml keymapper.conf config/blueclaw.json
	keymap -c keymapper.conf draw -j config/blueclaw.json --keys-only doc/keymap.yaml >doc/keymap.svg

doc/keymap_combos.svg: doc/keymap.yaml keymapper.conf config/blueclaw.json
	keymap -c keymapper.conf draw  --select-layers default  -j config/blueclaw.json  doc/keymap.yaml >doc/keymap_combos.svg

doc/keymap.yaml: config/blueclaw.keymap keymapper.conf
	keymap -c keymapper.conf parse -z config/blueclaw.keymap  >doc/keymap.yaml

rebuild: clean doc firmware

firmware: FORCE
	zmkbuild build-docker  --module  .

clean: FORCE
	rm -rf build firmware doc/*

FORCE:
PerLayer: $(LAYERS:%=doc/km_layer_%.svg)


$(LAYERS:%=doc/km_layer_%.svg): doc/keymap.yaml keymapper.conf config/blueclaw.json
#	name := $()
	@echo "target: $(@:doc/km_layer_%.png=%)"
# keymap -c keymapper.conf draw -j config/blueclaw.json --keys-only --select-layers $(@:doc/km_layer_%.png=%) doc/keymap.yaml >$@
	keymap -c keymapper.conf draw  --select-layers  $(@:doc/km_layer_%.svg=%)   -j config/blueclaw.json --keys-only  doc/keymap.yaml  >$@
	
png: doc/layouts/keymap.png doc/layouts/keymap_combos.png $(LAYERS:%=doc/layouts/km_layer_%.png)
	
doc/layouts/%.png: doc/%.svg
	mkdir -p doc/layouts
	inkscape --export-filename=$@ --export-background=#D3D3D3 $<
