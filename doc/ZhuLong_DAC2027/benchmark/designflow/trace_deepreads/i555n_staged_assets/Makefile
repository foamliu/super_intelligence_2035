SCRIPT_REPO  = /apps/imctf/cad/script/digital_flow/feint
ROOT_DIR     = $(shell pwd)
SCRIPT_DIR   = $(ROOT_DIR)/scripts
WORK_DIR     = $(ROOT_DIR)/flow_$(DESIGN)


#---------Project Config---------
DESIGN         = sync_level2level
RTL_FILELIST   = $(ROOT_DIR)/data/syn_filelist.f
SDC_FILE       = $(ROOT_DIR)/data/$(DESIGN).sdc
PT_CORNER      = tt0p8v25c
PT_CORNERS     = tt0p8v25c ss0p72vm40c
#RTL_FILES     = $(shell sed '/^\s*#/d; /^\s*$/d' $(RTL_FILELIST) )


#---------FM Config---------
ifneq ($(filter fm_g2g,$(MAKECMDGOALS)),)
    FM_MODE := gate2gate
else ifneq ($(filter fm_r2r,$(MAKECMDGOALS)),)
    FM_MODE := rtl2rtl
else
    FM_MODE ?= rtl2gate
endif

FM_REF_NETLIST ?= ""
FM_IMP_NETLIST ?= ""
FM_IMP_RTL_FILELIST ?= ""

SYN_DONE     = $(WORK_DIR)/results/syn.done
FM_DONE      = $(WORK_DIR)/results/fm_$(FM_MODE).done

#FM_DONE      = $(WORK_DIR)/results/fm.done
#PA_DONE      = $(WORK_DIR)/results/pa.done

USE_LSF       ?= 1
LSF_QUEUE     ?= fqueue2h

MODULE_SYN    ?= ds/dc/2023.12-SP5
MODULE_FM     ?= ds/fm/2023.12-SP5
MODULE_PA     ?= ds/pt/2022.12-SP5
MODULE_LC     ?= ds/lc/2023.12-SP4


ifeq ($(USE_LSF),1)
  define RUN
	bsub -Is \
		-q $(LSF_QUEUE) \
		"$(2)"
  endef
else
  define RUN
	eval "$(2)"
  endef
endif

.PHONY: all build_feint_flow dc_syn fm_r2g fm_g2g fm_r2r sta-pa pa_sweep clean distclean

all: build_feint_flow dc_syn fm_r2g sta-pa

build_feint_flow: $(SCRIPT_DIR) $(WORK_DIR)
	@echo ">> Flow environment ready."

$(SCRIPT_DIR):
	@echo ">> Getting FEINT flow scripts from $(SCRIPT_REPO)..."
	cp -r $(SCRIPT_REPO)/scripts $(ROOT_DIR)
	cp -r $(SCRIPT_REPO)/setup   $(ROOT_DIR)


$(WORK_DIR):
	@mkdir -p $(WORK_DIR)/logs $(WORK_DIR)/reports $(WORK_DIR)/results $(ROOT_DIR)/data


dc_syn: $(SYN_DONE)

$(SYN_DONE): $(RTL_FILELIST) $(SDC_FILE) $(SCRIPT_DIR)/dc.tcl | $(WORK_DIR)
	@echo ">> Submitting DC synthesis..."
	$(call RUN, $(DESIGN)_syn, \
		module purge && \
		module load $(MODULE_SYN) && \
		cd $(WORK_DIR) && \
		dcnxt_shell -f $(SCRIPT_DIR)/dc.tcl \
			-x 'set DESIGN $(DESIGN); set RTL_FILELIST $(RTL_FILELIST); set SDC $(SDC_FILE); set ROOT_DIR $(ROOT_DIR)' \
			| tee logs/dc.log && \
		touch $(SYN_DONE) \
	)


dg_syn:
	@echo ">> Submitting DC topographical synthesis..."
	$(call RUN, $(DESIGN)_syn, \
		module purge && \
		module load $(MODULE_SYN) && \
		cd $(WORK_DIR) && \
		dcnxt_shell -topo -f $(SCRIPT_DIR)/dc.tcl \
			-x 'set DESIGN $(DESIGN); set RTL_FILELIST $(RTL_FILELIST); set SDC $(SDC_FILE); set ROOT_DIR $(ROOT_DIR)' \
			| tee logs/dc.log \
	)



fm_r2g fm_g2g: $(FM_DONE)

ifneq ($(FM_MODE),rtl2rtl)
$(FM_DONE): $(SYN_DONE) $(SCRIPT_DIR)/fm.tcl
	@echo ">> Submitting Formality (mode: $(FM_MODE))..."
	$(call RUN, $(DESIGN)_fm_$(FM_MODE), \
		module purge && \
		module load $(MODULE_FM) && \
		cd $(WORK_DIR) && \
		fm_shell -f $(SCRIPT_DIR)/fm.tcl \
			-x 'set DESIGN $(DESIGN); set RTL_FILELIST $(RTL_FILELIST); set ROOT_DIR $(ROOT_DIR); set FM_MODE $(FM_MODE); set FM_REF_NETLIST $(FM_REF_NETLIST); set FM_IMPL_NETLIST $(FM_IMPL_NETLIST)' \
			| tee logs/fm_$(FM_MODE).log && \
		touch $(FM_DONE) \
	)
endif

FM_R2R_DONE = $(WORK_DIR)/results/fm_rtl2rtl.done

fm_r2r: $(FM_R2R_DONE)
$(FM_R2R_DONE): $(SCRIPT_DIR)/fm.tcl | $(WORK_DIR)
	@echo ">> Submitting Formality (mode: rtl2rtl)..."
	$(call RUN, $(DESIGN)_fm_rtl2rtl, \
		module purge && \
		module load $(MODULE_FM) && \
		cd $(WORK_DIR) && \
		fm_shell -f $(SCRIPT_DIR)/fm.tcl \
			-x 'set DESIGN $(DESIGN); set RTL_FILELIST $(RTL_FILELIST); set ROOT_DIR $(ROOT_DIR); set FM_MODE rtl2rtl; set FM_IMPL_RTL_FILELIST $(FM_IMPL_RTL_FILELIST)' \
			| tee logs/fm_rtl2rtl.log && \
		touch $(FM_R2R_DONE) \
	)

sta-pa: $(SYN_DONE) $(SCRIPT_DIR)/pt.tcl
	@echo ">> Submitting PTPX (corner: $(PT_CORNER))..."
	$(call RUN, $(DESIGN)_pa_$(PT_CORNER), \
		module purge && \
		module load $(MODULE_PA) && \
		module load $(MODULE_LC) && \
		cd $(WORK_DIR) && \
		pt_shell -f $(SCRIPT_DIR)/pt.tcl \
			-x 'set DESIGN $(DESIGN); set ROOT_DIR $(ROOT_DIR); set PT_CORNER $(PT_CORNER)' \
			| tee logs/pa_$(PT_CORNER).log \
	)

pa_sweep:
	@if ! command -v xterm >/dev/null 2>&1; then \
		echo "ERROR: xterm not found. Run manually: make pa PT_CORNER=<corner>"; \
		exit 1; \
	fi
	@if [ -z "$$DISPLAY" ]; then \
		echo "ERROR: DISPLAY not set. Enable X11 forwarding or run manually."; \
		exit 1; \
	fi
	@for corner in $(PT_CORNERS); do \
		echo ">> Launching PA in xterm (corner: $$corner)..."; \
		xterm -hold -T "PA $(DESIGN) $$corner" \
			-e "$(MAKE) sta-pa PT_CORNER=$$corner" & \
		sleep 1; \
	done
	@echo ">> All PA jobs launched in xterm windows."
