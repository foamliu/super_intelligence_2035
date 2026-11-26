# q11i6 深读笔记 — STA flow scaffolding (A档 faithful)

## trace
- session: `1793618961003_q11i6.messages.json` (e0046913@hfeg0pkn003, mc=874, 178 msgs, ~850KB)
- domain: digital (post-synth STA flow construction)
- fresh 11/02-11/03 session, daily eda_trace_2026110{2,3}.log 命中

## A档②判定
- user#0 逐字：「/proj/lacaa/TV1_digital/simdir/yutingq/CXDP/cla_top/lint 仔细阅读该目录下的文件层次和结构，以cla_top的lint flow为参考，为我构建一个相同文件层次结构的sta flow。（sta flow的脚本参考来源为/proj/lacaa/TV1_digital/simdir/yutingq/feint）」
- = clean 提需求（构建 STA flow 文件层次，参考 lint + feint 脚本），未给根因/修复 → **A档②合格 → A档 faithful**

## 助手真实工具链
- list_allowed_files / read_files 读 lint flow 目录结构 + feint PT 脚本
- writableRoots 仅 /home/e0046913 → 在 /home/e0046913/cla_top_sta/ 镜像构建（非真实 cla_top/sta/）
- editor 逐文件写：README.md, run/{CXDP_STA_CFG, sta_setup.tcl, sta.tcl, Makefile}, data/{cla_top.netlist.f, cla_top.sdc, sta_override.tcl}, script/sta_qa_chk.pl, install.sh
- _mk_sta_staging.py 创建 symlink (CXDP_DESIGN_CFG/CXDP_PROJ_CFG -> ../../config/...) + all_out 子目录
- 验证：make -n help parse OK / perl -c sta_qa_chk.pl OK / tcl brace balance OK / 真实 config 链接后 make -n 读出 Design=cla_top

## 金标准（用户接受）
- 用户未拒绝，要求中文版（engaged）+ 精简步骤（engaged）；末尾清理 home 时**显式保留 cla_top_sta/ 交付物**（msg#177）
- gold tree = /home/e0046913/cla_top_sta/ (已 scp 到 .75 workdir gold_sta_A.tgz, 11KB/900 行)
  - all_out/v1.0_Latest/{filelist,log,out_src,QA,report}/
  - data/{cla_top.netlist.f, cla_top.sdc, sta_override.tcl}
  - run/{CXDP_STA_CFG(117L), sta.tcl(137L), sta_setup.tcl(124L), Makefile(179L), CXDP_DESIGN_CFG+CXDP_PROJ_CFG symlinks}
  - script/sta_qa_chk.pl(88L), README.md(123L), install.sh(46L)

## verb = `sta-flow-scaffold`
- 与所有已有 shard-A verb 互斥（AprSetupAudit/AprLogAudit/AprStampFix=审计/修复 APR；VcsEquiv/VCSMakefile=验证；FlatNet=网表扁平；CalibrePdf2md/ItfCompare=文档/ITF；DcUpfDiag=DC 诊断；LibToParm=lib 抽取；PortCatch=端口连通性）→ 本 case=**构建新 STA flow 目录树**，unique

## case 设计（A档 faithful + 自包含 bundle 便于 cross-input guard B）
- **交付**: submit.zip{build_sta_flow.py} — 通用 STA flow 构建器，CLI `--lint <lint_dir> --feint <feint_dir> --out <out_dir>`，读 lint flow 结构 + feint PT 脚本 → 镜像产 STA flow 树
- **A 可见 bundle**（合成忠实 minimal）：lint_flow_A/（config/{CXDP_DESIGN_CFG:CXDP_DESIGN_NAME=cla_top, CXDP_PROJ_CFG}, run/{CXDP_LINT_CFG, lint.tcl, Makefile, symlinks}, data/cla_top.awl, script/lint_qa_chk.pl, all_out/v1.0_Latest/...）+ feint_ref_A/（setup/common_setup.tcl, scripts/pt.tcl, Makefile）
- **B 隐藏 bundle**（异构 cross-input guard 击破硬编 A）：lint_flow_B（design=uart_top, tag=v2.1_Latest, corner=ss0p72vm40c, **额外 mcmm/ 子目录**）+ feint_ref_B（common_setup.tcl PBA=exhaustive ≠ A 的 gba）
- **判分纯 stdlib python3**（无 PT/VCS license 依赖，本地 PASS==判分环境等价）：subprocess 真跑 `perl -c`/`tclsh info complete`/`make -n help`/`bash -n` 验证生成的脚本可解析
- check.py ~20 条 a-t 独立断言（zip+py_compile/候选跑 B exit0+产 outB/outB 结构 5 子目录/run 6 文件+symlinks/data 3 文件/script/perl -c/tclsh info complete sta.tcl+sta_setup.tcl/make -n help/PT 命令集/Makefile target+pt_shell+LSF/CXDP_STA_CFG 变量/README+install.sh+bash -n/跨输入守卫 design name A≠B/跨输入守卫 mcmm 仅 B/跨输入守卫 PBA A=gbv B=exhaustive/跨输入守卫 tag A=v1.0 B=v2.1）
- 5 negatives: fake_empty/fake_print_expected/naive_hardcode_a/fake_structure_only/fake_scripts_only + §4.9 三假

## 进度
- 轮 49 已 claim q11i6 → 本轮（50）合成 StaFlowScaffold-001
