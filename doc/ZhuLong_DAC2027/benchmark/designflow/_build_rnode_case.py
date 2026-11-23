#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the case JSON for RnodeScatterScript-001, embedding check.py as test."""
import json
import os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CHECK = os.path.join(BASE, "reference", "RnodeScatterScript-001", "check.py")
OUT = os.path.join(BASE, "cases", "C", "EDA-Eval-DesignFlow-RnodeScatterScript-001.json")

with open(CHECK, "r", encoding="utf-8") as f:
    check_src = f.read()

prompt = '''# 任务：实现 pyAether layout 自动化脚本 rnode_scatter.py

## 真实场景（来自真实 trace，仅掩码 key/token）

用户 junweiw（layout 工程师）在 hfeg0pkn001（ip 10.129.2.10）上用 opencode（cline）迭代
pyAether layout 自动化脚本，工作目录 `/ai_sandbox/drcpa/V0/agentdir/junweiw`，
脚本输出路径 `/home/junweiw/script/`。session `1794967961276_dp48n`，match_count=132，
pyaether:547 / drc:358 / aether:181 / cellview:114 / lvs:36 → layout_aether 域。

真实 agent 交付了 `rnode_scatter.py`：在指定 Power Net 的 M1/CT 孔位置撒 "M1 RNODE"
标记，供 Rscalc 做电源网络电阻（Grid/IR）提取。

## 用户原始需求（2 条，逐字保留）

1. 「帮我写一下用在 layout 中的脚本，脚本放在这个路径下 /home/junweiw/script。
   功能，帮助我在每个 m1/CT 孔的位置打上 M1 RNODE 这个层次，启动脚本，调出 GUI 界面，
   可以跟脚本 auto via tool 的方式类似，填写我们需要给哪些 power nets 上撒 RNODE，
   将生成的每种 power RNODE 做成一个 cell，要是存在多个，将每个 power RNODE 汇总成一个
   top cell，放置 cell lib 库可以自定义，要是有哪些不明白的可以随时问我应该怎么设置」
2. 「修改一下，用 label 代替 pin，pin 占用不会比较大，label 比较小」

## 你要交付的脚本：rnode_scatter.py

单文件 Python3，`import pyAether as ae`，实现以下**公开函数契约**（判分器据此调用）：

```python
def rnode_scatter_run(lib, nets, rndLayer='M1', rndPurpose='RNODE',
                      ctLayer='CT', ctPurpose='drawing', boxSize=0.0,
                      cellPrefix='RNODE_', topCell='', alwaysTop=False,
                      markMode='label'):
    """主流程：在当前打开的 layout cellview 中，对 nets 里每个 power net，
    在其 M1 图形范围内的 CT 孔中心撒 RNODE 标记，每个 net 生成一个 cell；
    当 net 数 > 1（或 alwaysTop=True，或显式给 topCell）时，再生成一个 top cell
    把各 net 的 cell 作为 instance 汇总。返回 True 成功 / False 失败。"""

def rnode_scatter_gui():
    """弹出 GUI 界面（aeCreateAppForm），让用户填写 lib / power net 列表 /
    RNODE 层 / CT 层 / 标记方式 / 尺寸 / cell 前缀 / top cell 名 / 是否总生成 top。"""
```

## 核心逻辑要求

1. **收集 RNODE 点**：遍历当前 cellview（`ae.aeGetCurDesign()`）的 shapes，筛选属于目标
   net（`shape.net.name`，去掉 `!` 后缀大小写不敏感匹配）且 layer==rndLayer /
   purpose=='drawing' 的 M1 金属图形；对每个 M1 图形调用
   `ae.dbGetTrueOverlapsEx(cv, shape.bbox, ctLayer, ctPurpose, 0, 0)` 查 CT 孔，
   取每个 CT 孔 bbox 的中心 `(cx, cy)` 与最大边长 `ct_size`，去重。
2. **每 net 建 cell**：`ae.dbNewCellView(lib, cell, 'layout', 'layout')` 新建 cell；
   对每个点用 **label 模式**（默认，`ae.dbCrtLabel(cv, layer=rndLayer, purpose=rndPurpose,
   point=ae.emyPointF(cx,cy), textName=net, justify='centerCenter', orient='R0',
   font='roman', height=...)`）放标记；rect 模式（`ae.dbCrtRect3X`）作为可选退化。
   label 高度建议 = ct_size * 0.2（参照 IMClePGnet 约定）。`ae.dbSaveCV` + `ae.dbCloseCV`。
3. **Top cell 汇总**：当 net 数 > 1（或 alwaysTop / 显式 topCell 名）时，
   `ae.dbNewCellView` 建 top cell，对每个 net cell 用 `ae.dbCrtInst(cv=cv_top,
   point=(0,0), lib=lib, cell=sub, view='layout', inst='I_i', orient='R0')` 放 instance。
4. **GUI**：`ae.aeCreateStringField` 建字段（lib / nets / rndLayer / ctLayer / markMode /
   size / cellPrefix / topCell / alwaysTop），`ae.aeCreateFormButton` 建按钮，
   `ae.aeCreateAppForm` 组装，`ae.aeDisplayForm` 显示；OK 回调里解析字段并调
   `rnode_scatter_run`。
5. **cell 名冲突**：用 `ae.dbCVExist(lib, name, 'layout')` 检测，已存在则追加 `_1/_2`。
6. **库存在性**：用 `ae.dmGetObj(lib)` 检测目标库。

## 附件

- `config_a.json`：示例 mock layout 配置（2 nets VDD!/VSS!, 4 CT vias），仅供理解
  「mock layout 长什么样」，不进判分。判分器用隐藏的 config_b.json（不同的 net 数 /
  via 数 / lib / cell 名）跑你的脚本。

## 交付

把 `rnode_scatter.py` 打包成 `outputs/submit.zip`（zip 根目录下就是 rnode_scatter.py）。'''

case = {
    "task_id": "EDA-Eval-DesignFlow-RnodeScatterScript-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "benchmarks/EDA-Eval-DesignFlow/assets/RnodeScatterScript-001/config_a.json",
        "benchmarks/EDA-Eval-DesignFlow/assets/RnodeScatterScript-001/task_brief.md",
    ],
    "expected_artifacts": ["rnode_scatter.py"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "junweiw",
            "host": "hfeg0pkn001",
            "session_file": "1794967961276_dp48n/1794967961276_dp48n.messages.json",
            "match_count": 132,
            "real_task_summary": "junweiw (layout 工程师) 在 hfeg0pkn001 (ip 10.129.2.10) 用 opencode/cline (deepseek-v4-flash) 迭代 pyAether layout 自动化脚本，cwd=/ai_sandbox/drcpa/V0/agentdir/junweiw，脚本输出 /home/junweiw/script/。session 1794967961276_dp48n 99msgs/618KB/status=idle。关键词 pyaether:547/drc:358/aether:181/cellview:114/lvs:36/layout_aether 域。真实任务(U#0 主任务+U#62 refinement): 产出一个 pyAether layout 脚本 rnode_scatter.py —— 在指定 Power Net 的 M1/CT 孔位置撒 'M1 RNODE' 标记(供 Rscalc 做电源网络电阻 Grid/IR 提取)，默认用 label(U#62 要求 label 代替 pin，label 占地小)，每个 power net 的 RNODE 生成一个 cell，多个 net 时汇总成一个 top cell(dbCrtInst 放 instance)，目标 cell lib 可自定义，带 GUI 界面(aeCreateAppForm 填 lib/nets/层/标记方式等)。agent 工具链: skills(eda_agent)+RAG search_apis/get_api_details(aeCreateRect/dbNewCellView/dbCrtInst/emyShapeGetNetName/aeCreateFormButton/aeCreateStringField/aeCreateAppForm)+run_approved_command(grep CAD 源码找 RNODE 真实用法→IMCutRscalcFlow.py/IMClePGnet.py)+editor(写 rnode_scatter.py/README)+run_approved_command(python-runner py_compile+mock pyAether stub 逻辑自检，pyAether sandbox offline 故仅静态+mock 验证)。可判分子问题=rnode_scatter.py 脚本结构+mock pyAether 录制 API 调用判分。",
        },
        "domain": "layout_aether",
        "subpattern": "rnode_scatter_pg_label",
        "test_rationale": "14 条断言：①submit.zip 合法且含 rnode_scatter.py(§4.9a 空壳/缺文件 FAIL) ②rnode_scatter.py py_compile 通过 ③AST 定义 rnode_scatter_run 函数(只 print 无函数 FAIL) ④AST 定义 rnode_scatter_gui 函数 ⑤AST 引用 dbCrtLabel(label 模式，用户 U#62 refinement 要求 label 代替 pin；删核心 dbCrtLabel FAIL) ⑥AST 引用 dbNewCellView(cell 创建) ⑦AST 引用 dbCrtInst(top cell instance 汇总) ⑧AST 引用 RNODE purpose 字符串 ⑨AST 引用 aeCreateAppForm(GUI 界面) ⑩mock pyAether 下 import 成功 ⑪mock B(3 nets VDD!/VSS!/AVDD! 6 vias lib=REF_LIB_B)运行 rnode_scatter_run 返回 True 且建≥3 net cell ⑫dbCrtLabel 调用≥6 次且 textName 覆盖 3 个 net ⑬dbCrtInst 调用≥3 次(top 汇总 3 instance) ⑭跨输入守卫:mock A(2 nets 4 vias)运行建≥4 label+≥2 inst+≥2 net cell，且 A label 数≠B label 数(反硬编码：硬编 B 6-label 结构在 A 上仍产 6 label→A==B FAIL)",
        "k_rationale": 14,
        "k_check": 14,
    },
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(case, f, ensure_ascii=False, indent=2)
print("wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
