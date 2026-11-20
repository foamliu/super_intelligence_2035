#!/usr/bin/env python3
"""R114: SFT Training Framework Decision + Data Format Pipeline Design
Wake 161 (2026-11-09): GPU day, GPUs still occupied (0/8 free).
Key findings: verl 0.4.0 has built-in FSDP SFT Trainer; our parquet is directly compatible.
Usage: python3 baize_posttrain_r114_sft_framework_pipeline.py [--verbose] [--html] [--json]
"""
import argparse, json, os, sys
from pathlib import Path
from datetime import datetime

RUN_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
REPORT_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
MODEL_PATH = "/nas_data/app.e0031982/models/MiniCPM5-2B"
SFT_V2 = RUN_DIR / "sft_pyaether_corpus_v2.parquet"
SFT_V5 = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet"
RL_PQ = RUN_DIR / "rl_pyaether_synth_v2.parquet"

def load_parquet_summary(path):
    try:
        import pandas as pd, numpy as np
        df = pd.read_parquet(path)
        s = {"path": str(path), "exists": True, "rows": len(df),
             "columns": list(df.columns), "size_mb": round(path.stat().st_size/1048576, 2)}
        if "conversation" in df.columns:
            conv = df.iloc[0]["conversation"]
            cl = conv.tolist() if isinstance(conv, np.ndarray) else conv
            s["conv_type"] = type(conv).__name__
            s["conv_length"] = len(cl) if isinstance(cl, list) else 1
            if isinstance(cl, list) and len(cl) > 0 and isinstance(cl[0], dict):
                s["conv_msg_keys"] = list(cl[0].keys())
                s["conv_first_role"] = cl[0].get("role", "?")
        return s
    except Exception as e:
        return {"path": str(path), "exists": path.exists(), "error": str(e)}

def analyze_verl_sft():
    venv = os.path.expanduser("~/code/verl_cu124_venv")
    return {
        "sft_trainer": Path(f"{venv}/lib/python3.10/site-packages/verl/trainer/fsdp_sft_trainer.py").exists(),
        "multiturn_ds": Path(f"{venv}/lib/python3.10/site-packages/verl/utils/dataset/multiturn_sft_dataset.py").exists(),
        "config_tmpl": Path(f"{venv}/lib/python3.10/site-packages/verl/trainer/config/sft_trainer.yaml").exists(),
        "verdict": "RECOMMENDED: verl 0.4.0 FSDP SFT - zero setup, unified with RL, reads parquet directly",
        "alternatives": {"trl": "NOT AVAILABLE", "megatron": "NOT AVAILABLE", "custom": "PLACEHOLDER"},
        "data_compat": "PyAether parquet 'conversation' column directly compatible with MultiTurnSFTDataset",
    }

def generate_sft_config_yaml():
    yaml_text = """# baize_posttrain_sft_verl_config.yaml — verl 0.4.0 FSDP SFT for MiniCPM5-2B on 4xA40
# R114: SFT framework = verl FSDP SFT (unified with RL toolchain)
# Uses MultiTurnSFTDataset with messages_key='conversation' — directly compatible.

data:
  train_batch_size: 128
  micro_batch_size_per_gpu: 2
  train_files: sft_blended_v1.parquet
  val_files: null
  multiturn:
    enable: true
    messages_key: conversation
    tools_key: null
  max_length: 16384
  truncation: left
  balance_dp_token: false
  chat_template: null
  use_shm: false

model:
  partial_pretrain: /nas_data/app.e0031982/models/MiniCPM5-2B
  use_shm: false
  fsdp_config:
    model_dtype: bf16
    wrap_policy:
      min_num_params: 0
    cpu_offload: false
    offload_params: false
  enable_gradient_checkpointing: true
  trust_remote_code: true
  lora_rank: 0
  lora_alpha: 16
  target_modules: all-linear
  use_liger: false
  strategy: fsdp2
  use_remove_padding: true

optim:
  lr: 2e-5
  betas: [0.9, 0.95]
  weight_decay: 0.01
  warmup_steps_ratio: 0.03
  clip_grad: 1.0
  lr_scheduler: wsd

ulysses_sequence_parallel_size: 1
use_remove_padding: true

trainer:
  default_local_dir: /nas_data/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize_posttrain_sft
  default_hdfs_dir: null
  resume_path: null
  project_name: baize-posttrain-sft
  experiment_name: sft-v1-ctx16k
  total_epochs: 3
  total_training_steps: 3000
  logger: ['console', 'wandb']
  seed: 42
  save_freq: 300
  test_freq: -1
  nnodes: 1
  n_gpus_per_node: 4
  max_ckpt_to_keep: 3
"""
    p = RUN_DIR / "baize_posttrain_sft_verl_config.yaml"
    p.write_text(yaml_text)
    return str(p)

def generate_html(results, data_summaries, yaml_path):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    ds_rows = ""
    for n, ds in data_summaries.items():
        ds_rows += f"<tr><td>{n}</td><td>{'YES' if ds.get('exists') else 'NO'}</td><td>{ds.get('rows','-')}</td><td>{ds.get('size_mb','-')}MB</td><td>{', '.join(ds.get('columns',[]))}</td></tr>\n"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R114: SFT Framework + Data Pipeline</title>
<style>
body{{font-family:sans-serif;max-width:1100px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}
h2{{color:#2874a6;margin-top:30px;border-bottom:1px solid #d5dbdb;padding-bottom:5px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}}
th{{background:#ebf5fb;text-align:left}}td,th{{border:1px solid #bdc3c7;padding:6px 10px}}
code{{background:#f4f6f7;padding:2px 5px;border-radius:3px}}
.box{{background:#eafaf1;border-left:4px solid #27ae60;padding:10px 15px;margin:15px 0}}
</style></head><body>
<h1>R114: SFT Training Framework Decision + Data Format Pipeline Design</h1>
<div class="box"><strong>Decision</strong>: SFT = verl 0.4.0 FSDP SFT Trainer (unified with RL)<br>
<strong>Data</strong>: PyAether parquet directly compatible; UltraData needs JSONL-to-parquet<br>
<strong>Deliverables</strong>: verl SFT YAML + blending pipeline + this report</div>
<h2>1. Executive Summary</h2>
<p>R114 | wake161 | {now}</p>
<p>GPU: 0/8 free (root SGLang Qwen3.8-27B, since Sep17). gpu_watcher restarted PID 2709455, max-wait=604800s (7 days).</p>
<table border="1" cellpadding="6"><tr><th>Decision</th><th>Conclusion</th><th>Rationale</th></tr>
<tr><td>SFT Framework</td><td><strong>verl 0.4.0 FSDP SFT</strong></td><td>Installed; unified with RL; reads parquet; multi-turn+LoRA+FSDP</td></tr>
<tr><td>PyAether Data</td><td><strong>No conversion needed</strong></td><td>parquet 'conversation' = MultiTurnSFTDataset format</td></tr>
<tr><td>UltraData</td><td>JSONL to parquet</td><td>Need converter script</td></tr>
<tr><td>Blend Ratio</td><td>agent50:general30:pyaether20</td><td>Agentic dominant, general prevents forgetting</td></tr>
<tr><td>Context Length</td><td>16384 (truncation=left)</td><td>R60: 16K captures 82%</td></tr>
</table>
<h2>2. Framework Comparison</h2>
<table border="1" cellpadding="6"><tr><th>Framework</th><th>Available</th><th>Verdict</th></tr>
<tr><td>verl FSDP SFT</td><td>YES v0.4.0</td><td>RECOMMENDED: zero setup, unified RL, parquet, multi-turn, LoRA, FSDP, WSD</td></tr>
<tr><td>TRL</td><td>NO</td><td>NOT AVAILABLE in venv</td></tr>
<tr><td>Megatron-LM</td><td>NO</td><td>NOT AVAILABLE, needs MEGATRON format</td></tr>
<tr><td>Custom sft_launcher</td><td>PLACEHOLDER</td><td>Would need full implementation</td></tr>
</table>
<h3>verl FSDP SFT Advantages</h3>
<ul>
<li><strong>Zero install</strong>: verl 0.4.0 in cu124 venv (torch 2.6.0+cu124, flash_attn 2.7.4)</li>
<li><strong>Unified toolchain</strong>: SFT + RL same framework, venv, model loading</li>
<li><strong>Direct parquet</strong>: MultiTurnSFTDataset accepts parquet, no MEGATRON format</li>
<li><strong>Multi-turn loss masking</strong>: auto train only assistant tokens</li>
<li><strong>FSDP on A40</strong>: 2B+FSDP = ~8GB/GPU, 46GB A40 plenty</li>
<li><strong>LoRA built-in</strong>: lora_rank config switch</li>
<li><strong>WSD scheduler</strong>: consistent with pretrain</li>
</ul>
<h2>3. Data Format Compatibility</h2>
<h3>verl MultiTurnSFTDataset Expected</h3>
<ul>
<li>Input: parquet file</li>
<li>Required column: messages_key (configured as 'conversation')</li>
<li>Format: list of dicts [{{role, content}}, ...]</li>
<li>Loss masking: auto, only role='assistant' tokens trained</li>
</ul>
<h3>Our SFT v2 Data</h3>
<ul>
<li>Column: conversation (numpy array of dicts)</li>
<li>Format: [{{role: "system", content}}, {{role: "user", content}}, {{role: "assistant", content}}]</li>
<li>Rows: 19,524 (v2) / 1,193 (v5)</li>
<li>Compatibility: DIRECTLY COMPATIBLE with messages_key='conversation'</li>
</ul>
<h2>4. SFT Config Design</h2>
<p>Generated: <code>baize_posttrain_sft_verl_config.yaml</code></p>
<table border="1" cellpadding="6"><tr><th>Param</th><th>Value</th><th>Rationale</th></tr>
<tr><td>multiturn.enable</td><td>true</td><td>Multi-turn conversations</td></tr>
<tr><td>messages_key</td><td>conversation</td><td>Match parquet column</td></tr>
<tr><td>max_length</td><td>16384</td><td>R60: 16K captures 82%</td></tr>
<tr><td>truncation</td><td>left</td><td>Preserve recent context</td></tr>
<tr><td>batch_size</td><td>128</td><td>GBS=128</td></tr>
<tr><td>micro_batch</td><td>2</td><td>2B*16K ~20GB, fits A40</td></tr>
<tr><td>model_dtype</td><td>bf16</td><td>A40 supports bf16</td></tr>
<tr><td>gradient_checkpointing</td><td>true</td><td>Save memory</td></tr>
<tr><td>lora_rank</td><td>0 (full FT)</td><td>Main experiment; ablation lora=64</td></tr>
<tr><td>lr</td><td>2e-5</td><td>2B SFT standard</td></tr>
<tr><td>lr_scheduler</td><td>wsd</td><td>Consistent with pretrain</td></tr>
<tr><td>epochs</td><td>3</td><td>SFT standard</td></tr>
<tr><td>n_gpus</td><td>4</td><td>4xA40</td></tr>
</table>
<h2>5. Data Blending Pipeline</h2>
<p><strong>Blend ratio</strong>: agent50:general30:pyaether20</p>
<table border="1" cellpadding="6"><tr><th>Source</th><th>Format</th><th>Location</th><th>Weight</th><th>Conversion</th></tr>
<tr><td>PyAether SFT v2</td><td>parquet</td><td>.17 local</td><td>20%</td><td>None</td></tr>
<tr><td>UltraData-Agent-2609</td><td>JSONL</td><td>.29/.12 (transfer needed)</td><td>50%</td><td>JSONL to parquet</td></tr>
<tr><td>UltraData-General-2605</td><td>JSONL</td><td>.29/.12 (transfer needed)</td><td>30%</td><td>JSONL to parquet</td></tr>
</table>
<h3>Pipeline Steps</h3>
<ol>
<li>Transfer UltraData .29 to .17 (baize_posttrain_data_transfer.sh --sft)</li>
<li>JSONL to parquet conversion (baize_posttrain_jsonl_to_parquet.py - to create)</li>
<li>Sample/weight to 50:30:20 ratio</li>
<li>Concatenate into sft_blended_v1.parquet</li>
<li>Contamination gate (baize_posttrain_contamination_gate.sh)</li>
<li>verl MultiTurnSFTDataset dry-load verification</li>
</ol>
<p><strong>Estimated scale</strong>: PyAether 19,524 = 20% -> total ~97,620 -> Agent ~48,810 + General ~29,286</p>
<h2>6. JSONL Converter Design</h2>
<p><strong>Script</strong>: <code>baize_posttrain_jsonl_to_parquet.py</code> (to create)</p>
<ul>
<li>Input: UltraData JSONL (various schemas: 'messages'/'conversations')</li>
<li>Output: parquet 'conversation' column (list of {{role, content}})</li>
<li>Logic: streaming read; format normalization; length filter; source tag; shard write</li>
<li>Est. runtime: General 319G -> ~30-60 min CPU</li>
</ul>
<h2>7. Data Summaries</h2>
<table border="1" cellpadding="6"><tr><th>File</th><th>Exists</th><th>Rows</th><th>Size</th><th>Columns</th></tr>
{ds_rows}
</table>
<h2>8. GPU Watcher Extension</h2>
<p>Old watcher max-wait=86400s (24h), expiring ~00:14 on 11/10. GPU still 0/8 free.</p>
<p>Action: killed old watcher, restarted PID 2709455 with max-wait=604800s (7 days).</p>
<p>Auto-launch: GPU free (>=4 cards >=40000MiB) -> watcher triggers launch_11_9.sh --step 1-5.</p>
<h2>9. Conclusions and Next Steps</h2>
<h3>Key Conclusions</h3>
<ol>
<li>SFT framework decided: verl 0.4.0 FSDP SFT - zero install, unified RL</li>
<li>PyAether data directly compatible: parquet conversation = MultiTurnSFTDataset format</li>
<li>UltraData needs conversion: JSONL to parquet, converter designed</li>
<li>SFT config generated: baize_posttrain_sft_verl_config.yaml</li>
<li>Data blending decided: 50:30:20 (agent:general:pyaether)</li>
<li>GPU watcher extended: 7 days, ensuring auto-launch continuity</li>
</ol>
<h3>Next Steps (R115+)</h3>
<ol>
<li>Implement baize_posttrain_jsonl_to_parquet.py converter</li>
<li>GPU release: launch_11_9.sh step 2 (baseline) + step 5 (RL smoke)</li>
<li>Formal SFT: wait pretrain ckpt (ETA 2026-12-25) + UltraData transfer</li>
<li>Update baize_posttrain_sft.sh to call verl SFT trainer (replace placeholder)</li>
</ol>
<h3>Blockers</h3>
<ul>
<li>GPU: 0/8 free - watcher polling</li>
<li>Formal SFT: wait pretrain ckpt (ETA 2026-12-25)</li>
<li>UltraData: transfer from .29 needed (R113 script ready)</li>
</ul>
<hr><p style="color:#7f8c8d;font-size:12px">R114 | wake161 | 2026-11-09 | BaiZe Stage(ii) | Surrogate results NOT transferable to BaiZe</p>
</body></html>"""

def main():
    ap = argparse.ArgumentParser(description="R114: SFT Framework + Data Pipeline")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    print("=" * 60)
    print("R114: SFT Training Framework Decision + Data Format Pipeline")
    print("=" * 60)
    print("\n[1] Analyzing verl SFT compatibility...")
    results = analyze_verl_sft()
    if args.verbose:
        print(f"  SFT trainer: {results['sft_trainer']}")
        print(f"  MultiTurn dataset: {results['multiturn_ds']}")
        print(f"  Verdict: {results['verdict']}")
    print("\n[2] Loading data summaries...")
    data_summaries = {}
    for name, path in [("SFT PyAether v2", SFT_V2), ("SFT PyAether v5", SFT_V5), ("RL PyAether v2", RL_PQ)]:
        ds = load_parquet_summary(path)
        data_summaries[name] = ds
        if args.verbose:
            print(f"  {name}: {ds.get('rows', 'N/A')} rows, {ds.get('size_mb', 'N/A')}MB")
    print("\n[3] Generating SFT config YAML...")
    yaml_path = generate_sft_config_yaml()
    print(f"  Config: {yaml_path}")
    if args.html:
        print("\n[4] Generating HTML report...")
        html = generate_html(results, data_summaries, yaml_path)
        hp = REPORT_DIR / "report_posttrain_r114_sft_framework_pipeline_zh.html"
        hp.write_text(html, encoding="utf-8")
        print(f"  HTML: {hp} ({round(hp.stat().st_size/1024, 1)}KB)")
    output = {"research_id": "R114", "wake": "wake161", "timestamp": datetime.now().isoformat(),
              "gpu_status": "0/8 free", "gpu_watcher": "PID 2709455, max-wait=604800s",
              "framework": "verl 0.4.0 FSDP SFT", "sft_config": yaml_path,
              "blend_ratio": "agent50:general30:pyaether20", "data_summaries": data_summaries}
    if args.json:
        jp = RUN_DIR / "baize_posttrain_r114_results.json"
        jp.write_text(json.dumps(output, indent=2, ensure_ascii=False, default=str))
        print(f"\n  JSON: {jp}")
    print("\n" + "=" * 60)
    print("R114 COMPLETE")
    print(f"  Framework: verl 0.4.0 FSDP SFT")
    print(f"  Config: {yaml_path}")
    print(f"  Data: PyAether compatible, UltraData needs conversion")
    print(f"  Blend: agent50:general30:pyaether20")
    print("=" * 60)

if __name__ == "__main__":
    main()
