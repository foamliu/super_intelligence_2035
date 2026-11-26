# 深读笔记 — 1792495939340_13fwy — WaveView 激励提取 → HSPICE stimulus deck

- **session**: 1792495939340_13fwy.messages.json
- **user / host**: thqu @ hfeg0plg99（多 host: plg99/plg15/plg102/pkn003）
- **model**: deepseek-v4-flash (provider hefei / cxmt-deepseek-flash)
- **match_count**: 211；工具分布：644 hspice / 602 schematic / 421 netlist / 7 pyAether / 1 spectre
- **size**: 1.48MB / 264 msgs（threshold 内，本轮可深读+合成）
- **period**: 2026-10-20 ~ 10-23（completed）
- **cwd**: /home/thqu

## 用户意图演进（按 user 轮）
- [0] "可以帮我从waveview中提取出来激励吗" —— 初始模糊需求。
- [45] **核心需求轮（本 case 任务说明来源）**：给出网表路径 `/proj/ddgoa/V0/workdir/thqu/simulation/ddgoa_cmos_work_R_NegVssIdd_opt_qyh_schematic_ALPS/`，输入信号 `GrEn, SanEn2G, SapEn2GP, Ra16L<1:0>, Ra16H<1:0>, PwrOnLsVwlp`，WaveView 导出波形在 `/proj/ddgoa/V0/workdir/thqu/circuit_opt/R_NegVssIdd_opt_qyh/` 的 `si1.sp, si2.sp, si3.sp`，要求"帮我写一个激励"。
- [79] 补充映射：`sanen2gsec55, sapen2gp, pwronlsvwlpsec55` 三个对应 SanEn2G/SapEn2GP/PwrOnLsVwlp；要求写成 `pwl(0n pvcc 30n pvcc 30.1n 0)` 类紧凑形式；**pwr 有毛刺，拉平成固定电位 2.71**。
- [109] "其他的几个也写成PWL的形式" —— SanEn2G/SapEn2GP/PwrOnLsVwlp 也要紧凑 pwl（pwr 仍 DC）。
- [135] "Ra16H<0>,Ra16L<0>,Ra16L<1>,GrEn 也写成 VSanEn2G SanEn2G gnd pwl(0n 0 30n 0 30.1n pvcc 100000n pvcc) 这种形式" —— 全部紧凑单行。
- [153] "把生成的脚本/文件归类到 /home/thqu" —— 整理。
- [178/188/225/244] 后续 Q&A：电源域识别、vintcore、full-chip PVT、Z_power（与本 case 无关，未取）。

## assistant 工具链
- `skills` (waveview-fsdb-readerV2-2) → `list_allowed_files` 探目录 → `read_files` 读 si1/si2/si3.sp + 网表 → `editor` 写 `gen_stimulus.py` → `run_approved_command`(python-runner) 跑生成 → `read_files` 验证 stimulus.sp（761 行）→ 反复迭代紧凑 pwl 格式 → `org_files.py` 归类到 stimulus_project/。
- 关键产物：`/home/thqu/stimulus.sp` —— 8 个 V 源（SanEn2G, SapEn2GP, PwrOnLsVwlp(DC 2.71), GrEn, Ra16L<1>, Ra16L<0>, Ra16H<1>, Ra16H<0>），PWL 数据从 si1(grensec55→GrEn)/si2(ra16l)/si3(ra16h) 搬运，SanEn2G/SapEn2GP 紧凑 pwl，PwrOnLsVwlp DC 2.71。用户接受（无返工，仅格式精修）。

## .sp 文件格式（实测）
```
*** Custom WaveView SPICE PWL EXPORT (version T-2022.06-SP1 build Aug 20, ) ***
*** created at 17:15:07 on Tue Oct 20 2026 ***
Vgrensec55 grensec55 0 PWL(
+ 0.000000000000000E+00  6.208265403984115E-07
+ 1.006975000000000E-08 -7.552791794296354E-05
...
+)
```
si2 含 `Vra16l<0>...` + `Vra16l<1>...` 两块；si3 含 `Vra16h<0>...` + `Vra16h<1>...` 两块。解析须按块（到 `+)` 闭合）切分，否则跨块计数会重复。

## 金标准（用户接受产物）
stimulus.sp：8 V 源 + 设计输入名；GrEn/Ra16L/Ra16H 从 .sp 忠实搬运 PWL 点；SanEn2G/SapEn2GP 单行紧凑 pwl；PwrOnLsVwlp DC 2.71。pvcc=0.73（vcc! 0.73V）。

## 合成决策（B档）
真实 si*.sp 属 ddgoa 项目组，`/proj/ddgoa/...` 对 e0031982 **permission denied**，无法取原文附件 → 按 A 档规则 6（资产用真实附件原文）不可满足，故标 **B档 synthesized**：资产按 WaveView PWL EXPORT 原格式合成（sigmoid 上升/下降沿，点数/翻转时刻 A vs B 不同）。prompt 据 trace 用户轮[45]意图改写。判分对事实（PWL 点数忠实、翻转时刻 HSPICE 真跑、紧凑 vs DC、跨输入 A≠B）。

## L2 真跑设计
判分在 .75 跑 HSPICE（`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice` wrapper，非 hspice64 裸二进制）：toy testbench 每输入挂 1pF + .tran + .measure 量半 VCC 翻转时刻，证实激励把每个输入驱到正确时刻。net 名 `Ra16L<0>` 的 `<>` hspice 接受。
