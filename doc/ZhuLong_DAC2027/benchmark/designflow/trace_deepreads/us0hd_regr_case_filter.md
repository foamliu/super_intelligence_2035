# trace_deepread: 1792066483816_us0hd (e0039102@hfeg0pkn002, mc=166)

- **domain**: schematic_netlist (netlist:23, pyAether:5, schematic:1; verilog:2918/.def:24/aether:20/analog:16)
- **真实任务**: LPDDR5/DDR5 回归驱动脚本(Perl caselist)按 bus 配置挑选 case、保留可运行格式、写新文件不覆盖原文件
- **trace 规模**: 1.2MB messages.json, 294 msgs, 144 assistant, 11 非空 user
- **关键 user 轮**:
  - U#0 (msg[0]): 原 run_normal_allconfig_noprobe_xrun_jack_UVS 下挑 case，分组列出 x8/x8_hibyte/x8_hibyte_mrconfig/x8_mrconfig/x16/x16_hibyte_mrconfig 各自要保留的 case，"保留现在能运行的格式，写一个新文件，不要覆盖原文件"
  - U#2 (msg[99]): /regr-case-filter skill 触发，对 /proj/drgsa/.../run_uvs 再做一次类似挑选
  - U#4 (msg[190]): 怀疑 ddgoa 项目生成时没理解要求，让 agent 检查项目
  - U#6 (msg[222]): 质疑 run_uvs 只有几个 case 而 selected 很多(发现 agent 误把别的目录 case 混入)
- **assistant 工具链**: editor(50) + run_approved_command/python-runner(49) + read_files(23) + list_allowed_files(10) + search_codebase(1)
- **关键产物**: run_normal_allconfig_noprobe_xrun_jack_UVS_selected(9664 bytes, 34 case)，原文件 90847 bytes 未改
- **驱动文件格式**:
  - shebang `#!/usr/bin/perl` + `system("sleep 5");`
  - 分区注释: `###-----------------for x16-------------#`(x16 无 -b) / `########---------- x8---------------------------###` / `########---------- x8 hibyte---------------------------###` / `########---------- x8 hibyte mrconfig ---------------------------###` / `########---------- x8 mrconfig ---------------------------###` / `########---------- x16 hibyte mrconfig ---------------------------###`
  - case 行: `system("./vsim_uvs -sr <case> [-b "<bus>"] -d \"LPDDR5G ...\" --noprobe -q bcp_LP1 --ncconfig \"+ncnowarn+...\" -l \"log...\" &"); system("sleep 5");`；禁用行前缀 `#`
  - 同名 case 跨分区出现(auto/basiccheck/mrr/zqcal 等)，必须按 (section, sr) 匹配而非按名字
- **挑选清单格式**: `<bus下划线> : <case1>; <case2>; ...`，每行一组，bus 用 `x8_hibyte` 写法需归一化为 `x8 hibyte`
- **资产权限**: /rundata/ddgoa、/proj/drgsa 均 e0039102 私有，e0031982 无读权限(DEBT④)→B-grade synthesized
- **本 case**: EDA-Eval-DesignFlow-RegrCaseFilter-001 (schematic_netlist B-grade L2 k=15)
