# h15ge → ayl62 — spice_sim PVT corner subset deck generator

> 深读记录：本轮(11-10 22:xx) shard-B 交付轮。原本按上轮 summary 计划用 h15ge，但
> 复核发现 **h15ge 已在 ledger line 229 标记为 case（EDA-Eval-DesignFlow-SlicerFbTimeOpt-001，
> 2026-11-06 交付）**——上轮 summary 的「h15ge CLEAN」是误判（peek 时用了未过滤的
> cand_spice_dom250 列表而非 diff 后的 unledg_spice250，h15ge 本就在 anchors 中）。
> 故弃用 h15ge，改从 unledg_spice250 的 29 个真正未入账候选中按 hspice 占比重筛。

## 候选筛选

unledg_spice250.tsv（29 un-ledgered，hspice-dominant top-250 diff）按 hspice count 取 top：
- ayl62 (sophiaw@hfeg0plg09, mc=46, hspice:105, ratio 0.31) ← 选中
- qe1va (e0025730@hfeg0plg49, mc=54, hspice:60) — peek：U#1「启动业务场景: 仿真与验证」泛化启动，75 次 run_commands 串行执行，无可提取确定性交付物，reject
- mx7xh (junweix@hfeg0pjn185, mc=77, hspice:68) — scp host 不可达，skip
- zwqbl (zhukaic@hfeg0plg58, mc=104, hspice:64) — peek：U#1「读取 skill /home/zhukaic/aether_skill/ota_skill/ota.md」+U#2「开始执行」skill 驱动，任务埋在 ota.md 里，可提取性差，reject

8 个候选 ledger_hits 全部 =0（grep ayl62/qe1va/mx7xh/zwqbl/hsrib/of6ff/8b8wk/kjibr 均无），确认真正未入账。

## ayl62 深读（sophiaw, 103 msgs, 403KB）

### 会话结构
- U#1 (msg0)：仿真与验证 Workflow 模板启动（泛化 scenario prompt，含元数据/目标/验收标准，非具体 produce 任务）
- assistant msg1-13：list_allowed_files/search_codebase/read_files 探查 /rundata/ieda_agent_test/weihan/v1_vddsoc/ 目录，分析出 9 个文件：model.sp(G4B_CIP_Model_L6_v0d5_t7, 8 MOS 角点 tt/ft/st/tf/ts/ff/ss/fs)、tck_clk.sp(119行主仿真)、tck_clk_function.sp、trim.sp、inc(30行仿真选项)、tck_clk_alter(779行/65 PVT 角点)、netlist(737行)、incFile_G4B_CIP、incFile_lp
- **U#2 (msg14) — CLEAN produce-task**：「请从tck_clk.sp 中选出10个corner，生成一个新的命名为tck_clk_10corner.sp。在/rundata/ieda_agent_test/weihan/v1_vddsoc/ 目录下，并且在同一个目录下运行tck_clk_10corner.sp 的仿真」
- assistant msg15-31：执行 produce
- U#3 (msg32)「Agent Policy 配置怎么修改」+ U#4 (msg36)「check my agent-policy.json」— 偏题咨询（不影响 U#2 的 produce 性质）

### 交付流（msg15-31，gold standard）
1. **选 10 个代表角点**（从 65 个 alter）：覆盖 6 MOS（tt/ff/ft/tf/sf/ss）× 3 温度（-40/85/130）× 3 电压（1.6/1.8/2.1）× 3 电阻（tt/ff/ss）。具体：alter1=tt/tt/85/1.8(标称)、2=ff/ff/-40/1.6、3=ff/ss/-40/2.1、4=ft/ss/-40/2.1、5=tf/ff/-40/1.6、6=sf/ff/-40/1.6、7=ss/ff/-40/1.6、8=ff/ff/130/1.6、9=sf/ff/130/1.6、10=ss/ss/130/2.1(最差慢速)
2. **生成 tck_clk_10corner_alter**（editor msg18）：10 个 .alter 块，每块 .LIB model/res + .temp + .param pvcc/pvdd1 + .LIB bjt/diode/nicap + .TITLE "mos,res,bjt,diode,nicap"
3. **生成 tck_clk_10corner.sp**（editor msg18）：基于 tck_clk.sp，**唯一差异** = `.include ./tck_clk_alter` → `.include ./tck_clk_10corner_alter`，保留 13 条 .meas + 全部探针 + .tran + .temp
4. **生成 runsim.sh**（editor msg29）：`#!/bin/bash`，hspice 优先（`hspice -i ${SP_FILE} -o ${OUTPUT_DIR}/tck_clk_10corner`）+ finesim 回退（`finesim -spice -i ...`），输出到 10corner_sim/
5. 仿真执行被阻：run_commands(policy 禁) / run_approved_command(脚本 0775) / SandBox MCP(离线) / spice-sim-runner skill(依赖 SandBox) 全失败 → 给手动命令

### 可提取确定性交付物
**PVT 角点子集 deck 生成器**：读 base.sp + full_alter + corner_select.json → 输出 out_alter(子集 .alter 重编号 1..K) + out_sp(.include 行改写) + out_runsim.sh(hspice/finesim 回退)。纯文本编辑，不真跑仿真。

## case 设计：EDA-Eval-DesignFlow-PvtCornerSubsetGen-001

- domain: spice_sim / synthesized / L1
- deliverable: pvt_corner_subset_gen.py（CLI 6 参：<base.sp> <full_alter> <corner_select.json> <out_alter> <out_sp> <out_runsim.sh>）
- 资产 A: base.sp(.temp 85, .meas WL7<3>/wl1_r<192>, .tran 10p 600n sweep WL_len 1024 2048 256, .include ./pvt_alter) + pvt_alter_full(20 .alter 块) + corner_select.json(orig=pvt_alter, out=pvt_alter_10corner, select [1,2,3,5,7,8,10,12,15,18], hspice, sim_10corner) + task_brief.md + output_format_spec.txt
- 隐藏 B1: 24 块 alter(不同内容/顺序), select [2,4,6,9,11,14,16,19,21,23], out=pvt_alter_10corner_b1, base .temp 25 .meas WL3<5>/wl2_r<128> .tran 20p 800n sweep WL_len 2048 2560 256
- 隐藏 B2(反硬码): 24 块 alter(同 B1 block 数 + 同 select_indices，但角点内容不同), out=pvt_alter_10corner_b2
- reference: pvt_corner_subset_gen_ref.py（stdlib only, parse_alter_blocks + renumber + rewrite_base_sp + gen_runsim）
- check.py 13 断言(a-m: zip含py/py_compile/B1 exit0三输出/.alter块数=10/重编号1..10/.TITLE匹配源/.include替换+orig缺席/.meas+.temp+.tran保留/runsim shebang+simulator -i+output_dir/反硬码B2≠B1且匹配B2源/跨输入A gold title缺席/omission orig名缺席/确定性3x sha1)
- subprocess 真跑 B1+B2+det×3，_expected 独立重算
- 自验：ref PASS 13/13 + 5neg(naive_empty/hardcoded_a/only_print/empty_shell/ref_core_deleted)全 FAIL ALL_NEG_FAIL=True + §4.9 三假(hardcoded_a/only_print/ref_core_deleted)全 FAIL + 断言门 k_rationale=k_check=13≥8 ✓ + test 字段与盘上 check.py 字节同步(sha1 b291efb51dcd92858a9c8139fef757040438a106, 16036B) + .75 Python3.7.1 stdlib OK
- claim+mark ayl62 case；jsonl B 244→245, ledger covered 245→246(spice_sim 197→198), claimed 1→0
