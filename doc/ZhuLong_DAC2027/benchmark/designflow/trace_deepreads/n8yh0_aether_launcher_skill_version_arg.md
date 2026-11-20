# Deepread: 1793241802885_n8yh0 — aether-launcher skill 版本参数化改造

**session**: 1793241802885_n8yh0
**user**: jcgu
**host**: 10.129.32.236 (hfeg0pin003)
**match_count**: 124 (aether:1442; drc:172; analog:48; pyaether:24; waveview:18; netlist:16; lib.defs:16; skipper:14)
**domain**: layout_aether (skill-config / env-config 子型)
**date**: 2026-10-30
**msgs**: 71 total (10 real user-text turns, 6 distinct user tasks)

## 用例选用轮

**U#0** (msg#0, 逐字原文):
> 修改一下aether-launcher这个skill，shell脚本中cd路径为/proj/项目名/版本名/workdir/jcgu,项目名和版本名从输入获得，输入没有版本名时，默认为V0

**判定**: 单一明确 skill-modification 意图。用户提出需求（加版本名参数到 cd 路径，缺省 V0），未给出根因或修复方案 → 符合 A 档选轮规则。本 case 只取 U#0。

**后续用户轮（分离子任务，不取）**:
- U#38: 调用 aether-launcher skill（技能已改完后执行）— 分离的 skill-execution 任务
- U#59: "source和bash的区别" — 分离的 Q&A
- U#61: "[aether-launcher] aether版本...项目drcoa,版本V0" — 分离的 skill-execution
- U#67: "[aether-launcher] aether版本...项目train,版本AI_drcqa" — 分离的 skill-execution

## assistant 工具链 (msg#1–#37)

1. `get_agent_policy_status` + `list_allowed_files` (×5): 确认 policy + 定位 skill 目录
2. `read_files` SKILL.md: 读取原始 aether-launcher SKILL.md (4346 bytes on disk, 含 YAML frontmatter)
3. `editor` (×9 targeted edits): 对 SKILL.md 做以下修改——
   - **目标 section**: 拆分为 3 类输入（项目名 / 项目版本名 缺省 V0 / Aether 程序版本号）
   - **验收 start_aether.sh**: cd 路径 `/proj/<项目名>/V0/workdir/jcgu` → `/proj/<项目名>/<版本名>/workdir/jcgu`，注明 `${2:-V0}`
   - **输出命令**: `start_aether.sh <项目名>` → `start_aether.sh <项目名> <版本名>`
   - **输入 section**: work 目录路径加 `<版本名>` 段，新增 **版本名** 条目
   - **可用工具**: `/proj/<项目>/V0/workdir/` → `/proj/<项目>/<版本名>/workdir/`
   - **start_aether.sh 脚本内容**: 新增 `VERSION=${2:-V0}`，`WORKDIR="/proj/${PROJECT}/${VERSION}/workdir/jcgu"`，Usage 注释加 `[version]`，Example 加 `V0`
   - **给用户的汇报**: 手动运行命令加 `<版本名>`
   - **metadata 最后更新**: 2026-10-26 → 2026-10-29
   - **方法论**: "先确认版本号与项目名" → "先确认项目名、版本名与 Aether 程序版本号"
4. `read_files` SKILL.md (msg#27): 验证最终文件一致性
5. `search_codebase` (msg#35): 确认无残留硬编码 `V0/workdir` 引用

## 真实产物

- **modified SKILL.md** (4811 bytes, on disk at `/home/jcgu/.cline/skills/aether-launcher/SKILL.md`)
- 9 处定向编辑，核心 = `start_aether.sh` 脚本的 `WORKDIR` 行从硬编码 `V0` 改为 `${VERSION}` + 新增 `VERSION=${2:-V0}`

## reframe = mock-behavioral `aether-launcher-skill-version-arg`

**r431 AetherLauncherSkill-001 (19e3k) = CREATE skill from scratch** vs **本例 n8yh0 = MODIFY existing skill to add version param** → 非重复，distinct sessions, distinct intents。

真实 SKILL.md path-dependent（需 jcgu 机器 + cline 环境）→ mock-stdlib：SUT 读固定 `SKILL.md` (text asset) → 写 `solve.py`（接受 `<input_skill_md> <output_skill_md>`，执行版本参数化改造）→ check.py 在隐藏 B/B2 上跑 solve.py 验证。

**mode ③generative-transform**（同 r739 PolicyWritableRootMerge 类族）：SUT 产 transformation script，check.py 在 B/B2 上真跑验证输出。

## BUILD n8yh0 → AetherLauncherSkillVersionArg-001

- **input A**: 真实原始 SKILL.md (jcgu/V0/drvqa, 4346 bytes, from msg#10 read_files)
- **hidden B**: aether-launcher SKILL.md variant (REL2.1/aex/t0002638, 2026.04 版本示例, 2026-11-02 日期)
- **hidden B2**: variant (rev3/chipx/e0031668, 2026.05 版本示例, 2026-11-05 日期, 精简文档风格)
- 三 fixture hardcoded_version (V0/REL2.1/rev3) + project (drvqa/aex/chipx) + username (jcgu/t0002638/e0031668) 八维度全不同 → 反硬编码
- **reference solve.py**: 纯 stdlib，正则提取 WORKDIR 行硬编码版本 → 替换为 ${VERSION} + 插入 VERSION=${2:-V0} + 更新 Usage/Example/doc cd refs/手动命令/输入 section
- **check.py 18 断言 a-r**: a zip 合法 b B exit0 非空 c WORKDIR=${VERSION} d VERSION=${2:-V0} e PROJECT 保留 f Usage 版本参数 g 用户名保留 h doc cd refs <版本名> i 手动命令 <版本名> j 输入 section 版本名 k 非版本内容保留 l B2 cross-input guard m B2 doc transform n bash -n 语法 o 空输入鲁棒 p 确定性 q anti-stub r B2 VERSION+Usage
- **3 negatives**: solve_empty (空壳) / solve_print_gold (硬编 A gold) / solve_no_version (verbatim copy 无变换) → 全 FAIL

## 自验

- reference solve.py: 18/18 PASS ✓
- 3 negatives: 全 FAIL (16/8/10 FAIL distinct) ✓
- §4.9 退化提交 (空壳/print-gold/删核心): 全 FAIL ✓
- k_rationale=k_check=18 ≥8 GATE PASS ✓
- test 字段 byte-iden on-disk check.py (16033B) ✓
