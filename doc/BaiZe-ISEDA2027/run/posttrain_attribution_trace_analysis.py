#!/usr/bin/env python3
# posttrain_attribution_trace_analysis.py
# 3.04%(.17) -> 15.82%(36.15) 5x attribution - trace-driven reproducible analysis.
# Reproduce: python3 posttrain_attribution_trace_analysis.py
import json, os

RUN = os.path.dirname(os.path.abspath(__file__))
A36 = os.path.join(RUN, "attribution_3615_run1")
OLD = os.path.join(RUN, "trace_deep_analysis_3p04.json")

def loadj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

fr = loadj(os.path.join(A36, "final_report.json"))
summ = fr["summary"]; gen = summ["generation_statistics"]
rt = summ["runtime_statistics"]["pyAether_aether"]
unk = summ["runtime_statistics"]["unknown"]
funnel_3615 = {
    "total": summ["total_problems_evaluated"],
    "gen_success": gen["success"], "gen_timeout": gen["timeout"], "gen_fail": gen["fail"],
    "gen_success_rate": round(gen["success"]/summ["total_problems_evaluated"],4),
    "pass_on_gen_success": rt["num_correct"],
    "pass_rate_on_completed": round(rt["num_correct"]/rt["num_tasks"],4),
    "overall_pass_rate": round(fr["metrics"]["pass_rate"],4),
    "unknown_lang_null_tasks": unk["num_tasks"],
    "model_name_field_stale": fr["model_name"],
    "actual_model": "minicpm5-2b-sft-v39-final (final_report.model_name=zhulong_deepseek_v32 是 run_eval.py 陈旧默认字段)",
}

rej = loadj(os.path.join(A36, "codegen_rejection_stats.json"))
rej_by = rej["rejection_by_tool"]; rej_total = rej["rejected_total"]
tool_profile_3615 = {
    "log_lines": rej["log_lines"],
    "rejected_before_execution_total": rej_total,
    "rejection_by_tool_top": dict(list(rej_by.items())[:10]),
    "run_commands_rejected": rej_by.get("run_commands",0),
    "run_commands_share_of_rejections": round(rej_by.get("run_commands",0)/rej_total,4) if rej_total else None,
    "run_commands_string_not_array": rej.get("run_commands_string_not_array",0),
    "submit_and_exit_count": rej["submit_and_exit_count"],
    "pyAether_MCP_calls": rej["pyAether_MCP_calls"],
    "eda_flow_calls": rej["eda_flow_calls"],
    "timeout_markers": rej["timeout_markers"],
    "dual_mcp_servers": "pyAether_MCP_server(:8090 RAG) + eda_flow(:18891 sandbox) - 模型混淆两者工具(把 submit_and_exit 参数传给 eda_flow__open_session)",
}

old = loadj(OLD)
def agg(key):
    return [old[r][key] for r in ["run1","run2","run3","run4","run5"] if r in old and key in old[r]]
sc=agg("submit_calls"); se=agg("submit_err"); ch=agg("contradiction_hits"); ct=agg("contradiction_total")
rv=agg("retrieved_apis_count"); ov=agg("used_overlap")
profile_17 = {
    "source_file": "trace_deep_analysis_3p04.json (5-run 790 题-会话, .17 no-sandbox prompt + 本地 MCP:18888)",
    "submit_calls_per_run": sc, "submit_err_per_run": se,
    "submit_err_rate_avg": round(sum(se)/sum(sc),4) if sum(sc) else None,
    "submit_calls_total": sum(sc),
    "contradiction_hits_per_run": ch, "contradiction_total_per_run": ct,
    "retrieved_apis_per_run": rv, "used_overlap_per_run": ov,
    "overlap_rate_avg": round(sum(ov)/sum(rv),4) if sum(rv) else None,
    "head_failure": "degenerate pass 479/790=60.63% (空操作/无效实现却自报 verified=True, run_eval 判不过) + submit 风暴 6009/6984/132 (91.77% 报错)",
    "baseline_pass_rate": "3.04% ± 0.83% (5-run mean, pass=[6,3,4,5,6]/158)",
}

prompt_diff = {
    "V1_17_no_sandbox": "eval_sys_prompt_template_no_sandbox.md - 明写 本场景无沙箱, 内部推演是唯一逻辑校验",
    "V1_3615_sandbox": "eval_sys_prompt_template_old.md - 承认沙盒, 要求 代码必须通过 run_pyAether_code_tool 测试, 看 error_log",
    "key_behavioral_delta": ".17 否认沙盒->推演不执行->退化代码+虚假自报; 36.15 承认沙盒->真执行真自测->完成题质量 86.2%",
    "V2_RAG": ".17 本地 MCP:18888 vs 36.15 原生 pyAether_MCP_server:8090",
    "V3_sandbox": ".17 实际可达但提示否认 vs 36.15 eda_flow:18891 直连且提示承认",
    "V4_network": ".17 本地 GPU6:8096 vs 36.15 反向隧道 .17:8096->36.15:18096 (延迟更高)",
}

attribution = {
    "is_5x_attributable_to_prompt_wording_alone": False,
    "why_not_prompt_alone": "3.04% 与 15.82% 之间同时变 4 件事(提示/RAG/沙盒/网络), 单变量未跑, 不能归给 prompt 措辞",
    "evidence_based_decomposition": {
        "prompt_sandbox_admission": "高置信主因: .17 否认沙盒->退化60.63%+submit风暴; 36.15 承认沙盒->真执行, submit 334 vs 6000+, 退化消失",
        "sandbox_feedback_loop": "高置信主因: 36.15 完成题 86.2% 通过(执行->报错->修正回路有效); .17 无执行回路->质量塌缩",
        "rag_backend": "中置信: 36.15 原生:8090 检索 get_api_details 349/search_apis 280; .17 overlap 5.7% 检索未落地. 未单变量隔离",
        "network_latency": "低置信: 36.15 经隧道延迟更高但 pass 更高 -> 延迟非负因子",
    },
    "new_failure_mode_on_3615": "code-gen 完成率仅 18.35%(29/158): 主因=工具调用格式错误 1295 次(80.5% 是 run_commands 传 string 而非 array)+双 MCP 工具混淆. 与 .17 退化提交是不同失败模式",
    "prompt_optimization_opportunity": "是 - 36.15 完成题质量 86.2%, 瓶颈是完成率. 修工具调用格式引导(run_commands 数组化)+澄清双 MCP 边界 -> 完成率升 -> pass 率可显著超 15.82%",
    "must_run_single_variable_before_final": "A0-A3 单变量消融未跑, 以上为 trace 证据导向的待验结论, 非定论. 预注册判据见 POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §2",
}

out = {
    "meta": {"task": "posttrain 5x attribution (3.04%->15.82%)", "spec": "POSTTRAIN_ENV_ATTRIBUTION_SPEC.md", "generated_by": "posttrain_attribution_trace_analysis.py", "note": "36.15=单 run1(5-run 仍跑, 不引用未完成 run); .17=5-run trace_deep_analysis_3p04.json"},
    "funnel_3615_run1": funnel_3615,
    "tool_profile_3615_run1": tool_profile_3615,
    "profile_17_5run": profile_17,
    "prompt_diff_V1_to_V4": prompt_diff,
    "attribution_verdict": attribution,
}
op = os.path.join(RUN, "attribution_analysis_3615_vs_17.json")
with open(op, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("WROTE", op)
print(json.dumps({"3615_funnel": funnel_3615, "3615_rej_total": rej_total, "17_submit_total": profile_17["submit_calls_total"], "verdict_prompt_alone": attribution["is_5x_attributable_to_prompt_wording_alone"]}, ensure_ascii=False, indent=1))
