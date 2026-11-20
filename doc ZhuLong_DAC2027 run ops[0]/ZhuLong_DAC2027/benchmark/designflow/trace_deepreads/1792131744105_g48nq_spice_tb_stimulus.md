# trace deepread — 1792131744105_g48nq (spice testbench stimulus skill)

- **session**: 1792131744105_g48nq · user adaml @ hfeg0pkn001 (10.129.2.10) · mc=192
- **keywords**: hspice:1489 / synopsys:346 / schematic:219 / netlist:152 / pdk:140 / analog:63 / pyaether:43 / aether:10
- **cwd**: (cline session, desktop) · 102 msgs (70 user / 32 assistant) · 707KB
- **domain**: spice_sim (shard B)

## 用户意图（提出需求轮，A-档合规）
- **T0 (msg 0, mode=act)**: `[skill-creator] 帮我生成一个 skill…参考 /proj/drvsa/V0/workdir/adaml/drgqa_simulation/Lbx_sim_DQ_TX_schematic_ALPS/Postsim/DR9500_woCH_woFFE.sp, Curry_tes_DL_CDL_schematic_ALPS/Pre_IOlib/*.sp, Lbx_DL_CPAMP_TB_schematic_ALPS/Postsim/*sp 等目录下撰写的电路spice仿真激励文件，生成用于撰写电路testbench spice仿真激励的skill`。要求：激励高度结构化可复用；覆盖 simulator option / spice model corner / 电源电压 / 温度 / designer parameters / netlist / 后仿 SPF / analysis / probe / measurement / 输入激励波形与 pattern 与 config 信号 / .alter / sweep 等。
- **T40 (msg 40)**: 项目 m2701 的 spice model 目录是 `/proj/m2701/V0_DDR4/model/current/`，更新 skill 里 model 内容。
- **T64 (msg 64)**: 调用 skill 时发现没充分利用 EDA 仿真器自身能力（如内建 bisection 优化），反而用 sh 脚本做分析。要求：写激励和做分析时**首先检查仿真器是否有内建功能**来实现需求。

用户这三轮都是「提出需求/表达目标」型，未指出根因或给修复方案 → A-档合规。

## assistant 工具链
- read_files 读 DR9500_woCH_woFFE.sp / Curry_tes_DL_CDL / Lbx_DL_CPAMP_TB 真实 .sp 激励 → 总结结构。
- editor 创建/更新 `~/.cline/skills/spice_tb_stimulus/{SKILL.md, 00_INDEX.md, references/template_tran_io.sp, template_*.sp}`。
- T64 后：list_allowed_files/read_files 探 `/apps/synopsys/hspice/S-2023.12-SP1-1/hspice/demo/hspice/{bisect,ciropt}` 官方示例 → 读 dff_top.sp/dff_push.sp/ampopt.sp 验证内建 bisection/optimization 语法 → 新增 `references/builtin_analysis.md`（需求→内建功能映射表 9 类 + bisection 完整语法 + 内建优先决策顺序）+ 同步更新 SKILL.md 6 处 + 00_INDEX.md。
- 末态 (msg 101): 更新总结，skill 可用。

## 关键产物（trace 末尾用户接受的结果）
- `~/.cline/skills/spice_tb_stimulus/SKILL.md`（13-section 骨架 + 内建优先原则章节 + 验收标准 + 已知陷阱）
- `references/builtin_analysis.md`（内建能力映射表 + bisection/optimization 语法）
- `references/template_tran_io.sp` / `template_*.sp`（带注释的完整激励模板）

## 便携化与 case 抽取
trace 末产物是 skill.md（文档），属 skill-撰写类，非直接 sim 结果。但可抽取可复用 L2 内核：**写结构化 hspice testbench 激励 + 内建 .measure 提取 tpd(3级链 .tran trig/targ) + vtrip(单级 .dc sweep .measure when v(out)=v(in)) + 真跑 HSPICE**。foundry .sp/PDK 不可移植 .75，取 Synopsys HSPICE V-2023.12 demo apps/inv.sp 的 level-28 inverter 模型（agauss→定常均值）+ .subckt inv in out(w=10u l=1u)。候选交付 tb.sp（引用 inv 的通用激励）+ out.lis。隐藏 B 改 w/l → tpd/vtrip 不同，cross-input guard。

## .75 HSPICE 排雷（重要，可复用）
1. **`.inc`/`.include` 在 HSPICE V-2023.12-SP1-1 不注册 .subckt/.macro 定义**：include 文件被打开（无 unable-to-open 报错）但 inv 仍 not found。demos 的 subckt 全 inline（worst.sp 的 inv 在主文件 `.mac inv`，tlib3 只放 .tran/.op/.measure 续接）。→ check.py 须用 **concat-swap**，不可依赖 .inc 解析隐藏 B。
2. level-1 自写 `.model nch nmos level=1 kp=...` 在本 build 报 "Definition of model nch is not found"（未定位根因）→ 复用 demo level-28 模型可用。
3. 慢角 (B2 l=2u) 3 级链 tpd~1.5ns，`.tran` stop=1n → v(out) 不穿 2.5 → `tpd=failed`，须 stop≥5ns。

## case
EDA-Eval-DesignFlow-InvTripDelay-001 (spice_sim, B档 synthesized, L2, k=14)。ref PASS 14/14 + 3 neg FAIL + §4.9 三假 FAIL。.75 verify.py ~5.7s 一把过。
