#!/usr/bin/env python3
"""Sync EDA-Eval-DesignFlow-Ddr5ClDelayPivot-001 jsonl entry after anti-hardcode fix."""
import json, os, fcntl, hashlib, tempfile, shutil

JSONL = '/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl'
CHECK = '/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/Ddr5ClDelayPivot-001/check.py'
TARGET = 'EDA-Eval-DesignFlow-Ddr5ClDelayPivot-001'

check_src = open(CHECK).read()
check_sha = hashlib.sha256(check_src.encode()).hexdigest()
check_size = os.path.getsize(CHECK)

NEW_RATIONALE = (
    "14 条断言："
    "①(zip 含 ddr5_cl_delay_pivot.py + 源码非空 + 无禁 import[subprocess/socket/urllib/ctypes/numpy/pandas] "
    "+ 无禁 call[eval/exec/__import__] + 无 B/C 字面量泄漏[TS_9500/TS_9200/TS_8600/TS_8400/TS_8200/TS_7600/"
    "TS_6800/TS_6720/TS_6000/TS_5200/TS_4400/TS_3600/TS_1600/TS_9800/TS_8900/TS_7800/TS_7000/TS_6200/TS_5400/"
    "TS_4600/TS_3800 等]) "
    "②(py_compile 通过) "
    "③(SUT 跑隐藏 B 输入退 0 + 产 pivot_B.csv) "
    "④(CSV header 严格为 Speed Grade,SS (ns),TT (ns),FF (ns),tCK (ns) 5 列) "
    "⑤(数据行数 == B 的速度档数 13) "
    "⑥(各行 Speed Grade 名按文件出现顺序全匹配 oracle) "
    "⑦(tCK 列对所有行匹配 oracle,3 位小数 = round(2000/dr,3)) "
    "⑧(SS/TT/FF 三列 delay 对所有行匹配 oracle,2 位小数 = round(CL_tCK×2000/dr,2)) "
    "⑨(反硬编码嵌入 C 变体:C 行数≠B + C 档名与 B 不相交 + C 各行值匹配 C oracle) "
    "⑩(§4.9 隐藏 A' 变体:SUT 跑 A'(从 B 派生 CL+4 移位)退 0 + 产 pivot_Ap.csv) "
    "⑪(A' header 严格为 5 列同 B) "
    "⑫(A' 行数 == A' oracle == B 行数 13,TS 签名不可区分) "
    "⑬(A' 各行 Speed Grade 名按序匹配 A' oracle,与 B 同名同序) "
    "⑭(A' SS/TT/FF/tCK 各行值匹配 A' oracle[核心交叉:B-hardcode stub 在 A' 上吐 B-gold 18.95 vs A'-gold 19.79 击穿] "
    "+ A'-gold 与 B-gold 显式不相等)"
)

# read all lines
with open(JSONL) as f:
    lines = f.readlines()
assert len(lines) == 565, f"unexpected line count: {len(lines)}"

found = False
new_lines = []
for line in lines:
    d = json.loads(line)
    if d.get('task_id') == TARGET:
        found = True
        d['test'] = check_src
        d['metadata']['k_check'] = 14
        d['metadata']['k_rationale'] = 14
        d['metadata']['test_rationale'] = NEW_RATIONALE
        d['metadata']['check_sha256'] = check_sha
        d['metadata']['check_size'] = check_size
        line = json.dumps(d, ensure_ascii=False) + '\n'
    new_lines.append(line)
assert found, "target entry not found"

# atomic write with flock
tmp = JSONL + '.tmp'
with open(tmp, 'w') as f:
    f.writelines(new_lines)
# acquire lock on target
lockfd = open(JSONL + '.lock', 'w')
fcntl.flock(lockfd, fcntl.LOCK_EX)
try:
    shutil.move(tmp, JSONL)
finally:
    fcntl.flock(lockfd, fcntl.LOCK_UN)
    lockfd.close()

# verify
with open(JSONL) as f:
    n = sum(1 for _ in f)
print(f"jsonl lines: {n}")
for line in open(JSONL):
    d = json.loads(line)
    if d.get('task_id') == TARGET:
        m = d['metadata']
        print(f"k_check={m['k_check']} k_rationale={m['k_rationale']}")
        print(f"check_size={m['check_size']} check_sha={m['check_sha256'][:16]}...")
        print(f"test len={len(d['test'])}")
        print(f"rationale len={len(m['test_rationale'])}")
        # dup check
        break
# integrity: no duplicate task_ids
seen = {}
for line in open(JSONL):
    d = json.loads(line)
    tid = d.get('task_id')
    seen[tid] = seen.get(tid,0)+1
dups = {k:v for k,v in seen.items() if v>1}
print(f"duplicates: {dups if dups else 'none'}")
