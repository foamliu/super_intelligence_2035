# deepread — u33un (e0030760 @ hfeg0plg52) — Solido HSV RSNM custom-output parser fail

- session_file: `1795143327362_u33un.messages.json` (16 msgs, 215KB)
- user: e0030760  ·  host: hfeg0plg52 (10.129.35.68)  ·  mc: 19 (hspice-dominant)
- domain: characterization (shard B spice_char)  ·  tier: A (trace-faithful)
- 落库 case_id: **EDA-Eval-DesignFlow-SolidoRsnmParserFix-001** (r942, 2026-11-21)
- ledger row: 1647 (B)

## 用户原话 (msg0，逐字保留)

> /proj/lacaa/V0/workdir/e0039809/solido/HD_6T_CH252_RSNM/results/HSV-0 检查一下这个HSV的模拟结果为什么读取RSNM失败？

## 真实任务上下文

e0030760 在 hfeg0plg52 上跑 CXMT CH252 HD 6T SRAM 的 Solido High-Sigma Verifier (HSV) characterization 流（trace 16 msg session, mc=19, hspice-dominant）。HSV 跑完 99 个初始样本（HSPICE 仿真 810.7s 全部完成），但 `summary.json` 报：

```
"Warnings": {"HSNM": ["All simulations have failed."]}
"Dropped aims": {"HSNM-min": "All simulations have failed."}
```

RSNM/HSNM 一个都没读到。trace 中 agent 诊断根因 + 在 msg5/10/12/14 给出完整证据链：

### 证据 1 — `engine.log`（trace msg5，每个样本都报同一条错，从第 27 行起）

```
2026-11-20 10:39:43 39033  user  ERROR: Custom parser "/proj/lacaa/V0/workdir/e0039809/testbench/solido_snm_custom_output.py" failed to run: Outputs file "/proj/lacaa/V0/workdir/e0039809/variation_designer/21fbcc75-c576-4fb1-b98d-dc8575c864c6/00000000/00000003/solido_parameters.out0" is not found after running post-process executable "/proj/lacaa/V0/workdir/e0039809/testbench/solido_snm_custom_output.py".
2026-11-20 10:39:43 39033  user  INFO:  Failed simulation 3 located at .../00000000/00000003.tgz
```

99 个样本全部如此，最后 `summary.json` 把每个样本判成 "failed"。

### 证据 2 — `summary.json` 关键字段（trace msg5）

```json
{
  "Setup": {"Simulator name": "hspice", "Testbenches": ["HD_6T_CH252_RSNM.sp"], "Initial samples simulated": 99},
  "Warnings": {"HSNM": ["All simulations have failed."]},
  "Dropped aims": {"HSNM-min": "All simulations have failed."}
}
```

### 证据 3 — 网表 `HD_6T_CH252_RSNM.sp`（trace msg10）

RSNM read butterfly 网表，**只有 `Q_RNM` / `QB_RNM` 两个节点，没有 `Q_HNM` / `QB_HNM`**：

```
$ Test item: RSNM read butterfly - XRSNML + XRSNMR (WL=VDD), loop broken by VI source
.NODESET V(Q_RNM)=0 V(QB_RNM)=VVDD
...
.PROBE DC  V(Q_RNM)  V(QB_RNM)  V(VI)
.Print DC  V(Q_RNM)
.Print DC  V(QB_RNM)
```

### 证据 4 — 原脚本 `solido_snm_custom_output.py`（trace msg12，258 行）— **根因**

```python
NODES = ("q_rnm", "qb_rnm", "q_hnm", "qb_hnm")   # .Print DC 的列顺序

def parse_dc_per_signal(path):
    ...
    if all(got.get(s) for s in NODES):   # 必须 4 个全有
        return got
    return None                          # 否则返回 None

def parse_dc_merged(path):
    ...
    if all(("v(%s)" % s) in low for s in NODES) and "print" not in low:  # 必须 4 个全有
        hdr = i; break
    ...
    return None

def main():
    ...
    data = None
    for p in find_lis_files(sim_dir):
        data = parse_any(p)
        if data: break
    if not data:
        sys.stderr.write("ERROR: DC sweep tables (%s) not found in %s\n" % (", ".join(NODES), sim_dir))
        sys.exit(1)                      # ← 不写输出文件 → Solido "Outputs file not found"
    ...
    rsnm = snm_butterfly(vin, aligned("q_rnm"),  aligned("qb_rnm"))
    hsnm = snm_butterfly(vin, aligned("q_hnm"),  aligned("qb_hnm"))
    if rsnm is None or hsnm is None:
        sys.exit(1)                      # ← 即便有数据，HSNM 没节点也算 None → 退出
    with open(out_path, "w") as f:
        f.write("HSNM=%.6g\n" % hsnm)
        f.write("RSNM=%.6g\n" % rsnm)
```

### 证据 5 — `project_setup_12.xml`（trace msg14，trace 已读）

项目目录名 `HD_6T_CH252_RSNM` 是 RSNM，但 Solido aim 配的是 `HSNM-min`，原脚本又要 HSNM+RSNM 两个都算——三层目标对不上。

## 根因小结（agent 诊断，trace msg15 agent 总结）

不是仿真失败，是后处理脚本 `solido_snm_custom_output.py` 把"必须同时算 HSNM 和 RSNM"硬编进了 `NODES = (q_rnm, qb_rnm, q_hnm, qb_hnm)`：
- `parse_dc_per_signal` / `parse_dc_merged` 都要求 4 个节点齐全才返回数据；
- 网表只做 RSNM 蝴蝶（只有 `Q_RNM` / `QB_RNM`，无 `Q_HNM` / `QB_HNM`）→ 解析永远返回 `None`；
- `main()` 走 `sys.exit(1)`，不写输出文件 `solido_parameters.out0`；
- Solido 看不到输出文件 → 每个样本判 failed → summary 报 "All simulations have failed"，RSNM/HSNM 都读不到。
- 附带不一致：项目目录名是 RSNM 但 Solido aim 是 HSNM-min，脚本又要两者——三层目标对不上。

## Case 落库（r942, A 档 trace-faithful）

- 交付：纯 Python `solido_snm_parser_fix.py <SIM_DIR> <OUTFILE_NAME>`
  - 核心修复：把原脚本"必须 4 节点齐全否则退出"改成"按可用节点子集弹性计算"——RSNM-only / HSNM-only / both 任一非空子集都成功
  - `parse_dc_per_signal` / `parse_dc_merged` 接受任意非空子集（不再硬性要求 4 节点）
  - 输出按实际可算子集写：HSNM-only → `HSNM=...\n`；4 节点 → `HSNM=...\nRSNM=...\n`（HSNM= 在前，向后兼容）；空 → `sys.exit(1)` 不写 outfile
  - SNM 算法 (`snm_butterfly` / `interp` / `aligned`) 全部不动
- k=16（a–p），ref PASS 16/16
- §4.9 三假（empty/print/core-removed）+ hardcode-A 全 FAIL
- 3-seed 字节 sha256 一致
- visible A（trace-faithful）：RSNM-only 网表 `HD_6T_CH252_RSNM.sp`（Q_RNM/QB_RNM，VIN 0..1.2V, 21 samples, .lis0 文件）+ 原 buggy 脚本
- hidden B（anti-hardcode-A，全异）：**HSNM-only** 节点集（q_hnm/qb_hnm）+ VIN 0..1.0V + 15 samples + `simulator_stdout.log` 文件名
- 4-node 向后兼容 dir：HSNM=0.319547 + RSNM=0.382278（HSNM= 在前），与原脚本逐字节兼容
- 空 dir：exit 1，不创建 outfile（与原脚本失败语义一致）

## self-verify

```
$ python3 negative_selftest.py
PASS  reference (rc=0)
PASS  negative/naive_empty.py (rc=1, expected non-zero)
PASS  negative/print_only.py (rc=1, expected non-zero)
PASS  negative/core_removed.py (rc=1, expected non-zero)
PASS  negative/hardcode_a.py (rc=1, expected non-zero)
All expectations hold (reference PASS, 4 negatives FAIL).
```

ref 实际输出：
- HSNM-only B → `HSNM=0.319547`（无 RSNM=）
- 4-node dir → `HSNM=0.319547\nRSNM=0.382278`（HSNM 在前）
- empty dir → exit 1，不创建 outfile

## 记账

- cases/B 471→472（json 已落）
- B.jsonl 470→471（auto-regen by build_jsonl.py --shard B, SolidoRsnmParserFix 末位）
- ledger_B row 1647：u33un `claimed` → `case` (EDA-Eval-DesignFlow-SolidoRsnmParserFix-001) @ 2026-11-21 01:15

## 后续候选（同 session 不在本 case 范围）

- Solido `project_setup_12.xml` aim 配置不一致修复子任务（HSNM-min aim 配在 RSNM-only 项目目录）
- 99 样本 rerun 后 summary.json 重生成
- `variation_designer` UUID 路径恢复（msg5/agent 提到 `21fbcc75-c576-4fb1-b98d-dc8575c864c6/00000000/00000003/`）
