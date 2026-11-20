交付接口：outputs/submit.zip 解压后须含下列文件结构（验收只读此结构，不实跑工具）：

syn/（Design Compiler 综合流程）：
  Makefile, SourceMe, README.md, setup/common_setup.tcl,
  scripts/{dc.tcl, dc_setup.tcl, dc_setup_filenames.tcl},
  sdc/cfreq_ctrl.sdc, data/syn_filelist.f
lint/（VC Static 静态检查项目）：
  work/{Makefile, design_rtl.list, cfreq_ctrl.prj},
  config/{cdc_sdc/cdc.sdc, rdc_sdc/rdc.sdc}

目标 RTL：assets/rtl_synth/cfreq_ctrl.v。综合/lint 顶层=cfreq_ctrl。
各文件须为可用的工程脚本（Makefile/Tcl/SDC/prj），内容自洽；判分器静态校验脚本结构与跨输入泛型，不会启动 dc_shell/spyglass。
