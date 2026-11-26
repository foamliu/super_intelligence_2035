# =============================================================================
# Makefile : cfreq_ctrl  Design Compiler (DC) 综合流程顶层入口
# -----------------------------------------------------------------------------
# 用法:
#   make          # 默认跑完整综合流程 (等价 make syn)
#   make syn      # 调用 dc_shell 执行综合
#   make clean    # 清理综合产物 (netlist / reports / logs)
#   make help     # 打印帮助
# =============================================================================

SHELL        := /bin/bash

# ---- 工具可执行 ----
DC_SHELL     ?= dc_shell
DC_OPTS      ?= -64bit

# ---- 项目路径 (导出为绝对路径, 供 dc_setup_filenames.tcl / dc.tcl 使用) ----
export SYN_ROOT      := $(abspath .)
export SETUP_DIR     := $(SYN_ROOT)/setup
export SCRIPTS_DIR   := $(SYN_ROOT)/scripts
export SDC_DIR       := $(SYN_ROOT)/sdc
export DATA_DIR      := $(SYN_ROOT)/data
export RTL_FILELIST  := $(DATA_DIR)/syn_filelist.f
export NETLIST_DIR   := $(SYN_ROOT)/netlist
export REPORTS_DIR   := $(SYN_ROOT)/reports
export LOG_DIR       := $(SYN_ROOT)/logs

# ---- 设计属性 ----
export DESIGN_NAME   ?= cfreq_ctrl
export TOP           ?= cfreq_ctrl

# ---- 主综合脚本 ----
DC_TCL         := $(SCRIPTS_DIR)/dc.tcl

.PHONY: all syn clean help

all: syn

syn:
	@echo "=============================================================="
	@echo " cfreq_ctrl : Design Compiler synthesis flow"
	@echo " TOP       = $(TOP)"
	@echo " SYN_ROOT  = $(SYN_ROOT)"
	@echo "=============================================================="
	@mkdir -p $(NETLIST_DIR) $(REPORTS_DIR) $(LOG_DIR)
	$(DC_SHELL) $(DC_OPTS) -f $(DC_TCL) 2>&1 | tee $(LOG_DIR)/dc_syn.log

clean:
	@echo "==> Cleaning synthesis outputs ..."
	rm -rf $(NETLIST_DIR) $(REPORTS_DIR) $(LOG_DIR)
	rm -f command.log filenames.log view_command.log *.ddc

help:
	@echo "cfreq_ctrl synthesis flow:"
	@echo "  make        run full synthesis (default)"
	@echo "  make syn    run dc_shell synthesis"
	@echo "  make clean  remove generated outputs"