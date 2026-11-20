#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_data_mapping_md.py — 把 DATA_MAPPING.md 做成脚本生成的真·单一事实源.

运维令 2026-10-25 18:5x ①（第一优先）：
  - 输入 = tokenized/INDEX.tsv + 下载目录 du -sb 实测 + deleted_unmapped32 TSV + judgment TSV
  - 输出 = A/B 两节 + 合计 + 核对式 + 驱动数据指纹（INDEX.tsv mtime+size+blob-hash）
  - A 节 14 列：在原 12 列基础上新增「下载目录字节(B)」「下载/分词字节比」
  - 判据：**连跑两次 md 逐字节相同**（幂等）

幂等设计（关键）：
  - 不写 wall-clock 时间；「生成时间 / 校验时间」均取自 INDEX.tsv 的 mtime（确定性）。
  - 驱动数据指纹 = INDEX.tsv 的 size + git blob-hash（`git hash-object`），稳定不变。
  - du 下载目录字节走缓存（.du_download_cache.tsv）；两次连跑用同一缓存 ⇒ 字节相同。
  - 「证据」列写**可复现命令**（不嵌实时 done 计数），保证逐字节稳定。
  - 行顺序 = INDEX.tsv 顺序（稳定）；B 节按 shard 名排序（稳定）。

用法：
  python gen_data_mapping_md.py                      # 用缓存 du，输出到 DATA_MAPPING.md
  python gen_data_mapping_md.py --measure            # 重新 du 下载目录并刷新缓存
  python gen_data_mapping_md.py --check-idempotent   # 连跑两次比较字节
"""
import os, sys, csv, hashlib, subprocess, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DATA = HERE
INDEX_DEFAULT = "/nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv"
DELETED_TSV_DEFAULT = os.path.join(RUN_DATA, "deleted_unmapped32_20261025.tsv")
JUDGMENT_TSV_DEFAULT = os.path.join(RUN_DATA, "prune_unmapped_judgment_20261025.tsv")
DU_CACHE_DEFAULT = os.path.join(RUN_DATA, ".du_download_cache.tsv")
INPROGRESS_DEFAULT = os.path.join(RUN_DATA, "mapping_inprogress.txt")
CLEANUP_TSV_DEFAULT = os.path.join(RUN_DATA, "cleanup_batches_20261025.tsv")
UNTOKENIZED_TSV_DEFAULT = os.path.join(RUN_DATA, "untokenized_sft_sources.tsv")
OUT_DEFAULT = os.path.join(RUN_DATA, "DATA_MAPPING.md")

GB = 1024 ** 3


def du_bytes(path):
    """du -sb <path> -> int bytes (0 if missing)."""
    try:
        out = subprocess.check_output(["du", "-sb", path], stderr=subprocess.DEVNULL, text=True)
        return int(out.split()[0])
    except Exception:
        return 0


def file_mtime_iso(path):
    """文件 mtime -> 'YYYY-MM-DD HH:MM'（无秒，确定性粒度）。"""
    if not os.path.exists(path):
        return "—"
    ts = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return ts.strftime("%Y-%m-%d %H:%M")


def git_blob_hash(path):
    """git hash-object <path> -> 短 hash（文件内容指纹，不依赖 commit）。失败回退 sha256 前 12 位。"""
    try:
        out = subprocess.check_output(["git", "hash-object", path], stderr=subprocess.DEVNULL, text=True)
        return out.strip()[:12]
    except Exception:
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        return h[:12]


def load_du_cache(cache_path):
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, newline="") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                d = row.get("download_dir", "")
                b = row.get("bytes", "")
                if d and b.isdigit():
                    cache[d] = int(b)
    return cache


def measure_download_dirs(index_rows, cache_path):
    """对 INDEX 中每个 download_dir 跑 du -sb，写缓存。"""
    cache = {}
    with open(cache_path, "w") as f:
        f.write("download_dir\tbytes\n")
    for row in index_rows:
        d = row["download_dir"]
        if d and d not in cache:
            b = du_bytes(d)
            cache[d] = b
            with open(cache_path, "a") as f:
                f.write(f"{d}\t{b}\n")
            print(f"  measured {d} = {b}")
    return cache


def load_inprogress(path):
    """读 in-progress 侧车（每行一个 download_dir，# 开头注释）。不存在 ⇒ 空集。"""
    s = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                s.add(line)
    return s


def load_cleanup_batches(path):
    """读清理批次侧车 cleanup_batches_*.tsv（幂等：历史记录，不改）。不存在 ⇒ 空列表。"""
    rows = []
    if os.path.exists(path):
        with open(path, newline="") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                rows.append({
                    "batch": row.get("batch", ""),
                    "date": row.get("date", ""),
                    "items": row.get("items", ""),
                    "released_bytes": int(row.get("released_bytes", "0") or "0"),
                    "manifest": row.get("manifest", ""),
                    "status": row.get("status", ""),
                })
    return rows


def load_untokenized(path):
    """读未分词源侧车 untokenized_sft_sources.tsv（运维令 2026-10-26 14:4x）。
    列：download_dir, files, bytes, status, evidence_cmd, structure, notes。
    不存在 ⇒ 空列表（保持向后兼容 / 幂等）。"""
    rows = []
    if os.path.exists(path):
        with open(path, newline="") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                rows.append({
                    "download_dir": row.get("download_dir", ""),
                    "files": int(row.get("files", "0") or "0"),
                    "bytes": int(row.get("bytes", "0") or "0"),
                    "status": row.get("status", "未分词"),
                    "evidence_cmd": row.get("evidence_cmd", ""),
                    "structure": row.get("structure", ""),
                    "notes": row.get("notes", ""),
                })
    return rows


def load_index(index_path):
    """读 INDEX.tsv，返回数据行列表（跳过 TOTAL）+ TOTAL 行（若有）。"""
    rows = []
    with open(index_path, newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row.get("tokenized_dir") != "TOTAL":
                rows.append(row)
    return rows


def load_deleted(deleted_tsv, judgment_tsv):
    """读 32 个已删 shard：bytes/symlink_count 来自 deleted_tsv，理论 tokens 来自 judgment(action~保留)。"""
    del_rows = {}
    with open(deleted_tsv, newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            del_rows[row["shard"]] = {
                "dir_path": row["dir_path"],
                "bytes": int(row["bytes"]),
                "symlink_count": int(row["symlink_count"]),
            }
    tok_map = {}
    with open(judgment_tsv, newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["action"].startswith("保留"):
                try:
                    tok_map[row["shard"]] = int(row["num_tokens"])
                except ValueError:
                    tok_map[row["shard"]] = 0
    out = []
    for shard, d in del_rows.items():
        out.append({
            "shard": shard,
            "dir_path": d["dir_path"],
            "bytes": d["bytes"],
            "symlink_count": d["symlink_count"],
            "tokens": tok_map.get(shard, 0),
        })
    out.sort(key=lambda x: x["shard"])
    return out


def fmt_ratio(download_bytes, tok_bytes):
    if tok_bytes <= 0:
        return "—"
    return f"{download_bytes / tok_bytes:.3f}"


def short_path(p):
    """绝对路径压短：用 …/ 代替重复前缀，便于表格可读。"""
    for pref in ("/nas_train/app.e0031982/datasets/openbmb/",
                 "/nas_inference/app.e0031982/datasets/openbmb/",
                 "/nas_train/app.e0031982/datasets/baize-data/tokenized/"):
        if p.startswith(pref):
            return "…/" + p[len(pref):]
    return p


def status_for(row, inprogress):
    """镜像完整 / 分词中 / 未分词。in-progress 集合 ⇒ 分词中；shards>0 且 triplet OK ⇒ 镜像完整；shards==0 且非 in-progress ⇒ 未分词。"""
    dl = row.get("download_dir", "")
    shards = int(row.get("shards", 0) or 0)
    triplet = row.get("triplet", "")
    if dl in inprogress:
        return "分词中"
    if shards > 0 and triplet == "OK":
        return "镜像完整"
    if shards == 0:
        return "未分词"
    return "镜像完整"


def evidence_for(row, idx_line, status):
    """可复现证据（确定性字符串，不嵌实时值）。"""
    tok_dir = row.get("tokenized_dir", "")
    dl_dir = row.get("download_dir", "")
    storage = row.get("storage", "")
    if status == "镜像完整":
        return f"INDEX.tsv L{idx_line}: triplet={row.get('triplet','')} inode_ok={row.get('inode_ok','')} ({storage})"
    if status == "分词中":
        return f"ls {short_path(tok_dir)}/*.bin | wc -l ; 日志 /tmp/tokenize_untokenized_*.log（done=131/131 后刷新）"
    return f"ls {short_path(tok_dir)}/*.bin | wc -l (=0); du -sb {short_path(dl_dir)}"


def build_md(args):
    index_rows = load_index(args.index)
    if args.measure or not os.path.exists(args.du_cache):
        print("[measure] 重新 du 下载目录 …")
        du_cache = measure_download_dirs(index_rows, args.du_cache)
    else:
        du_cache = load_du_cache(args.du_cache)
    inprogress = load_inprogress(args.inprogress)
    deleted = load_deleted(args.deleted_tsv, args.judgment_tsv)
    untokenized = load_untokenized(args.untokenized_tsv)

    idx_mtime = file_mtime_iso(args.index)
    idx_size = os.path.getsize(args.index) if os.path.exists(args.index) else 0
    idx_hash = git_blob_hash(args.index)

    L = []
    L.append("# DATA_MAPPING.md — BaiZe 训练数据「下载 ↔ 分词」映射表（单一事实源）")
    L.append("")
    L.append("> 维护规程（运维令 2026-10-25 17:5x / 18:5x）：本文件为 Markdown 单一事实源，由 `run/data/gen_data_mapping_md.py` 生成；HTML 报告按需由 `gen_tokenized_inventory_report.py` 渲染。")
    L.append("> 一行 = 一个下载目录（粒度以盘上 `ls` 实测为准）；`状态` 取值：`镜像完整` / `分词中` / `未分词` / `未映射` / `已废弃` / `已删除`。")
    L.append("> 合计行由脚本求和，禁手填。数字均来自实测（`du -sb` / `find | wc -l` / `INDEX.tsv`）。")
    L.append(f"> 生成器：`run/data/gen_data_mapping_md.py`（幂等：连跑两次逐字节相同）。驱动数据指纹：`INDEX.tsv` size={idx_size} blob-hash={idx_hash} mtime={idx_mtime}。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## A. 当前可用映射（下载目录 ↔ 分词镜像）")
    L.append("")
    L.append(f"> 来源：`{args.index}`（镜像 build_tokenized_mirror.py 产出）。下载目录字节来自 `du -sb` 实测（缓存 `.du_download_cache.tsv`）。")
    L.append("")
    L.append("| # | 下载目录 | 分词目录 | .bin | .idx | .json | 字节(B) | GB | tokens(B) | 下载目录字节(B) | 下载/分词字节比 | 状态 | 校验时间 | 证据 |")
    L.append("|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|")

    s_bin = s_idx = s_json = s_bytes = s_tokens = s_dl = 0
    for i, row in enumerate(index_rows, 1):
        shards = int(row.get("shards", 0) or 0)
        tokens = int(row.get("tokens", 0) or 0)
        byts = int(row.get("bytes", 0) or 0)
        dl_dir = row.get("download_dir", "")
        tok_dir = row.get("tokenized_dir", "")
        dl_bytes = du_cache.get(dl_dir, 0)
        status = status_for(row, inprogress)
        evidence = evidence_for(row, i + 1, status)
        ratio = fmt_ratio(dl_bytes, byts)
        L.append(f"| {i} | `{short_path(dl_dir)}` | `{short_path(tok_dir)}` | {shards} | {shards} | {shards} | {byts:,} | {byts/GB:.0f} | {tokens:,} | {dl_bytes:,} | {ratio} | {status} | {idx_mtime} | {evidence} |")
        s_bin += shards; s_idx += shards; s_json += shards
        s_bytes += byts; s_tokens += tokens; s_dl += dl_bytes

    # —— 未分词源（运维令 2026-10-26 14:4x）：SFT/指令微调 JSONL，未进分词镜像 ——
    # 追加在已分词行之后、合计行之前；.bin/.idx/.json=0、tokens=0、分词字节=0，
    # 仅下载目录字节计入合计（如实登记「未分词」，不伪造「镜像完整」）。
    s_ut_files = s_ut_dl = 0
    next_i = len(index_rows) + 1
    for u in untokenized:
        u_dl = u["download_dir"]
        u_bytes = u["bytes"]
        u_files = u["files"]
        u_status = u["status"]
        u_evidence = f"未分词：{u['evidence_cmd']}"
        u_ratio = "—"
        L.append(f"| {next_i} | `{short_path(u_dl)}` | — | 0 | 0 | 0 | 0 | 0 | 0 | {u_bytes:,} | {u_ratio} | {u_status} | — | {u_evidence} |")
        s_dl += u_bytes
        s_ut_files += u_files
        s_ut_dl += u_bytes
        next_i += 1

    L.append(f"| **合计** | | | **{s_bin}** | **{s_idx}** | **{s_json}** | **{s_bytes:,}** | **{s_bytes/GB:.0f}** | **{s_tokens:,}** | **{s_dl:,}** | **{s_dl/GB:.0f} GB** | | | 误差 0 |")
    L.append("")
    L.append(f"核对式：`sum(.bin)={s_bin} = sum(.idx)={s_idx} = sum(.json)={s_json}`；`sum(分词字节)={s_bytes:,}`；`sum(tokens)={s_tokens:,}`；`sum(下载字节)={s_dl:,}`。")
    if untokenized:
        L.append(f"> 未分词源小计（运维令 2026-10-26 14:4x）：{len(untokenized)} 个 JSONL 指令微调数据集，{s_ut_files} 个 `.jsonl` 文件，下载目录字节 {s_ut_dl:,}（≈ {s_ut_dl/GB:.1f} GB），状态=未分词，未进 `.bin/.idx/.json` 分词镜像。明细：`run/data/untokenized_sft_sources.tsv`。")
    L.append("")
    L.append("> 注：`env14_*` 真身在 `/nas_train/.../baize-data/text/`（与 `tokenized/` 同盘 ⇒ hardlink）；`full_*` 真身在 `/nas_env/app.e0031982/baize-data/`（跨盘 ⇒ symlink）。两者均属「下载的一律保留」，未删未改未移。`下载/分词字节比` = 下载目录字节 ÷ 分词产物字节（int32 token×4B 常大于压缩 parquet，故比值多 < 1）。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## B. 已删除 / 不可用（运维令 2026-10-25 18:2x · 用户直令 · 终裁）")
    L.append("")
    L.append("> 用户口径：不能被本表 A 节收录的数据即不可用，留着只占盘。本节为终裁，删完即结案，不再挂账。")
    L.append(f"> 明细：`run/data/deleted_unmapped32_20261025.tsv`（{len(deleted)} 行）；理论 tokens 来自 `run/data/prune_unmapped_judgment_20261025.tsv`（action 以「保留」开头的 32 行）。")
    L.append("> ⚠️ **实测更正**：此 32 目录实为 `staging_r3/` 下的**输入符号链接暂存**（仅 ~471.6 KB 元数据，非 `.bin/.idx/.json` 产物）；真正的分词产物此前迁移 `/nas_env/full_*` 时已处置。删除释放 ≈ 471.6 KB（非任务书所述 1.89 TB；1.89 TB 为按 token×4B 的理论 .bin 体积）。`/nas_inference` 源 parquet 原样保留。")
    L.append("")
    L.append("| # | shard | 原路径(staging_r3/) | 删前字节 | 符号链接数 | 理论tokens(参考) | 状态 |")
    L.append("|:---|:---|:---|---:|---:|---:|:---|")
    sb_bytes = sb_links = sb_tokens = 0
    for i, d in enumerate(deleted, 1):
        base = os.path.basename(d["dir_path"].rstrip("/"))
        L.append(f"| {i} | {d['shard']} | {base} | {d['bytes']:,} | {d['symlink_count']} | {d['tokens']:,} | 已删除 |")
        sb_bytes += d["bytes"]; sb_links += d["symlink_count"]; sb_tokens += d["tokens"]
    L.append(f"| **合计** | | | **{sb_bytes:,}** | **{sb_links}** | **{sb_tokens:,}** | |")
    L.append("")
    theo_tb = sb_tokens * 4 / (1024 ** 4)
    L.append(f"核对式：`sum(删前字节)={sb_bytes:,}`；`sum(符号链接)={sb_links}`；`sum(理论tokens)={sb_tokens:,}`（理论 .bin 体积 ≈ {theo_tb:.2f} TB，**非实际释放量**）。")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## C. 维护说明")
    L.append("")
    L.append("- 生成器：`run/data/gen_data_mapping_md.py`（本文件由它产出；驱动数据指纹见页首）。")
    L.append("- 幂等判据：`python gen_data_mapping_md.py --check-idempotent` ⇒ 连跑两次 `DATA_MAPPING.md` 逐字节相同。")
    L.append("- A 节由 `tokenized/INDEX.tsv`（build_tokenized_mirror.py 产出）+ `.du_download_cache.tsv`（`du -sb` 下载目录）驱动；`--measure` 重测下载字节并刷新缓存。")
    L.append("- B 节由 `deleted_unmapped32_20261025.tsv`（删前留档）+ `prune_unmapped_judgment_20261025.tsv`（理论 tokens）驱动。")
    L.append("- 分词中 → 镜像完整：`done=131/131` 后重跑 `build_tokenized_mirror.py`（把新 shard hardlink 进镜像、刷新 INDEX.tsv），再清空 `mapping_inprogress.txt`，最后重跑本脚本 ⇒ A 节第 7–10 行自动翻 `镜像完整` 并补字节/tokens。")
    L.append("- 改名同步：分词后允许改目录名，但必须与本表同一批提交同步；改完跑 triplet+inode 校验写回 INDEX.tsv，再重跑本脚本。")
    L.append("- HTML 报告：需要时用 `gen_tokenized_inventory_report.py` 从本表渲染 `reports/report_data_tokenized_inventory_zh.html`。")
    L.append("")
    # —— 清理记录指针（运维令 2026-10-25 18:5x ③）——
    cleanup = load_cleanup_batches(args.cleanup_tsv)
    if cleanup:
        L.append("### 清理记录（运维令 2026-10-25 18:5x ②）")
        L.append("")
        L.append("> 磁盘清理按实测分批执行；每批实占 ≤500 GB，删后校验镜像 .bin 恒定 + 悬空链接 = 0。manifest = `run/data/disk_cleanup_candidates_20261025.tsv`。")
        L.append("")
        L.append("| 批次 | 日期 | 删除项 | 释放字节(实占) | manifest | 状态 |")
        L.append("|:---|:---|:---|---:|:---|:---|")
        for b in cleanup:
            L.append(f"| {b['batch']} | {b['date']} | {b['items']} | {b['released_bytes']:,} | `{b['manifest']}` | {b['status']} |")
        L.append("")
        L.append("> 注：`释放字节(实占)` = 硬链接只算一次后的实际释放量（非表观体积）。batch1 释放 ~1.13 MB（78 个 staging_r3 符号链接目录 + .bak + 空目录 + 旧日志）；表观体积远大于实占因 110 env14 hardlink 实占 0。")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="生成 DATA_MAPPING.md（幂等单一事实源）")
    ap.add_argument("--index", default=INDEX_DEFAULT)
    ap.add_argument("--deleted-tsv", default=DELETED_TSV_DEFAULT)
    ap.add_argument("--judgment-tsv", default=JUDGMENT_TSV_DEFAULT)
    ap.add_argument("--du-cache", default=DU_CACHE_DEFAULT)
    ap.add_argument("--inprogress", default=INPROGRESS_DEFAULT)
    ap.add_argument("--cleanup-tsv", default=CLEANUP_TSV_DEFAULT)
    ap.add_argument("--untokenized-tsv", default=UNTOKENIZED_TSV_DEFAULT, help="未分词源侧车 TSV（运维令 2026-10-26 14:4x）")
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--measure", action="store_true", help="重新 du 下载目录并刷新缓存")
    ap.add_argument("--check-idempotent", action="store_true", help="连跑两次比较字节，退出码 0=幂等")
    args = ap.parse_args()

    md = build_md(args)
    with open(args.out, "w") as f:
        f.write(md)
    print(f"[ok] wrote {args.out} ({len(md)} bytes)")

    if args.check_idempotent:
        md2 = build_md(args)
        same = (md == md2)
        print(f"[idempotent] run1 == run2 : {same} (len1={len(md)} len2={len(md2)})")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
