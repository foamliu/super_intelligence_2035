# 深读 · 0ox36 (alexli @ 10.129.2.13, mc=111) — schematic→hspice 网表抽取 · cds.lib 陷阱

**trace**: `/home/alexli/.cline/data/sessions/1794445370497_0ox36/1794445370497_0ox36.messages.json` (414510B, 78 msgs)
**user 原话**: 「可以抽取这个的网表吗 /proj/ddgoa/V0/workdir/alexli/BolinT_P2S_TB/TB_P2STOP_dq_noclktree_vintio/schematic/」
**domain**: spice_sim (presim 网表抽取, hspice) · **档**: A 档 trace-faithful → B 档便携化

## 任务结构
alexli 要从 Aether schematic 抽 TB_P2STOP_dq_noclktree_vintio 的 hspice 网表。assistant 用 `presim-automation` skill，调 `emy2netlist`（`/apps/empyrean/tools/aether_new/bin/emy2netlist`）。

## 核心洞察（case 化关键）
1. **cds.lib 是陷阱**：项目 `/proj/ddgoa/V0/cds.lib` 的 DEFINE 指向 **`/proj/ddgom`**（错误项目，路径不存在/不对）。直接信 cds.lib ⇒ emy2netlist 解析失败。
2. **正解**：不信 cds.lib，按真实物理库树 `/proj/ddgoa/V0/libs/` 重建 `lib.defs`（每个 DEFINE 名 → 真实路径），再加 testbench 设计库（`workdir/alexli/BolinT_P2S_TB`）。
3. **参考先例**：发现 `P2STopM5_netlist/lib.defs`（27 DEFINE，已修 TECHLIB→真实 release）+ 可用 run script，复用其结构。
4. **emy2netlist 调用**：`emy2netlist` 读 `lib.defs` + cell spec → 导出分层 hspice 网表。首次 SIGKILL（>120s 工具墙钟），改后台 poll，最终 **rc=0 "Successfully exported"**，输出 `TB_P2STOP_dq_noclktree_vintio.hsp`（68835B, 1688 行，~9s）。
5. **网表校验**：前半段叶子 subckt（`commonIP/*`、`TECHLIB/*`、`stdcells_am/*` 如 `P2sLSM5InvGFx6IP`/`invGT`/`nor2N`），结尾 `**TopDesStart … **TopDesEnd` 顶层含 DUT 例化。

## 交付物定义
`extract_netlist.py`：输 `<project_root> <out_dir>`，① 检测 cds.lib 陷阱（ddgom/缺失路径）② 按真实 libs/ 树 + workdir tb 库重建 `lib.defs` ③ 调 `bin/emy2netlist` 导出 hspice 网表 ④ 写 `lib.defs` + `<cell>.hsp` + `report.md`。

## case 化（B 档便携 fixture）
- 真实 sch.oa 是 Aether 二进制不可移植 ⇒ 用文本 `sch.oa` marker（列 leaf subckt + top 例化）+ mock `emy2netlist`（读 lib.defs，校验所有 DEFINE 路径存在且无 ddgom，读 sch.oa 发分层网表）
- A 可见 = proj_A（libs {stdcells_am,analog_ip,techlib_release}, workdir/alice/TB_P2S_TB, cell TB_P2STOP_demo, 种植叶子 invGT）
- B 隐藏 = proj_B（不同 libs {stdcells_io,analog_blk,techlib_core}, workdir/bob/TB_DDR_TB, cell TB_DDRTOP_demo, 种植叶子 nand2T）
- 判分 subprocess 在 B 跑候选 + 独立校验 lib.defs(无 ddgom/路径全存在/含所有真实库) + 网表结构(≥K subckt + TopDesStart/End + 种植叶子 + 顶层 cell) + cross-input guard(在 A 重跑抓写死)
- L2（subprocess 真跑候选 + 驱动外部工具 mock + 结构断言 + oracle 复算）
