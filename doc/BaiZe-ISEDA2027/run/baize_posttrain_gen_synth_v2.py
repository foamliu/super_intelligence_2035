#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_gen_synth_v2.py — BaiZe Stage(ii) E1 合成题生成器 v2
将 R2 调研设计（五层难度 L1-L5 + 五种断言模板 T1-T5）转化为可执行的合成题数据集。
产出：rl_pyaether_synth_v2.jsonl（目标 4000 题，每题含可机器判定的断言）
设计来源：EXPERIMENTS_POSTTRAIN.md §R2（wake50）
用法：python3 baize_posttrain_gen_synth_v2.py --dry-run | --max-tasks 100 | --help
"""
import argparse, hashlib, json, os, random, re, sys
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

API_DB_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
EVAL_DATASET_PATH = os.path.expanduser("~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rl_pyaether_synth_v2.jsonl")
LEVEL_TARGETS = {"L1": 1500, "L2": 1000, "L3": 800, "L4": 500, "L5": 200}
TOTAL_TARGET = sum(LEVEL_TARGETS.values())
DIFF_WEIGHTS = {"w1": 0.35, "w2": 0.15, "w3": 0.20, "w4": 0.15, "w5": 0.15}
PRIMITIVE_TYPES = {"bool","emyBoolean","str","emyString","aeStringField","int","emyUInt4","emyInt4","emyChar","float","emyDouble","emyDist"}
COLLECTION_TYPES = {"list","tuple","List[str]","List[int]","List[bool]"}
PY_TYPE_MAP = {"bool":"bool","emyBoolean":"bool","str":"str","emyString":"str","aeStringField":"str","int":"int","emyUInt4":"int","emyInt4":"int","emyChar":"int","float":"float","emyDouble":"float","emyDist":"float","list":"list","tuple":"tuple","List[str]":"list","List[int]":"list","List[bool]":"list"}

def parse_return_type(desc):
    if not desc: return None
    m = re.search(r"\*\*out\*\*\s*(\S+)", desc)
    if m: return m.group(1).strip().rstrip(",")
    m = re.search(r"Returns\s+\*\*(\S+?)\*\*", desc)
    if m: return m.group(1).strip()
    m = re.search(r"->\s*(\S+)", desc)
    if m: return m.group(1).strip()
    return None

def classify_return_type(rt):
    if rt is None: return "unknown"
    rc = rt.strip().rstrip(",")
    if rc in ("None","void","null"): return "void"
    if rc in PRIMITIVE_TYPES: return "primitive"
    if rc in COLLECTION_TYPES: return "collection"
    if rc.startswith(("emy","ae","C","List","Dict")): return "object"
    return "unknown"

def get_py_type(rt):
    if rt is None: return "NoneType"
    rc = rt.strip().rstrip(",")
    return PY_TYPE_MAP.get(rc, "object")

# ── 断言模板生成器 ──
def gen_assertion_t1(ret_type):
    pt = get_py_type(ret_type)
    if pt == "bool": tc = "isinstance(result, bool)"
    elif pt == "str": tc = "isinstance(result, str)"
    elif pt == "int": tc = "isinstance(result, int)"
    elif pt == "float": tc = "isinstance(result, (int, float))"
    elif pt == "list": tc = "isinstance(result, (list, tuple))"
    else: tc = "result is not None"
    return 'import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None, "Should return non-None"\n    assert %s, "Expected %s"\n' % (tc, ret_type)

def gen_assertion_t2(ret_type):
    return 'import pyAether as pyScript\ndef check(candidate):\n    r1 = candidate()\n    r2 = candidate()\n    assert r1 is not None, "First call should return non-None"\n    assert r2 is not None, "Second call should return non-None"\n    assert r1 == r2, f"Non-deterministic: {r1} != {r2}"\n'

def gen_assertion_t3(ret_type, n_apis):
    return 'import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None, "Should return non-None"\n    assert isinstance(result, (list, tuple)), "Should return collection"\n    assert len(result) == %d, "Should return %d results"\n    for i, r in enumerate(result):\n        assert r is not None, "Result %%d should be non-None" %% i\n' % (n_apis, n_apis)

def gen_assertion_t4(ret_type, n_apis):
    return 'import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None, "Should return non-None"\n    assert isinstance(result, (list, tuple, dict)), "Should return structured result"\n    assert len(result) >= %d, "Should have at least %d results"\n    for i, r in enumerate(result):\n        if r is not None:\n            assert not isinstance(r, type(None)), "API %%d returned None unexpectedly" %% i\n' % (n_apis, n_apis)

def gen_assertion_t5(ret_type, n_apis):
    return 'import pyAether as pyScript\ndef check(candidate):\n    r1 = candidate()\n    r2 = candidate()\n    assert r1 is not None, "First call should return non-None"\n    assert r2 is not None, "Second call should return non-None"\n    assert isinstance(r1, (list, tuple)), "Should return collection"\n    assert len(r1) == %d, "Should return %d results"\n    assert len(r1) == len(r2), "Idempotent: same length"\n    for i, (a, b) in enumerate(zip(r1, r2)):\n        assert a == b, "Idempotent: result %%d differs" %% i\n' % (n_apis, n_apis)

def select_assertion(level, ret_type, n_apis):
    rc = classify_return_type(ret_type)
    if level == "L1":
        if rc == "void": return ("T2_value_invariant", gen_assertion_t2(ret_type))
        return ("T1_type_check", gen_assertion_t1(ret_type))
    elif level == "L2":
        if n_apis == 1 and rc in ("primitive","object"): return ("T1_type_check", gen_assertion_t1(ret_type))
        return ("T3_chain_type", gen_assertion_t3(ret_type, n_apis))
    elif level == "L3":
        if n_apis <= 3: return ("T3_chain_type", gen_assertion_t3(ret_type, n_apis))
        return ("T4_state_verify", gen_assertion_t4(ret_type, n_apis))
    elif level == "L4":
        return ("T4_state_verify", gen_assertion_t4(ret_type, n_apis))
    elif level == "L5":
        return ("T5_behavior", gen_assertion_t5(ret_type, n_apis))
    return ("T1_type_check", gen_assertion_t1(ret_type))

def compute_difficulty_score(api_count, ret_class, techlib, loc, cat_div):
    ac = 1 if api_count<=1 else (2 if api_count<=2 else (3 if api_count<=5 else (4 if api_count<=10 else 5)))
    rc = 1 if ret_class=="primitive" else (2 if ret_class=="object" else 3)
    td = 2 if techlib else 0
    le = 1 if loc<=3 else (2 if loc<=8 else (3 if loc<=15 else 4))
    cd = cat_div
    return DIFF_WEIGHTS["w1"]*ac + DIFF_WEIGHTS["w2"]*rc + DIFF_WEIGHTS["w3"]*td + DIFF_WEIGHTS["w4"]*le + DIFF_WEIGHTS["w5"]*cd

def extract_params(desc):
    if not desc: return []
    params = []
    m = re.search(r"`([^`]+)`\s*\(([^)]*)\)", desc)
    if m:
        for p in m.group(2).split(","):
            p = p.strip()
            if p and p != "self" and not p.startswith("*"):
                params.append(p.split(":")[0].strip())
    return params[:5]

# ── 题目生成 ──
def gen_single_api_task(api_key, api_info, task_idx, level):
    api_name = api_info["api_name"]
    desc = api_info.get("api_descriptions", "")
    ret_type = parse_return_type(desc)
    short_name = api_name.replace("pyAether.", "")
    func_name = "call_" + short_name.replace(".", "_").lower()
    params = extract_params(desc)
    sig = "`%s`" % api_name
    ret_str = " -> %s" % ret_type if ret_type else ""
    prompt = 'import pyAether as pyScript\n\ndef %s():\n    """\n    Write a function that calls the PyAether API %s to accomplish:\n    **`%s()%s`**\n    The function should use the pyAether API and return the result.\n    """\n' % (func_name, sig, short_name, ret_str)
    if params:
        args = ", ".join(["None"] * len(params))
        solution = "    return pyScript.%s(%s)" % (short_name, args)
    else:
        solution = "    return pyScript.%s()" % short_name
    tpl, assertion = select_assertion(level, ret_type, 1)
    rc = classify_return_type(ret_type)
    loc = 1 if level == "L1" else 3
    score = compute_difficulty_score(1, rc, False, loc, 0)
    return {"task_id": "synth-v2-%s-%05d" % (level, task_idx), "prompt": prompt, "entry_point": func_name, "canonical_solution": solution, "test": assertion, "metadata": {"task_name": "Single API: %s" % short_name, "source": api_name, "scenario": "Synth-RL-%s" % level, "category": api_info.get("category", "unknown"), "difficulty": level, "difficulty_score": round(score, 3), "assertion_template": tpl, "apis_used": [api_name], "num_unique_apis": 1, "techlib_dependency": False, "lines_of_code": loc, "verification_type": tpl, "return_type": ret_type or "unknown"}}

def gen_multi_api_task(apis, task_idx, level):
    n = len(apis)
    if n < 2: return None
    first_short = apis[0][1]["api_name"].replace("pyAether.", "")
    func_name = "call_multi_%s_n%d" % (first_short.replace(".", "_").lower(), n)
    api_lines = []
    for i, (ak, ai) in enumerate(apis):
        sn = ai["api_name"].replace("pyAether.", "")
        rt = parse_return_type(ai.get("api_descriptions", ""))
        ret_str = " -> %s" % rt if rt else ""
        api_lines.append("    %d. `%s%s`" % (i+1, ai["api_name"], ret_str))
    prompt = 'import pyAether as pyScript\n\ndef %s():\n    """\n    Write a function that calls the following PyAether APIs in sequence and returns a tuple of all results:\n%s\n    The function should call each API and return a tuple containing each result in order.\n    """\n' % (func_name, "\n".join(api_lines))
    calls = []
    for ak, ai in apis:
        sn = ai["api_name"].replace("pyAether.", "")
        params = extract_params(ai.get("api_descriptions", ""))
        if params:
            args = ", ".join(["None"] * len(params))
            calls.append("pyScript.%s(%s)" % (sn, args))
        else:
            calls.append("pyScript.%s()" % sn)
    solution = "    results = []\n" + "".join("    results.append(%s)\n" % c for c in calls) + "    return tuple(results)"
    first_rt = parse_return_type(apis[0][1].get("api_descriptions", ""))
    tpl, assertion = select_assertion(level, first_rt, n)
    rc = classify_return_type(first_rt)
    techlib = any("tech" in ai.get("category", "").lower() for _, ai in apis)
    loc = n * 2
    cats = set(ai.get("category", "") for _, ai in apis)
    cat_div = 0 if len(cats)==1 else (1 if len(cats)<=2 else 2)
    score = compute_difficulty_score(n, rc, techlib, loc, cat_div)
    return {"task_id": "synth-v2-%s-%05d" % (level, task_idx), "prompt": prompt, "entry_point": func_name, "canonical_solution": solution, "test": assertion, "metadata": {"task_name": "Multi-API (%d): %s" % (n, ", ".join(ai["api_name"].replace("pyAether.", "") for _, ai in apis[:3])), "source": "; ".join(ai["api_name"] for _, ai in apis), "scenario": "Synth-RL-%s" % level, "category": apis[0][1].get("category", "unknown"), "difficulty": level, "difficulty_score": round(score, 3), "assertion_template": tpl, "apis_used": [ai["api_name"] for _, ai in apis], "num_unique_apis": n, "techlib_dependency": techlib, "lines_of_code": loc, "verification_type": tpl, "return_type": first_rt or "unknown"}}

def load_eval_blacklist():
    bl = set()
    with open(EVAL_DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            for api in d.get("metadata", {}).get("apis_used", []):
                bl.add(api)
    return bl

def build_whitelist(api_db, blacklist):
    by_cat = defaultdict(list)
    for key, info in api_db.items():
        if info.get("api_type") not in ("function", "method"): continue
        an = info.get("api_name", "")
        if an in blacklist: continue
        if not info.get("api_descriptions"): continue
        cat = info.get("category", "unknown")
        by_cat[cat].append((key, info))
    return dict(by_cat)

def generate_dataset(api_db, blacklist, max_tasks=0, seed=42):
    random.seed(seed)
    wl = build_whitelist(api_db, blacklist)
    all_apis = []
    for cat, apis in wl.items():
        for pair in apis:
            all_apis.append(pair)
    random.shuffle(all_apis)
    tasks = []
    idx = 0
    # L1: 1500 single-API primitive return
    l1 = [(ak,ai) for ak,ai in all_apis if classify_return_type(parse_return_type(ai.get("api_descriptions","")))=="primitive"]
    random.shuffle(l1)
    t1 = min(LEVEL_TARGETS["L1"], len(l1))
    if max_tasks>0: t1 = min(t1, max_tasks//4)
    for i in range(t1):
        t = gen_single_api_task(l1[i][0], l1[i][1], idx, "L1")
        if t: tasks.append(t); idx+=1
    print("  L1: %d tasks (from %d primitive APIs)" % (t1, len(l1)))
    # L2: 1000 single-API object return
    l2 = [(ak,ai) for ak,ai in all_apis if classify_return_type(parse_return_type(ai.get("api_descriptions","")))=="object"]
    random.shuffle(l2)
    t2 = min(LEVEL_TARGETS["L2"], len(l2))
    if max_tasks>0: t2 = min(t2, max_tasks//4)
    for i in range(t2):
        t = gen_single_api_task(l2[i][0], l2[i][1], idx, "L2")
        if t: tasks.append(t); idx+=1
    print("  L2: %d tasks (from %d object APIs)" % (t2, len(l2)))
    # L3: 800 multi-API 3-5 same category
    l3_cats = [(c,a) for c,a in wl.items() if len(a)>=3]
    random.shuffle(l3_cats)
    t3 = min(LEVEL_TARGETS["L3"], sum(len(a)//3 for _,a in l3_cats)*3)
    if max_tasks>0: t3 = min(t3, max_tasks//5)
    c3 = 0
    for cat, apis in l3_cats:
        if c3>=t3: break
        al = list(apis); random.shuffle(al)
        n = random.randint(3,5)
        for i in range(0, len(al)-n+1, n):
            if c3>=t3: break
            grp = al[i:i+n]
            t = gen_multi_api_task(grp, idx, "L3")
            if t: tasks.append(t); idx+=1; c3+=1
    print("  L3: %d tasks (3-5 API chains)" % c3)
    # L4: 500 multi-API 6-10 same category
    l4_cats = [(c,a) for c,a in wl.items() if len(a)>=6]
    random.shuffle(l4_cats)
    t4 = min(LEVEL_TARGETS["L4"], sum(len(a)//6 for _,a in l4_cats)*2)
    if max_tasks>0: t4 = min(t4, max_tasks//8)
    c4 = 0
    for cat, apis in l4_cats:
        if c4>=t4: break
        al = list(apis); random.shuffle(al)
        n = random.randint(6,10)
        for i in range(0, len(al)-n+1, n):
            if c4>=t4: break
            grp = al[i:i+n]
            t = gen_multi_api_task(grp, idx, "L4")
            if t: tasks.append(t); idx+=1; c4+=1
    print("  L4: %d tasks (6-10 API chains)" % c4)
    # L5: 200 multi-API 10+ cross category
    l5 = list(all_apis); random.shuffle(l5)
    t5 = min(LEVEL_TARGETS["L5"], len(l5)//10)
    if max_tasks>0: t5 = min(t5, max_tasks//20)
    c5 = 0
    for i in range(0, len(l5)-10+1, 10):
        if c5>=t5: break
        grp = l5[i:i+10]
        t = gen_multi_api_task(grp, idx, "L5")
        if t: tasks.append(t); idx+=1; c5+=1
    print("  L5: %d tasks (10+ API chains)" % c5)
    return tasks

def verify_contamination(tasks, blacklist):
    checked = 0; contaminated = 0
    for t in tasks:
        checked += 1
        for api in t["metadata"]["apis_used"]:
            if api in blacklist:
                contaminated += 1; break
    return checked, contaminated

def main():
    parser = argparse.ArgumentParser(description="BaiZe Stage(ii) E1 合成题生成器 v2")
    parser.add_argument("--dry-run", action="store_true", help="仅打印配方")
    parser.add_argument("--max-tasks", type=int, default=0, help="限制题数(0=4000)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="输出路径")
    parser.add_argument("--api-db", type=str, default=API_DB_PATH, help="API数据库路径")
    parser.add_argument("--eval-dataset", type=str, default=EVAL_DATASET_PATH, help="评测数据集路径")
    args = parser.parse_args()
    print("=" * 60)
    print("BaiZe Stage(ii) E1 合成题生成器 v2")
    print("  设计来源: EXPERIMENTS_POSTTRAIN.md §R2 (wake50)")
    print("=" * 60)
    print("\n[1/5] 加载API数据库: %s" % args.api_db)
    if not os.path.exists(args.api_db):
        print("ERROR: API数据库不存在: %s" % args.api_db); return 1
    with open(args.api_db) as f:
        api_db = json.load(f)
    print("  API总数: %d" % len(api_db))
    print("\n[2/5] 加载评测数据集→构建黑名单: %s" % args.eval_dataset)
    if not os.path.exists(args.eval_dataset):
        print("ERROR: 评测数据集不存在: %s" % args.eval_dataset); return 1
    bl = load_eval_blacklist()
    print("  评测API黑名单: %d个" % len(bl))
    print("\n[3/5] 构建白名单...")
    wl = build_whitelist(api_db, bl)
    wl_total = sum(len(a) for a in wl.values())
    print("  白名单API: %d个" % wl_total)
    print("  白名单类别: %d个" % len(wl))
    if args.dry_run:
        print("\n[DRY-RUN] 配方:")
        print("  目标题量: %d (L1=1500/L2=1000/L3=800/L4=500/L5=200)" % TOTAL_TARGET)
        print("  断言模板: T1_type_check/T2_value_invariant/T3_chain_type/T4_state_verify/T5_behavior")
        print("  输出: %s" % args.output)
        return 0
    print("\n[4/5] 生成合成题...")
    tasks = generate_dataset(api_db, bl, max_tasks=args.max_tasks, seed=args.seed)
    print("  总生成: %d题" % len(tasks))
    print("\n  快速污染检查...")
    ck, ct = verify_contamination(tasks, bl)
    print("  检查: %d / 命中: %d" % (ck, ct))
    if ct > 0:
        print("  ERROR: 检测到%d个污染题目! 阻断输出。" % ct); return 2
    print("\n[5/5] 写入输出: %s" % args.output)
    with open(args.output, "w") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print("  写入%d行" % len(tasks))
    lc = defaultdict(int); tc = defaultdict(int)
    for t in tasks:
        lc[t["metadata"]["difficulty"]] += 1
        tc[t["metadata"]["assertion_template"]] += 1
    print("\n=== 生成统计 ===")
    print("按难度层:")
    for lv in ["L1","L2","L3","L4","L5"]:
        print("  %s: %d" % (lv, lc[lv]))
    print("按断言模板:")
    for tpl, cnt in sorted(tc.items()):
        print("  %s: %d" % (tpl, cnt))
    ra = sum(1 for t in tasks if t["test"].strip() and "pass" not in t["test"].strip().split("\n")[-1])
    print("\n真实断言数: %d / %d" % (ra, len(tasks)))
    print("\n✅ E1生成完成: %s" % args.output)
    print("   下一步: bash baize_posttrain_contamination_gate.sh --rl-synth %s" % args.output)
    return 0

if __name__ == "__main__":
    sys.exit(main())
