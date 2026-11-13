# deepread · 8mrkr (e0039602 @ hfeg0pkn005, mc194, digital)

trace: `1794377434558_8mrkr` · user e0039602 · host hfeg0pkn005 (10.129.2.12) · 775KB / 71 user-role / 11 real user turns
工程: `/home/e0039602/Documents/verilog_lib_trans_v2.3.2copy`（Verilog 网表→simlib 缺失 cell 转换工具）

## 用户意图（3 个 produce-task + 几个 Q&A）
- U#0 Q&A: "读代码，告诉我当没有给 log 的时候默认转换哪些 cell，cell 调用别的 cell 时 AI 怎么理解"
- U#1 Q&A: 读 D6 网表几个 cell 说明功能（agent 解析出 6 个 module: C_latsq2_ParityOpLat_LV / D_latrq3_ColRedFlagUnit / R_trimand2_WLOn2SaOnRcDly / WrLat_WrMux / T_trimnand2_RdColPlsGenNewBdly / ...）
- **U#3 produce-task #1**: "把逻辑改为当不给 log 的时候，就把网表里所有 cell 全部重跑"
  - 根因: `run.py:298` `block_path = (args.block_list or p.get('block_list') or '').strip()` 即使不给 `--block-list` 也回退到 config.yaml 默认 `block_list`，导致只跑白名单 module。
  - fix: 改成 `block_path = (args.block_list or '').strip()` + config `block_list: ""`，不给 `--block-list` → `block_names=None` → 全量。
- U#77/78/80 Q&A: 解释 netlist_parser 怎么从网表解析出每个 model（extract_instances 字符级扫描 + cell名在行首 + cell名+例化名+`(` 三件套）
- **U#81+U#104 produce-task #2（核心·本 case 选用）**: "我的 stdcell 知识库里明明有 latrq3 啊，为什么没匹配到 prompt 里" → 定位到 `simlib_ref_db._eligible_similar` 的"家族门控"：`family_names.txt` 只有 `latrq` 没有 `latrq3` → `t_token not in family_bases` → `return []`。用户令："遇到族名字，能全匹配上最好就选全匹配上的；不能全匹配上可以无视数字差别，给 lat 加上这些之后也应用这个逻辑"。
  - fix: `_eligible_similar` 改两级门控 `full_ok = t_token in family_bases`（族+数字全匹配，digit_match 优先 score 2.0）/ `base_ok = t_letters in family_bases`（仅族字母 base 命中→容忍数字差异，score 1.0）；`family_names.txt` 补 latrq2/latrq3/latrqb/latrqn5/latrqn7/latrsq2/latrsq3/latsq2/latsq3。
- **U#120 produce-task #3**: "新增功能，如果匹配到名字完全一样的，就在参考样例那里加一句『请尽可能模仿这个的逻辑写』"
  - fix: `reference_snippet` 在 `exact()` 命中时追加 mimic note。

## 名字解析逻辑（agent 源码推断 + MSG#103/119 验证）
- `_cell_part(name)`: 去掉首段 role 前缀（单大写字母 D_/R_/T_/C_）→ `D_latrq3_ColRedFlagUnit` → `latrq3_ColRedFlagUnit`
- `_family_token(cell_part)`: 首段 `latrq3` → 字母+数字整体 `latrq3`
- `_family_letters(cell_part)`: 首段字母 base `latrq`
- `_family_digit(cell_part)`: 首段数字 `3`（无数字→''）
- exact(全名) > eligible_similar(同 family_letters, digit_match score 2.0 优先, 否则 1.0, file order) > none
- reference_snippet: exact → mimic note "请尽可能模仿这个的逻辑写"；similar → snippet 无 mimic note

## A-faithful 判定
合格：用户给"知识库有 latrq3 却没匹配上"症状 + "能全匹配选全匹配/不能就无视数字"需求 + "完全同名加 mimic 句"需求，未给名字解析算法/家族门控两级逻辑/打分规则/role 前缀剥离规则。deliverable = 改私有 `/home/e0039602/Documents/verilog_lib_trans_v2.3.2copy/src/simlib_ref_db.py` + `family_names.txt` → .75 Permission denied（私有路径）→ INFEASIBLE → B档合成。

## 合成方向
**StdcellFamilyRefMatch-001**（digital L1-B, stdcell 家族名参考匹配器, k≈14 B档）: 自包含 stdlib CLI，输入 ref-db(simlib module 定义) + family-names registry + queries(待解析 module 名)，输出每条的 {exact_match, matched_name, mimic_note, score, family_token, family_letters, family_digit, gate(full/base/none)}。A/B 不同家族名/数字/规模，跨输入守卫 + 3-seed 顺序无关。
