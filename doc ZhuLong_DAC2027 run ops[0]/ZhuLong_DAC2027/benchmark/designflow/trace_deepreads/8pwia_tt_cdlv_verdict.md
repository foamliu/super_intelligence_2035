# Deepread — 8pwia (e0029308 @ hfeg0pkn001, mc112)

session: `1795065039863_8pwia`  · user: e0029308 · host: hfeg0pkn001 (10.129.2.10) · mc=112
agent: lead · 135 msgs (active .messages.json, 716KB; archive 28MB 含更早轮)
扫描: 1119 快照 fresh_B_1119 (r898 取证), r899-r902 用了 cixxj/yy8pd(parked-dup)/f4v84, 本轮选 8pwia

## 项目背景
用户 e0029308 长期维护 `Auto_Check.py` —— 一个 tkinter GUI 自动化工具，跑 Hspice/AMS 仿真链做标准单元真值表验证（"Library VS V" / "CDL VS V" 两种组合流程）。
真实代码路径 `/proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/BK/AI/Auto_Check/`（沙盒 ssh 用户无读权限，但 trace 内 agent 通过 read_files 工具读到了全文）。
关键文件：`Auto_Check.py`(主GUI, 2000+行)、`compare_truth_table.py`(对比模块)、`Hspice_SIM/5_Truth_table_summary.py`、`AMS_SIM/10_CLC_truth_table_summary.py`、`Hspice_SIM/6_dff_hspice_summary.py`、`AMS_SIM/10_dff_all_summary.py`。

## 本 session 的用户任务（按 msg 顺序）
- **Task B (msg 17-58)**: "你看下Hspice侧和AMS侧的最后汇总命名是否一致" → 修正为 "Cell名称是否正确提取电路家族，以及不区分大小写"。结论：CLC 家族提取两侧完全一致(都加 re.IGNORECASE)；发现 DFF 侧 `_norm_cell` 三处大小写不一致(Hspice 有 IGNORECASE, AMS+compare 没有)，用受控替换脚本给 AMS `10_dff_all_summary.py` 与 `compare_truth_table.py` 的 `norm_cell` 加 IGNORECASE。
- **Task C (msg 59-76)** ★本轮选题: "还有个问题，最后我们对比，如果出现仅CDL存在或者V存在这种，两侧数据对不上的，也算做Fall"。实现：`compare_truth_table.render()` 增加「整体判定: PASS/FAIL(原因)」结论行；GUI `_show_compare_popup` 对该行上色(绿/红)；新增 `_show_compare_fail_popup`，把 `if match_all: show_pass_image` 改成 `if match_all: pass else: show_compare_fail_popup`。`match_all()` 语义本就把 only_cdl/only_v/diff 算不通过，本次把"不弹通过图"升级为"红字结论+FAIL弹窗"。
- **Task D (msg 77-105)**: 弹窗文字可复制 + "查看对比结果"按钮也弹出脚本运行日志。新增 `_readonly_select`/`_save_run_logs`/`_show_runlogs_popup`。
- **Task E (msg 106-133)**: 输入类型下拉切换后按钮可选/不可选没切换。根因 `<<ComboboxSelected>>` 事件绑定被覆盖，改 `add="+"`。
- **Task F (msg 134)**: 脚本运行日志弹窗右侧详情不能左右拖动(水平滚动)。← 最后一条 user，active 文件无 assistant 回复(进行中)。

## compare_truth_table.py 关键数据结构（从 trace agent 读出的全文摘录）
```python
def compare(cdl, v):
    # cdl, v: dict family_name -> truth_table_repr
    ks_c, ks_v = set(cdl), set(v)
    same, diff, only_cdl, only_v = [], [], [], []
    for k in sorted(ks_c & ks_v):
        if cdl[k] == v[k]: same.append(k)
        else: diff.append(k)
    only_cdl = sorted(ks_c - ks_v)
    only_v   = sorted(ks_v - ks_c)
    return {'cdl':cdl, 'v':v, 'same':same, 'diff':diff,
            'only_cdl':only_cdl, 'only_v':only_v}

def match_all(cdl_path, v_path):
    r = compare(...)  # 实际从文件读
    return bool(r['same']) and not r['diff'] and not r['only_cdl'] and not r['only_v']

def norm_cell(name):
    return re.sub(r'(?:DBCP|FSP)\d+H\d+L\d+W\d+T\d+[A-Z0-9]*$', '', str(name))
    # 本 session 改为加 flags=re.IGNORECASE
```
render() 本 session 增加的结论行逻辑（trace msg 62 设计 + msg 76 验证）：
```python
nd, noc, nov = len(diff), len(only_cdl), len(only_v)
if not same or nd or noc or nov:
    reason = "；".join([t for t in [
        ("不同%d个"%nd) if nd else "",
        ("仅CDL %d个"%noc) if noc else "",
        ("仅V %d个"%nov) if nov else "",
        ("无一致家族") if not same else "",
    ] if t])
    overall = "FAIL(" + reason + ")"
else:
    overall = "PASS"
L.append("整体判定: " + overall)
```
验证用例（msg 76）：
- PASS → `整体判定: PASS`
- 仅CDL 1 + 仅V 1 → `整体判定: FAIL(仅CDL 1个；仅V 1个)`
- diff 1 + 无 same → `整体判定: FAIL(不同1个；无一致家族)`

## 选题判定
- Task C 是用户真实意图(msg 59 原话)，本 session 已完成并验证。
- 交付物可独立检查：纯 Python 对比+判定模块，无需 GUI/tkinter 显示。
- 与现有 e0029308 case 不重复：
  - CellFamilyExtractGen-001(cixxj/r899) 是家族"提取器"——本题是"对比判定器"(family 已在汇总文件里给出)，角度不同。
  - SimlibMatchAnalyze / SimLogCompareReport / FinesimConvCompare / NetlistMisModCompare / DffPvtCompareGen —— 域与对象均不同(Verilog simlib匹配 / sim日志 / FineSim收敛 / 网表mis_mod / DFF PVT表)，本题是 CDL(Hspice) vs V(AMS) 真值表两侧对比 + 仅CDL/仅V判FAIL + 整体判定行。
- portability-reframe 第 N 实证: Q&A/"也算做Fail"确认 → produce `tt_cdlv_verdict.py` 通用真值表对比判定器。

## 拟造任务形态
produce-generator: `tt_cdlv_verdict.py`
- 输入: 两个真值表汇总文件(CDL侧 + V侧)
- 输出: 文本render(含「整体判定: PASS/FAIL(原因)」行) + `--json` 模式输出结构化 {same,diff,only_cdl,only_v,verdict,reason}
- 判分: hidden B(不同家族/不同混合/结构性不同) 上验 same/diff/only_cdl/only_v 集合 + verdict + render 整体判定行 + 退化提交FAIL
