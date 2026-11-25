#!/usr/bin/env python3
"""
rca_recover_extract.py — RCA 抽取丢码回补工具（2026-11-16 源码取证终版）

根因（经 format_cline_cli_output.py 源码取证，05:xx 终版；更正早先 02:xx 误判）：
  eda_fastmcp/pyAether-eval/script/format_cline_cli_output.py 的 process_cline_gene_files：
    **主因 = ws/no-ws 路径失配**：L166 `folder_path = os.path.join(cli_output,
    folder_name, "ws", "pyAether_code")` 只读 `code/<task>/ws/pyAether_code`（带 ws）；
    L168-170 `if not os.path.exists(folder_path): skip_tasks.append(...); continue`
    无 no-ws 回退。模型把 .py 写到 `code/<task>/pyAether_code`（无 ws）→ 整题跳过
    → generations jsonl 只剩写到 ws/ 的那几条。
    **次因 = 共享 temp race**：L156-157 共享相对 temp `./pyAether-eval/temp/pyAether_code`
    + `shutil.rmtree` 清空；36.15 并发 eval 互踩（真实但非 run2/3/4 主因，因其 ws
    条目本就只有 1/1/0）。
  源码取证（36.15 经 3333 隧道 sed 实读 L155-170）：
    L156 pyAether_code = "./pyAether-eval/temp/pyAether_code"   # 共享相对 temp
    L157 shutil.rmtree(pyAether_code, ignore_errors=True) ...
    L166 folder_path = os.path.join(cli_output, folder_name, "ws", "pyAether_code")  # 带 ws
    L168 if not os.path.exists(folder_path): skip_tasks.append(folder_name); continue  # 无回退
  实测 run2 batch(2026_1115_110506)：ws/ 目录 1 个、no-ws pyAether_code 目录 53 个、
    真实 .py 52 个 → 抽取器只取到 1 → jsonl 真码 1 行(task 003)；
    run3(144001)=1 ws/39 no-ws→1 行(task 107)；run4(183438)=0 ws/45 no-ws→0 行。
    run1=36 ws 段全取到→18.99%。
  （02:xx 版曾误判「extractor 读 no-ws pyAether_code、主因=共享 temp race」——
    该声称与源码 L166 不符，已更正。共享 temp race 降为次因。）

本工具：从 `code/<task>/ws/pyAether_code/`（原管线目标）+ `code/<task>/pyAether_code/`
        （无 ws，被抽取器跳过的）两路重新抽取 .py 写回 generations jsonl，
        **同时绕过抽取器的 ws-only 限制与共享 temp**，再由 run_eval 重跑即可恢复
        真实 execution_results。并发安全（读 code/ 直写独立文件，不经共享 temp）。
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
