# Deep-read: 1790214684453_ocopa (e0041123 @ 10.129.40.58, mc=42)

- **session**: `1790214684453_ocopa.messages.json` (135 KB, 27 msgs, 2026-09-24, agent='lead', zhulong system prompt)
- **user**: e0041123 @ 10.129.40.58 (host hfeg0plg106), 14 sessions in `~/.cline/data/sessions/`
- **cwd/data**: `/home/e0041123/data` (user clarified at U#17; skill 标准位置 `~/.cline/scripts/data` 也有副本)
- **keywords (scan)**: pyaether:196; aether:152; schematic:15; cmos:15; skipper:2; floorplan:2 — pyaether/aether 主导，C-domain physical_verify/layout_aether

## 对话流（27 msgs, 14 user / 13 assistant）

- **U#0** (act mode): 加载 DRC Testpattern Generator skill 文档（贴出 skill spec：用户给规则名通配符 → `run_drc_pattern.sh` 包装脚本 → `drc_pattern_gen.py` 生成 .oa；所有路径相对脚本目录；规则名支持 `*` 忽略大小写）。要求「生成一个示例 pattern」。
- **A#1**: 加载 `drc-pattern` skill (skills 工具)
- **U#2**: skill 返回 instructions（Description: 为 DRC 规则生成 Testpattern 版图 PASS+FAIL）
- **A#3**: 执行计划：定位数据目录 → 检查环境 → 执行生成。调 `get_agent_policy_status` + `list_allowed_files`
- **U#4-#5**: policy enforcing；allowed files root=/home/e0041123
- **A#6**: 发现两个候选目录 `~/.cline/scripts/data` 和 `~/data`
- **U#7-#8**: list 两个目录内容
- **A#9**: 两目录都有完整数据；用 skill 标准位置 `~/.cline/scripts/data`。读 `run_drc_pattern.sh` + `drc_rules_spec.json`(1-80) + list `DRCPatLib`
- **U#10**: read_files 返回 wrapper 脚本（18 行 bash：设 AETHER_ROOT/HOME/OA_HOME/PYAETHER_HOME 环境变量，cd 脚本目录，`pythone drc_pattern_gen.py "$@"`）+ drc_rules_spec.json 头 80 行（spec_version=2.0.0, rule_count=49, 11 rule_categories, layer_definitions DNW/NW/NCH1...）
- **U#11**: DRCPatLib 含 .oalib/tech.db/NCH/layout.oa（上次运行残留 + cdslck 锁文件）
- **A#12**: 环境确认完毕：wrapper 就绪、规则 JSON 有效（49 条）、DRCPatLib 存在。`run_approved_command` 执行 wrapper，查询 `DNW*`
- **U#13**: **FAILED** exitCode=1。stdout: OpenAccess 2.2 loaded + emyLibInit.tcl for analog/amsLib。stderr: `LC_Check out license PY_AETHER` → `drc_pattern_gen.py` line 18 `import pyAether as pyScript` → `pyAether/__init__.py` → `pyaecore.py` line 34 `from PyQt5.QtWidgets import QWidget, QMdiArea` → **RuntimeError: the sip module implements API v12.0 to v12.6 but the PyQt5.QtWidgets module requires API v12.8**
- **A#14**: 诊断 = Python 环境冲突，非数据问题：用户 site-packages 旧版 sip 抢先加载覆盖 Aether 自带版本。读 `.bashrc` 诊断 PYTHONPATH
- **U#15-#16**: read .bashrc 结果；list `~/.local/lib` → ENOENT（不存在）
- **U#17** (act): **用户原话「我的完整data文件在/home/e0041123/data这里」**
- **A#18**: 改用 `/home/e0041123/data`。list data 目录 + 读 run_drc_pattern.sh（data 副本）。尝试创建诊断脚本 `diag_env.py` / `diag_pythone.sh`
- **U#19-#22**: data 目录列出（drc_pattern_gen.py/drc-pattern-SKILL.md/lib.defs/run_drc_pattern.sh/sample_drc_deck/techfile.tf/TECHLIB.layermap/display.drf）；**写 data/diag_env.py 被 policy 拒（writableRoots 不含 /home/e0041123/data）**；写 diag_pythone.sh 同样被拒
- **U#23** (act): **用户原话「开始吧」**
- **A#24**: 确认 policy 可写根 + data 目录文件权限 + 读 data/run_drc_pattern.sh
- **U#25-#26**: read policy json + wrapper 脚本；list data 目录（含 ownership：data/ 文件 ownedByRuntime=true mode 0664/0775，但 writableRoots 仍不含 data）

**trace 结束：助手仍在诊断 sip/PyQt5 环境冲突 + writableRoots 限制，未成功生成 testpattern，无用户接受结果。**

## 关键产物（实证于 .75:/home/e0041123/data）

- `run_drc_pattern.sh` (18 行 bash wrapper)：设 Aether 环境变量 + cd 脚本目录 + `pythone drc_pattern_gen.py "$@"`
- `drc_pattern_gen.py` (525 行 Python)：查询逻辑 = fnmatch(大小写不敏感，rule_id 与 query 都 upper) 匹配 rule_id，多 query 并集去重，deck 顺序；`derive_cell_name`（去首尾 *?，剩余 *?→_，去首尾 _，多 query 用 _ 连接，空→"drcPatterns"）；无 query 默认 "DNW_W_000_00"；无匹配 sys.exit(1)
- `drc_rules_spec.json` (80 KB, 49 rules, 11 rule_type categories, Calibre SVRF)：每条含 rule_id/rule_type/description/layers/layer_relation/region/parameters/conditions/svrf_raw/pattern_constraints{pass_case,fail_case}
- `sample_drc_deck/` (test_deck_new 等), `techfile.tf`, `TECHLIB.layermap`, `display.drf`, `lib.defs`, `drc_pattern/DRCPatLib/`

## 真实用户意图

让 DRC Testpattern Generator 跑起来生成示例 testpattern（默认查询 DNW*）。**主线被 sip/PyQt5 环境冲突阻塞** —— 这是 env-config/debug 类任务。底层意图 = pattern 生成器 flow 可用。

## B 档 reframe 选择

A 档不可行：(1) gold = 跑 run_drc_pattern.sh 生成 .oa testpattern，需 pyAether + Aether + 用户生产 fs，SUT 不可达；(2) trace 末尾助手仅诊断环境冲突、未生成 pattern，无接受结果无 gold 输出。

**抽离可离线复刻的子交付 = DRC 规则 spec 通配符查询/报告工具 `drc_rule_query.py`**：
- 这是 `drc_pattern_gen.py` 的查询前端（trace 内真实实现的子组件）：fnmatch 大小写不敏感匹配 rule_id + 并集去重 + derive_cell_name 派生 cell 名 + 报告规则详情
- 纯 stdlib(json/fnmatch/argparse/sys/os)，确定性 JSON(sort_keys)，不依赖 Aether/pyAether/PyQt5
- 2026-11-15 §二 recovery：env-config/debug-Q&A 类恢复为可造；查询子交付是生成器 flow 的真实可离线组件
- visible A = 真实 drc_rules_spec.json 子集(15 条 / 11 类别，e0041123 真实 CXMT DRAM deck)
- hidden B = 内联 check.py 的不同合成 deck(14 条 / 11 类别，AA/GT/M2/CT/NL/PL/HM/TS/SR 系列，rule_id/参数全异于 A) 防硬编码

## 断言清单 (k_check=18, k_rationale=18)

①zip 合法含 drc_rule_query.py + py_compile ②AA* exit0+合法JSON ③AA* matched_count==2 ④AA* 命中=={AA_W_001_00,AA_S_002_00} ⑤大小写不敏感 aa_w_*→AA_W_001_00 ⑥* 命中全部 14 条 ⑦多 query 并集 AA*+*ENC*==4 去重 ⑧去重 AA*+AA_S_*==2 ⑨cell_name AA*→AA、*→drcPatterns ⑩cell_name 多 query→AA_ENC ⑪必填字段非空 ⑫参数保留 min_width==0.18 ⑬无匹配 ZZZ* exit1+count0+unmatched[ZZZ*] ⑭非法JSON exit3 ⑮缺失文件 exit2 ⑯幂等 ⑰svrf_raw 含 EXT AA ⑱* 命中覆盖 11 类别
