# deepread 2m9z2 — junlingw GENGUI 代码审计与清理

**trace**: junlingw @ hfeg0pkn005 (10.129.2.14), session 1795074908715_2m9z2.messages.json, mc=190, pdom=netlist, 748 msgs / 2.3MB
**深读时间**: 2026-11-23 (r1203)
**scp 路径**: `/home/junlingw/.cline/data/sessions/1795074908715_2m9z2/1795074908715_2m9z2.messages.json`（live 路径，非 .snapshot）

## 真实意图（10 轮用户指令）
用户 junlingw 在 `/proj/drvqa/V0/workdir/junlingw/GENGUI/` 让 agent 学习并清理一套**自研 FineSim/HSPICE 测试平台网表生成器**（Python + tkinter GUI，三层架构：知识库 `fgrammar.py` + 引擎 `fengine.py` + 主程序 `finesim_tb_generator.py`）。逐轮要求：

1. "这是GENGUI的路径，你看看学一下" → agent 通读全目录 24 个 .py
2. "我看不懂英文，你用中文输出和思考" → 切中文
3. "finesim_gui.py / finesim_tb_generator.py / finesim_tb_gui.py 有什么区别" → 三变体对比表
4. "哪些文件和 finesim_tb_generator.py 相关" → 五档关联度分类
5. "需要"(清理) → 写 `_scan_imports.py` 做**真实 import 依赖扫描**（行级正则 `^\s*(?:import|from)\s+([\w.]+)`，取顶层模块名，仅留本地模块），给出可删/必留清单
6. "再检查一遍" → 写 `_verify.py`（py_compile 逐文件编译 + import + 引擎实跑生成网表）实证
7. "语法坏的那个文件想实现什么功能？能修吗" → 诊断 `gen_pin_from_net.py`：**模块级 docstring 第 16 行 `"""` 开了头，第 38 行漏闭合**，Python 一直读到第 40 行函数 docstring 报 SyntaxError；agent 复制到可写根补 `"""` 闭合，py_compile OK
8. "对 check_all.py 进行了修改，你再检查一次" → `check_all.py` 第 18 行 `sys.path.insert(0, "...GENGUI//home/wzj")` 拼错指向不存在目录，已修为 `"...GENGUI/"`
9. "列一个要保留的清单" / "肯定没用的文件列表" / "把无用的删了" → 删 12 个无用文件（finesim_grammar/finesim_engine 吊空平行副本、finesim_gui/finesim_tb_gui 损坏/半成品、gengui/build_gui/assemble_gui/build_tb_gui/write_tb_gui 生成器、gen_pin_from_net/explore_g5_models/test_preview 废弃），剩 14 个全编译 OK
10. "ui窗口太小了…窗口做大一点" → 改 `__init__` geometry；并修 `_dlg` 回调 `for k,e: result[k]=e.get().strip(); d.destroy()` 在循环里就销毁对话框的 bug（先收完所有值再 destroy）

## agent 的三套实证脚本（核心可离线判分内核）
- `_scan_imports.py`：行级正则抓 import → 本地模块依赖图 → 报 0 引用吊空模块（finesim_grammar/finesim_engine 0 引用确认可删）
- `_verify.py`：py_compile 逐文件编译 + import 测试 + 引擎 `generate()` 实跑产出 `.end` 结尾网表
- `_audit.py`：综合审计（core import + PROCESS 完整性 + 路径可写性 + check_* 作用域）

实际 import 图（GENGUI 24 文件，agent 扫描结果）：
- `check_all → fgrammar`；`finesim_gui → fengine,fgrammar`；`finesim_tb_generator → fengine,fgrammar`
- 其余 21 文件本地 import = []（含吊空的 finesim_grammar/finesim_engine 平行副本）

## 抽题判断
真实意图 = **对 Python 代码库做依赖审计 + 死文件检测 + bug 修复**。GUI 改动/删除操作依赖可写根 + tkinter 显示，无法离线判分。可离线判分的纯 Python 内核 = **模块依赖图审计器**：读 .py 目录 → 行级正则抓本地 import → 入度 + 入口点(__main__) + 语法正确性(py_compile) → 按 broken/entry/core/orphan 互斥优先级分类 → 输出 audit_report.json。

**case_id**: EDA-Eval-DesignFlow-PyDepGraphAudit-001（domain=schematic_netlist, level=L1）
- A（可见，12 文件）: core/engine/helper(core) + main/gui/builder/check(entry) + orphan1/orphan2/dup_core/stale(orphan) + broken(broken, 未闭合 docstring，import 了 core 故 core inbound=4)
- B1（隐藏，14 文件）: netlib/simcore/util(core) + runner/viewer/validator/tool(entry) + dead1-3/junk/legacy(orphan) + crasher/half(broken，两种不同语法错) — 与 A 文件名/数量/图/集合全不相交
- B2（隐藏，8 文件）: parser/model(core) + app/cli(entry) + unused1-3(orphan) + bad(broken) — 第三套结构，反硬编码 A 与 B1
- k_check=15（①zip含脚本 ②B1 exit0+合法JSON ③B1 files=14反A=12 ④B1 inbound全匹配 ⑤entry_point全匹配 ⑥syntax_ok全匹配 ⑦class优先级全匹配 ⑧orphan=5反A ⑨broken=2反A ⑩core=3 ⑪entry=4 ⑫imports全匹配 ⑬确定性3次md5一致 ⑭B2泛化files=8四列表全匹配 ⑮B2 inbound+class全匹配）
- §4.9 三假: print_only（打印 A 分类）/empty_stub（空报告）/hardcode_a（硬编码 A 12 文件分类）全 FAIL（B1 14 文件 + 不同 orphan/broken 名）
- 自验: reference 15/15 PASS + 3 负样本全 FAIL + negative_selftest PASS(BUG):0
