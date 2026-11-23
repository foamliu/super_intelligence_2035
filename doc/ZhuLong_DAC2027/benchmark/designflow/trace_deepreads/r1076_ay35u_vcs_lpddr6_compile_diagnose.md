# r1076 deepread — ay35u (e13zhang@hfeg0pkn004) — VCS LPDDR6 Denali VIP compile-error diagnose produce-task

## trace 来源
- scan: `ssh_eda_search_20261123_064315/summary.tsv` (.75, 2026-11-23)
- session: `1792113124796_ay35u.messages.json` (197KB / 39 msgs / 8 user Q&A turns)
- host: 10.129.2.13 = hfeg0pkn004 ; user: e13zhang ; mc=13 (verilog:29 + systemverilog:7 + rtl:1 主导 A-pure verification；cadence:17 为 VIP 工具目录，非 layout)
- 归因: A=37 (verilog+systemverilog+rtl) vs C=0 (无 aether/virtuoso/layout/gds/drc/lvs) vs B/D=0 (无 spice/netlist/schematic) → 强 A-pure verification
- ledger 状态: fresh (4-shard ledger diff；r1076 核查 cases/A 已有 qm8x2/46vx0/gw1z7 三 case 未 ledgered，ay35u 无 case 无 ledger → 真正 fresh)
- scp 路径陷阱: 文件在子目录 `/home/e13zhang/.cline/data/sessions/1792113124796_ay35u/1792113124796_ay35u.messages.json` (非直接 sessions/<sid>.messages.json)

## 用户原话（8 Q&A 轮，逐字关键句）
- U#0: "分析上游 tc_driver.sv 的驱动行为，并与 Denali 示例对比"
- U#2: "我如果写了 +incdir+${DENALI}/ddvapi/sv 还需要把这个目录的文件一个一个给添加进 filelist 吗"
- U#4: "+incdir+ 可以让 import 找到 package 吗"
- U#6: 贴 filelist（含 denaliMem.sv / denaliLpddr6.sv / cdnLpddr6UvmTop.sv / lpddr6_interface.sv / SomaUvm/lpddr6.sv 等）"我看我的 filelist 这么写 确实把 +incdir+${DENALI}/ddvapi/sv 下面的文件都 Parsing design file 添加进来了"
- U#8: 贴 cdnVipTop.sv "package CdnSvVip; import CdnSvVip 也没有报错"
- U#12: "我都没有增加过 cdnVipTop.sv 到 filelist 里面，只写了 +incdir+ 发现一样可以 import"
- U#14: "denali_64bit/bin/ 下面都是什么文件 有什么用"
- U#18: 贴 `Error-[DBG_UCLI_DEP] Option -ucli/-gui is deprecated ...`
- U#20: 贴 `Error-[ITSFM] Illegal `timescale for module .../d_line_model.sv, 7 ...`
- U#22: 贴链接错误 `uvm_dpi.o: In function 'm_uvm_report_dpi': undefined reference to 'm__uvm_report_dpi' ... [COMPILE-FAIL] base_fun failed!`
- U#24/U#26: 贴 cdn_vip_setup_example 脚本 & CDN_VIP_* 环境变量，问 CommandSc0 显示

## trace 调查结论（assistant，3 个核心 VCS 编译错误）
1. **DBG_UCLI_DEP** (deprecated 选项): VCS 2023.12 起 `./simv -ucli -i inp_viprun.vcs` 单独跑被废弃，只能编译时配 `-R`/`-debug*`。修：删运行命令里的 `-ucli -i inp_viprun.vcs`，让 UVM 测试自己 drop objection / `$finish`，或加 `#(timeout); $finish;` 兜底。
2. **ITSFM** (Illegal timescale): `d_line_model.sv:7` 有 `` `timescale `` 但同编译单元前面的 module/package 没有 → 不一致。修：vcs 命令行加全局 `-timescale=1ns/1fs`；或给报错文件及它前面那个无 timescale 的文件顶部都补 `` `timescale ``（同精度）。
3. **LINKER undefined reference to m__uvm_report_dpi**: UVM SV 侧 `m_uvm_report_dpi` 与 C++ `uvm_dpi.o` 不匹配（UVM 版本/home 不一致或陈旧 csrc）。修：`rm -rf csrc simv simv.daidir` 后重编；确认 `-uvm` 还在、没混自定义 UVM 源/UVM 宏。

## 造题转化 (11-15 令 debug-Q&A → produce-task)
用户把 VCS 编译日志里的错误逐条贴出来问"为什么 + 怎么修"。提炼为通用 produce-task：
`diagnose_vcs_errors.py <compile_log> <output_json>` — 解析 VCS 编译日志，抽取每条 `Error-[CODE]` 块 + 链接器 `undefined reference to <sym>` 错误 → 结构化 JSON（每条含 index/category/error_code/raw_header/file/line/symbol/root_cause/fix_steps），并按错误码知识表分类。另交付 `vcs_compile_diagnosis.md` 中文诊断文档（机制解释，覆盖 timescale 编译单元一致性 / `+incdir+` vs `import` vs package 编译 / UVM DPI SV↔C++ 链接）。

## 关键牙点（anti-hardcode）
- **A (visible)**: `compile_log_A.log` = trace-faithful VCS LPDDR6 VIP 编译日志，含 3 条真实错误（DBG_UCLI_DEP / ITSFM file=d_line_model.sv:7 / LINKER undefined ref sym=m__uvm_report_dpi）。错误原文逐字来自 trace user paste。
- **hidden B**: `compile_log_B.log` = 合成的另一 VCS 编译日志，3 条**不同**错误：
  - `Error-[LCA_FEATURE_NOT_ENABLED]` (license 类，feature=VCS_API_Suite)
  - `Error-[UID]` (undefined identifier 类，sym=p_aess_config_t file=top_cfg.sv:42)
  - 链接器 `undefined reference to sv_get_scope` (sym≠A 的 m__uvm_report_dpi)
- A/B 的 error_code、symbol、file 全不相交 → 硬编码 A 的解在 B 上必 FAIL（B output 不含 A-only code/sym，且 B 的 code/sym 必须被结构性抽取）。
- solver 必须真解析日志文本（正则 + 知识表），不能硬编码 A 答案。

## check.py (k=16)
① zip 解压干净 ② 含 .py + .md ③ py_compile 通过 ④ B 运行 exit0 ⑤ B JSON 顶层 keys {tool,total_errors,errors} ⑥ total_errors==3 ⑦ 每条 error 含 8 必填 key ⑧ B error_codes 含 LCA_FEATURE_NOT_ENABLED 与 UID（A 缺的 2 码，测泛化）⑨ B 链接错误 symbol==sv_get_scope ⑩ B output 不含 A-only token (DBG_UCLI_DEP / m__uvm_report_dpi / d_line_model.sv) ⑪ 每条 root_cause 非空(>10 字) + fix_steps 非空 list ⑫ md >200B 且含 ≥4 机制词(timescale/incdir/import/package/linker/DPI/undefined/deprecated) ⑬ 确定性 3x md5 一致 ⑭ §4.9 空壳(size>200+def+import) ⑮ §4.9 print-only-A(B code 缺/sym 错) ⑯ §4.9 core-deleted(errors=[]→total≠3)

## negatives (§4.9 三假)
- neg_empty.py: 仅注释空壳 → ④/⑤/⑥ FAIL
- neg_print_only_A.py: 硬编码 A 的 3 条 JSON 输出无视输入 → ⑧(B 缺 LCA/UID)/⑨(sym=m__uvm_report_dpi≠sv_get_scope)/⑩(含 A-only token) FAIL
- neg_core_deleted.py: 脚手架在但 errors=[] → ⑥(total≠3) FAIL

## 自测
- ref solve_ref.py 在 A/B 下均正确分类 → ref PASS 16/16
- `python3 negative_selftest.py` → ref PASS + 3 negs FAIL = ALL GOOD
- §4.9 三假全 FAIL ✓ ; 确定性 3x md5 ✓

## 交付物
- assets/EDA-Eval-DesignFlow-VcsCompileErrorDiagnoseProduce-001/: compile_log_A.log, task_brief.md
- reference/EDA-Eval-DesignFlow-VcsCompileErrorDiagnoseProduce-001/: solve_ref.py, check.py, hidden/(compile_log_B.log), negative/{neg_empty,neg_print_only_A,neg_core_deleted}.py, negative_selftest.py
- cases/A/EDA-Eval-DesignFlow-VcsCompileErrorDiagnoseProduce-001.json (运维令 2026-11-23: 写 cases/ 不碰 jsonl)
- ledger: ay35u claimed → case

## 选料注
r1075 MEMORY 标记 "ay35u 197KB verilog/SV 需评估" → r1076 兑现。ay35u 是 e13zhang 新 session，与既有 case 无 intent-dup（VCS LPDDR6 VIP 编译错误诊断 vs MsieWaveDump/RedBist/VlogFindLibSubdepParse 均不同意图）。域判: verification（VCS/SystemVerilog/UVM 编译主体）。同时发现并修复 3 处 ledger sync gap（qm8x2/46vx0/gw1z7 case 已存在但未 mark case）。
