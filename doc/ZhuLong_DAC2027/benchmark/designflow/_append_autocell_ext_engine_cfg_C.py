#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001 to shard C jsonl."""
import json, os

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_C.jsonl")
A    = os.path.join(ROOT, "assets", CID)
REF  = os.path.join(ROOT, "reference", CID)

with open(os.path.join(REF, "check.py"), encoding="utf-8") as f:
    check_src = f.read()

prompt = open(os.path.join(A, "prompt.txt"), encoding="utf-8").read()

rationale = (
    "14 条断言："
    "①submit.zip 含 gen_rule_kit.py 且 py_compile 通过 "
    "②生成器在隐藏 B 上 exit 0 且产出文件名 = manifest output_name "
    "③输出 rule.tcl 无注释行（stripped 不以 # 开头） "
    "④原 kit 非注释代码行 verbatim 全保留无缺失 "
    "⑤输出含 set_external_engine 调用 "
    "⑥set_external_engine 含 -bin calibre（manifest engine_bin） "
    "⑦-drc_deck 路径 = manifest 推导期望（power_side+flow 变体+calibre_DRC_<SIDE>.rule） "
    "⑧-lvs_deck 路径 = manifest 推导期望（calibre_LVS_<SIDE>.rule） "
    "⑨set_external_engine 段插在 source .../prepr.tcl 之后 "
    "⑩真跑候选：subprocess tclsh info complete 校验输出 TCL 语法合法 "
    "⑪set_external_engine 目标 tech 名 = manifest tech_name（default_tech） "
    "⑫deck 路径变体正确（flow=gds 无 _virtuoso；flow=oa 含 _virtuoso） "
    "⑬含 -timeout 且值 = manifest timeout_sec（600） "
    "⑭原 kit 头注释行 # AutoCell Layout Generator TCL 不在输出中"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        "assets/" + CID + "/R_H204_000.tcl",
        "assets/" + CID + "/autocell_engine_cfg_manifest.json",
        "assets/" + CID + "/autocell_engine_cfg_spec.md",
        "assets/" + CID + "/task_brief.md",
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["gen_rule_kit.py"],
    "test": check_src,
    "budget": {"max_turns": 25, "wall_time_sec": 600},
    "metadata": {
        "domain": "physical_verify",
        "task_name": "AutoCellExtEngineCfg",
        "scenario": (
            "Empyrean AutoCell 标准单元编译器跑完 GDS 后用 calibre 做 DRC+LVS 物理验证，"
            "需把外部验证引擎 rule deck 挂到 technology 上。客户给 4 个 PDK runset 目录"
            "（tv1_fs 正面 / tv1_dbc 背面 / *_virtuoso OA 变体）；AutoCell GDS flow 走非 virtuoso，"
            "用户正面供电 → tv1_fs/current/calibre_DRC_FS.rule + calibre_LVS_FS.rule。"
            "GUI Rule File Settings 对话框拒 .rule 扩展名，正式入口是 TCL "
            "tech set_external_engine。用户选方案B：不动原 kit R_H204_000.tcl，"
            "生成 kit 变体 R_H204_000_rule.tcl，逐行保留原代码 + 插 set_external_engine 段 + 去注释。"
        ),
        "direction": "generate (kit TCL variant with external DRC/LVS engine config)",
        "layer": "L1-boundary",
        "topic": "autocell_external_engine_config",
        "difficulty": "L1-boundary",
        "design": (
            "B-档 synthesized (A-档 disqualified: live AutoCell 安装树 + live PDK runset "
            "/apps/imctf/cad/runset/lacaa + live autocell doc 内网；gold 是静态 TCL 文本变换). "
            "把 set_external_engine 命令语法 + tv1_fs/dbc/_virtuoso runset 路径约定 + kit 变体要求固化为 "
            "autocell_engine_cfg_spec.md + manifest JSON. 候选写纯标准库生成器 gen_rule_kit.py: 读 manifest"
            "(power_side fs|dbc / flow gds|oa / runset_root / pdk_tag / tech_name / engine_bin / timeout / "
            "insertion_anchor / no_comments / preserve_original) + kit TCL → 推导 deck 路径(side=upper(power_side),"
            "flow_suffix=_virtuoso if oa else '', side_dir=runset_root/pdk_tag_power_side+suffix/current, "
            "drc=calibre_DRC_<SIDE>.rule, lvs=calibre_LVS_<SIDE>.rule) → 产 <kit_base>_rule.tcl(去注释行 + 原"
            "代码 verbatim + 在 prepr.tcl 锚点后插 5 行 set_external_engine 段). 隐藏 B1(dbc,gds→tv1_dbc,"
            "*_DBC.rule)/B2(fs,oa→tv1_fs_virtuoso,*_FS.rule)/B3(dbc,oa→tv1_dbc_virtuoso,*_DBC.rule) 防 hardcode "
            "fs/gds; 14 条断言 a-n 含 tclsh info complete 真跑候选."
        ),
        "tcr_refs": "trace 1792742027783_8ky45 USER#23/28/29 (USER#29=A-档 seed 提出目标: 生成 R_H204_000_rule.tcl 加 rule 配置不改原 kit; USER#23-28 deck 路径推理=hint; USER#30-32 去注释=hint)",
        "heavy": False,
        "wall_time_sec": 600,
        "trace_source": {
            "user": "e0047434",
            "host": "hfeg0pnd002",
            "session_file": "1792742027783_8ky45.messages.json",
            "match_count": 211,
            "real_task_summary": (
                "AutoCell N5 标准单元编译器物理验证配置: 用户用 Empyrean AutoCell 生成 std cell GDS, "
                "需配 calibre DRC/LVS rule deck. 客户给 4 个 ALS PDK runset 路径(tv1_fs 正面/tv1_dbc 背面/"
                "*_virtuoso OA 变体). AutoCell GDS flow 走非 virtuoso, 正面供电选 tv1_fs. GUI Rule File "
                "Settings 对话框拒 .rule 扩展名, 正式入口是 TCL tech set_external_engine. 用户选方案B: "
                "生成 kit 变体 R_H204_000_rule.tcl(逐行保留原 R_H204_000.tcl 代码 + 插 set_external_engine "
                "段 -bin calibre -drc_deck tv1_fs/current/calibre_DRC_FS.rule -lvs_deck calibre_LVS_FS.rule "
                "-timeout 600 + 去所有注释行). 200 msgs, assistant list_allowed_files+read_files 通读 autocell/"
                "doc + 探 4 runset 目录 + editor 生成 R_H204_000_explain.tcl(逐行注释版) + R_H204_000_rule.tcl"
                "(kit 变体) + ac_rule_verify.py 自验(剥注释后 diff 原代码零改动+仅插 5 行引擎段)."
            ),
        },
        "test_rationale": rationale,
        "track": "faithful-seed-B-synthesized",
    },
}

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("appended", CID, "to", JSONL)
# verify
n = sum(1 for _ in open(JSONL))
print("jsonl now has", n, "entries")
