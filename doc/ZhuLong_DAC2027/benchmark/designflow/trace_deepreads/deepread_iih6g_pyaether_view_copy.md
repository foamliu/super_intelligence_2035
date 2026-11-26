# 深读笔记 · iih6g — pyAether view 拷贝 + 可写打开 + instance 计数

- **session**: 1791871316059_iih6g
- **user**: laryu @ hfeg0pkn001
- **match_count**: 265 (tools col: 487 pyAether + 462 dbGet + 88 dbCreatePath + 68 "lang":"pyAether" + 42 cellview + 18 schematic + 4 netlist — pyAether-dominant)
- **size**: 826KB messages.json, 206 msgs
- **domain**: eda_other (Empyrean Aether pyAether Python 自动化)
- **shard**: A

## 用户轮（逐字原文，仅 key/token 掩码——本 trace 无需掩码）

- U#0 (msg[0]): `<user_input mode="act">使用pyAether，先copy一个view为A，然后以可写模式打开，并将A中的instance个数打印出来</user_input>`  ← **本轮 A档任务说明**
- U#23 (msg[23]): `<user_input>` + TOOL_RESULT `先写一个通用脚本，我稍后自己修改`  ← **关键澄清：通用脚本(参数化)**
- U#24 (msg[24]): `<user_input mode="act">这个路径下，lib为A_testLary，cell为BCenterL，view为layout，新的view为layout_laryxi</user_input>`  ← 具体示例值（供脚本默认/示例）
- U#38 (msg[38]): `<user_input mode="act">我要先copy一个view，然后将instance中的pin浮到最上层，我写了这个代码，帮我检查一下 def copView1(...): ...`  ← **rule2 违例（用户给出自己代码求 review）→ 不可作 A档**

## 选轮判定

U#0 = 纯目标（copy view → 可写打开 → 打印 instance 个数），未给根因、未给修复 → 符合 A档选轮规则。
U#23 进一步澄清"先写一个通用脚本，我稍后自己修改" → 强调脚本要通用(参数化)，不是写死 A_testLary/BCenterL。
U#24 给出具体 lib/cell/view 值（A_testLary/BCenterL/layout → layout_laryxi），仅作示例。
U#38 是后续子任务（pin 浮到最上层 + 用户自带代码 review），违反 rule2，不纳入本案任务说明。

## assistant 工具链（msg[1]–msg[37]，对 U#0+U#23+U#24 的响应）

- RAG_MCP_Server__search_apis × 10+ 次：query "copy cell view" / "open cell view writable mode" / "get instances from cell view" / "dbGetInstances design instances count" / "dbOpenCVByType open cell view" / "emyInitAether initialize pyAether" / "dbCloseCV close design cell view" / "design get master instances count length" 等
- RAG_MCP_Server__get_api_details(["dbCopyCellView","aeMakeEditable","aeGetCellView","dbNewCellView"]) + (["dbInstanceQuery","dbFindInst","dbOpenCV"]) + (["dbOpenCVByType"]) + (["emyInitAether","dbCloseCV"])
- SandBox_MCP_Server__run_code(pyAether) 一次（msg#31）：尝试在沙盒执行脚本，**Connection refused by sandbox [pyAether] at 10.129.8.224:52305** → 沙盒不可用，转用 editor 写脚本文件
- editor 写 `/home/laryu/Desktop/copy_and_count_instances.py`（msg#33）→ 用户在 msg#35 read_files 确认，msg#37 assistant 给出说明文档，用户未反驳（msg#38 直接进入下一子任务）

## 金标准（用户实际接受的产物，msg#33 editor 写入的脚本）

`copy_and_count_instances.py`，结构：
1. `import pyAether as pyScript`
2. 顶部配置块 `LIB / CELL / SRC_VIEW / DST_VIEW = "A_testLary"/"BCenterL"/"layout"/"layout_laryxi"`
3. `def main():`
   - `pyScript.emyInitAether('-adv')` — 初始化 Aether
   - `src_cv = pyScript.dbOpenCVByType(LIB, CELL, SRC_VIEW, 'layout', 'r')` — 只读打开源 view
   - `new_cv = pyScript.dbCopyCellView(src_cv, LIB, CELL, DST_VIEW, overWrite=True)` — 拷贝
   - `pyScript.dbCloseCV(src_cv); pyScript.dbCloseCV(new_cv)` — 关闭
   - `writable_cv = pyScript.dbOpenCVByType(LIB, CELL, DST_VIEW, 'layout', 'a')` — 可写模式重新打开（'a' = append/writable）
   - `insts = pyScript.dbInstanceQuery(writable_cv)` — 查询所有 instance
   - `inst_count = len(insts) if insts else 0` — 计数
   - `print(f"  Cell View : {LIB}/{CELL}/{DST_VIEW}")` + `print(f"  Instance 个数: {inst_count}")` — 打印
   - `pyScript.dbCloseCV(writable_cv)` — 关闭
4. `if __name__ == "__main__": main()`

## 关键 API（assistant 经 RAG 查证的真实 pyAether API，金标准使用）

| 步骤 | API | 签名要点 |
|------|-----|---------|
| 初始化 | `emyInitAether(mode)` | mode='-adv' |
| 打开 | `dbOpenCVByType(lib, cell, view, viewType='', mode='r')` | mode='r' 只读, 'a' 可写 |
| 拷贝 | `dbCopyCellView(srcDesign, lib, cell, view, overWrite=False)` | 返回新 emyDesign |
| 查 inst | `dbInstanceQuery(cv, bbox=..., startLevel=..., stopLevel=...)` | 返回 tuple of instances |
| 关闭 | `dbCloseCV(cv)` | |

## 本案合成（A档 faithful · L1-static）

- **交付**: `copy_and_count_instances.py`（config-driven，从 `config.json` 读 lib/cell/src_view/dst_view），打包进 `outputs/submit.zip`
- **判分**: 静态结构检查 (a-m) + 嵌入 `pyAether_stub.py` 用 python3 在独立临时目录真跑候选 (n-s)，stub mock 全部 pyAether API 并记录调用序列，验候选用 config 派生的 lib/cell/view（反硬编码 A）、调对 API 序列、len() 计数、exit 0
- **A**: prompt(U#0 逐字) + task_brief + config_A (A_testLary/BCenterL/layout/layout_laryxi, count=42)
- **隐藏 B**: config_B 结构对立 (myLib/Inverter/schematic/schematic_copy, count=7)
- **隐藏 B2**: config_B2 随机化 (testLib/TopCell/layout/layout_b2, count=15)
