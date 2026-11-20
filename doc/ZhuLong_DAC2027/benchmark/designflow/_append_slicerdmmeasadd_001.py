#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SlicerDmMeasAdd-001 to B.jsonl (shard B spice_sim)."""
import json, os, re

CASE = "EDA-Eval-DesignFlow-SlicerDmMeasAdd-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BASE, "reference", CASE)
AST = os.path.join(BASE, "assets", CASE)

with open(os.path.join(REF, "check.py"), "r") as f:
    check_src = f.read()
with open(os.path.join(AST, "prompt.txt"), "r") as f:
    prompt = f.read().strip()

attachments = [
    "assets/%s/prompt.txt" % CASE,
    "assets/%s/task_brief.md" % CASE,
    "assets/%s/strongarm_tb_cm.sp" % CASE,
]

test_rationale = (
    "12 条断言：①(a)submit.zip 合法且含 add_dm_meas.py 且 py_compile 通过 "
    "②(b)候选 --help 正常打印用法且 exit 0 "
    "③(c)在可见 A(strongarm_tb_cm.sp)上生成 *_cmdm.sp 文件且行数 > 源 .sp 行数(确有新增内容) "
    "④(d)输出保留原始 5 条 CM measure 名(inp_cur_cm/pmos_cur_cm/nmos_cur_cm/inp_volt_cm/out_volt_cm 仍在,未破坏源测量) "
    "⑤(e)输出含全部 5 条 DM measure 名(inp_cur_dm/pmos_cur_dm/nmos_cur_dm/inp_volt_dm/out_volt_dm) "
    "⑥(f)DM 电流测量沿用源 .sp 的 .mp1/.mn1 子电路实例语法(DM 电流行含 .mp1 或 .mn1,非重写为其他) "
    "⑦(g)DM 测量不使用 .d 语法(DM measure 行不含 .d 设备语法——trace 中用户曾纠正 .d 应为 .mp1/.mn1) "
    "⑧(h)DM 表达式为差分:含 '-' 且 DM 行与对应 CM 行不同(非把 CM 求和复制为 DM) "
    "⑨(i)DM 块插入在 CM 块之后(最后一条 DM measure 行号 > 最后一条 CM measure 行号) "
    "⑩(j)DM 测量为 .meas tran 形式且至少 5 条 "
    "⑪(k)L2 真跑:HSPICE 在隐藏 B 生成的 _cmdm.sp 上 subprocess 执行得 'job concluded' 且无 **error**/abort/syntax error "
    "⑫(l)跨输入护栏:B 输出引用 B 的实例 xcmp 与网 vp/vn/qp/qn 且不含 A 的 xslicer(证明候选从 CM measure 泛化提取实例名,非硬编码 A)。"
    "§4.9 三假(empty/print_expected/ref-core-deleted)经自验均 FAIL;5 个 negative(empty/print_expected/hardcode_a/copy_cm/use_dot_d)经 negative_selftest 全 FAIL 且首失败标签互异。"
)

metadata = {
    "domain": "spice_sim",
    "track": "faithful",
    "layer": "L2",
    "k_check": 12,
    "k_rationale": 12,
    "trace_source": {
        "user": "jiangbaol",
        "host": "hfeg0pkn002",
        "session_file": "1793932002608_suauw.messages.json",
        "match_count": 113,
        "real_task_summary": (
            "jiangbaol @ hfeg0pkn002 的 cline session 1793932002608_suauw(113 msgs, "
            "spice_sim, mtime 2026-11-06 NEW——写入于 11-05 19:28 重扫快照之后,本轮 11-06 "
            "经 .75 run_commands 对 fresh summary.tsv 的 42 个 host 定向重扫(threshold "
            "2026-11-05 19:28:00)发现 111 NEW sessions 后筛出)。USER#11 verbatim A 档"
            "「/proj/dscqa/V0_LP6/.../004_onlySlicer_delay_dejoa_test_cm.sp 该.sp已添加了"
            "共模电流与共模电压,在此基础上添加差模电流及差模电压」(纯需求轮,未指出根因/未给"
            "修复→A 档可用)。assistant read_files 源 .sp(strongarm,已有 CM I/V 测量)→editor "
            "写 add_dm.sh(拷贝源 .sp→在 out_cm_avg measure 后插入 5 条差模 probe+measure,用 "
            ".mp1(PMOS)/.mn1(NMOS)子电路实例语法,用户曾纠正 .d 应为 .mp1/.mn1)→run_approved "
            "执行生成 004_onlySlicer_delay_dejoa_test_cmdm.sp(288→302 行,+14 行)→USER#31 回 "
            "「compact」接受。金标准=trace 末尾用户接受的 _cmdm.sp(5 条 DM measure,+.→-. 差分"
            "变换)。本 case 取 verbatim A 档需求,合成金标准:通用 add_dm_meas.py 读已有 CM "
            "measure(.meas tran <base>_cm param='<+expr>')→插入 <base>_dm param='<-expr>' "
            "DM 块(.mp1/.mn1 语法)→写 _cmdm.sp。A=strongarm stub(xslicer/inp/inn/outp/outn);"
            "hidden B=doubletail stub(xcmp/vp/vn/qp/qn,不同拓扑/实例名→强制泛化)。.75 HSPICE "
            "真跑 A/B 生成的 _cmdm.sp 均 job concluded 且 5 条 DM measure 打印数值。"
        ),
    },
    "test_rationale": test_rationale,
    "layer_rationale": (
        "L2 真跑沙盒 HSPICE:check.py 在候选于隐藏 B 源 deck 生成的 _cmdm.sp 上 subprocess "
        "调 hspice,断言 'job concluded' 且无 **error**/abort/syntax error(证明生成的 deck "
        "电气可仿真,非纯文本拼接);并跨输入护栏 B 引用 xcmp 非 A 的 xslicer。非离线 Python 复刻。"
    ),
}

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["add_dm_meas.py"],
    "test": check_src,
    "budget": {"max_turns": 20},
    "metadata": metadata,
}

# idempotency: remove any prior entry with same task_id
jsonl = os.path.join(BASE, "EDA-Eval-DesignFlow_B.jsonl")
lines = []
if os.path.exists(jsonl):
    with open(jsonl, "r") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                o = json.loads(ln)
            except Exception:
                lines.append(ln); continue
            if o.get("task_id") == CASE:
                continue  # drop prior
            lines.append(ln)
lines.append(json.dumps(entry, ensure_ascii=False))
with open(jsonl, "w") as f:
    for ln in lines:
        f.write(ln + "\n")
print("appended", CASE, "-> total lines:", len(lines))

# assert gate
n = len(re.findall(r'[①-⑯]', test_rationale))
print("circled-count =", n, "k_check =", metadata["k_check"],
      "startswith_ok =", test_rationale.startswith("12 条断言："),
      "GATE_PASS =", (n == metadata["k_check"] == 12 and n >= 8))
