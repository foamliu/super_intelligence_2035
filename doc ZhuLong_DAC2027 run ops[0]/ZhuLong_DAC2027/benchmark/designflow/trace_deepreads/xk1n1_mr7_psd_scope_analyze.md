# trace_deepread: xk1n1 — MR7 PSD0/PSD1 scope analyze (spice_sim A-faithful)

## trace 来源
- user: tongfanl · host: hfhds201 · session: 1791958972412_xk1n1 · match_count: 506
- path: /home/tongfanl/.cline/data/sessions/1791958972412_xk1n1/1791958972412_xk1n1.messages.json
- nmsg: 74 · last: assistant (COMPLETE, 证据链闭环)
- 11-05 重扫令 hfhds201 cron 盲区 not-in-ledger top-250 diff ledger_B(robust) → 178 not-in-ledger → peek top 18 → xk1n1 CLEAN

## A-档选轮判定
- U#0（逐字原文）：`/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local\n帮我看下，对于MR7，会区分PSD0或者PSD1吗？是不是只用设置PSD0即可，PSD1会和PSD0的保持一致。`
- 选轮合规：U#0 提出需求（理解 MR7 是否区分 PSD），**无根因、无修复方向** → A-faithful CLEAN ✓
- 后续无用户追问（trace 止于 assistant 最终答案 U#0 → A#73）

## 金标准（assistant A#73 完整分析，证据链闭环）
**结论：MR7 不区分 PSD0/PSD1，只设置一次即可** —— MR7 在 direct 共享空间，PSD0/PSD1 共享同一份 MR7。

### 代码证据（真实 file:line，从 trace tool_result 提取）
1. **MR7 的 MA 值 = 7（direct 空间，MA[7]=0）**
   - `ddr6_specdef.sv:36`: `MODEMA_BITS = 8; // bit[7]=0 : modereg_direct`（MA[7]=0 → direct 共享；MA[7]=1 → page per-PSD）
   - `ddr6_specdef.sv:288-308`: `MA_zq_upd_flag / MA_zq_initiator / MA_zq_rst / MA_zq_stop / MA_zq_interval = 7`（MR7 的 5 个字段 MA=7）

2. **MR7 字段属于 TYPE_modereg_direct（共享 struct）**
   - `ddr6_package.sv:487-491`: MR7 的 5 字段（MR7_zq_upd_flag/initiator/rst/stop/interval）定义在 `TYPE_modereg_direct` 内
   - `ddr6_package.sv:585`: `} TYPE_modereg_direct; // Direct address (shared between both PSD0, PSD1)` ← **共享注释**
   - 对比 `ddr6_package.sv:788`: `} TYPE_modereg_page0; // per PSD page0` ← page 空间才是 per-PSD

3. **实例化：direct 单份，page 按 [0:1] 分 PSD**
   - `ddr6_interface.sv:129`: `TYPE_modereg_direct modereg_direct;` ← **单份**
   - `ddr6_interface.sv:136`: `TYPE_modereg_page0 modereg_page0[0:1];` ← per-PSD 数组

4. **宏定义：mr_da 单份，mr_pg0 [0:1]**
   - `ddr6_test.sv:8-9`: `` `mr_da = ShareDRIVER.modereg_direct ``（单份）、`` `mr_pg0 = ShareDRIVER.modereg_page0 ``（[0:1]）

5. **写入路径：MRSettingDirect case 7 只写 mr_da（无 psd 参数）**
   - `timing_load.sv:2362-2368`（MRSettingDirect 的 case 7）:
     - 2363: `` `mr_da.MR7_zq_upd_flag = ShareDRIVER.mr_direct[7][0]; // ZQ Update Flag, Attribute = R ``
     - 2364: `` `mr_da.MR7_zq_initiator = ShareDRIVER.mr_direct[7][1]; // Attribute = R ``
     - 2365: `` `mr_da.MR7_zq_rst = ShareDRIVER.mr_direct[7][2]; // Attribute = RW ``
     - 2366: `` `mr_da.MR7_zq_stop = ShareDRIVER.mr_direct[7][3]; // Attribute = RW ``
     - 2367: `` `mr_da.MR7_zq_interval = ShareDRIVER.mr_direct[7][6:4]; // Attribute = RW ``
   - 函数签名无 psd 参数 → 只更新一份共享 shadow

6. **总线行为：MRUPD 对 direct MR 固定广播 4'b1111**
   - `ddr6_test.sv:4848-4863`（MRUPD task）:
     - 4848: `if((dutconfig.dqmode == X1P6 || dutconfig.dqmode == X1P12) && ma[7]) begin` ← page MR (ma[7]==1) 才走 per-PSD
     - 4849-4856: page MR 由 ca4_bit 选 die：`4'b1111`→两 PSD 都写、`4'b0011`→自身 PSD、`4'b1100`→另一 PSD
     - 4859: `end else begin` ← direct MR (ma[7]==0, 含 MR7)
     - 4860: `mrwenable = multicyc_flag && (ca4_bit == 4'b1111) & ...` ← **direct MR 只接受 4'b1111（广播）**
     - 4863: `MRSettingDirect(...)` ← 写共享 shadow

### 顺带行为特性（与 PSD 无关）
- ZQ Interval 只在 zq_initiator=1 时有效（timing_load.sv:2168-2170）
- zq_rst 自清除（ddr6_test.sv:2541-2546）
- OP[0]/OP[1] 是只读状态位（Attribute = R）

## 合成方案
- 通用化脚本 `analyze_mr7_psd_scope.py <root> -o out.json`：静态解析 SV 文件树，判定 MR7 的 PSD 作用域
  - 解析 ddr6_specdef.sv：找 `MA_zq_*=<n>` → mr7_ma；找 `MODEMA_BITS` + bit[7] 语义
  - 解析 ddr6_package.sv：找含 `MR7_zq_*` 字段的 `TYPE_modereg_<x>` struct + 闭合注释（shared vs per PSD）
  - 解析 ddr6_interface.sv：找 `TYPE_modereg_<x> <inst>;` vs `<inst>[0:1];` → single vs array
  - 解析 ddr6_test.sv：找 `` `mr_da / `mr_pg0 `` 宏定义；找 MRUPD `ma[7]` 分支 + ca4_bit 条件
  - 解析 timing_load.sv：找 MRSettingDirect case 7 → 写目标（mr_da vs mr_pg0[psd]）
  - 输出 JSON：{mr7_ma, ma_bit7, space("direct"|"page"), struct_name, struct_comment, shared(bool), per_psd(bool), storage("single"|"array[0:1]"), write_target, ca4_required, conclusion("shared"|"per_psd"), evidence:[{file,line,snippet}]}
- A = 真实 SV 节选（5 文件，上述证据行）
- hidden B = 合成 per-PSD 变体：MR7 字段在 TYPE_modereg_page0、实例 [0:1]、写 mr_pg0[psd]、MRUPD per-PSD → conclusion="per_psd"（与 A 相反，挡硬编码 "shared"）
- 判分 ≥8 断言 + 交叉输入守卫（A→shared 证明真解析）+ A-only 泄漏闸门 + 3 次幂等
