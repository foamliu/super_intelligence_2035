# y6ito · SkillTreeDiffAudit 深读笔记

**session**: `1790578434343_y6ito` · **user**: `binwenh` · **host**: `10.129.8.139` (hfeg0plg88)
**mc**: 46 · **关键词**: aether:886;drc:114;netlist:105;pdk:104;schematic:93;lvs:90;calibre:69;pyaether:39
**domain**: layout_aether (Spice_Agent skill env-config 诊断；2026-11-15 §二 reaudit revival)
**status**: idle (snapshot weekly-new.2026-11-01_2330；session 2026-09-28)

## 选料理由（r794 guidance）
r794 识别 167 fresh C-pure 候选，建议优先非 xinqiaoz 候选增加用户多样性 → 选 y6ito (binwenh)。candidates_mc10.tsv 关键词看似 physical_verify (drc/lvs/calibre)，深读后实际是 **Spice_Agent skill 目录结构 env-config 诊断** —— 正是 2026-11-15 §二 reaudit 复活令覆盖的「env-config / setup 类 / debug-Q&A」（旧规则会判 weak，新标准合法）。

## trace 全貌
74 msgs (45 user / 29 assistant)。无 thinking_blocks。assistant 工具：read_files / list_files / search_codebase / run_approved_command / editor。

## 用户真实意图演进（按真实 user_input 轮，非工具回包）
- **U#0**: 「你加载了哪些 Skill 脚本？」 → 助手列 SKILL.md（Spice_Agent）+ skill-creator
- **U#24**: 「为什么SpiceAgent_Skill/和skills的文件是一样的？」 → 起「两副本相同」疑问
- **U#62**: 「是不是因为你是在skills目录下打开的，所以你现在使用的是skills里面的配置？」 → 假设根因（cwd 影响加载）
- **U#64**: 「这个 SpiceAgent_Skill是通过`sg skilldev -c "cp -r /home/xiao5w/SpiceAgent_Common/SpiceAgent_Skill ~/.cline/skills/"`命令得到的」 → 提供来源线索
- **U#66 (本轮主任务，最末实质请求)**: 「**先检查一下两个副本之间有没有实际的内容差异，再决定怎么处理**」 → 真正交付请求 = 对两副本做内容级 diff 审计

按 A 档选轮规则：U#0/U#24/U#62/U#64 都是「提问/提供线索」（未给方案），U#66 是「提出需求」。U#64 给出 cp 命令是线索不是修复方案 → 可用作 task 上下文。U#66 是任务核心。

## 助手真实工作流（trace-end-gold 形成）
1. U#0-U#23: 列 skills/ 子目录、读 SKILL.md/skill-creator/SKILL.md，识别加载了 Spice_Agent + skill-creator
2. U#24-U#61: 调查为何 SpiceAgent_Skill/ 与 skills/ 内容相同 — `list_files` / `read_files` 检查 `.git/` 两边都是独立 repo、refs/heads/main 都指向 `7aec287e368af09fa5a9c7588bfb2873b0d8c43a`、logs/HEAD 完全一致、`.git/worktrees` 不存在（非 worktree，是 nested clone）
3. U#66-U#72: 写 `tmp_diff_check.sh` (`editor` 工具)，`run_approved_command` 跑该脚本
4. **A#73 (trace-end-gold)**: 删临时脚本，给结论表

## trace-end-gold (A#73 + U#70/U#72 stdout)
**diff 脚本输出 12 节**：
1. 文件级差异（排除 .git / __pycache__）：只在 root 有 `skill-creator/`、`tmp_diff_check.sh`
2. SKILL.md 完全相同 ✓
3. SPICE_AGENT.md 完全相同 ✓
4-8. src/、aether/、knowledge/、memory/、design/ 目录差异：空（无差异）
9. runs/ 差异行数: 1
10/11. only-in-DIR1 / only-in-DIR2（排除 .git / __pycache__ / *.pyc）：空
12. 统计：DIR1=1804 文件 / DIR2=1802 文件 / 两边 git commit 同为 `7aec287e368af09fa5a9c7588bfb2873b0d8c43a`

**A#73 结论**：两副本内容**完全一致**（仅 runs/ 1 行差异，疑换行符），无分叉。
**建议**：方案 A — 以 `SpiceAgent_Skill/` 为正牌技能目录（来自规范源 SpiceAgent_Common/，sg skilldev 更新），清理根目录冗余（保留 skill-creator/）。

## 关键产物
- `tmp_diff_check.sh`（临时脚本，运行后已删除）：bash 调 `diff -r` + `git rev-parse HEAD` + `find ... | wc -l`，按 12 节输出对比报告
- 输出报告（A#73 表格 + 12 节 stdout）

## reframe（pure stdlib · SUT 沙盒不可达用户 home）
真实跑在 binwenh 的 home (1804 文件) 上，沙盒不可达。抽离离线可验核心：
**`skill_tree_diff_audit.py`** — 纯 stdlib (os.walk + hashlib.sha256) 目录树差异审计器：
- 输入：两个目录路径
- 行为：
  - 各自 os.walk 收集文件清单（相对路径）
  - 应用 .gitignore 风格过滤：跳过 `.git/`、`__pycache__/`、`*.pyc`、`*.tmp`、`*~`、`*.swp`、`*.s30p`、`*.s2p`、`*.gds`、`.state.lock`
  - 按 relative path 分组：only_in_A / only_in_B / both
  - both 中按 SHA-256 内容哈希分：identical / differ
  - 统计：A 文件数、B 文件数、各类计数
  - 输出 JSON report：{only_in_A:[...], only_in_B:[...], identical:[...], differ:[...], counts:{...}, verdict: "identical|forked"}
- 不调 git（git commit hash 需 .git/，但 .git/ 已被过滤；可选输出 git_head_a/b 若 .git/refs/heads/main 存在，但本 reframe 简化：跳过 git，专注内容级 diff，与真实 gold 的核心结论「内容是否相同」对齐）

## check() 设计（≥8 独立条件，hidden B anti-hardcode）
check() 在独立临时目录构造 hidden B fixture（不同文件名/大小/内容，与 A visible 完全不同），跑 SUT 提交的 `skill_tree_diff_audit.py`，断言：
a. 退出码 0，stdout 是合法 JSON
b. JSON 顶层含 4 键：only_in_A / only_in_B / identical / differ
c. only_in_A 列表内容正确（hidden B fixture 中只在 A 出现的文件）
d. only_in_B 列表内容正确
e. identical 列表正确（特定文件）
f. differ 列表正确（特定文件，含 same-size-diff-content 用例）
g. .git/ 目录下文件不在任一列表（过滤生效）
h. __pycache__/*.pyc 不在任一列表
i. *.tmp 文件不在任一列表
j. counts.A / counts.B / 各类计数正确
k. verdict 字段逻辑正确（有 differ→"forked"，无→"identical"）
l. 确定性：2 次运行 byte-identical
m. 错误处理：不存在目录 → 退出码非 0
n. anti-hardcode：hidden B 文件名/内容与 visible A 完全不同，输出必须反映 hidden B 而非固定串

## 档位
B 档 (synthesized)：visible A 用合成小 fixture（不 ship 1804 文件），hidden B 不同 fixture anti-hardcode。
不选 A 档原因：trace-faithful 需要用户实际 home 目录的 1804 文件，无法经 MCP 透传到 SUT 沙盒，且文件涉及生产 Spice_Agent skill 代码（含 EDA 工具配置）不宜外发；reframe 为纯 stdlib 是必须的，故 B 档。

## 子型
skill-tree-diff-audit (env-config debug-Q&A revival)

## 2026-11-15 §二 reaudit 适用性
- 旧判定会归为「env-config / setup / Q&A → weak 不可造」
- 新标准：env-config 是真实用户意图，合法
- 唯一排除标准检查：①有真实 trace ✓ (y6ito) ②能写出有牙 check() ✓ (12+ 独立条件 + hidden B + 三假 FAIL)
