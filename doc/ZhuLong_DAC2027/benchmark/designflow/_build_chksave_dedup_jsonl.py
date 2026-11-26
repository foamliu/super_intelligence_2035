#!/usr/bin/env python3
"""Build the jsonl entry for EDA-Eval-DesignFlow-ChkSaveHistDedup-001 and append
to EDA-Eval-DesignFlow_C.jsonl (idempotent — skips if task_id already present)."""
import json
import os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
CASE = "EDA-Eval-DesignFlow-ChkSaveHistDedup-001"
JSONL = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "EDA-Eval-DesignFlow_C.jsonl")
REF = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "reference", CASE)

# idempotency
existing = []
if os.path.isfile(JSONL):
    for line in open(JSONL, encoding="utf-8"):
        existing.append(json.loads(line))
if any(e["task_id"] == CASE for e in existing):
    print("already present, skipping")
    raise SystemExit(0)

with open(os.path.join(REF, "check.py"), encoding="utf-8") as f:
    check_src = f.read()

prompt = """你是版图工程师 zqzhan，在 Aether/CXMT 环境里维护版图 cellview 的「Custom Check and Save」流程。现象（用户原话要点）：对 layout cellview 做 check save，但是看 log 只有 save —— CIW 里确实打印了 `Custom Check and Save function called`（说明 check 真跑了），但 cellview 的 save-history 审计文件 `.hist` 里只看到之前的 `Save` 记录，看不到 `Checkandsave` 条目，导致审计上看像 check 没执行。

你已定位到根因在 `CXMTutAddSaveHistory`（位于 `CXMThiSHBarIconRemap.il`）里的一段**去重逻辑**：它读 `.hist` 最后一行作为 `prior`，当 `prior.user == 当前 user` 且 `delta = 当前时间 - prior.time < time_interval`（layout 的 `time_interval = 600` 秒）时，把本次写入**抑制**（`flag = nil`）。问题：这个去重条件**只比 user + 时间差，不看操作类型 comm**，所以「同一用户 10 分钟内先 Save 后 Check and Save」时，Checkandsave 被 prior 的 Save 抑制 —— `.hist` 只剩 Save，审计失真。debug 症状原文：`Debug: not print user sczhang,sczhang, time delta 171, 2026/10/20 10:57:21	2026/10/20 10:54:30.`（delta 171s < 600s 被抑制）。

修复方案 B：在去重条件里**加 `pcomm == comm`**，并从最后一行捕获 `pcomm = nth(...)` —— 只有「同一用户 + 同一操作类型 + 时间差 < interval」才抑制；不同操作类型互不抑制（Save 不再抑制 Checkandsave）。

## 沙盒注（L1 占位）
在线 Aether + CXMT SKILL 引擎在评测沙盒不可达，故不要求真跑 Aether。请完成**确定性子任务**：写一个纯 Python3（仅标准库）离线诊断 + 补丁工具 `chk_save_hist_dedup.py`，读 `.hist` 日志 + 一组新操作，模拟去重守卫、分类每个操作的结局、并输出修正后的 SKILL 补丁片段。不调任何 EDA 工具。

### `.hist` 文件格式（6 字段，空白分隔）
```
<lib>  <cell>  <view>  <user>  <timestamp>  <comm>
```
- `timestamp`：`Mon_DD_HH:MM:SS_YYYY`，例 `Oct_20_12:37:46_2026`（月份 3 字母英文缩写、日零填充、24h 时分秒、年）。SKILL 里用 `buildString(parseString(nth(...) "_") " ")` 还原成 `Oct 20 12:37:46 2026` 再 `compareTime` 解析。
- `comm` ∈ {`Save`, `Checkandsave`, `schCheck`, `dbSave`}。
- 去重守卫只读 `.hist` 的**最后一行**（跳过 `#` 注释行与空行）作为 `prior`。

### 去重守卫（要同时模拟「 buggy 」与「 fixed 」两版）
- **BUGGY（原始，comm-blind）**：`if prior.user == op.user and delta < time_interval -> SUPPRESSED`，否则 `WRITTEN`。
- **FIXED（方案B，comm-aware）**：`if prior.user == op.user and prior.comm == op.comm and delta < time_interval -> SUPPRESSED`，否则 `WRITTEN`。
- `delta = op.ctime_epoch - prior.epoch`（秒）。时间一律换算成 epoch（用 UTC，`calendar.timegm` 即可，避免时区漂移）。

### 每个新操作的分类（diagnosis）
- `bug_triggered`：BUGGY 判 SUPPRESSED 但 FIXED 判 WRITTEN（comm-blind 把不同类型的操作误抑制了 —— 这就是本问题）。
- `correct_dedup`：两版都 SUPPRESSED（同 user + 同 comm + 最近，正确去重，不是 bug）。
- `delta_exceeded`：两版都 WRITTEN 且因 `delta >= time_interval`（间隔太久不去重）。
- `different_user`：两版都 WRITTEN 且因 `prior.user != op.user`。
- `no_prior`：`.hist` 无最后一行，两版都 WRITTEN。
- `written`：其它两版都 WRITTEN 的情况。

### 修正后的 SKILL 补丁（patch）
输出**修正版**（方案B）的关键片段，必须包含：
- `let` 变量列表里出现 `pcomm`；
- 从最后一行捕获 `pcomm = nth(...)`；
- 去重条件为 `puser == username && ptime && pcomm == comm`（**不是** buggy 的 `puser == username && ptime`）。

### CLI
```
python3 chk_save_hist_dedup.py --hist <histfile> --ops <ops.json> --interval <sec> --out <report.json>
```
`ops.json` 是一个 JSON 数组，每个元素 `{"user":..., "comm":..., "ctime":"Mon_DD_HH:MM:SS_YYYY"}`。

### 输出 `report.json` 字段
- `tool` = `"chk_save_hist_dedup"`、`version`、`interval_sec`；
- `prior`：解析出的最后一行 `{lib, cell, view, user, timestamp, comm, epoch}`（无则 `null`）；
- `per_op[]`：每个 op 给 `{user, comm, ctime, ctime_epoch, delta_sec, prior_user_match, prior_comm_match, decision_buggy, decision_fixed, diagnosis}`；
- `patch`：修正后的 SKILL 片段字符串。

## 交付
把 `chk_save_hist_dedup.py` 打包成 `outputs/submit.zip`（内含这一个 `.py` 文件）。约束：纯标准库，不引第三方包，不调任何 EDA 工具，全本地可跑，确定性（同输入多次运行结果 byte 一致）。"""

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-ChkSaveHistDedup-001/hist_A.log",
        "assets/EDA-Eval-DesignFlow-ChkSaveHistDedup-001/ops_A.json",
        "assets/EDA-Eval-DesignFlow-ChkSaveHistDedup-001/task_brief.md",
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["outputs/submit.zip"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "zqzhan",
            "host": "hfeg0pkn005",
            "session_file": "1792463960005_7frw8.messages.json",
            "match_count": 371,
            "real_task_summary": "Aether/CXMT Custom Check-and-Save .hist 审计失真诊断（zqzhan, hfeg0pkn005, 7frw8 session, layout_aether 域）：用户报告对 layout cellview 做 check save 但 .hist 只看到 Save、看不到 Checkandsave。trace 5 轮真实迭代：search/read CXMTseCustomCheckAndSave.il + CXMThiSHBarIconRemap.il→定位根因=CXMTutAddSaveHistory 去重逻辑只比 puser==username && delta<time_interval(600s)，不看 comm→同一用户 10min 内先 Save 后 Check and Save 时 Checkandsave 被抑制→.hist 只剩 Save（debug 原文 'not print user sczhang,sczhang, time delta 171'）。修复方案B：去重条件加 pcomm==comm + 捕获 pcomm=nth(5 tmp_s)→不同操作类型互不抑制。UI#6 用户接受：log 显示 'drcpa_digital R_trimSanpDlyA_LP schematic sczhang Oct_20_12:37:46_2026 Checkandsave'。本 case 把『.hist 6字段解析+epoch+BUGGY(comm-blind)vsFIXED(comm-aware)双守卫模拟+per-op诊断(bug_triggered/correct_dedup/delta_exceeded/different_user)+方案B SKILL补丁』合成成离线 chk_save_hist_dedup.py，核心坑=comm-blind 去重把不同类型操作误抑制（bug_triggered vs correct_dedup 必须区分）。",
        },
        "domain": "layout_aether",
        "track": "synthesized",
        "level": "L1-boundary",
        "test_rationale": "15 条断言：①zip恰1个.py≥800B+UTF-8无NUL+py_compile通过 ②CLI --hist/--ops/--interval/--out在隐藏B上exit0+合法JSON+报告含tool/version/interval_sec/prior/per_op/patch六键 ③prior解析正确:最后一行{lib=drcpa_digital,cell=INVx4,view=layout,user=sczhang,timestamp=Oct_20_12:37:46_2026,comm=Checkandsave} ④timestamp epoch正确(UTC calendar.timegm):prior.epoch与per_op[0].ctime_epoch与check独立重算一致 ⑤delta_sec正确:op#0=134s,op#2=734s ⑥BUGGY守卫(comm-blind)op#0(Save,同user,delta134<600)判SUPPRESSED ⑦FIXED守卫(comm-aware)op#0(prior.comm=Checkandsave≠Save)判WRITTEN ⑧op#0 diagnosis==bug_triggered(buggy SUPPRESS+fixed WRITTEN=comm-blind误抑制) ⑨op#1(Checkandsave,同comm,delta254<600)两版都SUPPRESS且diagnosis==correct_dedup(同comm去重不是bug,naive'全抑制即bug'工具FAIL) ⑩op#2(Save,delta734>=600)两版都WRITTEN且diagnosis==delta_exceeded(间隔太久不去重,always-suppress stub FAIL) ⑪op#3(wang5≠sczhang)两版都WRITTEN且diagnosis==different_user(不同用户不去重) ⑫patch含pcomm变量+`pcomm==comm`条件+`pcomm=nth(...)`捕获且无buggy的when(puser==username&&ptime)无pcomm子句(=方案B修正版非buggy版) ⑬交叉输入守卫A:prior.user=li1wen+prior.comm=Save+op#0 bug_triggered且A输出不泄露B-only token(sczhang/INVx4/drcpa_digital/wang5)证非硬编码B ⑭交叉输入守卫B2:prior.user=zqzhan+op#0 bug_triggered且B2报告≠B报告证非print-only ⑮确定性:隐藏B同输入3跑byte-identical",
    },
}

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended:", CASE)
print("jsonl_C lines now:", sum(1 for _ in open(JSONL, encoding="utf-8")))
