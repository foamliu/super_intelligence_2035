# 深读：1791783189298_t2hnp — steveny @ hfeg0pnd001/10.129.32.189 (r279)

**trace**: 1791783189298_t2hnp · steveny@hfeg0pnd001 · mc=336 · 115 msgs · 6 real user turns
**markers**: pyAether 85, virtuoso 34, dbCreateRect 4 (eda_trace 11/06-11/09 聚合)
**shard C · domain: layout_virtuoso**

## 种子（U#0 逐字，A-faithful eligible，提出需求未给根因）
> 通过mcp 工具，获取api和桥接服务，实现：高亮当前打开的virtuoso design的schemetic view 中所有以net 打头的net。注意是virtuoso skill，不是pyaether。用户名是steveny。可参考/home/steveny/context-infrastructure/rules/skills/eda_agent/README.md

## 真实 assistant 工具链 + 产物（grounded from MSG#1–#17）
- 读 `/home/steveny/context-infrastructure/rules/skills/eda_agent/`（README/SKILL.md/00_INDEX/case_007_highlight_nets_by_pattern_skill.md）
- RAG 查 SKILL API：`geMakeProbeWithColor` / `geGetEditCellView` / `geDeleteAllProbe` / `hiGetCurrentWindow`
- 注：`schHiHiliteLabel` 只能按 object-type 高亮所有对象，**不能按名过滤** → 改用 probe+名称正则路线
- 真跑 SKILL（SandBox_MCP_Server__run_code, lang=skill, username=steveny）：
  - `cv = geGetEditCellView()`
  - `geDeleteAllProbe(hiGetCurrentWindow() t)` 清旧 probe
  - `cv~>nets` 取所有 net
  - `setof(n nets rexMatchp("^[nN][eE][tT]" n~>name))` —— case-insensitive 前缀 "net"
  - `geMakeProbeWithColor(?window win ?object n ?color list("y3" "drawing"))` 黄色高亮
- **结果**：目标设计 `auto_steveny_case1/BCenterL/schematic`，匹配并高亮 **80 个** net（不区分大小写），无 error。MSG#17 用户接受。

## 其余 user 轮（U#12+，**另一子任务，不进 seed**）
- U#12「review eda_agent skill 包是否有个人敏感信息」→ 隐私脱敏审查（fmy@960823 密码/steveny/xtli/shaoyou/内网 IP/项目名 → 占位符），跑 sanitize/verify 脚本，残留=0
- U#50「复制到 ~/.cline/skills/ 做格式适配」、U#54/62 续改
- **与 U#0 高亮任务无关，本案不纳入**

## 为何 B 档重定义为离线 L2
真实 Virtuoso/OA `geGetEditCellView`/`geMakeProbeWithColor` 不可沙盒复现。离线核心 = 给定 schematic net 清单 JSON + 高亮配置(pattern/match/case/color) →
1. 按配置过滤 net 名（case-insensitive prefix）→ `matched_nets.json`（cellview/pattern/match/case/color/match_count/matched[]）
2. 生成可在 Virtuoso CIW `load` 的 `.il`：`geGetEditCellView` 守卫 + `geDeleteAllProbe` 清旧 + `setof`+`rexMatchp` 过滤 + `geMakeProbeWithColor(?color)` 高亮

check.py 在 hidden B 上 subprocess 真跑候选脚本，断言输出结构（matched 集合精确 / .il 含必需 API / color·pattern·cellview 随 B 变化非硬编码）。

## B-track 防硬编码
- B cellview `ADCChip/CompA/schematic` ≠ A `auto_steveny_case1/BCenterL/schematic`
- B pattern `in`（prefix, insensitive）≠ A `net`
- B color `g2` ≠ A `y3`
- B net 名词表完全不同；B 含 case 变体 `IN2`/`InBuf`（挫败 naive case-sensitive）、含 `init`/`input`（prefix "in" 真匹配，非 substring 假阳）

## DISTINCT from 现有 layout_virtuoso 系
- HilightCsvGroupGen-001（r279-era）= layout bbox 从 CSV 按 layer 分组高亮（geCreateHilightSet + geAddHilightRectangle），输入是 CSV bbox + layer 规则
- 本案 = **schematic net 按名前缀**高亮（geMakeProbeWithColor probe 路线，因 schHiHiliteLabel 不能按名过滤），输入是 net 清单 + 名 pattern 配置
- 不同输入（net 名 vs CSV bbox）、不同 SKILL API（probe vs hilightSet）、不同过滤（名 regex vs layer 分组）
- r236 SkillBindkeyFlattenMakeCell / r233 InstM0ShapePinIdentify / r232 SkillM1ShapeDeleteAudit / r230 VirtuosoStartupDiag / r211 NoOverlapPcellLayerParse / r207 QaWidthPatternGen 均不同主题
