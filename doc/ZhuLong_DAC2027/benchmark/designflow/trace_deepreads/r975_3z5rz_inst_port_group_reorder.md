# Deep-read: r975 — 3z5rz (guomings @ hfeg0pkn003, mc67)

## Session
- session_file: `1795075634215_3z5rz.messages.json`
- user: guomings, host: hfeg0pkn003, mc=67
- keywords: rtl:78;synopsys:5;verilog:3;analog:1 (A-pure digital)
- size: 1037745 bytes, 137 messages, 9 clean user turns

## Trace gold (U#1, the selected intent)

User verbatim:
> /proj/lagat/V0_digital/workdir/guomings/project/sos6/units/slice_wrapper/rtl/slice_interface.v 里面 u_cxmt_dont_touch_dram1sc 的例化接口分类排列下，有规律点，然后 PAD_DQ / PAD_DQST / PAD_DQSC / ZQ0 / ZQ1 / ALERT0 / ALERT1 / FP_RST_N / RST_N_DRAM / CSR_READEN_RST_POS_DSB / ... / CP_EN / ICP / ... / VCTRL_DAC / R_SEL / C_SEL / ... / RST_N_DIV / P_PRE / P_FB / ... / CLK_MF_P0 / CLK_LF_P0 / ... / HCLK_P / HCLK_N / ... / FP_DQ0_OE~FP_DQ11_OE / ...

The user lists desired functional groupings for the ports of the
`u_cxmt_dont_touch_dram1sc` instantiation in `slice_interface.v` and asks
the agent to "classify and arrange" them to be "more regular".

### Assistant's actual work (msg 1–51)
1. read_files slice_interface.v lines 489–620 (the dram1sc instance block, ~100+ ports).
2. First edit attempt (msg 30) accidentally ADDED ports not in the dram1sc
   instantiation (ALERT_CLK, FP_RALERT, BYPASS, VCO_EN…) — those only exist
   in the sibling `u_SLICE_SP_IO` (else branch).
3. Recognised the error (msg 33), re-copied the original, and redid the edit
   (msg 36) reorganising ONLY existing ports into named groups:
   - `// 0) Front — Result & Status Outputs` (RESULT, DQ_OUT, P_CLK, S2P_DVLD, FP_RDQ, ALERT_OUT, CSR_DTC_RES, PLL_CLK_MUX, OSC_CLK_MUX)
   - `// 1) DRAM PAD Interface` (PAD_DQ, PAD_DQST, PAD_DQSC, ZQ0, ZQ1, ALERT0, ALERT1, FP_RST_N, RST_N_DRAM)
   - `// 2) Reset` (CSR_READEN_RST_POS_DSB, CSR_READEN_RST_NEG_DSB, RSTN_1P25G, SLICE_RX_SFT_RSTN)
   - `// 3) CP (Charge Pump)` (CP_EN, ICP, DAC_EN)
   - `// 4) PLL Trim` (VCTRL_DAC, R_SEL, C_SEL, VCO_RESERVE, LOCK_FORCE, LOCK_RESET, BG_TR, LDO_TR)
   - `// 5) PLL Divider` (RST_N_DIV, P_PRE, P_FB)
   - `// 6) PLL Clock Output` (LOCK, CFEQ_RDY, CLK_MF_P0, CLK_MF_P180, CLK_LF_P0…)
   - `// 7) PLL Reference Clock & HCLK` (CLK_REF, HCLK_P, HCLK_N)
   - `// 8) FPGA DQ/CA/CK Write Data` (FP_DQ_PRE, FP_DQ_MAIN, FP_DQ_POST, FP_DQST, FP_DQSC, FP_CA, FP_CS, FP_CKT, FP_CKC)
   - `// 9) DQ Enable & Control` (FP_DQ_RD_EN, FP_DQS_RD_EN, FP_DQST_OE, FP_DQSC_OE, …)
   Each group preceded by a `//===...` bar + `// N) <name>` + `//===...` header.
   All `.PORT(SIG)` connection lines preserved verbatim; only order changed +
   headers inserted. Lines outside the instance block untouched.
4. Tried to copy the edited file back to the read-only original (chmod 444) —
   permission denied (msg 44); attempted chmod+copy (msg 45–46). (The
   destination being read-only is an environment artefact, not part of the
   intent — the deliverable is the reordered file content.)

### Key insight for case design
The intellectual core is: parse a Verilog instance block, map each port to a
user-specified group, reorder so groups appear in order (ports within a group
in the user-listed order), insert group-header comments, preserve everything
else. Ports the user listed but the instance doesn't have → skip. Ports the
instance has but the user didn't list → "Other" tail (original order).

## Other user turns in this session (NOT used, to avoid dup with r971)
- U#2/U#3/U#4: "文件路径在哪" / "你重新排列的文件路径在哪" / "其他的信号去哪了，也加上" — follow-ups to U#1.
- U#5/U#6: "忘掉之前的事" / "无视之前的对话，重新做一件事？" — context reset.
- **U#7**: slice_interface.v tie-zero task (same project, different file).
- **U#8**: slice_interface_sos.v tie-zero task — **this is the EXACT intent
  used in r971 (InstTieZeroProduce-001)**. Deliberately NOT used here to
  avoid duplicating r971.
- U#9: reorder slice_interface_sos_tmp.v ports — a later variant of U#1 on a
  different file; structurally identical to U#1, so U#1 was chosen as the
  canonical intent.

## Case produced
`EDA-Eval-DesignFlow-InstPortGroupReorderProduce-001` (digital, A档
trace-faithful produce-task + hidden-B, k=18/18 + §4.9 three-fake FAIL).
Generalised script: `reorder_inst_ports.py <src.v> <inst_name> <groups.json>
<out.v>`. A = slice_interface_A.v (17 ports, 5 groups) + groups_A.json;
hidden B = slice_interface_B.v (phy_bb u_phy_blackbox, 14 ports, 3 groups) +
groups_B.json. ref PASS 18/18, 3 neg FAIL, §4.9 three-fake FAIL.
