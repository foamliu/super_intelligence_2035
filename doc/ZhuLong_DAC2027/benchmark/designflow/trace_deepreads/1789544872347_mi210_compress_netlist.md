# trace deepread — 1789544872347_mi210 (zjqiao @ hfhds206, mc=119)

- **session**: `/home/zjqiao/.cline/data/sessions/1789544872347_mi210/1789544872347_mi210.messages.json` (86 msgs, 53 user turns)
- **workdir**: netlist → compress netlist 转换（Run_Compress_Netlist shell 流程 + SKILL compressNetlist.il）
- **keyword summary**: netlist/Run_Compress_Netlist/Netlist=/sed/switch_close→switch_open/vcap/Spf/TSV module Netlist/compressNetlist.il
- **domain**: schematic_netlist（D 域 ✓）

## 用户意图流（关键 user text 轮）
1. **U#48 (msg 32, 需求轮 — 用作 A 档任务说明)**：「注意，我不是要将最新的netlist进行转换，而是希望用户在调用skill时可以指定netlist，然后你去将相应的参数改为用户指定的netlist，然后运行脚本进行转换」——澄清：要把「指定 netlist 名 → 改 shell 参数 → 运行转换」参数化进 skill，而非每次手改最新 netlist。
2. 其余 user 轮：多为「转换这个/那个 netlist」「跑一下」等执行指令，agent 在 Run_Compress_Netlist shell 模板上手改 active `Netlist=` 行 + 按 `#vcap`/`#Spf`/`#TSV module Netlist` header 切换 sed 块注释态，再生成 SKILL `compressNetlist.il`。
3. U#48 是唯一「提需求/定接口」轮（A-faithful ✓）；其余为执行/根因轮，不可用作 A。

## 工具链（真实产物）
- **Run_Compress_Netlist shell 模板**：顶部多段 `#Netlist='...'` 选择行（mode 注释 + 值，恰好 1 行未注释=active）；中部 `cp -rf -L ${Netlist} ${Netlist}_Compress` + `chmod 775`；下部按 header `#vcap`/`#Spf`/`#TSV module Netlist` 分块的 `sed -i "s;...switch_close;...switch_open;g"` 行（按 mode 注释/未注释切换）。
- **compressNetlist.il**（SKILL）：`procedure (RunCompressNetlist userInput @optional (mode nil))`，暴露用户指定 netlist 名 + 可选 mode。
- 真实模板从 msg 84 editor new_text 逐块重建（磁盘最终态）。

## 真实数值（trace 中验证）
- A 模板 netlist 名：`Netlist_Vcap_20240811PM_2STACK_TSV` / `Netlist_Vcap_20240802PM_V1` / `Netlist_SpfBA_20250613_REVC_PowerFill` / `Netlist_Vcap_20260915PM_Fullchip`；active=Fullchip → TSV module Netlist sed 块未注释。
- sed 实例模式：`XI2_11 inh_vss YioN7<15>` / `XI0_11 inh_vcc Yio7<15>`（switch_close→open）。

## case 抽取
- **case_id**: EDA-Eval-DesignFlow-CompressNetlist-001（shard D / schematic_netlist / A 档 faithful / L1-boundary）
- 可移植化抽象：真实 Virtuoso/SPF shell 流程降级为确定性 Python 生成器 `gen_compress_netlist.py`：读 config.json → `fuzzy_match`(user_input → Netlist_* 全名) → `infer_mode`(2STACK→TSV_Vcap / POWERFILL→Norm_Spf / FULLCHIP→TSV_Spf / TSV+VCAP→TSV_Vcap / TSV+SPF→TSV_Spf / VCAP→Norm_Vcap / SPF→Norm_Spf) → `rewrite_shell`(改 active `Netlist=` 行 + 按 header 切换 sed 块注释态) → `write_skill_il`(emit RunCompressNetlist userInput)。
- **A**（真实派生）：Run_Compress_Netlist_A.sh（2024 netlist 名，active=Fullchip，TSV module Netlist 块未注释，sed XI2_11/XI0_11）+ netlists_A.txt + config_A.json(user_input=Netlist_Vcap_20240811PM)。
- **隐藏 B**（不同结构/值，跨输入护栏）：Run_Compress_Netlist_B.sh（2025 netlist 名，**默认 active=V2→vcap 块未注释**非目标 TSV module Netlist，迫使生成器切换；sed XI3_22/XI1_10 inh_vdd/gnd）+ netlists_B.txt + config_B.json(user_input=Netlist_SpfBA_20251015 → fuzzy 匹配 Netlist_SpfBA_20251015PM_Fullchip → mode TSV_Spf)。B_TOKENS 排除被替换的 active 名(Netlist_Vcap_20251201PM_V2)，用持久 PowerFill 名避免误判。
- check.py **14 条件 a-n**：a zip含gen b py_compile c 跑B退0出out_shell+out_il d 恰1未注释Netlist= e active==B全名 f TSV module Netlist块未注释vcap/Spf全注释 g 非active全注释active全未注释 h cp -rf -L与chmod未注释 i active含user_input子串 j Fullchip→TSV_Spf→out_il标TSV_Spf k out_il含RunCompressNetlist+userInput+名+mode l A token不泄漏+B token齐 m 3seed sha256一致 n 非退化active≠A名且sed有切换。
- check.py `_find_b` 多路径搜索（FT_HIDDEN_DIR / workdir / _HERE→../assets/<id>/hidden/B/）适配 repo layout。
- 自验：ref PASS 14/14；4 negatives ALL-FAIL{empty→c / print_fixed_A→e / core_deleted→f / naive_no_toggle→f}；NEG_SELFTEST ALL-FAIL OK；§4.9 三假(c/e/f) distinct ✓；test==disk roundtrip EXACT；k_rationale==k_check==14 ✓；D.jsonl 70→71 行。
- 教训：(1) 默认 active sed 块≠目标模式块 是防 naive copy 的关键护栏（B 模板 active=vcap 但目标=TSV module Netlist，naive/core_deleted 不切换→f）；(2) B_TOKENS 须排除被替换的 active 名用持久 token；(3) shell sed 块 header 解析(#vcap/#Spf/#TSV module Netlist)是模式切换的核心抽象。
