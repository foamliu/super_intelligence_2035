#!/usr/bin/env python3
"""setup_shards.py — 把现有 30 条 case + 35 条 ledger 按 domain 拆成 4 个 shard

shard 分片：
  A (digital_front):    digital, verification, pnr_signoff, eda_other
  B (spice_char):       spice_sim, characterization
  C (physical_layout):  physical_verify, layout_virtuoso, layout_aether, pg_layout
  D (netlist_wave):     schematic_netlist, waveform, analog_context

每个 shard 产出：
  benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_<X>.jsonl   — 该 shard 的 case
  designflow/trace_ledger_<X>.tsv                                 — 该 shard 的台账
  MEMORY_DESIGNFLOW_<X>.md                                        — 该 shard 的心跳
  BAIZE_DESIGNFLOW_BENCH_TASK_<X>.md                              — 该 shard 的 TASK（主 TASK + shard 配置块）
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(HERE, "..")  # benchmark/
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
JSONL_DIR = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
MAIN_JSONL = os.path.join(JSONL_DIR, "EDA-Eval-DesignFlow.jsonl")

SHARDS = {
    "A": {"name": "digital_front",   "domains": {"digital", "verification", "pnr_signoff", "eda_other"}},
    "B": {"name": "spice_char",      "domains": {"spice_sim", "characterization"}},
    "C": {"name": "physical_layout", "domains": {"physical_verify", "layout_virtuoso", "layout_aether", "pg_layout"}},
    "D": {"name": "netlist_wave",    "domains": {"schematic_netlist", "waveform", "analog_context"}},
}

# domain → shard 反查（含未分类 domain 的兜底分配）
DOMAIN_FALLBACK = {
    "skipper": "C",  # physical_verify 类
}


def shard_of(domain):
    if domain in DOMAIN_FALLBACK:
        return DOMAIN_FALLBACK[domain]
    for sid, info in SHARDS.items():
        if domain in info["domains"]:
            return sid
    return "D"  # 兜底放 D


def split_jsonl():
    """拆主 jsonl → 4 个 shard jsonl"""
    shard_cases = {s: [] for s in SHARDS}
    unassigned = []
    with open(MAIN_JSONL, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            dom = d.get("metadata", {}).get("domain", "")
            sid = shard_of(dom)
            shard_cases[sid].append(line)
            if sid not in SHARDS:
                unassigned.append((d["task_id"], dom))

    for sid, lines in shard_cases.items():
        path = os.path.join(JSONL_DIR, "EDA-Eval-DesignFlow_%s.jsonl" % sid)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("  shard %s (%s): %d cases -> %s" % (sid, SHARDS[sid]["name"], len(lines), path))

    if unassigned:
        print("  ⚠️ unassigned:", unassigned)


def split_ledger():
    """拆 trace_ledger.tsv → 4 个 shard ledger"""
    ledger = os.path.join(HERE, "trace_ledger.tsv")
    if not os.path.exists(ledger):
        print("  ledger not found: %s" % ledger)
        return
    shard_rows = {s: [] for s in SHARDS}
    with open(ledger, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if parts[0] == "session_file":
                continue  # header
            domain = parts[4] if len(parts) > 4 else ""
            sid = shard_of(domain)
            shard_rows[sid].append(line)

    for sid, rows in shard_rows.items():
        path = os.path.join(HERE, "trace_ledger_%s.tsv" % sid)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(rows)
        print("  shard %s ledger: %d rows -> %s" % (sid, len(rows), path))


def create_memory_files():
    """为每个 shard 创建 MEMORY 文件"""
    template = """WAITING: 0
SHARD: {sid} ({name})
DOMAINS: {domains}

- **PHASE**: 🆕 shard {sid} 启动，从主 loop 分片而来。负责 domain: {domains}
- 每轮做 1 条 case：trace_ledger.py --shard {sid} next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_{sid}.jsonl → 日报
- **本轮任务**：trace_ledger.py --shard {sid} next 取候选，建第一条 case
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard {sid} stats
- 🎯 通过率: 0/0（刚启动）
"""
    for sid, info in SHARDS.items():
        path = os.path.join(BENCH, "MEMORY_DESIGNFLOW_%s.md" % sid)
        doms = ", ".join(sorted(info["domains"]))
        with open(path, "w", encoding="utf-8") as f:
            f.write(template.format(sid=sid, name=info["name"], domains=doms))
        print("  shard %s MEMORY -> %s" % (sid, path))


def create_task_files():
    """为每个 shard 创建 TASK 文件 = 主 TASK + shard 配置块"""
    main_task = os.path.join(BENCH, "BAIZE_DESIGNFLOW_BENCH_TASK.md")
    if not os.path.exists(main_task):
        print("  main TASK not found: %s" % main_task)
        return
    with open(main_task, encoding="utf-8") as f:
        base = f.read()

    for sid, info in SHARDS.items():
        shard_block = """

## 🔀 SHARD 配置（本 shard 专用 · 覆盖主 TASK 中的通用描述）

**你是 shard %s（%s）**。只负责以下 domain：%s

### 你的文件（不要碰别的 shard 的文件）
- **jsonl**：`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_%s.jsonl`（只往这个文件追加 case）
- **台账**：`designflow/trace_ledger_%s.tsv`（通过 `trace_ledger.py --shard %s` 自动使用）
- **心跳**：`MEMORY_DESIGNFLOW_%s.md`（只写这个文件）
- **日记忆**：`daily-memories-designflow/daily_%s_*.md`

### 选 trace 命令（带 shard 过滤）
```bash
python3 designflow/trace_ledger.py --shard %s next --n 5
python3 designflow/trace_ledger.py --shard %s claim --session <s> --user <u> --host <h> --match <m> --domain <d>
python3 designflow/trace_ledger.py --shard %s mark --session <s> --status case --case-id <id>
```

### 合并
- **不要碰主 jsonl**（`EDA-Eval-DesignFlow.jsonl`），它由 merge 脚本自动合并 4 个 shard 生成
- 你的 case 只追加到 `EDA-Eval-DesignFlow_%s.jsonl`
- merge 脚本每 30 分钟自动合并 4 片 → 主 jsonl + regen 日报

### 收尾提交（只提交自己 shard 的文件）
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_%s.md \\
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_%s.tsv \\
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads \\
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow/daily_%s_*
git commit -m "designflow shard %s #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_%s.jsonl \\
           benchmarks/EDA-Eval-DesignFlow/assets benchmarks/EDA-Eval-DesignFlow/reference
git commit -m "designflow shard %s #<轮次>: <一句话>" && git push origin master
```
""" % (sid, info["name"], ", ".join(sorted(info["domains"])),
       sid, sid, sid, sid, sid,
       sid, sid, sid,
       sid,
       sid, sid, sid, sid, sid, sid)

        path = os.path.join(BENCH, "BAIZE_DESIGNFLOW_BENCH_TASK_%s.md" % sid)
        with open(path, "w", encoding="utf-8") as f:
            f.write(base)
            f.write(shard_block)
        print("  shard %s TASK -> %s" % (sid, path))


def main():
    print("=== 1. 拆主 jsonl → 4 shard jsonl ===")
    split_jsonl()
    print("\n=== 2. 拆 trace_ledger.tsv → 4 shard ledger ===")
    split_ledger()
    print("\n=== 3. 创建 4 个 MEMORY 文件 ===")
    create_memory_files()
    print("\n=== 4. 创建 4 个 shard TASK 文件 ===")
    create_task_files()
    print("\n✅ 分片完成。下一步：创建 merge 脚本 + 4 个 shard loop 脚本")


if __name__ == "__main__":
    main()
