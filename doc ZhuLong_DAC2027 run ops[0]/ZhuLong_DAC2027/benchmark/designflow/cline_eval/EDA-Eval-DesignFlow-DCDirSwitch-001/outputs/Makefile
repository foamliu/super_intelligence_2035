# Top-level Makefile (project root).
#
# Targets:
#   make scan      scan ./synth/results and switch the flow to the newest
#                  dc_* result directory found there.
#   make replace   switch the flow to the DC_RESULT_DIR defined below
#                  (override it on the command line, for example:
#                     make replace DC_RESULT_DIR=synth/results/dc_XXXX)
#
# The tool that actually performs the switch lives in ../tools/.

TOOLS_DIR ?= ../tools
PYTHON    ?= python3
SCRIPT    := $(abspath $(TOOLS_DIR)/set_dc_result_dir.py)

# DC result directory used by `make replace`.
DC_RESULT_DIR ?= synth/results/dc_2026-10-29-19.16.52

.PHONY: scan replace

scan:
	@$(PYTHON) $(SCRIPT) "$$(ls -1d synth/results/dc_* 2>/dev/null | sort -r | head -n 1)" --project .

replace:
	@$(PYTHON) $(SCRIPT) "$(DC_RESULT_DIR)" --project .