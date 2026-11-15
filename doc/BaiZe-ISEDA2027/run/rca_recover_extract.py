#!/usr/bin/env python3
"""
rca_recover_extract.py — RCA 抽取丢码回补工具（2026-11-16 取证更正）

根因（已取证，推翻早先「ws vs no-ws」假说）：
  eda_fastmcp/pyAether-eval/script/format_cline_cli_output.py 的 Step5 用
  **共享相对临时目录** `./pyAether-eval/temp/pyAether_code`（L95/L156-157），
  且 process_cline_gene_files 开头 `shutil.rmtree` 清空它。当 36.15 上多个 eval
  并发跑 Step5 时，后启动者的 rmtree 会踩空前者已拷进去的 .py → generations
  jsonl 只剩 0~1 行。extractor 读的目标路径其实是对的（`code/<task>/pyAether_code`，
  L165，不是 ws/ 子目录；实测仅 1 个 task 有 ws/）。
  实测：run2 batch code/ 有 44 个真实 .py（全 mtime ≤ 14:17:31），
        但 code_generation_2026_1115_110506.jsonl 只 1 行；run3=37→1 行；run4=43→0 字节。

本工具：直接从 `code/<task>/pyAether_code/`（及 `ws/pyAether_code/` 兜底）重新抽取
        .py 写回 generations jsonl，**完全绕过共享 temp**，再由 run_eval 重跑即可
        恢复真实 execution_results。并发安全（读 code/ 直写独立文件，不经共享 temp）。
  （不改 eda_fastmcp 代码；作为 post-pipeline 回补 wrapper，遵守 08:1x 纪律。）

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
