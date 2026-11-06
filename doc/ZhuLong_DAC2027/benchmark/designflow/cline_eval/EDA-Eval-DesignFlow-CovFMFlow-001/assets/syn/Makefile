
#==============================================================
# CFREQ_CTRL Design Compiler 综合流程
# 参考: lagat_flow_ref/syn/Makefile (lagat FEINT 流程)
#
# 用法 (在 syn/ 目录下):
#   make dc_syn                # 集群: LSF 提交 dcnxt_shell (module 环境)
#   make dc_syn USE_LSF=0      # 本地: 直接调用 dcnxt_shell
#   make clean / distclean
#
# 产出 (flow_cfreq_ctrl/):
#   results/cfreq_ctrl.mapped.{v,ddc,sdc}   results/syn.done
#   reports/cfreq_ctrl.{timing,area,qor,...}.rpt
#   logs/dc.log
#
# 后续流程 (lagat 中央 FEINT 仓库提供):
#   Formality 一致性检查 (fm_shell) / PrimeTime 功耗时序 (pt_shell)
#==============================================================

SCRIPT_REPO  = /apps/imctf/cad/script/digital_flow/feint
ROOT_DIR     = $(shell pwd)
SCRIPT_DIR   = $(ROOT_DIR)/scripts
WORK_DIR     = $(ROOT_DIR)/flow_$(DESIGN)

#---------Project Config---------
DESIGN       = cfreq_ctrl
RTL_FILELIST = $(ROOT_DIR)/data/syn_filelist.f
SDC_FILE     = $(ROOT_DIR)/sdc/$(DESIGN).sdc
LINK_LIB_PATH  = $(ROOT_DIR)/data/lib
PROJECT_HOME = $(ROOT_DIR)/../
# 报告/产物批次标签 (corner 名), 参考ref工程 cur_date 机制
TAG          ?= Au22

SYN_DONE     = $(WORK_DIR)/results/syn.done

#---------Tool Config---------
USE_LSF       ?= 1
LSF_QUEUE     ?= fqueue2h
# 集群 module 环境 (与 lagat 主流程一致)
MODULE_SYN    ?= ds/dc/2023.12-SP5
# 本地直跑二进制: 优先取 PATH, 否则用 SRB 的 V-2023.12-SP5
DCNXT_BIN     ?= $(shell command -v dcnxt_shell 2>/dev/null || echo /apps/synopsys/SRB/designcompiler/V-2023.12-SP5/bin/dcnxt_shell)
# Verdi (网表浏览); 标准单元 Verilog 模型 PDK 当前未提供, cell 显示为
# 黑盒; 若拿到模型文件, make verdi CELL_MODELS="a.v b.v" 即可展开 schematic
VERDI        ?= $(shell command -v verdi 2>/dev/null || echo /apps/synopsys/SRB/verdi_2023.12-SP2-3/bin/verdi)
CELL_MODELS  ?=

# dc.tcl 变量透传 (与 lagat Makefile 接口一致)
DC_XARGS = set DESIGN $(DESIGN); set cur_date $(TAG); \
           set RTL_FILELIST $(RTL_FILELIST); \
           set ROOT_DIR $(ROOT_DIR); set SDC $(SDC_FILE); \
           set LINK_LIB_PATH $(LINK_LIB_PATH); set PROJECT_HOME $(PROJECT_HOME)

# 从 filelist 提取 RTL 源文件绝对路径, 作为 syn.done 依赖:
# 修改 rtl_synth/*.v 后直接 make dc_syn 即可自动重新综合。
# 过滤指令行 (+incdir/+define/-F/-f/-v/-y) 与 // 注释行。
# 注: 全部用 make 原生函数实现, 避免转义问题; file <file 需 make 4.2+,
#     若 make 过旧导致取不到文件, 依赖退化为仅 filelist 时间戳。
RTL_FILES = $(addprefix $(dir $(RTL_FILELIST)), \
            $(filter-out +incdir% +define% -F% -f% -v% -y% //%, \
              $(strip $(file <$(RTL_FILELIST)))))

ifeq ($(USE_LSF),1)
  define RUN
	bsub -Is \
		-q $(LSF_QUEUE) \
		"module purge && module load $(MODULE_SYN) && \
		 cd $(WORK_DIR) && \
		 dcnxt_shell -f $(SCRIPT_DIR)/dc.tcl -x '$(DC_XARGS)' \
		 | tee logs/dc.log && \
		 touch $(SYN_DONE)"
  endef
else
  define RUN
	bash -c "set -o pipefail; cd $(WORK_DIR) && \
		 $(DCNXT_BIN) -f $(SCRIPT_DIR)/dc.tcl -x '$(DC_XARGS)' \
		 2>&1 | tee logs/dc.log && \
		 touch $(SYN_DONE)"
  endef
endif

.PHONY: all dc_syn verdi clean distclean

all: dc_syn

$(WORK_DIR):
	@mkdir -p $(WORK_DIR)/logs $(WORK_DIR)/reports $(WORK_DIR)/results

dc_syn: $(SYN_DONE)

$(SYN_DONE): $(RTL_FILELIST) $(SDC_FILE) $(SCRIPT_DIR)/dc.tcl $(SCRIPT_DIR)/dc_setup.tcl $(SCRIPT_DIR)/dc_setup_filenames.tcl $(RTL_FILES) | $(WORK_DIR)
	@echo ">> Running DC synthesis for $(DESIGN) (USE_LSF=$(USE_LSF))..."
	$(call RUN, $(DESIGN)_syn)
	@echo ">> DC synthesis done: $(SYN_DONE)"

# 用 Verdi 打开综合网表 (black-box 模式, 无需工艺库 Verilog 模型)
verdi: | $(WORK_DIR)
	@if [ ! -f $(WORK_DIR)/results/$(DESIGN).mapped.v ]; then \
		echo "[ERR] $(WORK_DIR)/results/$(DESIGN).mapped.v 不存在, 先跑: make dc_syn"; \
		exit 1; \
	fi
	@echo "results/$(DESIGN).mapped.v" > $(WORK_DIR)/verdi_netlist.f
	@if [ -n "$(CELL_MODELS)" ]; then for m in $(CELL_MODELS); do echo $$m >> $(WORK_DIR)/verdi_netlist.f; done; fi
	cd $(WORK_DIR) && $(VERDI) -f verdi_netlist.f &
	@echo ">> Verdi 已打开网表: $(WORK_DIR)/results/$(DESIGN).mapped.v"
	@echo "   (无标准单元模型时 cell 显示为黑盒; 拿到模型后:"
	@echo "    make verdi CELL_MODELS='<cell_model.v>')"

# 查看关键报告
report: | $(WORK_DIR)
	@grep -E "Resource Area|Total cell area|Combinational" $(WORK_DIR)/reports/$(DESIGN)_$(TAG).mapped.area.rpt 2>/dev/null || true
	@head -40 $(WORK_DIR)/reports/$(DESIGN)_$(TAG).mapped.qor.rpt 2>/dev/null || echo "no qor report"

clean:
	rm -rf $(WORK_DIR)/results $(WORK_DIR)/reports $(WORK_DIR)/logs \
	       $(WORK_DIR)/*.db $(WORK_DIR)/command.log $(WORK_DIR)/WORK

distclean: clean
	rm -rf $(WORK_DIR)
=====END=====
