#==============================================================
# CFREQ_CTRL Formality 形式验证流程 (等价性检查)
# 参考: lagat_flow_ref/syn/Makefile (lagat FEINT 流程), feint/scripts/fm.tcl
#
# 用法 (在 fm/ 目录下):
#   make fm_r2g                  # RTL vs 综合网表 (Synopsys auto setup, 推荐)
#   make fm_g2g                  # 参考网表 vs 实现网表 (gate-to-gate)
#   make fm_r2g USE_LSF=0        # 本地直跑 fm_shell (不走 LSF)
#   make report / clean / distclean
#
# 产出 (flow_cfreq_ctrl/):
#   results/cfreq_ctrl_match/  cfreq_ctrl_verify/  (Formality session)
#   reports/cfreq_ctrl.fmv_{unmatched_points,failing_points,...}.rpt
#   logs/fm_{fm_r2g,fm_g2g}.log
#
# 前置: 综合网表来自 syn/ 流程 (results/cfreq_ctrl.mapped.v + .svf),
#       请将其复制到 data/netlist/ 或通过 FM_IMPL_NETLIST 指定绝对路径。
#==============================================================

SCRIPT_REPO  = /apps/imctf/cad/script/digital_flow/feint
ROOT_DIR     = $(shell pwd)
SCRIPT_DIR   = $(ROOT_DIR)/scripts
WORK_DIR     = $(ROOT_DIR)/flow_$(DESIGN)

#---------Project Config---------
DESIGN            = cfreq_ctrl
RTL_FILELIST      = $(ROOT_DIR)/data/syn_filelist.f
FM_REF_NETLIST    = $(ROOT_DIR)/data/netlist/$(DESIGN).mapped.v
FM_IMPL_NETLIST   = $(ROOT_DIR)/data/netlist/$(DESIGN).mapped.v
SVF_FILE          = $(ROOT_DIR)/data/$(DESIGN).svf
PROJECT_HOME      = $(ROOT_DIR)/../
TAG              ?= Au22

#---------Tool Config---------
USE_LSF    ?= 1
LSF_QUEUE  ?= fqueue2h
MODULE_FM  ?= ds/fm/2023.12-SP5
FM_BIN     ?= $(shell command -v fm_shell 2>/dev/null || echo /apps/synopsys/SRB/formality/V-2023.12-SP5/bin/fm_shell)

# fm.tcl 变量透传 (与 lagat Makefile -x 接口一致)
FM_XARGS = set DESIGN $(DESIGN); set cur_date $(TAG); \
           set RTL_FILELIST $(RTL_FILELIST); \
           set ROOT_DIR $(ROOT_DIR); set FM_MODE $(FM_MODE); \
           set FM_REF_NETLIST $(FM_REF_NETLIST); \
           set FM_IMPL_NETLIST $(FM_IMPL_NETLIST); \
           set SVF_FILE $(SVF_FILE); set PROJECT_HOME $(PROJECT_HOME)

# 从 filelist 提取 RTL 源文件作为参考设计依赖 (syn 流程同款实现)
RTL_FILES = $(addprefix $(dir $(RTL_FILELIST)), \
            $(filter-out +incdir% +define% -F% -f% -v% -y% //%, \
              $(strip $(file <$(RTL_FILELIST)))))

FM_R2G_DONE = $(WORK_DIR)/results/fm_r2g.done
FM_G2G_DONE = $(WORK_DIR)/results/fm_g2g.done

ifeq ($(USE_LSF),1)
  RUN_CMD = bsub -Is -q $(LSF_QUEUE) "module purge && module load $(MODULE_FM) && cd $(WORK_DIR) && fm_shell -f $(SCRIPT_DIR)/fm.tcl -x '$(FM_XARGS)' | tee logs/fm_$(FM_MODE).log && touch $@"
else
  RUN_CMD = bash -c "set -o pipefail; cd $(WORK_DIR) && $(FM_BIN) -f $(SCRIPT_DIR)/fm.tcl -x '$(FM_XARGS)' 2>&1 | tee logs/fm_$(FM_MODE).log && touch $@"
endif

.PHONY: all fm_r2g fm_g2g report clean distclean

all: fm_r2g

$(WORK_DIR):
	@mkdir -p $(WORK_DIR)/logs $(WORK_DIR)/reports $(WORK_DIR)/results

fm_r2g: $(FM_R2G_DONE)
fm_g2g: $(FM_G2G_DONE)

$(FM_R2G_DONE): FM_MODE := rtl2gate
$(FM_G2G_DONE): FM_MODE := gate2gate

$(FM_R2G_DONE) $(FM_G2G_DONE): $(RTL_FILELIST) $(FM_REF_NETLIST) $(FM_IMPL_NETLIST) $(SCRIPT_DIR)/fm.tcl $(ROOT_DIR)/setup/common_setup.tcl $(RTL_FILES) | $(WORK_DIR)
	@echo ">> Running Formality ($(FM_MODE)) for $(DESIGN) (USE_LSF=$(USE_LSF))..."
	$(RUN_CMD)
	@echo ">> Formality ($(FM_MODE)) done: $@"

report: | $(WORK_DIR)
	@grep -E "Verification (SUCCEEDED|FAILED|INCONCLUSIVE)|Failing Points" $(WORK_DIR)/reports/*.rpt 2>/dev/null || echo "no fmv report"

clean:
	rm -rf $(WORK_DIR)/results $(WORK_DIR)/reports $(WORK_DIR)/logs \
	       $(WORK_DIR)/*.db $(WORK_DIR)/command.log $(WORK_DIR)/WORK

distclean: clean
	rm -rf $(WORK_DIR)