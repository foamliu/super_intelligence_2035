#!/usr/bin/env python3
"""AST scan C cases: classify check() return value shape per JUDGE_CONTRACT.md §2."""
import ast, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/C"
REF_DIR   = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference"

def classify_return(node):
    v = node.value
    if v is None:
        return ("BAD", "NONE", "return")
    if isinstance(v, ast.Constant) and isinstance(v.value, bool):
        return ("OK", "BOOL", repr(v.value))
    try:
        from ast import NameConstant
        if isinstance(v, NameConstant) and isinstance(v.value, bool):
            return ("OK", "BOOL", repr(v.value))
    except ImportError:
        pass
    if isinstance(v, ast.Tuple):
        return ("BAD", "TUPLE", "return (...)")
    if isinstance(v, ast.List):
        return ("BAD", "LIST", "return [...]")
    if isinstance(v, ast.Constant):
        if isinstance(v.value, str):
            return ("BAD", "STR", repr(v.value)[:40])
        return ("BAD", "NUM", repr(v.value)[:40])
    try:
        from ast import Num, Str
        if isinstance(v, (Num, Str)):
            return ("BAD", "NUM/STR", "")
    except ImportError:
        pass
    if isinstance(v, ast.Dict):
        keys = []
        for k in v.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.append(k.value)
            else:
                keys.append("?")
        if "pass" in keys or "ok" in keys:
            return ("OK", "DICT", "{" + ",".join(keys) + "}")
        return ("BAD", "DICT-BAD", "{" + ",".join(keys) + "}")
    if isinstance(v, ast.Name):
        return ("BAD", "OTHER", "return " + v.id)
    return ("BAD", "OTHER", ast.dump(v)[:60])

def find_check_returns(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            returns = []
            stack = [node]
            visited = set()
            while stack:
                cur = stack.pop()
                if id(cur) in visited:
                    continue
                visited.add(id(cur))
                if isinstance(cur, ast.Return):
                    returns.append((cur.lineno, classify_return(cur)))
                for child in ast.iter_child_nodes(cur):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                        continue
                    stack.append(child)
            return returns
    return None

def scan_case(case_id):
    ref_path = os.path.join(REF_DIR, case_id, "check.py")
    if not os.path.exists(ref_path):
        return None
    try:
        with open(ref_path, "r", errors="replace") as f:
            src = f.read()
        tree = ast.parse(src)
    except Exception as e:
        return ("PARSE-ERR", str(e)[:50], None)
    returns = find_check_returns(tree)
    if returns is None:
        return ("NO-CHECK", "", None)
    bads = [r for _, r in returns if r[0] == "BAD"]
    if not bads:
        return ("OK", "", returns)
    subtags = sorted(set(r[1] for r in bads))
    return ("BAD", "/".join(subtags), returns)

def main():
    cases = sorted(c[:-5] for c in os.listdir(CASES_DIR) if c.endswith(".json"))
    bad_list = []
    ok_count = 0
    other = 0
    subtag_counts = {}
    for cid in cases:
        res = scan_case(cid)
        if res is None:
            other += 1
            continue
        if res[0] == "OK":
            ok_count += 1
        elif res[0] == "BAD":
            subtag_counts[res[1]] = subtag_counts.get(res[1], 0) + 1
            bad_list.append((cid, res[1], res[2]))
        else:
            other += 1
    print(f"# Total cases: {len(cases)}")
    print(f"# OK: {ok_count}")
    print(f"# BAD: {len(bad_list)}")
    print(f"# OTHER: {other}")
    print(f"# Subtag counts: {subtag_counts}")
    print(f"# BAD list ({len(bad_list)}):")
    for cid, subtag, returns in bad_list:
        last = returns[-1] if returns else (0, ("?","?","?"))
        print(f"{cid}\t{subtag}\tlast_return=L{last[0]}={last[1][1]}:{last[1][2]}")

if __name__ == "__main__":
    main()
