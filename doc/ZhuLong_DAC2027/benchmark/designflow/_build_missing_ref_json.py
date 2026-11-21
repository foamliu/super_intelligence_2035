#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the case JSON for EDA-Eval-DesignFlow-MissingRefDiagnose-001 and append
to EDA-Eval-DesignFlow_B.jsonl."""
import os, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-MissingRefDiagnose-001"
ASSET = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)

check_src = open(os.path.join(REF, "check.py")).read()

attachments = [
    "assets/%s/task_brief.md" % CASE,
    "assets/%s/deck_A.sp" % CASE,
    "assets/%s/netlist_A.sp" % CASE,
    "assets/%s/error_log_A.txt" % CASE,
    "assets/%s/model_lib_A/model.lib" % CASE,
    "assets/%s/model_lib_A/model_setup_fs.lib" % CASE,
    "assets/%s/model_lib_A/res_fs.mdl" % CASE,
]

prompt = """你在帮同事 t0002607（HuQinyu）排查一个 SRAM 仿真报错。环境是 hfeahpc505 上的 nanospice/HSPICE，PDK 是 lacaa 35H。

## 背景（真实发生的事）
t0002607 跑 HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu 这个 SRAM 的仿真，nanospice 直接 abort，报错只有一行：

```
Error: no reference ckt rm2cb_fs for xi_cds_thru_0  (line 1226)
```

他第一反应是「是不是我 `.lib` 没挂对？」，需要你写一个诊断工具帮他**一次性把根因查清楚**：到底是模型库挂载链断了，还是网表里这个器件引用的模型名在库里压根不存在（笔误）。

## 你要交付的东西
写一个纯 Python（仅标准库）的诊断脚本 `missing_ref_diagnose.py`，命令行用法：

```
python3 missing_ref_diagnose.py <deck.sp> <netlist.sp> <error_log.txt> <model_lib_dir> <out_dir>
```

工具要自动完成下面这一整套排查（这就是当时人工一步步做的事，把它固化成脚本）：

1. **解析报错日志**：从 "no reference ckt <模型名> for <实例名>" 里抽出缺失的模型名和出问题的实例名（大小写不敏感；SPICE 网表里实例名通常大写、报错里可能小写）。
2. **定位实例**：在 netlist 里按实例名找到那一行，记录：行号、连接的节点、master 引用名、参数。
3. **追踪 `.lib` 挂载链**：从 deck 的 `.lib '<file>' <section>` 行开始，递归地打开 model_lib_dir 下的库文件，按 section（`.lib <sec>` … `.endl` 块）提取内容，一路追到最底层的模型定义文件；记录链上每一环（文件名、section、文件是否存在、section 是否找到），判断整条链是否完整。
4. **收集已定义模型名**：在所有被链路实际包含进来的 section 里，grep `.SUBCKT <name>` 和 `.model <name>` 两种定义形式，得到模型库真正提供的模型名集合。
5. **判定根因**：如果链完整但缺失模型名不在已定义集合里 → 根因是「模型名不存在（很可能笔误）」；如果链断了 → 根因是「挂载问题」。
6. **笔误建议**：用编辑距离（Levenshtein）把缺失模型名和所有已定义模型名排序，给出距离最近的 top 建议（这就是当年发现 `rm2cb` 其实是 `rms2cb` 漏了一个 `s` 的逻辑——纯靠模型库本身就能把范围缩小到一两个候选）。
7. **输出**：在 `<out_dir>` 下写 `diagnosis.json`（结构化）和 `diagnosis.txt`（人可读报告），字段至少包含：missing_model、instance、instance_line、instance_nodes、instance_master、instance_params、lib_chain、lib_chain_intact、defined_models、missing_in_defined、suggestions(含 name+distance)、best_suggestion、root_cause、fix。

## 可见输入（A 档，附件里给了）
这就是 t0002607 当时的真实场景：
- `deck_A.sp`：顶层 deck，`.lib './model.lib' tt_res_fs` 挂电阻模型库
- `netlist_A.sp`：网表片段，`HCSP_LEAF_TIEHL_CORNER` 里 `XI_cds_thru_0 TRKWL TRKWL_BCK rm2cb_fs w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res`
- `error_log_A.txt`：nanospice 报错日志
- `model_lib_A/`：三级 `.lib` 链（model.lib → model_setup_fs.lib → res_fs.mdl），res_fs.mdl 里定义了 rm1ca_fs/rm1cb_fs/rms2ca_fs/rms2cb_fs/... 等金属电阻，**但没有 rm2cb_fs**

你的脚本必须能在 A 上跑通并正确诊断出：链完整、rm2cb_fs 不在库中、最接近的候选是 rms2cb_fs（和 rm1cb_fs 并列距离最近）。

## 判分说明
评测会用一组**隐藏输入 B**（不同的网表、不同的实例、不同的模型族、不同的 `.lib` 链、不同的笔误，规模/取值/结构都和 A 不同，不是换个文件名）跑你的脚本，并检查 `diagnosis.json` 的各个字段是否正确。脚本必须通用、不能 hardcode A 的任何具体名字。输出必须确定（同样输入两次结果逐字节一致，且不受 PYTHONHASHSEED 影响）。

把 `missing_ref_diagnose.py` 打包成 `outputs/submit.zip` 提交。
"""

task_brief = """# MissingRefDiagnose-001 — 任务说明（trace-faithful，源自 t0002607 session gpya9）

## 背景（真实用户意图）
用户 t0002607 (HuQinyu) @ hfeahpc505 跑 nanospice 仿真 HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu，
报 "no reference ckt rm2cb_fs for xi_cds_thru_0 (line 1226)"。用户怀疑是 .lib 挂载问题。agent 逐级追踪
.lib 链(model_tt.sp->model.lib tt_res_fs->model_setup_fs.lib res_default/res_tt->res_fs.mdl res)确认链路
完整, grep res_fs.mdl 列出已定义金属电阻(rm1ca/rm1cb/rms2ca/rms2cb/rms3ca/rms3cb/rmx4ca/rmx4cb/rmx5ca/rmx5cb/rmy6~rmy10 _fs),
全版本递归搜 rm2cb 0 命中, 排除挂载问题; 后续 SVS 网表比对时 tiling 版同位置用 rms2cb_fs, 证实 rm2cb 是 rms2cb 笔误(漏 s)。

## 交付
`missing_ref_diagnose.py`：纯标准库 Python，CLI `python3 missing_ref_diagnose.py <deck> <netlist> <error_log> <model_lib_dir> <out_dir>`，
解析 "no reference ckt <name> for <inst>" 错误 → 定位实例(行/节点/master/参数) → section-aware 递归追踪 .lib 链 →
收集 .SUBCKT/.model 定义 → 标记缺失 → Levenshtein 笔误建议 → 输出 diagnosis.json + diagnosis.txt。

## A 档（可见，trace-faithful）
deck_A.sp / netlist_A.sp(rm2cb_fs @ XI_cds_thru_0 in HCSP_LEAF_TIEHL_CORNER) / error_log_A.txt / model_lib_A/(三级 .lib 链 + res_fs.mdl 15 个电阻模型, 无 rm2cb_fs)。

## 隐藏 B（判分用，不在沙箱）
电容族(.model 格式), 异 subckt(HCSP_LEAF_DECOUPLE)/异实例(XCD_cpl0)/异笔误(cm2n_fs→cm2m_fs)/异 .lib 链(cap.lib/cap_setup_fs.lib/cap_fs.mdl)。
"""

trace_source = {
    "user": "t0002607",
    "host": "hfeahpc505",
    "ip": "10.129.33.28",
    "session_file": "1795074929427_gpya9",
    "match_count": 163,
    "scan_snapshot": "ssh_eda_search_20261121_151844/summary.tsv (B fresh list; gpya9 r973 triage peek 取证, r974 合成)",
    "real_task_summary": (
        "用户 t0002607 (HuQinyu) @ hfeahpc505 (session gpya9, mc=163, spice_sim/SRAM netlist debug) 跑 nanospice 仿真 "
        "HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu, 报 'no reference ckt rm2cb_fs for xi_cds_thru_0' "
        "(netlist 1226 行 HCSP_LEAF_TIEHL_CORNER 内 XI_cds_thru_0 TRKWL TRKWL_BCK rm2cb_fs w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res); "
        "agent 逐级追踪 .lib 挂载链(model_tt.sp->model.lib tt_res_fs->model_setup_fs.lib res_default/res_tt->res_fs.mdl res)确认链路完整, "
        "grep res_fs.mdl 列出已定义金属电阻(rm1ca_fs/rm1cb_fs/rms2ca_fs/rms2cb_fs/rms3ca_fs/rms3cb_fs/rmx4ca_fs/rmx4cb_fs/rmx5ca_fs/rmx5cb_fs/rmy6_fs~rmy10_fs), "
        "全版本(/proj/lacaa/TV1_FS/model 下 Rev03~Rev06/SRAM 各版本)递归搜 rm2cb 0 命中, 排除挂载问题; "
        "后续做 SVS 网表比对时 tiling 版网表同位置(HCSP_LEAF_TIEHL_CORNER RI_cds_thru_0)用 rms2cb_fs, 证实 rm2cb 是 rms2cb 笔误(漏 s). "
        "主线交付=诊断结论 + (后续)netcmp.py SVS 比对脚本; 本 case 取诊断主线 reframe."
    ),
}

test_rationale = (
    "15 条断言：①(a) submit.zip 有效且解压后含 missing_ref_diagnose.py ②(b) 脚本在隐藏 B 上以指定 CLI "
    "运行 exit 0 且产出非空可解析的 diagnosis.json ③(c) 两次运行 diagnosis.json 逐字节一致（确定性，禁随机/时间戳）"
    " ④(d) missing_model == cm2n_fs ⑤(e) instance == xcd_cpl0（大小写不敏感）"
    " ⑥(f) instance_line == netlist_B 中 XCD_cpl0 所在行（check 独立重算）⑦(g) instance_nodes 集合 == {vdd,vss} "
    " ⑧(h) instance_master == cm2n_fs 且 instance_params 不少于 2 个 ⑨(i) lib_chain_intact==True 且链长≥3 且 "
    "chain 含 cap.lib/cap_setup_fs.lib/cap_fs.mdl 三个文件且每环 exists ⑩(j) defined_models 含 B 五个 cap 模型"
    "(cm1m~cm5m_fs)且不含 cm2n_fs ⑪(k) missing_in_defined == False ⑫(l) best_suggestion == cm2m_fs 且 cm2m_fs 出现在 suggestions "
    " ⑬(m) 反 hardcode-A：B 诊断序列化后不含任一 A-only token(rm2cb_fs/rms2cb_fs/rm1cb_fs/HCSP_LEAF_TIEHL_CORNER/xi_cds_thru_0/TRKWL/res_fs/rctmod_res/tt_res_fs 等)"
    " ⑭(n) fix 字段非空且引用 cm2m_fs ⑮(o) 三种子 PYTHONHASHSEED=0/1/42 三次运行 diagnosis.json 哈希完全一致"
)

case = {
    "id": CASE,
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "task_brief": task_brief,
    "test": check_src,
    "metadata": {
        "domain": "spice_sim",
        "track": "B",
        "layer": "L1",
        "trace_source": trace_source,
        "test_rationale": test_rationale,
        "k_rationale": 15,
        "k_check": 15,
        "gold_standard": (
            "assistant gpya9 交付: 逐级追踪 .lib 链(model_tt.sp->model.lib tt_res_fs->model_setup_fs.lib "
            "res_default/res_tt->res_fs.mdl res)验证挂载完整, grep res_fs.mdl 列出已定义电阻 subckt(rm1cb_fs/rms2cb_fs/...), "
            "确认 rm2cb_fs 不在库中, 后经 tiling 网表同位置 rms2cb_fs 证实为 typo(漏 s); reframe 为通用 "
            "missing_ref_diagnose.py(读 deck/netlist/error_log/model_lib_dir, 解析 'no reference ckt <name> for <inst>' "
            "错误, 定位实例行/节点/master/参数, section-aware 递归追踪 .lib 链收集 .SUBCKT/.model 定义, Levenshtein "
            "排序给 typo 建议, 输出 diagnosis.json+diagnosis.txt). 参考 missing_ref_diagnose.py."
        ),
        "asset_fidelity": "trace_faithful_spice_libchain_typo_diag",
        "reframe_note": (
            "harness-for-teeth reframe: trace 原意图=诊断 nanospice 'no reference ckt rm2cb_fs for xi_cds_thru_0' "
            "报错(用户问 '是不是.lib挂载问题还是模型不存在'), agent 逐级验 .lib 链+grep res_fs.mdl+跨网表(tiling)印证 "
            "得出 rm2cb 是 rms2cb 的笔误(漏 s); 判分有牙需参数化通用 CLI(任意 netlist/deck/lib 链/模型族/typo), 故 "
            "reframe 成 produce 参数化 missing_ref_diagnose.py, A 档 trace-faithful(用 t0002607 原始 rm2cb_fs/"
            "xi_cds_thru_0/HCSP_LEAF_TIEHL_CORNER/.lib 链/res_fs.mdl 模型集), hidden B 换电容族(.model 格式)/异 subckt/"
            "异实例/异 typo(cm2n_fs→cm2m_fs)/异 .lib 链, anti-hardcode-A 守门."
        ),
    },
}

# write task_brief.md asset
with open(os.path.join(ASSET, "task_brief.md"), "w") as f:
    f.write(task_brief)

# append to B.jsonl
BJSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
line = json.dumps(case, ensure_ascii=False)
with open(BJSONL, "a") as f:
    f.write(line + "\n")

print("appended case to", BJSONL)
print("k_rationale=", case["metadata"]["k_rationale"], "k_check=", case["metadata"]["k_check"])
print("prompt chars=", len(prompt), "test chars=", len(check_src))
