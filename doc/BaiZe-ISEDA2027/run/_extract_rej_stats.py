import json, re, collections, sys
L = "/tmp/posttrain_baseline_3615/run1/codegen.log"
txt = open(L, encoding="utf-8", errors="ignore").read()
def gc(p):
    return txt.count(p)
rej_total = gc("rejected before execution")
by_tool = collections.Counter(re.findall(r"Tool call ([a-zA-Z_]+(?:__[a-zA-Z_]+)?) was rejected", txt))
eda = collections.Counter(re.findall(r"eda_flow__([a-zA-Z_]+)", txt))
pa = collections.Counter(re.findall(r"pyAether_MCP_server__([a-zA-Z_]+)", txt))
out = {
    "log_lines": txt.count("\n"),
    "rejected_total": rej_total,
    "rejection_by_tool": dict(by_tool.most_common(25)),
    "submit_and_exit_count": gc("submit_and_exit"),
    "eda_flow_calls": dict(eda.most_common(20)),
    "pyAether_MCP_calls": dict(pa.most_common(20)),
    "timeout_markers": gc("timeout"),
    "run_commands_string_not_array": len(re.findall(r"run_commands was rejected before execution: Invalid input for tool run_commands: Type validation failed.*received string", txt)),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
