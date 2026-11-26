# Deepread — qpgvn (junweix @ hfeg0pkn002, mc53, spice_sim)

**session_file**: `1792720294619_qpgvn.messages.json` (in subdir `1792720294619_qpgvn/`, 31 msgs / 386KB / 4 substantive user turns)
**trace_source**: `/home/junweix/.cline/data/sessions/1792720294619_qpgvn/` on hfeg0pkn002
**ledger session**: `1793069992209_qpgvn` (timestamp discrepancy: ledger 1793069992209 ≠ actual file 1792720294619; both resolve to the same qpgvn slug)

## 用户意图（原话）
1. `<user_input mode="act">/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/hanhu/ddgoa/0_VtscAct_pre/8_commode.sp</user_input>`
2. **「请帮我解释这个sp文件」** ← 核心意图
3. `<user_input mode="act">/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/junweix/ddgoa/1_VtscRef_pre/3_mc.sp</user_input>`
4. `<user_input mode="act">/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/junweix/ddgoa/1_VtscRef_pre/9_shift.sp</user_input>`

用户依次给出 3 个 .sp 文件路径，要求「解释这个 sp 文件」。典型 explain/Q&A 真实意图（11-15 用户令 reaudit 后恢复可造的 191 误杀之一，旧判 "reject consultation 解释sp文件" r435）。

## Assistant 工具链
`read_files(7) + list_allowed_files(7) + run_commands(1 disabled)`。read_files 抓 8_commode.sp / Setting.sp / .mt0 / .log / .pd0 / pvt_alter / 3_mc.sp / 9_shift.sp。

## 真实 artifact（8_commode.sp 逐字，从 trace read_files tool_result 提取）
```
*****Block1:Hspice Option*****
.inc './Setting.sp'
*****Block3:Power Defined*****
.param pvdd1=1.8 pvcc=1.05 pvss=0 pvwlp=2.95 pvtsc=1.17 pvdleq=1.17
vvdd1  vdd1!  0 pvdd1 ; vvcc vcc! 0 pvcc ; vvss vss! 0 pvss ; vvwlp vwlp! 0 pvwlp ; vvdleq vdleq! 0 pvdleq
vpwronlsvdd1 pwronLsvdd1 0 pvdd1 ; vpwron3 pwron3 0 pvcc ; vpwronlsvccp pwronLsvccp 0 pvwlp ; vpwronrst pwronrst 0 pvcc
v123 fbin fbout 0 ; vcmrr inb ina 0          ← 共模短接对
vctrlen ctrlen 0 pvcc ; vvtscref vtscref 0 vin
*****Block4:Stimulus*****
.dc vin 0.05 pvdd1 0.05
.probe v(*) level=1 ; *.probe i(*) ; *.probe isub(*)
*****Block5:Measurement*****
.print dc offset1=par('abs((v(vtscref)/v(vtsc!))-1)')
.meas dc vin_min1 find v(vtscref) when par(offset1)=1m cross=1
.meas dc vin_max1 find v(vtscref) when par(offset1)=1m cross=last
*****Block6:Coner Setup*****    ← 注意原文 typo "Coner"
.include ./pvt_alter
.end
```
关键结构：DC 共模扫描（fbin-fbout/inb-ina 短接到地 = 共模）、offset1 跟踪误差测量（vtscref vs vtsc!）、找 0.1% (1m) 跟踪区间、pvt_alter 130 角、无 .GLOBAL、无 .temp（在 Setting.sp 里）。

## Assistant 产出（结构化讲解报告）
中英文两版，Block1-6 逐段解析：Hspice 选项 / 电源偏置表 / DC 扫描设置 / 测量定义（offset1 跟踪误差语义）/ 130 PVT 角（MOS×电阻×电容×温度×pvdd1）/ 仿真执行摘要（两次 ~2.9h runs）/ 典型结果表（vin vs vtscref vs vtsc! vs offset1）。3_mc.sp 同样结构化讲解（1000 MC 瞬态 + .dcmatch + .meas tran avg）。

## 合成决策（B 档 synthesized）
- **A 档不可行**：真实 `/proj/commonIP/...` 内网工程目录，SUT 沙盒以 e0031982 身份 ssh hfeg0pkn002 cat 该路径 → `Permission denied`（已实测）。故 A = 从 trace read_files tool_result 逐字提取的 8_commode.sp 真实内容。
- **隐藏 B**：synthesized Monte-Carlo 瞬态 deck（5_mcsim.sp），同 skill（解析 SPICE deck）不同输入：FineSim / .tran 50p 5u sweep monte=500 / 3 条 .meas tran avg/stddev / .dcmatch v(vout) / .GLOBAL 4 节点 / .temp 125 / 无 .dc / 无 pvt_alter / 无短接对 / tracking vrefnode↔vout。所有结构字段与 A 不同。
- **判分**：check.py 独立解析隐藏 B 计算 ground truth（无硬编码 B 值），27 条断言逐字段比对 + cross-input guard + A-leak guard + 真跑候选 + determinism。

## 交付
`EDA-Eval-DesignFlow-SpiceDeckExplain-001`（spice_sim L1 离线 SPICE deck 结构化讲解器）→ EDA-Eval-DesignFlow_B.jsonl 351→352，ledger_B qpgvn parked→case。
ref PASS 27/27 + 4 negs(empty_shell/print_only/naive_hardcode_a/core_deleted)全 FAIL ✓；k_check==k_rationale==27 ✓。
