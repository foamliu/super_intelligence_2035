#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""swebench_guarded_eval.py — SWE-bench eval entry with mandatory docker resource limits.

WHY (2026-11-20 用户令·Step 1 硬护栏):
  11-19 夜 deepseek incr_eval R2800 的 matplotlib 评测容器吃穿宿主 ~2TB 内存 → .29 OOM 卡死。
  根因 = swebench v5.0.2 的 create_container() (run_evaluation.py:116-142) 用
  `client.containers.create(...)` 时 **不带任何内存/CPU 上限**，且 daemon.json 无默认限制。
  swebench 用的是 docker Python SDK（非 `docker run` CLI），所以 CLI wrapper 无效；
  必须在 SDK 的 `containers.create()` 调用点注入 `mem_limit`/`memswap_limit`/`nano_cpus`。

HOW:
  本脚本在 import swebench 之前，monkey-patch `docker.models.containers.ContainerCollection.create`，
  给**每一次** create 自动注入：
      mem_limit     = "128g"     (--memory 128g)
      memswap_limit = "128g"     (--memory-swap 128g  = 不可换出超 128g)
      nano_cpus     = 16.0       (--cpus 16)
  然后委托 swebench.harness.run_evaluation.main()，argv 原样透传。

USAGE (替代 `python -m swebench.harness.run_evaluation`):
  python3 swebench_guarded_eval.py \
      --predictions_path X --dataset_name Y --split test \
      --instance_ids A B C --max_workers 1 --run_id Z --timeout 1800

  外层仍应 nice -n 19 ionice -c 3（incr_eval 脚本里已有），本脚本只管 docker 容器上限。

VERIFY:
  python3 swebench_guarded_eval.py --self-test   # 打印 patch 是否生效 + 模拟 create 参数
"""
from __future__ import annotations
import os
import sys

# ── 资源上限（可被环境变量覆盖） ──────────────────────────────────────────
EVAL_MEM_LIMIT     = os.environ.get("EVAL_MEM_LIMIT", "128g")   # --memory
EVAL_MEMSWAP_LIMIT = os.environ.get("EVAL_MEMSWAP_LIMIT", "128g")  # --memory-swap
EVAL_NANO_CPUS     = int(float(os.environ.get("EVAL_NANO_CPUS", "16")) * 1_000_000_000)  # --cpus 16 (int nanocpus)

_PATCHED = False


def _patch_docker_create():
    """Monkey-patch docker SDK 的 ContainerCollection.create，注入内存/CPU 上限。"""
    global _PATCHED
    if _PATCHED:
        return
    import docker.models.containers as _dc  # noqa

    _orig_create = _dc.ContainerCollection.create

    def _guarded_create(self, image, command=None, **kwargs):
        # 只给 sweb.eval.* 容器名加限制（避免误伤别的容器，虽然 harness 线一般只跑这个）
        # 但 swebench 的 create 调用里 name= 已在 kwargs，我们统一加（更安全：所有经过本 SDK 的 create 都限）
        kwargs.setdefault("mem_limit", EVAL_MEM_LIMIT)
        kwargs.setdefault("memswap_limit", EVAL_MEMSWAP_LIMIT)
        kwargs.setdefault("nano_cpus", EVAL_NANO_CPUS)
        return _orig_create(self, image, command, **kwargs)

    _dc.ContainerCollection.create = _guarded_create
    _PATCHED = True


def _self_test():
    """验证 patch 生效：确认 create 已被替换 + setdefault 注入逻辑正确。"""
    _patch_docker_create()
    import docker.models.containers as _dc

    # 1) 确认 create 已被替换为我们的 _guarded_create
    patched_fn = _dc.ContainerCollection.create
    is_patched = patched_fn.__name__ == "_guarded_create"
    print("[self-test] _PATCHED =", _PATCHED)
    print("[self-test] create.__name__ =", patched_fn.__name__, "→ patched" if is_patched else "→ NOT patched!")

    # 2) 验证 setdefault 注入逻辑（用 dict 模拟 kwargs）
    sample = {"name": "sweb.eval.fake.test", "detach": True}
    sample.setdefault("mem_limit", EVAL_MEM_LIMIT)
    sample.setdefault("memswap_limit", EVAL_MEMSWAP_LIMIT)
    sample.setdefault("nano_cpus", EVAL_NANO_CPUS)
    ok = (is_patched
          and sample.get("mem_limit") == EVAL_MEM_LIMIT
          and sample.get("memswap_limit") == EVAL_MEMSWAP_LIMIT
          and sample.get("nano_cpus") == EVAL_NANO_CPUS)
    print("[self-test] would-inject mem_limit=%s memswap_limit=%s nano_cpus=%s"
          % (EVAL_MEM_LIMIT, EVAL_MEMSWAP_LIMIT, EVAL_NANO_CPUS))
    print("[self-test] PASS — docker create limits will be injected" if ok else "[self-test] FAIL!")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return _self_test()

    # 1) 先打 patch（在 import swebench 之前）
    _patch_docker_create()

    # 2) 委托 swebench 的 run_evaluation —— 用 runpy 执行其 __main__ 块
    #    （swebench 5.0.2 的 __main__ 块用 argparse 解析 sys.argv[1:] 再调 main(**vars(args))，
    #     等价于 `python -m swebench.harness.run_evaluation`，但 patch 已先行生效）
    import runpy
    runpy.run_module("swebench.harness.run_evaluation", run_name="__main__", alter_sys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
