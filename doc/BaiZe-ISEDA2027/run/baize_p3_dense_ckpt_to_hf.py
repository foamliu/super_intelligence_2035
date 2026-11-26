#!/usr/bin/env python3
# P-9.11: Convert p3_dense mcore distcp (dense GPT 42L, 2.512B) to HF Llama format.
# Arch: hidden=2048 ffn=6144 16Q/2KV SwiGLU silu no-bias pre-norm vocab=129408
import argparse, json, os, shutil
os.environ.setdefault("MASTER_ADDR","127.0.0.1")
os.environ.setdefault("MASTER_PORT","29503")
import torch
from safetensors.torch import save_file

HIDDEN=2048; FFN=6144; NL=42; NH=16; NKV=2; HD=128; KVD=NKV*HD; VOCAB=129408; EPS=1e-6

def build_config():
    return {"model_type":"llama","architectures":["LlamaForCausalLM"],
        "vocab_size":VOCAB,"hidden_size":HIDDEN,"intermediate_size":FFN,
        "num_hidden_layers":NL,"num_attention_heads":NH,"num_key_value_heads":NKV,
        "head_dim":HD,"hidden_act":"silu","max_position_embeddings":4096,
        "rms_norm_eps":EPS,"attention_bias":False,"mlp_bias":False,
        "tie_word_embeddings":False,"torch_dtype":"bfloat16",
        "bos_token_id":1,"eos_token_id":2,"pad_token_id":0,"use_cache":True,
        "rope_theta":10000.0}

def convert(sd):
    # p3_dense uses batched keys: decoder.layers.self_attention.linear_qkv.weight
    # has shape [42, 2560, 2048] (all layers stacked on dim 0)
    hf={}
    def put(n,t): assert n not in hf; hf[n]=t.contiguous()
    put("model.embed_tokens.weight",sd["embedding.word_embeddings.weight"])
    fn_key="decoder.final_layernorm.weight" if "decoder.final_layernorm.weight" in sd else "decoder.final_norm.weight"
    put("model.norm.weight",sd[fn_key])
    if "output_layer.weight" in sd: put("lm_head.weight",sd["output_layer.weight"])
    else: put("lm_head.weight",sd["embedding.word_embeddings.weight"].clone())
    qkv_all=sd["decoder.layers.self_attention.linear_qkv.weight"]
    qkv_ln=sd["decoder.layers.self_attention.linear_qkv.layer_norm_weight"]
    proj_all=sd["decoder.layers.self_attention.linear_proj.weight"]
    fc1_all=sd["decoder.layers.mlp.linear_fc1.weight"]
    fc1_ln=sd["decoder.layers.mlp.linear_fc1.layer_norm_weight"]
    fc2_all=sd["decoder.layers.mlp.linear_fc2.weight"]
    for i in range(NL):
        hp=f"model.layers.{i}"
        put(f"{hp}.input_layernorm.weight",qkv_ln[i])
        qkv=qkv_all[i]
        q,k,v=qkv.split([HIDDEN,KVD,KVD],dim=0)
        put(f"{hp}.self_attn.q_proj.weight",q)
        put(f"{hp}.self_attn.k_proj.weight",k)
        put(f"{hp}.self_attn.v_proj.weight",v)
        put(f"{hp}.self_attn.o_proj.weight",proj_all[i])
        put(f"{hp}.post_attention_layernorm.weight",fc1_ln[i])
        fc1=fc1_all[i]
        gate,up=fc1.split([FFN,FFN],dim=0)
        put(f"{hp}.mlp.gate_proj.weight",gate)
        put(f"{hp}.mlp.up_proj.weight",up)
        put(f"{hp}.mlp.down_proj.weight",fc2_all[i])
    return hf

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ckpt",required=True)
    ap.add_argument("--tokenizer",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if not torch.distributed.is_initialized():
        torch.distributed.init_process_group(backend="gloo",rank=0,world_size=1)
    from megatron.core.dist_checkpointing.serialization import load_plain_tensors
    sd=load_plain_tensors(a.ckpt)
    np=sum(v.numel() for v in sd.values() if hasattr(v,"numel"))
    print(f"[load] {len(sd)} keys, {np/1e9:.3f}B params")
    hf=convert(sd)
    print(f"[map] {len(hf)} HF keys")
    os.makedirs(a.out,exist_ok=True)
    with open(os.path.join(a.out,"config.json"),"w") as f:
        json.dump(build_config(),f,indent=2)
    save_file({k:v.to(torch.bfloat16) for k,v in hf.items()},
              os.path.join(a.out,"model.safetensors"))
    for fn in ("tokenizer.json","tokenizer_config.json","special_tokens_map.json"):
        src=os.path.join(a.tokenizer,fn)
        if os.path.exists(src): shutil.copy2(src,os.path.join(a.out,fn))
    print(f"[done] wrote HF model to {a.out}")

if __name__=="__main__": main()

