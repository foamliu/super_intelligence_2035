# 深读笔记 — 1795597907386_oyqvh (chuanqiz@hfeg0pnd001)

- **trace**: `/home/chuanqiz/.cline/data/sessions/1795597907386_oyqvh/1795597907386_oyqvh.messages.json` (2.0MB, 814 msgs, 416 user / 398 assistant)
- **mc**: 532 · **domain**: analog_context (analog:705 / schematic:480 / cellview:464 / virtuoso:341 / verilog:179 主导)
- **keywords 主导**: analog, schematic, cellview, virtuoso, dbopencellviewbytype — D 域 schematic_netlist/analog_context

## 用户真实意图（多主题 session，选可合成主线）
用户(chuanqiz)在 Cadence Virtuoso / Aether 中以只读方式打开 analogIP 库的 cell schematic，逐实例读 pin→net 连通，**忽略内部信号，输出每个 cell 输出端口相对输入端口的逻辑真值表**，并最终批量覆盖整个库(2717 cell)。核心线程(U#5..U#10, idx51..324)：
1. U#5: "忽略内部信号，输出这个cell的输出端口与输入端口的逻辑关系：analogIP/CustomDlyNcCtrlIP/schematic"
2. U#6: "生成该 schematic 的门级网表"
3. U#9: "本cell输入输出真值表"
4. U#10: "给定项目的Library后能否读其下的所有cell的schematic view并给出输出与输入的逻辑真值表，并统一输出到一个文本中"

后段(U#11..)切到 LPDDR6 JEDEC 回归分析(Active.run / lpddr6_test.sv / cmd_cal / pattern_start / loadca)，与本域无关，不合成。

## 助手实现关键
- 用 SKILL `dbOpenCellViewByType(lib cell "schematic" nil "r")` 只读打开，`cv~>terminals` 取端口方向(input/output)，`inst~>instTerms` + `iterm~>net~>name` 取 pin→net 连通
- **分类** classify3: 按实例 cell 名子串判 LOGIC/ANALOG/MIXED/EMPTY/NSCH（含 inv/nand/nor/and/or/xor/xnor/buf/ff/latch/mux → logic；ptn/ntn/res/cap/nmos/pmos/bjt/osc/amp/bias/comp → analog）→ 全库 2717 cell：LOGIC=687 / ANALOG=1253 / MIXED=705 / NSCH=72
- **门级真值表验证**(代表性 cell `rsnand22Lx1_VblhIP`)：I0=nand2Lx1(Y1=¬(A1·Y2))、I1=nand3Lx1(Y2=¬(B2·B1·Y1)) → 交叉耦合 NAND = **RS 锁存器**（反馈结构），真值表分置位/复位/保持
- **发现误分类**：`InvVdd1VbnsX3IP` 名含 "Inv" 但实为晶体管级反相器(ptk/ntk_hv 实例，无数字门) → 仅靠 cell 名子串分类不可靠，应按是否含标准单元数字门判定
- 沙盒脆弱(SKILL 批量打开 schematic 频报 "Unknown SKILL error")，全量 687 cell 真值表未完成；交付了全库分类 + 代表性真值表示例

## case 合成（synthesized-reframe）
把"在 Virtuoso 中读 schematic 推真值表"(强依赖 Virtuoso DB) reframe 为 **spec-JSON 驱动的门级真值表提取器** `extract_truth_table.py(spec)->report.json` —— 纯 Python 结构化判分，无真实 EDA 二进制依赖。
- **A**(visible) spec_A.json 3 组合 cell：CarryGenIP(全加器 SUM=A⊕B⊕CIN/COUT=AB+CIN(A⊕B), 8 行) / Mux2DiffIP(mux2+inv, Y=S?D1:D0/Yn=¬Y, 8 行) / AndOrInvIP(AOI22 Y=¬(AB+CD), 16 行)
- **hidden B**(token-structurally 不同) spec_B.json 3 cell：Parity4IP(4 位奇偶 ODD=P0⊕P1⊕P2⊕P3/EVEN=¬ODD, 16 行) / **LatchMuxIP**(mux2 输出反馈回自身 B 输入 on net Q → **时序反馈**, sequential=true/truth_table=null) / Nand3ChainIP(Y=¬(ABC), 8 行)；不同库(ioIP)/cell 名/net 前缀(m_)/inst 前缀(J)
- **reference** `extract_truth_table.py` spec 驱动通用实现(8 门语义表 + 实例依赖图环检测 + 拓扑序仿真 + 反馈 net 识别 + malformed 收口)
- **check.py 17 conds(a-q)**：独立 GT 门级仿真器复算真值表逐组合比对(a zip ②b py_compile ③c A valid ④d A 3 cell 名 ⑤e CarryGenIP 非时序 ⑥f 8 行 ⑦g SUM ⑧h COUT ⑨i AOI22 Y ⑩j mux Y/Yn ⑪k 全 A 非时序 ⑫l B valid ⑬m Parity ODD ⑭n Nand3 Y ⑮o Latch 反馈+null ⑯p 反硬编码源码无 A token ⑰q malformed→valid=false)
- **LIVE-NA**(deliverable=Python 脚本, check 跑候选+独立复算, 无真实 EDA 工具二进制依赖) judge_layers=[L0,L1] 无 check_live
- **自验全绿**：ref check.py on reference_submit.zip → PASS 17/17 + negative_selftest 4 neg ALL-FAIL distinct first-fail{c,f,m}(§4.9 trio: empty→c/print_only→c/core_deleted→f + hardcode_a→m) + SKIP_RUN=1 workdir leak 自检通过 + 3-way sha sync(disk==JSON test==metadata.check_sha256=dbd579ab... size 14161) + k_check=17=k_rationale=17 + 框架 auto-build jsonl D 602 case 含本条
