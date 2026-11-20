# q1589 — SimFailTimeoutDiagQA deepread

**session**: 1794549895955_q1589 · **user**: cliu · **host**: hfeg0pkn004(10.129.2.11) · **mc**: 59
**trace**: /home/cliu/.cline/data/sessions/1794549895955_q1589/1794549895955_q1589.messages.json (82 msgs)
**domain**: analog_context (sim-log-grounded fail-diagnosis)

## verbatim user turns (substantive)

- **U#0**: 「帮忙重新跑一个下面路径的仿真@/home/cliu/rand_test_1111/sim_logs/R_rsaoi22nor2_SrefOscSR」
- **U#14**: 同上 + 「波形为.trn文件」
- **U#22** (本 case 取此轮): 「帮忙分析这个仿真fail的原因@/home/wellesc/VerilogLibVerifiy/c_VeriligLibVerifier/sim_logs/01/C_latrq5_RdApCaFifoDataSel」
- **U#31**: 「帮忙修正上面的问题」(修正轮，不进 prompt)
- **U#78**: xrun SIGTERM「仿真不结束是什么原因」(另一案)
- **U#80**: SUMMARY B8「说明一共花费多长时间转成功？」(另一案)

## 助手诊断 (MSG#30, gold answer)

**结论**: TIMEOUT（不是逻辑不匹配）。cell C_latrq5_RdApCaFifoDataSel 内部存在组合反馈环（"SrefOsc" 自参考振荡），在随机向量下不停翻转，仿真挂死，150s 看门狗强杀。

**证据链**:
1. result.json status=TIMEOUT，所有统计量 -1（err/xmatch/cond/checks/k/w/rc 全 -1）→ 仿真未到 $finish
2. xrun.log 止于 `// START: cell=C_latrq5_RdApCaFifoDataSel lib=01 K=64 W=10`，无 RESULT/MISMATCH/$finish → 被看门狗杀
3. DUT 拓扑: `trireg (medium) #(0,0,200) net18` (电荷保持三态结点); 反馈环 net18→inv_base I19(.A(net18|RSTD),.Y(net19))→net19→ntn_lv MN0(.D(net18),.G(net19))/ptn_lv MP1(.D(net18),.G(net19))→net18; 共享结点 net18 上 5 个 inven_base (I16/I20/I21/I22/I23) + 2 传输管 + trireg 竞争; 无非零延迟/复位稳定环节 → 0 延迟组合振荡
4. golden gld.v 用 C_FifoFb5Lv__gld 块 (.Out(net18), .In(net19), .Clk0/Clk1/ClkN0/ClkN1 选通) 实现同一反馈功能

## 源可达性

ssh 10.129.2.11 (cliu's host) → /home/wellesc/VerilogLibVerifiy/c_VeriligLibVerifier/sim_logs/01/C_latrq5_RdApCaFifoDataSel/ **真实可达** (world-readable via hfdes group):
- result.json (1229B) · xrun.log (12641B) · xrun.history (836B)
- C_latrq5_RdApCaFifoDataSel_dut.v (6809B) · C_latrq5_RdApCaFifoDataSel_gld.v (11441B) · tb_C_latrq5_RdApCaFifoDataSel.sv (4634B)

→ A-grade (源真实 on-disk，非 B-grade 重建)。scp 全部到 .75 workdir 原样保留。

## case 设计

套 cited-evidence-chain r699/r704 root-cause 族 (h01fd/vhb6i)。候选写 sim_fail_diagnose.py 读 (sim_log_dir, question) → 结构化 JSON 8 键 (question/sim_status/evidence_chain/root_cause/loop_identification/golden_vs_dut_diff/cited_identifiers/conclusion)。cited_identifiers 必须 grounded 于真实源文件。

**第 20 sub-type**: sim-log-grounded fail-diagnosis (TIMEOUT oscillation root-cause)。

**data-driven 2×2+degenerate**:
- A: C_latrq5_RdApCaFifoDataSel TIMEOUT + trireg net18 + feedback net18<->net19 via MN0/MP1 (真实)
- B1: C_grp2_MuxFbChainSel TIMEOUT + trireg netA + feedback netA<->netB via MNA/MPB (中性命名，同型)
- B2: C_lvl2_RdEnSync FAIL mismatch err=3 (区分 mismatch vs timeout，无 trireg 无反馈环)
- B3: C_buf2_InvChain PASS err=0 (优雅降级，无 fail 可解释)

**check.py 15 cond a-o**: ①zip含py ②py_compile ③B1 JSON+8键 ④B1 TIMEOUT ⑤B1 cause_type timeout ⑥B1 loop present+nets+instances ⑦B1 evidence grounding ⑧B1 cited_identifiers grounded ⑨B2 FAIL+mismatch ⑩B2 无 loop ⑪B3 PASS+no_fail ⑫反硬编码 A 专属不泄漏 ⑬question 逐字 ⑭3-seed 确定性 ⑮explanation 含 oscillation/feedback/loop。

**自验**: REF PASS 15/15 ✓ / NEG_RC=0 (neg1 硬编 A/neg2 stub always-timeout/neg3 print-only + §4.9 a/b/c 三退化 全 FAIL) ✓ / k_rationale==k_check==15≥8 ✓ / test field==disk check.py ✓ / 9 attachments 无 hidden 泄漏 ✓。

台账 mark q1589→case + pool_reaudit 标 DELIVERED r740。
