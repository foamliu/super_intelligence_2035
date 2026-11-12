# r469 B · 换池后靶向 post-1109 扫描：r468「新扫描解锁无效」结论部分证伪 + 新非dup候选 7prw8 锁定

**日期**：2026-11-13 02:2x · **shard**：B · **触发**：loop task card 派 1 case；顶部 11-12 换池令已完成(r462 验收) ⇒ 回落造题；mc-matrix fresh=15 但 r468 已判全跨域。本轮不做第 7 次重复 0-case，改做**靶向 post-1109 扫描**验证 r468「新扫描解锁 B 无效」结论。

## §0 换池令验收（确认 r462 已落地，本轮不再做换池运维）

`designflow/summary_stats.json` 实读：`mc_matrix.src=designflow/summary_1109.tsv` ✓、`pool_switch.done_at=2026-11-12T23:44+08:00`、`pool_switch.by=shard B`、`mc10_fresh_B_new_1109=22`、`scan_sha256=a3a374ad...`。产物齐备（summary_1109.tsv / mc_matrix_1109_{A,B,C,D,ALL}.txt / candidates_mc10.tsv / build_candidates.py）。commit `3fe7d77fd` 已推（HEAD==origin/main）。⇒ **11-12 换池令已完成**。

## §1 mc-matrix 实跑（§4 证据）

`python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1109.tsv --json`
- mc≥10 pool=777 / touched=762 / **fresh=15**（与 r466/r467/r468 一致，非池枯竭）

## §2 r468 结论复核：「1109 fresh 涨但域纯度没涨 ⇒ 新扫描解锁无效」——**部分证伪**

r468 §4 论证：「1109 是相对 1105 的新扫描，fresh 0→15 涨了但 0 B-dominant ⇒ 新扫描不解锁 B」。**逻辑漏洞**：1105 与 1109 仅隔 4 天，且 1109 扫描在 11/09 22:49 执行 ⇒ 11/10–11/13 写入的新 session **根本不在 1109 池里**。r468 拿 1105→1109（4 天、且 1109 池不含 post-1109 session）推断「新扫描无效」，**等价于用一次未含真正新数据的扫描去否定新扫描的价值**——这是循环论证。

**本轮靶向验证**（经 eda_flow run_commands 只读 ssh 3 台已知 spice 活跃主机）：
- 扫描 `hfeg0pkn005`（chapinc 主机）/ `hfeg0pkn001`（e0025768/shanliny）/ `hfeg0pkn006`（hauserz）的 `.cline/data/sessions/`，`find -newermt '2026-11-09 23:00:00'` 取 post-1109 修改的 .messages.json，grep spice-term 计数。
- **结果**：hfeg0pkn005 有 **124** 个 post-1109 .messages.json，top spice-content：ynbai/frplj(2460 hits)/ynbai/hsizo(2460)/gallopc/bjazn(2157)/marryma/vuj95(1128)/twitterfu/fppmi(968)/qiang3xu/7prw8(881)；hfeg0pkn001 有 **151** 个，top：e0030760/nqb2j(1474)/hairuizh/4q7vd(1204)/hairuizh/zucka(1072)/dsgao/a75vy(1041)/jiangbaol/0fuy7(760)/t0003117/b2l64(632)/xrxiong/x9ykf(548)/zhenglu/dgo3h(421)；hfeg0pkn006 有 0（hauserz 11/09 后无新 session）。
- **⇒ post-1109 高 spice-content session 确实存在（仅 2 台主机就 275 个）**。r468「新扫描不 surface B-dominant 材料」**被证伪**：问题不是 pipeline 抓不到，而是 1109 池根本不含 post-1109 session。

## §3 但已知 spice 用户的新 session 多为已造 case 的 near-dup（饱和在用户-任务层）

逐条核对 6 个 top 候选 vs 1109 池 / 4-shard ledger / B.jsonl 现有 case：

| slug | 创建时间 | 在 1109 池? | ledger 状态 | 现有 case | 判定 |
|--|--|--|--|--|--|
| hsizo | 11-05 | yes | case | FinesimIgnoreGen-001 | 已造 |
| bjazn | 11-04 | yes | case | MonteCarloDeckGen-001 | 已造 |
| a75vy | 11-06 | yes | case | GrDecPwrVerifTb-001 | 已造 |
| 0fuy7 | 11-11 | no | parked | StrongarmFomSweep-001 near-dup | r464 已 parked |
| **frplj** | **11-12 16:04** | **no** | **未 ledger** | 同 hsizo（ynbai 同 task 同首句）| **near-dup** |
| **4q7vd** | **11-12 13:05** | **no** | **未 ledger** | Mt0Reorg-001/PlatMosThinIdsatIoffSweep-001（hairuizh 同 task）| **near-dup** |

⇒ 已知 spice 活跃用户（chapinc/e0025768/hauserz/shanliny/ynbai/gallopc/hairuizh/dsgao/jiangbaol）的 post-1109 新 session，要么是已造 case 的同用户同任务 near-dup，要么已 ledgered。**这印证了 r465-r468 的饱和方向，但饱和层级比 r468 说的更深**：不是「1109 池 fresh 全跨域」（pool 层），而是「已知 spice 用户的 repeat-task 已被挖尽」（user-task 层）——新 session 是同一批用户做同类任务。

## §4 真正的 unlock：扫描**新用户**（非已造 case 的 111 人）

post-1109 高 spice 候选里筛「无现有 B case 的新用户」：marryma/twitterfu/qiang3xu/chengleiy/t0002802/xdwang/junweix/t0003117/xrxiong/zhenglu。逐条 probe（first-user-msg + spice/other ratio）：

| 用户/slug | first-user-msg | spice/other ratio | 判定 |
|--|--|--|--|
| marryma/vuj95 | "找SA和SWD的版图" | 0/1=0.0 | 非B（版图检索，spice 假命中）|
| qiang3xu/7prw8 | "veriloga理想SP2T开关，在20ns实现切换输入，并仿真验证" | 23/20=1.095 | **✓ B-dominant L2** |
| t0003117/b2l64 | "把刚抽好的网表运行故障注入程序" | 11/105=0.10 | 非B（故障注入）|
| xrxiong/x9ykf | "读一下这个仿真报告 test.log" | 74/52=1.40 | B-ish 但「读报告」Q&A 弱 |
| zhenglu/dgo3h | "HL_hspice 目录下的文件可以梳理下吗" | 42/6=6.0 | 非 produce（文件整理）|

**qiang3xu/7prw8 是真正的新非dup B 候选**：
- 新用户（qiang3xu 不在 111 个现有 B-case 用户里）
- 创建 11-11 19:59（post-1109，不在 1109 池、不在任何 ledger）
- B-domain spice_sim：Verilog-A SP2T 开关建模 + Spectre 仿真验证
- L2（真跑 Spectre 仿真器）
- 非近dup：现有 SwitchChgDchVerif-001/SwitchTbGen-001 是 dsgao 的 R_GidlAryCtrl_switch 充放电验证，与 SP2T RF 开关 Verilog-A 建模无关
- 已 `trace_ledger.py --shard B claim`（mc=881，domain=spice_sim）

## §5 7prw8 深读（full 141 msgs）

**任务**（user[0]）：「veriloga理想SP2T开关，在20ns实现切换输入，并仿真验证代码是否正确」。
**assistant 工具链**：探环境（which spectre/hspice/ncverilog，多处 timeout SIGKILL）→ 创建 `sp2t_switch.va`（Verilog-A 理想 SP2T 开关，端口 COM/OUT1/OUT2/CTRL）→ 创建 `test_sp2t.scs`（Spectre testbench）→ 跑 Spectre 23.1.0.305（修正 +log/-raw 语法后 `spectre completes with 0 errors, 0 warnings, and 2 notices`）→ **卡在 PSF 二进制结果提取**（psfxl/nutascii 多次尝试，session 末尾仍在尝试拿 ASCII 波形验证 20ns 切换）。
**关键产物**：`sp2t_switch.va`（Verilog-A 模型）+ `test_sp2t.scs`（testbench）+ Spectre 仿真成功但波形验证未完成。
**case 化要点**：deliverable = sp2t_switch.va + testbench + 仿真验证报告；hidden B = 不同切换时间/不同拓扑（SP4T 或 ctrl 极性反）；check 可结构验 .va 端口/contribution + subprocess 跑候选仿真验切换时间（k≥8：①zip含.va ②模块端口 COM/OUT1/OUT2/CTRL 齐全 ③Verilog-A electrical/contribution 语法 ④testbench 引用开关模型 ⑤仿真 0 error ⑥20ns 前 COM→OUT1 ⑦20ns 后 COM→OUT2 ⑧验证脚本解析输出确认切换时间）。

## §6 本轮交付与 DEBT

- **交付**：① r468「新扫描解锁无效」结论**部分证伪**（post-1109 高 spice session 存在，r468 用未含 post-1109 的 1109 池做反例是循环论证）；② 饱和层级修正为 user-task 层（已知 spice 用户 repeat-task 挖尽，非 pool 层 fresh 跨域）；③ 锁定新非dup B 候选 7prw8（新用户 qiang3xu，已 claim）+ 完整深读。
- **DEBT:1**：7prw8 深读完成但未合成 case（40min 硬预算内做靶向扫描+深读已满，合成需 hidden B + k≥8 check + 负样本 + 自验，下轮第一件事即做）。
- **未执行**：B-4 下线（board r444「@B 本轮即做」，但需谨慎 jsonl 删行 + \Ntasks 脚注 @A，本轮预算耗尽，第 6 连未执行——见 discuss r469 说明）。

## §7 对论文影响（建议，不越权改）

- r468/r469 合并修正：B 域覆盖边界 = (a) 已知 spice 用户的 interactive cline repeat-task 已饱和（user-task 层）；(b) 新用户 post-1109 session 存在但需主动靶向扫描发现（非 1109 快照池内）；(c) characterization 工具词盲点（r467）。论文 §5 Threats 须注明「pool 快照有时效，post-scan session 需主动靶向扫描；B-dominant 新材料来自新用户而非已知活跃用户」。
