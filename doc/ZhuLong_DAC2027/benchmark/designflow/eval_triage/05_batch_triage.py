#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_batch_triage.py — 全量批次（696 例）失败归因 CLI，stdlib-only，py3.8+。

用法
----
  python3 05_batch_triage.py --batch <RUN_DIR> --cases <EDA-Eval-DesignFlow.jsonl> \
      --out <OUTDIR> [--dry-run] [--emit-tex] [--json-only] [--selftest] \
      [--layout auto|flat|nested|shard] [--limit N] [--seed N]

设计目标
--------
1. 不假设批次目录结构：先"启发式发现"，发现不足时**明确告警 + 友好报错**，
   而不是静默产出 0 命中。
2. 每个 case 的判定都带**可复核的证据路径**（写进 triage_summary.json 与
   report.md 的抽样段）。
3. 只有能机器核验的信号才进分类；核验不了的一律进 UNKNOWN，并把
   unknown 比例显式写进报告。

目录发现顺序（任务书 a–d 的逐条实现：build_case_index / discover_case）
----------------------------------------------------------------------
a. case 目录不存在 → ABSENT（依据：--cases 里的 task_id 在 RUN_DIR 下找不到目录）
b. 判分产物发现（三级证据，tier 越低越不可信）：
     tier1  结构化判定：case 目录内 *.json 含 pass/verdict/score/result/status/
            grade/passed 字段（支持一层嵌套，如 {"result": {"pass": true}}）
     tier2  文本摘要：check*.log / judge*.log / grade*.log / verdict*.log /
            summary*.txt / result*.txt 等，grep 词边界 PASS / FAIL / ERROR。
            只有"名字像判分产物"的文件才计入 PASS/FAIL 标记（避免把 prompt.txt
            任务描述里的措辞当证据）；ERROR/infra/timeout/runtime 在所有文本
            文件里都统计。标记再分强/弱：判定行（行首 PASS / "PASS:" /
            "verdict: ... PASS" / "case X: PASS"）为强，正文里的裸词为弱。
     tier3  交付物：submit.zip / submission.zip / answer.zip / deliverable.zip，
            或同名目录（submit/ submission/ answer/ deliverable/ solution/）
c. 判定优先级（先命中先返回，命中项全部写进 evidence）：
     1) tier1 PASS                          → PASS
     2) tier1 FAIL                          → FAIL + classify_fail()
     3) tier1 ERROR/异常值                   → ERROR + classify_error()
     4) tier2 强 FAIL 标记                   → FAIL + classify_fail()
     5) tier2 强 PASS 标记（无强 FAIL）       → PASS
     6) tier2 弱 FAIL 标记                   → FAIL（并打 coverage 警告）
     7) tier2 弱 PASS 标记（无弱 FAIL）       → PASS（并打 coverage 警告）
     8) tier2 有 ERROR/Traceback 标记：
          a. 有 runtime 签名且无 infra/timeout → FAIL + classify_fail()
             （候选脚本崩了 = ASSERT_RUNTIME，不是 harness 的 ERROR）
          b. 否则                              → ERROR + classify_error()
     9) wall >= 2400s                        → ERROR（ERROR_TIMEOUT）
    10) 有 submit 交付物但无任何判分证据      → FAIL(unknown_reason, UNKNOWN)
                                                 + coverage_warning
    11) 什么都没有                            → FAIL(no_evidence, UNKNOWN)
                                                 + coverage_warning
   说明：强标记按"强 FAIL > 强 PASS > 弱 FAIL > 弱 PASS"定序（宁可低估 PASS，
   也不把一次失败运行记成通过）；weak 命中的 case 一律带 coverage 警告，
   供人工抽样复核。
d. tier3-only（有提交、无判分）→ FAIL class=UNKNOWN，kind=NO_VERDICT_BUT_SUBMIT，
   计入 coverage_warning 与 unknown 比例。

分类触发证据（classify_fail / classify_error，每条都是正则 + 命中日志行）
----------------------------------------------------------------------
  ERROR_INFRA      日志行命中 MCP/connection refused|reset/ECONNRESET/refused/
                   API/gateway/rate limit/429/... 且该行不含 agent 自身逻辑
                   排除词（syntax error / FAIL / check failed / assert）
  ERROR_TIMEOUT    wall >= 2400s，或日志命中 timed out / timeout / deadline
                   exceeded / killed after（纯 "timeout=2400" 配置行被过滤）
  NO_SUBMIT        FAIL 判定成立，但 case 目录内没有任何 submit 交付物
  FORMAT_CONTRACT  有 submit，但 zip 打不开/空 zip（真实机器检查），或日志命中
                   BadZip / not a zip / missing entry / naming ...
  ASSERT_RUNTIME   日志命中非 0 退出码 / Traceback / No such file or directory /
                   syntax error（候选脚本没跑完）
  ASSERT_SEMANTIC  日志命中"失败条件编号"（condition/check/test #N ... FAIL），
                   即跑通但结果与 oracle 不符；编号写进 evidence.fail_conditions
  ASSERT_ANTIHARDCODE  可见 A 通过、hidden B 失败（A: PASS 且 hidden/held-out 行
                   命中 FAIL）
  UNKNOWN          以上都不命中 → 保留在 UNKNOWN，绝不并入别的类

Pass% 口径
----------
  本工具 Pass% = PASS / (PASS + FAIL)，即"已判定样本"口径（62/620）。
  全批次 62/(62+558) = 10.0%；ERROR/ABSENT 计入分母则 62/626 = 9.9%、
  62/696 = 8.9%。三种口径都写进 triage_summary.json 的 meta.pass_rate，
  正文若用 62/626 = 9.9%，请保留 tex 表头注释。

退出码
------
  0 成功；1 selftest 失败；2 输入路径/参数错误（含友好提示与探针命令）。
"""

import argparse
import contextlib
import io
import json
import os
import random
import re
import shutil
import sys
import tempfile
import time
import zipfile

VERSION = "1.0.0"

STATUSES = ["PASS", "FAIL", "ERROR", "ABSENT"]
ERROR_CLASSES = ["ERROR_TIMEOUT", "ERROR_INFRA"]
FAIL_CLASSES = [
    "NO_SUBMIT",
    "FORMAT_CONTRACT",
    "ASSERT_RUNTIME",
    "ASSERT_SEMANTIC",
    "ASSERT_ANTIHARDCODE",
    "UNKNOWN",
]
# 表格列顺序：超时排在 infra 前，因为 2400s 是最硬的机器可核验信号
CLASS_ORDER = ["PASS"] + ERROR_CLASSES + FAIL_CLASSES

TIMEOUT_WALL_SEC = 2400.0          # 批次统一 2400s 超时
MAX_TEXT_BYTES = 4 * 1024 * 1024   # 单文件最多读 4MB 做 grep
MAX_TEXT_LINES = 40000             # 或最多 4 万行
MAX_JSON_BYTES = 2 * 1024 * 1024   # 判定 json 上限
MAX_FILES_PER_CASE = 4000          # 单 case 扫描文件数上限（防 oracle 大目录）
MAX_ZIP_BYTES = 512 * 1024 * 1024  # 只 inspect zip 中央目录，不解压

# ---------------------------------------------------------------- 判定/分类正则
PASS_RE = re.compile(r"(?<![A-Za-z0-9_])PASS(?:ED)?(?![A-Za-z0-9_])")
FAIL_RE = re.compile(r"(?<![A-Za-z0-9_])FAIL(?:ED|URE)?(?![A-Za-z0-9_])")
# "强标记"：判定行（行首 PASS / PASS: / verdict|status|result ... PASS / case|test ... PASS）
# 弱标记：文本里随便出现 PASS/FAIL 字样（可能只是 prompt 里的措辞）
STRONG_PASS_RE = re.compile(
    r"(?:^\s*[\[\(\|\-]?\s*PASS(?:ED)?\b"
    r"|(?<![A-Za-z0-9_])PASS(?:ED)?\s*[:=]"
    r"|\b(?:verdict|status|result|outcome|summary|conclusion)s?\b[^\n]{0,20}?"
    r"(?<![A-Za-z0-9_])PASS(?:ED)?\b"
    r"|\b(?:case|test|check|condition|assertion|task)s?\b[^\n]{0,24}?"
    r"(?<![A-Za-z0-9_])PASS(?:ED)?\b)", re.I)
STRONG_FAIL_RE = re.compile(
    r"(?:^\s*[\[\(\|\-]?\s*FAIL(?:ED|URE)?\b"
    r"|(?<![A-Za-z0-9_])FAIL(?:ED|URE)?\s*[:=]"
    r"|\b(?:verdict|status|result|outcome|summary|conclusion)s?\b[^\n]{0,20}?"
    r"(?<![A-Za-z0-9_])FAIL(?:ED|URE)?\b"
    r"|\b(?:case|test|check|condition|assertion|task)s?\b[^\n]{0,24}?"
    r"(?<![A-Za-z0-9_])FAIL(?:ED|URE)?\b)", re.I)
ERR_MARK_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:ERROR|FATAL|CRITICAL)(?![A-Za-z0-9_])"
    r"|Traceback \(most recent call last\)"
    r"|(?<![A-Za-z0-9_])(?:Exception|EXCEPTION)(?![A-Za-z0-9_])"
)

TIMEOUT_SIG = re.compile(
    r"(timed out|time[-\s]?out|deadline exceeded|killed after|exceeded the \d+\s?s"
    r"|TimeoutError|watchdog)", re.I)
# 纯配置行（timeout=2400 / "timeout": 2400）不算超时证据
TIMEOUT_CFG_ONLY = re.compile(
    r"time[-\s]?out\s*[:=]\s*\d+(?:\.\d+)?\s*[)\]}]*\s*$", re.I)
TIMEOUT_CTX = re.compile(r"(after|exceed|kill|raise|abort|fail|terminat|signal)", re.I)

INFRA_SIG = re.compile(
    r"(mcp|model context protocol|connection (?:refused|reset|closed|error|aborted)"
    r"|econnrefused|econnreset|socket hang up|gateway|rate[-\s]?limit|\b429\b"
    r"|api[-\s]?key|unauthorized|no route to host|network is unreachable"
    r"|temporary failure in name resolution|service unavailable|\b50[234]\b"
    r"|proxy error|tls handshake)", re.I)
# 这些词出现说明同一行是 agent/checker 自身逻辑失败，不是基础设施
INFRA_EXCLUDE = re.compile(
    r"(syntax error|undefined variable|\bFAIL\b|check failed|assert"
    r"|assertionerror|condition\s*#?\s*\d+|checker\.tcl)", re.I)

FORMAT_SIG = re.compile(
    r"(badzip|bad zip|not a zip|corrupt(?:ed)? (?:zip|archive)"
    r"|invalid (?:zip|archive)|missing (?:required )?(?:entry|file|manifest)"
    r"|no such (?:entry|file) in|(?:unexpected|wrong|invalid) (?:entry )?name"
    r"|naming (?:convention|mismatch|violation)|empty (?:zip|submission)"
    r"|zip (?:error|is invalid)|cannot open zip)", re.I)

RUNTIME_SIG = re.compile(
    r"(traceback \(most recent call last\)|returncode[^\n]{0,24}?\b[1-9]\d*\b"
    r"|exit(?:ed)? (?:code|status)[^\n]{0,24}?\b[1-9]\d*\b|non[-\s]?zero exit"
    r"|command not found|no such file or directory|syntax error"
    r"|permission denied|segmentation fault|core dumped)", re.I)

COND_RE = re.compile(
    r"(?:condition|check|test|assertion|checker)[\s_#:\-]*([A-Za-z]?\d{1,3})\b"
    r"[^\n]{0,60}?\b(?:FAIL(?:ED)?|MISMATCH|VIOLATED|NOT MET|MISSING)\b", re.I)
COND_RE_REV = re.compile(
    r"\b(?:FAIL(?:ED)?|MISMATCH)\b[^\n]{0,60}?"
    r"(?:condition|check|test|assertion)[\s_#:\-]*([A-Za-z]?\d{1,3})\b", re.I)

HIDDEN_RE = re.compile(
    r"(hidden|held[-\s_]?out|private (?:test|case)s?|case[\s_]?B\b"
    r"|variant[\s_]?B\b|second (?:test|case) set)", re.I)
VIS_A_OK_RE = re.compile(
    r"(?:case[\s_]?A\b|\bvisible\b|\bpublic\b)[^\n]{0,30}?(?:PASS|OK|SUCCESS)",
    re.I)

WALL_RE = re.compile(
    r"(?:wall|elapsed|duration|runtime|took|finished in)\D{0,16}?"
    r"(\d+(?:\.\d+)?)\s*(?:s\b|sec\b|secs\b|seconds\b)", re.I)

VERDICT_KEYS = ("pass", "passed", "verdict", "result", "status", "grade",
                "success", "ok", "score")
PASS_TOKENS = {"pass", "passed", "ok", "success", "succeed", "succeeded",
               "true", "yes", "accept", "accepted", "1"}
FAIL_TOKENS = {"fail", "failed", "failure", "false", "no", "reject", "rejected",
               "wrong", "mismatch", "0"}
ERROR_TOKENS = {"error", "errored", "exception", "crash", "crashed", "timeout",
                "timed_out", "aborted", "skipped"}

SUBMIT_FILE_RE = re.compile(
    r"^(?:submit|submission|answer|deliverable|solution|final)[\w.\-]*"
    r"\.(?:zip|tar|tar\.gz|tgz)$", re.I)
SUBMIT_DIR_NAMES = {"submit", "submission", "answer", "deliverable", "solution"}

VERDICT_JSON_NAME_RE = re.compile(
    r"(judge|check|checker|result|verdict|score|grade|eval|report|summary|status)",
    re.I)
TEXT_LOG_NAME_RE = re.compile(r"\.(?:log|txt|out|jsonl|md)$", re.I)
TEXT_SUMMARY_NAME_RE = re.compile(
    r"(check|checker|judge|grade|verdict|score|summary|result|eval|report)",
    re.I)


# ------------------------------------------------------------------ 小工具
def eprint(*a):
    print(*a, file=sys.stderr)


def norm_id(s):
    """归一化 id 用于目录名匹配：小写，非字母数字 → '_'，压缩下划线。"""
    s = str(s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def rel_to(path, root):
    try:
        r = os.path.relpath(path, root)
    except ValueError:      # Windows 跨盘符
        return path
    return r.replace(os.sep, "/")


def safe_float(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if v != v:              # NaN
        return None
    return v


def pct(num, den):
    return (100.0 * num / float(den)) if den else 0.0


def die(msg, hint=None, probe=None):
    """输入类错误统一走这里：清楚说明 + 可执行的下一步，退出码 2。"""
    eprint("ERROR: " + msg)
    if hint:
        eprint("提示: " + hint)
    if probe:
        eprint("探针: " + probe)
    raise SystemExit(2)



# --------------------------------------------------------------- cases jsonl
ID_ALIASES = ["task_id", "id", "task_name", "name", "case_id", "case"]
DOMAIN_ALIASES = ["domain", "category", "subdomain", "group", "family"]
TEXT_ALIASES = ["task", "instruction", "prompt", "description", "query"]


def _domain_from_id(tid):
    """从 task_id 推 domain：EDA-Eval-DesignFlow-PnRSignoff-003 → PnRSignoff。

    仅在 cases jsonl 完全没有 domain 类键时使用（真实全量 jsonl 就是这种：
    只有 task_id/prompt/metadata），推出来后仍逐 case 写进 summary 可核对。
    """
    s = str(tid or "").strip()
    for pref in ("EDA-Eval-DesignFlow-", "EDA-Eval-", "EDA-"):
        if s.startswith(pref):
            s = s[len(pref):]
            break
    s = re.sub(r"[-_]?\d+$", "", s)
    return s or "unknown"


def load_cases(path):
    """解析 cases jsonl，自动探测键名。

    返回 (records, info)
      records: [{"task_id", "domain", "text_len", "line_no"}]
      info:    {"id_key", "domain_key", "text_key", "n", "duplicate_ids",
                "missing_domain", "first_keys"}
    键名缺失时 die()（退出码 2）并打印可用顶层键，绝不静默兜底。
    注意：任务描述只在必要时才读（这里只记 text_len），避免 696 条长 prompt 全驻留。
    """
    if not os.path.isfile(path):
        die("cases jsonl 不存在: %s" % path,
            hint="确认 --cases 指向 EDA-Eval-DesignFlow.jsonl（集群绝对路径，勿用 "
                 "~ 或相对路径）",
            probe='ls -l "<cases.jsonl>"; head -c 400 "<cases.jsonl>"')

    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError as exc:
                die("cases jsonl 第 %d 行不是合法 JSON: %s" % (ln, exc),
                    hint="先定位坏行再重跑；本工具不做静默跳过",
                    probe='python3 - <<"PY"\nimport json\np="<cases.jsonl>"\n'
                          'for i,l in enumerate(open(p,encoding="utf-8"),1):\n'
                          '    l=l.strip()\n'
                          '    if not l: continue\n'
                          '    try: json.loads(l)\n'
                          '    except Exception as e: print(i,e)\nPY')
            if not isinstance(obj, dict):
                die("cases jsonl 第 %d 行不是 JSON object（是 %s）"
                    % (ln, type(obj).__name__))
            rows.append((ln, obj))

    if not rows:
        die("cases jsonl 是空的: %s" % path,
            hint="空文件说明 cases 导出步骤没跑完，或路径指向了别的空文件",
            probe='wc -l "<cases.jsonl>"; head -2 "<cases.jsonl>"')

    first_keys = list(rows[0][1].keys())

    def pick(aliases):
        for k in aliases:                       # 1) 精确按优先级
            if any(k in o for _, o in rows[:80]):
                return k
        lower = {k.lower(): k for k in first_keys}
        for k in aliases:                       # 2) 大小写不敏感兜底
            if k in lower:
                return lower[k]
        return None

    id_key = pick(ID_ALIASES)
    domain_key = pick(DOMAIN_ALIASES)
    text_key = pick(TEXT_ALIASES)

    if id_key is None:
        die("cases jsonl 里找不到 id 键（试过 %s）；该文件顶层键为: %s"
            % ("/".join(ID_ALIASES), first_keys),
            hint="本工具不会静默兜底 id（否则 696 例会整体错位）。"
                 "请确认 cases 文件是否被换成了别的格式，或导出时补 task_id",
            probe='head -1 "<cases.jsonl>" | python3 -m json.tool | head -40')

    recs, seen, dup, missing_dom = [], {}, [], []
    derived_dom = 0
    for ln, obj in rows:
        tid = obj.get(id_key)
        if tid is None or str(tid).strip() == "":
            die("cases jsonl 第 %d 行缺少 id 键 '%s'（该行顶层键: %s）"
                % (ln, id_key, list(obj.keys())),
                hint="逐行校验 id；空 task_id 会让目录发现整体错位")
        tid = str(tid).strip()
        if domain_key:
            dom = obj.get(domain_key)
            dom = str(dom).strip() if dom not in (None, "") else ""
            if not dom:
                missing_dom.append(tid)
                dom = _domain_from_id(tid)
        else:
            dom = _domain_from_id(tid)
            derived_dom += 1
        if tid in seen:
            dup.append(tid)
            continue
        seen[tid] = ln
        raw_text = obj.get(text_key) if text_key else None
        recs.append({
            "task_id": tid,
            "domain": dom,
            "line_no": ln,
            "text_len": len(str(raw_text)) if raw_text else 0,
        })

    info = {
        "id_key": id_key,
        "domain_key": domain_key,
        "text_key": text_key,
        "domain_source": ("field:" + domain_key) if domain_key
                          else "derived_from_task_id",
        "n": len(recs),
        "duplicate_ids": dup,
        "missing_domain": missing_dom,
        "first_keys": first_keys,
    }
    return recs, info


# ------------------------------------------------------------ 批次目录发现
LAYOUT_HINT = (
    "先用探针看批次目录真实结构（不要猜）：\n"
    "    find <RUN_DIR> -maxdepth 2 | head -50\n"
    "    find <RUN_DIR> -maxdepth 3 -name 'submit.zip' | head -5\n"
    "    find <RUN_DIR> -maxdepth 3 -name 'check*.log' | head -5\n"
    "然后显式指定布局：--layout flat（RUN_DIR/<task_id>）| "
    "nested（RUN_DIR/cases/<task_id>）| shard（RUN_DIR/<worker>/<task_id>）| auto，"
    "或用 --case-glob '<RUN_DIR>/*/{task_id}' 自己写模板（模板里 {task_id} 会被替换）。"
)


def build_case_index(batch_dir, task_ids, layout="auto", case_glob=None,
                     max_depth=4):
    """在 RUN_DIR 下启发式找到每个 task_id 的 case 目录。

    返回 (index, stats)：
      index: {task_id: abs_dir}
      stats: {layout_roots: [...], scanned_dirs: n, depth_limit: n,
              missing: [task_id...], ambiguous: {task_id: [dirs]}}
    策略（auto）：先试显式布局根（flat/nested/shard），再退化为全树 basename 匹配
    （按 task_id 归一化比对，兼容 0007_<task_id> 这类前缀命名）。
    """
    if not os.path.isdir(batch_dir):
        die("批次目录不存在或不是目录: %s" % batch_dir,
            hint="集群上先确认 RUN_DIR 拼写（run_batch_YYYYMMDD_HHMMSS）",
            probe='ls -ld "<RUN_DIR>"; ls "<RUN_DIR>" | head -20; '
                  'find "<RUN_DIR>" -maxdepth 2 | head -50')

    idset = list(task_ids)
    norm_to_id = {}
    for t in idset:
        norm_to_id.setdefault(norm_id(t), t)
    index, ambiguous = {}, {}

    def register(path, tid):
        path = os.path.abspath(path)
        if tid in index and index[tid] != path:
            ambiguous.setdefault(tid, [index[tid]]).append(path)
            return
        index[tid] = path

    def try_root(root):
        """在某个布局根目录下按 basename 建索引，返回命中数。"""
        if not os.path.isdir(root):
            return 0
        hits = 0
        try:
            entries = sorted(os.listdir(root))
        except OSError:
            return 0
        for name in entries:
            full = os.path.join(root, name)
            if not os.path.isdir(full):
                continue
            tid = norm_to_id.get(norm_id(name))
            if tid is None:
                # 兼容 "0007_EDA-Eval-...-002" / "run7_EDA-Eval-...-002" 前缀命名
                n = norm_id(name)
                for cand_norm, cand_id in norm_to_id.items():
                    if n.endswith("_" + cand_norm):
                        tid = cand_id
                        break
            if tid:
                register(full, tid)
                hits += 1
        return hits

    layout_roots = []
    if layout in ("auto", "flat", "nested", "shard"):
        roots = []
        if layout in ("auto", "flat"):
            roots.append(batch_dir)
        if layout in ("auto", "nested"):
            for sub in ("cases", "case", "runs", "run", "eval", "outputs",
                        "output", "results", "work"):
                roots.append(os.path.join(batch_dir, sub))
        if layout in ("auto", "shard"):
            for i in range(1, 65):          # worker_1..64 / shard_1..
                for pre in ("worker", "shard", "w"):
                    roots.append(os.path.join(batch_dir, "%s_%d" % (pre, i)))
                    roots.append(os.path.join(batch_dir, "%s%d" % (pre, i)))
        for r in roots:
            hits = try_root(r)
            if hits:
                layout_roots.append((rel_to(r, batch_dir) or ".", hits))

    if case_glob:                            # 用户显式模板优先级最高
        base = case_glob.replace("{task_id}", "*")
        parent = os.path.dirname(base) or "."
        for name in sorted(os.listdir(parent)) if os.path.isdir(parent) else []:
            full = os.path.join(parent, name)
            tid = norm_to_id.get(norm_id(name))
            if tid and os.path.isdir(full):
                register(full, tid)
        if not layout_roots:
            layout_roots.append(("glob:%s" % case_glob, len(index)))

    # ---- 退化：全树扫描（有深度上限），只认 basename 命中 task_id 的目录
    scanned = 0
    if len(index) < len(idset):
        base_depth = batch_dir.rstrip(os.sep).count(os.sep)
        for root, dirs, _files in os.walk(batch_dir):
            depth = root.count(os.sep) - base_depth
            scanned += 1
            if depth >= max_depth:
                dirs[:] = []
                continue
            dirs.sort()
            hit_here = False
            for d in list(dirs):
                full = os.path.join(root, d)
                tid = norm_to_id.get(norm_id(d))
                if tid is None:
                    n = norm_id(d)
                    for cand_norm, cand_id in norm_to_id.items():
                        if n.endswith("_" + cand_norm):
                            tid = cand_id
                            break
                if tid:
                    register(full, tid)
                    hit_here = True
            if hit_here:
                # 命中层以下不再下钻，避免把 oracle/ 子目录误当 case
                dirs[:] = [d for d in dirs
                           if norm_id(d) not in norm_to_id
                           and d not in ("oracle", "assets", "workspace")]

    missing = [t for t in idset if t not in index]
    stats = {
        "layout_roots": layout_roots,
        "scanned_dirs": scanned,
        "depth_limit": max_depth,
        "missing": missing,
        "ambiguous": ambiguous,
        "found": len(index),
        "total": len(idset),
    }
    return index, stats


def list_case_files(case_dir, max_files=MAX_FILES_PER_CASE):
    """列出 case 目录内文件（有上限，跳过隐藏目录），返回 (files, truncated)。"""
    files, truncated = [], False
    for root, dirs, names in os.walk(case_dir):
        dirs.sort()
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for n in sorted(names):
            files.append(os.path.join(root, n))
            if len(files) >= max_files:
                return files, True
    return files, truncated


# ----------------------------------------------------- tier1：结构化判定 json
def norm_verdict(key, value):
    """把判定字段归一成 PASS/FAIL/ERROR；无法核验的返回 None（不猜）。"""
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if isinstance(value, (int, float)):
        if value == 1:
            return "PASS"
        if value == 0:
            return "FAIL"
        return None            # 纯 score 需要阈值，本工具不单独据此定状态
    if isinstance(value, str):
        t = value.strip().lower()
        if t in PASS_TOKENS:
            return "PASS"
        if t in FAIL_TOKENS:
            return "FAIL"
        if t in ERROR_TOKENS:
            return "ERROR"
    return None


def _walk_verdicts(obj, prefix, out, depth):
    if depth > 1 or not isinstance(obj, dict):
        return
    for k, v in obj.items():
        lk = str(k).strip().lower()
        if lk in VERDICT_KEYS:
            if isinstance(v, dict):
                _walk_verdicts(v, prefix + [str(k)], out, depth + 1)
            else:
                nv = norm_verdict(lk, v)
                if nv:
                    out.append({"key": ".".join(prefix + [str(k)]),
                                "value": v if isinstance(v, (bool, int, float, str))
                                else str(v)[:80],
                                "norm": nv})
        elif isinstance(v, dict) and depth < 1:
            _walk_verdicts(v, prefix + [str(k)], out, depth + 1)


def parse_verdict_json(path):
    """读一个 json 文件里所有可核验判定字段。返回 {"hits":[...], "error":str|None}。"""
    try:
        if os.path.getsize(path) > MAX_JSON_BYTES:
            return {"hits": [], "error": "too_large"}
    except OSError as exc:
        return {"hits": [], "error": "stat_failed:%s" % exc}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            obj = json.load(f)
    except (ValueError, OSError) as exc:
        return {"hits": [], "error": "parse_failed:%s" % str(exc)[:120]}
    hits = []
    _walk_verdicts(obj, [], hits, 0)
    return {"hits": hits, "error": None}


# ------------------------------------------------------- tier2：文本摘要 grep
class TextHit(object):
    """单文件 grep 结果（每文件只留少量片段，避免 summary.json 膨胀）。"""

    __slots__ = ("path", "lines", "pass_n", "fail_n", "err_n", "fail_lines",
                 "err_lines", "infra", "timeout", "format_sig", "runtime",
                 "conds", "hidden_fail", "a_ok", "wall", "strong_pass",
                 "strong_fail")

    def __init__(self, path):
        self.path = path
        self.lines = 0
        self.pass_n = self.fail_n = self.err_n = 0
        self.strong_pass = self.strong_fail = 0
        self.fail_lines = []
        self.err_lines = []
        self.infra = []
        self.timeout = []
        self.format_sig = []
        self.runtime = []
        self.conds = []
        self.hidden_fail = []
        self.a_ok = []
        self.wall = None

    def as_dict(self):
        return {
            "path": self.path,
            "lines": self.lines,
            "pass": self.pass_n, "fail": self.fail_n, "error": self.err_n,
            "strong_pass": self.strong_pass, "strong_fail": self.strong_fail,
            "wall_sec": self.wall,
            "infra": self.infra[:3],
            "timeout": self.timeout[:3],
            "format_sig": self.format_sig[:3],
            "runtime_sig": self.runtime[:3],
            "fail_conditions": self.conds[:8],
            "hidden_fail": self.hidden_fail[:3],
            "a_pass": self.a_ok[:2],
            "fail_lines": self.fail_lines[:3],
            "err_lines": self.err_lines[:3],
        }


def _snip(line, n=180):
    return line.strip()[:n]


def scan_text_file(path, rel, count_markers=True):
    """逐行 grep 一个文本日志，返回 TextHit。

    count_markers=False 时不计 PASS/FAIL/失败条件（用于 prompt/task 描述这类
    非判分文本，避免把任务措辞里的 "fail" 当成判分证据）；ERROR/infra/timeout/
    runtime/wall 始终统计，因为崩溃信息常常只出现在 agent 日志里。
    """
    hit = TextHit(rel)
    try:
        if os.path.getsize(path) == 0:
            return hit
    except OSError:
        return hit
    read_bytes = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                hit.lines += 1
                read_bytes += len(line)
                if hit.lines > MAX_TEXT_LINES or read_bytes > MAX_TEXT_BYTES:
                    break
                # 纯配置行（timeout=2400）不算超时证据
                is_timeout_cfg = bool(TIMEOUT_CFG_ONLY.search(line)) and \
                    not TIMEOUT_CTX.search(line)
                if count_markers and PASS_RE.search(line):
                    hit.pass_n += 1
                    if STRONG_PASS_RE.search(line):
                        hit.strong_pass += 1
                    if len(hit.a_ok) < 2 and VIS_A_OK_RE.search(line):
                        hit.a_ok.append(_snip(line))
                if count_markers and FAIL_RE.search(line):
                    hit.fail_n += 1
                    if STRONG_FAIL_RE.search(line):
                        hit.strong_fail += 1
                    if len(hit.fail_lines) < 3:
                        hit.fail_lines.append(_snip(line))
                    if len(hit.hidden_fail) < 3 and HIDDEN_RE.search(line):
                        hit.hidden_fail.append(_snip(line))
                if ERR_MARK_RE.search(line):
                    hit.err_n += 1
                    if len(hit.err_lines) < 3:
                        hit.err_lines.append(_snip(line))
                if not is_timeout_cfg and TIMEOUT_SIG.search(line) \
                        and len(hit.timeout) < 3:
                    hit.timeout.append(_snip(line))
                if INFRA_SIG.search(line) and not INFRA_EXCLUDE.search(line) \
                        and len(hit.infra) < 3:
                    hit.infra.append(_snip(line))
                if FORMAT_SIG.search(line) and len(hit.format_sig) < 3:
                    hit.format_sig.append(_snip(line))
                if RUNTIME_SIG.search(line) and len(hit.runtime) < 3:
                    hit.runtime.append(_snip(line))
                if count_markers:
                    for rx in (COND_RE, COND_RE_REV):
                        m = rx.search(line)
                        if m:
                            cid = m.group(1)
                            if cid not in hit.conds and len(hit.conds) < 12:
                                hit.conds.append(cid)
                            break
                if hit.wall is None:
                    wm = WALL_RE.search(line)
                    if wm:
                        v = safe_float(wm.group(1))
                        if v is not None:
                            hit.wall = v
    except OSError:
        pass
    return hit


# ------------------------------------------------------------- tier3：交付物
def inspect_zip(path):
    """只检查 zip 能否打开 + entry 数，不解压。"""
    info = {"openable": False, "entries": 0, "sample": [], "issue": None}
    try:
        if os.path.getsize(path) > MAX_ZIP_BYTES:
            info["issue"] = "zip_too_large_skip"
            return info
    except OSError as exc:
        info["issue"] = "stat_failed:%s" % str(exc)[:60]
        return info
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            info["openable"] = True
            info["entries"] = len(names)
            info["sample"] = names[:5]
            if not names:
                info["issue"] = "empty_zip"
    except zipfile.BadZipFile as exc:
        info["issue"] = "bad_zip:%s" % str(exc)[:80]
    except (OSError, RuntimeError) as exc:
        info["issue"] = "zip_unreadable:%s" % str(exc)[:80]
    return info


def find_submits(case_dir, files):
    """找 submit 交付物：zip/tar 文件 或 submit/ 类目录。返回 list[dict]。"""
    found = []
    for p in files:
        base = os.path.basename(p)
        if SUBMIT_FILE_RE.match(base):
            item = {"kind": "file", "path": rel_to(p, case_dir)}
            if base.lower().endswith(".zip"):
                item.update(inspect_zip(p))
            else:
                item.update({"openable": True, "entries": None, "issue": None})
            found.append(item)
    seen = set()
    for root, dirs, _names in os.walk(case_dir):
        depth = rel_to(root, case_dir).count("/")
        if depth >= 2:
            dirs[:] = []
            continue
        dirs.sort()
        for d in list(dirs):
            if d.lower() in SUBMIT_DIR_NAMES:
                full = os.path.join(root, d)
                rp = rel_to(full, case_dir)
                if rp in seen:
                    continue
                seen.add(rp)
                try:
                    n = len(os.listdir(full))
                except OSError:
                    n = 0
                found.append({"kind": "dir", "path": rp, "openable": True,
                              "entries": n,
                              "issue": None if n else "empty_submit_dir"})
    return found


# --------------------------------------------------------------- 单 case 发现
MAX_JSON_CANDIDATES = 40
MAX_TEXT_CANDIDATES = 40


def _pick_candidates(files, rx_ext, name_re, limit):
    """按"名字像判分产物"优先排序，返回前 limit 个候选文件。"""
    prio, rest = [], []
    for p in files:
        base = os.path.basename(p)
        if not rx_ext.search(base):
            continue
        (prio if name_re.search(base) else rest).append(p)
    prio.sort()
    rest.sort()
    return (prio + rest)[:limit]


def discover_case(case_dir, batch_root):
    """对一个 case 目录执行三级证据发现并给出 status/class/evidence。"""
    ev = {
        "case_dir": rel_to(case_dir, batch_root) if case_dir else None,
        "files_scanned": 0,
        "files_truncated": False,
        "verdicts": [],
        "logs": [],
        "submit": [],
        "hit_files": [],
        "skipped_json": [],
    }
    if not case_dir or not os.path.isdir(case_dir):
        return {
            "status": "ABSENT",
            "class": None,
            "unknown_kind": None,
            "decision": "a_no_case_dir",
            "wall_sec": None,
            "evidence": ev,
            "coverage": {"judgment_evidence": False, "warning": None},
        }

    files, truncated = list_case_files(case_dir)
    ev["files_scanned"] = len(files)
    ev["files_truncated"] = truncated

    # ---- tier1：*.json 里的判定字段
    json_files = _pick_candidates(files, re.compile(r"\.json$", re.I),
                                  VERDICT_JSON_NAME_RE, MAX_JSON_CANDIDATES)
    for p in json_files:
        res = parse_verdict_json(p)
        if res["hits"]:
            for h in res["hits"]:
                ev["verdicts"].append({"path": rel_to(p, case_dir),
                                       "key": h["key"], "value": h["value"],
                                       "norm": h["norm"]})
        elif res["error"]:
            ev["skipped_json"].append({"path": rel_to(p, case_dir),
                                       "error": res["error"]})

    # ---- tier2：文本摘要 grep
    text_files = _pick_candidates(files, TEXT_LOG_NAME_RE,
                                  TEXT_SUMMARY_NAME_RE, MAX_TEXT_CANDIDATES)
    for p in text_files:
        # 只有"名字像判分产物"的文件才计入 PASS/FAIL 标记，避免把 prompt/任务
        # 描述里的措辞当判分证据；ERROR/infra/timeout 到处都统计
        is_summary = bool(TEXT_SUMMARY_NAME_RE.search(os.path.basename(p)))
        th = scan_text_file(p, rel_to(p, case_dir), count_markers=is_summary)
        if th.lines:
            ev["logs"].append(th.as_dict())

    # ---- tier3：交付物
    ev["submit"] = find_submits(case_dir, files)

    wall = None
    for lg in ev["logs"]:
        w = lg.get("wall_sec")
        if w is not None and (wall is None or w > wall):
            wall = w

    res = _decide(ev, wall)
    res["wall_sec"] = wall
    res["evidence"] = ev
    res["coverage"] = {
        "judgment_evidence": bool(ev["verdicts"]) or any(
            (lg["pass"] + lg["fail"] + lg["error"]) > 0 for lg in ev["logs"]),
        "warning": None,
    }
    if not res["coverage"]["judgment_evidence"]:
        res["coverage"]["warning"] = (
            "无判分证据（tier1/tier2 均未命中）；仅凭 submit 存在性推断，需人工复核"
            if ev["submit"] else
            "无判分证据且无 submit 交付物；该 case 的 FAIL 只是默认判定")
    elif "weak" in res["decision"]:
        # 只有弱标记（正文里出现过 PASS/FAIL 字样，但不是判定行）→ 抽样复核
        res["coverage"]["warning"] = (
            "仅弱标记命中（非判定行出现 PASS/FAIL 字样），建议人工抽样复核")
    # 只有真正"用到"的文件进 hit_files，方便抽样复核
    hits = set()
    for v in ev["verdicts"]:
        hits.add(v["path"])
    for lg in ev["logs"]:
        if lg["pass"] or lg["fail"] or lg["error"] or lg["infra"] or \
                lg["timeout"] or lg["format_sig"] or lg["runtime_sig"] or \
                lg["fail_conditions"] or lg["hidden_fail"]:
            hits.add(lg["path"])
    for s in ev["submit"]:
        hits.add(s["path"])
    ev["hit_files"] = sorted(hits)
    return res


def _agg_logs(ev, field):
    out = []
    for lg in ev["logs"]:
        vals = lg.get(field) or []
        if isinstance(vals, list):
            for v in vals:
                out.append((lg["path"], v))
    return out


def _decide(ev, wall):
    """判定优先级见模块 docstring c 段。"""
    def out(status, cls, decision, unknown_kind=None):
        return {"status": status, "class": cls, "decision": decision,
                "unknown_kind": unknown_kind}

    norms = [v["norm"] for v in ev["verdicts"]]
    has_pass = "PASS" in norms
    has_fail = "FAIL" in norms
    has_err = "ERROR" in norms

    # ---- tier1 结构化判定（最可信）
    if has_pass and not has_fail:
        return out("PASS", None, "tier1_pass_verdict")
    if has_fail:
        cls, why = classify_fail(ev)
        if has_pass:      # 同一 case 既有 pass 又有 fail 字段：保守判 FAIL
            return out("FAIL", cls, "tier1_mixed_verdict_worst_wins: " + why)
        return out("FAIL", cls, "tier1_fail_verdict: " + why)
    if has_err:
        cls, why = classify_error(ev, wall)
        return out("ERROR", cls, "tier1_error_verdict: " + why)

    # ---- tier2 文本标记（strong 优先；weak 只做兜底但会打 coverage 警告）
    sp = sum(lg.get("strong_pass", 0) for lg in ev["logs"])
    sf = sum(lg.get("strong_fail", 0) for lg in ev["logs"])
    p_n = sum(lg["pass"] for lg in ev["logs"])
    f_n = sum(lg["fail"] for lg in ev["logs"])
    e_n = sum(lg["error"] for lg in ev["logs"])
    if sf:
        cls, why = classify_fail(ev)
        return out("FAIL", cls,
                   "tier2_strong_fail_markers(fail=%d,strong=%d,pass=%d): %s"
                   % (f_n, sf, p_n, why))
    if sp:
        return out("PASS", None,
                   "tier2_strong_pass_markers(pass=%d,strong=%d)" % (p_n, sp))
    if f_n:
        cls, why = classify_fail(ev)
        return out("FAIL", cls,
                   "tier2_weak_fail_markers(fail=%d,strong=0,pass=%d): %s"
                   % (f_n, p_n, why))
    if p_n:
        return out("PASS", None, "tier2_weak_pass_markers(pass=%d)" % p_n)
    if e_n:
        # 崩溃型错误（Traceback / 非 0 退出）语义上属于候选脚本失败，
        # 只有 infra/timeout 签名才升级成 ERROR
        has_rt = bool(_agg_logs(ev, "runtime_sig"))
        has_infra = bool(_agg_logs(ev, "infra"))
        has_tmo = bool(_agg_logs(ev, "timeout")) or (
            wall is not None and wall >= TIMEOUT_WALL_SEC)
        if has_rt and not (has_infra or has_tmo):
            cls, why = classify_fail(ev)
            return out("FAIL", cls,
                       "tier2_runtime_error_marks_candidate_failure(err=%d): %s"
                       % (e_n, why))
        cls, why = classify_error(ev, wall)
        return out("ERROR", cls, "tier2_error_markers(err=%d): %s" % (e_n, why))

    # ---- 无任何判定标记：靠 wall / 交付物兜底
    if wall is not None and wall >= TIMEOUT_WALL_SEC:
        return out("ERROR", "ERROR_TIMEOUT",
                   "wall_ge_%.0fs_no_verdict" % TIMEOUT_WALL_SEC)
    if ev["submit"]:
        return out("FAIL", "UNKNOWN", "no_judgment_evidence_but_submit",
                   unknown_kind="NO_VERDICT_BUT_SUBMIT")
    return out("FAIL", "UNKNOWN", "no_judgment_evidence_no_submit",
               unknown_kind="NO_EVIDENCE_AT_ALL")


def classify_fail(ev):
    """FAIL 细分。返回 (class, 一句话理由)，理由进 summary 便于人工核验。

    优先级（越靠前越硬）：
      NO_SUBMIT > FORMAT_CONTRACT > ASSERT_RUNTIME > ASSERT_ANTIHARDCODE
      > ASSERT_SEMANTIC > UNKNOWN
    理由：runtime 失败说明候选脚本没跑完，语义比较不成立；anti-hardcode 是
    "语义不符"里更具体的子情形（hidden B 失败），故排在 SEMANTIC 之前。
    """
    submits = ev["submit"]
    if not submits:
        return "NO_SUBMIT", "case 目录内无 submit.zip / submit/ 交付物"

    # 有 submit 但 zip 打不开 / 空 zip / 空目录：真实机器检查，压过任何日志文本
    for s in submits:
        if s.get("kind") == "file" and s.get("openable") is False:
            return "FORMAT_CONTRACT", "submit 打不开: %s (%s)" % (
                s["path"], s.get("issue"))
        if s.get("issue") == "empty_zip":
            return "FORMAT_CONTRACT", "submit 是空 zip: %s" % s["path"]
        if s.get("issue") == "empty_submit_dir":
            return "FORMAT_CONTRACT", "submit 目录为空: %s" % s["path"]

    fmt = _agg_logs(ev, "format_sig")
    if fmt:
        return "FORMAT_CONTRACT", "日志签名: %s @%s" % (fmt[0][1], fmt[0][0])

    rt = _agg_logs(ev, "runtime_sig")
    if rt:
        return "ASSERT_RUNTIME", "日志签名: %s @%s" % (rt[0][1], rt[0][0])

    hid = _agg_logs(ev, "hidden_fail")
    a_ok = _agg_logs(ev, "a_pass")
    if hid and a_ok:
        return "ASSERT_ANTIHARDCODE", "A 通过但 hidden/B 失败: %s @%s" % (
            hid[0][1], hid[0][0])

    conds = []
    for lg in ev["logs"]:
        for c in lg.get("fail_conditions") or []:
            conds.append((lg["path"], c))
    if conds:
        ids = sorted(set(c for _, c in conds))
        return "ASSERT_SEMANTIC", "失败条件编号 %s @%s" % (
            ",".join(ids[:8]), conds[0][0])

    return "UNKNOWN", "有 submit 且无任何可核验的失败信号"


def classify_error(ev, wall):
    """ERROR 细分：先超时（2400s 最硬），再基础设施，再 UNKNOWN。"""
    if wall is not None and wall >= TIMEOUT_WALL_SEC:
        return "ERROR_TIMEOUT", "wall=%.1fs >= %.0fs" % (wall, TIMEOUT_WALL_SEC)
    tmo = _agg_logs(ev, "timeout")
    if tmo:
        return "ERROR_TIMEOUT", "日志签名: %s @%s" % (tmo[0][1], tmo[0][0])
    infra = _agg_logs(ev, "infra")
    if infra:
        return "ERROR_INFRA", "日志签名: %s @%s" % (infra[0][1], infra[0][0])
    return "UNKNOWN", "有 ERROR 标记但无 infra/timeout 签名"


# ------------------------------------------------------------------ 聚合
def aggregate(records):
    """整体 + 逐域 status 矩阵、失败类别分布、coverage、unknown 比例。"""
    counts = dict((s, 0) for s in STATUSES)
    class_counts = dict((c, 0) for c in CLASS_ORDER)
    unknown_kinds = {}
    per_domain = {}
    judged = 0
    warnings = []
    weak = []
    wall_max = None

    for r in records:
        dom = r["domain"] or "unknown"
        d = per_domain.setdefault(dom, {
            "status": dict((s, 0) for s in STATUSES),
            "class": dict((c, 0) for c in CLASS_ORDER),
            "total": 0,
        })
        counts[r["status"]] += 1
        d["status"][r["status"]] += 1
        d["total"] += 1
        if r["class"]:
            class_counts[r["class"]] = class_counts.get(r["class"], 0) + 1
            d["class"][r["class"]] = d["class"].get(r["class"], 0) + 1
        if r.get("unknown_kind"):
            unknown_kinds[r["unknown_kind"]] = \
                unknown_kinds.get(r["unknown_kind"], 0) + 1
        if r["coverage"]["judgment_evidence"]:
            judged += 1
            if r["coverage"].get("warning"):
                weak.append({"task_id": r["task_id"], "domain": dom,
                             "class": r["class"],
                             "decision": r["decision"],
                             "warning": r["coverage"]["warning"],
                             "case_dir": r["evidence"]["case_dir"]})
        elif r["coverage"].get("warning"):
            warnings.append({"task_id": r["task_id"], "domain": dom,
                             "class": r["class"],
                             "warning": r["coverage"]["warning"],
                             "case_dir": r["evidence"]["case_dir"]})
        w = r.get("wall_sec")
        if w is not None and (wall_max is None or w > wall_max):
            wall_max = w

    total = sum(counts.values())
    decided = counts["PASS"] + counts["FAIL"]
    fail_err = counts["FAIL"] + counts["ERROR"]
    # PASS 也进 class 统计，保证 class 分布与 status 矩阵可对账
    class_counts["PASS"] = counts["PASS"]
    return {
        "total": total,
        "counts": counts,
        "class_counts": class_counts,
        "unknown_kinds": unknown_kinds,
        "per_domain": per_domain,
        "coverage": {
            "judged_cases": judged,
            "total": total,
            "judged_ratio_pct": round(pct(judged, total), 2),
            "judged_over_nonabsent_pct": round(
                pct(judged, total - counts["ABSENT"]), 2),
            "warnings": warnings,
            "weak_marker_count": len(weak),
            "weak_marker_warnings": weak,
        },
        "unknown_ratio": {
            "unknown_count": class_counts.get("UNKNOWN", 0),
            "denominator_fail_error": fail_err,
            "unknown_over_fail_error": round(
                pct(class_counts.get("UNKNOWN", 0), fail_err), 2),
            "unknown_over_total": round(
                pct(class_counts.get("UNKNOWN", 0), total), 2),
        },
        "pass_rate": {
            "pass_over_pass_fail": round(pct(counts["PASS"], decided), 2),
            "pass_over_pass_fail_num": counts["PASS"],
            "pass_over_pass_fail_den": decided,
            "pass_over_non_absent": round(
                pct(counts["PASS"], total - counts["ABSENT"]), 2),
            "pass_over_total": round(pct(counts["PASS"], total), 2),
        },
        "wall_max_sec": wall_max,
    }


# ------------------------------------------------------------------ 输出
def _tex_escape(s):
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("#", r"\#"), ("_", r"\_"), ("$", r"\$")):
        s = s.replace(a, b)
    return s


def _tex_path(s):
    return str(s).replace("\\", "/")


def write_tex_status(path, agg, meta):
    """booktabs 状态矩阵：Domain / PASS / FAIL / ERROR / ABSENT / Total / Pass%"""
    per = agg["per_domain"]
    lines = [
        "% auto-generated by 05_batch_triage.py v" + VERSION
        + " -- do not edit by hand",
        "%% batch: %s" % _tex_path(meta["batch_dir"]),
        "%% cases: %s" % _tex_path(meta["cases_jsonl"]),
        "% Pass\\% = PASS/(PASS+FAIL). 全批次参考: 62/620 = 10.0%, "
        "62/626 = 9.9%, 62/696 = 8.9%.",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Domain & PASS & FAIL & ERROR & ABSENT & Total & Pass\% \\",
        r"\midrule",
    ]
    for dom in sorted(per):
        st = per[dom]["status"]
        lines.append("%s & %d & %d & %d & %d & %d & %.1f \\\\" % (
            _tex_escape(dom), st["PASS"], st["FAIL"], st["ERROR"],
            st["ABSENT"], per[dom]["total"],
            pct(st["PASS"], st["PASS"] + st["FAIL"])))
    c = agg["counts"]
    lines += [
        r"\midrule",
        (r"\textbf{Total} & \textbf{%d} & \textbf{%d} & \textbf{%d} & "
         r"\textbf{%d} & \textbf{%d} & \textbf{%.1f} \\"
         % (c["PASS"], c["FAIL"], c["ERROR"], c["ABSENT"], agg["total"],
            agg["pass_rate"]["pass_over_pass_fail"])),
        r"\bottomrule",
        r"\end{tabular}",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_tex_failure(path, agg, meta):
    """booktabs 失败类别分布（逐域）。UNKNOWN 单列，绝不并入其他类。"""
    per = agg["per_domain"]
    cols = ["ERROR_TIMEOUT", "ERROR_INFRA", "NO_SUBMIT", "FORMAT_CONTRACT",
            "ASSERT_RUNTIME", "ASSERT_SEMANTIC", "ASSERT_ANTIHARDCODE",
            "UNKNOWN"]
    short = ["TO", "INFRA", "NOSUB", "FMT", "RT", "SEM", "ANTI", "UNK"]
    lines = [
        "% auto-generated by 05_batch_triage.py v" + VERSION
        + " -- do not edit by hand",
        "%% batch: %s" % _tex_path(meta["batch_dir"]),
        "% 列缩写: TO=ERROR_TIMEOUT INFRA=ERROR_INFRA NOSUB=NO_SUBMIT "
        "FMT=FORMAT_CONTRACT RT=ASSERT_RUNTIME SEM=ASSERT_SEMANTIC "
        "ANTI=ASSERT_ANTIHARDCODE UNK=UNKNOWN",
        "% F+E = FAIL+ERROR 合计; UNKNOWN 已单列，不并入其他类",
        "% 若超出版心，整表用 \\resizebox{\\columnwidth}{!}{ ... } 包裹",
        r"\begin{tabular}{l" + "r" * (len(cols) + 1) + "}",
        r"\toprule",
        "Domain & " + " & ".join(short) + r" & F+E \\",
        r"\midrule",
    ]
    for dom in sorted(per):
        cl = per[dom]["class"]
        st = per[dom]["status"]
        vals = [str(cl.get(c, 0)) for c in cols]
        lines.append("%s & %s & %d \\\\" % (
            _tex_escape(dom), " & ".join(vals), st["FAIL"] + st["ERROR"]))
    cc = agg["class_counts"]
    c = agg["counts"]
    lines += [
        r"\midrule",
        (r"\textbf{Total} & "
         + " & ".join(r"\textbf{%d}" % cc.get(k, 0) for k in cols)
         + r" & \textbf{%d} \\" % (c["FAIL"] + c["ERROR"])),
        r"\bottomrule",
        r"\end{tabular}",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _md_row(cells):
    return "| " + " | ".join(str(c) for c in cells) + " |"


def write_report_md(path, agg, meta, records, samples, extra_notes):
    per = agg["per_domain"]
    c = agg["counts"]
    pr = agg["pass_rate"]
    ur = agg["unknown_ratio"]
    cov = agg["coverage"]
    L = []
    L.append("# Batch failure triage — %s" % meta["batch_name"])
    L.append("")
    L.append("> 由 `05_batch_triage.py` v%s 自动生成（%s）。所有判定都带证据路径，"
             "可直接回查。" % (VERSION, meta["generated_at"]))
    L.append("")
    L.append("## 1. 输入与发现")
    L.append("")
    L.append("- batch 目录: `%s`" % _tex_path(meta["batch_dir"]))
    L.append("- cases jsonl: `%s`（%d 条，id 键=`%s`，domain 键=`%s`）"
             % (_tex_path(meta["cases_jsonl"]), meta["n_cases"],
                meta["cases_info"]["id_key"],
                meta["cases_info"]["domain_key"] or "(无此键)"))
    L.append("- domain 来源: `%s`" % meta["cases_info"]["domain_source"])
    L.append("- 目录布局命中: %s"
             % (", ".join("`%s`x%d" % (r, h) for r, h in
                          meta["index_stats"]["layout_roots"])
                or "（退化全树扫描）"))
    L.append("- 找到 case 目录 %d/%d；缺失 %d（判为 ABSENT）"
             % (meta["index_stats"]["found"], meta["index_stats"]["total"],
                len(meta["index_stats"]["missing"])))
    if meta["index_stats"]["ambiguous"]:
        L.append("- ⚠️ 同名 case 目录多处出现（取第一个）：%s"
                 % ", ".join(sorted(meta["index_stats"]["ambiguous"])[:10]))
    L.append("")
    L.append("## 2. 总体结果")
    L.append("")
    L.append(_md_row(["PASS", "FAIL", "ERROR", "ABSENT", "Total"]))
    L.append(_md_row(["---"] * 5))
    L.append(_md_row([c["PASS"], c["FAIL"], c["ERROR"], c["ABSENT"],
                      agg["total"]]))
    L.append("")
    L.append("- **Pass%%（本工具口径）= PASS/(PASS+FAIL) = %d/%d = %.2f%%**"
             % (pr["pass_over_pass_fail_num"], pr["pass_over_pass_fail_den"],
                pr["pass_over_pass_fail"]))
    L.append("- PASS/(PASS+FAIL+ERROR) = %d/%d = %.2f%%（ERROR 记 non-pass）"
             % (c["PASS"], pr["pass_over_pass_fail_den"] + c["ERROR"],
                pct(c["PASS"], pr["pass_over_pass_fail_den"] + c["ERROR"])))
    L.append("- PASS/非 ABSENT = %d/%d = %.2f%%"
             % (c["PASS"], agg["total"] - c["ABSENT"],
                pr["pass_over_non_absent"]))
    L.append("- PASS/Total = %d/%d = %.2f%%"
             % (c["PASS"], agg["total"], pr["pass_over_total"]))
    L.append("- Ground-truth 对照（2026-11-09 全量批次）：62 PASS / 558 FAIL / "
             "70 ERROR / 6 ABSENT / 696，即 62/620 = 10.0%、62/626 = 9.9%。"
             "若本报告计数与之一致，说明目录发现与判定口径都对得上。")
    L.append("")
    L.append("## 3. 逐域状态矩阵")
    L.append("")
    L.append(_md_row(["Domain", "PASS", "FAIL", "ERROR", "ABSENT", "Total",
                      "Pass%"]))
    L.append(_md_row(["---"] * 7))
    for dom in sorted(per):
        st = per[dom]["status"]
        L.append(_md_row([dom, st["PASS"], st["FAIL"], st["ERROR"],
                          st["ABSENT"], per[dom]["total"],
                          "%.1f" % pct(st["PASS"], st["PASS"] + st["FAIL"])]))
    L.append(_md_row(["**Total**", c["PASS"], c["FAIL"], c["ERROR"],
                      c["ABSENT"], agg["total"],
                      "%.1f" % pr["pass_over_pass_fail"]]))
    L.append("")


    L.append("## 4. 失败类别分布（FAIL + ERROR 细分）")
    L.append("")
    L.append(_md_row(["Class", "Count", "% of FAIL+ERROR"]))
    L.append(_md_row(["---", "---", "---"]))
    for cls in CLASS_ORDER:
        if cls == "PASS":
            continue
        n = agg["class_counts"].get(cls, 0)
        if not n:
            continue
        L.append(_md_row([cls, n,
                          "%.1f" % pct(n, ur["denominator_fail_error"])]))
    L.append("")
    top = sorted(((k, v) for k, v in agg["class_counts"].items()
                  if k != "PASS" and v), key=lambda kv: (-kv[1], kv[0]))[:3]
    L.append("Top 3: %s" % (", ".join("%s=%d" % (k, v) for k, v in top)
                            or "（无）"))
    L.append("")
    L.append("## 5. UNKNOWN 与 coverage（显式披露，不藏进别的类）")
    L.append("")
    L.append("- UNKNOWN = %d 例，占 FAIL+ERROR 的 **%.2f%%**（%d/%d），"
             "占全批 %.2f%%"
             % (ur["unknown_count"], ur["unknown_over_fail_error"],
                ur["unknown_count"], ur["denominator_fail_error"],
                ur["unknown_over_total"]))
    if agg["unknown_kinds"]:
        L.append("- UNKNOWN 构成: %s"
                 % ", ".join("%s=%d" % (k, v) for k, v in
                             sorted(agg["unknown_kinds"].items())))
    L.append("- coverage：找到判分证据的 case = %d/%d = %.2f%%"
             "（非 ABSENT 口径 %.2f%%）"
             % (cov["judged_cases"], cov["total"], cov["judged_ratio_pct"],
                cov["judged_over_nonabsent_pct"]))
    if cov["warnings"]:
        L.append("- ⚠️ coverage_warning：%d 例无判分证据（全部清单见 "
                 "triage_summary.json 的 coverage.warnings）"
                 % len(cov["warnings"]))
        for w in cov["warnings"][:5]:
            L.append("  - `%s` (%s, %s): %s"
                     % (w["task_id"], w["domain"], w["class"], w["warning"]))
    else:
        L.append("- coverage_warning：无（每个非 ABSENT case 都找到了判分证据）")
    if cov.get("weak_marker_count"):
        L.append("- ⚠️ 弱标记 case：%d 例只用弱标记（非判定行出现 PASS/FAIL 字样）"
                 "判定，建议抽样复核（清单见 triage_summary.json 的 "
                 "coverage.weak_marker_warnings）" % cov["weak_marker_count"])
    L.append("")
    if extra_notes:
        L.append("## 6. 运行告警")
        L.append("")
        for n in extra_notes:
            L.append("- " + n)
        L.append("")
    L.append("## 7. 随机抽样 case 的证据路径（%d 例，seed=%d）"
             % (len(samples), meta["seed"]))
    L.append("")
    for s in samples:
        L.append("### `%s` — %s / %s" % (s["task_id"], s["status"],
                                         s["class"] or "-"))
        L.append("")
        L.append("- 判定依据: `%s`" % s["decision"])
        L.append("- wall: %s s" % (s.get("wall_sec")
                                   if s.get("wall_sec") is not None else "n/a"))
        L.append("- case 目录: `%s`"
                 % (s["evidence"]["case_dir"] or "(不存在 → ABSENT)"))
        ev = s["evidence"]
        if ev["verdicts"]:
            L.append("- tier1 结构化判定: %s" % ", ".join(
                "`%s`:%s=%s→%s" % (v["path"], v["key"], v["value"], v["norm"])
                for v in ev["verdicts"][:4]))
        if ev["logs"]:
            L.append("- tier2 日志摘要: %s" % ", ".join(
                "`%s`(pass=%d,fail=%d,err=%d)" % (l["path"], l["pass"],
                                                  l["fail"], l["error"])
                for l in ev["logs"][:4]))
        if ev["submit"]:
            L.append("- tier3 交付物: %s" % ", ".join(
                "`%s`(openable=%s,entries=%s,issue=%s)"
                % (x["path"], x.get("openable"), x.get("entries"),
                   x.get("issue")) for x in ev["submit"][:3]))
        L.append("- 证据文件清单: %s"
                 % (", ".join("`%s`" % p for p in ev["hit_files"][:6])
                    or "（无）"))
        if s["coverage"].get("warning"):
            L.append("- ⚠️ " + s["coverage"]["warning"])
        L.append("")
    L.append("## 8. 复现命令")
    L.append("")
    L.append("```bash")
    L.append(meta["repro_command"])
    L.append("```")
    L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ------------------------------------------------------------------ 主流程
def _write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:      # utf-8 无 BOM
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")


def _pick_samples(records, k, seed):
    """从 FAIL/ERROR 里随机抽 k 例（不足则补 PASS/ABSENT），固定 seed 可复现。"""
    pool = [r for r in records if r["status"] in ("FAIL", "ERROR")]
    rest = [r for r in records if r["status"] not in ("FAIL", "ERROR")]
    rnd = random.Random(seed)
    picks = rnd.sample(pool, min(k, len(pool)))
    if len(picks) < k:
        picks += rnd.sample(rest, min(k - len(picks), len(rest)))
    return sorted(picks, key=lambda r: r["task_id"])


def run_pipeline(ns):
    """完整流水线：load_cases → 目录发现 → 逐 case 归因 → 聚合 → 落盘。"""
    t0 = time.time()
    # 保留原始输入字符串：Windows 上 abspath 会把 Linux 路径变成 D:\nasdata\...
    # 报错时给用户看他输入的东西，另附解析后的绝对路径
    batch_raw = ns.batch or ""
    cases_raw = ns.cases or ""
    batch_dir = os.path.abspath(batch_raw) if batch_raw else ""
    cases_path = os.path.abspath(cases_raw) if cases_raw else ""

    if not batch_raw:
        die("必须提供 --batch <RUN_DIR>")
    if not os.path.isdir(batch_raw):
        die("批次目录不存在或不是目录: %s" % batch_raw
            + ("" if os.path.abspath(batch_raw) == batch_raw
               else "（解析为 %s）" % os.path.abspath(batch_raw)),
            hint=("集群上先确认 RUN_DIR 拼写（形如 "
                  ".../eval/run_batch_20261109_171201）；本工具不做路径猜测。"),
            probe='ls -ld "<RUN_DIR>"; ls "<RUN_DIR>" | head -20; '
                  'find "<RUN_DIR>" -maxdepth 2 | head -50')

    all_cases, cases_info = load_cases(cases_raw)

    if ns.domain_alias:
        if not os.path.isfile(ns.domain_alias):
            die("--domain-alias 文件不存在: %s" % ns.domain_alias)
        try:
            with open(ns.domain_alias, "r", encoding="utf-8") as f:
                amap = json.load(f)
            if not isinstance(amap, dict):
                raise ValueError("映射文件必须是 JSON object")
        except (ValueError, OSError) as exc:
            die("--domain-alias 解析失败: %s" % exc)
        mapped = 0
        for r in all_cases:
            if r["domain"] in amap:
                r["domain"] = str(amap[r["domain"]])
                mapped += 1
        eprint("[triage] --domain-alias: %d/%d 条 domain 已按映射归一"
               % (mapped, len(all_cases)))
    selected = all_cases[:ns.limit] if ns.limit else all_cases
    if ns.limit:
        eprint("[triage] --limit %d：只处理前 %d 例（用于探结构）"
               % (ns.limit, len(selected)))

    index, istats = build_case_index(
        batch_dir, [r["task_id"] for r in selected],
        layout=ns.layout, case_glob=ns.case_glob, max_depth=ns.max_depth)

    notes = []
    found_ratio = pct(istats["found"], istats["total"])
    if istats["found"] == 0:
        notes.append("0 个 case 目录命中 → 目录布局与假设不符。")
        eprint("[triage][ERROR] 在 %s 下没找到任何 case 目录。" % batch_dir)
        eprint(LAYOUT_HINT)
        if not ns.dry_run:
            # 不做"全 ABSENT/全 UNKNOWN"的假报告：直接报错退出
            die("0 个 case 目录命中，拒绝产出空报告（--out 未写入任何文件）",
                hint=LAYOUT_HINT)
    elif found_ratio < 60.0:
        notes.append("只有 %d/%d (%.1f%%) 的 case 目录命中；其余记为 ABSENT。"
                     % (istats["found"], istats["total"], found_ratio))
        eprint("[triage][WARN] 只命中 %d/%d (%.1f%%) 的 case 目录。"
               % (istats["found"], istats["total"], found_ratio))
        eprint(LAYOUT_HINT)
    if cases_info["duplicate_ids"]:
        notes.append("cases jsonl 有重复 id %d 个（保留首条）：%s"
                     % (len(cases_info["duplicate_ids"]),
                        ", ".join(cases_info["duplicate_ids"][:5])))
    if cases_info["missing_domain"]:
        notes.append("cases jsonl 有 %d 条 domain 为空（该条按 task_id 推域）：%s"
                     % (len(cases_info["missing_domain"]),
                        ", ".join(cases_info["missing_domain"][:5])))
    if cases_info.get("domain_source") == "derived_from_task_id":
        notes.append("cases jsonl 没有 domain 类键 → 逐域统计用 task_id 前缀推导"
                     "（EDA-Eval-DesignFlow-<Domain>-<NNN> → <Domain>）；"
                     "若需官方域标签，请用带 domain 字段的 cases 文件复核。")

    records = []
    n = len(selected)
    for i, rec in enumerate(selected, 1):
        cdir = index.get(rec["task_id"])
        res = discover_case(cdir, batch_dir)
        row = {
            "task_id": rec["task_id"],
            "domain": rec["domain"],
            "status": res["status"],
            "class": res["class"],
            "unknown_kind": res["unknown_kind"],
            "decision": res["decision"],
            "wall_sec": res["wall_sec"],
            "coverage": res["coverage"],
            "evidence": res["evidence"],
        }
        records.append(row)
        if ns.dry_run:
            print("[%3d/%3d] %-38s status=%-6s class=%-18s %s"
                  % (i, n, rec["task_id"][:38], res["status"],
                     res["class"] or "-", res["decision"][:90]))
            print("          case_dir=%s" % (res["evidence"]["case_dir"]
                                             or "(missing -> ABSENT)"))
            print("          evidence=%s" % (", ".join(
                res["evidence"]["hit_files"][:6]) or "(none)"))
            if res["coverage"].get("warning"):
                print("          WARN=%s" % res["coverage"]["warning"])
        elif not ns.quiet and (i % 50 == 0 or i == n):
            eprint("[triage] %d/%d 已归因 (%.1fs)"
                   % (i, n, time.time() - t0))

    agg = aggregate(records)
    meta = {
        "tool": "05_batch_triage.py",
        "version": VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "elapsed_sec": round(time.time() - t0, 2),
        "batch_dir": batch_dir,
        "batch_name": os.path.basename(batch_dir.rstrip(os.sep)) or batch_dir,
        "cases_jsonl": cases_path,
        "n_cases": len(selected),
        "n_cases_in_file": len(all_cases),
        "cases_info": {k: cases_info[k] for k in
                       ("id_key", "domain_key", "text_key", "domain_source",
                        "duplicate_ids", "missing_domain")},
        "layout": ns.layout,
        "case_glob": ns.case_glob,
        "domain_alias": ns.domain_alias,
        "index_stats": istats,
        "seed": ns.seed,
        "timeout_wall_sec": TIMEOUT_WALL_SEC,
        "pass_rate": agg["pass_rate"],
        "pass_rate_note": ("Pass% = PASS/(PASS+FAIL); 全批次参考 62/620=10.0%, "
                           "62/626=9.9%, 62/696=8.9%"),
        "notes": notes,
        "repro_command": "python3 05_batch_triage.py "
                         + " ".join(sys.argv[1:]),
    }

    if ns.dry_run:
        print("")
        print("=" * 78)
        print("DRY-RUN 汇总（未写任何文件）")
        print("  batch        : %s" % batch_dir)
        print("  cases        : %s (%d 条)" % (cases_path, len(all_cases)))
        print("  布局命中     : %s"
              % (", ".join("%s x%d" % (r, h) for r, h in
                           istats["layout_roots"]) or "(全树退化扫描)"))
        print("  status       : %s" % (agg["counts"],))
        print("  Pass%%(P/F)   : %.2f%% (%d/%d)"
              % (agg["pass_rate"]["pass_over_pass_fail"],
                 agg["pass_rate"]["pass_over_pass_fail_num"],
                 agg["pass_rate"]["pass_over_pass_fail_den"]))
        print("  coverage     : %d/%d 找到判分证据 (%.2f%%)"
              % (agg["coverage"]["judged_cases"], agg["total"],
                 agg["coverage"]["judged_ratio_pct"]))
        print("  UNKNOWN      : %d (%.2f%% of FAIL+ERROR)"
              % (agg["unknown_ratio"]["unknown_count"],
                 agg["unknown_ratio"]["unknown_over_fail_error"]))
        print("  classes      : %s"
              % (", ".join("%s=%d" % (k, v) for k, v in
                           agg["class_counts"].items() if v) or "(none)"))
        for a in notes:
            print("  WARN         : %s" % a)
        print("=" * 78)
        return {"agg": agg, "records": records, "meta": meta, "notes": notes,
                "written": []}

    # ---- 落盘
    out_dir = os.path.abspath(ns.out)
    tables_dir = os.path.join(out_dir, "tables")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        die("无法创建输出目录 %s: %s" % (out_dir, exc),
            hint="检查 --out 的权限；集群上应指向仓库内 results/ 目录")

    samples = _pick_samples(records, 10, ns.seed)
    summary = {
        "tool": {"name": "05_batch_triage.py", "version": VERSION},
        "meta": meta,
        "overall": {
            "total": agg["total"],
            "counts": agg["counts"],
            "pass_rate": agg["pass_rate"],
            "unknown_ratio": agg["unknown_ratio"],
            "unknown_kinds": agg["unknown_kinds"],
            "wall_max_sec": agg["wall_max_sec"],
        },
        "class_order": CLASS_ORDER,
        "failure_classes": agg["class_counts"],
        "domains": agg["per_domain"],
        "coverage": agg["coverage"],
        "notes": notes,
        "cases": records,
    }
    written = []
    p = os.path.join(out_dir, "triage_summary.json")
    _write_json(p, summary)
    written.append(p)

    if not ns.json_only or ns.emit_tex:
        if not os.path.isdir(tables_dir):
            os.makedirs(tables_dir, exist_ok=True)
        p = os.path.join(tables_dir, "status_by_domain.tex")
        write_tex_status(p, agg, meta)
        written.append(p)
        p = os.path.join(tables_dir, "failure_by_domain.tex")
        write_tex_failure(p, agg, meta)
        written.append(p)
    if not ns.json_only:
        p = os.path.join(out_dir, "report.md")
        write_report_md(p, agg, meta, records, samples, notes)
        written.append(p)

    print("[triage] 结果: PASS=%d FAIL=%d ERROR=%d ABSENT=%d total=%d"
          % (agg["counts"]["PASS"], agg["counts"]["FAIL"],
             agg["counts"]["ERROR"], agg["counts"]["ABSENT"], agg["total"]))
    print("[triage] Pass%%(PASS/(PASS+FAIL)) = %.2f%% (%d/%d); "
          "PASS/全批 = %.2f%%"
          % (agg["pass_rate"]["pass_over_pass_fail"],
             agg["pass_rate"]["pass_over_pass_fail_num"],
             agg["pass_rate"]["pass_over_pass_fail_den"],
             agg["pass_rate"]["pass_over_total"]))
    print("[triage] coverage=%d/%d (%.2f%%), UNKNOWN=%d (%.2f%% of FAIL+ERROR)"
          % (agg["coverage"]["judged_cases"], agg["total"],
             agg["coverage"]["judged_ratio_pct"],
             agg["unknown_ratio"]["unknown_count"],
             agg["unknown_ratio"]["unknown_over_fail_error"]))
    for a in notes:
        eprint("[triage][NOTE] " + a)
    print("[triage] 写出 %d 个文件:" % len(written))
    for w in written:
        print("    " + w)
    return {"agg": agg, "records": records, "meta": meta, "notes": notes,
            "written": written}


# ------------------------------------------------------------------ selftest
def _ws(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _mkzip(path, names=("impl.tcl",)):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        for n in names:
            zf.writestr(n, "# dummy payload\n")


def _build_fixture(root):
    """合成批次：12 case / 4 域 / 覆盖每个 FAIL 子类 + ERROR + ABSENT + 无证据。

    目录布局故意混搭（flat + cases/ + w3/），用来验证 auto 发现：
      RUN/<id>          C01..C04
      RUN/cases/<id>    C05..C08
      RUN/w3/<id>       C10..C12
      C09 完全不建目录 → ABSENT
    """
    run = os.path.join(root, "run_batch_selftest")
    os.makedirs(run, exist_ok=True)
    D = "EDA-Eval-DesignFlow-"
    ids = {
        "C01": D + "Digital-001", "C02": D + "Digital-002",
        "C03": D + "Digital-003", "C04": D + "Analog-001",
        "C05": D + "Analog-002", "C06": D + "Analog-003",
        "C07": D + "Virtuoso-001", "C08": D + "Virtuoso-002",
        "C09": D + "Virtuoso-003", "C10": D + "Verif-001",
        "C11": D + "Verif-002", "C12": D + "Verif-003",
    }
    doms = {"C01": "digital", "C02": "digital", "C03": "digital",
            "C04": "analog", "C05": "analog", "C06": "analog",
            "C07": "layout_virtuoso", "C08": "layout_virtuoso",
            "C09": "layout_virtuoso", "C10": "verification",
            "C11": "verification", "C12": "verification"}

    def cd(key):
        if key in ("C01", "C02", "C03", "C04"):
            return os.path.join(run, ids[key])
        if key in ("C05", "C06", "C07", "C08"):
            return os.path.join(run, "cases", ids[key])
        return os.path.join(run, "w3", ids[key])

    # C01 PASS：tier1 判定 json + 合法 submit
    _ws(os.path.join(cd("C01"), "judge_result.json"),
        json.dumps({"pass": True, "score": 1.0, "reason": "all conditions met"}))
    _mkzip(os.path.join(cd("C01"), "submit.zip"))
    _ws(os.path.join(cd("C01"), "check.log"), "PASS: all 5 conditions met\n")

    # C02 FAIL / ASSERT_SEMANTIC：tier1 false + 失败条件编号
    _ws(os.path.join(cd("C02"), "judge_result.json"),
        json.dumps({"pass": False, "reason": "condition mismatch"}))
    _mkzip(os.path.join(cd("C02"), "submit.zip"))
    _ws(os.path.join(cd("C02"), "check.log"),
        "checking outputs ...\nFAIL: condition 3 not met (expected 1.2, got 1.4)\n")

    # C03 FAIL / ASSERT_ANTIHARDCODE：A 通过、hidden B 失败
    _mkzip(os.path.join(cd("C03"), "submit.zip"))
    _ws(os.path.join(cd("C03"), "check.log"),
        "visible case A: PASS (conditions 1-4 ok)\n"
        "hidden case B: FAIL mismatch on port count\n")

    # C04 ERROR / ERROR_TIMEOUT：wall 2512s + timed out
    _ws(os.path.join(cd("C04"), "run.log"),
        "wall: 2512.3s elapsed\nERROR: command timed out after 2400s\n")

    # C05 ERROR / ERROR_INFRA：MCP 网关断连
    _ws(os.path.join(cd("C05"), "run.log"),
        "ERROR MCP gateway: connection refused (ECONNRESET) from api proxy\n")

    # C06 FAIL / NO_SUBMIT：有 FAIL 判定、无交付物
    _ws(os.path.join(cd("C06"), "judge.log"),
        "FAIL: no submission found for this case\n")

    # C07 FAIL / FORMAT_CONTRACT：submit.zip 是坏的
    _ws(os.path.join(cd("C07"), "submit.zip"), "this is definitely not a zip")
    _ws(os.path.join(cd("C07"), "judge.log"),
        "FAIL: cannot open zip: BadZipFile\n")

    # C08 FAIL / ASSERT_RUNTIME：候选脚本非 0 退出
    _mkzip(os.path.join(cd("C08"), "submit.zip"))
    _ws(os.path.join(cd("C08"), "runner.log"),
        "Traceback (most recent call last):\n"
        "  File \"impl.py\", line 7, in <module>\n"
        "subprocess returncode 1\n"
        "FAIL: candidate script exited with error\n")

    # C09 ABSENT：不建目录

    # C10 PASS：嵌套 results/verdict.json
    _ws(os.path.join(cd("C10"), "results", "verdict.json"),
        json.dumps({"verdict": "pass", "checks": {"1": True}}))
    _mkzip(os.path.join(cd("C10"), "submit.zip"))

    # C11 FAIL / UNKNOWN：只有 submit，无判分证据 → coverage_warning
    _mkzip(os.path.join(cd("C11"), "submit.zip"))

    # C12 FAIL / UNKNOWN：空目录，什么都不给
    os.makedirs(cd("C12"), exist_ok=True)

    lines = []
    for key in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
                "C09", "C10", "C11", "C12"):
        lines.append(json.dumps({"task_id": ids[key], "domain": doms[key],
                                 "task": "synthetic case " + key},
                                ensure_ascii=False))
    cases = os.path.join(root, "cases.jsonl")
    _ws(cases, "\n".join(lines) + "\n")
    return {"run": run, "cases": cases, "ids": ids, "domains": doms}


def _ns(**kw):
    base = dict(batch=None, cases=None, out=None, dry_run=False,
                emit_tex=False, json_only=False, layout="auto",
                case_glob=None, limit=0, seed=20261109, quiet=True,
                max_depth=4, domain_alias=None)
    base.update(kw)
    return argparse.Namespace(**base)


def selftest():
    """合成 fixture → 跑完整流水线 → 断言精确计数与 tex 内容。

    任何一条失败都会打印 FAIL 行，最后返回 1；全通过打印 ALL SELFTEST PASSED。
    """
    failures = []
    checks = [0]

    def check(cond, label, detail=""):
        checks[0] += 1
        if cond:
            print("PASS: %s%s" % (label, ("  [%s]" % detail) if detail else ""))
        else:
            print("FAIL: %s%s" % (label, ("  [%s]" % detail) if detail else ""))
            failures.append(label)

    def eq(got, want, label):
        check(got == want, label, "got=%r want=%r" % (got, want))

    root = tempfile.mkdtemp(prefix="triage_selftest_")
    try:
        fx = _build_fixture(root)
        out_dir = os.path.join(root, "out")

        # ---------- 1. 完整流水线 ----------
        with contextlib.redirect_stdout(io.StringIO()) as quiet:
            res = run_pipeline(_ns(batch=fx["run"], cases=fx["cases"],
                                   out=out_dir, emit_tex=True))
        agg = res["agg"]
        recs = dict((r["task_id"], r) for r in res["records"])
        ids = fx["ids"]

        print("---- 1. status 计数 ----")
        eq(agg["total"], 12, "case 总数 = 12")
        eq(agg["counts"], {"PASS": 2, "FAIL": 7, "ERROR": 2, "ABSENT": 1},
           "status 矩阵 = 2 PASS / 7 FAIL / 2 ERROR / 1 ABSENT")
        eq(agg["pass_rate"]["pass_over_pass_fail_den"], 9,
           "Pass%(PASS+FAIL) 分母 = 9")
        eq(round(agg["pass_rate"]["pass_over_pass_fail"], 1), 22.2,
           "Pass%(PASS+FAIL) = 22.2")

        print("---- 2. 逐 case 判定与类别 ----")
        expect = {
            "C01": ("PASS", None),
            "C02": ("FAIL", "ASSERT_SEMANTIC"),
            "C03": ("FAIL", "ASSERT_ANTIHARDCODE"),
            "C04": ("ERROR", "ERROR_TIMEOUT"),
            "C05": ("ERROR", "ERROR_INFRA"),
            "C06": ("FAIL", "NO_SUBMIT"),
            "C07": ("FAIL", "FORMAT_CONTRACT"),
            "C08": ("FAIL", "ASSERT_RUNTIME"),
            "C09": ("ABSENT", None),
            "C10": ("PASS", None),
            "C11": ("FAIL", "UNKNOWN"),
            "C12": ("FAIL", "UNKNOWN"),
        }
        for key in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
                    "C09", "C10", "C11", "C12"):
            st, cls = expect[key]
            r = recs[ids[key]]
            eq((r["status"], r["class"]), (st, cls),
               "%s → %s/%s" % (key, st, cls or "-"))

        print("---- 3. 失败类别分布 ----")
        want_cls = {"PASS": 2, "ERROR_TIMEOUT": 1, "ERROR_INFRA": 1,
                    "NO_SUBMIT": 1, "FORMAT_CONTRACT": 1, "ASSERT_RUNTIME": 1,
                    "ASSERT_SEMANTIC": 1, "ASSERT_ANTIHARDCODE": 1,
                    "UNKNOWN": 2}
        eq(agg["class_counts"], want_cls, "class 分布精确匹配")
        eq(sum(v for k, v in agg["class_counts"].items() if k != "PASS"), 9,
           "FAIL+ERROR 合计 = 9")

        print("---- 4. UNKNOWN 比例与 coverage ----")
        eq(agg["unknown_ratio"]["unknown_count"], 2, "UNKNOWN 计数 = 2")
        eq(round(agg["unknown_ratio"]["unknown_over_fail_error"], 1), 22.2,
           "UNKNOWN/FAIL+ERROR = 22.2%")
        eq(agg["coverage"]["judged_cases"], 9, "找到判分证据的 case = 9")
        eq(round(agg["coverage"]["judged_ratio_pct"], 1), 75.0,
           "coverage = 75.0%")
        eq(len(agg["coverage"]["warnings"]), 2, "coverage_warning 2 条")
        eq(recs[ids["C11"]]["unknown_kind"], "NO_VERDICT_BUT_SUBMIT",
           "C11 unknown_kind = NO_VERDICT_BUT_SUBMIT")
        eq(recs[ids["C12"]]["unknown_kind"], "NO_EVIDENCE_AT_ALL",
           "C12 unknown_kind = NO_EVIDENCE_AT_ALL")
        eq(recs[ids["C09"]]["evidence"]["case_dir"] is None, True,
           "C09 ABSENT 无 case_dir")

        print("---- 5. 证据路径可复核 ----")
        check(any("judge_result.json" in p
                  for p in recs[ids["C01"]]["evidence"]["hit_files"]),
              "C01 证据含 judge_result.json")
        check(any("check.log" in p
                  for p in recs[ids["C02"]]["evidence"]["hit_files"]),
              "C02 证据含 check.log")
        eq(recs[ids["C02"]]["evidence"]["logs"][0]["fail_conditions"], ["3"],
           "C02 失败条件编号 = ['3']")
        eq(recs[ids["C04"]]["status"], "ERROR", "C04 无 submit 仍判 ERROR")
        check(recs[ids["C04"]]["wall_sec"] is not None
              and round(recs[ids["C04"]]["wall_sec"], 1) == 2512.3,
              "C04 wall = 2512.3s", recs[ids["C04"]]["wall_sec"])
        eq(recs[ids["C07"]]["evidence"]["submit"][0]["openable"], False,
           "C07 submit.zip 机器检查为打不开")
        eq(recs[ids["C07"]]["class"], "FORMAT_CONTRACT",
           "C07 坏 zip → FORMAT_CONTRACT")
        eq(recs[ids["C08"]]["evidence"]["logs"][0]["runtime_sig"] != [], True,
           "C08 有 runtime 签名证据")

        print("---- 6. 逐域矩阵 ----")
        per = agg["per_domain"]
        eq(per["digital"]["status"],
           {"PASS": 1, "FAIL": 2, "ERROR": 0, "ABSENT": 0}, "digital = 1P/2F")
        eq(per["analog"]["status"],
           {"PASS": 0, "FAIL": 1, "ERROR": 2, "ABSENT": 0}, "analog = 1F/2E")
        eq(per["layout_virtuoso"]["status"],
           {"PASS": 0, "FAIL": 2, "ERROR": 0, "ABSENT": 1},
           "layout_virtuoso = 2F/1A")
        eq(per["verification"]["status"],
           {"PASS": 1, "FAIL": 2, "ERROR": 0, "ABSENT": 0},
           "verification = 1P/2F")

        print("---- 7. 输出文件与 tex 内容 ----")
        p_json = os.path.join(out_dir, "triage_summary.json")
        p_tex_s = os.path.join(out_dir, "tables", "status_by_domain.tex")
        p_tex_f = os.path.join(out_dir, "tables", "failure_by_domain.tex")
        p_md = os.path.join(out_dir, "report.md")
        for p in (p_json, p_tex_s, p_tex_f, p_md):
            check(os.path.isfile(p), "生成 %s" % p.replace(root, "<tmp>"))
        with open(p_json, "r", encoding="utf-8") as f:
            summ = json.load(f)
        eq(len(summ["cases"]), 12, "summary.json 含 12 个 case")
        eq(summ["overall"]["counts"]["PASS"], 2, "summary.json PASS = 2")
        eq(summ["coverage"]["judged_cases"], 9, "summary.json coverage = 9")
        missing_cls = [r["task_id"] for r in summ["cases"]
                       if r["status"] in ("FAIL", "ERROR") and not r["class"]]
        eq(missing_cls, [], "所有 FAIL/ERROR case 都有 class")

        with open(p_tex_s, "r", encoding="utf-8") as f:
            tex_s = f.read()
        for row in ("digital & 1 & 2 & 0 & 0 & 3 & 33.3 \\\\",
                    "analog & 0 & 1 & 2 & 0 & 3 & 0.0 \\\\",
                    "layout\\_virtuoso & 0 & 2 & 0 & 1 & 3 & 0.0 \\\\",
                    "verification & 1 & 2 & 0 & 0 & 3 & 33.3 \\\\",
                    "\\textbf{Total} & \\textbf{2} & \\textbf{7} & "
                    "\\textbf{2} & \\textbf{1} & \\textbf{12} & "
                    "\\textbf{22.2} \\\\"):
            check(row in tex_s, "status tex 含行[%s]" % row[:40])
        check("62/626 = 9.9%" in tex_s, "status tex 注释含 62/626 = 9.9% 口径")
        check("\\toprule" in tex_s and "\\bottomrule" in tex_s,
              "status tex 是 booktabs 风格")

        with open(p_tex_f, "r", encoding="utf-8") as f:
            tex_f = f.read()
        for row in ("digital & 0 & 0 & 0 & 0 & 0 & 1 & 1 & 0 & 2 \\\\",
                    "analog & 1 & 1 & 1 & 0 & 0 & 0 & 0 & 0 & 3 \\\\",
                    "layout\\_virtuoso & 0 & 0 & 0 & 1 & 1 & 0 & 0 & 0 & 2 \\\\",
                    "verification & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 2 & 2 \\\\",
                    "\\textbf{Total} & \\textbf{1} & \\textbf{1} & "
                    "\\textbf{1} & \\textbf{1} & \\textbf{1} & "
                    "\\textbf{1} & \\textbf{1} & \\textbf{2} & "
                    "\\textbf{9} \\\\"):
            check(row in tex_f, "failure tex 含行[%s]" % row[:40])

        with open(p_md, "r", encoding="utf-8") as f:
            md = f.read()
        check("## 5. UNKNOWN 与 coverage" in md, "report.md 有 UNKNOWN 披露段")
        check("62/626 = 9.9%" in md, "report.md 有 62/626 口径对照")
        eq(md.count("### `"), 10, "report.md 抽样 10 例")
        check("seed=20261109" in md, "report.md 标注 seed 可复现")


        print("---- 8. 确定性与 dry-run 不落盘 ----")
        out2 = os.path.join(root, "out2")
        with contextlib.redirect_stdout(io.StringIO()):
            res2 = run_pipeline(_ns(batch=fx["run"], cases=fx["cases"],
                                    out=out2))
        eq(res2["agg"]["counts"], agg["counts"], "二次运行计数一致（确定性）")
        eq(res2["agg"]["class_counts"], agg["class_counts"],
           "二次运行 class 分布一致")
        dry_out = os.path.join(root, "dry_out")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_pipeline(_ns(batch=fx["run"], cases=fx["cases"],
                             out=dry_out, dry_run=True))
        dry_txt = buf.getvalue()
        check("DRY-RUN 汇总（未写任何文件）" in dry_txt, "--dry-run 打印汇总")
        check("case_dir=" in dry_txt and "evidence=" in dry_txt,
              "--dry-run 打印每个 case 的证据路径")
        check(not os.path.isdir(dry_out), "--dry-run 未创建输出目录")

        print("---- 9. json-only / emit-tex 组合 ----")
        out3 = os.path.join(root, "out3")
        with contextlib.redirect_stdout(io.StringIO()):
            run_pipeline(_ns(batch=fx["run"], cases=fx["cases"], out=out3,
                             json_only=True))
        check(os.path.isfile(os.path.join(out3, "triage_summary.json")),
              "--json-only 写 summary.json")
        check(not os.path.isfile(os.path.join(out3, "report.md")),
              "--json-only 不写 report.md")
        check(not os.path.isdir(os.path.join(out3, "tables")),
              "--json-only 不写 tex")
        out4 = os.path.join(root, "out4")
        with contextlib.redirect_stdout(io.StringIO()):
            run_pipeline(_ns(batch=fx["run"], cases=fx["cases"], out=out4,
                             json_only=True, emit_tex=True))
        check(os.path.isfile(os.path.join(out4, "tables",
                                          "status_by_domain.tex")),
              "--json-only --emit-tex 仍写 tex")

        print("---- 10. 键名探测 / 错误友好性 ----")
        alias_cases = os.path.join(root, "alias.jsonl")
        _ws(alias_cases, "\n".join(json.dumps(x) for x in [
            {"id": "A-1", "category": "digital", "instruction": "x"},
            {"id": "A-2", "category": "analog", "instruction": "y"},
        ]) + "\n")
        recs2, info2 = load_cases(alias_cases)
        eq((info2["id_key"], info2["domain_key"]), ("id", "category"),
           "自动探测 id/category 键")
        eq([r["task_id"] for r in recs2], ["A-1", "A-2"], "别名 cases 解析正确")

        no_id = os.path.join(root, "no_id.jsonl")
        _ws(no_id, json.dumps({"foo": 1}) + "\n")
        err1 = io.StringIO()
        try:
            with contextlib.redirect_stderr(err1):
                load_cases(no_id)
            check(False, "缺 id 键应报错")
        except SystemExit as exc:
            eq(exc.code, 2, "缺 id 键退出码 = 2")
        check("找不到 id 键" in err1.getvalue() and "顶层键" in err1.getvalue(),
              "缺 id 键的报错说清了试过的键名与可用键")

        err2 = io.StringIO()
        try:
            with contextlib.redirect_stderr(err2):
                build_case_index(os.path.join(root, "nope"), ["x"])
            check(False, "不存在的 batch 目录应报错")
        except SystemExit as exc:
            eq(exc.code, 2, "不存在的 batch 目录退出码 = 2")
        check("批次目录不存在" in err2.getvalue()
              and "find" in err2.getvalue(),
              "不存在的 batch 目录报错带探针命令")

        print("---- 11. 强/弱标记与 prompt 噪声抑制 ----")
        prompt_like = os.path.join(root, "prompt.txt")
        _ws(prompt_like, "If the check fails, retry; report PASS or FAIL per case.\n")
        th = scan_text_file(prompt_like, "prompt.txt", count_markers=False)
        eq((th.pass_n, th.fail_n), (0, 0),
           "prompt/任务描述不计 PASS/FAIL 标记（不污染判分）")
        check(STRONG_FAIL_RE.search("if the result fails, retry") is None,
              "散文里的 'fails' 不算强 FAIL 标记")
        check(STRONG_FAIL_RE.search("FAIL: condition 3 not met") is not None,
              "'FAIL: ...' 算强 FAIL 标记")
        check(STRONG_PASS_RE.search("PASS: all 5 conditions met") is not None,
              "'PASS: ...' 算强 PASS 标记")

        print("")
        print("---- selftest 统计 ----")
        print("检查项: %d, 失败: %d" % (checks[0], len(failures)))
        if failures:
            for f in failures:
                print("FAILED CHECK: %s" % f)
            print("SELFTEST FAILED")
            return 1
        print("ALL SELFTEST PASSED")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ------------------------------------------------------------------ CLI
def build_parser():
    ap = argparse.ArgumentParser(
        prog="05_batch_triage.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="全量评测批次失败归因（stdlib-only, py3.8+）。"
                    "先 --dry-run 探结构，再正式跑。")
    ap.add_argument("--batch", help="批次 run dir，如 "
                                    ".../eval/run_batch_20261109_171201")
    ap.add_argument("--cases", help="EDA-Eval-DesignFlow.jsonl 绝对路径")
    ap.add_argument("--out", help="输出目录（建议仓库内 results/）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只打印发现结果与每个 case 的证据路径，不写任何文件")
    ap.add_argument("--emit-tex", action="store_true",
                    help="显式要求 booktabs tex 表（默认写；与 --json-only "
                         "同时给出时仍写 tex）")
    ap.add_argument("--json-only", action="store_true",
                    help="只写 triage_summary.json（不写 report.md/tex）")
    ap.add_argument("--layout", default="auto",
                    choices=["auto", "flat", "nested", "shard"],
                    help="case 目录布局：flat=RUN/<id>，nested=RUN/cases/<id>，"
                         "shard=RUN/<worker_N>/<id>，auto=依次尝试+全树退化")
    ap.add_argument("--case-glob", default=None,
                    help="自定义模板，如 '<RUN_DIR>/*/{task_id}'；{task_id} "
                         "会被替换（仅最后一级为通配）")
    ap.add_argument("--max-depth", type=int, default=4,
                    help="全树退化扫描的深度上限（默认 4）")
    ap.add_argument("--domain-alias", default=None,
                    help="可选 JSON 映射文件，把推导出的 domain 名归一成论文里的"
                         " 13 个域标签，如 {\"PnRSignoff\": \"pnr_signoff\"}")
    ap.add_argument("--limit", type=int, default=0,
                    help="只处理前 N 例（探结构用）")
    ap.add_argument("--seed", type=int, default=20261109,
                    help="report.md 抽样随机种子（默认 20261109）")
    ap.add_argument("--quiet", action="store_true", help="关掉进度输出")
    ap.add_argument("--selftest", action="store_true",
                    help="跑合成 fixture 的端到端自测（不需要集群）")
    return ap


def main(argv=None):
    ap = build_parser()
    ns = ap.parse_args(argv)
    if ns.selftest:
        return selftest()
    missing = [k for k in ("batch", "cases", "out") if not getattr(ns, k)]
    if missing:
        ap.print_help()
        eprint("")
        die("缺少必需参数: %s" % ", ".join("--" + m for m in missing),
            hint="示例: python3 05_batch_triage.py --batch <RUN_DIR> "
                 "--cases <EDA-Eval-DesignFlow.jsonl> --out results/ "
                 "--dry-run")
    run_pipeline(ns)
    return 0


if __name__ == "__main__":
    sys.exit(main())
