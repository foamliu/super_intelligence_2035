#!/usr/bin/env python3
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "PgRscalcAgentInline-001"
ref_dir = os.path.join(HERE, "reference", CASE)
check_py = os.path.join(ref_dir, "check.py")
test_src = open(check_py, "r", encoding="utf-8").read()

prompt = (
    "你是 EDA 版图工程师 steveny，正在一台配好 Virtuoso IC617 + RsCalc 8.2.1 的机器上跑"
    "「RsCalc -> AutoVia -> PowerFill」电源网络（PG）降阻迭代 flow（见 prompt_flow.md："
    "持续迭代直到版图电源网络最坏寄生电阻相对基线下降达到 targetReduction）。"
    "基线 RsCalc 这一步需要一个自包含的 SKILL agent 脚本 run_rscalc_agent.il：把 common.config"
    "（共享设计参数 process/project/libName/cellName/viewName + 流控参数 targetReduction/maxIterations）"
    "和 rscalc.config（RsCalc 专属参数 pwrNets/version/runDir/metalOption/useExistGds/gdsFile/"
    "checkShort/divMetRatio/parallel/viaGroup/viaGroupRatio/reduceShort/reduceShortRatio/checkPoints）"
    "里的全部参数内联进脚本，不再 load() 外部配置，末尾自动调用 RunRsCalcNoGui()，并配套生成"
    "run_rscalc_agent.cmd（供 virtuoso -nograph -replay 使用）。\n\n"
    "flow 里已提供生成器 gen_rscalc_agent.py（纯 Python，读 common.config + rscalc.config + "
    "run_rscalc_nogui.il 模板，把 load(\"RSCALC_CONFIG_PLACEHOLDER\") 替换成内联赋值块、把末尾提示"
    "替换成 RunRsCalcNoGui() 自动调用、生成 .cmd），调用顺序为："
    "python3 gen_rscalc_agent.py <rscalc.config> <run_rscalc_nogui.il> <输出.il> <common.config>。\n\n"
    "请写一个 Python 审计程序 baseline_rscalc_agent_audit.py，CLI 为 "
    "`python3 baseline_rscalc_agent_audit.py <config_dir> <work_dir>`，其中 config_dir 含 "
    "common.config、rscalc.config、run_rscalc_nogui.il、gen_rscalc_agent.py。程序要："
    "(1) 用正确的参数顺序驱动 gen_rscalc_agent.py，在 work_dir 下产出 run_rscalc_agent.il + "
    "run_rscalc_agent.cmd；(2) 解析源配置与生成的 .il/.cmd；(3) 把 JSON 审计报告打印到 stdout。"
    "报告须 certify：所有非流控参数（targetReduction/maxIterations 这两个流控键不得内联）都正确"
    "内联、生成的 .il 内不再残留 RSCALC_CONFIG_PLACEHOLDER、.il 末尾含 RunRsCalcNoGui() 自动调用、"
    ".cmd 含 load(\".../run_rscalc_agent.il\")。判分器会在一套与资产不同的隐藏 PG 配置上跑你的程序，"
    "所以必须按实际读到的配置动态判定，不能硬编码任何具体取值。"
)

trace_source = {
    "user": "steveny",
    "host": "hfeg0pnd001",
    "session_file": "1790042369946_o1yhw.messages.json",
    "match_count": 78,
    "real_task_summary": (
        "steveny 在 hfeg0pnd001 上跑 RsCalc->AutoVia->PowerFill 电源网络降阻 flow"
        "（test_layout_rscalc_flow_19）；用户要求 read the prompt_flow.md and do the job, "
        "基线电阻分布一定要重新算不要用已有的。agent 探测环境后受阻于 OA 库不可达 + Virtuoso -nograph 起不来，"
        "改为推进可落地部分：建全新 workdir、跑 gen_rscalc_agent.py 生成基线 run_rscalc_agent.il(19 参数内联)+.cmd 并校验。"
        "trace 末尾 agent 报阻塞并询问方向(ask 超时)，无用户接受产物 -> 取 B-synthesized。"
    ),
}

test_rationale = (
    "15 条断言：①submit.zip 合法且含 baseline_rscalc_agent_audit.py ②该 .py 通过 py_compile "
    "③SUT 在隐藏 B 上 exit0 且 stdout 为 JSON dict ④JSON 含全部必需顶层键(il_path/cmd_path/"
    "params_expected/params_inlined/no_placeholder/auto_invokes_runrscalc/cmd_loads_il/all_pass) "
    "⑤no_placeholder==True(生成 .il 内无 RSCALC_CONFIG_PLACEHOLDER 残留) ⑥auto_invokes_runrscalc"
    "==True(.il 末尾含 RunRsCalcNoGui() 自动调用) ⑦cmd_loads_il==True(.cmd 含 load + run_rscalc_agent.il) "
    "⑧n_inlined_expected==19(5 共享 + 14 RsCalc 专属，流控键已剔除) ⑨流控键 targetReduction/"
    "maxIterations 不出现在 inlined 参数中 ⑩process==B 的 \"cxmt10G5\"(非 A 的 cxmt10G4plus，反硬编码 A) "
    "⑪parallel==B 的 \"32\"(RsCalc 专属参数取 B 值) ⑫每个 expected 参数的 inlined 值逐项一致(核心内联正确性) "
    "⑬生成的 .il 确实存在且非空 ⑭cellName==B 的 \"PGMesh_rscalc_via2\"(非 A 的 BCenterL_rscalc_via4) "
    "⑮checkPoints 内联==B 的 8 个内层 list(\"net\"...) 元组且含 gnd! 网络(反硬编码 A 的 vdd1!/vss!/vcc!)"
)

case = {
    "id": "EDA-Eval-DesignFlow-PgRscalcAgentInline-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/PgRscalcAgentInline-001/common.config",
        "assets/PgRscalcAgentInline-001/rscalc.config",
        "assets/PgRscalcAgentInline-001/run_rscalc_nogui.il",
        "assets/PgRscalcAgentInline-001/gen_rscalc_agent.py",
    ],
    "test": test_src,
    "metadata": {
        "trace_source": trace_source,
        "domain": "pg_layout",
        "track": "B-synthesized",
        "layer": "L1-boundary",
        "k_check": 15,
        "k_rationale": 15,
        "test_rationale": test_rationale,
    },
}

# k-gate self-check
import re
labels = re.findall(r'\((a|[a-z])\)', test_src)
# count _cond("x", ...) calls
cond_calls = re.findall(r'_cond\("([a-z])"', test_src)
k_check = len(set(cond_calls))  # unique labels a..o
circled = test_rationale.count("\u2460") or len(re.findall(r"[\u2460-\u2473]", test_rationale))
# count ①-⑮ 
import unicodedata
ncirc = sum(1 for ch in test_rationale if 0x2460 <= ord(ch) <= 0x2473)
print("k_check(cond calls)=", k_check, " k_rationale(circled)=", ncirc)
assert k_check == 15, k_check
assert ncirc == 15, ncirc
assert k_check == ncirc, (k_check, ncirc)
assert test_rationale.startswith("15 条断言："), test_rationale[:20]

line = json.dumps(case, ensure_ascii=False)
jsonl = os.path.join(HERE, "EDA-Eval-DesignFlow_C.jsonl")
with open(jsonl, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED to", jsonl)
print("line bytes:", len(line.encode("utf-8")))
# verify roundtrip + test field == disk check.py
with open(jsonl, "r", encoding="utf-8") as f:
    last = json.loads(f.readlines()[-1])
assert last["test"] == test_src, "test field != disk check.py"
assert last["id"] == case["id"]
print("roundtrip OK; test==disk check.py (bytes=%d)" % len(test_src))
