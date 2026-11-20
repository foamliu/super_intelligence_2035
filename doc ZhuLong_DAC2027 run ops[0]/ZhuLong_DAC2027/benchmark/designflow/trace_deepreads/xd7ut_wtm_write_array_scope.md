# xd7ut — WTM write-to-array scope (deepread)

## trace
- session: `1792033394584_xd7ut` · user `tongfanl` · host `hfhds201`
- size 1.38MB · 234 msgs · last=assistant COMPLETE
- source: 11-05 重扫令 hfhds201 cron 盲区 top-100 diff ledger_B → 9 not-in-ledger non-internal (all tongfanl) → peek 9 → xd7ut CLEAN
- spice_sim / DDR6 vecgen sim_vector domain (same as xk1n1)

## A-faithful 选轮
- U#0 (msg 0) 逐字：「/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen\n帮我分析下这个环境，并回答：当进入WTM 模式时，发送write命令，会不会把数据发到array里去？」
- 提出需求/问题，无根因、无修复方向 → A-faithful CLEAN ✓
- 后续轮 (U#69「如何让我发送的write不往array里写」、U#71「仅分析ddr6_test.sv即可」、U#112 CRC注错、U#154 写task、U#195 WTM004 完善...) 漂移到修复方案/CRC注错 → 不入 prompt

## 金标准（assistant 真实产物，人工复核）
assistant 经 read_files + run_approved_command(python-runner grep/sed 在 /proj/dscqa 源码树) 给出完整证据链：

**核心结论（A#107）**：当进入 WTM 模式发送 write 命令时，**数据会写入 array**（因为 `write_mem_arr` 的门控条件只跳过 `Write_Leveling_Training`，未包含 `Write_Training_Mode`(WTM)）。

### 完整证据链（真实 file:line，从 trace tool_result 提取）
1. **write_mem_arr 调用** — `ddr6_test.sv:1548`:
   `write_mem_arr(.ba(ba),.bg(bg),.col(col),.bl(bl),.dq(dq_org),.pw(pw));`
   （array 写路径：把期望读数据写入 memory array）
2. **门控 if** — `ddr6_test.sv:1537`:
   `if(!nt & !cmd_ignore&!command_block_flag&!current_command_block_flag & !(\`mr_da.MR5_func_mode == Write_Leveling_Training)) begin`
   - 跳过条件只列 `Write_Leveling_Training`，**未列 `Write_Training_Mode`(WTM)**
   - 即 WTM 模式下该 if 条件成立 → write_mem_arr 执行 → 数据写入 array
3. **MR5_func_mode 枚举** — `ddr6_package.sv:387-403` `typedef enum bit [7:0] {...} MR5_func_mode_enum;`：
   - `Write_Leveling_Training = 8'b0001_0000` (line 394)
   - `Write_Training_Mode      = 8'b0001_0001` (line 395) ← WTM，与 Write_Leveling_Training 是**不同**枚举值
   - 故 `MR5_func_mode == Write_Leveling_Training` 在 WTM 模式下为 false → 不跳过
4. **struct 字段** — `ddr6_package.sv:485`: `MR5_func_mode_enum MR5_func_mode;`（modereg struct 中 MR5 OP 字段）
5. **MR5 MA 地址** — `ddr6_specdef.sv:259`: `parameter bit[MODEMA_BITS-1:0] MA_func_mode = 5;`（MR5 = func mode）
6. **OP 参数** — `ddr6_specdef.sv:267`: `OP_func_mode_Write_Leveling_Training = 8'b0001_0000`；line 268 `OP_func_mode_Write_Training_Mode = 8'b0001_0001`
7. **distractor 同款跳过**（证明脚本必须定位 write_mem_arr 的门控，而非任意 MR5 跳过）：
   - `ddr6_test.sv:734`: `if(!(\`mr_da.MR5_func_mode == Write_Leveling_Training)) begin //xxm0928`（另一 task）
   - `ddr6_test.sv:809`: `if (!cmdcancel & !cmd_ignore&!command_block_flag&!current_command_block_flag & !(\`mr_da.MR5_func_mode == Write_Leveling_Training)) begin`（Active task 路径）

### 对比结论
- `Write_Leveling_Training` 模式：在 skip 条件内 → write_mem_arr 被跳过 → 数据**不**写入 array
- `Write_Training_Mode`(WTM)：**不**在 skip 条件内 → write_mem_arr 执行 → 数据**写入** array

## 合成
- 通用化脚本 `analyze_wtm_write_array.py <root> -o out.json`：静态解析 SV 树
  - 找 `write_mem_arr(` 调用 → 记 file:line + raw
  - 向上找最近的 `if(...) begin` 且条件含 `MR5_func_mode ==` → 门控 if（记 line + condition）
  - 从条件抽 `MR5_func_mode == <Enum>` 的 `<Enum>` → skip_modes
  - 找 `typedef enum ... { ... } MR5_func_mode_enum;` → all_modes（枚举成员名）
  - wtm_in_skip_modes = ("Write_Training_Mode" in skip_modes)
  - write_goes_to_array_in_wtm = not wtm_in_skip_modes
  - write_leveling_skipped = ("Write_Leveling_Training" in skip_modes)
  - conclusion = "write_goes_to_array" if write_goes_to_array_in_wtm else "write_skipped_in_wtm"
- A=真实 SV 节选（ddr6_test.sv 1537-1548+734+809+1628 / ddr6_package.sv 387-403+485 / ddr6_specdef.sv 259-275）
  - 实体 .sv 在 /proj/dscqa 对 t0002965/e0031982 权限拒绝 → A 资产为从 trace tool_result 提取的真实 file:line 节选
- hidden B=合成变体：门控 if (1537) 额外含 `& !(\`mr_da.MR5_func_mode == Write_Training_Mode)` → skip_modes=[Write_Leveling_Training, Write_Training_Mode] → wtm_in_skip_modes=True → write_goes_to_array_in_wtm=False（与 A 相反，挡硬编码）；distractor 734/809 保持只跳 Write_Leveling_Training

## 判分（15 断言 a-o）
a zip 含 analyze_wtm_write_array.py + py_compile exit 0
b B: outB.json 合法 JSON dict 含必需键
c B: write_mem_arr_call.line 为 int > 0（找到调用）
d B: write_mem_arr_call.raw 含 "write_mem_arr" 且 ".ba(" 且 ".dq("（非子串误命中）
e B: gating_if.line 为 int > 0（找到门控 if）
f B: skip_modes 为 list 含 "Write_Leveling_Training"
g B: "Write_Training_Mode" in all_modes（WTM 是合法枚举成员）
h B: wtm_in_skip_modes == True（B 中 WTM 被跳过，非硬编码 A 的 False）
i B: write_goes_to_array_in_wtm == False（B 中 WTM 不写 array，与 A 相反）
j B: write_leveling_skipped == True
k B: conclusion == "write_skipped_in_wtm"
l 交叉输入守卫：A 上 wtm_in_skip_modes==False & write_goes_to_array_in_wtm==True & conclusion=="write_goes_to_array"（证明泛化，非硬编码 B）
m A-only 未泄漏：outB.json 无 A-only 标记 "A_only_marker_WLVL_1537"
n 3 次幂等：B 上 outB.json sha256 一致
o evidence 为非空 list

## 自验
- ref PASS 15/15 + 4 negative 全 FAIL distinct + NEG_RC=0 + §4.9 三假全 FAIL + 断言闸门 15==15≥8
