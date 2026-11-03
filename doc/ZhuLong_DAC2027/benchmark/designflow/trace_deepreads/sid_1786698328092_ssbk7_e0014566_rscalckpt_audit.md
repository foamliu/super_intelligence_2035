# Deepread: sid 1786698328092_ssbk7 (e0014566 / hfeg0plg58, mc=280, pg_layout)

**Session**: `1786698328092_ssbk7` · user `e0014566` · host `hfeg0plg58` · 346 msgs / 1.195 MB · agent `lead` · model glm-5.2
**Trace path**: `/home/e0014566/.cline/data/sessions/1786698328092_ssbk7/1786698328092_ssbk7.messages.json`

## Real user intent (4 user text turns)

- **msg[0]** (A-档 seed, clean goal — 提出需求，未给根因/修复):
  「先看一下配置参数 rscalc.config, 获取到 目标 layout. 我现在要用rscalc计算电阻，看看其powernet 上的RTEXT，没有的话，帮忙在合适的位置上打上。既然不能修改原本的layout, 请先原封不动拷贝一份这个layout, 然后分析，然后打上RTEXT。另外，请在配置文件rscalc.config 中增加 check points, 以计算这点的电阻。增加的量控制在50左右，分布要广泛典型。」
- msg[62] 「好的，来吧，计算电阻吧」(approval, not a new task)
- msg[287] 「怎么样才能使RDV via 被正确提取」(gives fix direction → hint, not prompt)
- msg[313] 「你帮我看下版本 AI_Virtuoso 下的TECHLIB中有没有你想要的」(guidance → hint)

## Assistant tool chain (175 tool uses)

1. `run_commands` cat rscalc.config + ls test_skills_4 → 读取配置（process/project/libName/cellName=BCenterR/version/pwrNets=""/checkPoints=nil）
2. `read_files` prompt.md + SKILL.md + run_rscalc_nogui.il (virtuoso-rscalc-runner skill)
3. `SandBox_MCP_Server__run_code` (SKILL) `dbOpenCellViewByType("auto_austin_case1" "BCenterR" "layout")` → 枚举 shapes/labels/RTEXT/RNODE；发现 BCenterR 无 RTEXT
4. 逐层（RDL/M5/M4/M3/M2/M1）在 pad 位置点查金属 → 确定 vdd1!/vss!/vcc! powernet 的有效金属坐标
5. `dbCopyCellView` BCenterR → BCenterR_rtext（不修改原 layout）→ 在 12 个 RDL pad 位置打 RTEXT 标签
6. `editor` 改 rscalc.config: cellName=BCenterR_rtext, pwrNets="vdd1! vss! vcc!", checkPoints=list(list(x y "layer" "net")...) 50 个已点查金属的坐标
7. `run_commands` gen_rscalc_agent.py → nohup virtuoso -nograph -replay run_rscalc_agent.il 跑 rscalc（等 DONE!）
8. 发现 .rvn 未生成 → 查 rsb.log/rsc.config/addtext.dat → addtext.dat parser 报 `Failed to convert position to decimal value (token=M5)` —— check_points 写成 `x y "M5" , ` 但 runrsc 二进制 parser 不认引号层名
9. `editor` 改 run_rscalc_nogui.il 的 `fprintf(cfgPort "%L %L %L  , " ...)` 格式 → 重跑
10. msg[58] FINAL VERIFICATION: 原 BCenterR RTEXT=0/RNODE=0 (未改)；新 BCenterR_rtext 有 12 RTEXT；config 50 checkPoints 全部有金属

## Gold artifacts (real, user-accepted)

- `rscalc.config` 终态: cellName=BCenterR_rtext, pwrNets="vdd1! vss! vcc!", targetCount~50, checkPoints = list(list(x y "layer" ["net"])...) 50 个点
- checkPoints 格式: `list(15309.665 -548.644 "RDL" "vdd1!")` — 4 元素 (x, y, 层名, net)；net 可省
- 新 cell BCenterR_rtext: 12 个 RTEXT 标签在 RDL pad 位置
- 关键审计维度（msg58 FINAL VERIFICATION）: 原 layout 未改 + 新 cell 有 RTEXT + 每个检查点在指定层有金属

## Adaptation → EDA-Eval-DesignFlow-RsCalcCkPtAudit-001 (B-档 synthesized, L1-boundary)

真实任务依赖 live Virtuoso IC617 + 私有 auto_austin_case1 库 → A-disqualified → B-档 synthesized L1-boundary。
把 msg58 的 "FINAL VERIFICATION" 维度抽出来：对一份 **候选** checkPoints 计划 + layout 金属 inventory 做静态审计。

**candidate**: `rscalc_checkpt_plan_audit.py` (stdlib re/json/sys/os)
- 解析 rscalc.config (SKILL-ish key=value + `checkPoints = list(list(x y "layer" ["net"])...)`)
- 解析 inventory.json (layout_bbox / allowed_layers / nets[net][layer]=[bboxes] / rtext_labels)
- 10 类审计（每点按优先级取第一条命中）：out_of_bbox > invalid_layer > undeclared_net > wrong_net_layer > off_metal > duplicate_rtext；全局 count_mismatch / per_net_coverage / layer_diversity / cluster(200×200 窗口>2)
- 输出 audit_report.json: config + audit(total_points/target_count/per_net_counts/undeclared_net_points/per_layer_counts/distinct_layer_count/bbox_coverage/issues/issue_counts_by_kind/issue_total) + verdict(OK|HAS_ISSUES)

**A**(visible, clean): 50 valid points, 3 nets vdd1!/vss!/vcc!, verdict OK
**B**(hidden, 7 issue kinds): 40 points target 40 — off_metal×3, wrong_net_layer×2, out_of_bbox×1, undeclared_net×2(VDDIO), duplicate_rtext×4, cluster×1, per_net_coverage×1(VCCIO=0) → verdict HAS_ISSUES, issue_total=14
**B2**(hidden, single net VDD, 25 pts target 20): count_mismatch×1, off_metal×1, duplicate_rtext×1, invalid_layer×1, out_of_bbox×1 → issue_total=5 (kill hardcode B)
**B3**(hidden, clean 30 pts 2 nets): verdict OK (kill always-FAIL)

**check.py 14 条断言 (a)-(n), k=14=k_check≥8 GATE PASS**:
①[a]zip+compile+run B rc0+JSON+file==stdout+顶层/audit 键齐全 ②[b]config 解析 total/target/pwrNets==独立重派生 ③[c]per_net_counts+undeclared==独立重派生 ④[d]B verdict HAS_ISSUES ⑤[e]B issue_total==14 ⑥[f]B 10 类 issue_counts 逐类对账 ⑦[g]B per_net VDD22/VSS16/VCCIO0 ⑧[h]跨输入 B2 计数==期望且 B≠B2 ⑨[i]跨输入 B3 verdict OK ⑩[j]distinct_layer≥2 + per_layer sum==total ⑪[k]bbox_coverage 6 键 + cov∈[0,2] ⑫[l]确定性 3×md5 ⑬[m]issues 条目格式 + kind∈10 类 ⑭[n]audit_report.json 非空

自验: ref PASS 14/14 ✓; 4 neg(empty→a/print_expected→h[hardcode B]/core_deleted→b/naive_hardcode_b→h)全 FAIL NEG_RC=0 ✓; §4.9(a)(b)(c)全 FAIL ✓; test==disk roundtrip 12576B ✓; jsonl_C 76→77; pg_layout 10→11.

## Candidate selection record

- 候选池（shard C, mc≥100, 排除台账 171）: top = as67p(mc786,netlist/waveview→非C域), 4a852(mc661,aether+virtuoso), okq91/t0aom(mc650,analog), 82iou(mc606,pyAether/schematic→layout_aether)
- pg_layout 优先（覆盖最低 10 cases）: ssbk7(mc280, floorplan:53+virtuoso+rscalc+RTEXT) 选定
- x1ulx(mc330, calibre:585) 作为 physical_verify 备选保留
