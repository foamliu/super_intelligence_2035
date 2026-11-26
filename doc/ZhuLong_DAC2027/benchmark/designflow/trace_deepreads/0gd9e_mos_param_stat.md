# Deep-read: 1793519984879_0gd9e — MOS 参数统计

- session: `1793519984879_0gd9e.messages.json`
- user/host: e0023936 @ hfeg0pkn004 (10.129.2.13)
- mc=129, n=50 (messages)
- shard D, domain schematic_netlist
- picked at fresh_D275_pool.tsv rank 59 (peek_D279 batch, 15 cand 段)

## U#0 (逐字, A-faithful 提需求)
> 帮我统计当前打开的schematic中所有MOS的参数

纯提需求，未给根因/修复/参考实现 → 符合 A 档前提（produce-task）。

## trace 演化（n=50）
- A1-A3: 读 pyAether 子 skill 案例目录 + 入门文档（00_INDEX / 01_foundation）。
- A4-A6: 搜 API（aeGetCurDesign / aeEmyInstGetParameter），确认 `aeGetCurDesign()` 拿当前设计、`cv.instances` 遍历实例。
- A7-A10: 探 policy / 取用户名（get-username.sh → e0023936）。
- A11-A12: 在 pyAether 沙箱探索实例结构：枚举所有 inst.cellName，发现 MOS 器件在 TECHLIB（ptn_lvio/pmos, ntn_lvio/nmos）。
- A13: 确认稳健 MOS 识别规则 = "w 和 l 参数均非空"（aeEmyInstGetParameter），可排除 ipin/opin（basic 库）+ vcc/vssz/vbn（TECHLIB 电源/偏置单元）。识别出 6 个 MOS。
- A14: 在沙箱内自测 stat_mos_parameters()，输出表（见下）通过。
- A15: editor 保存 `/home/e0023936/devops/mos_params_stat.py`（仅函数定义）。
- A16: 给最终报告（markdown 表 + W/L/NF 分布 + 实现要点）。

## A 侧真实产出（mos_params_stat.py, 金标准）
```python
import pyAether as ae
from collections import Counter
def _get_param(inst, pname):
    try:
        val = ae.aeEmyInstGetParameter(pname, inst)
        return str(val).strip()
    except Exception:
        return ""
def stat_mos_parameters():
    cv = ae.aeGetCurDesign()
    if cv is None:
        print("No open design.")
        return []
    mos_list = []
    for inst in cv.instances:
        w = _get_param(inst, "w"); l = _get_param(inst, "l")
        if not w or not l: continue
        model = str(inst.cellName).strip()
        mtype = "P" if model.lower().startswith("p") else "N"
        mos_list.append({"name": str(inst.name), "model": model, "type": mtype,
                         "w": w, "l": l, "nf": _get_param(inst,"nf"), "m": _get_param(inst,"m")})
    print("=== MOS instances in %s/%s/%s ===" % (cv.libName, cv.cellName, cv.viewName))
    print("%-6s %-4s %-10s %-10s %-8s %-6s %-6s" % ("Name","Type","Model","W","L","NF","M"))
    for r in mos_list:
        print("%-6s %-4s %-10s %-10s %-8s %-6s %-6s" % (r["name"],r["type"],r["model"],r["w"],r["l"],r["nf"],r["m"]))
    print("Total MOS count = %d" % len(mos_list))
    print("--- W/L distribution (type x width x length x fingers) ---")
    cnt = Counter((r["type"],r["w"],r["l"],r["nf"]) for r in mos_list)
    for k,n in sorted(cnt.items()):
        print("  %sMOS W=%s L=%s NF=%s : %d" % (k[0],k[1],k[2],k[3],n))
    return mos_list
```

## A 侧 schematic / 结果
- schematic = `drcqa_stdcells/DqsGatingAoi_dqs/schematic`
- 6 MOS：
  - MP0/MP1/MP2 PMOS ptn_lvio  W=11.2u L=0.162u NF=5  M=(空)
  - MN0/MN1    NMOS ntn_lvio  W=5.4u  L=0.162u NF=4  M=(空)
  - MN3        NMOS ntn_lvio  W=2.7u  L=0.162u NF=2  M=(空)
- 分布：PMOS 11.2u/0.162u/5×3；NMOS 5.4u/0.162u/4×2；NMOS 2.7u/0.162u/2×1。

## 关键 API / 逻辑（check 锚点）
- `ae.aeGetCurDesign()` → cv（None 时打印 "No open design." 并 return []）
- `cv.instances` 遍历；`inst.name` / `inst.cellName` / `cv.libName/cellName/viewName`
- `ae.aeEmyInstGetParameter(pname, inst)` 取参数（不存在则 raise → SUT 需 try/except → ""）
- MOS 识别 = w 且 l 均非空（排除 ipin/opin/vcc/vssz 等 w/l 缺失的实例）
- 类型判定 = cellName 小写前缀 'p' → P 否则 N
- 输出：明细表 + "Total MOS count = N" + "--- W/L distribution ... ---" 分布块
- 返回 mos_list（dict list，键 name/model/type/w/l/nf/m）

## B-grade 合成策略（为何不是纯 A-faithful）
真实 Aether schematic（drcqa_stdcells/DqsGatingAoi_dqs）为用户实时打开的 cellview，不可附加（无 standalone 网表/文件）。故：
- A 资产：prompt.txt（逐字 U#0）+ task_brief.md（交付规范 + A 侧示例 schematic/结果，作为格式锚）+ example_output_A.txt（A 侧预期 stdout）。
- hidden B：合成 mock pyAether 模块（pyAether_B.py）模拟一个**不同** schematic（analog_lib/AmpBiasCore_v2/schematic），8 MOS（4 PMOS ptn_m / 4 NMOS ntn_m，W/L/NF/M 值均异于 A），+ 4 非 MOS（ipin/opin/vcc/vssz）必须被排除；其中 MP3.m=4、MN2.m=8 测 m 参数处理。
- hidden C：pyAether_C.py 第二个 mock（soc_lib/ClkBufLv/schematic，3 MOS + 2 非 MOS，名称全异）→ 反硬编码 / 通用性。
- no-design：复用 B mock，将 `_design=None` 测 "No open design." 分支。

## 难度定级
L2：需 pyAether API 知识（aeGetCurDesign/cv.instances/aeEmyInstGetParameter）+ MOS 识别逻辑（w&l 非空）+ 类型判定（cellName 前缀）+ 表/分布输出 + 返回值 + no-design 分支 + 通用性（不能硬编码 A/B 名称）。非平凡但单文件可完成。

## 案例落点
- case_id: EDA-Eval-DesignFlow-MosParamStat-001
- domain: schematic_netlist；track: faithful；layer: L2
- k_check = k_rationale = 16 (a-p)
