# r623 deepread — miccao @ hfeg0plg37 / 1789631689135_9pcjd (mc 79)

- **trace**: 56 msgs / 2 real user turns / via .75 ssh to 10.129.32.47
- **domain**: physical_verify (PDK/techlib param audit)
- **user**: miccao (foundry 工艺库维护)
- **session_file**: `/home/miccao/.cline/data/sessions/1789631689135_9pcjd/1789631689135_9pcjd.messages.json`

## 用户原话（逐字）
- **U#0**：「/apps/proplus/autocell.1.2026.8/autocell/examples/dram下所有文件里的参数和/proj/train/ddcpc/libs/TECHLIB_release里面的参数有类似的吗？进行安全性检查，我怕这个工具写死了我们的工艺数据」
- **U#1**：「出一份rep附件，放到/home/miccao/autocell/secuirty下」

## 用户真实意图（任务初衷）
安全性审计：比对 AutoCell 自带 DRAM 教学示例的参数与 CXMT G5 CIP 真实工艺库 (TECHLIB_release) 的参数，确认工具是否"写死"了工艺数据（即示例里是否硬编码了真实工艺库的参数值）。交付物 = 一份安全审计报告 (rep)。

## agent 实际产出（gold）
1. 列出 DRAM 示例 12 文件（run/layers/layer_functions/viadefs/globals/rules/place/route/README.md + 3 sch.cdl）
2. 列出 TECHLIB 18+ 文件（techfile.tf 3353 行 + cdf + lib.defs 等）
3. 逐项比对 7 类参数：Layer 命名/GDS、设计规则值(min_width/min_spacing/min_area)、Via 定义、Device 参数、制造网格、路径引用、PG 网络
4. 写 307 行 6 章报告到 `/home/miccao/autocell/security/AutoCell_DRAM_Example_Security_Check.rep`
   （用户原话 "secuirty" 拼写错误，agent 自动修正为 security）
5. **结论：✅ 安全 — 无工艺数据泄露风险**（DRAM 示例为教学简化值 0.3/0.2/0.5，TECHLIB 为真实精密值 0.1035/0.234/0.312；两者工艺节点差 10 倍；仅 NW/CT 名字相同系行业通用缩写且底层 GDS 编号不同；无外部路径引用）

## gold 报告结构（6 章）
1. 检查范围（数据源 A/B 文件清单）
2. 数据源身份确认（工艺类型/节点/用途/格式/金属层数/Via 种类 9 项）
3. 逐项参数比对（3.1 Layer 命名 16 行 / 3.2 设计规则值 12 项 / 3.3 Via 定义 9 项 / 3.4 Device 参数 12 项 / 3.5 制造网格 / 3.6 路径引用 / 3.7 PG 网络）
4. 安全性评估结论（6 层面综合 → 判定）
5. 建议（4 条）
6. 附录（25 个已检查文件清单）

## 选料判定
- **新标准下合法任务**：安全性审计/分析 = 真实用户意图（2026-11-15 令：analysis/Q&A 全部恢复可造）。用户是工艺库维护者，担忧工具写死工艺数据，是真实的 physical_verify/PDK-audit 任务。
- **reframe 路径**：P-006 (C) 分流 → grounded-extraction-tool。真实 AutoCell/TECHLIB 路径不可达沙盒 → B档 mock-behavioral。deliverable = `autocell_security_check.py`（读 DRAM 示例配置 + TECHLIB 配置 → 提取 7 类参数 → 比对值匹配 → 输出结构化 JSON 报告）。check() subprocess 跑于隐藏 B（B 有硬编码值匹配 = 泄露 → 判 unsafe；A 无匹配 → safe）。grounding 牙 = B 的匹配值由 B 配置动态解析（非硬编 A 金答案）。
- **判分有牙**：A safe / B unsafe(B=4 值匹配) / B2 unsafe(B2=2 值匹配+1 路径引用，与 B 不同) → always-safe/always-unsafe/print-expected 三假全 FAIL。

## 同源组
- same_trace_group: 9pcjd-autocell-param-security-audit (cap-1，本 shard 首例 PDK-param-audit)
- 新子型: autocell-pdk-param-security-audit
