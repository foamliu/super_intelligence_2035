#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build EDA-Eval-DesignFlow-EccDsaLocate-001 (shard C, layout_aether, B-synthesized, L2).
Trace: xiwang@hfeg0pkn002 / 1794035650061_tmx27
U#0 (verbatim): "帮我基于DDGOA spine的版图，画出ECC和DSA所在的位置"
Grounding: assistant parsed SpineTop_modules.csv (cell/instName/lib/x1_um/y1_um/x2_um/y2_um)
  + fullmap.json hierarchy; filtered ECC/DSA by name regex; aggregated per-class bbox union
  + instance lists; opened SpineTop layout via pyAether. Real OA/pyAether not sandbox-reproducible
  -> offline L2: candidate script reads a spine layout instance inventory JSON, classifies ECC/DSA
  by delimited-token name patterns, aggregates per-class bbox union + counts + instance list,
  writes ecc_dsa_map.json + ecc_dsa_positions.csv. check.py runs candidate on hidden B inventory
  (subprocess) and structured-compares 15 conditions a-o.
"""
import os, json, re, csv, io, zipfile, shutil, subprocess, sys, hashlib, tempfile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EccDsaLocate-001"
AST = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
HID = os.path.join(AST, "hidden")
NEG = os.path.join(REF, "negative")

for d in (AST, REF, HID, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- core algorithm (shared: golden + check.py ground truth) ----------
ECC_RE = re.compile(r'^(ECC|Ecc)[A-Z_]')
DSA_RE = re.compile(r'(^|_)DSA(_|$)')

def classify(cell):
    c = cell or ""
    if ECC_RE.search(c):
        return "ECC"
    if DSA_RE.search(c):
        return "DSA"
    return None

def aggregate(instances, kind):
    sel = [i for i in instances if classify(i["cell"]) == kind]
    cells = sorted({i["cell"] for i in sel})
    if sel:
        x1 = min(float(i["bbox"][0]) for i in sel)
        y1 = min(float(i["bbox"][1]) for i in sel)
        x2 = max(float(i["bbox"][2]) for i in sel)
        y2 = max(float(i["bbox"][3]) for i in sel)
        union = [x1, y1, x2, y2]
    else:
        union = None
    return {
        "class": kind,
        "instance_count": len(sel),
        "distinct_cells": cells,
        "bbox_union": union,
        "instances": sorted(sel, key=lambda i: i["instName"]),
    }

def build_map(inventory):
    insts = inventory["instances"]
    ecc = aggregate(insts, "ECC")
    dsa = aggregate(insts, "DSA")
    other = [i for i in insts if classify(i["cell"]) is None]
    return {
        "spine": inventory["spine"],
        "units": inventory.get("units", "um"),
        "ecc": ecc,
        "dsa": dsa,
        "summary": {
            "total_ecc": ecc["instance_count"],
            "total_dsa": dsa["instance_count"],
            "total_other": len(other),
            "grand_total": len(insts),
        },
    }

def write_outputs(m, outdir):
    os.makedirs(outdir, exist_ok=True)
    jp = os.path.join(outdir, "ecc_dsa_map.json")
    cp = os.path.join(outdir, "ecc_dsa_positions.csv")
    with open(jp, "w") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    with open(cp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class", "instName", "cell", "lib", "x1", "y1", "x2", "y2"])
        for kind in ("ECC", "DSA"):
            for i in m[kind.lower()]["instances"]:
                w.writerow([kind, i["instName"], i["cell"], i["lib"]] + i["bbox"])
    return jp, cp

# ---------- inventories ----------
def mkinst(inst, cell, lib, x1, y1, x2, y2):
    return {"instName": inst, "cell": cell, "lib": lib, "bbox": [x1, y1, x2, y2]}

INVA = {
    "spine": "SpineTop",
    "units": "um",
    "instances": [
        # ECC (9)
        mkinst("I0", "ECC_LbusN_Unit8bit_Rev28", "ddgoa_cmos_digital", 10.0, 100.0, 110.0, 200.0),
        mkinst("I1", "ECC_Lbus_Unit8bit_Rev28", "ddgoa_cmos_digital", 10.0, 210.0, 110.0, 310.0),
        mkinst("I2", "EccStg_topdown", "ddgoa_cmos_digital", 120.0, 100.0, 180.0, 260.0),
        mkinst("I3", "EccStg_topup", "ddgoa_cmos_digital", 120.0, 270.0, 180.0, 430.0),
        mkinst("I4", "EccStg_botdown", "ddgoa_cmos_digital", 190.0, 100.0, 250.0, 260.0),
        mkinst("I5", "EccStg_botup", "ddgoa_cmos_digital", 190.0, 270.0, 250.0, 430.0),
        mkinst("I6", "EccTop128x1New_DDGOA_R1A_plan5_new_Rev28", "ddgoa_cmos_digital", 260.0, 100.0, 360.0, 300.0),
        mkinst("I7", "ECC_LbusDrv_2Bank_Rev28", "ddgoa_cmos_digital", 260.0, 310.0, 360.0, 460.0),
        mkinst("I8", "ECC_LbusDrvN_2Bank_Rev28", "ddgoa_cmos_digital", 370.0, 100.0, 470.0, 250.0),
        # DSA (4)
        mkinst("I9",  "RWCBWNewV2_DDGOA_A_DSA_Rev28", "ddgoa_cmos_digital", 480.0, 100.0, 540.0, 220.0),
        mkinst("I10", "RWCBWNewV2_DDGOA_B_DSA_Rev28", "ddgoa_cmos_digital", 480.0, 230.0, 540.0, 350.0),
        mkinst("I11", "DSA_SenseAmp_Rev28", "ddgoa_cmos_digital", 550.0, 100.0, 600.0, 200.0),
        mkinst("I12", "DataPath_DSA_Ctl_Rev28", "ddgoa_cmos_digital", 550.0, 210.0, 600.0, 320.0),
        # decoys / other (6) -- incl BANDSAW false-positive guard
        mkinst("I13", "SpineRptANew2", "zlib", 10.0, 470.0, 60.0, 520.0),
        mkinst("I14", "SpineRptBNew2", "zlib", 70.0, 470.0, 120.0, 520.0),
        mkinst("I15", "Abus_top_mux", "ddgoa_cmos_digital", 130.0, 470.0, 200.0, 520.0),
        mkinst("I16", "BankTopX2_gut_0820", "ddgoa_cmos_digital", 210.0, 470.0, 300.0, 520.0),
        mkinst("I17", "BANDSAW_mux", "ddgoa_cmos_digital", 310.0, 470.0, 380.0, 520.0),  # 'dsa' substring, NOT DSA
        mkinst("I18", "Array16GTop_spine_rt_gut", "zlib", 390.0, 470.0, 470.0, 520.0),
    ],
}

INVB = {
    "spine": "SpineTop_R2",
    "units": "um",
    "instances": [
        # ECC (10) -- different cells, bboxes, one extra
        mkinst("E0", "ECC_BusDrv_X4_Rev30", "ddgoa_cmos_digital", 5.0, 50.0, 90.0, 180.0),
        mkinst("E1", "EccStage_up_R2", "ddgoa_cmos_digital", 5.0, 190.0, 90.0, 320.0),
        mkinst("E2", "EccStage_dn_R2", "ddgoa_cmos_digital", 100.0, 50.0, 185.0, 180.0),
        mkinst("E3", "EccTop256x2_DDGOA_R2B_Rev30", "ddgoa_cmos_digital", 100.0, 190.0, 240.0, 360.0),
        mkinst("E4", "ECC_LbusN_Unit16_Rev30", "ddgoa_cmos_digital", 250.0, 50.0, 360.0, 200.0),
        mkinst("E5", "ECC_Lbus_16bit_Rev30", "ddgoa_cmos_digital", 250.0, 210.0, 360.0, 360.0),
        mkinst("E6", "EccStg_midup", "ddgoa_cmos_digital", 370.0, 50.0, 430.0, 200.0),
        mkinst("E7", "EccStg_middn", "ddgoa_cmos_digital", 370.0, 210.0, 430.0, 360.0),
        mkinst("E8", "ECC_LbusDrv_4Bank_Rev30", "ddgoa_cmos_digital", 440.0, 50.0, 560.0, 200.0),
        mkinst("E9", "ECC_LbusDrvN_4Bank_Rev30", "ddgoa_cmos_digital", 440.0, 210.0, 560.0, 360.0),
        # DSA (6) -- different, more
        mkinst("D0", "RWCBWV3_DDGOA_C_DSA_Rev30", "ddgoa_cmos_digital", 570.0, 50.0, 650.0, 180.0),
        mkinst("D1", "RWCBWV3_DDGOA_D_DSA_Rev30", "ddgoa_cmos_digital", 570.0, 190.0, 650.0, 320.0),
        mkinst("D2", "DSA_SenseAmp_X8_Rev30", "ddgoa_cmos_digital", 660.0, 50.0, 740.0, 170.0),
        mkinst("D3", "DSA_Ctl_Rev30", "ddgoa_cmos_digital", 660.0, 180.0, 740.0, 300.0),
        mkinst("D4", "WrPath_DSA_Mux_Rev30", "ddgoa_cmos_digital", 750.0, 50.0, 830.0, 170.0),
        mkinst("D5", "DSA_BufRow_Rev30", "ddgoa_cmos_digital", 750.0, 180.0, 830.0, 300.0),
        # decoys / other (7) -- incl BANDSAW_clk false-positive guard + MeSaDiv (Sa not DSA)
        mkinst("O0", "SpineRptC_R2", "zlib", 5.0, 370.0, 70.0, 430.0),
        mkinst("O1", "AbusBotMux", "ddgoa_cmos_digital", 80.0, 370.0, 160.0, 430.0),
        mkinst("O2", "BankTopX4_gut", "ddgoa_cmos_digital", 170.0, 370.0, 270.0, 430.0),
        mkinst("O3", "BANDSAW_clk", "ddgoa_cmos_digital", 280.0, 370.0, 360.0, 430.0),  # 'dsa' substring, NOT DSA
        mkinst("O4", "PeriTop_gut", "ddgoa_cmos_digital", 370.0, 370.0, 450.0, 430.0),
        mkinst("O5", "Channel_N", "zlib", 460.0, 370.0, 540.0, 430.0),
        mkinst("O6", "MeSaDiv", "ddgoa_cmos_digital", 550.0, 370.0, 620.0, 430.0),  # 'Sa' not DSA
    ],
}

# ---------- write assets A ----------
with open(os.path.join(AST, "spine_inventory_A.json"), "w") as f:
    json.dump(INVA, f, indent=2, ensure_ascii=False)

PROMPT = (
    "我是 xiwang，正在做 DDGOA spine 的版图分析。帮我基于 DDGOA spine 的版图，画出 ECC 和 DSA 所在的位置。\n\n"
    "附件 spine_inventory_A.json 是 SpineTop 版图的实例清单（每个实例含 cell 名、instName、lib、bbox，"
    "坐标单位 µm，bbox 为 [x1,y1,x2,y2]）。ECC 和 DSA 是版图中两类功能模块，需要按 cell 名称识别：\n"
    "- ECC 类：cell 名以 ECC_ / EccStg / EccTop / EccStage / EccLbus 等开头的模块；\n"
    "- DSA 类：cell 名中 DSA 作为独立词出现（DSA_xxx、xxx_DSA、xxx_DSA_xxx）的模块。\n\n"
    "请写一个 Python 脚本 locate_ecc_dsa.py，读取一个 spine 实例清单 JSON（路径由命令行参数 argv[1] 给出），"
    "识别所有 ECC 和 DSA 实例，分别聚合每类的 bbox 并集（[xmin,ymin,xmax,ymax]）、实例数、distinct cell 列表，"
    "并把每个实例的位置列出，输出 ecc_dsa_map.json 和 ecc_dsa_positions.csv 到当前目录。\n\n"
    "注意：cell 名中包含 'dsa' 子串但 DSA 不是独立词的（例如 BANDSAW_mux）不是 DSA 类，要排除。"
)
with open(os.path.join(AST, "prompt.txt"), "w") as f:
    f.write(PROMPT)

with open(os.path.join(AST, "task_brief.md"), "w") as f:
    f.write("交付接口：把 locate_ecc_dsa.py 打包进 outputs/submit.zip。脚本接受 spine 实例清单 JSON 路径"
            "(argv[1])，运行后在当前目录生成 ecc_dsa_map.json 与 ecc_dsa_positions.csv。\n")

# ---------- hidden B ----------
with open(os.path.join(HID, "spine_inventory_B.json"), "w") as f:
    json.dump(INVB, f, indent=2, ensure_ascii=False)
with open(os.path.join(HID, "hidden_manifest.json"), "w") as f:
    json.dump({
        "hidden_input": "spine_inventory_B.json",
        "diff_vs_A": "不同 spine 名(SpineTop_R2)、不同 ECC/DSA cell 名与 bbox、ECC 10/DSA 6(A 为 9/4)、"
                     "含 BANDSAW_clk 与 MeSaDiv 两个非 DSA 诱饵（子串假阳性守卫）",
        "check_runs_candidate_on": "B",
    }, f, indent=2, ensure_ascii=False)

# ---------- golden deliverable script ----------
GOLDEN = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Locate ECC & DSA instances in a DDGOA spine layout inventory."""
import sys, os, json, re, csv

ECC_RE = re.compile(r'^(ECC|Ecc)[A-Z_]')
DSA_RE = re.compile(r'(^|_)DSA(_|$)')

def classify(cell):
    c = cell or ""
    if ECC_RE.search(c):
        return "ECC"
    if DSA_RE.search(c):
        return "DSA"
    return None

def aggregate(instances, kind):
    sel = [i for i in instances if classify(i["cell"]) == kind]
    cells = sorted({i["cell"] for i in sel})
    if sel:
        x1 = min(float(i["bbox"][0]) for i in sel)
        y1 = min(float(i["bbox"][1]) for i in sel)
        x2 = max(float(i["bbox"][2]) for i in sel)
        y2 = max(float(i["bbox"][3]) for i in sel)
        union = [x1, y1, x2, y2]
    else:
        union = None
    return {"class": kind, "instance_count": len(sel), "distinct_cells": cells,
            "bbox_union": union, "instances": sorted(sel, key=lambda i: i["instName"])}

def main():
    inv_path = sys.argv[1]
    inv = json.load(open(inv_path))
    insts = inv["instances"]
    ecc = aggregate(insts, "ECC")
    dsa = aggregate(insts, "DSA")
    other = [i for i in insts if classify(i["cell"]) is None]
    m = {"spine": inv["spine"], "units": inv.get("units", "um"), "ecc": ecc, "dsa": dsa,
         "summary": {"total_ecc": ecc["instance_count"], "total_dsa": dsa["instance_count"],
                     "total_other": len(other), "grand_total": len(insts)}}
    with open("ecc_dsa_map.json", "w") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    with open("ecc_dsa_positions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class", "instName", "cell", "lib", "x1", "y1", "x2", "y2"])
        for kind in ("ECC", "DSA"):
            for i in m[kind.lower()]["instances"]:
                w.writerow([kind, i["instName"], i["cell"], i["lib"]] + i["bbox"])

if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF, "locate_ecc_dsa.py"), "w") as f:
    f.write(GOLDEN)

# ---------- reference_submit.zip ----------
with zipfile.ZipFile(os.path.join(REF, "reference_submit.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("locate_ecc_dsa.py", GOLDEN)

# ---------- check.py (15 conditions a-o) ----------
CHECK = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-EccDsaLocate-001.
15 conditions a-o. Runs candidate locate_ecc_dsa.py on hidden B inventory and
structured-compares output to independently recomputed ground truth."""
import os, sys, json, re, csv, zipfile, shutil, subprocess, tempfile

ECC_RE = re.compile(r'^(ECC|Ecc)[A-Z_]')
DSA_RE = re.compile(r'(^|_)DSA(_|$)')

def classify(cell):
    c = cell or ""
    if ECC_RE.search(c): return "ECC"
    if DSA_RE.search(c): return "DSA"
    return None

def aggregate(instances, kind):
    sel = [i for i in instances if classify(i["cell"]) == kind]
    cells = sorted({i["cell"] for i in sel})
    if sel:
        union = [min(float(i["bbox"][0]) for i in sel), min(float(i["bbox"][1]) for i in sel),
                 max(float(i["bbox"][2]) for i in sel), max(float(i["bbox"][3]) for i in sel)]
    else:
        union = None
    return {"class": kind, "instance_count": len(sel), "distinct_cells": cells,
            "bbox_union": union, "instances": sorted(sel, key=lambda i: i["instName"])}

def truth(inv):
    insts = inv["instances"]
    ecc = aggregate(insts, "ECC"); dsa = aggregate(insts, "DSA")
    other = [i for i in insts if classify(i["cell"]) is None]
    return {"spine": inv["spine"], "units": inv.get("units","um"), "ecc": ecc, "dsa": dsa,
            "summary": {"total_ecc": ecc["instance_count"], "total_dsa": dsa["instance_count"],
                        "total_other": len(other), "grand_total": len(insts)}}

def feq(a, b, tol=1e-6):
    if a is None or b is None: return a == b
    if not (isinstance(a, list) and isinstance(b, list) and len(a)==4 and len(b)==4): return False
    return all(abs(float(a[i])-float(b[i]))<=tol for i in range(4))

def check(deliverable, workdir):
    workdir = os.path.abspath(workdir)
    # locate hidden B inventory relative to workdir
    bpath = os.path.join(workdir, "hidden", "spine_inventory_B.json")
    if not os.path.exists(bpath):
        bpath = os.path.join(workdir, "spine_inventory_B.json")
    inv = json.load(open(bpath))
    T = truth(inv)
    # extract deliverable
    tmp = tempfile.mkdtemp(prefix="eccdsa_chk_")
    try:
        z = zipfile.ZipFile(deliverable)
        names = z.namelist()
        # a. zip must contain locate_ecc_dsa.py
        script = None
        for n in names:
            if n.endswith("locate_ecc_dsa.py") and not n.startswith("__"):
                script = n; break
        assert script is not None, "a: submit.zip 缺少 locate_ecc_dsa.py"
        z.extractall(tmp)
        sp = os.path.join(tmp, script)
        # run candidate on hidden B
        run = subprocess.run([sys.executable, sp, bpath], cwd=tmp, capture_output=True, text=True, timeout=120)
        assert run.returncode == 0, "candidate 脚本执行失败: " + run.stderr[:300]
        jp = os.path.join(tmp, "ecc_dsa_map.json")
        cp = os.path.join(tmp, "ecc_dsa_positions.csv")
        # b. outputs exist & map valid JSON with required keys
        assert os.path.exists(jp), "b: 缺少 ecc_dsa_map.json"
        assert os.path.exists(cp), "b: 缺少 ecc_dsa_positions.csv"
        m = json.load(open(jp))
        for k in ("spine","units","ecc","dsa","summary"):
            assert k in m, "b: ecc_dsa_map.json 缺少 key "+k
        # c. ecc.class == ECC
        assert m["ecc"].get("class") == "ECC", "c: ecc.class 不是 ECC"
        # d. dsa.class == DSA
        assert m["dsa"].get("class") == "DSA", "d: dsa.class 不是 DSA"
        # e. units == um
        assert m["units"] == T["units"], "e: units 不匹配"
        # f. ecc instance_count
        assert m["ecc"]["instance_count"] == T["ecc"]["instance_count"], "f: ECC 实例数不匹配"
        # g. dsa instance_count
        assert m["dsa"]["instance_count"] == T["dsa"]["instance_count"], "g: DSA 实例数不匹配"
        # h. ecc distinct_cells
        assert sorted(m["ecc"]["distinct_cells"]) == T["ecc"]["distinct_cells"], "h: ECC distinct_cells 不匹配"
        # i. dsa distinct_cells
        assert sorted(m["dsa"]["distinct_cells"]) == T["dsa"]["distinct_cells"], "i: DSA distinct_cells 不匹配"
        # j. ecc bbox_union
        assert feq(m["ecc"]["bbox_union"], T["ecc"]["bbox_union"]), "j: ECC bbox_union 不匹配"
        # k. dsa bbox_union
        assert feq(m["dsa"]["bbox_union"], T["dsa"]["bbox_union"]), "k: DSA bbox_union 不匹配"
        # l. every ecc instance well-formed & within inventory bbox range
        xmin = min(float(i["bbox"][0]) for i in inv["instances"]); xmax = max(float(i["bbox"][2]) for i in inv["instances"])
        ymin = min(float(i["bbox"][1]) for i in inv["instances"]); ymax = max(float(i["bbox"][3]) for i in inv["instances"])
        for i in m["ecc"]["instances"]:
            for kk in ("instName","cell","lib","bbox"):
                assert kk in i, "l: ECC 实例缺字段 "+kk
            assert len(i["bbox"]) == 4, "l: ECC bbox 维度错"
            assert xmin-1e-6 <= float(i["bbox"][0]) <= xmax+1e-6, "l: ECC bbox x1 越界"
            assert ymin-1e-6 <= float(i["bbox"][1]) <= ymax+1e-6, "l: ECC bbox y1 越界"
        # m. every dsa instance well-formed
        for i in m["dsa"]["instances"]:
            for kk in ("instName","cell","lib","bbox"):
                assert kk in i, "m: DSA 实例缺字段 "+kk
            assert len(i["bbox"]) == 4, "m: DSA bbox 维度错"
            assert xmin-1e-6 <= float(i["bbox"][2]) <= xmax+1e-6, "m: DSA bbox x2 越界"
            assert ymin-1e-6 <= float(i["bbox"][3]) <= ymax+1e-6, "m: DSA bbox y2 越界"
        # n. summary consistency
        assert m["summary"]["total_ecc"] == m["ecc"]["instance_count"], "n: summary.total_ecc 不一致"
        assert m["summary"]["total_dsa"] == m["dsa"]["instance_count"], "n: summary.total_dsa 不一致"
        assert m["summary"]["grand_total"] == len(inv["instances"]), "n: summary.grand_total 不一致"
        # o. false-positive guard: BANDSAW decoy NOT in dsa.instances; all dsa cells truly DSA
        dsa_cells = {i["cell"] for i in m["dsa"]["instances"]}
        for c in dsa_cells:
            assert classify(c) == "DSA", "o: DSA 类中出现非 DSA cell: "+c
        assert "BANDSAW_clk" not in dsa_cells, "o: 诱饵 BANDSAW_clk 误判为 DSA"
        # csv cross-check: row count == ecc+dsa instances
        rows = list(csv.reader(open(cp)))
        assert len(rows) == m["ecc"]["instance_count"] + m["dsa"]["instance_count"] + 1, "csv 行数与实例数不符"
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "reference_submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    print(check(d, w))
'''
with open(os.path.join(REF, "check.py"), "w") as f:
    f.write(CHECK)

# ---------- negatives ----------
def neg_empty():
    return '#!/usr/bin/env python3\nimport sys\n# empty shell: produces nothing\n'
def neg_print_expected():
    # hardcodes A's expected map (prints A's truth regardless of input)
    ta = build_map(INVA)
    return '#!/usr/bin/env python3\nimport sys, json\nm = ' + json.dumps(ta, ensure_ascii=False) + '\njson.dump(m, open("ecc_dsa_map.json","w"), indent=2)\nimport csv\nwith open("ecc_dsa_positions.csv","w",newline="") as f:\n w=csv.writer(f); w.writerow(["class","instName","cell","lib","x1","y1","x2","y2"])\n for k in ("ECC","DSA"):\n  for i in m[k.lower()]["instances"]: w.writerow([k,i["instName"],i["cell"],i["lib"]]+i["bbox"])\n'
def neg_core_deleted():
    # filters but does NOT aggregate bbox (union None) -> j/k fail
    return r'''#!/usr/bin/env python3
import sys, json, re, csv
ECC_RE = re.compile(r'^(ECC|Ecc)[A-Z_]'); DSA_RE = re.compile(r'(^|_)DSA(_|$)')
def classify(c):
    c=c or ""
    if ECC_RE.search(c): return "ECC"
    if DSA_RE.search(c): return "DSA"
    return None
inv = json.load(open(sys.argv[1])); insts = inv["instances"]
def agg(kind):
    sel = [i for i in insts if classify(i["cell"])==kind]
    return {"class":kind,"instance_count":len(sel),"distinct_cells":sorted({i["cell"] for i in sel}),
            "bbox_union":None,"instances":sorted(sel,key=lambda i:i["instName"])}
ecc=agg("ECC"); dsa=agg("DSA"); other=[i for i in insts if classify(i["cell"]) is None]
m={"spine":inv["spine"],"units":inv.get("units","um"),"ecc":ecc,"dsa":dsa,
   "summary":{"total_ecc":ecc["instance_count"],"total_dsa":dsa["instance_count"],"total_other":len(other),"grand_total":len(insts)}}
json.dump(m,open("ecc_dsa_map.json","w"),indent=2)
with open("ecc_dsa_positions.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["class","instName","cell","lib","x1","y1","x2","y2"])
    for k in ("ECC","DSA"):
        for i in m[k.lower()]["instances"]: w.writerow([k,i["instName"],i["cell"],i["lib"]]+i["bbox"])
'''
def neg_naive_substring():
    # uses 'dsa' in cell.lower() -> catches BANDSAW decoy -> g/i/o fail
    return r'''#!/usr/bin/env python3
import sys, json, csv
inv = json.load(open(sys.argv[1])); insts = inv["instances"]
def agg(kind):
    if kind=="ECC":
        sel=[i for i in insts if "ecc" in (i["cell"] or "").lower()]
    else:
        sel=[i for i in insts if "dsa" in (i["cell"] or "").lower()]
    if sel:
        union=[min(float(i["bbox"][0]) for i in sel),min(float(i["bbox"][1]) for i in sel),max(float(i["bbox"][2]) for i in sel),max(float(i["bbox"][3]) for i in sel)]
    else: union=None
    return {"class":kind,"instance_count":len(sel),"distinct_cells":sorted({i["cell"] for i in sel}),"bbox_union":union,"instances":sorted(sel,key=lambda i:i["instName"])}
ecc=agg("ECC"); dsa=agg("DSA"); other=[i for i in insts if "ecc" not in (i["cell"] or "").lower() and "dsa" not in (i["cell"] or "").lower()]
m={"spine":inv["spine"],"units":inv.get("units","um"),"ecc":ecc,"dsa":dsa,
   "summary":{"total_ecc":ecc["instance_count"],"total_dsa":dsa["instance_count"],"total_other":len(other),"grand_total":len(insts)}}
json.dump(m,open("ecc_dsa_map.json","w"),indent=2)
with open("ecc_dsa_positions.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["class","instName","cell","lib","x1","y1","x2","y2"])
    for k in ("ECC","DSA"):
        for i in m[k.lower()]["instances"]: w.writerow([k,i["instName"],i["cell"],i["lib"]]+i["bbox"])
'''
def neg_wrong_class():
    # swaps ECC/DSA classification -> c/d/f/g/h/i fail
    return r'''#!/usr/bin/env python3
import sys, json, re, csv
ECC_RE = re.compile(r'^(ECC|Ecc)[A-Z_]'); DSA_RE = re.compile(r'(^|_)DSA(_|$)')
def classify(c):
    c=c or ""
    if ECC_RE.search(c): return "DSA"   # swapped
    if DSA_RE.search(c): return "ECC"   # swapped
    return None
inv = json.load(open(sys.argv[1])); insts = inv["instances"]
def agg(kind):
    sel=[i for i in insts if classify(i["cell"])==kind]
    if sel: union=[min(float(i["bbox"][0]) for i in sel),min(float(i["bbox"][1]) for i in sel),max(float(i["bbox"][2]) for i in sel),max(float(i["bbox"][3]) for i in sel)]
    else: union=None
    return {"class":kind,"instance_count":len(sel),"distinct_cells":sorted({i["cell"] for i in sel}),"bbox_union":union,"instances":sorted(sel,key=lambda i:i["instName"])}
ecc=agg("ECC"); dsa=agg("DSA"); other=[i for i in insts if classify(i["cell"]) is None]
m={"spine":inv["spine"],"units":inv.get("units","um"),"ecc":ecc,"dsa":dsa,
   "summary":{"total_ecc":ecc["instance_count"],"total_dsa":dsa["instance_count"],"total_other":len(other),"grand_total":len(insts)}}
json.dump(m,open("ecc_dsa_map.json","w"),indent=2)
with open("ecc_dsa_positions.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["class","instName","cell","lib","x1","y1","x2","y2"])
    for k in ("ECC","DSA"):
        for i in m[k.lower()]["instances"]: w.writerow([k,i["instName"],i["cell"],i["lib"]]+i["bbox"])
'''

negs = {
    "empty_shell.py": neg_empty(),
    "print_expected_A.py": neg_print_expected(),
    "core_deleted.py": neg_core_deleted(),
    "naive_substring.py": neg_naive_substring(),
    "wrong_class.py": neg_wrong_class(),
}
for nm, code in negs.items():
    with open(os.path.join(NEG, nm), "w") as f:
        f.write(code)

# negative_selftest.py
SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all negatives; every one MUST FAIL check(). Exit 0 iff all FAIL."""
import os, sys, importlib.util, tempfile, zipfile, shutil
here = os.path.dirname(os.path.abspath(__file__))
ref = os.path.dirname(here)
# locate hidden B inventory: ../../../assets/<CASE>/hidden/spine_inventory_B.json
CASE = "EccDsaLocate-001"
bpath = os.path.normpath(os.path.join(here, "..", "..", "..", "assets", CASE, "hidden", "spine_inventory_B.json"))
assert os.path.exists(bpath), "hidden B inventory not found at "+bpath
# build a judge workdir with hidden/B so check.py can find it
judge = tempfile.mkdtemp(prefix="neg_judge_")
os.makedirs(os.path.join(judge, "hidden"))
shutil.copy(bpath, os.path.join(judge, "hidden", "spine_inventory_B.json"))
def load_check():
    spec = importlib.util.spec_from_file_location("chk", os.path.join(ref, "check.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.check
check = load_check()
negs = ["empty_shell.py","print_expected_A.py","core_deleted.py","naive_substring.py","wrong_class.py"]
fails = 0; passes = 0
try:
    for n in negs:
        src = os.path.join(here, n)
        tmp = tempfile.mkdtemp(prefix="neg_")
        try:
            zp = os.path.join(tmp, "submit.zip")
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(src, "locate_ecc_dsa.py")
            try:
                check(zp, judge)
                print(f"  {n}: PASS (UNEXPECTED -- negative must FAIL)"); passes += 1
            except Exception as e:
                print(f"  {n}: FAIL (expected) -- {str(e)[:80]}"); fails += 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
finally:
    shutil.rmtree(judge, ignore_errors=True)
print(f"negatives: {fails}/{len(negs)} FAIL, {passes} unexpected PASS")
sys.exit(0 if passes == 0 else 1)
'''
with open(os.path.join(NEG, "negative_selftest.py"), "w") as f:
    f.write(SELFTEST)

print("BUILD: assets/hidden/reference/negatives written")
print("  A instances:", len(INVA["instances"]), "B instances:", len(INVB["instances"]))
print("  A ECC/DSA:", build_map(INVA)["summary"]["total_ecc"], build_map(INVA)["summary"]["total_dsa"])
print("  B ECC/DSA:", build_map(INVB)["summary"]["total_ecc"], build_map(INVB)["summary"]["total_dsa"])

# ---------- SELF-VERIFY ----------
print("\n=== SELF-VERIFY ===")
import importlib.util
# set up judge workdir with hidden B
judge = tempfile.mkdtemp(prefix="eccdsa_judge_")
os.makedirs(os.path.join(judge, "hidden"))
shutil.copy(os.path.join(HID, "spine_inventory_B.json"), os.path.join(judge, "hidden", "spine_inventory_B.json"))
# load check
spec = importlib.util.spec_from_file_location("chk", os.path.join(REF, "check.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

# 1. reference_submit.zip on B -> must PASS
try:
    r = chk.check(os.path.join(REF, "reference_submit.zip"), judge)
    print("  [1] reference_submit.zip on B: PASS" if r else "  [1] ref: FAIL(unexpected)")
    ref_pass = bool(r)
except Exception as e:
    print("  [1] reference_submit.zip on B: FAIL --", str(e)[:200]); ref_pass = False

# 2. reference golden on A (sanity)
tmpA = tempfile.mkdtemp(prefix="eccdsa_A_")
try:
    subprocess.run([sys.executable, os.path.join(REF, "locate_ecc_dsa.py"), os.path.join(AST, "spine_inventory_A.json")], cwd=tmpA, check=True, capture_output=True, text=True, timeout=60)
    mA = json.load(open(os.path.join(tmpA, "ecc_dsa_map.json")))
    print("  [2] golden on A sanity: spine=%s ecc=%d dsa=%d other=%d" % (mA["spine"], mA["summary"]["total_ecc"], mA["summary"]["total_dsa"], mA["summary"]["total_other"]))
finally:
    shutil.rmtree(tmpA, ignore_errors=True)

# 3. 5 negatives -> all FAIL via negative_selftest
nr = subprocess.run([sys.executable, os.path.join(NEG, "negative_selftest.py")], capture_output=True, text=True, timeout=120)
print("  [3] negative_selftest rc=%d" % nr.returncode)
print("     " + nr.stdout.replace("\n", "\n     ").strip())
neg_ok = (nr.returncode == 0)

# 4. §4.9 three fakes (empty/print/core) -> already in negatives; confirm individually FAIL
fakes = {"empty_shell.py": "a", "print_expected_A.py": "f/g", "core_deleted.py": "j/k"}
fake_ok = True
for n, cond in fakes.items():
    src = os.path.join(NEG, n)
    tmp = tempfile.mkdtemp(prefix="fake_")
    try:
        zp = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(src, "locate_ecc_dsa.py")
        try:
            chk.check(zp, judge)
            print("  [4] §4.9 %s: PASS (UNEXPECTED)" % n); fake_ok = False
        except Exception as e:
            print("  [4] §4.9 %s: FAIL (expected, cond %s) -- %s" % (n, cond, str(e)[:70]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# 5. byte-sync test==disk check.py
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
# extract test field check.py from jsonl later; here just print disk sha
disk_sha = sha(os.path.join(REF, "check.py"))
print("  [5] disk check.py sha256:", disk_sha)

# 6. 3-run determinism on B
shas = set()
for k in range(3):
    tmp = tempfile.mkdtemp(prefix="eccdsa_det_")
    try:
        subprocess.run([sys.executable, os.path.join(REF, "locate_ecc_dsa.py"), os.path.join(HID, "spine_inventory_B.json")], cwd=tmp, check=True, capture_output=True, timeout=60)
        shas.add(sha(os.path.join(tmp, "ecc_dsa_map.json")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print("  [6] 3-run determinism: %d distinct map shas -> %s" % (len(shas), "OK" if len(shas)==1 else "FAIL"))

shutil.rmtree(judge, ignore_errors=True)
print("\n=== SUMMARY ===")
print("  ref PASS:", ref_pass, "| negatives all FAIL:", neg_ok, "| §4.9 fakes FAIL:", fake_ok, "| 3-run det OK:", len(shas)==1)
print("  k_check = 15 (a-o) ; k_rationale = 15 (a-o)")
all_ok = ref_pass and neg_ok and fake_ok and len(shas)==1
print("  ALL_OK:", all_ok)
sys.exit(0 if all_ok else 1)
