# Deep-read: 1791861302008_d7v3k (jcgu / hfeg0pin003)

- **session**: `1791861302008_d7v3k` (jcgu, hfeg0pin003, mc=200)
- **meta**: model deepseek-v4-flash, cwd `/home/jcgu/Desktop`, status=**completed** (exit_code=0), source=desktop, interactive, 132 msgs, 1 user_input
- **tools dist**: 280 pyAether · 135 dbGet · 128 cellview · 106 netlist · 91 schematic · 72 "lang":"pyAether" · 1 "lang":"skill" (layout/pyAether-dominant)
- **domain**: layout_aether

## User turn (verbatim, single request)
> U[0] (逐字): 「帮我写一个python脚本，在当前运行路径下，使用aether打开某个指定的lib/cell/view,并获取view里全部的instance信息，这个脚本要能在terminal下直接运行」

纯需求委托轮 — 无根因、无修复方案、无澄清追问 ⇒ **合规 A-档 faithful seed**。

## Assistant tool chain (84 tool_uses)
1. `list_allowed_files` 探 `/home/jcgu/Desktop`
2. **70+ `RAG_MCP_Server__search_apis` / `get_api_details`** 反复查 `dbOpenCVByType / dbOpenCV / emyInitAether / emyInitQuery / emyBlock.getInsts / emyInst.getName/getLibName/getViewName/getMaster / emyCdbaNS / emyCollection / dbOpenLib / emyDesign.block` 等
3. `SandBox_MCP_Server__run_code` (lang=pyAether) 验 `import pyAether` 可用 + `ast.parse` 候选代码
4. **`editor` × 5** 写/改 `/home/jcgu/Desktop/get_instances.py`（中间 1 次 `rm` 重建）
5. `run_commands` `chmod +x` + 最终 `read_files` 读回确认

## Gold (final delivered file)
`/home/jcgu/Desktop/get_instances.py`（5500B，byte-faithful 取自末次 editor `new_text`）：
- `import pyAether as aet`
- `get_str(obj)` 辅助转 emyString → str
- `main()`：
  1. `sys.argv` 解析 `<lib> <cell> <view> [viewType="layout"] [mode="r"]`，<4 参打印 `__doc__` + Usage + `sys.exit(1)`
  2. `aet.emyInitAether("-adv")` 初始化
  3. `aet.dbOpenCVByType(lib, cell, view, viewType, mode)` 打开（`design is None` → 报错 exit 1）
  4. `block = design.block` → `block.getInsts(2)`（`emcInstIterNotImplicit=2`），fallback `design.instances`
  5. `ns = aet.emyCdbaNS()` + 逐实例 `inst.getName(ns, s)` / `getLibName` / `getViewName` / `getMaster().cellName`
  6. 表格打印 `# / Instance Name / Master Lib / Master Cell / Master View` + `Total instances found: <count>`

## 用户接受判据
session meta `status=completed`, `exit_code=0`, 单轮请求未被拒绝 ⇒ **用户接受** ⇒ A-档 faithful gold 可用（byte-faithful 取 trace 末版）。

## 与既有 case 区别
- FindCircuitByPath-001（GUI 表单 + dbOpenCV 链沿 inst path 下钻）/ HierJump-001（pulldown 菜单 + sleGuiDescendRead）/ PortPropagate-001（port 沿层次向上传播 + sync symbol）⇒ 本案 **单 cellview 内扁平枚举全部 instance**（不下钻、不传播、无 GUI），主题独立，非 near-duplicate。
- AddCellPin-001（layout_virtuoso，加 pin）主题不同。

## 合成决策
- **A-档 faithful**：prompt = U[0] 逐字原文 + 沙盒注（脚本通用化、CLI 参数、打印 instance 名 + master lib/cell/view）。
- **L1-boundary**：离线 Python，check.py 内嵌 fake `pyAether` 模块（`FAKE_PYAETHER_TEMPLATE`）确定性 seed 两套 hidden B 实例集（seed1: 3 inst U_DRV/U_BIAS/U_LOAD；seed2: 5 inst U_A1..U_A5），`INST_SEED` 环境变量切换；A 示例 `myLib/myCell` 让 fake `dbOpenCVByType` 返回 `None`（cross-input guard 拦硬编码）；判分机无需真 Aether（§4.2 ✓）。
- **hidden B 内嵌判分器**（无外部 hidden 文件）：结构性与 A 的 myLib/myCell 例子完全不同。
- **check.py 13 条独立断言** (a-m)：①zip 内容/大小/UTF-8 ②py_compile ③import pyAether ④def main + emyInitAether ⑤dbOpenCVByType ⑥emyCdbaNS + getInsts/instances ⑦≥3/4 getter ⑧Total instances found: ⑨sys.argv ≥3 位置参 ⑩真跑 seed1 exit0 + 3 名 + 3 master cell + count 3 ⑪随机化 seed2 exit0 + 5 名 + count 5 ⑫cross-input guard myLib/myCell 不泄漏 B token ⑬缺 viewType 默认值仍 exit0。
- **k_rationale == k_check == 13 ≥ 8 ✓**

## 自验
- ref `check.py submit.zip .` → **PASS** (exit 0)
- 4 negative 全 FAIL：empty_shell / print_only / naive_hardcode_B 均在条件 (c)「缺 import pyAether」FAIL；core_deleted 在条件 (g)「缺 ≥3 getter」FAIL
- 真跑 seed1/seed2/cross-input/default-viewType 在 gold 上全 PASS

## ledger
`mark --session 1791861302008_d7v3k --status case --case-id EDA-Eval-DesignFlow-ListInstCV-001` → 台账已动 60：case 40 · parked 20 · claimed 0
