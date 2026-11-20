#############################################################################
# Makefile -- Innovus floorplan + routing driver via LSF bsub (stamp-fixed)
#############################################################################
SHELL := /bin/bash
.PHONY: all fp route clean

TOP      ?= hl22_porting_test_chip_v1
WORK_DIR ?= .
LOG_DIR  ?= logs
BSUB     ?= bsub

# Tcl stamp files (stamp-priority: checked before the log-grep fallback)
TSTAMP1 := $(CURDIR)/.inv_fp_$(TOP).stamp
TSTAMP2 := $(CURDIR)/.inv_pr_$(TOP).stamp

INV_FP_STAMP := $(TSTAMP1)
INV_PR_STAMP := $(TSTAMP2)
export INV_FP_STAMP INV_PR_STAMP

all: fp route

fp: $(TSTAMP1)
$(TSTAMP1): innovus_fp.tcl
	@rm -f $(TSTAMP1) $(TSTAMP1).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_fp.log "innovus -files innovus_fp.tcl"
	@for i in {1..60}; do touch .nfsprobe; rm -f .nfsprobe; if [ -f $(TSTAMP1) ]; then touch $@; exit 0; fi; if [ -f $(TSTAMP1).fail ]; then break; fi; if grep -q "INNOVUS FP DONE" $(LOG_DIR)/inv_fp.log 2>/dev/null; then touch $(TSTAMP1); exit 0; fi; if grep -q "INNOVUS FP FAILED" $(LOG_DIR)/inv_fp.log 2>/dev/null; then break; fi; sleep 2; done; echo "FAILED"; exit 1

route:
	@rm -f $(TSTAMP2) $(TSTAMP2).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_route.log "innovus -files innovus_pr.tcl"
	@for i in {1..60}; do touch .nfsprobe; rm -f .nfsprobe; if [ -f $(TSTAMP2) ]; then exit 0; fi; if [ -f $(TSTAMP2).fail ]; then break; fi; if grep -q "INNOVUS PR DONE" $(LOG_DIR)/inv_route.log 2>/dev/null; then touch $(TSTAMP2); exit 0; fi; if grep -q "INNOVUS PR FAILED" $(LOG_DIR)/inv_route.log 2>/dev/null; then break; fi; sleep 2; done; echo "FAILED"; exit 1

clean:
	@rm -f $(TSTAMP1) $(TSTAMP1).fail $(TSTAMP2) $(TSTAMP2).fail