#!/usr/bin/env python3
"""reconstruct_rerun_trials.py — 从 chunked rerun 的聚合 result.json 重建 per-task result.json.

问题: 使用 --n-concurrent auto + --chunk-size 的 rerun (deepseek/opencode/pi)
      harbor 只产出聚合 result.json (reward_stats/exception_stats), 没有 per-trial
      子目录.  而报告生成器 gen_report_tb21_7way.py 需要读 per-task result.json
      (verifier_result.rewards.reward == 1.0 => passed).

本脚本: 读每个 chunk 的聚合 result.json + lock.json, 为每个 task 重建一个
        per-task result.json, 放到 /tmp/tb21_glm53_jobs/<harness>/ 下的标准结构:
        <dated_dir>_rerun_<tag>/<task>__rerun_<tag>/result.json

用法:
  python3 reconstruct_rerun_trials.py <rerun_jobs_dir> [--harness <name>] [--tag <tag>]
  python3 reconstruct_rerun_trials.py /tmp/tb21_glm53_jobs/deepseek-harness_rerun_20261115_1950 --harness deepseek-harness
"""
import json
import argparse
import time
from pathlib import Path

JOBS = Path("/tmp/tb21_glm53_jobs")


def reconstruct(rerun_jobs: Path, harness: str, tag: str):
    """从聚合 result.json 重建 per-task result.json, 放到 JOBS/<harness>/."""
    dst_root = JOBS / harness
    dst_root.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for dated in sorted(p for p in rerun_jobs.iterdir() if p.is_dir()):
        result_f = dated / "result.json"
        if not result_f.exists():
            continue
        try:
            r = json.loads(result_f.read_text())
        except Exception:
            continue

        dst_dir = dst_root / f"{dated.name}_rerun_{tag}"
        dst_dir.mkdir(parents=True, exist_ok=True)

        evals = r.get("stats", {}).get("evals", {})
        for _ev_name, ev in evals.items():
            # reward_stats: {"0.0": ["task__id", ...], "1.0": ["task__id", ...]}
            rs = ev.get("reward_stats", {}).get("reward", {})
            for reward_str, task_list in rs.items():
                reward = float(reward_str)
                for task_full in task_list:
                    task_name = task_full.split("__")[0]
                    trial_dir = dst_dir / f"{task_name}__rerun_{tag}"
                    trial_dir.mkdir(parents=True, exist_ok=True)
                    tf = trial_dir / "result.json"
                    if tf.exists():
                        skipped += 1
                        continue
                    result = {
                        "task_name": task_name,
                        "verifier_result": {"rewards": {"reward": reward}},
                        "exception_info": None,
                        "_source": "reconstructed_from_aggregate",
                        "_rerun_tag": tag,
                    }
                    tf.write_text(json.dumps(result, indent=2))
                    created += 1

            # exception_stats: {"ExceptionType": ["task__id", ...]}
            es = ev.get("exception_stats", {})
            for exc_type, task_list in es.items():
                for task_full in task_list:
                    task_name = task_full.split("__")[0]
                    trial_dir = dst_dir / f"{task_name}__rerun_{tag}"
                    trial_dir.mkdir(parents=True, exist_ok=True)
                    tf = trial_dir / "result.json"
                    if tf.exists():
                        skipped += 1
                        continue
                    result = {
                        "task_name": task_name,
                        "verifier_result": {"rewards": {"reward": 0.0}},
                        "exception_info": {
                            "exception_type": exc_type,
                            "exception_message": f"reconstructed: {exc_type}",
                        },
                        "_source": "reconstructed_from_aggregate",
                        "_rerun_tag": tag,
                    }
                    tf.write_text(json.dumps(result, indent=2))
                    created += 1

    print(f"[reconstruct] harness={harness} created={created} skipped={skipped} "
          f"-> {dst_root}")
    return created


def main():
    ap = argparse.ArgumentParser(
        description="从 chunked rerun 聚合 result.json 重建 per-task result.json")
    ap.add_argument("rerun_jobs", help="rerun jobs 目录 (如 /tmp/tb21_glm53_jobs/deepseek-harness_rerun_...)")
    ap.add_argument("--harness", default=None,
                    help="目标 harness 名 (默认从目录名推断)")
    ap.add_argument("--tag", default=None,
                    help="rerun tag (默认时间戳)")
    args = ap.parse_args()

    rerun_jobs = Path(args.rerun_jobs)
    harness = args.harness
    if not harness:
        # 从目录名推断: deepseek-harness_rerun_... -> deepseek-harness
        name = rerun_jobs.name
        harness = name.split("_rerun_")[0] if "_rerun_" in name else name
    tag = args.tag or time.strftime("%Y%m%d_%H%M")

    print(f"[config] rerun_jobs={rerun_jobs} harness={harness} tag={tag}")
    reconstruct(rerun_jobs, harness, tag)


if __name__ == "__main__":
    main()
