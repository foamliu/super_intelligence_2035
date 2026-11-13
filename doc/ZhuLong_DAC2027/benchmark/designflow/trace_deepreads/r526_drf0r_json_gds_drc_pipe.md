# r526 deepread — 1794485932332_drf0r (e0047488@hfeg0pkn003, mc=268, physical_verify)

**trace_source**: user=e0047488, host=hfeg0pkn003, session=1794485932332_drf0r, match_count=268
**scan**: ssh_eda_search_20261113_131349 (11/13 full rescan)
**why picked**: fresh (not in any-shard ledger), strong C-domain keywords
(drc:761;calibre:681;pyaether:349;aether:101;lvs:61;.gds:36;gdsii:62), today's
session (ts 1794485932332 = 11/13), same user as mku3e→r523 (proven C-domain
produce-task user). Near-dups ef68k/vvdk8 (identical kw, same user) parked.

## User intent (U0, verbatim)
> 我们项目当前的输出文件是out下的JSON文件，当前通过pyaether_rendor中的脚本可以将其转化为layout，
> 但这是为了将生成的产物转化为layout。如果我们的项目要实现自动化校验，需要打通从我们的产物文件
> 直接到GDS到DRC check返回结果的路径

Produce-task: build an automated verification path **JSON 产物 → GDS → DRC check → 结构化结果**.
Only 3 user_input turns (U0 goal + two "你卡住了，请继续" nudges); no explicit
acceptance, so B档 synthesized (gold = the pipeline the assistant built).

## Assistant toolchain (71 tool-use msgs)
- list_allowed_files / read_files → 探查项目结构 (pyaether_render/, out/, run.py, README)
- RAG_MCP_Server search_apis / get_api_details → 查 GDS 导出 API (dbGdsOut / aeExportStream) + calibre-svrf skill
- run_approved_command → 环境探测: Calibre 2020.1 可用, Argus 可用, pyAether 须在 Aether 环境内跑
- editor → 写 json2gds.py (纯 Python GDSII writer), run_drc.py (GDS→Calibre→解析→判定→报告),
  render_and_export.py (Aether 侧 dbGdsOut 交叉验证), 给 run.py 加 drc 命令
- SandBox_MCP_Server run_code → pyAether 沙箱联跑 (未启动，render 段无法现场联跑)

## Key technical facts (from trace, used as case rule values)
- DRC 规则值: **M1.W.1 ≥ 0.014 μm, M1.S.1 ≥ 0.014 μm, M1.S.20 ≥ 0.14 μm, M1.A.1 ≥ 0.00368 μm²**
- M1/drawing → GDS 层 88/651(+652 双色); M1_mark1/drawing → 88/652
- 8 patterns (good/bad JSON), good vs bad 尺寸差异精确落在规则边界
  (good 宽 0.0185 vs bad 0.0175 等)
- SVRF 命名 check 语法: `CHECK_NAME { ... }`
- 卡点: Calibre 在 RHEL8.10 探测为 aok 但站点只装 aoi 树 (二进制库不兼容) → 换 Argus
  (GLIBCXX_3.4.26 not found，LD_LIBRARY_PATH 污染)

## Case synthesized (B档, physical_verify, L2)
EDA-Eval-DesignFlow-**JsonGdsDrcPipe-001**: 纯 Python 几何 DRC 校验流水线
(JSON pattern → 4 条 M1 规则 → 结构化 PASS/FAIL report + GDSII stream)。
- A (visible, assets/patterns/): 5 pattern (good_all + bad_w/s1/s20/a)
- B (hidden, assets/hidden/patterns/): 5 不同 cell/几何 (b_good_pat7 / b_badw_pat3 /
  b_bads1_pat5 / b_bads20_pat9 / b_bada_pat2) —— 每条孤立一条规则失败，防硬编码
- gold: reference/.../drc_pipeline.py (几何规则 + 最小 GDSII writer, stdlib only)
- check.py: 14 条件 a-n, k_check=14 ≥ 8
- GDSII 真实工具联跑 (Calibre/Argus) 在 SUT 沙箱不可靠，故 DRC 段用纯 Python 几何
  校验实现 (与 trace "纯 Python CI 友好" 路线一致)；GDSII 仅校验 HEADER v600 字节
  (00 02 00 02 02 58) 保真度。

## Self-verify
- GOLD PASS 14/14 ✓
- negative_selftest 5 fakes ALL-FAIL (NEG_RC=0) ✓
  (empty→c / print_expected→f / core_deleted→h / naive_hardcode→h / always_pass→h)
- §4.9 (a) empty→FAIL (b) print_expected→FAIL (c) core_deleted→FAIL ✓
- k_rationale == k_check == 14 ≥ 8 ✓
