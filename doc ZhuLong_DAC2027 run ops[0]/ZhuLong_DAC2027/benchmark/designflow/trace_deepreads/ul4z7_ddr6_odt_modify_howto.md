# ul4z7 — DDR6 激励环境 ODT 修改方法 Q&A (peek + synth)

## trace metadata
- session: `1792055082930_ul4z7.messages.json`
- user: `tongfanl`
- host: `hfhds206` (10.129.32.80)
- match_count: 12 (D ledger)
- domain: waveform (D-pure, kw analog:224/netlist:4)
- size: 213933 bytes, 26 msgs (6 user / agent=lead)

## 选轮判定 (A档合规)
- **U#0 (msg 0) verbatim**: `<user_input mode="act">帮我看下激励环境中，如何修改ODT的值。</user_input>`
- 选轮规则①（提出需求/表达目标）✓ — 用户提出"如何修改 ODT"需求
- 选轮规则②（已指出根因或修复方案）✗ — 用户未给根因，未给修复
- ⇒ A档合规，可作 task 说明（verbatim 原文）

## trace assistant 探索线索（GOLD 来源）
assistant 探索 ~/DDR6/ 验证环境，发现：
- 工作目录基于 `verilog.ddr6.dscqa.vecgen` testbench (ddr6_tb_notes.md)
- 顶层 `ddr6_test.sv` 72 行起声明 ODT 寄存器：`odt_ca_out`、`CA_RTT[RANK_NUM]`、`CK_RTT[RANK_NUM]`、`CS_RTT`、`DQ_RTT`、`DQS_RTT`
- `wr_rd_odt_timing_check.pl` 含 WRODT/RDODT 时序检查
- ODT 控制由 MR17/MR18/MR19/MR20 模式寄存器 RTT 字段控制：
  - `CA_RTT` ← MR18 OP[5:3]
  - `CK_RTT` ← MR18 OP[2:0]
  - `CS_RTT` ← MR17 OP[5:3]
  - `DQ_RTT` ← MR19 OP[2:0]
  - `DQS_RTT` ← MR20 OP[2:0]
- ODTL 偏移由 MR26/MR27 控制
- trace 在 stage 2 grep 时 `code_sidecar_sigterm` 中断（msg 25），未给最终 gold

## 其他用户轮（不取）
- U#6-8「marker 字体大小」— 无 gold，与 ODT 无关
- U#9「PRBS_TM 总结一下这个电路」— SIGKILL 中断，且 ujw1y 会话已有 PrbsTmCircuitSummaryQA-001

## reframe 决策
- 套用 **r928 SpiceIbisConvMethodQA-001 / r929 WvEyeDiagExtTrigMethodQA-001** manual-grounded howto produce reframe 范式
- A 手册 `ddr6_odt_modify_method_A.md` 由 trace 探索发现的事实（MR17-20 映射 + ODTL MR26/27）合成，并补全 DDR6 ODT 标准 GUI/SKILL 双方法、参数表、其他设置、知识库引用
- B 手册 `lpddr5_odt_modify_method_B.md` 平行场景（LPDDR5 ODT modify，不同 MR 布局 MR2/MR11/MR12/MR22/MR32 + ZQ Calibration，反硬编码 A-only token）
- candidate.py = `odt_method_guide.py` 通用 markdown 手册解析器（同 r929 wv_method_guide.py 范式）
- check.py 12 断言 a-l，identifier-boundary 正则匹配 A-only token（避免 MR26 误匹配 MR2、mrw_init 误匹配 zq_mrw_init）

## 自验
- reference_submit.zip 12/12 PASS ✓
- 3 neg 全 FAIL：empty→c / print_only→g / core_deleted→e ✓
- ALL_NEG_FAIL=True + §4.9 (a)(b)(c) 三假覆盖 ✓
- jsonl test 字段 sha256 39ba3d4b...424446 == disk check.py sha256 MATCH ✓
- cross-shard dup check 0/5 clean ✓
- D.jsonl 500→501 行
- ledger mark --session ul4z7 --status case --force ✓

## 子维度
- DDR6 ODT modify howto D 域首例（waveform 子维度补 DDR-protocol-ODT-howto）
- manual-grounded howto Q&A→produce reframe D 域第 3 例（承 r928 SpiceIbisConv / r929 WvEyeDiagExtTrig）
- l1_subgrade=L1-realrun-python 续标第 13 case
- asset_fidelity=synthesized-reframe 续标（D 域第 5 例，承 r921/r924/r928/r929 范式）
