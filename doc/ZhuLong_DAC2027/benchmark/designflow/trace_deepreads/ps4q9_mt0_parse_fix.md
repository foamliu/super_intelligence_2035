# Deepread: ps4q9 · Mt0ParseFix-001 · yifansun @ hfeg0pkn001

**Session**: 1794202410355_ps4q9.messages.json
**User**: yifansun @ hfeg0pkn001 (10.129.2.10)
**Found via**: 11-05 重扫令 path(d) fresh-window 直扫 (11-09 00:00→13:40), 35 spice-marker 主机全扫, kw=3 sz=753KB
**Ledger**: un-ledgered (NEW) → claimed 2026-11-09 14:1x
**Domain**: spice_sim (FineSim .mt0 measurement parsing)
**Track**: A-faithful · Level L1

## 用户意图（逐字原文）

U#0 (唯一需求轮): `/home/yifansun/session_record.md  读取这个文件，继续进行这段工作，现在的问题是：result里量侧结果似乎没有抓出来，我们不许要动其他文件，只调整parse_results.py即可`

- **提出需求**: 量测结果没抓出来 → fix parse_results.py
- **用户未给根因**: 用户只说"量测结果没抓出来"(症状), 未指出 .mt0 是列式格式 / `=` 分隔符不匹配
- **用户未给修复方案**: 用户说"只调整parse_results.py即可"(文件范围), 未说如何修
- ✅ 符合 A-faithful 选轮规则

## 对话流 (117 msgs, 1 user turn)

| 阶段 | msgs | 行为 |
|---|---|---|
| 读上下文 | 0-10 | read session_record.md + parse_results.py(原始buggy) |
| 诊断 | 11-40 | 读 .mt0 文件, 发现 FineSim .mt0 是空格分隔列表格式(非 key=value) |
| 修 fix_parse_results.py | 41-90 | editor 多次, 新增 parse_mt0() 列式解析, test_parse_mt0.py 验证 |
| 应用到真文件 | 91-110 | editor 写回 /rundata/.../AI/parse_results.py, 更新 session_record.md |
| 收尾 | 111-117 | 最终验证 4 个 .mt0, 总结根因+修复 |

工具: read_files×15, run_approved_command×16, editor×14, list_allowed_files×13, search_codebase×2

## 根因 (agent 诊断)

原始 `parse_results.py` 用 `=` 分隔符解析 .mt0 (key=value 格式):
```python
if "=" in line and not line.startswith("$"):
    kv = line.split("=", 1)
    v[kv[0].strip()] = kv[1].strip()
```

但 FineSim .mt0 实际是**空格/制表符分隔的列式表格**:
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
.TITLE '** w100_l42_lv FF_0.61V_130C'
        t_delay i_dyn_read_vcc i_dyn_read_vccz ...  temper alter#
     5.7824e-10     5.1124e-05     2.9861e-05 ...  1.3e+02 1.0e+00
```
- Line 1: `$DATA1` (注释, `$` 开头)
- Line 2: `.TITLE` (标题, `.` 开头)
- Line 3: 列标题 tokens (空格分隔的量测名)
- Line 4: 数值 tokens (空格分隔的浮点数)

→ 原始脚本找不到任何 `=` 行 → 所有量测值默认 0.0 → sim_result.txt 全零

## 修复 (agent 实现)

新增 `parse_mt0(content)` 函数, 列式解析:
1. 跳过 `$` (注释) 和 `.` (标题) 开头的行
2. 第一个非注释行 = 列标题 tokens
3. 第二个非注释行 = 数值 tokens
4. `zip(header, data)` 匹配列名与数值
5. Fallback: 保留原 `=` 解析逻辑兼容旧格式

验证: 4 个真实 .mt0 文件解析正确, t_delay/i_dyn_read_vcc 等非零。

## 金标准 (用户接受的结果)

agent 最终总结: "✅ 修复完成：parse_results.py 的 .mt0 解析逻辑" + 在 4 个 .mt0 上验证。
- 交付件: 修复后的 parse_results.py (parse_mt0 函数 + 保留原 sim_result.txt 输出逻辑)
- 资产: 原始 buggy parse_results.py + 4 个真实 .mt0 文件 (从 trace read_files tool_results 提取)

## 资产获取

- 原始 buggy parse_results.py: 从 trace MSG(read_files tool_result, /rundata/.../AI/parse_results.py) 提取, 2129B
- 4 个真实 .mt0: 从 trace read_files tool_results 提取 (w100_l42_lv_FF_0.61V_130C, w100_l42_lvio_TT_0.8V_25C, w117_l46_lvio_FF_0.61V_130C, w100_l42_lvio_SS_0.83V_-40C, sim.mt0)
- 修复版 parse_results.py: 从 trace editor tool_use (new_text) 提取, 4581B
- session_record.md: 从 trace read_files 提取 (项目上下文: DpMuxTop_2 DDR IO pad, 60 variants × 10 PVT corners, FineSim ALPS)
- 注: /proj/ddgoa/V0/workdir/yifansun/ 权限拒绝(e0031982), 资产全部从 trace 重建

## Case 设计

- **case_id**: EDA-Eval-DesignFlow-Mt0ParseFix-001
- **A (SUT 可见)**: buggy parse_results.py + 4 个真实 .mt0 (results/) + session_record.md
- **B (隐藏)**: 3 个合成 .mt0 (同 13 列格式, 不同 variant 名 + 不同数值 + 不同 HIGH/LOW corner)
- **check.py**: patch O 路径 → run `echo 1.0 | python3 patched.py` on B → 断言 sim_result.txt 14 条
- **k=14**: a(zip含py) b(运行exit0) c(sim_result生成) d(表头格式) e(B1在输出) f(B1=HIGH) g(B1 t_delay>0非零) h(B1 t_delay精确值) i(B1 i_dyn_read>0) j(B1 i_dyn_read=vcc+vccz和) k(B2=LOW) l(B2 i_dyn_read>0) m(B3=HIGH) n(B3 i_dyn_write和精确值)
