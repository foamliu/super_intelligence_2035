#!/usr/bin/env python3
# _build_spice_deck_pair_diff_001.py -- assemble negatives, reference_submit.zip,
# prompt/task_brief/manifest, and run self-verification for SpiceDeckPairDiff-001.
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "EDA-Eval-DesignFlow-SpiceDeckPairDiff-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)
REFPY = os.path.join(REF, "spice_deck_diff_ref.py")
TOOL = "spice_deck_diff.py"

# --- 1. copy ref -> spice_deck_diff.py (the deliverable name) ---
shutil.copy(REFPY, os.path.join(REF, TOOL))

# --- 2. build negatives ---
NEG = os.path.join(REF, "negative")
shutil.rmtree(NEG, ignore_errors=True)
os.makedirs(NEG, exist_ok=True)

ref_src = open(REFPY).read()

# (a) naive_empty: broken syntax
with open(os.path.join(NEG, "naive_empty.py"), "w") as f:
    f.write("# naive_empty\nimport sys\ndef main(:\n    pass\n")

# (n) naive_hardcode_B: prints hardcoded B report regardless of input
b_report = subprocess.check_output(
    [sys.executable, REFPY,
     os.path.join(ASSETS, "hidden", "deck_ref_B.sp"),
     os.path.join(ASSETS, "hidden", "deck_cmp_B.sp"),
     "/tmp/_b_report.json"]).decode()
b_json = json.load(open("/tmp/_b_report.json"))
hardcode_src = (
    "# naive_hardcode_B (print-expected: emits hardcoded B report regardless of input)\n"
    "import sys, json\n"
    "HARDCODE = " + repr(b_json) + "\n"
    "def main():\n"
    "    if len(sys.argv) != 4:\n"
    "        sys.stderr.write('usage: spice_deck_diff.py <ref> <cmp> <out>\\n'); sys.exit(2)\n"
    "    out = sys.argv[3]\n"
    "    with open(out, 'w') as f:\n"
    "        json.dump(HARDCODE, f, indent=2, sort_keys=True)\n"
    "    print('wrote', out)\n"
    "if __name__ == '__main__': main()\n"
)
with open(os.path.join(NEG, "naive_hardcode_B.py"), "w") as f:
    f.write(hardcode_src)

# (g) fake_core_deleted: real parser but measures.changed always []
fake_core = ref_src.replace(
    '    changed = []\n    for k in sorted(rk & ck):\n        if ref[k] != cmp[k]:\n            changed.append({"name": k, "ref_sig": ref[k], "cmp_sig": cmp[k]})\n    return {"added": added, "removed": removed, "changed": changed}\n',
    '    changed = []  # FAKE: core deleted -- never report changed measures\n    return {"added": added, "removed": removed, "changed": changed}\n',
    1)
assert fake_core != ref_src, "fake_core patch did not apply"
with open(os.path.join(NEG, "fake_core_deleted.py"), "w") as f:
    f.write(fake_core)

# (j) naive_no_alter_count: real parser but alter_count always 0
no_alter = ref_src.replace(
    '            deck["alter_count"] += 1\n',
    '            pass  # naive: do not count .alter\n',
    1)
assert no_alter != ref_src, "no_alter patch did not apply"
with open(os.path.join(NEG, "naive_no_alter_count.py"), "w") as f:
    f.write(no_alter)

# (f) naive_only_options: only options diff, everything else empty
only_opts = (
    "# naive_only_options\n"
    "import sys, json, re\n"
    "def _read(path):\n"
    "    out=[]\n"
    "    for ln in open(path):\n"
    "        s=ln.rstrip()\n"
    "        if s.lstrip().startswith('*'): continue\n"
    "        d=s.find('$')\n"
    "        if d!=-1: s=s[:d]\n"
    "        if s.strip(): out.append(s.strip())\n"
    "    return out\n"
    "def _opts(lines):\n"
    "    d={}\n"
    "    for ln in lines:\n"
    "        if ln.lower().startswith('.option'):\n"
    "            for t in ln.split()[1:]:\n"
    "                if '=' in t:\n"
    "                    k,v=t.split('=',1); d[k.strip().lower()]=v.strip()\n"
    "                else: d[t.strip().lower()]=True\n"
    "    return d\n"
    "def main():\n"
    "    ref=_opts(_read(sys.argv[1])); cmp=_opts(_read(sys.argv[2]))\n"
    "    added=sorted(set(cmp)-set(ref)); removed=sorted(set(ref)-set(cmp))\n"
    "    changed=[{'name':k,'ref':ref[k],'cmp':cmp[k]} for k in sorted(set(ref)&set(cmp)) if ref[k]!=cmp[k]]\n"
    "    rpt={'options':{'added':added,'removed':removed,'changed':changed},\n"
    "         'measures':{'added':[],'removed':[],'changed':[]},\n"
    "         'params':{'added':[],'removed':[],'changed':[]},\n"
    "         'tran':{'changed':False,'ref':[],'cmp':[]},\n"
    "         'stimulus':{'added':[],'removed':[],'changed':[]},\n"
    "         'alter':{'ref_count':0,'cmp_count':0,'delta':0},\n"
    "         'includes':{'added':[],'removed':[]},\n"
    "         'nodeset_probe':{'ref_nodeset':0,'cmp_nodeset':0,'nodeset_delta':0,'ref_probe':0,'cmp_probe':0,'probe_delta':0},\n"
    "         'instances':{'added':[],'removed':[],'changed':[]},\n"
    "         'summary':{}}\n"
    "    json.dump(rpt, open(sys.argv[3],'w'), indent=2, sort_keys=True)\n"
    "    print('wrote',sys.argv[3])\n"
    "if __name__=='__main__': main()\n"
)
with open(os.path.join(NEG, "naive_only_options.py"), "w") as f:
    f.write(only_opts)

# (h) naive_drop_param_added: real parser but params.added always [] (targeted, options untouched)
drop_param = ref_src.replace(
    '    params = _diff_dict(a["params"], b["params"])\n',
    '    params = _diff_dict(a["params"], b["params"])\n    params["added"] = []  # naive: drop params added\n',
    1)
assert drop_param != ref_src, "drop_param patch did not apply"
with open(os.path.join(NEG, "naive_drop_param_added.py"), "w") as f:
    f.write(drop_param)

print("negatives written:", sorted(os.listdir(NEG)))

# --- 3. reference_submit.zip (tool named spice_deck_diff.py) ---
zip_path = os.path.join(REF, "reference_submit.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REF, TOOL), TOOL)
print("reference_submit.zip written:", os.path.getsize(zip_path), "bytes")

# --- 4. negative_selftest.py ---
selftest = '''#!/usr/bin/env python3
# negative_selftest.py -- run every negative through check.py; all must FAIL (NEG_RC=0)
import os, sys, json, zipfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
CHK = os.path.join(HERE, "check.py")
NEG_DIR = os.path.join(HERE, "negative")
WORK = os.path.join(HERE, "__neg_work")
TOOL = "spice_deck_diff.py"

NEGATIVES = [
    "naive_empty.py",          # -> a
    "naive_hardcode_B.py",     # -> n
    "fake_core_deleted.py",    # -> g
    "naive_no_alter_count.py", # -> j
    "naive_only_options.py",   # -> f
    "naive_drop_param_added.py", # -> h
]


def _make_submit(neg_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(neg_path, TOOL)


def _first_fail(res):
    for c in res.get("conds", []):
        if not c[1]:
            return c[0]
    return None


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    neg_rc = 0
    first_fails = []
    for neg in NEGATIVES:
        neg_path = os.path.join(NEG_DIR, neg)
        zip_path = os.path.join(WORK, neg.replace(".py", "_submit.zip"))
        _make_submit(neg_path, zip_path)
        w = os.path.join(WORK, neg.replace(".py", "_wd"))
        shutil.rmtree(w, ignore_errors=True)
        os.makedirs(w, exist_ok=True)
        try:
            p = subprocess.run([sys.executable, CHK, zip_path, w],
                               capture_output=True, text=True, timeout=120)
            res = json.loads(p.stdout)
        except Exception as e:
            res = {"pass": False, "conds": [], "error": str(e)}
        ok = not res.get("pass", False)
        ff = _first_fail(res)
        first_fails.append((neg, ff))
        if ok:
            print("NEG %-26s FAIL-as-expected (first-fail=%s)" % (neg, ff))
        else:
            neg_rc += 1
            print("NEG %-26s UNEXPECTED PASS (first-fail=%s)  <-- BAD" % (neg, ff))
    distinct = len({ff for _, ff in first_fails if ff is not None})
    print("---")
    print("NEG_RC=%d (expect 0)" % neg_rc)
    print("distinct first-fail: %d/%d" % (distinct, len(NEGATIVES)))
    print("first-fails: %s" % first_fails)
    trio = {"naive_empty.py": None, "naive_hardcode_B.py": None, "fake_core_deleted.py": None}
    for neg, ff in first_fails:
        if neg in trio:
            trio[neg] = ff
    trio_distinct = len({v for v in trio.values() if v is not None})
    print("§4.9 trio {empty,hardcode_B,core_deleted} distinct: %s (%d distinct)" % (trio, trio_distinct))
    return 0 if (neg_rc == 0 and trio_distinct == 3) else 1


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
    f.write(selftest)

# --- 5. asset prompt.txt / task_brief.md / hidden_manifest.json ---
prompt = (
    '用户原始需求（逐字）：「I want to know the difference of _finesim.sp and _finesim_pre.sp tell me in chinease」\n'
    '（_finesim.sp = 当前修改后的 FineSim testbench deck，_finesim_pre.sp = 修改前的基线 deck）\n\n'
    '[交付任务] 请编写 Python 工具 spice_deck_diff.py，对比两份 FineSim/HSPICE testbench deck（基线 ref 与待比较 cmp），'
    '产出结构化差异报告 deck_diff.json（JSON）。CLI 用法：spice_deck_diff.py <deck_ref.sp> <deck_cmp.sp> <out.json>，'
    '其中 deck_ref.sp 为基线（_finesim_pre.sp），deck_cmp.sp 为当前（_finesim.sp）。\n\n'
    '需从每份 deck 解析以下类别（仅解析 .alter 块之前的「基线区」语句，.alter 块只计数不并入基线字典，避免覆盖顶层值）：\n'
    '  · .option 行：每个 token 为 NAME（标志）或 NAME=VALUE，存为字典；\n'
    '  · .measure tran <name> ...：name→语句签名（name 之后全部 token 小写化）；\n'
    '  · .param NAME=VALUE ...：name→value 字典；\n'
    '  · .tran <tstep> <tstop> [<tstart>] [<tmax>]：token 列表；\n'
    '  · 激励源 Vxxx/Ixxx ... PULSE|SINE|SIN|PWL|DC|EXP (...)：name→(kind, 参数串小写)；\n'
    '  · .alter：统计出现次数（alter_count）；\n'
    '  · .inc/.include <path>：路径集合；\n'
    '  · .nodeset 与 .probe：分别统计行数；\n'
    '  · Xxxx ... <subckt>：instance name→subckt 名（末 token）。\n'
    '注释行（首非空白为 *）与行内 $ 注释须剔除；以 + 开头的续行并入上一行。\n\n'
    '报告须含 10 个顶层键：options / measures / params / tran / stimulus / alter / includes / nodeset_probe / instances / summary。'
    '每个 diff 类别给出 added（cmp 有 ref 无）/ removed（ref 有 cmp 无）/ changed（同名但内容不同，给出 name+ref+cmp）；'
    'alter 给 {ref_count,cmp_count,delta}；nodeset_probe 给 {ref_nodeset,cmp_nodeset,nodeset_delta,ref_probe,cmp_probe,probe_delta}；'
    'tran 给 {changed(bool),ref,cmp}；summary 给各类别的 added/removed/changed 计数与 alter_delta/nodeset_delta/probe_delta/tran_changed。\n\n'
    '交付：outputs/submit.zip，内含可执行程序 spice_deck_diff.py。可见输入：assets/EDA-Eval-DesignFlow-SpiceDeckPairDiff-001/deck_ref_A.sp（ref）与 deck_cmp_A.sp（cmp）。\n'
)
with open(os.path.join(ASSETS, "prompt.txt"), "w") as f:
    f.write(prompt)

with open(os.path.join(ASSETS, "task_brief.md"), "w") as f:
    f.write(
        "# 交付接口\n"
        "- 工具：spice_deck_diff.py，CLI `<deck_ref.sp> <deck_cmp.sp> <out.json>`\n"
        "- 交付：outputs/submit.zip（仅含 spice_deck_diff.py）；判分用隐藏输入 B 跑候选并校验 deck_diff.json。\n"
    )

manifest = {
    "case": CASE,
    "hidden_inputs": {
        "deck_ref_B.sp": "NAND2-chain baseline deck (structurally different from A)",
        "deck_cmp_B.sp": "NAND2-chain modified deck (different options/measures/params/stimulus/alter/includes/instances from A)",
    },
    "note": "B pair is NOT placed in the SUT sandbox; check.py runs the candidate on B and verifies deck_diff.json against GT_B. Cross-input guard re-runs on visible A.",
}
with open(os.path.join(ASSETS, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print("assets + reference assembled for", CASE)
