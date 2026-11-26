# deepread stub — mw3vr (1789371142448_mw3vr) · spice_sim · r432 claim

> 状态：**claimed, 待深读合成**（DEBT: 1）· r432 (2026-11-12 13:19)
> 路径（已实测可读）：`/home/sophiaw/.cline/data/sessions/1789371142448_mw3vr/1789371142448_mw3vr.messages.json`
> host: hfeg0plg09 (172.16.8.175) · user: sophiaw · match_count: 28 · domain: spice_sim
> keywords: netlist:115;hspice:63;schematic:35;cmos:13;pex:11;analog:8;virtuoso:5;aether:3 (spice_kw=63, density=0.25)

## 首条 user 意图（原文摘录）

「# AnasimPro SPICE 仿真全流程自动化

## 元数据
- 类型: Workflow
- 适用场景: 对集成电路设计执行 SPICE 仿真全流程管理（PVT 角点仿真、LSF 批量提交、测量数据收集、跨仿真对比报告）
- 执行环境: 烛龙内置工具 + SandBox MCP（EDA 环境操作）
- 创建日期: 2026-08-28 · 最后更新: 2026-09-04

## 目标
对指定的仿真目录，完成完整的 SPICE 仿真管理流程：搭建仿真目录结构 → 分析网表文件 → 生成 PVT 角点 alter 文件 → 构建 runsim 提交脚本 → 提交 LSF 作业并监控状态 → 收集解析测量数据 → 生成 Benchmark 对比报告。最终产出结构化的 JSON 状态报告和对比报告文件。

## 验收标准（用户自带 8 条 ⇒ 直接映射 check() k≥8）
1. setup-folder: status=ok, 目录含 alter/ backup_spice/ runsim/ logs/ + .hspice_panel_config.json
2. analyze-spice: status=ok, JSON 含 total_sp_files≥1, 每个 .sp 文件 includes/model_paths/has_alter/has_end
3. generate-alters: status=ok, total_alters≥1, 文件含 `.alter N` 语句
4. build-runsim: status=ok, runsim.sh 含 bsub 命令行, total_jobs≥1
5. submit-jobs: status=ok, runsim.sh 含 bsub/sh 命令行（提示用户手动 bash runsim.sh）
6. monitor-jobs: 通过 read_files 读 .out/.err 判断完成 / 提示 bjobs
7. （measure-collect，待深读确认完整条件）
8. （benchmark-report，待深读确认完整条件）」

## 下轮合成计划（DEBT 清付）

1. scp mw3vr.messages.json 全文到 workdir，解析全部 user 意图 + assistant 工具链 + 关键产物（.sp 网表 / alter 文件 / runsim.sh / measurement JSON / report）。
2. A 档 trace-faithful：用 sophiaw 原话作任务说明（不改写），assets 用真实 .sp 网表片段（从 trace 产物或同域样例构造同结构 B）。
3. hidden B：换不同 PVT 角点集 / 不同 .sp 网表（规模/取值不同，非换文件名）。
4. check() ≥8 条件，逐条对应用户验收标准 1-8；≥1 条真跑候选（解析 alter 文件的 `.alter N` 结构、runsim.sh 的 bsub 行结构）。
5. negative: naive stub (只 setup-folder 不做后续) / always-ok stub / 参考解删 generate-alters 核心 ⇒ 全 FAIL。
6. 自验：ref PASS + §4.9 三假 FAIL + negative_selftest 全 FAIL；.75 HSPICE/sandbox 跑候选。
7. test_rationale = `8 条断言：①…②…` 与 check() 条件一一对齐。
8. 追加 EDA-Eval-DesignFlow_B.jsonl + mark --status case + 日报。

## 风险

- mw3vr 是 workflow 规范式任务（用户给 DoD），assistant 实际执行链需深读确认是否真产出了所有 8 项产物；若 assistant 只做了前几步，B 档 synthesized 需补全。
- LSF bsub 在沙盒可能不可用 ⇒ check() 验 runsim.sh 结构（bsub 行存在 + total_jobs≥1）而非真提交。
