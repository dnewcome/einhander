# einhander — regenerate CAD, PCB, fab bundle, and 3D model.
# `make help` lists targets.  Tools: build123d, bun/tscircuit, KiCad 9,
# Freerouting v2.2.4 + JDK 25 (routing), Blender 5 (GLB preview).

BLENDER ?= /opt/blender-5.0.1-linux-x64/blender
BUN     := $(HOME)/.bun/bin
PATHX   := PATH="$(BUN):$$PATH"
BOARD   := index.circuit.kicad_pcb
SRC     := index.circuit.tsx
NAME    := einhander

.PHONY: help all cad glb render fab route clean
.DEFAULT_GOAL := help

help:  ## list targets
	@grep -hE '^[a-z].*:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort | awk -F'\t' '{printf "  \033[36m%-10s\033[0m %s\n",$$1,$$2}'

all: cad glb render fab  ## regenerate everything derivable (CAD, GLB, preview, fab bundle)

cad:  ## enclosure STLs + renders (build123d)
	cd cad && python3 machine.py

glb:  ## PCBA 3D model (GLB) from tscircuit (parts + keyswitch models)
	cd pcb && $(PATHX) npx tsci export $(SRC) -f glb -o renders/$(NAME)-pcba.glb

render: glb  ## Blender preview PNG of the PCBA GLB
	cd pcb && LC_ALL=C $(BLENDER) -b -noaudio --python scripts/render_glb.py

fab:  ## Gerbers + drill + CPL + BOM(s) for JLCPCB & PCBWay (-> pcb/fab/)
	cd pcb && $(PATHX) bash scripts/make_fab.sh $(BOARD) $(NAME) both

route:  ## re-route the 4-layer PCB (auto-route baseline; hand-finish the tail via scripts/, see pcb-layout skill)
	cd pcb && $(PATHX) DISPLAY=$${DISPLAY:-:0} bash scripts/route4.sh

clean:  ## remove regenerable intermediates (keeps committed renders/fab/board)
	rm -rf pcb/dist pcb/build cad/build
