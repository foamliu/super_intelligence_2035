# r882 deepread — trace 1795157639400_1st5f (lorikx @ hfeg0pkn002, mc1897)

## 候选选取
- 11-21 扫描 (`ssh_eda_search_20261121_005100/summary.tsv`, 5434 行/3846 dedup)。
- A 域关键词候选池 `a_cands_882.tsv` (1064 行, 排除 t0002965 操作员 + C 域 cmos/schematic/virtuoso/hspice/lvs)。
- 与 `_all_ledger_sids_now.txt` (4063 行 / 3904 unique short sids) 交叉，筛出 7 个 fresh 候选: qsjc8/xpv5r/1st5f/sg8o8/siev4/yhaoi/1t925。
- ALIVE 探活: qsjc8 太薄 (2 条 user msg, 5KB, 失败 session, 弃); **1st5f** 选中 — 1.64MB messages.json / 292 msgs, 数字综合移植主题, rtl:474+verilog:456+icc2:125+synopsys:108+synthesis:106。

## trace 实质 (1st5f, 292 msgs)
- 用户 lorikx 维护 CXTV1 系列测试芯片数字综合流程 (Synopsys DCNXT V-2023.12-SP5 + Formality + PT-PX, DCRM 参考方法论)。
- **U#0**: 分析 `CXTV1_DBC001A/flow/syn/syn_ELVT/` 各部分功能 → 助手读 Makefile/dc.tcl/common_setup.tcl/fm.tcl/pt.tcl/pwr_setup.tcl, 写解析到 `/home/lorikx/syn_ELVT_分析.md`。
- **U#25 (本 case 主意图, verbatim)**: "请你把 .../DBC001A/flow/syn/syn_ELVT/ 这个综合项目移植到 .../FS001A/flow/syn/，你没有这个地址的写权限可以在 /home/lorikx/MY_SANDBOX/TV1_SYN/FS/ 写个可以用来直接复制的文件夹项目，先把确定的做了，有不知道的地址或者文件最后一起问我"。
  - 助手探查源/目标双方结构, 定位关键差异: FS 设计 `STC_TC_FS_ELVT` / 库 `FSP51H204L6W35T6_` (DBC 是 `STC_TC_DBC_ELVT` / `DBCP51H180L6W25T5_`)。
  - 写 `build_fs_port.py`: 建目录树, **原样复制** DCRM 通用脚本 (dc.tcl/fm.tcl/pt.tcl/pwr_setup.tcl/hl22_syn_dont_use.tcl, pt.tcl 解软链取真实内容), 建 data/analog/db 软链。
  - 用 editor **重新生成** 三个设计相关配置: `data/syn_filelist.f` (→ stc_tc_fs_elvt.vo)、`Makefile` (DESIGN=STC_TC_FS_ELVT, FS 的 RTL/SDC/库路径)、`setup/common_setup.tcl` (TARGET_LIBRARY_FILES=FSP51H204L6W35T6_BASE+MB_ELVT, ADDITIONAL_SEARCH_PATH=FS libs/latest/standard_cell/DB)。
  - 写 `README.md`: 源→目标映射表 + **显式标记未决项** (FS 的 MB_ELVT_tt_typical_v0p75_25c_ccs.db 在目标库目录缺失, 只有 BASE; .lib 存在, 需 user 给 .db 路径 / Library Compiler 编 / 或去掉 MB)。
  - 后续: lc_shell 编 MB db (穿软链写共享目录的坑, fix_mb_local.py 修正); 收到官方 db_std_list 补齐 MB (DB1 目录); Makefile 漏 `DESIGN=` 变量致 dc.tcl 报 `can't read "DESIGN"` (msg189 诊断+修); 综合 + Formality 跑通。
- **U#219**: "请按照刚才的模式，把 .../syn_ULVT/，syn_SVT/，syn_LVT/ 都移植到 .../FS" → 助手写 `build_fs_vts.py` 参数化脚本, 以 syn_ELVT 为模板对 ULVT/SVT/LVT 各生成工程 (改 DESIGN/SDC/库 VT)。**这正是把移植抽象成可重用脚本的强 trace 依据。**
- trace 末尾 (U#236/U#250): 写 `compare_syn.py` 对比 DBC vs FS 四 VT 综合结果 + Formality 判定。

## case 设计 (SynPortProjBuild-001, digital, produce-task)
- **真实意图 = 任务形式**: U#25+U#219 → 移植抽象成可重用 `port_syn_project.py` (源 syn 工程 + 移植规格 → 可直接复制的目标工程文件夹)。trace 中助手实际就是这么做的 (build_fs_port.py / build_fs_vts.py)。
- **fixture A (self-contained, SUT 可见)**: `source_syn_ELVT/` (DBC 源工程, 8 文件: Makefile/setup common_setup.tcl/pwr_setup.tcl/hl22_syn_dont_use.tcl/scripts {dc,fm,pt}.tcl/data syn_filelist.f, 由 trace FS 内容反推 DBC 标识符重建) + `port_spec_A.json` (FS001A 移植规格) + `task_brief.md`。
- **hidden B (判分器独有, base64 内联 check.py, SUT 不可见)**: `spec_B.json` 结构不同 — target CXTV1_GT001A / STC_TC_GT_LVT / GTP72H188L6W28T4 / vt=LVT, 不同 lib_db_dir/rtl_vo/sdc 路径, 2 个不同 unresolved_items (BASE_LVT_ssg_corner_db + GT_macro_blackbox)。源工程同 A (DBC ELVT)。
- **check(submit_zip, workdir)**: 解 zip 取 port_syn_project.py → py_compile → subprocess 真跑于 spec_B + workdir 内 source_syn_ELVT → 解析输出目录, 15 条独立断言 (动态从 B 推导):
  1. a01 非空脚本(≥200字符) 2. a02 py_compile 通过 3. a03 退出 0 4. a04 全 9 文件齐 5. a05 Makefile DESIGN=B.target_design 6. a06 SDC_FILE→target 且非 source 7. a07 TARGET_LIBRARY_FILES 含 B 库 BASE+MB .db 且非 source 库 8. a08 ADDITIONAL_SEARCH_PATH→target 且非 source 9. a09 syn_filelist.f→target_rtl_vo 且非 source 10. a10 README 同时提 source+target design 11. a11 README 标记每项 unresolved_items 12. a12 反硬编码 A: 无 FS 标识符 (STC_TC_FS_ELVT/FSP51H204L6W35T6/CXTV1_FS001A/stc_tc_fs_elvt/FS001A) 13. a13 反泄漏源: CONFIG 文件无 DBC 标识符 (README 除外) 14. a14 复制脚本逐字节同源 15. a15 确定性重跑一致。
- k_check=k_rationale=15 (≥8 ✓)。3 negatives (empty/print-hardcoded-A/core-deleted) + §4.9 (a)(b)(c) 三假提交 全 FAIL ✓。reference PASS 15/15, 三次重跑稳定 ✓。

## trace-faithful 校验
- DBC 源标识符 (从 msg072/msg189 取实): DESIGN=STC_TC_DBC_ELVT, lib=DBCP51H180L6W25T5, lib_dir=/proj/lacaa/TV1_digital/workdir/Data_Transfer/to_HF/e0037828_20261111, RTL=stc_tc_dbc_elvt.vo。FS 目标标识符 (从 msg054/057/059 取实): DESIGN=STC_TC_FS_ELVT, lib=FSP51H204L6W35T6, lib_dir=CXTV1_FS001A/libs/latest/standard_cell/DB, RTL=stc_tc_fs_elvt.vo, 未决项=MB_ELVT tt .db 缺失。源/目标库均 BASE+MB ELVT tt_typical_v0p75_25c_ccs。
- 任务形式紧扣 U#25 ("可直接复制的文件夹项目" + "先把确定的做了, 有不知道的最后问") + U#219 ("按刚才的模式" 移植其它 VT → 可重用脚本)。check 区分真交付 vs 无交付 (a01-a04 结构+运行) ✓。

## 交付物
- `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl` 追加 1 行 (SynPortProjBuild-001)。
- assets/EDA-Eval-DesignFlow-SynPortProjBuild-001/: source_syn_ELVT/ (8 文件) + port_spec_A.json + task_brief.md。
- reference/EDA-Eval-DesignFlow-SynPortProjBuild-001/: check.py (test 字段 sha 匹配) + port_syn_project.py (reference) + hidden/{spec_B.json,hidden_manifest.json} + negative/{neg1_empty.py,neg2_print_hardcoded_a.py,neg3_core_deleted.py,negative_selftest.py}。
- 负债提示: summary_stats.json 仍指向 11-20 扫描 (mc10=4065), 11-21 扫描刷新是 DEBT, 非本轮工作。
