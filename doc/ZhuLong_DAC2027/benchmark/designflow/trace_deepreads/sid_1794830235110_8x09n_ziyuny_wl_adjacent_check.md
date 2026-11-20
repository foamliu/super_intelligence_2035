# 深读笔记 — session 1794830235110_8x09n (ziyuny @ hfeg0pnd001)

> trace 深读 · 2026-11-19 · shard C · 用于 case `EDA-Eval-DesignFlow-WlAdjacentCheckRundrc-001`

## trace 元数据

- **session_file**: `1794830235110_8x09n.messages.json`（1.39MB，352 msgs，167 assistant，185 user）
- **user**: `ziyuny` @ `hfeg0pnd001`（physical_verify 域，mc=426）
- **时间**: 2026-11-15 ~ 11-18（R#0 ts=1794830236 ~ R#19 ts=1795006540，跨 3 天）
- **agent**: zhulong（lead），工作目录 `/home/ziyuny/zl/wl_adjcent`
- **真实产物**（在 hfeg0pnd001 上确认存在）:
  - `/home/ziyuny/.cline/skills/wl-adjacent-check/SKILL.md`（149 行，v0.2）
  - `/home/ziyuny/.cline/skills/wl-adjacent-check/references/{absolute-path.md, troubleshooting.md}`
  - `/home/ziyuny/zl/wl_adjcent/rundrc.sh`（75 行，v2 模板）
  - `/home/ziyuny/zl/wl_adjcent/{wl_adjacent.drc, parse_wl_pairs.py, runme, test.sh, wl_adjacent_run.drc, 12× wl_pairs_*.rep, ...}`

## 用户真实意图（R#0-R#19 逐条）

| # | 用户原话（逐字） | 意图 |
|---|---|---|
| R#0 | 你的工作目录是/home/ziyuny/zl/wl_adjcent | 设定工作目录 |
| R#1 | 你先读一下这个问题wl_adjcent_llm.md，我现在需要对这个文件里提及的需求做整个flow的串起来的skill | **核心需求**：把 WL 相邻检测全 flow 串成 skill |
| R#2 | 串起来的流程，其实就是两个run文件的内容，rundrc.sh跑calibre drc抓取特定的wl的violation; runme跑python脚本对drc结果做分析...现在每次的变量就是--pattern会变化 | flow = rundrc.sh + runme；变量 = --pattern |
| R#3 | 你读一下wl_adjacent.drc这个文件，告诉我查找逻辑是什么 | 读 deck 理解查找逻辑 |
| R#4 | deck中和python代码中的pattern其实是同一个...deck中的正则表达式写法和python中的并不一样，你学习一下calibre svrf语言中的正则表达式相关的写法 | **S1 翻译需求**：Python regex ↔ SVRF pattern |
| R#5-R#12 | 我需要对沙箱的环境做测试，你直接运行rundrc.sh / 继续 / 重新跑rundrc.sh / 执行机有calibre的安装包吗 / bsub 指定queue的主机... / 运行test.sh | 跑 rundrc.sh 调试（VCO/bsub/PATH 问题） |
| R#13 | 注意 这里的drc python 代码等文件，跑得shell命令和脚本中，都要写全路径，这一点将来要写入到skill中去 | **绝对路径纪律** |
| R#14 | rundrc.sh我需要做成一个template,输入是rundir；第一步是cd到rundir下面去，第二步是规定CALIBRE_BIN，第三步是bsub跑这个drc | **S2 rundrc.sh 模板化** |
| R#15 | （4972 字 skill_instructions）wl-adjacent-check skill 完整规格（目标/边界/绝对路径纪律/输入契约/流程 S1-S5/产物判读/三信号/排错） | 用户自己写好的 skill spec（含 SVRF 翻译规则） |
| R#16 | /skill-creator 帮我新建一个skill,名字叫wl-adjcent-check。这个skill的作用是检查版图gds中用户指定的特定名字（有规律）的相邻wl之间的space | 调 skill-creator 建 skill |
| R#17-R#19 | 现在我想调用skill-creator / 继续 / 继续 | skill-creator 执行 |

## trace-end-gold（r786 MEMORY 误判「无 gold」，本深读推翻）

助手末轮 @A#165（ts=1795006570524）输出完成总结：
> ✅ **`wl-adjacent-check` skill v0.2 重建并安装完成。**
> - SKILL.md 149 行（frontmatter + 绝对路径纪律 + 输入契约 + S1-S5 + 判读表 + 三信号 + 验收 + 陷阱 + 资源）
> - references/{absolute-path.md, troubleshooting.md}
> - rundrc.sh v2：参数化 rundir/space_um/svrf_pattern，sed 自动生成运行 deck，bsub 提交
> - 10/10 测试通过（缺省运行 / 改阈值 / bad rundir / 非数字 / 太小 / 含 |& / ...）
> - INDEX.md 登记

用户末轮 R#19「继续」→ 助手完成总结，**无后续用户修正** = trace-end-gold 成立。
真实产物在 hfeg0pnd001 上确认存在（SKILL.md 149 行、rundrc.sh 75 行字节匹配）。

## SVRF 翻译规则（R#4 + R#15 + SKILL.md S1，逐字）

| 规则 | Python 正则 | → SVRF NET pattern |
|---|---|---|
| 去 ^$ 锚点 | `^H_WL[oe][0-9]*<[0-9]+>$` | `H_WL?<?>` |
| 字符类 `[...]` → `?` | `[oe]`→`?`；`[0-9]`→`?` | |
| 量词 `*` `+` `{n,m}` → `?` | `[0-9]*`→`?`；`[0-9]+`→`?` | |
| **连续 variable atom 折叠成单个 `?`** | `[oe][0-9]*`→`?`（非 `??`） | |
| 转义 `\x` → 字面量 `x` | `\.`→`.` | |
| 字面量直写不转义 | `H_WL` `<` `>` 直写 | |
| 自检：宽松超集 ⊇ Python 严格版 | （枚举验证） | |

**金标准**：
- `^H_WL[oe][0-9]*<[0-9]+>$` → `H_WL?<?>`（2 个 `?`：`[oe][0-9]*` 折叠成 1 个，`[0-9]+` 1 个）
- `^s[0-9]+m[0-9]+wl[oe]<[0-9]+>$` → `s?m?wl?<?>`（4 个 `?`，每个 var run 1 个）

## rundrc.sh v2 模板逻辑（R#14 + R#15 + 真实 rundrc.sh 75 行）

```
RUNDIR=${1:-/home/ziyuny/zl/wl_adjcent}     # 不存在 -> rc=1
SPACE_UM=${2:-0.182}                          # 非数字 -> rc=1; <0.01 -> rc=1
SVRF_PATTERN=${3:-H_WL?<?>}                   # 含 |&\ -> rc=1
CALIBRE_BIN=/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibre
deck prep: 若 SPACE≠0.182 或 SVRF≠H_WL?<?> 则
  sed 's|< 0.182 OPPOSITE|< $SPACE OPPOSITE|g; s|"H_WL?<?>"|"$SVRF"|g' \
    wl_adjacent.drc > wl_adjacent_run.drc
bsub -q pv -env "USE_CALIBRE_VCO=aoi" -o $RUNDIR/drc.log $CALIBRE_BIN -hier -drc $DECK
```

deck 替换锚点（wl_adjacent.drc 实测）：
- 4 处 `"H_WL?<?>"`（NET 选网，行 158-161：wl_hsp/wl_m1/wl_m2/wl_m3）
- 3 处 `< 0.182 OPPOSITE`（EXTERNAL，行 209-211：wl_gaps_m1/m2/m3）

## reframe 决策

真实 `rundrc.sh` 是 bash 调 `bsub`/`calibre`，SUT 沙盒不可达 LSF/Calibre。
真实 SKILL.md 是 agent-skill 元数据 + prose，离线不可「跑」。
**Reframe 为纯 stdlib Python 脚本 `wl_adjacent_check.py`**，保留两个离线可验证核心：
- ① S1 `python_regex_to_svrf()` 翻译函数（规则逐字抄自 SKILL.md S1 + R#4）
- ② S2 rundrc 模板逻辑（参数校验 + sed 等价 deck 生成 + bsub 命令拼装打印）
bsub 命令**只拼装打印不执行**，符合「模板脚本」语义。

## case 落库

- **case_id**: `EDA-Eval-DesignFlow-WlAdjacentCheckRundrc-001`
- **domain**: physical_verify / **tier**: L1 / **档**: B（synthesized reframe）
- **subtype**: `wl-adjacent-check-rundrc-template`
- **k_check**: 17（a-q；r 退化回归由 negative_selftest 独立验）
- **自验**: ref PASS 17/17；4 negative（empty/print_only/core_deleted/hardcode_a）全 FAIL distinct（c/e/d/j）
- **anti-hardcode**: B 用 `^s[0-9]+m[0-9]+wl[oe]<[0-9]+>$`（SVRF `s?m?wl?<?>`）+ space 0.30，与 A（`H_WL?<?>` + 0.25）完全不同

## r786 MEMORY 修正

r786 parked 8x09n 理由「末尾 mid-skill-creator 无 trace-end-gold」**部分误判**：
- 确实末尾在 skill-creator 流程中（R#17-R#19「继续」）
- 但助手 @A#165 输出了完整完成总结（v0.2 重建 + 10/10 测试通过），且真实产物在磁盘上确认存在
- 用户「继续」后无修正 = 隐性接受 = trace-end-gold 成立
- r786 的「最有希望，SVRF↔Python regex 离线可验核心」判断正确，本深读证产
