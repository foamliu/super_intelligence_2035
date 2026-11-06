#==============================================================
# CFREQ_CTRL VCS 代码覆盖率检查流程
# 参考: lagat_flow_ref/syn/Makefile (lagat FEINT 流程结构), 工具换成 VCS + URG
#
# 用法 (在 cov/ 目录下):
#   make cov                      # VCS 编译 + 仿真 + URG 覆盖率报告 (默认)
#   make cov METRICS="line+cond+tgl+fsm+branch"
#   make cov USE_LSF=0            # 本地直跑 (不走 LSF)
#   make report / clean / distclean
#
# 产出 (flow_cfreq_ctrl/):
#   vdb/simv.vdb/                  (VCS coverage database)
#   reports/cfreq_ctrl.urgReport/  (URG HTML/文本报告)
#   logs/{vcs_compile,vcs_sim,urg}.log
#==============================================================

ROOT_DIR     = $(shell pwd)
SCRIPT_DIR   = $(ROOT_DIR)/scripts
WORK_DIR     = $(ROOT_DIR)/flow_$(DESIGN)

#---------Project Config---------
DESIGN       = cfreq_ctrl
RTL_FILELIST = $(ROOT_DIR)/data/syn_filelist.f
TB           = $(ROOT_DIR)/data/tb_$(DESIGN).sv
COV_METRICS ?= line+cond+tgl+fsm+branch
TAG         ?= Au22

#---------Tool Config---------
USE_LSF    ?= 0
LSF_QUEUE  ?= fqueue2h
MODULE_COV ?= vcs/vcs_mx/2023.12-SP2

# cov.tcl 变量透传 (argv)
COV_ARGS = -design $(DESIGN) -rtl $(RTL_FILELIST) -tb $(TB) -metrics $(COV_METRICS) -workdir $(WORK_DIR) -tag $(TAG)

COV_DONE = $(WORK_DIR)/cov.done

ifeq ($(USE_LSF),1)
  RUN_CMD = bsub -Is -q $(LSF_QUEUE) "module purge && module load $(MODULE_COV) && tclsh $(SCRIPT_DIR)/cov.tcl $(COV_ARGS) | tee logs/cov.log && touch $@"
else
  RUN_CMD = bash -c "set -o pipefail; tclsh $(SCRIPT_DIR)/cov.tcl $(COV_ARGS) 2>&1 | tee logs/cov.log && touch $@"
endif

.PHONY: all cov report clean distclean

all: cov

$(WORK_DIR):
	@mkdir -p $(WORK_DIR)/logs $(WORK_DIR)/reports $(WORK_DIR)/vdb

cov: $(COV_DONE)

$(COV_DONE): $(RTL_FILELIST) $(TB) $(SCRIPT_DIR)/cov.tcl $(ROOT_DIR)/setup/common_setup.tcl | $(WORK_DIR)
	@echo ">> Running VCS coverage for $(DESIGN) (metrics=$(COV_METRICS))..."
	$(RUN_CMD)
	@echo ">> Coverage done: $@"

report: | $(WORK_DIR)
	@ls -d $(WORK_DIR)/reports/*.urgReport 2>/dev/null || echo "no coverage report; run: make cov"

clean:
	rm -rf $(WORK_DIR)/vdb $(WORK_DIR)/reports $(WORK_DIR)/logs \
	       $(WORK_DIR)/csrc $(WORK_DIR)/simv* $(WORK_DIR)/*.vdb $(WORK_DIR)/*.log \
	       $(WORK_DIR)/*.vcd

distclean: clean
	rm -rf $(WORK_DIR)