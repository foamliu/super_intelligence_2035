#!/usr/bin/env python3
"""Append SvUsedModelExtract-001 case to EDA-Eval-DesignFlow_B.jsonl."""
import json, hashlib, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CASE_ID = "EDA-Eval-DesignFlow-SvUsedModelExtract-001"
REF_DIR = os.path.join(BENCH, "reference", CASE_ID)
CHECK_PY = os.path.join(REF_DIR, "check.py")

# read check.py -> test string
with open(CHECK_PY, encoding="utf-8") as f:
    test_src = f.read()
disk_sha = hashlib.sha256(test_src.encode("utf-8")).hexdigest()
print("disk check.py sha256:", disk_sha, "len:", len(test_src))

# read prompt
with open(os.path.join(BENCH, "assets", CASE_ID, "prompt.txt"), encoding="utf-8") as f:
    prompt = f.read()

entry = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/netlist_A1.v" % CASE_ID,
        "assets/%s/simlib_A1.sv" % CASE_ID,
        "assets/%s/netlist_A2.v" % CASE_ID,
        "assets/%s/simlib_A2.sv" % CASE_ID,
        "assets/%s/netlist_A3.v" % CASE_ID,
        "assets/%s/simlib_A3.sv" % CASE_ID,
    ],
    "test": test_src,
    "metadata": {
        "trace_source": {
            "user": "e0039602",
            "host": "hfeg0pkn004",
            "session_file": "1793956185129_xyou8.messages.json",
            "match_count": 116,
            "real_task_summary": "verilog simlib used-model extraction;用户(e0039602@hfeg0pkn004)给3对(netlist.v, simlib.sv),要求提取SV里被网表用到的model(名字在网表module定义中出现),舍弃未用的,合并成规范SV文件;后续补充保留`celldefine/`endcelldefine包裹;金标准=assistant _extract2.py:HDR_RE module名,used=sv_names&v_names(module定义名),extract_cell向后搜未闭合`celldefine+向前搜`endcelldefine,跨3对去重合并1543 models"
        },
        "domain": "spice_sim",
        "track": "faithful",
        "difficulty": "L1",
        "k_check": 14,
        "k_rationale": 14,
        "test_rationale": (
            "14 条断言：①submit.zip 含 .py 提取脚本 ②脚本能 py_compile 通过 "
            "③脚本在 B(3对netlist/sv)上运行 exit 0 产出 out.json "
            "④out.json 为 dict 且含 4 个必需键(per_pair/merged_count/merged_models/all_have_celldefine)且 per_pair 为 3 项列表 "
            "⑤per_pair[0].sv_total==3(B pair1 SV model 总数) "
            "⑥per_pair[0].kept_models 集合=={invX,bufZ}(B pair1 被 netlist 用到的 model) "
            "⑦per_pair[0].dropped_models 集合=={dropB1}(未被 netlist 用到的 SV model 被舍弃) "
            "⑧merged_count==6(跨 3 对去重后的 unique model 数) "
            "⑨merged_models 集合=={invX,bufZ,and2,or4,xor5,mux2}(各对 kept 的并集) "
            "⑩all_have_celldefine==False(B 中 xor5 缺 `celldefine 包裹) "
            "⑪交叉输入守卫:在 A 上运行 pair1 kept=={invY,invYx4} 且 merged_count==6(证明非硬编码 B) "
            "⑫A-only model 名(invY/invYx4/nand2/bufLx12/inv/bufLx24/AbusDrv_unused/CK_LbusDrv_unused/dropMe3/AF_buf_BiasVLowN)不泄漏进 B 的 merged_models "
            "⑬B 上 3 次运行 sha256 一致(幂等) "
            "⑭per_pair[1].sv_total==2(B pair2 SV model 总数,与 pair1 不同)"
        ),
    },
}

# verify test sha matches disk
entry_sha = hashlib.sha256(entry["test"].encode("utf-8")).hexdigest()
assert entry_sha == disk_sha, "test sha mismatch: entry=%s disk=%s" % (entry_sha, disk_sha)
print("test sha match ✓")

# append (one JSON per line)
with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify by re-reading last line
with open(JSONL, encoding="utf-8") as f:
    lines = f.readlines()
last = json.loads(lines[-1])
last_sha = hashlib.sha256(last["test"].encode("utf-8")).hexdigest()
assert last["id"] == CASE_ID, "last line id mismatch"
assert last_sha == disk_sha, "re-read test sha mismatch"
print("appended %s as jsonl line %d (test sha == disk ✓)" % (CASE_ID, len(lines)))
print("k_check=%d k_rationale=%d" % (last["metadata"]["k_check"], last["metadata"]["k_rationale"]))
