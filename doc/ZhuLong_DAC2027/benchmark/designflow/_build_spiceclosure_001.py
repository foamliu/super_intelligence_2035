#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-SpiceClosureExtract-001 (shard D, schematic_netlist).

B-grade synthesized L1. Facet: SPICE subcircuit dependency-closure extractor.
Trace-faithful to aw9d7 (dsgao) USER#188: assistant parsed netlist.presim
(subcircuit library), built a dependency-closure extractor to pull root blocks
+ all transitively-referenced cells into a standalone netlist for focused TB
simulation. This case offline-replicates the closure-extraction facet.

Generator interface: gen_spice_closure.py --lib <netlist.sp> --roots <roots.json> --outdir <dir>
  -> <dir>/closure.sp (root + transitively-referenced .SUBCKT blocks, topo order)
  -> <dir>/manifest.json (roots, counts, closure[], topo_order, missing, leaf_models)

A = Ras TM verify (2 roots, 9 subckts, 2 leaf models) -- mimic of netlist.presim
B = analog CmpCore + BiasGen (2 roots, 7 subckts, 2 leaf models) -- HIDDEN
B2 = InvChain single root (1 root, 4 subckts, 2 leaf models) -- HIDDEN, tests 1-root path

16 check conditions a-p. Self-verify: ref PASS 16/16 + 5 negatives FAIL + 3-fake FAIL.
"""
import os, json, zipfile, subprocess, sys, shutil, tempfile, hashlib, re

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SpiceClosureExtract-001"
A = os.path.join(ROOT, "assets", CID)
R = os.path.join(ROOT, "reference", CID)
for d in (A, R, os.path.join(A,"hidden"), os.path.join(R,"negative")):
    os.makedirs(d, exist_ok=True)

# ---------- A input (visible to SUT) ----------
LIB_A = """* SpiceClosureExtract-A: Ras TM verify dependency closure
* Synthetic mimic of netlist.presim subcircuit library (aw9d7/dsgao trace)
.SUBCKT ntn_lv d g s b
Mn1 d g s b ntn W=0.2u L=0.04u
.ENDS ntn_lv
.SUBCKT ptn_lv d g s b
Mp1 d g s b ptn W=0.4u L=0.04u
.ENDS ptn_lv
.SUBCKT nand_x1 a b zn
Xp1 zn a vdd vdd ptn_lv
Xp2 zn b vdd vdd ptn_lv
Xn1 zn a b gnd ntn_lv
.ENDS nand_x1
.SUBCKT nor_x1 a b zn
Xp1 zn a vdd vdd ptn_lv
Xn1 zn a gnd gnd ntn_lv
Xn2 zn b gnd gnd ntn_lv
.ENDS nor_x1
.SUBCKT inv_x2 a zn
Xp1 zn a vdd vdd ptn_lv
Xp2 zn a vdd vdd ptn_lv
Xn1 zn a gnd gnd ntn_lv
Xn2 zn a gnd gnd ntn_lv
.ENDS inv_x2
.SUBCKT nand_x2 a b zn
Xp1 zn a vdd vdd ptn_lv
Xp2 zn b vdd vdd ptn_lv
Xn1 zn a n1 gnd ntn_lv
Xn2 n1 b gnd gnd ntn_lv
.ENDS nand_x2
.SUBCKT inv_x1 a zn
Xp1 zn a vdd vdd ptn_lv
Xn1 zn a gnd gnd ntn_lv
.ENDS inv_x1
.SUBCKT Ras_Tscodecomp tsa tsb c ht lt nt
Xt1 tsa c ht nand_x1
Xt2 tsb c lt nor_x1
Xt3 ht lt nt inv_x2
.ENDS Ras_Tscodecomp
.SUBCKT Ras_SaNPCtrl ht sanp sanpht sanphtlten
Xs1 ht sanp sanpht sanphtlten nand_x2
Xs2 ht sanp sanpht sanphtlten inv_x1
.ENDS Ras_SaNPCtrl
"""

# ---------- hidden B (analog comparator + bias) ----------
LIB_B = """* SpiceClosureExtract-B: analog CmpCore + BiasGen closure
.SUBCKT ntn_m d g s b
Mn1 d g s b ntn_mos W=1u L=0.18u
.ENDS ntn_m
.SUBCKT ptn_m d g s b
Mp1 d g s b ptn_mos W=2u L=0.18u
.ENDS ptn_m
.SUBCKT diff_pair inp inn out tail
Xn1 out inp tail ntn_m
Xn2 out inn tail ntn_m
.ENDS diff_pair
.SUBCKT fold_load in out vdd
Xn1 out in gnd ntn_m
Xp1 out out vdd ptn_m
.ENDS fold_load
.SUBCKT ref_beta vref vbias
Xn1 vbias vref gnd ntn_m
Xp1 vbias vbias vdd ptn_m
.ENDS ref_beta
.SUBCKT CmpCore inp inn out vdd gnd
Xd1 inp inn difft vdd diff_pair
Xf1 difft out vdd fold_load
.ENDS CmpCore
.SUBCKT BiasGen vref vbias vdd gnd
Xr1 vref vbias ref_beta
.ENDS BiasGen
"""

# ---------- hidden B2 (single root, shallow, different leaf models) ----------
LIB_B2 = """* SpiceClosureExtract-B2: single-root InvChain
.SUBCKT nmos_iv d g s b
Mn1 d g s b nmos_iv_mod W=0.5u L=0.05u
.ENDS nmos_iv
.SUBCKT pmos_iv d g s b
Mp1 d g s b pmos_iv_mod W=1u L=0.05u
.ENDS pmos_iv
.SUBCKT inv_iv a zn
Xp1 zn a vdd pmos_iv
Xn1 zn a gnd nmos_iv
.ENDS inv_iv
.SUBCKT InvChain a zn
Xi1 a n1 inv_iv
Xi2 n1 n2 inv_iv
Xi3 n2 zn inv_iv
.ENDS InvChain
"""

open(os.path.join(A,"lib_A.sp"),"w").write(LIB_A)
json.dump({"roots":["Ras_Tscodecomp","Ras_SaNPCtrl"]}, open(os.path.join(A,"roots_A.json"),"w"), indent=2)
open(os.path.join(A,"hidden","lib_B.sp"),"w").write(LIB_B)
json.dump({"roots":["CmpCore","BiasGen"]}, open(os.path.join(A,"hidden","roots_B.json"),"w"), indent=2)
open(os.path.join(A,"hidden","lib_B2.sp"),"w").write(LIB_B2)
json.dump({"roots":["InvChain"]}, open(os.path.join(A,"hidden","roots_B2.json"),"w"), indent=2)
json.dump({"B":{"lib":"lib_B.sp","roots":"roots_B.json"},
           "B2":{"lib":"lib_B2.sp","roots":"roots_B2.json"}},
          open(os.path.join(A,"hidden","hidden_manifest.json"),"w"), indent=2)

# ---------- task_brief + prompt ----------
open(os.path.join(A,"task_brief.md"),"w").write(
"交付接口：生成器 `gen_spice_closure.py`，读 `--lib <netlist.sp> --roots <roots.json> --outdir <dir>`，"
"在 `<dir>/closure.sp` + `<dir>/manifest.json` 写出依赖闭包子电路网表与清单。\n"
"提交：把 `gen_spice_closure.py` 打包成 `outputs/submit.zip`。\n"
"判定：独立进程在 hidden lib_B/lib_B2 上真跑生成器，校验闭包结构 + 拓扑序 + 跨输入 + 确定性。\n")

PROMPT = """下面是一个 SPICE 子电路库网表（assets/lib_A.sp），它是一整套 `.SUBCKT` 定义，顶层根单元 `Ras_Tscodecomp` 与 `Ras_SaNPCtrl`（见 assets/roots_A.json）会被用来做聚焦的 testbench 仿真。要把仿真跑通，必须先把根单元及其**传递依赖**的所有子电路抽成一个独立的闭包子电路网表（依赖在前、根在后），再产一份清单描述闭包结构。

背景：这是 DRAM RAS 校准（TM）验证流程里的一步——`netlist.presim` 是整套子电路库，要做 `cm1_ro_TsLT/TsHT/...` 这些 TM 信号的功能验证 TB，得先把相关块（`Ras_Tscodecomp`、`Ras_SaNPCtrl`）连同它们用到的 std cell / MOS 叶子子电路一起抽出来，形成可独立仿真的网表。真实流程在 .75 上用 finesim 跑，这里改成「读 SPICE 网表文本 → 抽依赖闭包 → 写闭包网表 + 清单」的离线复刻。

交付：写一个生成器 `gen_spice_closure.py`，读 `--lib <netlist.sp> --roots <roots.json> --outdir <dir>`，在 `<dir>` 下产出：

1. `closure.sp` —— 闭包子电路网表。包含根单元及其传递依赖的全部 `.SUBCKT` 块，按**拓扑序**（被依赖的子电路在前、依赖它的在后）逐块输出，每块原文复刻自输入网表。
2. `manifest.json` —— 闭包清单，顶层键：
   - `roots`：根单元名列表（按输入 roots.json 顺序）
   - `n_roots`：根单元数
   - `n_subckts_in_closure`：闭包内子电路总数
   - `n_leaf_models`：闭包内 MOS 模型（M 行第 6 个 token）去重后的数量
   - `closure`：按拓扑序的列表，每项 `{name, type("root"|"subckt"), ports, deps, n_xi, n_mos}`，其中 `deps` 是该子电路 X 行引用且在输入库里存在的 master 列表（排序去重），`n_xi` 是 X 行数，`n_mos` 是 M 行数
   - `topo_order`：拓扑序子电路名列表（被依赖在前）
   - `missing`：未解析的引用（roots 里不在库中的，或闭包内 X 行指向库外 master 的，形如 `"<subckt>-><master>"`），排序去重；输入良好时为空列表
   - `leaf_models`：闭包内 M 行引用的 MOS 模型名，排序去重

解析要求：
- `.SUBCKT <name> <ports...>` 起头、`.ENDS` 结尾（`.ENDS` 可带也可不带名字）；大小写不敏感
- `X<inst> <nets...> <master>`：最后一个 token 是被引用的子电路 master
- `M<inst> <d> <g> <s> <b> <model> ...`：第 6 个 token 是 MOS 模型名
- `*` 开头行和 `$` 开头行是注释，跳过（但不破坏 .SUBCKT 块的原文复刻）
- 闭包 = 从 roots 出发，沿 X 行 master 引用传递可达的全部子电路（只收集库内存在的）
- 拓扑序：对闭包内每个子电路，其 deps（库内 X 引用）必须排在它前面

hidden 输入会换一个完全不同的子电路库（不同根单元名 / 不同 std cell / 不同 MOS 模型名 / 不同依赖深度），以及一个**只有单根、依赖很浅**的库，所以不要硬编码 `Ras_Tscodecomp` / `Ras_SaNPCtrl` / `nand_x1` / `ntn_lv` 等 A 的任何细节。

把 `gen_spice_closure.py` 打包进 `outputs/submit.zip` 提交。
"""
open(os.path.join(A,"prompt.txt"),"w").write(PROMPT)

# ---------- reference generator ----------
REF_GEN = '''#!/usr/bin/env python3
"""Reference generator: SPICE subcircuit dependency-closure extractor."""
import os, json, sys, argparse

def parse_lib(text):
    subckts = {}
    lines = text.splitlines()
    cur = None
    for ln in lines:
        s = ln.strip()
        low = s.lower()
        if low.startswith(".subckt"):
            toks = s.split()
            name = toks[1]
            ports = toks[2:]
            subckts[name] = {"ports": ports, "body": [ln], "xrefs": [], "mrefs": []}
            cur = name
        elif low.startswith(".ends"):
            if cur is not None:
                subckts[cur]["body"].append(ln)
                cur = None
        else:
            if cur is not None:
                subckts[cur]["body"].append(ln)
                if not s.startswith("*") and not s.startswith("$") and s:
                    c = s[0]
                    if c in ("X", "x"):
                        toks = s.split()
                        master = toks[-1]
                        subckts[cur]["xrefs"].append(master)
                    elif c in ("M", "m"):
                        toks = s.split()
                        if len(toks) >= 6:
                            subckts[cur]["mrefs"].append(toks[5])
    return subckts

def build_closure(subckts, roots):
    seen = set()
    stack = list(roots)
    while stack:
        n = stack.pop()
        if n in seen or n not in subckts:
            continue
        seen.add(n)
        for d in subckts[n]["xrefs"]:
            if d in subckts and d not in seen:
                stack.append(d)
    return seen

def topo_sort(subckts, nodes):
    visited = {}
    order = []
    def visit(n):
        st = visited.get(n, 0)
        if st == 2:
            return
        if st == 1:
            return
        visited[n] = 1
        for d in subckts[n]["xrefs"]:
            if d in nodes and d in subckts:
                visit(d)
        visited[n] = 2
        order.append(n)
    for n in sorted(nodes):
        visit(n)
    return order

def build_manifest(subckts, roots):
    clos = build_closure(subckts, roots)
    order = topo_sort(subckts, clos)
    leaf_models = set()
    closure_list = []
    for n in order:
        sd = subckts[n]
        for m in sd["mrefs"]:
            leaf_models.add(m)
        closure_list.append({
            "name": n,
            "type": "root" if n in roots else "subckt",
            "ports": list(sd["ports"]),
            "deps": sorted(set(d for d in sd["xrefs"] if d in subckts)),
            "n_xi": len(sd["xrefs"]),
            "n_mos": len(sd["mrefs"]),
        })
    missing = []
    for r in roots:
        if r not in subckts:
            missing.append(r)
    for n in order:
        for d in subckts[n]["xrefs"]:
            if d not in subckts:
                missing.append(n + "->" + d)
    return {
        "roots": list(roots),
        "n_roots": len(roots),
        "n_subckts_in_closure": len(order),
        "n_leaf_models": len(leaf_models),
        "closure": closure_list,
        "topo_order": order,
        "missing": sorted(set(missing)),
        "leaf_models": sorted(leaf_models),
    }

def emit_closure_sp(subckts, order, path):
    with open(path, "w") as f:
        f.write("* Closure netlist (auto-generated by gen_spice_closure)\\n")
        for n in order:
            for ln in subckts[n]["body"]:
                f.write(ln + "\\n")
            f.write("\\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lib", required=True)
    ap.add_argument("--roots", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    text = open(args.lib).read()
    roots = json.load(open(args.roots))["roots"]
    subckts = parse_lib(text)
    os.makedirs(args.outdir, exist_ok=True)
    manifest = build_manifest(subckts, roots)
    emit_closure_sp(subckts, manifest["topo_order"], os.path.join(args.outdir, "closure.sp"))
    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
'''
open(os.path.join(R,"gen_spice_closure_ref.py"),"w").write(REF_GEN)

print("assets + reference generator written")
print("A subckts:", len([l for l in LIB_A.splitlines() if l.lower().startswith('.subckt')]))
print("B subckts:", len([l for l in LIB_B.splitlines() if l.lower().startswith('.subckt')]))
print("B2 subckts:", len([l for l in LIB_B2.splitlines() if l.lower().startswith('.subckt')]))
