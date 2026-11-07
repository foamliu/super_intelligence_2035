#!/usr/bin/env python3
"""S2-fallback smoke: load Qwen3.5-2B with transformers 5.x + peft LoRA on CPU,
do 1 forward+backward step. Proves the fallback path is viable (wake#853).

Context: LLaMA-Factory 0.9.3 forces transformers 4.52.4 which cannot load
`qwen3_5` architecture (KeyError). Fallback = transformers 5.20.2 + peft direct
(proven pattern from wake#741, 69.7M LoRA adapter on text backbone).
"""
import os, sys, time, json, math, traceback
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("OMP_NUM_THREADS", "16")
os.environ.setdefault("MKL_NUM_THREADS", "16")

MODEL = "/nas_train/app.e0031982/datasets/baize-vision/out/hf_cache_qwen35/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc"
OUT = "/tmp/qwen35_fallback_smoke.json"

result = {"stage": "s2_fallback", "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
try:
    import torch, transformers, peft
    result["versions"] = {"torch": torch.__version__, "transformers": transformers.__version__, "peft": peft.__version__}
    print(f"[versions] torch={torch.__version__} transformers={transformers.__version__} peft={peft.__version__}", flush=True)

    t0 = time.time()
    from transformers import AutoConfig, AutoTokenizer
    cfg = AutoConfig.from_pretrained(MODEL)
    result["model_type"] = cfg.model_type
    result["architectures"] = getattr(cfg, "architectures", None)
    print(f"[config] model_type={cfg.model_type} arch={result['architectures']} ({time.time()-t0:.1f}s)", flush=True)

    tok = AutoTokenizer.from_pretrained(MODEL)
    print(f"[tokenizer] vocab={tok.vocab_size} loaded ({time.time()-t0:.1f}s)", flush=True)

    # Load full model on CPU in float32 (CPU; bf16 may not be fastest on CPU).
    t1 = time.time()
    from transformers import AutoModelForCausalLM
    # Qwen3.5 is a VLM (ConditionalGeneration). Try CausalLM first (text tower);
    # if that fails, try the full conditional-generation model with text-only input.
    model = None
    load_cls = None
    for cls_name, cls in [("AutoModelForCausalLM", AutoModelForCausalLM)]:
        try:
            model = cls.from_pretrained(MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
            load_cls = cls_name
            print(f"[model] loaded via {cls_name} ({time.time()-t1:.1f}s)", flush=True)
            break
        except Exception as e:
            print(f"[model] {cls_name} failed: {e!r}", flush=True)
    if model is None:
        from transformers import AutoModel
        model = AutoModel.from_pretrained(MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True, trust_remote_code=True)
        load_cls = "AutoModel"
        print(f"[model] loaded via AutoModel ({time.time()-t1:.1f}s)", flush=True)
    result["load_class"] = load_cls
    result["load_time_s"] = round(time.time()-t1, 1)
    n_params = sum(p.numel() for p in model.parameters())
    result["n_params"] = n_params
    print(f"[model] params={n_params/1e9:.3f}B", flush=True)

    # Apply LoRA
    from peft import LoraConfig, get_peft_model
    # Try language-model linear layers; fall back to all-linear.
    targets = ["q_proj", "k_proj", "v_proj", "o_proj"]
    try:
        lc = LoraConfig(r=8, lora_alpha=16, target_modules=targets, lora_dropout=0.0, task_type="CAUSAL_LM")
        pm = get_peft_model(model, lc)
    except Exception:
        lc = LoraConfig(r=8, lora_alpha=16, target_modules="all-linear", lora_dropout=0.0)
        pm = get_peft_model(model, lc)
    tp = sum(p.numel() for p in pm.parameters() if p.requires_grad)
    result["lora_trainable_params"] = tp
    print(f"[lora] trainable={tp/1e6:.2f}M", flush=True)

    # 1 training step
    t2 = time.time()
    pm.train()
    opt = torch.optim.AdamW([p for p in pm.parameters() if p.requires_grad], lr=5e-5)
    prompt = "你是一个波形分析助手。给定方波周期 T=1.0e-6 秒，回答其频率。"
    target = "该方波频率为 1.0e6 Hz。"
    ids = tok(prompt + target, return_tensors="pt")
    labels = ids["input_ids"].clone()
    out = pm(input_ids=ids["input_ids"], attention_mask=ids.get("attention_mask"), labels=labels)
    loss0 = float(out.loss)
    out.loss.backward()
    opt.step()
    opt.zero_grad()
    # second step to see trend
    out2 = pm(input_ids=ids["input_ids"], attention_mask=ids.get("attention_mask"), labels=labels)
    loss1 = float(out2.loss)
    result["step0_loss"] = loss0
    result["step1_loss"] = loss1
    result["loss_finite"] = all(math.isfinite(l) for l in (loss0, loss1))
    result["step_time_s"] = round(time.time()-t2, 1)
    print(f"[step] loss0={loss0:.4f} loss1={loss1:.4f} finite={result['loss_finite']} ({result['step_time_s']}s)", flush=True)
    result["verdict"] = "FALLBACK_VIABLE" if result["loss_finite"] else "LOSS_NOT_FINITE"
except Exception as e:
    result["verdict"] = "FALLBACK_FAILED"
    result["error"] = repr(e)
    result["traceback"] = traceback.format_exc()[-2000:]
    print(f"[FAIL] {e!r}", flush=True)
    traceback.print_exc()

with open(OUT, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\nRESULT -> {OUT}\n{json.dumps(result, ensure_ascii=False, indent=2)}", flush=True)
