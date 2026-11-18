# trace_deepread: xk5uw — drcoa PDK calibreDRC.rule 解析文档生成

- **session**: `1792025924814_xk5uw` | user `e0039122` @ `hfeg0plg53` | mc=56 | physical_verify
- **起止**: 2026-10-15 ~ 2026-10-29（interactive, model glm-5.3-flash, 9.5M input tokens, 184 msgs / 99 user / 85 assistant）
- **status（旧台账）**: parked 2026-11-03「查找 PDK drc 文件+层含义 QA 非 design-flow seed」——典型 weak-reason 误杀，2026-11-15 §二 reaudit 已标「可造」，本轮 r793 复活并落 case。

## 用户真实意图（6 个用户轮，逐字）
- U#0「帮我查找droca项目的PDK中drc文件在哪里」
- U#21「长鑫的版图每一层是什么含义」
- U#45「每一层的不通purpose是什么」(不通=不同)
- U#61「调用skill把这些内容发送得到我的workspace中」
- U#69「对drc.rule生成一份详细的解析文档」← **核心交付意图**
- U#164「这个md文档在linux下怎么查看」(收尾：md→html 转换)

## 助手工具链（37 editor + 21 run_approved_command + 22 read_files）
1. `find_droca_pdk.py` → 定位 PDK：`/apps/imctf/runset/calibre/cxmtG5_CIP/current/drcoa/G5_CIP_package_drcoa_v0d5_Rev08/calibreDRC.rule`（44436 行 / 2.2MB）+ `/apps/imctf/cad/techlib/.../techfile.tf`
2. `drcoa_layer_summary.py` / `drcoa_purpose_extract.py` → 抽 layer 表 + purpose（产 `drcoa_layers.txt` / `drcoa_layer_purposes.txt`）
3. **解析器迭代**：`parse_drc_rule.py` → `debug_braces.py` → `parse_drc_rule_v2.py` → `debug_blocks.py` → `parse_drc_rule_v3.py`（产 `drc_rule_stats.txt` + `drc_rule_samples.txt`）——大括号平衡 / rule block 切分是真难点
4. **金标准交付**：`drcoa_calibreDRC解析文档.md`（A#146-154 五次 editor 写入，由 v3 解析统计生成）
5. `verify_doc.py` / `check_viewers.py` / `md2html.py` / `verify_html.py`（U#164 收尾）

## 真实产物状态（2026-11-19 复核）
- `calibreDRC.rule` 在 hfeg0plg53 `/apps/.../` **仍在**（2.2MB, 44436 行, 2026-10-02）→ 已 scp 拉到 .75 workdir
- 助手中间产物（parse_drc_rule_v3.py / drcoa_calibreDRC解析文档.md / drc_rule_stats.txt）在 `/home/e0039122/` **已被清理**（session 10-29 结束后清，仅余 11 月其他 .py）→ 金标准 md 不可直接取，改为自建参考解析器

## reframe（C 线既定模式：真实交付→离线可验核心）
- **真实交付** = `drcoa_calibreDRC解析文档.md`（prose，check 牙弱）+ 其结构化后端 `drc_rule_stats.txt`
- **离线可验核心** = `parse_calibre_drc.py`：读 Calibre DRC rule deck → 输出 `drc_analysis.json`（14 个结构化字段：total_lines / define_active / define_inactive_count / layer_map_count / layer_name_count / layout_base_layers / brace_open / brace_close / rule_keyword_total / drc_maximum_vertex / drc_keep_empty / drc_maximum_results / drc_results_database / layer_id_samples）
- **真实跑 Calibre 需 GUI/runtime，SUT 沙盒不可达** → reframe 为纯 stdlib 静态解析（与 r787 WlAdjacent/bash→python、r789 CalibreLvs/静态规则修复器同模式）

## 输入 A / hidden B
- **A（visible, SUT 沙盒）**：`calibreDRC.rule` = 真实 CXMT drcoa PDK 文件的**结构化切片**（1768 行 / 76KB，保留全部受检特征：DEFINE 开关块 + 600+ LAYER MAP（含 AR_mark/AR_ARRAY/AR_SRF）+ LAYOUT BASE LAYER 行 + 规则块 + DRC 控制页脚）。原文件 2.2MB 无法经 MCP→model 透传到本地 repo（无跨机 mount，local 不可 ssh .75），故取真实切片。
  - A facts: total_lines=1768, define_active=[DDR_CHECK,DDR5_CHECK,HORI_PA2_CHECK,PA2_CHECK center,TOP_METAL_IS_M5,RDL_TECH,DEBUG], layer_map_count=602, layer_name_count=601, brace_open=2/brace_close=2, drc_maximum_vertex=199, drc_keep_empty=YES, drc_maximum_results=ALL, drc_results_database=AAAAA.drc.results, layer_id_samples={AR_mark:8001,AR_ARRAY:8002,AR_SRF:8003}
- **B（hidden, judge workdir）**：A 的修改变体（1126 行 / 49KB）：DDR5_CHECK→off、LPDRC_CHECK→on、删 LAYER MAP/LAYER name #200-#520（各 321 行）、DRC MAXIMUM VERTEX 199→250、KEEP EMPTY YES→NO、MAXIMUM RESULTS ALL→5000、加 1 个 '{'。**9 字段与 A 不同** → anti-hardcode。
  - B facts: total_lines=1126, layer_map_count=281, layer_name_count=280, brace_open=3, drc_maximum_vertex=250, drc_keep_empty=NO, drc_maximum_results=5000, define_active=[LPDRC_CHECK,...], define_inactive_count=6

## check()（k_check=17，标签 a-q，独立解析 B 对账）
a zip 合法含 parse_calibre_drc.py | b py_compile | c 候选在 B exit0+合法JSON | d total_lines | e define_active 集合 | f define_inactive_count | g layer_map_count | h layer_name_count | i layout_base_layers | j brace_open+brace_close | k drc_maximum_vertex | l drc_keep_empty | m drc_maximum_results | n drc_results_database | o layer_id_samples(3 命名层) | p rule_keyword_total | q 确定性 2x byte-identical

## 自验（.75 + 本地双跑）
- ref PASS 17/17（a-q），.75 与本地 repo 双跑一致
- 4 negative 全 FAIL（NEG_RC=0）：neg_empty→c / neg_print_only→c / neg_hardcode_a→d（硬编 A 的 total_lines=1768 vs B 1126）/ neg_fake_core_deleted→e（define_active 抽取被删 → [] vs B）
- §4.9 三假（empty/print_only/fake_core_deleted）全 FAIL ✓
- 确定性 2x byte-identical ✓
- test 字段 == disk check.py（9564 bytes roundtrip）✓
- k_rationale = k_check = 17 ≥ 8 GATE PASS ✓

## 与任务初衷对齐
- 真实 trace ✓（e0039122@hfeg0plg53, session 1792025924814_xk5uw, mc=56, 可溯源）
- 用户真实意图「对 drc.rule 生成详细解析文档」= doc-search + doc-generation，按 2026-11-15 §二「doc-search/Q&A 现合法」恢复
- check 有牙：17 条独立可失败断言，对 B 真实解析对账，硬编 A 必 FAIL
- 无配额痕迹：xk5uw 旧 parked 是「QA 非 design-flow」weak-reason 误杀，本轮按新标准复活
