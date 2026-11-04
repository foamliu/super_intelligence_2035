# Deepread: pjxhr — AutoCell TCL flow generator

- **session**: `1789612268376_pjxhr.messages.json` (miccao / hfeg0plg37, mc=340)
- **domain**: schematic_netlist
- **msgs**: 195 (108 user / 87 assistant), 946 KB

## 用户需求轮（A-faithful 截取）

**U#1 (msg0)** — 唯一提需求轮（逐字原文）:
> /autocell-tcl-flow-generator /home/miccao/autocell/black/pcell 这是我的管子的tcl，/home/miccao/autocell/black/netlist，这是cdl，生成对应的gds到/home/miccao/autocell/black下，禁止去找我别的配置文件，缺失的参数你自己想一个，不允许找我的配置文件，同时把缺失的参数列在一个文件里，文件名为loss_para.log，放在black目录下

U#2/U#3/U#4 均为 "go on"（继续，非新需求；不作 A 任务说明）。

## agent 工具链（关键产物）

1. **读 skill**：`/home/miccao/.cline/skills/autocell-tcl-flow-generator/`（pipeline.md / skeleton / scripts/validate_flow.py / references / DRAM 示例 flow）。
2. **读输入**：`black/pcell/*.tcl`（ntn/ntk/ptn/ptk 等 pcell 器件类定义）、`black/netlist/*.cdl`（543 个 cdl 网表）、grep 出器件模型名(ntn/ntn_m/ntn_lv/ntn_lvl/ntk/ntk_lv/ntk_hv/ptn/ptn_lv/ptn_lvl/ptk/ptk_lv)与 W/L 参数。
3. **生成 8 个 TCL flow 文件** 到 `black/flow/`：
   - `layers.tcl` — tech "default_tech"/planar，add_layer OD/PG/PG:NTAP/PG:PTAP/PGD/CT/NW/NSD/PSD/M0/M1/VIA1（GDS ld/dt 全部 INVENTED）
   - `layer_functions.tcl` — set_layer_function 语义角色
   - `viadefs.tcl` — CT_SD/CT_GATE/VIA1（cut_size 从 PCell contact 几何推导）
   - `globals.tcl` — set_global_net VDD/VSS/VPW(vbn)/VNW(vbp)
   - `rules.tcl` — min_width/min_area/min_spacing（全 INVENTED）
   - `place.tcl` — source pcell tcl + matched_template/nmos_template/pmos_template + 高度 3.0/pmos_y 2.1/nmos_y 0.9/unit_w 0.28
   - `route.tcl` — router 选项 + via 实例 + pin_template + 走线 grid
   - `run.tcl` — 主入口：source 7 个 tcl + glob *.cdl 自动发现 543 cell + folding_specs + cell 循环 + GDS 输出 black.gds
4. **生成 loss_para.log** 到 `black/loss_para.log` — 6 个发明参数分组（GDS 层映射/viadef/边界模板/设计规则/folding/走线 grid）。
5. **跑 validator** `validate_flow.py` → 通过（1 warning GDS 路径 → 修 `$case_dir` 后干净通过）。

## 后续（不作 A 金标）

- U#2 "go on" → agent 尝试真跑 autocell 生成 GDS：`autocell` 二进制 **segfault**（2024.12 & 2025.12 两个 Aether 版本均崩，dmesg 确认 core dump）。
- U#3 "go on" → 找到 `/home/miccao/work/autocell/`，继续排查。
- msg180: agent `rm -rf black/flow`（删自己生成的 flow 目录），转而用 `black/` 根目录下**已存在**的 run.tcl/layers.tcl（pre-existing，非本 session 生成）。
- U#4 "go on" → 末尾仍在找 autocell 二进制（msg193）。**GDS 从未生成**（autocell 崩溃）。

## 金标判定

- 用户**未明确接受**任何最终结果（trace 末尾无 "ok"/"good"/确认）；GDS 未产出。
- 但 agent 在 msg40-msg67 生成的 **8 个 TCL flow + loss_para.log** 是 skill 的具体可验证产物，且通过 validate_flow.py。
- **取金标 = agent 生成的 8 个 TCL flow 文件 + loss_para.log 的结构**（从 trace editor 内容重建为 config-driven 确定性生成器 gen_autocell_flow.py）。真实 AutoCell 二进制无法在评测沙箱跑 → L1-boundary 降级（读 config 出已实例化结构 TCL）。
- 本 case 标 `track: faithful`（U#1 逐字原文为任务说明），但金标为 B 档式合成（结构重建），因 trace 末尾无用户接受的最终产物。判分对**事实结构**（文件齐全/tech 名/层 GDS/viadef/folding/cell 发现/loss 分组/跨输入护栏/确定性），不对措辞。

## 资产

- A: `config_A.json`（default_tech/planar/black, ntn/ntk/ptn/ptk 12 类, OD/PG/CT 层, 7 cell, folding 1.534/1.394/2.762）+ prompt.txt(U#1 逐字) + task_brief.md
- hidden B: `config_B.json`（fin_tech/fin/red, nfn/nfk/pfn/pfk 8 类, FIN/GATE/CA 层, 8 cell, folding 1.8/1.65/3.1, 不同 global net vccd!/vssd!）+ hidden_manifest.json
- 判分只跑 B（跨输入测试）。

## check.py 15 条件 a-o

a zip 含 gen / b py_compile / c 跑 B 出 9 件非空 / d run.tcl 按序 source 7 tcl / e tech_name+output==B / f glob *.cdl+cell loop / g folding_specs B 类+宽度 / h layers B 层+GDS / i viadefs B 名+cut_size / j globals B 网 / k place B pcell+模板 / l loss ≥6 组+层/viadef 名 / m 跨输入 A 不泄 B 在 / n 3 seed sha256 一致 / o 退化三假全 FAIL

自验：ref PASS 15/15 / 4 neg ALL-FAIL distinct{empty→c, print_fixed_A→e, core_deleted→g(nfn), naive_no_layers→h(FIN)} / §4.9 三假(c/e/g) 3-distinct ✓ / k_rationale==k_check==15 ✓ / D.jsonl 77→78 行
