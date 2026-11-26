# r662 deepread — yongk1li @ hfeg0pkn002 (10.129.2.11) · session 1789710184698_xbtsx · mc77 · physical_verify

## trace 概览
- 85 msgs, 1 real user task chain (U#0 是 identity Q「你是什么模型」ignore).
- 工具链：list_allowed_files → read_files → editor (写 ~/bin/idd_to_ipf_flow.py) → run_approved_command (py 语法校验)
- 用户接受状态：**未明确接受**——assistant 多次误读 path 需求，用户三次骂「傻逼」，会话末尾用户质疑「你是 glm5.2吗」后结束。属「真实意图清晰但交付笨拙」型 trace。

## 用户真实意图（核心，逐字）
- **U#10**：「/proj/drcoa/.../white_box_cell/idd_to_ipf_flow.p 看看这个脚本是干嘛的」→ understanding (analysis)
- **U#24**（produce-task，A档合规——提出需求，未给根因/修复方案的全部细节）：
  > 「1. 不许兼容 老功能：
  > 2.CSV 里 cell 名都是小写（bcenterca），但规则里写的是 BCenterCA，直接 in 比较匹配不上。
  > 需要在 apply_spec 里做大小写不敏感比较：」
  - 需求1：删除旧配置兼容代码（TARGET_LEVEL / TARGET_CELLS / TARGET_FATHER_CELLS + main() fallback 分支）
  - 需求2：在 apply_spec 中做 cell 名大小写不敏感比较（CSV 小写 vs 规则混合大小写）
- **U#65/U#69/U#75/U#79**（follow-up path 配置，逐步纠正 assistant）：INPUT_DIR / OUTPUT_IPF 改为绝对路径 `/proj/drcoa/V0/workdir/yongk1li/simulation/DDR5TOP_4_channel_channel_gds_only/white_box_cell/IDD` 及对应 output.ipf。

## 脚本功能（idd_to_ipf_flow.py, 260 行，gold 在 ~/bin/）
IDD CSV → IPF 功耗文件生成，用于 Totem-SC **Signal EM**（信号电迁移可靠性分析）流程：
- 读取目录下所有 IDD CSV（每文件 = 一个 power domain）
- 按 IDD_THRESHOLD 筛选 tlc idd > 阈值的 domain
- build_children_map + get_level_instances 逐层展开到 target_level（leaf_fallback 补偿叶子）
- OUTPUT_SPECS 多条规则，每条 {level, father, include, exclude}；多 spec 间 captured_hdls 去重
- apply_spec：father/include/exclude 对 cellName 比较 (**gold 已修为 case-insensitive via _to_lower_set**)
- 可选 GDS 流式提取 cell 名做大小写纠正、功耗归一化、white_box_cells 输出
- POWER_DOMAIN_VOLTAGES 电压表

## gold 状态
- ~/bin/idd_to_ipf_flow.py = assistant 分块 editor 写入的「最终版」，但文件在 line 260 处截断于 apply_spec 内部（`idd = float(row["idd"])` 之后无 return / 无 main()）→ **gold 不完整**，assistant 的交付是 broken 的。
- 但用户意图（case-insensitive matching + 删 legacy + 绝对路径）清晰可重构成正确解。

## 拟造设计（B档 mock-behavioral reframe）
- 真实 idd_to_ipf_flow.py 依赖 GDS 二进制流 + Totem-SC 环境（沙盒不可达 + 产物不可独立校验）→ reframe 为通用纯 stdlib `idd_to_ipf_converter.py`：
  - CLI：`idd_to_ipf_converter.py <input_dir> <config.json> <output.json>`
  - 读 IDD CSV（instHdl/parentHdl/cellName/idd/power/power_pin），build hierarchy，level expansion，apply OUTPUT_SPECS（**case-insensitive father/include/exclude**），IDD_THRESHOLD domain 筛选，输出结构化 JSON（domains/output_groups/summary）
  - **无 legacy TARGET_LEVEL/TARGET_CELLS/TARGET_FATHER_CELLS**（用户需求1）
  - **case-insensitive matching**（用户需求2，核心 computable predicate）
- 新子型 `idd-to-ipf-case-insensitive-spec`（distinct vs r661=cell-list-layout-planner / r660=spf-rcc-net-cap-structured-extract / r658=netlist-to-schematic-builder）。
- asset A：idd_csv_A/（trace 风格 cell 名 ddr5top/bcenter/bcenterca/dl_dlltop）+ idd_to_ipf_flow_A.py（trace 原物作 schema 参考）+ config_A.json + prompt.md（用户原话 U#24+U#75）+ task_brief.md。
- hidden B：idd_csv_B/（不同 cell 名 topchip/gridcore/gridcoreca/wldriver/arrctl/senseamp/decblk + 3 domains 2 kept 1 skipped by threshold）+ config_B.json（father="GridCore" 混合大小写，include=["SenseAmp","DecBlk"]，exclude="GridCoreCA"）— 反硬编 A 档 cell 名/条目数/threshold。
- hidden B2：退化（1 domain, 1 cell, threshold=0, 1 spec level=1）— 击败硬编 instance count。
- check() 预估 16 条件 a-p：zip+compile / B 跑通+合法JSON / 顶层键 / threshold domain 筛选 / case-insensitive father 匹配 / case-insensitive include / case-insensitive exclude / level expansion 正确 / dedup 跨 spec / summary 计数 / 电压表 / 确定性 / AST 无 legacy 标识 / AST 无 A 档专属字面量 / B2 退化反硬编 / 输出 instance idd_sum 聚合。

## 资产可达性
- ~/bin/idd_to_ipf_flow.py 经 ssh 10.129.2.11 e0031982 身份可达（已读，260 行 broken gold）。
- /proj/drcoa/.../IDD CSV 实际数据未取（沙盒路径 + 用户私有），reframe 用合成 CSV（结构同 trace）。

## 契约
- mode=design_flow, entry_point=outputs/submit.zip, test=check(deliverable, workdir) 双参
- trace_source: {user: yongk1li, host: hfeg0pkn002, session_file: 1789710184698_xbtsx.messages.json, match_count: 77, real_task_summary: "modify idd_to_ipf_flow.py: remove legacy TARGET_LEVEL/CELLS compat + case-insensitive cell-name matching in apply_spec + absolute paths for Totem-SC Signal EM IDD→IPF flow"}
