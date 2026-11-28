# 1mmir — junxu bilingual EDA-skill doc generation

> trace: `1789644520518_1mmir.messages.json` · junxu @ hfeg0pjn200 · mc=297
> scan: `.75:/home/t0002965/log/ssh_eda_search_20261128_014416/summary.tsv`
> D-dominant: virtuoso:1791 / schematic:381 / netlist:254 / waveview:168 / cellview:124 / cadence:55 / hspice:43 / analog:27
> 212 msgs (120 user / 92 asst). FRESH (4-shard 台账 grep 0 hit). NEW user.

## 真实任务

用户在自研 `custom_design_skill` 仓库（4 个 EDA skill：`wv-cli` / `virtuoso-cli` / `block-sim` / `block-design`，位于 `/home/junxu/Agents/custom_design_skill/`）里，参考已有的 `wv-cli` 双语文档模板，为其余 3 个 skill 补写**设计文档 + 改进文档**（中英文各一份，每 skill 共 4 个 `.md`）。

agent 行为（brainstorming flow，Bounded 分类）：
1. `list_allowed_files` + `read_files` 探索仓库结构 + 各 skill 的 `SKILL.md` + `git log --oneline --graph --all`（73 次 editor / 19 次 read_files / 11 次 run_commands / 8 次 list_allowed_files / 4 次 search_codebase）
2. 读 `wv-cli` 文档作模板，读各 skill 源码 + git 提交历史理解架构演进
3. 按 wv-cli 模板生成 12 份 markdown（3 skill × 设计/改进 × 中/英），写到各 skill 的 `docs/` 子目录
4. 用户反馈（msg#140）：「文档中的图片用 mermaid 来画，而不是 ascii，另外用语使用人类的自然语言，类似红旗表之类的表达很奇怪」→ 改 ascii 方框图为 mermaid

## 文档模板（wv-cli）

- **设计文档**：`## Problem Statement` → `## Solution` → `## Architecture` → `## Implementation Decisions` → `## Testing Decisions` → `## Out of Scope` → `## Further Notes`
- **改进文档**：`## Problem Statement` → `## Solution` → `## User Stories` → `## Implementation Decisions` → `## Testing Decisions` → `## Out of Scope` → `## Further Notes`

## 三个 skill 的真实架构（用于 spec）

- **virtuoso-cli**：TCP bridge daemon（本地 socket 监听转发 JSON-line 请求）+ Python API（用户面函数）+ SKILL bridge（Virtuoso 侧执行）；66 commits；特性 F1 session api / connect_by_name / wire_pin / error handling；改进=manual session lookup→connect_by_name、structured error objects
- **block-sim**：5 阶段仿真管线 netlist 提取 → PVT corners → control file → stimulus → LSF 仿真 → 结果解析；改进=删 gen_control/gen_stimulus 改模板、Python 3.6 兼容、viewNLCheck 弹窗抑制
- **block-design**：设计树访谈 + 渐进式构建流程

## reframe（合成方向）

把「在真实仓库里读源码/git log 写 12 份 markdown」（强依赖仓库文件系统 + git 历史）reframe 为 **spec-JSON 驱动「EDA-skill 双语文档生成器 `gen_skill_docs.py(spec, out_dir)->report`」**：纯 Python 读 spec 生成 4 份结构化 markdown（design.md / design-zh.md / improvements.md / improvements-zh.md），含 7 章节 + ```mermaid 架构图（组件名作节点）+ 双语 CJK。判分为静态结构校验 + hidden-B 反硬编码，LIVE-NA，judge_layers=[L0,L1]。

- **A**(visible) spec_A.json = virtuoso-cli（3 组件 tcp_bridge_daemon/python_api/skill_bridge，66 commits，4 features）
- **hidden B**(token-structurally 不同) spec_B.json = block-sim（6 组件 netlist_extractor/pvt_corner_selector/control_file_builder/stimulus_builder/lsf_runner/result_parser，42 commits，4 不同 features）→ A 硬编码器在 B 全错
- **reference** gen_skill_docs.py spec 驱动通用实现（_validate 必填字段→malformed valid=False+errors；_mermaid_design 组件→target 节点图；_mermaid_improvements feature 链式图；4 文件 en/zh 各 7 章节）
- **check.py 18 conds(a-r)**：a zip 含 py ②b py_compile ③c A valid+4文件 ④d A design 7 章节 ⑤e A improvements 7 章节(含 User Stories) ⑥f A design ≥1 mermaid ⑦g A design 无 ascii-art 块 ⑧h A zh 含 CJK 且 en 无 CJK ⑨i A mermaid 含全部组件名 ⑩j A design 含 skill_name+架构词 ⑪k A improvements 含 commit_count+全部 feature ⑫l malformed→valid=False+errors ⑬m B valid+4 文件 ⑭n B design 含 B skill_name+B 组件 且 ≠A 内容 ⑮o B zh 含 CJK ⑯p 源码无 A 专属字面量 ⑰q B design 无 A 专属字面量 ⑱r B mermaid 含全部 B 组件名

## 自验

- ref check.py PASS（A+B+malformed+反硬编码全过）
- negative_selftest 5 neg 全 FAIL（naive_empty→c / naive_print_expected→c / naive_core_deleted→d / hardcode_a→l / missing_gen→a）
- SKIP_RUN=1 eval/run_one.sh 部署通过，workdir clean 无泄漏
- sha 三方同步（disk==JSON test==metadata.check_sha256=678791bf…），k_check=k_rationale=18
