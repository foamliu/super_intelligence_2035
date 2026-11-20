# Deepread — sid 1789614314714_ctu99 · rongjiez @ hfeg0pkn005 · characterization (MPQA model QA)

**trace**: 40 msgs / 260KB · spice_c=15 (finesim model QA) · source: eda_trace_20261107.log (11-07 00:01 daily cron), NOT-in-ledger scout batch 11-07 04:1x

## USER 轮（逐字）
- **USER#0 (msg 0, A-档 任务轮)**: `@runModelQA_new.pl 我的代码中our $shrink 是从getSSD($cfg);中解析cdg文件获取的，现在输入cfg文件不会包含cfg，你去要去$model文件中的 .lib tt .lib 'incFile_G5_CIP' mos_tt 中的同级目录下的'incFile_G5_CIP' 文件，去查找SHRINK = 来获取具体的数据，注意我'incFile_G5_CIP有几十万行，有没有快速的方法，用grep可以吗，其次SHRINK和=直接可能有一个空格或者多个空格，可能会有多个SHRINK数据，只需要匹配第一个`
  - **意图**：把全局 `$shrink` 的来源从 cfg 改为「读 model 文件找 `.lib 'incFile' corner` 行 → 在 model 同目录定位 incFile → grep 第一个 `SHRINK = 值`」。
  - **关键约束**（用户明列）：①incFile 几十万行要快（建议 grep -m1）②`SHRINK` 与 `=` 间空格数可变 ③多个 SHRINK 只取第一个。
  - **A-档判定**：这是「提出需求 + 给实现规格」的 feature 修改轮（cfg 格式变更，非 bug 诊断）；用户给的是 spec 不是 root-cause。与近轮 ZqCodeLinExtract/HcellMissingFind/FinesimIgnoreGen 同型（goal+method 轮作 A-档），✓ 可作 A-档任务说明。
- **USER#1 (msg 30)**：要求 `generate_report` 报告头部加 shrink 行、把 `* Vdd: 1/1.2 * Vpp: 1/1.2` 改成 `* Voltage: Vdd=... Vpp=...` 格式。本 case 不取此轮（独立子任务，trace 未闭合到接受）。

## assistant 工具链 / 产物
1. `read_files` runModelQA_new.pl → `search_codebase` 找 `getSSD`/`getPVT` 行号 → `run_commands` `grep -n 'sub getSSD'`。
2. **`editor` (msg 19)**：改 `getSSD`（新增局部 `$shrink_from_cfg`，若 cfg 无 shrink 则调 `getShrinkFromModel($model)`）+ **新增 `getShrinkFromModel`**：
   - `abs_path($modelFile)` → `dirname` 取 model 目录
   - 读 model，正则 `^\.lib\s+['"]([^'"]+)['"]\s+\S+` 取 incFile 名（第一个匹配）
   - incPath = 绝对则原样，否则 `$modelDir/$incFile`
   - `grep -m1 -E 'SHRINK[[:space:]]*=[[:space:]]*[^[:space:]]+'` 取首匹配（容空格、几十万行快）
   - 未找到 incFile / incFile 缺失 → `outputMsg("Warn",...)` 回退默认 $shrink
3. `editor` (msg 23) 补空行；msg 31+ 转 generate_report 头部修改（读 901-920 行，trace 末尾 msg 39 仍在定位，未确认接受）。

## 金标准 / DoD
- USER#0 的需求 assistant 已用 `getShrinkFromModel` 实现（msg 19 编辑应用，msg 21「修改已应用」、msg 27「代码结构已验证」）。
- **case 把该技能以可移植 Python 脚本交付**（L1 离线解析）：`extract_shrink.py <model> <output>` → 解析 model 引用的 incFile → 跳过 `*` 注释 → 容空格变长 → 只取第一个 `SHRINK = 值` → 写 output。错误处理（incFile 缺失 / 无引号 include / 无 SHRINK）非零退出。
- A=合成 model_A.sp(`.lib 'incFile_A' mos_tt`)+incFile_A(`* SHRINK=9.999` 注释陷阱 + 真 `SHRINK=0.035` + 后续 0.099/0.150)；hidden B=model_B.sp(`.lib 'incFile_B' ss_15`)+incFile_B(`* SHRINK=9.999` 陷阱 + `SHRINK=0.028` + 0.051/0.077)。A≠B✓。

## 自验
- REF extract_shrink_ref.py：A→0.035 B→0.028 ✓
- check.py 14 断言 a-n：REF PASS 14/14 ✓
- negative/ 6 stub（naive_empty/print_only/hardcode_B/wrong_target/first_match_violation/comment_trap）全 FAIL ✓
- §4.9 三假（empty_zip / print_only / core_cut）全 FAIL ✓
- 断言闸门：k_rationale=14 == k_check=14 ≥ 8 ✓

## 同批 scout 拒绝（parked）
mwijd(meta zlcli 测试)/nv8gj(问报错原因 rootcause)/ne32u(skill 编写 meta)/p8wm1(启动 anasim GUI trivial)/8fe71(解析 .simrc consulting)/izlej(分析 CV_curve 路径 consulting)/r8yj1(GUI 咨询,00:3x 已 scout) → 全 parked。
