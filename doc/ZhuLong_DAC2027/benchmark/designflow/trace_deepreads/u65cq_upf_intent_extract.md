# Deepread: 1793843123624_u65cq — UPF 电源意图提取脚本

- **session**: `1793843123624_u65cq.messages.json` (1,776,328 bytes)
- **user / host**: e0047472 / hfeg0plg53 (10.129.35.69) — 也在 hfeg0plg87/hfeg0plg99 有副本
- **match_count**: 189；keywords: dbget:570; innovus:493; netlist:330; pyaether:309; virtuoso:265; calibre:251; aether:234; techfile:129
- **tools used**: dbGet 567, netlist 286, pyAether 177, calibre 130, innovus 51, schematic 27, virtuoso 24, dbCreateRect 12, dbCreateInst 11, synthesis 5
- **msg count**: 372 (user 199 / assistant 173)
- **domain**: pnr_signoff (low-power 后端 + Innovus + UPF 电源意图)
- **case**: EDA-Eval-DesignFlow-UpfIntentExtract-001 (A.jsonl #241)

## 会话性质
探索性 Q&A session，用户用拼音/中文混合提问，话题横跨 Innovus dummy 命令、calibre 结果查看、CDL、tcl/python 文本截取、qrcTechFile 抽取、virtuoso/Aether GUI 插件、UPF 格式与 PG 连接、retention cell、DFM via、filler cell 报类型、shield net、auto-generate UPF 脚本。共 ~50+ 独立小问。

## 选中任务（idx 170, u#24）
原话：**「写一个 Python 脚本自动提取 UPF 里所有域/供电网/开关的清单，输出到home目录」**

这是整段 session 里唯一一个有**清晰可验证交付物**的连贯任务，其余多为问答/查命令（不适合做 design_flow case）。

## Agent 实际工作流（idx 170–192）
1. 写 `upf_extract.py`：UPF 解析器，处理续行/注释/嵌套花括号，提取 电源域/供电端口/供电网/供电集合/电源开关/隔离/电平转换/保持 8 类清单，输出报告到 `~/upf_report.txt`。
   - 脚本太长，分 3 次 editor 写入（PART1 + `# __PART2__` 占位 → 替换 PART2 → 替换 PART3）。
2. 造测试 `test.upf`：2 个 power domain (PD_TOP/PD_CPU)、3 supply port、4 supply net (含 -reuse)、1 power switch (SW_CPU, VDD→VDD_SW)、1 isolation (clamp 0)、1 retention、1 level shifter；含续行/注释/嵌套花括号/`create_supply_set`/`map_power_switch`/PST 等干扰项。
3. 首跑 `python-runner` 退出 0 但报告为空 → 定位：传参时把脚本路径重复当 UPF 输入（runner 自动把 filePath 作为 argv[0]），脚本把自己当 UPF 解析了。
4. 修正参数重跑 → 解析成功，Summary: domains=2 supply_nets=4 switches=1 iso=1 retention=1。
5. read `upf_report.txt` 验证 8 段内容齐全 → 宣称交付。

## test.upf（trace-faithful 可见示例 A，已用作 sample.upf）
见 `assets/EDA-Eval-DesignFlow-UpfIntentExtract-001/sample.upf`（与 agent 造的 test.upf 一致，含 PD_TOP/PD_CPU、SW_CPU、PD_CPU iso/retention/level_shifter）。

## 我合成的隐藏 B（与 A 不同）
`hidden/hidden.upf`：design_top=chip_top，3 个域 (PD_TOP/PD_GPU/PD_MEM)、5 supply port、5 supply net (VDD_MEM_SW/VDDIO-reuse)、2 power switch (SW_GPU VDD→VDD_GPU / SW_MEM VDD→VDD_MEM_SW)、2 isolation (PD_GPU clamp0/parent, PD_MEM clamp1/child)、1 retention (PD_MEM save_cmd/restore_cmd)、1 level shifter (PD_MEM)。B 与 A 在域数/开关数/隔离数/名字上全不同 → 击败硬编码。

## 判分设计（18 条独立断言，k_check=18）
见 `reference/.../check.py` 的 CONDITIONS (a–r)。独立 oracle 用 token/line-scan（与 ref 的 regex+brace-matching 不同）重算期望。含：
- 结构/键/合法 JSON (a–d)
- 各类计数+名字集合 (e–p)
- 跨输入判别：对 A 跑出 A-期望 (q，击败 hardcoded_A/print_only)
- 3-seed 注释/空行洗牌稳定性 (r)

## 自验
- ref 自跑 check.py：**PASS**（18/18）
- 4 个负样本（naive_empty / print_only / core_removed / hardcoded_A）：**全 FAIL**
- §4.9 三假提交回归：naive_empty=空壳✓FAIL / print_only=只打期望串✓FAIL / core_removed=参考解删核心(去掉 power_switch 解析)✓FAIL
- 断言闸门：k_rationale == k_check == 18 ≥ 8 ✓
- E2E：从 jsonl 取 inlined test 跑 ref → PASS

## 备注
- session 是探索性 Q&A，不是单一大任务；选 idx 170 这一段做 case 是因为它有清晰交付物。其余问答（DFM via/filler cell/dict 排序 等）多为知识性回答，不适合做 design_flow 判分。
- 用户拼音输入未改写，trace_source 保留原值（user/host/session_file/match_count 均真实）。
