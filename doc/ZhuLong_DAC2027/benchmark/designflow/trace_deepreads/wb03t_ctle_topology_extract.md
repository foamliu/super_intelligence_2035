# 深读笔记 — wb03t (cwei / hfeg0plg93) — CTLE 原理图生成 → 拓扑解析 case

## trace 来源
- session_file: `1790487462826_wb03t.messages.json`
- user: `cwei`，host: `hfeg0plg93`，match_count: 691
- keywords: 268 pyAether / 231 hspice / 204 schematic / 95 netlist / 62 calibre / 42 spectre
- 400 msgs（261 user / 139 assistant），2026-09-27 单日会话

## 用户意图（逐字关键轮）
- U[0] SpiceAgent skill 入口索引（CP0–CP4 模拟电路设计 Agent，工具链 Aether/pyAether + FineSim + PDK TECHLIB）
- U[9] **帮我设计一个CTLE**  ← 提出需求
- U[180] 设计原理图放在 `spice_agent_test` 这个库下面
- U[205] **Aether 已经启动了，所有的设计都要在 spice_agent_test里操作，PDK 库的名字是 TECHLIB, 参考一下 golden ctle 的设计情况，总结一下目前状态**  ← 本 case prompt 取此轮
- U[239] 先搞定 TECHLIB 指向问题，然后全新开始在 spice_agent_test 库中生成一个 golden 类似的 ctle 原理图
- U[341/353] 仔细检查是否有 Aether GUI 会话和 spice_agent_test 库（该 aether 不是 home 路径下起的）
- U[381] `/proj/drvqa/V0/workdir/cwei` 这个路径下启动的 Aether
- U[393] **在 spice_agent_test 中直接生成 ctle 原理图**  ← 提出需求

> 注：U[669]/U[865]（指出 aether 而非 virtuoso / 改写 aether flow）属另一同用户会话（t1xjg=SkillToAether-001）的主题，本 trace 主题是 **CTLE 原理图生成**，不重叠。

## assistant 工具链（关键）
- `run_commands`：探活 Aether 工作目录 `/proj/drvqa/V0/workdir/cwei/`、读 `cds.lib`/`lib.defs` 确认 `spice_agent_test` OA 库 + TECHLIB 路径 `/proj/drvqa/V0/libs/TECHLIB_release/TECHLIB`
- 读 SpiceAgent skill 的 golden 参考：`/home/cwei/.cline/skills/SpiceAgent_Skill/aether/gen_ctle_skill_v1_scheme_aether.py`（V17 层次化：main CTLE 调 prog_tail + prog_tailnc，RS=170）+ `gen_ctle_skill_v1_tailcells_aether.py`
- 生成 `gen_ctle_all.py`（18607 字符，A[390]）写入 `/proj/drvqa/V0/workdir/cwei/`，含 3 个 cell：prog_tail / prog_tailnc / ctle_skill_v1
- 尝试 `aether -nographic -replay` / `-exec` 批处理跑 → 被 X11 display 阻塞 → 最终指示用户在 Aether GUI Python Console 执行 `exec(open("gen_ctle_all.py").read())`
- 会话止于 A[399]（无显式用户接受回执；金标准 = 该 gen_ctle_all.py 脚本本身，与 skill golden 一致）

## 金标准 CTLE 拓扑（取自 gen_ctle_all.py / 与 skill golden gen_ctle_skill_v1 一致）
层次化 3 cell，库 `spice_agent_test`，PDK `TECHLIB`：
- **prog_tail**：3× ntn_m 尾电流 MOS（Mtail0=12.45u/nf50, Mtail1=5.22u/nf21, Mtail2=7.23u/nf29）+ leg1/leg2 CMOS TG 开关（sw0_n ntn 3.46u/10, sw0_p ptn 6.92u/20, pd0 ntn 1.73u/5；sw1 同；g1=g_mt1, g2=g_mt2）+ pins drain/vdd/vbias/sw0/sw0b/sw1/sw1b/gnd
- **prog_tailnc**：同结构，尾 MtailNc0/1/2=5.27/2.11/3.16u(nf20/8/12)，vbias_name=vbias_nc，sw→swnc*，g1=g_mnc1,g2=g_mnc2
- **ctle_skill_v1（主 CTLE）**：
  - 输入对 M1/M2 = `ntn_lvio` w98.9u l0.1u nf286（M1.G→dinn, M1.D→outp, M1.S→srcp, B→gnd；M2.G→dinp, M2.D→outn, M2.S→srcn）
  - 负载电阻 RD1/RD2 = `RNPOLY2t` w0.13u l3.6u（RD1.PLUS→outp, MINUS→vdd；RD2.PLUS→outn, MINUS→vdd）
  - 退化电阻 RS1 = `RNPOLY2t` w0.13u l0.875u R90（PLUS→srcp, MINUS→srcn）
  - 退化电容 CS_A/CS_B = `ntn_lvio` w774u nf1276（G/S/D/B→srcp / srcn，MOS cap 接法）
  - 负载 MOS cap CP_MOS1/CP_MOS2 = `ntn_lvio` w4u nf10（G→outp/outn, S/D/B→gnd）
  - NC3 交叉耦合对 M5/M6 = `ntn` w15.93u nf46（M5.G→outp, M5.D→outn, S→sn5；M6.G→outn, M6.D→outp, S→sn6）
  - NC3 耦合 CCS_MOS = `ntn_lvio` w70u nf84（G→sn5, S/D/B→sn6）
  - 层次实例 Ptail1/Ptail2 = `prog_tail`（Ptail2.drain→srcp, Ptail1.drain→srcn + sw*/vbias/vdd/gnd），PtailNc1/PtailNc2 = `prog_tailnc`（drain→sn5/sn6）
  - 顶层 pins：vdd/gnd/dinp/dinn/vbias/outp/outn/vbias_nc/sw0/sw0b/sw1/sw1b/swnc0/swnc0b/swnc1/swnc1b
  - symbol：leftPins=[dinp,dinn,vbias,outp,outn,vbias_nc,sw0,sw0b,sw1,sw1b] rightPins=[swnc*] topPins=[vdd] bottomPins=[gnd]

## case 合成（B 档 synthesized）
- **任务**：写 `extract_topology.py`（pyAether 原理图脚本拓扑解析器），吃 `gen_ctle_A.py`，产出 `topology.json`（cells/instances/pins/connections 四元结构）。交付 `outputs/submit.zip` 含两文件。
- **判分**：L1-boundary（.75 沙盒无 spice_agent_test OA 库 / 无 TECHLIB，纯离线解析），check.py 17 条独立条件 (a)–(q)。
- **隐藏 B**：`gen_ctle_B.py` 单 cell `ctle_simple`（非层次化，nch_lvt/pch_lvt 器件，7 ports vinp/vinn/voutp/voutn/vdd/vss/tail_bias，R_src1/R_src2 RNPOLY2t + M_tail nch_lvt）—— 结构/取值/器件族均与 A 不同，cross-input guard 防硬编码 A 层次泄漏。
- **金标准** = `reference/CTLEAether-001/extract_topology.py`（真实解析器，复跑 A 与提交 topology.json 逐集合对账）。
- **domain**: analog_context（CTLE 模拟电路原理图）；**layer**: L1（离线 Python 解析）；**track**: B（synthesized reframe：把"生成 CTLE"转写成"解析 CTLE 拓扑"以便离线判分，保留 trace 真实 artifacts 与用户原话 prompt）。

## 自验
- ref reference_submit.zip → check() PASS（17/17）
- 5 negatives ALL-FAIL（distinct labels: fake_empty→c / fake_print_expected→m / fake_core_deleted→g / naive_a_only→n / naive_no_conn→l）
- §4.9 三假提交（fake_empty / fake_print_expected / fake_core_deleted）全 FAIL ✓
- 断言闸门：k_rationale=k_check=17 ≥ 8 ✓

## 备注
CTLEAether-001 reference 目录在本轮之前已存在于磁盘（check.py + assets + negatives + reference_submit 齐全），但未入任何 shard jsonl（未交付）。本 trace wb03t 即其来源；本轮 shard D 认领 wb03t → 自验通过 → 追加 D.jsonl 完成交付（不重复造轮子）。
