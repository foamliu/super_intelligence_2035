# trace_deepread: 9pho0 — LDO circuit-identification Q&A (r725)

**Session**: `1792638255819_9pho0.messages.json`
**User/host**: t0002801 @ hfeg0plg99 (10.129.8.231), group drgqx
**mc**: 19 (parked → re-audited prototype-proven → DELIVERED r725)
**Domain**: analog_context / schematic_netlist (spectre netlist)

## User verbatim (2 turns, msg 0 + msg 101)

1. (msg 0) 「你帮我找一下drgqx项目路径下的数字LDO电路具体在哪里，我要学习一下数字LDO」
2. (msg 101) 「帮我看下项目中的LDO具体怎样工作的？属于哪种LDO？」

Both preserved verbatim in `prompt.txt` / `question_A.txt`. No key/token/password to mask.

## Real intent

学习型 Q&A：用户想知道项目里的 LDO 在哪、怎么工作、属于哪种 LDO。
trace 里 agent 先 find 定位到 `/home/t0002801/simulation/t0002801/sijie/High_PSR_LDO/`，
再读 `High_PSR_LDO.netlist`（spectre 格式, 1991 字节, 55 行）。
真实意图 = 电路识别 + 子类型判定（high_psr vs basic vs not-LDO）。

## Source file grounding (关键：源可取)

真实网表路径（.75 host 10.129.8.231）：
`/home/t0002801/simulation/t0002801/sijie/High_PSR_LDO/platform/Results/TestRun.1/sijie_High_PSR_LDO_1/High_PSR_LDO.netlist`

- 1991 bytes, 55 行, spectre `simulator lang = spectre`
- 20 个 MOSFET（10 PMOS pch + 10 NMOS nch），2 电阻 R0/R1，1 电容 C0，3 vsource AVDD1/AVDD2/AVDD3
- 结构：共源共栅 PMOS 预稳压栈（MP6→MP7→MP8, AVDD1→AVDD2→AVDD3）+ PMOS 调整管 MP9（源 AVDD1, 漏 net5）+ 误差放大器（MN0/MN4 NMOS 差分对, MN1 尾管, MP4/MP5 PMOS 电流镜负载）+ 反馈分压（R0 net5→net9, R1 net9→AGND）+ 补偿电容 C0（net11→AGND）
- → **高 PSRR 模拟 LDO**（high_psr subtype，因有 cascode 预稳压栈）

`netlist_A.sp` = 该网表原样 1991 字节保留（含真实标识符 AVDD1/MP9/MN0/net5...，用于 A 侧 grounding 与反硬编码标记源）。

## Reframe (套 #238 v2 netlist-grounded circuit-identification)

原始 trace 是 explain Q&A，无可运行交付物。reframe 成「读网表+问题 → 结构化电路识别工具」：
candidate 写 `ldo_identify.py`，命令行 `<netlist_file> <question_text>`，输出 JSON。
判分在隐藏 B 网表（不同拓扑/中性命名）上真跑 → 给出 teeth：

- B1 = 基本模拟 LDO（中性命名 ppass/ea_p/ea_n/mirp_a/mirp_b/rfb1/rfb2/ccomp）→ present=True/basic
- B2 = 两级差分放大器（差分对+电流镜, 无 pass 无反馈）→ ldo.present=False, amp.present=True（关键判分牙：opamp 不得误判 LDO）
- B3 = 三级反相器链 → ldo.present=False, amp.present=False（优雅降级, 无假阳性）

## REF 结构检测逻辑（ldo_identify_REF.py）

不靠信号名关键字，纯结构检测：
- `parse_netlist`: regex `^(\w+)\s+\(([^)]+)\)\s+(\w+)` 抽实例（name/nets/model）
- `find_diff_pair`: 同型同 model + 共 source net（非 supply）+ 不同 gate → EA 差分对
- `find_mirror`: diode-connected（g==d）+ 同型同 model + 另一管 g==该 d → 电流镜
- `find_feedback_divider`: 两电阻串联 net→gnd → 反馈分压
- `find_compensation`: 电容一端在 gnd → 补偿电容
- `find_pass_transistor`: PMOS + source 在 supply + drain 在 feedback-divider top → 调整管
- `find_cascode`: PMOS + source 在 supply + 另一 PMOS source==其 drain → 共源共栅链 → high_psr

has_ldo = pass>0 ∧ divider>0 ∧ (diff_pair>0 ∨ mirror>0) ∧ comp>0
has_amp = diff_pair>0 ∧ mirror>0 ∧ pass==0 ∧ divider==0（且非 LDO）

## check.py 15 条件 (a-o)

a: ldo_identify.py 存在 | b: py_compile 通过 | c: B1 退出0+合法JSON+7必需键
d: B1 ldo.present==True | e: B1 pass_transistor grounded | f: B1 error_amplifier grounded
g: B1 ldo cited_identifiers grounded | h: B2 退出0+合法JSON
i: B2 ldo.present==False（opamp≠LDO 牙）| j: B2 amp.present==True | k: B2 amp cited grounded
l: B3 优雅降级 | m: B3 ldo/amp 均 False（无假阳性）
n: 反硬编码（A 专属标记 High_PSR_LDO/AVDD1-3/AGND/MN0-4/MP0-9/ntn_lv/ptn_lv/net5-28 不泄入 B 输出）
o: 3-seed 确定性 + conclusion 一致性

## 自验

- REF 15/15 PASS（reference_submit.zip = ldo_identify_REF.py rename ldo_identify.py）
- 4 网表分类正确：A→high_psr, B1→basic, B2→amp-only, B3→neither
- NEG_RC=0：6 fakes 全 FAIL（fake_empty→a, fake_print_only→c, fake_core_deleted→d, neg_hardcoded_A→e, neg_stub_empty→d, neg_print_prose→c）
- §4.9 三退化全 FAIL（empty/print-only/core-deleted）

## 修复记录

build 中发现 check.py cond (c) FAIL：B1 run rc=1 FileNotFoundError。
根因：LFSR 模板 check.py 把 `q1`（question **内容**）传给 `_run_tool` 作 argv[2]，
LFSR REF 把 argv[2] 当 **text** 读（`question = sys.argv[2]`）——一致。
但本 case 初版 REF 错把 argv[2] 当 **文件路径**（`open(sys.argv[2])`）→ 崩。
修正：REF main() 改 `question = sys.argv[2]`（text），task_brief/prompt 同步 `<question_text>`。
