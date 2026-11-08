# trace_deepread — bjkmi · DQSEH flag no-effect diagnosis

## trace
- session `1790849679042_bjkmi` (tongfanl@hfhds201, dir-based, 534 msgs, 4.2MB)
- U#0 (A-faithful 提出需求, no root-cause/fix): "帮我看下这个路径下/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local，运行脚本./runsti/gen_stimulus_ltf后，无论有没有定义-d \"DQSEH\"，产生的激励都是PSD0出DQ543、PSD1出DQ210。这是为啥？"
- 后续 U#71/U#111/U#136/U#142/U#154/U#164 扩展为 6 章 notes 文件（不入 A 档 prompt，仅 U#0 作 prompt）

## 金标准 (assistant M#70 — 直接回答 U#0 的根因诊断)
两个独立根因，任一即可导致 DQSELH 未定义 → else 分支 → PSD0=DQ543/PSD1=DQ210：

### 根因 1：`## -d "DQSEH"` 是 shell 尾随注释（flag 未传入）
gen_stimulus_ltf 真实内容（trace M#17 tool_result 逐字）：
```
1 | ### /home/wenwenl/work/DDR6/d6vecgenbak -q verilog -p dscqa -v V0 -f cfg_files/zq_cfg_tongfanl -l log/stimulus_tongfanl/ZQ
2 | ##/home/wenwenl/work/DDR6/d6vecgenbak -q verilog -p dscqa -v V0 -f cfg_files/cfg_WTM  -l log/stimulus_tongfanl/WTM_fsm
3 | /home/coverage/DDR6/d6vecgen -q star -p dscqa -v V0 -f cfg_files/cfg_WTM  -l log/stimulus_tongfanl/WTM_fsm_1001  ## -d "DQSEH" 
4 | # /home/coverage/DDR6/d6vecgen -q rscalc -p dscqa -v V0 -f cfg_files/zq_cfg_tongfanl  -l log/stimulus_tongfanl/ZQ_0918 
5 | #/home/tongfanl/d6vecgen_tongfanl -q rscalc -p dscqa -v V0 -f cfg_files/controller_cfg_tongfanl  -l log/stimulus_tongfanl/Aging_control_1_0914 
```
- Line 3 = 唯一活跃命令（首字符 `/`，非 `#`）。行尾 `## -d "DQSEH"` 是尾随注释（`##` = shell 注释符）→ `-d "DQSEH"` **未传入** d6vecgen
- Lines 1,2,4,5 = 整行注释（`#`/`##`/`###` 开头）

### 根因 2：宏名不匹配 `DQSEH` ≠ `DQSELH`
ddr6_genvector.sv 真实内容（trace M#58 tool_result, lines 168-275 逐字）：
- 代码检查的宏是 **`DQSELH`**（DQ-SELect-High，多一个 L）
- 命令行传入的是 **`DQSEH`**（少了 L）→ 即使传入也不匹配，宏不定义
- 即使两个根因都不存在（flag 传入 + 名字匹配），才会走 `ifdef DQSELH` 定义分支

### DQ 映射逻辑 (X1P6 + SC0, 非 SK1P6)
PSD0 DQ（6-bit {DQ5..DQ0} 拼接）：
- `ifdef DQSELH` → `{3'bz, A_pin_if.DQ[2:0]}` → 驱动物理 DQ2,DQ1,DQ0 = **"DQ210"**
- `else`          → `{A_pin_if.DQ[2:0], 3'bz}` → 驱动物理 DQ5,DQ4,DQ3 = **"DQ543"**

PSD1 DQ：
- `ifdef DQSELH` → `{A_pin_if.DQ[5:3], 3'bz}` → 驱动物理 DQ5,DQ4,DQ3 = **"DQ543"**
- `else`          → `{3'bz, A_pin_if.DQ[5:3]}` → 驱动物理 DQ2,DQ1,DQ0 = **"DQ210"**

### 有效结果
DQSELH 未定义（根因 1+2）→ else 分支 → **PSD0=DQ543, PSD1=DQ210** ✓ 与用户观察一致

## 合成 (通用化 diag.py)
- CLI: `diag.py <script> <genvector> --width <W> --sc <S> -o out.json`
- 解析 shell 脚本：找活跃 d6vecgen 命令行（首字符非 `#`），提取 `-d "MACRO"` 及其是否在尾随注释（`#`/`##`/`###` 之后）
- 解析 SV：ifdef 栈式解析，按 config(width/sc/sk1p6) 走活跃分支，找最内层非 config 宏（非 X1P12/X1P6/X2P3/X2P6/SK1P6/SC0/SC1/DUALSC/COMPRESS）的 `ifdef <MACRO>` 守护的 `{...DQ[...]...}` 表达式
- 物理引脚标签：`{X, Y}` 拼接按 MSB→LSB 映射到物理 DQ 位，非 z 的位 = 驱动位，标签 = "DQ" + 降序位号拼接
- 输出 JSON: {flag_passed, comment_marker, cli_macro_name, code_macro_name, name_match, config, psd0_mapping{defined,undefined,effective}, psd1_mapping{...}, effective_mapping{PSD0,PSD1}, root_causes}

## A (真实 trace-time 资产, 逐字)
- A_gen_stimulus_ltf = trace M#17 逐字（6 行）
- A_genvector.sv = trace M#58 lines 168-275 逐字（PSD0/PSD1 DQ 段，含 X1P12/X1P6/X2P3/X2P6 + SK1P6/SC0/SC1/DUALSC + DQSELH 嵌套）

## hidden B (合成, 结构不同, 挡硬编码)
- B_gen_stimulus: 不同脚本，`-d "WRSEQ"` **未注释**（真传入），不同路径/cfg/log
- B_genvector.sv: 8-bit DQ bus, 宏 `WRSEQ_H`（非 DQSELH），config X2P3+SC1（非 A 的 X1P6+SC0）
- B 测试：flag_passed=true, name_match=false (WRSEQ vs WRSEQ_H), effective=undefined 分支 (PSD0=DQ3210, PSD1=DQ7654), root_causes=["macro_name_mismatch"] (无 flag_commented_out)
