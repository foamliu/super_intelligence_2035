#!/usr/bin/env python3
# Build negatives + selftest + reference_submit.zip + prompt for VdbiasScanProduce-001
import os, zipfile, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-VdbiasScanProduce-001"
REF = os.path.join(BENCH, "reference", CID)
AST = os.path.join(BENCH, "assets", CID)
NEG = os.path.join(REF, "negative")
os.makedirs(NEG, exist_ok=True)

def wr(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

# B-gold embedded in print_only / hardcode_b stubs (the expected hidden-B report)
B_GOLD = {
    "total_folders": 5,
    "total_si": 12,
    "used_count": 9,
    "pvdias_values": {"0.7700": 4, "0.8100": 2, "0.9200": 2},
    "no_vdbias": [
        "AgingRun_Bb06_step2/si_Bb06_003.si.inp",
        "AgingRun_Bb07_step1/si_Bb07_002.si.inp",
        "AgingRun_Bb09_step1/si_Bb09_002.si.inp",
    ],
    "per_folder": [
        {"folder": "AgingRun_Bb05_step1", "si_count": 3, "used": 3},
        {"folder": "AgingRun_Bb06_step2", "si_count": 3, "used": 2},
        {"folder": "AgingRun_Bb07_step1", "si_count": 2, "used": 1},
        {"folder": "AgingRun_Bb08_step2", "si_count": 2, "used": 2},
        {"folder": "AgingRun_Bb09_step1", "si_count": 2, "used": 1},
    ],
}

B_GOLD_JSON = json.dumps(B_GOLD, indent=2, sort_keys=True)

# ---- neg_fake_empty.py (§4.9a empty shell) ----
wr(os.path.join(NEG, "neg_fake_empty.py"),
"""#!/usr/bin/env python3
import sys
sys.exit(0)
""")

# ---- neg_fake_print_only.py (§4.9b print_only) ----
wr(os.path.join(NEG, "neg_fake_print_only.py"),
"""#!/usr/bin/env python3
# §4.9(b) print_only stub: ignore input, emit precomputed B-gold report.
import sys, json
B_GOLD = """ + json.dumps(B_GOLD) + """
def main():
    out = None
    for i, a in enumerate(sys.argv):
        if a == '-o' and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    s = json.dumps(B_GOLD, indent=2, sort_keys=True)
    if out:
        open(out, 'w').write(s + "\\n")
    else:
        print(s)
main()
""")

# ---- neg_fake_core_deleted.py (§4.9c core_deleted) ----
wr(os.path.join(NEG, "neg_fake_core_deleted.py"),
"""#!/usr/bin/env python3
# §4.9(c) core_deleted stub: walks files (counts them) but removes the
# vdbias-detection core; reports everything as not-used.
import os, sys, json
def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = None
    for i, a in enumerate(sys.argv):
        if a == '-o' and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    sis = []
    for r, d, f in os.walk(root):
        d[:] = [x for x in d if not x.startswith('.')]
        for fn in f:
            if fn == 'si.inp' or fn.endswith('.si.inp'):
                sis.append(os.path.join(r, fn))
    sis.sort()
    topf = sorted([x for x in os.listdir(root) if os.path.isdir(os.path.join(root, x))])
    rep = {
        'total_folders': len(topf),
        'total_si': len(sis),
        'used_count': 0,
        'pvdias_values': {},
        'no_vdbias': sorted([os.path.relpath(s, root) for s in sis]),
        'per_folder': [{'folder': tf, 'si_count': 0, 'used': 0} for tf in topf],
    }
    s = json.dumps(rep, indent=2, sort_keys=True)
    if out:
        open(out, 'w').write(s + "\\n")
    else:
        print(s)
main()
""")

# ---- neg_fake_hardcode_b.py (smart §4.9b B-hardcoded stub) ----
wr(os.path.join(NEG, "neg_fake_hardcode_b.py"),
"""#!/usr/bin/env python3
# smart §4.9(b) B-hardcoded stub: detect input dir; if it looks like hidden B
# (folder name contains 'Bb'), emit B-gold; otherwise ALSO emit B-gold (cannot
# distinguish the SUT-invisible A'). Runtime proof: B-hardcode passes a-i on B
# but FAILS j-n on A' (A'-gold differs).
import sys, json, os
B_GOLD = """ + json.dumps(B_GOLD) + """
def looks_like_B(root):
    try:
        for d in os.listdir(root):
            if 'Bb' in d:
                return True
    except Exception:
        pass
    return False
def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = None
    for i, a in enumerate(sys.argv):
        if a == '-o' and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    _ = looks_like_B(root)  # gesture: detection does not help, always B-gold
    s = json.dumps(B_GOLD, indent=2, sort_keys=True)
    if out:
        open(out, 'w').write(s + "\\n")
    else:
        print(s)
main()
""")

# ---- negative_selftest.py ----
wr(os.path.join(NEG, "negative_selftest.py"),
'''#!/usr/bin/env python3
"""Run every negative through check(); all MUST fail (raise AssertionError)."""
import os, sys, tempfile, zipfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
sys.path.insert(0, REF)
import check as chk

NEGATIVES = [
    "neg_fake_empty.py",
    "neg_fake_print_only.py",
    "neg_fake_core_deleted.py",
    "neg_fake_hardcode_b.py",
]


def run_one(neg):
    tmp = tempfile.mkdtemp(prefix="negchk_")
    try:
        zipf = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zipf, "w") as zf:
            zf.write(os.path.join(HERE, neg), "scan_vdbias.py")
        try:
            chk.check(zipf, tmp)
            return False  # PASSED = bad (negative must fail)
        except AssertionError:
            return True  # FAILED = good
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    results = {}
    for n in NEGATIVES:
        results[n] = run_one(n)
    for n, r in results.items():
        print("%s: %s" % (n, "FAIL(good)" if r else "PASS(BAD!)"))
    allok = all(results.values())
    n_distinct = len(set(n.split("_")[1] for n in NEGATIVES))
    print("NEG_RC=%s  n_distinct=%d" % ("ALL FAIL" if allok else "SOME PASS", n_distinct))
    sys.exit(0 if allok else 1)


main()
''')

# ---- reference_submit.zip (ref solution as scan_vdbias.py) ----
ref_script = os.path.join(REF, "scan_vdbias.py")
zip_path = os.path.join(REF, "reference_submit.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(ref_script, "scan_vdbias.py")

# ---- prompt.txt (A-faithful, based on U#47) ----
wr(os.path.join(AST, "prompt.txt"),
"""你是 EDA 设计流编排助手。用户 tongfanl 在做 DDR6 全芯片 Aging 仿真，前期已经在 /rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun 下跑出了约 40 个 Aging 仿真结果文件夹（每个文件夹的子文件夹里都有 SPICE 仿真输入文件 si.inp）。用户想确认这些 si.inp 是否都使用了 vdbias 偏置电压。

vdbias 偏置电压在 si.inp 里以一个电压源行的形式出现，形如：
    vdbias vdbias! 0 dc=pvdias power=0
即第一段是 vdbias、引用了全局节点 vdbias!、并用 dc=pvdias 取值（pvdias 由 .param pvdias=<值> 定义）。以 * 开头的注释行不算。

请编写一个 Python 脚本 scan_vdbias.py，扫描一个根目录下所有 si.inp 文件（文件名等于 si.inp 或以 .si.inp 结尾），逐个判断是否「使用了 vdbias」，并输出一份结构化 JSON 报告。

脚本命令行用法：
    python3 scan_vdbias.py <root_dir> [-o report.json]
不指定 -o 时把 JSON 打到 stdout，指定 -o 时写到该文件。

JSON 报告必须包含以下字段：
- total_folders：根目录下顶层子文件夹的数量
- total_si：扫描到的 si.inp 文件总数
- used_count：「使用了 vdbias」（含 active vdbias 电压源行）的 si.inp 个数
- pvdias_values：dict，键为 .param pvdias 的取值（字符串），值为出现该取值且确实使用了 vdbias 的文件数（仅有 active vdbias 行但缺 .param pvdias 的文件不计入此 dict）
- no_vdbias：list，未使用 vdbias 的 si.inp 相对根目录的路径（排序）
- per_folder：list，每个顶层子文件夹一项 {folder, si_count, used}

作为输入样例，附件 aging_A 目录是一个小规模示例（4 个 Aging 文件夹、共 8 个 si.inp），你可以用它来理解和验证你的脚本。注意：真实的 ~40 个 Aging 文件夹结构与 aging_A 类似但规模/取值/命名都不同，评测时会在一组你看不到的真实 si.inp 目录上运行你的脚本。

交付：把 scan_vdbias.py 打包成 outputs/submit.zip 提交。
""")

# ---- task_brief.md ----
wr(os.path.join(AST, "task_brief.md"),
"""# EDA-Eval-DesignFlow-VdbiasScanProduce-001

## 真实来源
trace_source: tongfanl @ hfeg0pgn072, session 1795051092028_wm05l (mc=90)
真实任务: 扫描 ~40 个 Aging 仿真结果文件夹的子文件夹中的 si.inp，确认是否都用了 vdbias 偏置电压。

## 任务形态
Produce（写脚本）。交付 scan_vdbias.py（打包 outputs/submit.zip）。

## 判分
check(deliverable, workdir) 双参，14 条独立断言：
- a-i (9 B-side): 在隐藏 aging_B 上跑候选，校验 zip/py_compile/JSON/6 键/total_si/used_count/pvdias_values/no_vdbias/per_folder
- j-n (5 A'-gold 交叉, §4.9 anti-hardcode): 在隐藏 aging_Ap 上跑候选，A' 与 B 在文件夹名/pvdias 取值/文件数上结构性不相交，B-only 硬编码 stub 在 A' 上 FAIL

## 隐藏输入
- hidden/aging_B: 5 文件夹 / 12 si.inp / used=9 (SUT 不可见)
- hidden_a/aging_Ap: 3 文件夹 / 7 si.inp / used=5 (SUT 不可见, anti-hardcode)

## 可见输入
- assets/aging_A: 4 文件夹 / 8 si.inp / used=6 (样例)
""")

print("negatives + selftest + ref_zip + prompt created")
print("B_GOLD:", B_GOLD_JSON[:120])
