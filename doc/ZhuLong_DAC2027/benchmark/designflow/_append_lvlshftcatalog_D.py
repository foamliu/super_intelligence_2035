#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-LvlShftCatalog-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_D.jsonl")
CID = "LvlShftCatalog-001"
ADIR = os.path.join(BASE, "assets", CID)
RDIR = os.path.join(BASE, "reference", CID)

prompt = open(os.path.join(ADIR, "prompt.txt")).read()
check_src = open(os.path.join(RDIR, "check.py")).read()

entry = {
    "task_id": "EDA-Eval-DesignFlow-" + CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
        "assets/%s/spec_A.json" % CID,
    ],
    "expected_artifacts": ["topology_catalog.md", "sizing_report.md", "manifest.json"],
    "budget": {"max_turns": 25},
    "test": check_src,
    "metadata": {
        "domain": "analog_context",
        "grade": "B",
        "track": "synthesized",
        "L_level": "L1",
        "trace_source": {
            "user": "e0025730",
            "host": "10.129.8.86",
            "session_file": "1782800756855_5u4s2",
            "match_count": 52,
            "real_task_summary": (
                "e0025730 @ 10.129.8.86 调用 lvlshft skill「启动业务场景: 模拟电路生成」(U#0) + 「/lvlshft」(U#70)。"
                "工作目录 /home/e0025730/devops/eda_data_bridge/bundle/lvlshft/lvlshft_optimize/01_lvlshft_spec，CLI lvlshft.py (list/status/result/run/params) 跑在 /usr/bin/python3.6。"
                "assistant 探 lvlshft bundle + eda_data_bridge + SKILL.md，发现 openpyxl 不可装(无网)但 pyyaml 可用，用 python3.6 跑 lvlshft.py list/status/result 成功。"
                "项目 = Level Shifter 电平转换器电路设计优化工具链：23 个拓扑分 6 个 Case(Case1 正向6拓扑 输入nMOS+保护nMOS*2+前馈pMOS+上拉pMOS / Case2 正向11拓扑 输入nMOS+保护nMOS+上拉pMOS / Case3 负压2 / Case4 负压1 / Case5 高压1 / Case6 特殊输入2)，当前 Case2 Vcc2Vdleq，最优 beta1=70 S=0.05 L=1.30um W=1.00，PVT 验证 Rise0.573<=0.694 / Fall0.304<=0.31 / Ioff1.588<=5 / Aging7.42<=20 全 PASS。"
                "A-faithful 不可行(真实 lvlshft bundle+SPICE 结果在 /home/e0025730 私有不可附加 + live SPICE 不可移植) → B 档 synthesized: facet = 电平转换器拓扑目录+尺寸/验收报告生成器(gen_lvlshft_catalog.py --spec --outdir)，读 spec JSON(module/design/cases[*].topologies[*].{name,structure}/current/sizing/verification[*].{metric,measured,spec,unit,op,corner})，按 op(<=,>=,==,!=,<,>) 真实计算 PASS/FAIL，产 topology_catalog.md(Case/拓扑/结构表+汇总)+sizing_report.md(尺寸参数表+验收表+PASS/FAIL)+manifest.json(11 键计数+overall)。"
                "A=Vcc2Vdleq(6cases/23topo/4metrics 全PASS)；hidden B=Hvdd12Vwlp_HV(4cases/15topo/5metrics 3PASS2FAIL：Rise0.85>0.694 FAIL + DC Margin op>= 0.18<0.20 FAIL)；hidden B2=NgVss2VkbVcc_Neg(3cases/8topo/4metrics 2PASS2FAIL：Rise0.72>0.70 + Ioff6.5>5.0)。"
            ),
        },
        "test_rationale": (
            "16 条断言："
            "①submit.zip 含候选 .py 且无 check/reference/negative/.jsonl/hidden/_tmp 泄漏且 py_compile 通过 "
            "②在隐藏输入 B 上运行 exit 0 且产出 topology_catalog.md+sizing_report.md+manifest.json 三个文件 "
            "③manifest.json 含全部 11 个顶层键(module/design/current_case/current_topology/n_cases/n_topologies/n_metrics/n_pass/n_fail/overall/files) "
            "④manifest n_cases==4 且 n_topologies==15(B 的 case 数与拓扑数) "
            "⑤topology_catalog.md 含 B 全部 15 个拓扑名(Hv2Vdd1/Hvcc2Vdleq/Hvss2VkbVcc/Hvdd12Vwlp 等) "
            "⑥topology_catalog.md 含各拓扑的晶体管结构描述(input_nMOS+protect_nMOS+pullup_pMOS / negative_voltage_pump / high_voltage_level_shift)非仅名字 "
            "⑦catalog 汇总行 'Total: 15 topologies across 4 cases.' 数字正确 "
            "⑧sizing_report.md 含 B 全部尺寸参数及值(beta1=45/S=0.08/L_um=1.0/W=1.5) "
            "⑨sizing_report.md 验收表含 B 全部 5 个指标(Rise Delay/Fall Delay/Ioff/Aging Max Deg/DC Margin) "
            "⑩PASS/FAIL 按 op 真实计算(非硬编码)：manifest n_pass==3 且 n_fail==2(B: Rise0.85<=0.694 FAIL + DC Margin0.18>=0.20 FAIL，余 PASS) "
            "⑪sizing_report.md 将 Rise Delay 标记为 FAIL(反 always-pass stub) "
            "⑫manifest overall=='HAS_FAIL'(B 有失败项) "
            "⑬反硬编码+跨输入：候选源码无 A 字面量(Vcc2Vdleq/beta1 70/0.573/0.694 等) 且 A-run n_topologies==23 且 B2-run n_cases==3+n_fail==2+design=='NgVss2VkbVcc_Neg' "
            "⑭>= 运算符正确处理：B 的 DC Margin 行 op 为 '>=' 且 status 为 FAIL(0.18<0.20) "
            "⑮确定性：3 次重复 B-run 的 manifest.json+topology_catalog.md sha256 一致 "
            "⑯B-run catalog 不泄漏任何 A 拓扑名(Vcc2Vdleq/Vcc2Vdd1/Vss2VkbVcc/Vdd12Vwlp/Vint2VdleqAryA 等)"
        ),
    },
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended:", entry["task_id"])
print("D.jsonl lines now:", sum(1 for _ in open(JSONL)))
