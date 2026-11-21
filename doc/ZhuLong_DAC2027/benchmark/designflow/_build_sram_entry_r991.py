#!/usr/bin/env python3
import json, os, sys

CASE="EDA-Eval-DesignFlow-SramVecCovAnalyze-001"
BENCH="/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
BASE=f"{BENCH}/assets/{CASE}"
REF_DIR=f"{BENCH}/reference/{CASE}"

with open(f"{REF_DIR}/check.py") as f: test_py=f.read()
with open(f"{BASE}/A/task_brief.md") as f: task_brief=f.read()

prompt = """我在做 SRAM 宏的 FineSim 仿真验证。宏是 `CXN4HCSPS2048X40M16B2C1R1W1BW1RE1_FS`（2048×40、MUX16、2 bank），已经用 FineSim 跑出了一版功能激励向量文件 `func.vec`（52 个时钟周期，覆盖 read / write / bit-write / column-redundancy / standby）。

真实工作场景（来自真实 trace，用户 e0044131 @ hfeahpc502 session h5giy，spice_sim 域）：我之前跟 agent 说——

- 「参照spec文件,sram的以下功能,在vec文件中,哪些可以验证？」

也就是：给我一份 SRAM spec 功能清单（每个功能给一组信号条件，比如 read = CEB==0 且 WEB==1，bit_write = CEB==0 且 WEB==0 且 BWEB!=全 1）和一份 FineSim `.vec` 激励文件，让我判断 vec 里哪些周期能验证哪个功能、哪些功能没被覆盖到。

附件 `assets/EDA-Eval-DesignFlow-SramVecCovAnalyze-001/` 里有一份 A 输入可以拿来研读格式：`spec_A.json`（5 个功能：read/write/bit_write/col_redundancy/standby，每个带 equals/not_equals 信号条件）和 `func_A.vec`（FineSim vec 格式：radix/io/vname 头 + 数据行，每周期 2 行对应 CLK=0/CLK=1，13 个信号 A[10:0]/CEB/CLK/CRSLA[5:0]/CRSLE/CRSRA/CRSRE/TEST/WEB/BYP/BWEB[39:0]/D[39:0]/Q[39:0]）。

请你交付一个 Python 脚本 `sram_vec_cov_analyze.py`：

```
python3 sram_vec_cov_analyze.py <spec.json> <vec_file> <output.json>
```

1. 解析 `spec.json`：读 macro 信息和 functions 列表（每个 function 有 id/name/conditions，condition 形如 `{"signal":"CEB","equals":"0"}` 或 `{"signal":"BWEB","not_equals":"ffffffffff"}`）。
2. 解析 `.vec` 文件：读 radix/io/vname 头拿到每个信号的位宽和顺序；数据行每两行一个时钟周期（CLK=0 / CLK=1），用 CLK=1 那一行作为该周期的信号取值。equals 比较时把信号值零填充到信号位宽的 hex 串再比较；not_equals 即不等于该串（用于检测 BWEB 部分掩码）。
3. 对每个 spec function，找出满足其全部 conditions 的周期（matching_cycles），covered = 有匹配周期；match_count = 匹配数。
4. verifiability 规则：
   - read：covered 即 verifiable；
   - write：covered 且存在同地址的 read-back 周期（WEB=1）才 verifiable；
   - bit_write：covered（BWEB 部分掩码写入）且有 read-back 才 verifiable；
   - col_redundancy：covered（CRSLE=1）且有 read-back 才 verifiable；
   - test_mode：covered 即 verifiable；
   - standby：covered 即 verifiable；
   - 其余默认 verifiable = covered。
5. 输出 `output.json`，schema：
```
{
  "macro": "<from spec>",
  "total_cycles": <int>,
  "functions": [
    {"id","name","covered","matching_cycles":[...],"match_count","verifiable","evidence"}
  ],
  "summary": {"total_functions","covered","verifiable","not_covered"}
}
```

约束：纯 Python 标准库；必须通用——能在一个**不同的隐藏 SRAM**（不同位宽、不同周期数、不同功能集，可能包含未被覆盖的功能）上正确工作；不得硬编码任何信号值或周期数；输出确定性。最终把 `sram_vec_cov_analyze.py` 打包成 `outputs/submit.zip` 交付。"""

test_rationale = "13 条断言：①(a) submit.zip 有效且解压后含 sram_vec_cov_analyze.py ②(b) 脚本 py_compile 通过 ③(c) 在隐藏 B 上以指定 CLI 运行 exit 0 且产出合法 JSON 对象 ④(d) total_cycles 正确（B=36） ⑤(e) functions 数量正确（B=6）且 id 集合恰为 {read,write,bit_write,test_mode,standby,col_redundancy_right} ⑥(f) read covered 且 match_count 正确（B=20） ⑦(g) write covered 且 verifiable（须存在同地址 read-back 周期） ⑧(h) bit_write covered 且 match_count 正确（B=4，BWEB 部分掩码） ⑨(i) col_redundancy_right **未** covered 且 match_count=0（隐藏 B 中 CRSRE 永不置 1） ⑩(j) standby covered（CEB=1 周期） ⑪(k) test_mode covered 且 match_count 正确（B=2） ⑫(l) 反硬编码 A：输出 JSON 中不得出现任何 A 专属 token（A 宏名/周期数/A 信号值） ⑬(m) 3 个随机种子重跑结论一致（确定性，禁随机/时间戳）"

entry = {
  "id": CASE,
  "task_id": CASE,
  "mode": "design_flow",
  "entry_point": "outputs/submit.zip",
  "prompt": prompt,
  "attachments": [
    f"{BASE}/task_brief.md",
    f"{BASE}/A/spec_A.json",
    f"{BASE}/A/func_A.vec",
    f"{BASE}/A/expected_cycles_A.txt",
  ],
  "task_brief": task_brief,
  "test": test_py,
  "metadata": {
    "domain": "spice_sim",
    "track": "A",
    "layer": "L1",
    "trace_source": {
      "user": "e0044131",
      "host": "hfeahpc502",
      "ip": "10.129.33.25",
      "session_file": "1795054813911_h5giy",
      "match_count": 34,
      "scan_snapshot": "ssh_eda_search_20261120/summary_1120_reconstructed.tsv (B fresh list; h5giy r988 取证合成, r988 MEMORY 误报已落库实未入 B.jsonl, 本轮 r991 补落库)",
      "real_task_summary": "用户 e0044131 @ hfeahpc502 (session h5giy, mc=34, spice_sim/SRAM FineSim 仿真验证) 做 SRAM 宏 CXN4HCSPS2048X40M16B2C1R1W1BW1RE1_FS 的 FineSim 仿真验证, 已生成 func.vec(52 周期覆盖 read/write/bit-write/col-redundancy/standby), 用户原话「参照spec文件,sram的以下功能,在vec文件中,哪些可以验证？」(analysis-Q&A→produce reframe). reframe: produce 参数化 sram_vec_cov_analyze.py(--spec/--vec/--out). asset A: 2048x40 MUX16 2bank/5 功能(read/write/bit_write/col_redundancy/standby)/52 周期/13 信号; hidden B: 1024x32 MUX8 1bank/6 功能(加 test_mode+col_redundancy_right后者uncovered)/36 周期/不同位宽与掩码→anti-hardcode-A."
    },
    "test_rationale": test_rationale,
    "k_rationale": 13,
    "k_check": 13,
    "gold_standard": "assistant 交付: sram_vec_cov_analyze.py 用 argparse 接 spec/vec/out; parse_vec 解析 FineSim vec 头(radix/io/vname)拿信号位宽与顺序, 数据行每 2 行一周期取 CLK=1 行; equals 比较零填充到信号位宽 hex 串, not_equals 检测部分掩码(BWEB!=全1); 对每个 spec function 找满足全部 conditions 的周期(matching_cycles/match_count/covered); verifiability: read=covered, write=covered+同地址read-back, bit_write=covered+read-back, col_redundancy=covered+read-back, test_mode/standby=covered; 输出 JSON 含 macro/total_cycles/functions[]/summary. 参考 sram_vec_cov_analyze_ref.py.",
    "asset_fidelity": "format_faithful_vec_spice",
    "reframe_note": "harness-for-teeth reframe: trace 原意图=analysis-Q&A(用户问 vec 能验证哪些 spec 功能), 判分有牙需参数化通用 CLI(任意 SRAM 宏/位宽/功能集/周期数), 故 reframe 成 produce 参数化 sram_vec_cov_analyze.py; hidden B 异宏(1024x32 MUX8)+异功能集(加 test_mode+col_redundancy_right后者uncovered)+异周期数(36 vs 52)+异位宽与掩码 验通用性与反硬编码 A."
  }
}

json.dumps(entry, ensure_ascii=False)  # validate
out = json.dumps(entry, ensure_ascii=False)

# Append to B.jsonl (only if not already present)
jsonl_path = f"{BENCH}/EDA-Eval-DesignFlow_B.jsonl"
existing = open(jsonl_path).read()
if CASE in existing:
    print("ALREADY PRESENT — not appending")
    sys.exit(1)
with open(jsonl_path, "a") as f:
    f.write(out + "\n")
print("APPENDED. prompt=%d test=%d rationale=%d entry=%d" % (len(prompt), len(test_py), len(test_rationale), len(out)))
# verify
lines = open(jsonl_path).readlines()
print("B.jsonl lines now:", len(lines))
import json as J
J.loads(lines[-1])
print("last line valid JSON, task_id:", J.loads(lines[-1])["task_id"])
