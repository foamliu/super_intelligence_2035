# =============================================================================
# Makefile : cfreq_ctrl  VC Static (SpyGlass) lint / CDC / RDC 静态检查流程
# -----------------------------------------------------------------------------
# 用法:
#   make          # 跑全套 (lint + cdc + rdc)
#   make lint     # lint/lint_rtl
#   make cdc      # cdc/cdc_verify
#   make rdc      # rdc/rdc_verify
#   make clean    # 清理检查结果与项目 work 目录
# =============================================================================

SHELL        := /bin/bash

# ---- 工具 ----
SPYGLASS     ?= vc_static

# ---- 路径 ----
LINT_ROOT    := $(abspath .)
PROJ_FILE    := $(LINT_ROOT)/cfreq_ctrl.prj
CONFIG_DIR   := $(LINT_ROOT)/../config
RTL_LIST     := $(LINT_ROOT)/design_rtl.list
WORK_DIR     := $(LINT_ROOT)/results

export DESIGN_NAME ?= cfreq_ctrl
export TOP         ?= cfreq_ctrl

# ---- 默认 goals ----
GOALS        ?= lint/lint_rtl cdc/cdc_verify rdc/rdc_verify

.PHONY: all lint cdc rdc clean help

all: lint cdc rdc

lint:
	$(SPYGLASS) -project $(PROJ_FILE) -goal lint/lint_rtl

cdc:
	$(SPYGLASS) -project $(PROJ_FILE) -goal cdc/cdc_verify

rdc:
	$(SPYGLASS) -project $(PROJ_FILE) -goal rdc/rdc_verify

clean:
	rm -rf $(WORK_DIR)
	rm -f spyglass.log synchrony.log *.log

help:
	@echo "cfreq_ctrl lint flow:"
	@echo "  make        run lint + cdc + rdc (default)"
	@echo "  make lint   run lint/lint_rtl"
	@echo "  make cdc    run cdc/cdc_verify"
	@echo "  make rdc    run rdc/rdc_verify"
	@echo "  make clean  remove results"