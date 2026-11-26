# trace_deepread — 1794225997663_uxowi (e0023936 @ hfhds201) — physical_verify

## 选料
- r322 沿用 r319/r321 的 layout-affinity score 排序法扫 summary.tsv → 1050 unique score≥阈值候选（.75 workdir/cands_uniq_all.tsv）→ 扣除 4-shard ledger exclusion set（2173 sids，A/B/C/D 合并去重）→ top-300 本地过滤 → 41 non-ledgered reachable（排除 172.16.x 不可达）→ peek 16 completed layout-domain 候选的 status + 首条 user_input → 挑 produce-task。
- **uxowi**(e0023936@hfhds201, score=1076, mc=27, kw=qa:89;drc:51;rule:33;pattern:24;layout:18, status=**cancelled**, 单 user turn) = CLEAN seed。虽 session cancelled（探索中打断），真实工作区 `/home/e0023936/devops/eda_data_bridge/qa_pattern_v0.1_1029` 完整可达，任务是一个干净的单步 YAML override 编辑。

## 真实对话流（1 user turn，session cancelled 中断）
- **U#0（唯一用户轮，逐字原文）**：「M1.W.1 的 bad 加一个 bad_2grid 的 L_shape,使用工具 qa_list_rules、qa_get_rule等」
- assistant 链路（被 cancel 截断，仅完成探索阶段）：read workspace → 找到 `qa_pattern_v0.1_1029/workspace/input_DR_m1/M1.W.1.yaml`（override，bad.add 空）+ `rules.json`/`rules_cache.json`（M1.W.1 = Width of M1, layer M1, >=0.014, track A, grid 0.0001）→ 读 `drcqa_kb/categories.py`（CATEGORY_META：bad_2grid = "低于规则两个格点，深度违规"，合法 bad 档位）+ `validator.py`（VALID_SHAPES 含 L_polygon）→ **未到写文件步骤即被 cancel**。
- 真实任务本质（从 user 逐字 + workspace 证据推断）：向 M1.W.1 override YAML 的 `bad.add` 追加 `{category: bad_2grid, shape: L_polygon}` 条目。bad_2grid 表示宽度比规则值低 2 个 grid（M1.W.1: 0.014 - 2×0.0001 = 0.0138），L_polygon 是 L 形多边形几何，用于测凹角处宽度。
- **gold = 任务语义明确**（user 单轮无纠正，workspace 文件齐全，目标条目可由 schema 唯一确定）。

## 关键产物（真实 workspace，pyAether NFS-read 验证）
- **M1.W.1 override**（真实，逐字）：
  ```yaml
  bad:
    add: []
    remove: []
    update: {}
  ```
- **rules.json M1.W.1**：`{layer: M1, type: Width, value: {op: >=, val: 0.014}, track: A, grid: 0.0001, desc: "Width of M1"}`。
- **categories.py CATEGORY_META**：bad_2grid ∈ valid_categories_bad（"低于规则两个格点"档位）。
- **validator.py VALID_SHAPES**：`{rect, L_polygon, U_polygon, Z_rects, Z_polygon, T_rects, T_polygon, O_polygon, diamond45, diamond45_pair, pair, U_notch, O_ring, enc_pair, ov_pair, ov_zero, area_rect, len_rect, overlap, false_overlap, s9_pair, s9_pair_h, s9_pair_nopo, s9_pair_cw_over, s9_pair_area_over, enc_line_end, array3x3, hole_ring, comb, density_window}`。
- **override YAML 结构**：`bad: {add: [{category, shape}, ...], remove: [...], update: {...}}`。
- 真实 assistant 因 cancel 未产出脚本 → 本 case 改造为「通用 append 脚本」题：候选须读任意规则 override、幂等追加、保留 remove/update。

## case 设计（EDA-Eval-DesignFlow-DrcBad2gridLshape-001，physical_verify，A档 faithful，L1，k=13 a-m）
- **A**（assets/.../override_A.yaml）：M1.W.1 override（bad.add 空）+ rules_A.json（M1.W.1 定义 + 邻接 M1.W.2/M1.S.1）+ schema_ref.md（合法词表）+ task_brief.md（交付接口）。
- **prompt**：A档 = U#0 逐字原文 + 附件说明。
- **task_brief**：交付 `add_bad_pattern.py <in.yaml> <out.yaml>`，向 bad.add 追加 {category: bad_2grid, shape: L_polygon}，幂等，保留 remove/update。
- **B/B2/B3**（hidden，结构不同非改名）：
  - B：M2.W.1（Width of M2, layer M2, >=0.012, track B），bad.add 空。
  - B2：M3.S.1（Space of M3, layer M3, >=0.018, track A），bad.add **已有 1 条** {bad_1g, rect}（测追加不替换）。
  - B3：AA.W.1（Width of AA, layer AA, >=0.020, track A），bad.add 空，不同规则命名空间。
- **check**：跑候选 `add_bad_pattern.py <B/B2/B3> <out>` ×3 → 验 13 条件 a-m（zip/脚本/3 YAML 运行/可解析含 bad.add/bad_2grid 条目/shape==L_polygon 且属 VALID_SHAPES/remove==[] update=={}/add 恰好 +1 且已有条目前缀不变/新条目仅 {category,shape} 两键/schema 一致/B2 已有 bad_1g/rect 保留）。
- **negatives**：naive(只打印不写文件) / print_only(写硬编码 YAML，丢 B2 已有条目) / deleted_core(替换 bad.add 而非追加，丢 B2 已有条目) 全 FAIL；§4.9 三假（empty_shell/print_expected/name_only）全 FAIL。ref self-test PASS ✓。
- 难度：候选须 (1) 解析任意规则 override YAML（非硬编码 M1.W.1）(2) 幂等追加（查重再 append）(3) 保留 remove/update 不变 (4) 不删已有条目（B2 关键）。A档 faithful 单轮，目标≤10%。

## trace_source
- user=e0023936, host=hfhds201, session_file=1794225997663_uxowi, match_count=27
- real_task_summary: 在 DRC QA 图案生成规则 M1.W.1 的 recipe override YAML 中，向 bad.add 追加一个 {category: bad_2grid, shape: L_polygon} 测试图案条目，使用 qa_list_rules / qa_get_rule 等工具确认规则信息。bad_2grid 表示低于规则两个格点的深度违规，L_polygon 是 L 形多边形几何。
- 档位：A档 faithful（prompt 逐字 U#0）；session cancelled 但任务语义 + workspace 完整可合成。
