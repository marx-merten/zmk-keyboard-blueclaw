doc: doc/keymap.svg doc/keymap_combos.svg

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
	rm -rf build firmware doc/keymap.yaml doc/keymap.svg doc/keymap_combos.svg

FORCE: