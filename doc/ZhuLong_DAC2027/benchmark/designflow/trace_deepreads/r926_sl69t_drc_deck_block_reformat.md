# r926 deepread — sl69t (lizwen @ hfeg0plg09) DRC deck block→single-line reformat

## trace 来源
- session_file: `1790126908419_sl69t.messages.json`
- user: lizwen / host: hfeg0plg09 (10.129.2.11)
- mc=22 (drc:180;aether:51;lvs:21;...)
- 20 msgs / 2 user inputs (single-turn task + 0 follow-up)
- 选中路径：r924 判 mc≥5 fresh C-keyword pool QUALITY depleted 后，r925 用 revival 池破 0-case；r926 revival 池只剩 8 候选且仅 gvm3g 标"可造"但 deepread 查实 gvm3g 已被 A/B/D 三 shard cased + C ledger r616 re-park 为 wrong-domain(spice_sim)。遂 pivot 回 fresh mid-mc (5-80) C-keyword 池， Lizwen 出现 3 次 (6lk3c/mvt8c/sl69t) 选中 sl69t。

## 真实意图 (trace msg 0/7/9/12/19)
- U#0 原话：「/home/lizwen/.cline/scripts/data/sample_drc_deck/specs/test_deck 将该文件的内容格式改成，比如 PG_Wmax_066_00:Max - NMOS width for ESD or MOSCAP [in peri: 168.575 ]这种，另存文件名：test_deck_new」
- assistant msg 7: tool_use run_commands `cat > reformat_deck.py << 'PYEOF' ... PYEOF; python3 reformat_deck.py` —— **gold reformat_deck.py 完整源码在 trace msg[7] tool_use input.commands[0] 内**（174 行 reformat_deck.py 的前身版本）。
- assistant msg 9: tool_use editor 修补 reformat_deck.py（new_text 字段含修正后源码）
- assistant msg 12: tool_result(5116 chars) = run_approved_command 输出：`Written 49 rules to .../test_deck_new` + 49 行 `RULE_NAME:description`
- assistant msg 19: 最终总结报告（810 chars）：转换逻辑 5 点（规则名提取/@描述提取/多@合并/无@ fallback Min-Max-Exact/跳过 VARIABLE+空行）+ 结果 49 条规则

## gold 解析逻辑 (从 trace msg[7] + msg[9] 提炼)
1. 正则 `^([A-Za-z0-9_]+)\s*\{` 匹配块头 → rule_name
2. 块内收集 `@` 开头行：去掉 `@` 前缀和空白，作为描述片段
3. 多条 `@` 描述行用单空格连接合并
4. **fallback**：块内无 `@` 行时，取第一条 `^(Min|Max|Exact)\s*-` 开头行作为描述
5. 跳过 `VARIABLE` 声明行和空行
6. 输出每行一条 `RULE_NAME:<描述>`

## trace gold bug 发现 + 修复
trace 原始 reformat_deck.py 的 fallback 逻辑有 bug：找到 `Min-Max-Exact` 行后 `break`，`j` 停在描述行，`i = j + 1` 落到 `drc { ... } ?` 行 → 误解析 `drc` 为新块。我的 ref solve.py 修正：单遍扫描块内所有行，同时收集 `@` 行 + 记录 fallback 候选 + 找到 `}` 时 `close_j = j`，最后 `i = close_j + 1` 跳过整个块。

## 跨 shard 串台检查
- sl69t 在 4 shard ledger 互斥 0 hit（fresh）
- sl69t 在 4 shard jsonl trace_source 0 hit
- 同 domain 已落库 case 检查：
  - DrcRuleFromDesc-001 (qhvcj kenwang): 从 @description **开发**规则代码 — **正交**（本 case 只重排格式，不开发代码）
  - DrcDeckRuleUpdClassify-001 (ksgw3 kenwang): **更新**规则块 code 段 — **正交**（本 case 不改 code）
  - DrcLogAnalyzer-001 / DrcRunStatusAnalyze-001 / DRCLogTeardown-001: DRC **运行 log** 分析 — **正交**（本 case 是 deck 文件格式重排，非 log 分析）
  - DRCPatGen-001 / DrcTestpatternGen-001 / DrcPatternPlan-001: DRC **testpattern 生成**（用 drc_pattern_gen.py 画 .oa）— **正交**（本 case 不画版图，只重排 deck 文本）
  - CalibreDrcRunsetConfigValidator-001 / DrcRunsetAutoConfigAnalyze-001: runset **配置校验** — **正交**（本 case 不校验配置，只重排）
- 结论：无串台，子型 "drc_deck_block_reformat" 首例

## A/B 差异化（§4.1 B≠A：规模/取值/结构均异）
- env_A sample_deck.drc: 25 规则 (DNW/NCH/PG/M1/NW/ESD/AT4/NARES 系列)，含 4-@ 合并 (PG_W_029_01) + 2 个 fallback (NCH_S_006_02, PG_EXT_031_01) + VARIABLE×3 + 章节注释×4
- hidden B sample_deck_B.drc: 15 规则 (M2/M3/VIA/DENS/ANT 系列)，含 2-3-@ 合并 (M2_W_002_00/M3_Wmax_005_00/AT4_Wmax... ) + 2 个 fallback (M3_S_015_00, M3_S_015_01, ANT_M3_001_00) + VARIABLE×3 + 章节注释×5
- 规则数 25 ≠ 15；规则名集合不交（A 用 DNW/PG/NCH/M1，B 用 M2/M3/VIA/ANT）；取值不同（A 的 [in peri: 8.260] vs B 的 [in core/peri: 0.100]）；结构都含多@/fallback/嵌套 drc{}

## k=16 teeth (≥8 硬闸门)
[a] zip 含 reformat_deck.py + py_compile
[b] 无参/--help 运行无未捕获 traceback
[c] hidden B 上 exit 0 + 输出文件非空
[d] 输出行数==B 规则数 15
[e] 每行匹配 RULE_NAME:description（冒号分隔）
[f] 规则名匹配 ^[A-Za-z0-9_]+$
[g] VARIABLE 声明跳过
[h] // 注释跳过
[i] 多@规则(M2_W_002_00)描述单空格合并 + 含 except supply rails
[j] 无@ fallback 规则(M3_S_015_00)描述含 Min - M3 spacing for dense routing regions
[k] 空行/章节标题跳过（无纯中文/括号行）
[l] B 特定 8 规则名全部出现
[m] 反硬编码 B 15 ≠ A 25
[n] 反硬编码 A 独有 4 规则名不出现在 B
[o] 3-seed 确定性：打乱 B 块顺序后 3 种子输出规则集合相同
[p] B 特定值保留：M2_DENS_001_00 描述含 "30 percent"

## 自验
- ref solve.py PASS 16/16（embedded check 也 PASS）
- §4.9 三假全 FAIL distinct teeth：
  - (a) naive_empty → tooth [c] "output file not produced / empty after B run"
  - (b) naive_print (硬编 A 25 规则) → tooth [d] "output rule count 25 != expected 15"
  - (c) neg_delete_core (删多@合并+fallback) → tooth [e] "empty description for rule 'M3_S_015_00'"
- 3-seed determinism PASS（seeds 11/22/33）

## 落库
- C.jsonl 571→572 (DrcDeckBlockReformat-001)
- ledger mark sl69t → case
- trace 覆盖率 584→585/2072=28.2%
