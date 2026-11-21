# Deepread: r971 — session 1795078644380_7t4og (guomings @ hfeg0pkn003, mc102)

## Trace Overview
- **Session**: 1795078644380_7t4og.messages.json
- **User**: guomings
- **Host**: hfeg0pkn003
- **mc**: 102, keywords: rtl:94;synopsys:17;verilog:5;primetime:3 (A-pure digital/rtl)
- **Domain**: A-pure digital (rtl dominant, synopsys/primetime → rtl 静态分析/synthesis 上下文)
- **Messages**: 218 (111 user / 107 assistant)
- **File size**: 1.3MB
- **Scan source**: ssh_eda_search_20261121_151844 (fresh A-domain candidate from r963 _a_dom_cands)

## User Intent (逐字, act-style 提取)
10 个 act-style 用户消息（port reorder / tie-zero / bbox rebuild 等任务，跨多轮）。本 case 提炼源为 **U#87**：

> 忘掉之前的事情，把 /proj/lagat/.../slice_interface_sos.v 这个文件中
> u_cxmt_dont_touch_dram1sc 例化的接口，输入全部 tie0，输出全部悬空，
> 生成一个新文件 slice_interface_sos_tmp.v

## Session Main Line
DRAM PHY fullchip 仿真环境 slice_interface 搭建。dram1sc 是 dont_touch blackbox，
上层 slice_interface_sos.v 在缺少 dram1sc 实物时需做 placeholder 改造以编译/跑通。
用户要求写脚本自动化 tie0/open 改造，生成 *_tmp.v。

## 本 case 提炼源 (U#87)
### 上下文
- 用户先让 assistant 读 slice_interface_sos.v，理解 dram1sc 例化块结构
- 例化块形如：
  ```
  dram1sc u_cxmt_dont_touch_dram1sc(/*autoinst*/
      // reset / global
      .RST_N_DRAM                 (RST_N                  ), //input //INST_NEW
      ...
      .CSR_DQ1_TX_OE_DLY          (CSR_DQ1_TX_OE_DLY[10:0]), //input //INST_NEW
      ...
      .PAD_DQ                     (PAD_DQ[7:0]            ), //inout
      .LOCK                       (LOCK                   ), //output
      ...
      .STATUS_FIFO                 (STATUS_FIFO[15:0]      )  //output //INST_NEW
  );
  ```
- 每端口行带方向注释 `//input` / `//output` / `//inout`，部分带 `//INST_NEW`

### Trace Gold (assistant M#98–M#116)
assistant 写 Python 脚本 `generate_sos_tmp.py`：
1. **定位例化块**：找含 `u_cxmt_dont_touch_dram1sc` 的行，括号深度追踪到 `);` 闭合
2. **逐端口改写**（按方向注释）：
   - `//input` → `1'b0`（多 bit 用 `{N{1'b0}}`，N 从 connection 里的 `[hi:lo]` 推断）
   - `//output` / `//inout` → 悬空 `()`（空括号，端口名 `.PORT` 保留）
3. **保留**：端口名、方向注释（含 `//INST_NEW`）、`// synopsys black_box` 尾注释、
   例化块之外全部代码（module 声明 / wire / 其他例化 / endmodule）
4. 写入 slice_interface_sos_tmp.v

## Case 契约 (EDA-Eval-DesignFlow-InstTieZeroProduce-001)
- **mode**: design_flow (produce-task)
- **reframed**: 泛化为 `tie_inst_zero.py <src.v> <inst_name> <dst.v>`
- **visible A**: `slice_interface_A.v`（inst `u_cxmt_dont_touch_dram1sc`，8 input + 10 output/inout）
- **hidden B**: `phy_wrapper_B.v`（inst `u_phy_dram1sc`，8 input + 9 output/inout，不同 module/port 名/位宽/方向混合）
- **anti-hardcode**: B-only 端口名（POR_B_N/CTRL_WORD/BIAS_TRIM_B/SCAN_EN_B）必须在 B 输出中，A-only 端口名不得泄漏进 B 例化块
- **check.py**: 16 条独立断言（a–p），subprocess 在 B 上跑 SUT 脚本，A 作金标交叉检查
- **§4.9 anti-degenerate**: 3 假提交（空壳/print-only/core-deleted）全 FAIL（negative_selftest.py 验证通过）

## Verification
- REF selftest: PASS (check.py --selftest)
- negative_selftest: ALL OK (REF PASS, neg_a_empty FAIL, neg_b_print_only FAIL, neg_c_core_deleted FAIL)
- A 输出人工核对：8 input 全 tie（CSR_DQ1_TX_OE_DLY={11{1'b0}}, CML_IBIAS1_CTRL={4{1'b0}}），10 output/inout 全 open，块外代码完整
- B 输出人工核对：8 input 全 tie（CFG_BUS_IN={16{1'b0}}, CTRL_WORD={24{1'b0}}, BIAS_TRIM_B={6{1'b0}}, BIST_MODE_B={3{1'b0}}），9 output/inout 全 open，u_osc_main/endmodule 保留

## 修复记录
首轮 ref 脚本有两处 bug（selftest 暴露）：
1. `close = m.group(3)` 取错组（group 3 是 conn 不是 close paren）→ 改用 named group `m.group('close')`
2. PORT_RE 不匹配 `),`（逗号在 `)` 后）→ 改为 `(\)\s*,?\s*)` 允许可选逗号
check.py 的 `_parse_inst_block` port_re 同步修复逗号问题。
