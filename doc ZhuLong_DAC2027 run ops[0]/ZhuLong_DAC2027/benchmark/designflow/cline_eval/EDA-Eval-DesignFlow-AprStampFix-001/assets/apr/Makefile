#############################################################################
# Makefile -- Innovus floorplan + routing driver via LSF bsub
#   BUGGY (qiqs7): 30s grep-only retry loop (no stamp check, no NFS refresh)
#############################################################################
SHELL := /bin/bash
.PHONY: all fp route clean

TOP      ?= hl22_porting_test_chip_v1
WORK_DIR ?= .
LOG_DIR  ?= logs
BSUB     ?= bsub

S1 := $(CURDIR)/.inv_fp_$(TOP).stamp

all: fp route

fp: $(S1)
$(S1): innovus_fp.tcl
	@rm -f $(S1)
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_fp.log "innovus -files innovus_fp.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
	  if grep -q "INNOVUS FP DONE" $(LOG_DIR)/inv_fp.log 2>/dev/null; then touch $@; exit 0; fi; \
	  if grep -q "INNOVUS FP FAILED" $(LOG_DIR)/inv_fp.log 2>/dev/null; then break; fi; \
	  sleep 2; \
	done; \
	echo "FAILED"; exit 1

route:
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_route.log "innovus -files innovus_pr.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
	  if grep -q "INNOVUS PR DONE" $(LOG_DIR)/inv_route.log 2>/dev/null; then exit 0; fi; \
	  if grep -q "INNOVUS PR FAILED" $(LOG_DIR)/inv_route.log 2>/dev/null; then break; fi; \
	  sleep 2; \
	done; \
	echo "FAILED"; exit 1

clean:
	@rm -f $(S1)
