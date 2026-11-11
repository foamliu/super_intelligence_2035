#!/usr/bin/env python3
"""Test vLLM GPU generation for BaiZe 2B (NemotronH) @ 160k.
Purpose: Determine if generation degradation is a llama.cpp bug or model issue.
vLLM has native NemotronHForCausalLM support (vllm 0.14.1).

Usage (when GPU window available):
  # On .17 (A40, posttrain machine) or any GPU machine:
  export CUDA_VISIBLE_DEVICES=0  # use 1 GPU
  /nas_train/app.e0031982/miniforge3/envs/vllm/bin/python baize_vllm_gpu_gen_test.py

  # On .29 (during a brief GPU window, use leftover memory):
  export CUDA_VISIBLE_DEVICES=0
  /nas_train/app.e0031982/miniforge3/envs/vllm/bin/python baize_vllm_gpu_gen_test.py --gpu-mem-util 0.05

Expected outcome:
  If vLLM generates coherent text → llama.cpp SSM generation is buggy → switch to vLLM for generative evals
  If vLLM also collapses → model architecture/training issue → need more training or arch fix
"""
import argparse
import time
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu-mem-util", type=float, default=0.9,
                        help="gpu_memory_utilization for vLLM (lower if sharing GPU)")
    parser.add_argument("--model-path", type=str,
                        default="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000")
    parser.add_argument("--max-model-len", type=int, default=4096)
    args = parser.parse_args()

    from vllm import LLM, SamplingParams

    print(f"Loading model with vLLM (gpu_mem_util={args.gpu_mem_util})...", flush=True)
    t0 = time.time()
    llm = LLM(
        model=args.model_path,
        dtype="float16",
        gpu_memory_utilization=args.gpu_mem_util,
        max_model_len=args.max_model_len,
        enforce_eager=True,  # avoid CUDA graph overhead
        trust_remote_code=True,
    )
    print(f"Model loaded in {time.time()-t0:.1f}s", flush=True)

    tests = [
        "True or False: (True and False) or (True and True) =",
        "Question: What is 2 + 3? Answer:",
        "The capital of France is",
        "Q: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May? A:",
        "def fibonacci(n):\n    if n <= 1:\n        return n\n    return",
    ]

    sampling_params = SamplingParams(max_tokens=100, temperature=0, top_p=1.0, seed=1234)

    for prompt in tests:
        print(f"\n--- Test: {prompt[:80]} ---", flush=True)
        t1 = time.time()
        outputs = llm.generate([prompt], sampling_params)
        gen_text = outputs[0].outputs[0].text
        elapsed = time.time() - t1
        print(f"Generated ({elapsed:.1f}s): {gen_text[:300]}", flush=True)

    # Compare with llama.cpp output (known to degrade):
    # llama.cpp output for "True or False: ...": "111, the111111111..."
    # If vLLM produces "True" or coherent text → confirms llama.cpp bug

    print("\n=== vLLM GPU generation test complete ===", flush=True)
    print("\nComparison with llama.cpp (CPU):", flush=True)
    print("  llama.cpp: '111, the111111111...' (DEGRADED)", flush=True)
    print("  vLLM:      see results above", flush=True)
    print("  If vLLM output is coherent → switch generative evals to vLLM", flush=True)

if __name__ == "__main__":
    main()
