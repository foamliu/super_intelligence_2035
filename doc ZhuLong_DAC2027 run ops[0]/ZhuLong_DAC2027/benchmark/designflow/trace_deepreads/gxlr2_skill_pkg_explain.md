# Deepread · gxlr2 (1793587429686_gxlr2) — skill 包功能讲解 + 使用 SOP

- **session**: 1793587429686_gxlr2  (trace 在子目录 1793587429686_gxlr2/ 下)
- **user**: shunlinp @ hfeg0pkn002  · **mc**: 71 · **domain**: spice_sim
- **trace size**: 540KB / 49 msgs (user×28 assistant×21) / 3 substantive user turns
- **旧判**: r435 parked "reject skill-install/demo Q&A" → r618 reaudit 复活 (新标准 Q&A/咨询 → 结构化回答 合法形态)
- **拟造**: `EDA-Eval-DesignFlow-SkillPkgCapabilityExplain-001` · spice_sim L1 离线 · B 档 synthesized

## 用户原话（3 turn）
1. `hi，你会装skill吗，帮忙装一下这个skill，/home/e0019581/skills_v0.2` — 装一个 skill 包
2. `这个skill能实现哪些功能，一个个解释演示一下` — 逐个讲解功能 + 演示
3. `我该怎么用呢，有SOP之类的吗` — 怎么用，有没有 SOP

## 助手实际行为
- list_allowed_files + read_files 探查 `/home/e0019581/skills_v0.2/` 结构 ⇒ 发现 6 个子模块 + INDEX.md
- read INDEX.md + 各子模块 SKILL.md + 关键脚本 (.il/.py/.sh/.sp/.json)
- 发现包**已部署**在 `/home/e0019581/yyl_testing/skills_v0.2/` (源包在 /home/e0019581/skills_v0.2/)
- 输出①安装完成确认报告(检查清单表)；②`skills_v0.2 功能全景`：6 个子 Skill 逐个讲解(功能/核心逻辑/演示/输出文件)；③`skills_v0.2 完整使用 SOP`(文档索引 + 前置条件清单 + SOP-A 无缺陷 + SOP-B 带缺陷 + SOP-C 从缺陷坐标 + 每步验收速查 + Troubleshooting + 实战建议)

## skill 包结构（6 个子 Skill）
| # | 模块 | 语言 | 角色 | 关键文件 |
|---|---|---|---|---|
| 1 | netlist_extract | SKILL (.il) | 抽 SPICE 网表 | extract_current_netlist.il |
| 2 | pwl_extract | SKILL (.il) | 抽 PWL 激励 | extract_pwl_stimulus.il |
| 3 | fault_inject | Python | 注入 4 类缺陷 (open/short/leakage/vth_shift) | run_fault_inject.py + defects_template.json |
| 4 | finesim_sim | Python+sh | 组装 SP + bsub 提交 | assemble_sim_sp.py + run_finesim_sim.sh + sim_template.sp |
| 5 | defect_loc | Python | SEM 缺陷坐标批量定位 | defect_coordinate.py + extract_coords_txt.py |
| 6 | circuit_extract_flow | 文档 | 全流程编排 (无可执行脚本) | SKILL.md |

## 完整缺陷仿真流程
```
[P1] defect_loc → [S1] netlist_extract → [S2] fault_inject → [S3] pwl_extract → [S4] finesim_sim
[Flow] circuit_extract_flow = 串联以上所有步骤
```
- SOP-A 无缺陷: S1 → S3 → S4
- SOP-B 带缺陷: S1 → S2 → S3 → S4
- SOP-C 从坐标: P1 → S1 → S2 → S3 → S4

## 关键真实参数（A 输入用）
- work_dir: `/home/e0019581/yyl_testing/`
- source_path: `/home/e0019581/skills_v0.2` · target_path: `/home/e0019581/yyl_testing/skills_v0.2`
- primary cell: lib=`ddcpb_top` cell=`Array24GTop` view=`schematic` timestamp=`20260911_111442`
- sim queue: `fqueue3` · sim temp: `45` · model lib: `/apps/imctf/models/10G5/...`
- defect_loc python: `/apps/local/bin/python3` (必须，非默认 python3)
- 4 defect types: open(1e9Ω)/short(1.0Ω)/leakage(10e6Ω)/vth_shift(value 如 30m)
- 验收 token: EXTRACTION COMPLETE / TEMPLATE GENERATED / [DONE] N fault(s) injected. / PWL EXTRACTION RESULT / [DONE] SP file assembled successfully. / [DONE] Finesim job submitted to queue:

## 隐藏 B 合成参数（cross-input guard）
- work_dir: `/home/e0024852/eva_testing/` · source: `/home/e0024852/skills_v1.0` · target: `/home/e0024852/eva_testing/skills_v1.0`
- package name: `skills_v1.0`
- primary cell: lib=`hbt_top` cell=`Lp5Top` view=`schematic` timestamp=`20261015_093022`
- sim queue: `spqueue2` · sim temp: `85` · model lib: `/opt/eda/models/22G7/...`
- defect_loc python: `/opt/eda/bin/python3`

## A 档不可行理由
真实 trace 是纯知识 Q&A + 已装包探查，无文件产物；skill 包在 hfeg0pkn002 工作站 SUT 沙盒无 Cadence/Virtuoso/GUI 不可达。取 B 档 synthesized：A 的 doc/ 为合成但真实风格的 skills_v0.2 包还原（保留真实结构/参数/路径），隐藏 B 为合成结构不同的 skills_v1.0 包。

## 判分形态
check.py 独立解析 hidden/doc/ 求 B ground truth + swap hidden/doc/ 进 workdir/doc/ 防背题。断言：cross-input guard (B≠A) + A-leak guard + 真跑候选(subprocess on B) + 确定性(3 rerun) + module_count==6 + 6 module names + 4 defect types + flow_order + 3 SOP variants + prerequisites(defect_loc python) + evidence_snippets。k=18。
