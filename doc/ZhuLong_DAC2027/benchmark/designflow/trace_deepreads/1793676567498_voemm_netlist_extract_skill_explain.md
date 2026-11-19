# deepread — 1793676567498_voemm (t0003117@10.129.2.14, mc23, schematic_netlist)

**revival-from-parked (r934)**：原 2026-11-11 以「Q&A/explain only: read SKILL.md → summarize → '直接执行它' → assistant explains cannot run w/o Virtuoso CIW → gives manual steps, no artifact produced」parked。B-shard 同时以「wrong-domain by kw-profile: spice ratio<0.10, netlist/drc/virtuoso/aether/waveview dominant」parked（r401 0-case）。2026-11-15 候选重审令将 Q&A / teaching / explain / walkthrough 全部恢复为可造。承 r928/r929/r930/r932/r933 「manual-grounded howto produce reframe」范式可造；B-shard wrong-domain 标注正好证明该 trace 属 D 域（netlist/virtuoso），不属 B 域 spice_sim，故 D 域 --force 跨 shard 互斥覆盖合理。

## trace 概览

- 用户 t0003117 在 10.129.2.14 上有自建 skill `netlist_extract`（目录 `/home/t0003117/skills_v0.2/netlist_extract/`，含 `SKILL.md` 60 行 + `extract_current_netlist.il` 214 行 SKILL）。
- 9 msgs，2 个用户轮（U#0 + U#6），会话总长 ~5 分钟（ts 1793676567 → 1793676641）。
- domain 复核：keywords 含 `netlist`/`virtuoso`/`aether`/`schematic` 命中（mc23 是 keywords 中 D-正向词的累计计数），SPICE 网表抽取属 D 域 schematic_netlist。B-shard kw-profile 判 spice ratio<0.10 → wrong-domain，与 D 域归属一致。

## 用户轮原文（A 档合规判定）

| 轮 | ts | 原文 | A档合规 |
|----|----|------|---------|
| U#0 | 1793676567950 | 告诉我/home/t0003117/skills_v0.2/netlist_extract/SKILL.md的主要内容 | ✅ 提出需求✓ 未给根因/修复✗ → **选用** |
| U#6 | 1793676599655 | 直接执行它 | ✗ 执行请求（非新需求；assistant 解释须 Virtuoso CIW 环境 → ask_question → 用户选「在 Virtuoso CIW 中手动加载执行」→ 给出步骤指引，无产物） |

**主意图 = U#0**：解释 skill 的主要内容（teaching/explain Q&A）。U#6 是用户在理解后的执行请求，验证了 assistant 解释的实操指引可落地性（但因缺 Virtuoso 环境未实际跑）。

## assistant 工具链

- A#1: `read_files /home/t0003117/skills_v0.2/netlist_extract/SKILL.md` — 读 skill 元数据（60 行）
- A#3: **完整解释（GOLD）** — 概括 SKILL.md：Workflow single-step，自动检测 Virtuoso 当前 schematic 导出 HspiceD SPICE 网表到 `finesim_data/<cell>_<ts>/netlist/<cell>.sp`，基于 `pwd()` 动态路径，写 `.current_run` 握手，4 条验收标准 + 2 个已知陷阱
- A#7 (U#6 后): `list_allowed_files /home/t0003117/skills_v0.2/netlist_extract depth=2` — 列目录（2 文件）
- A#9: `read_files extract_current_netlist.il` — 读 214 行 SKILL 参考实现
- A#11: 说明须在 Virtuoso CIW 中 `cd()`+`load()` 执行 + `ask_question` 三选项
- A#13: 用户选「在 Virtuoso CIW 中手动加载执行」→ 给出 CIW 步骤指引（cd/load/预期输出/输出文件位置/问题排查表）

## GOLD 关键内容（A#3 + A#9 + .il 源码合成 handbook 的依据）

### §1 整体功能（SKILL.md）
- 名 `netlist_extract`，类型 Workflow (single-step)，适用场景：从 Virtuoso 当前打开的电路抽取 SPICE 网表
- 创建/更新 2026-09-04，输出位置 `<pwd>/finesim_data/<cellname>_<timestamp>/netlist/<cellname>.sp`
- 自动检测 Virtuoso 当前 schematic，导出 HspiceD 格式 SPICE 网表；不写死绝对路径，全部基于 `pwd()`

### §2 实现架构 — 5 阶段流水线（extract_current_netlist.il 214 行，全包在一个 let() 作用域）
1. `load exportNetlistNoGUI.il` L36-39 — 拼接 `pwd()/skill_scripts/netlist_extract/exportNetlistNoGUI.il` 并 `load()`，使 `InnoExportNetlistNoGUI()` 进入环境
2. `geGetEditCellView()` L41-56 — 检测当前活动窗口 cellview，读 libName/cellName/viewName；nil 则 `error("No edit cellview available")`
3. 创建 run 目录 + 写 .current_run L58-89 — `baseDir=pwd()/finesim_data`，shell `date +%Y%m%d_%H%M%S` 落地再 fscanf 读时间戳，`runDir=baseDir/<cell>_<ts>`，`netlistDir=runDir/netlist`，把 runDir 写入 `finesim_data/.current_run`
4. `InnoExportNetlistNoGUI` 导出 HspiceD 网表 L91-157 — 调 `InnoExportNetlistNoGUI(lib, cell, view, "hspiceD", "hspiceD spice schematic symbol")`；4 层 fallback：(a) nil → `simplifyFilenameUnique(envGetVal("asimenv.startup" "projectDir"))` 推导 projDir/<cell>/hspiceD/<view>/netlist/netlist (b) `<pwd>/simulation/<cell>/hspiceD/<view>/netlist/netlist` (c) `<pwd>/<cell>/hspiceD/<view>/netlist/netlist` (d) `find <pwd>/simulation -name netlist -type f | head -1`
5. 拷贝 + cat fallback + EXTRACTION COMPLETE L159-214 — `targetFile=netlistDir/<cell>.sp`，`cp -f` 失败则 `cat >` 重定向兜底；成功打印 `EXTRACTION COMPLETE` 横幅 + Circuit Module/Run directory/Netlist saved/Source netlist 四行摘要

### §3 SKILL.md 工程价值 — 已知陷阱（SKILL.md 2 个 + .il 源码补 6 个 = 8 个）
| 陷阱 | 应对 |
|------|------|
| `pwd()` 不是项目根目录 | 找不到 `skill_scripts/netlist_extract/exportNetlistNoGUI.il`；在项目根目录下执行 |
| schematic 窗口不是活动窗口 | `geGetEditCellView()` 返回 nil；执行前点击目标 schematic 窗口 |
| `InnoExportNetlistNoGUI` 返回 nil | 启用 `simplifyFilenameUnique(envGetVal("asimenv.startup" "projectDir"))` fallback |
| 网表落在 simulation/ 子目录 | 4 层 fallback（projectDir → simulation → 当前目录 → find） |
| `cp -f` 跨文件系统失败 | `cat >` 重定向兜底 |
| 变量被 `InnoExportNetlistNoGUI` 内部同名参数踩 | 全部共享变量包在一个 `let()` 动态作用域内 |
| `date` 命令格式不一致 | `+%Y%m%d_%H%M%S` 固定格式，落地文件再 fscanf 读回 |
| 下游 PWL 脚本找不到 run 目录 | 写 `finesim_data/.current_run` 握手文件 |

### §4 使用方式（A#13 GOLD 步骤指引）
- CIW（推荐）：`cd("/home/e0019581/yyl_testing/")` → `load("skills_v0.2/netlist_extract/extract_current_netlist.il")` → 观察 `EXTRACTION COMPLETE`
- Python 模块（pyAether 桥接）：`aeRunSkill(code, host="aether")` 远程执行 cd+load
- 人工阅读：SKILL.md + .il 源码按 5 阶段顺序阅读

### §5 验收标准（SKILL.md 4 条）
1. CIW 打印 Library/Cell/View 和 Run directory
2. `netlist/<cellname>.sp` 存在且非空
3. `finesim_data/.current_run` 存在且内容为 run 目录路径
4. CIW 显示 `EXTRACTION COMPLETE`

## 造题形态决定

- **形态**：manual-grounded howto produce reframe（承 r928/r929/r930/r932/r933 范式，复用 r933 skill_explain_parser.py 通用解析器 verbatim）
- **A 档 prompt** = U#0 verbatim「告诉我/home/t0003117/skills_v0.2/netlist_extract/SKILL.md的主要内容」
- **A 手册**：从 A#3 GOLD + .il 源码合成 `netlist_extract_skill_explain_A.md`（保留真实结构：§一-§六 + 5 阶段 + 8 陷阱表 + 3 方法 + CLI 参数表）
- **B 平行场景**（hidden）：合成 `layout_gds_streamout_skill_explain_B.md` —— 另一个 skill「layout_gds_streamout」用 `InnoStreamOutNoGUI` 导出 GDSII，平行 5 阶段流水线（load streamoutNoGUI.il → geGetWindowCellView → mkdir gdsout_data+.current_gds → InnoStreamOutNoGUI+4 层 fallback → cp/cat fallback+STREAMOUT COMPLETE），平行陷阱表（8 个 B-only 陷阱），平行 CIW/Python/人工阅读三入口。B-only token 反硬编码 A-only {netlist_extract, extract_current_netlist, InnoExportNetlistNoGUI, geGetEditCellView, HspiceD, finesim_data, .current_run, exportNetlistNoGUI.il, EXTRACTION COMPLETE, asimenv.startup, projectDir, simplifyFilenameUnique, envGetVal, SKILL.md, yyl_testing, e0019581, skills_v0.2, 2026-09-04, netlist.sp, schematic symbol}，identifier-boundary 正则 netlist_extract 不误匹配 layout_gds_streamout、geGetEditCellView 不误匹配 geGetWindowCellView
- **candidate_ref.py** = `skill_explain_parser.py` —— 通用 markdown 手册解析器（r933 同款 verbatim 复用），输出 JSON {question, methods, prerequisites, parameters, cited_sections, primary_method, overall}
- **check.py**：12 断言 a-l（同 r933 结构，调整 A-only token + B 文件名 + prerequisite 关键词）

## buildable 判定

✅ 真实 trace（trace_source 完整：user t0003117 / host 10.129.2.14 / session 1793676567498_voemm / mc23 / real_task_summary）
✅ A 档合规（U#0 提出需求，未给根因/修复）
✅ GOLD 可合成（A#3 完整解释 + .il 214 行源码完整捕获）
✅ check() 有牙（B 平行场景 + 反硬编码 identifier-boundary + 3 seed idempotence + 3 假提交 FAIL + §4.9 三退化 FAIL）
✅ 11-15 reaudit 已判 Q&A/teaching/explain 可造
✅ B-shard wrong-domain 标注支持 D 域归属（netlist/virtuoso dominant，spice ratio<0.10）
✅ self-verify 12/12 PASS + 3 neg FAIL + §4.9 三退化 FAIL
