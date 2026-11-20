#!/usr/bin/env python3
"""NCCL all_reduce micro-benchmark for BaiZe pretrain speedup investigation.

Usage (2-GPU on GPU0-1):
  CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node=2 nccl_bench.py \
      --sizes 1M,10M,100M,500M,1G --iters 20 --warmup 5

Measures algbw (algorithm bandwidth) and busbw (bus bandwidth) for all_reduce.
Captures NCCL transport info when run with NCCL_DEBUG=INFO.
"""
import argparse
import os
import sys
import time
import json
import torch
import torch.distributed as dist


def parse_size(s):
    """Parse size strings like 1M, 100M, 1G."""
    s = s.strip().upper()
    if s.endswith('G'):
        return int(float(s[:-1]) * 1024 * 1024 * 1024)
    elif s.endswith('M'):
        return int(float(s[:-1]) * 1024 * 1024)
    elif s.endswith('K'):
        return int(float(s[:-1]) * 1024)
    return int(s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=str, default='1M,10M,100M,500M,1G',
                        help='Comma-separated message sizes (e.g. 1M,100M,1G)')
    parser.add_argument('--iters', type=int, default=20, help='Iterations per size')
    parser.add_argument('--warmup', type=int, default=5, help='Warmup iterations')
    parser.add_argument('--output', type=str, default=None, help='Output JSON path')
    args = parser.parse_args()

    # Init process group
    dist.init_process_group(backend='nccl')
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    device = torch.device(f'cuda:{rank}')
    torch.cuda.set_device(device)

    sizes = [parse_size(s) for s in args.sizes.split(',')]
    results = []

    if rank == 0:
        print(f"NCCL all_reduce benchmark: world_size={world_size}, "
              f"iters={args.iters}, warmup={args.warmup}")
        print(f"{'Size (MB)':>12} {'algbw (GB/s)':>14} {'busbw (GB/s)':>14} "
              f"{'latency (us)':>14}")
        print("-" * 60)

    for size_bytes in sizes:
        n_elems = size_bytes // 4  # float32 = 4 bytes
        if n_elems == 0:
            continue
        tensor = torch.randn(n_elems, dtype=torch.float32, device=device)

        # Warmup
        for _ in range(args.warmup):
            dist.all_reduce(tensor, op=dist.ReduceOp.SUM, async_op=False)
        torch.cuda.synchronize()

        # Timed run
        start_events = [torch.cuda.Event(enable_timing=True) for _ in range(args.iters)]
        end_events = [torch.cuda.Event(enable_timing=True) for _ in range(args.iters)]

        for i in range(args.iters):
            start_events[i].record()
            dist.all_reduce(tensor, op=dist.ReduceOp.SUM, async_op=False)
            end_events[i].record()
        torch.cuda.synchronize()

        # Compute median latency
        times_us = [s.elapsed_time(e) * 1000 for s, e in zip(start_events, end_events)]
        times_us.sort()
        median_us = times_us[len(times_us) // 2]
        min_us = times_us[0]

        # Bandwidth
        size_gb = size_bytes / 1e9
        algbw = size_gb / (median_us / 1e6)  # GB/s
        # Bus bandwidth factor for all_reduce on ring: (n-1)/n for n GPUs
        bus_factor = (world_size - 1) / world_size
        busbw = algbw * bus_factor

        if rank == 0:
            print(f"{size_bytes/1024/1024:>12.1f} {algbw:>14.2f} {busbw:>14.2f} "
                  f"{median_us:>14.1f}")

        results.append({
            'size_bytes': size_bytes,
            'size_mb': size_bytes / 1024 / 1024,
            'iters': args.iters,
            'median_latency_us': round(median_us, 1),
            'min_latency_us': round(min_us, 1),
            'algbw_gbs': round(algbw, 2),
            'busbw_gbs': round(busbw, 2),
            'world_size': world_size,
        })

    # Gather results on rank 0
    if rank == 0 and args.output:
        env_vars = {k: v for k, v in os.environ.items()
                    if k.startswith('NCCL_') or k.startswith('CUDA_')}
        out = {
            'world_size': world_size,
            'nccl_version': list(torch.cuda.nccl.version()),
            'env_overrides': env_vars,
            'results': results,
        }
        with open(args.output, 'w') as f:
            json.dump(out, f, indent=2)
        print(f"\nResults saved to {args.output}")

    dist.barrier()
    dist.destroy_process_group()


if __name__ == '__main__':
    main()
