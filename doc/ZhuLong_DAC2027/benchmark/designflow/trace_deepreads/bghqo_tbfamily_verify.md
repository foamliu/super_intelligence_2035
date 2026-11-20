# 深读 bghqo · e0039602@hfeg0pkn002 · mc=386 · schematic_netlist

sid: 1793839606322_bghqo.messages.json · 254 msgs · 1.78MB · 2026-11-05
claimer: shard D #464

## 项目背景
`/home/e0039602/Documents/verilog_lib_trans_v2/`：verilog 网表→SystemVerilog 转换工具。
- `run.py --netlist final_merged_netlist_digitial.v --block-list block_name_digital.log --workers 6` → `outputs/result_map_*.txt`（279 module，每个含 `# ---- module: NAME` + `## 完整原文` + `## cell 转换` 块，部分 `[TIMEOUT]`）。
- `tb_family/`：55 个族测试台模板 `tb_<family>.sv`（inv/nand2/nor2/buf/and2/or2/xor2/mux2/...）+ `scripts/_familymap.py`（FamilyMap.map(cell) 三层命中：families_index.json → 名字前缀规则 → 兜底 None=NO_TBRef）+ `scripts/_run_one_shot.py`（构建 TB + xrun 仿真对拍）。
- `extract_converted_sv.py`：从 result_map 抽 `## cell 转换` 块写 AIoutNNN.sv（`--only-converted` 只写网表里有的；`[TIMEOUT]` 写成占位文本不进有效 module）。

## 用户意图（首轮 U0，A 档任务说明原文）
> 请你将outputs当中的 result_map_20261104_202610_c0ef.txt文件，他是用python3 run.py --netlist ... --block-list ... --workers 6 这个命令跑出来的结果，使用目录下的tb_family skill，对他进行检查并重写错误的

= 对 run.py 产出的 result_map，用 tb_family 族模板方法逐 cell 检查转换是否正确，重写错误的。

## agent 工作流（首个 produce，U0→A117）
1. 读 result_map + tb_family/SKILL.md + skill_tools + run.py + config + _FAIL_Report.md。
2. xrun 烟测（v23.09-s003 可用）→ 仿真对拍可行。
3. 写 `_verify_tbfamily.py`：parse_result_map → FamilyMap 命中 → 构建 TB（族模板 + 端口自适应 name-first/role-fallback）→ xrun 对拍 → PASS/MISMATCH。
4. 跑 57 个族命中 cell：41 PASS / 16 MISMATCH；分析后修端口适配器（name-first + role fallback）→ 46 PASS / 11 MISMATCH（11 全是 hierarchical/multi-phase 子电路，转换忠实镜像原文，非真错）。
5. 写 `_make_report.py` → `tbfamily_verify/_verify_report.md`（四态 PASS/RerunPASS/FAIL(DUT)/NO_TBRef + 每 cell 判定）。
6. **A117 用户接受**：核心结论「能用族模板验证的标准单元类 cell 全部正确，无需重写转换逻辑」+ 报告。

## 后续（U188+，超出首轮意图，不进本 case）
- U188「把 PASS 的四十几个仿照 AIout1105 格式写 AIoutTBPass」→ A209 交付 `AIoutTBPass.sv`（46 PASS 模块，celldefine…endcelldefine 块，2136 行）。
- U210+ 转向 rule_prompt X 安全 clk 合成 + simlib 金标准替换 AIout1105（22 模块）——独立子任务。

## 金标准（首轮用户接受产物）
`_verify_report.md`：279 module 分类（46 PASS / 11 MISMATCH / NO_TBRef / TIMEOUT 7）+ 每 module 判定。
`AIoutTBPass.sv`：PASS 模块的 `## cell 转换` 块按 AIout1105 格式（头部注释 + timescale + 每块 celldefine/endcelldefine）。

## 不可复刻
私有 `/home/e0039602/Documents` + 279-module 真实 result_map + xrun 仿真环境不可在沙盒复刻 → B-grade synthesized 自包含。

## 合成方案（schematic_netlist B-grade synthesized L2）
- 输入：`result_map.txt`（N module：`# ---- module: NAME` + `## 完整原文` + `## cell 转换` 块，部分 `[TIMEOUT]`）+ `family_spec.json`（family → 名字前缀规则 + 期望 primitive 名 + 端口角色集）。
- 候选写 `tbfamily_verify.py`：
  1. parse_result_map（按 `# ---- module:` 切块，标 TIMEOUT / 抽 `## cell 转换` SV 块）。
  2. family_map(name) 按 spec 前缀规则首匹配，无 → NO_TBRef。
  3. TIMEOUT 优先 → TIMEOUT；family 命中且有转换块 → 结构功能检查（转换块实例化 family 期望 primitive + 端口角色集齐全且匹配）→ PASS / MISMATCH；family 命中但无转换块 → MISMATCH。
  4. 输出 `verify_report.md`（四态计数 + 每 module 判定 + 总数）+ `AIoutTBPass.sv`（PASS 模块转换块按 AIout1105 格式：头部注释 + timescale + 每块 celldefine/endcelldefine）。
- A（可见）vs 隐藏 B：family 前缀规则、primitive 名、module 名/数、TIMEOUT/NO_TBRef/MISMATCH 分布全不同 → 反硬编码。
- check.py 子进程真跑候选 on B + 内嵌独立 parse+family_map+结构检查器重推导每 module 判定 + 期望 AIoutTBPass.sv 内容比对。
