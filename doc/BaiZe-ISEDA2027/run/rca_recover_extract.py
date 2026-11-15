#!/usr/bin/env python3
"""
rca_recover_extract.py — RCA 抽取丢码回补工具（2026-11-15）

根因：eda_fastmcp/pyAether-eval/script/format_cline_cli_output.py:166 只从
  code/<task>/ws/pyAether_code/*.py 抽取代码，但 zhulong agent 常把代码写到
  code/<task>/pyAether_code/*.py（无 ws 子目录）→ 被 silently drop。
  实测 run2 丢 48/54、run3 丢 37/49 个真实代码文件 → generation_success 被压成 1。

本工具：把 no-ws 路径的 .py 回补进 completed_code_generation_<batch>.jsonl，
        再由 run_eval 重跑即可恢复真实 execution_results。
  （不修改 eda_fastmcp 代码；作为 post-pipeline 回补 wrapper，遵守 08:1x 纪律。）

用法（在 36.15 上，batch 跑完 run_cline_script.sh 之后）：
  python rca_recover_extract.py <batch_dir> <completed_code_generation_NAME.jsonl>
  python scripts/run_eval.py -g <completed_code_generation_NAME.jsonl> --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl

例：
  python rca_recover_extract.py ~/eda_code_eval/2026_1115_110506 completed_code_generation_2026_1115_110506.jsonl
"""
import json, os, sys
from pathlib import Path


def recover(batch_dir: Path, gen_name: str) -> int:
    gp = Path.home() / "eda_code_eval" / gen_name
    existing = {}
    if gp.is_file():
        for line in open(gp):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            existing[r["task_id"]] = r
    code_root = batch_dir / "code"
    recovered = 0
    for td in sorted(code_root.glob("EDA-Eval-PyAether-*/")):
        tid = td.name
        found = None
        # 先 ws/pyAether_code（原管线目标），再 pyAether_code（无 ws，被丢的）
        for sub in ("ws/pyAether_code", "pyAether_code"):
            d = td / sub
            if d.is_dir():
                cands = [f for f in os.listdir(d)
                         if f.endswith(".py") and not f.startswith(("test_", "explore_")) and f != "README.md"]
                if cands:
                    found = d / sorted(cands)[-1]
                    break
        if found and (tid not in existing or existing[tid].get("completion", "").strip() in ("", "pass")):
            existing[tid] = {"task_id": tid, "completion": found.read_text(), "status": "success"}
            recovered += 1
    with open(gp, "w") as f:
        for tid in sorted(existing):
            f.write(json.dumps(existing[tid], ensure_ascii=False) + "\n")
    print(f"[rca_recover] recovered {recovered} no-ws code files into {gen_name} (total {len(existing)} tasks)")
    return recovered


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    recover(Path(sys.argv[1]).expanduser(), sys.argv[2])
