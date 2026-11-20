#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _append_porttextpinplan_C.py -- append EDA-Eval-DesignFlow-PortTextPinPlan-001
# to EDA-Eval-DesignFlow_C.jsonl (shard C, layout_virtuoso).
import json, os

CASE = "PortTextPinPlan-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_C.jsonl")
CASE_ROOT = os.path.join(ROOT, "reference", CASE)

PROMPT = """你是全定制版图工程师 ellawu，在 Cadence Virtuoso 里用 SKILL 维护 CXMT 内部脚本 cxmt_autoPR_generatePortText.il。这个脚本把 schematic 的端口/网络信息以 Label 和 Pin 的形式自动生成到 Layout 顶层视图：它先打开同 cell 的 schematic 视图，用 schTraceNetToConn 递归追踪网络建立 instance#pin -> 顶层信号名 的映射，再在 layout 顶层创建 label/pin，并按 PROJ_NAME 设置字体、对已有 label 按坐标去重、把总线实例名 <a:b> 用 dbProduceMemName 展开、把子 cell pin 的 bBox 中心变换到顶层坐标后用 leCreatePin/dbCreateLabel 创建。

你本轮要按下面 3 条真实需求改它（用户原话逐字）：
1. "根据这个脚本修改 使得底层的pin能覆到顶层" —— 底层 pin 要能浮到顶层；
2. "创建底层除了 vcc vss 的所有 pin" —— 创建底层除 vcc/vss 之外的所有 pin；
3. "读版图底层位置是在daimanage部分体现的" —— 底层版图位置在 daimanage 部分体现。
已澄清意图为「情况 B」：layout 中所有 instance 的 pin 都要被处理，包括只存在于 layout、schematic 里没有的 instance（不能只处理 schematic 出现的 instance）。

真实流程要 live Virtuoso 跑 SKILL，但 .75 沙盒没有可用的 Virtuoso 安装与你的版图库。请把这个 port-text/pin 生成流程的「可验证核心」做成一个自包含纯 Python（标准库、ASCII only，不引 pyAether/numpy/cadence 等第三方包）离线工具 port_text_pin_plan.py：输入一份 layout 层次规范 JSON（见附件 spec_A.json），输出顶层 pin/label 创建计划 JSON。

算法要求（与上述 SKILL 行为一一对应）：
- 遍历 instances 里的【所有】实例（不管 in_schematic 是 true 还是 false —— 覆盖 layout-only 实例）；
- 对总线实例名 `<a:b>` 做展开（升序 a..b 或降序 b..a 都要支持），每个 bit slice 是一个独立实例；bus 实例可带 pitch，slice i 的 origin = base_origin + i*pitch；
- 对每个实例的每个 pin：若 pin 的 net 属于 power_nets（如 vcc/vss）则跳过、不计入 creations（"除 vcc vss"）；
- 顶层坐标 = pin bBox 中心 + slice origin（子 cell -> 顶层坐标变换）；
- top_signal：pin 有 top_signal 就用它（非总线不加后缀，总线 bit 加 `<bit>` 后缀）；没有就用 net 名（同样总线加 `<bit>` 后缀）；
- 去重：若已有 existing_labels 在同位置且同名 -> create_label=False；若已有 existing_pins 在同位置且同名 -> create_pin=False；否则对应标志为 True；
- 输出 plan JSON 含 top_cell / power_nets / creations[] / summary{n_instances,n_pins_total,n_power_skipped,n_creations,n_labels_new,n_pins_new}；每个 creation 含 instance/pin/net/top_signal/location[x,y]/layer/create_label/create_pin。

附件 spec_A.json 是 ADC_TOP 的真实规范（实例 I0=INVX1 in_schematic=true 含 A/Z/VDD/VSS；总线实例 I1<0:1>=BUFX2 in_schematic=false pitch[0,100] 含 A/Z；power_nets vcc/vss；existing_labels/existing_pins 在 I0.A 位置(120,220)有 A_sig 做去重）。schema: top_cell/power_nets/instances[{name,master,origin,pitch?,in_schematic,pins[{name,net,layer,bBox,top_signal?}]}]/existing_labels[{location,name}]/existing_pins[{location,name}]。

判分会在一份结构不同的隐藏规范 spec_B（不同 top_cell、不同电源网名 vdd/gnd、含降序总线 IB<2:0>、含 layout-only 实例、在 IA.A 位置有 dup label/pin）和 spec_B2（极简、跨输入守卫）上真跑你的脚本：必须真正读规范、真做坐标变换/去重/总线展开/电源跳过，不能硬编码 A 的计划。用你的脚本跑 spec_A.json 得到 plan_A.json，把 port_text_pin_plan.py + plan_A.json 一起打包成 outputs/submit.zip 交付。"""

with open(os.path.join(CASE_ROOT, "check.py")) as f:
    check_src = f.read()

entry = {
    "task_id": "EDA-Eval-DesignFlow-PortTextPinPlan-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        {
            "name": "spec_A.json",
            "source": "spec_A.json",
            "desc": "可见 layout 层次规范 A（ADC_TOP：I0=INVX1 in_schematic=true 含 A/Z/VDD/VSS；总线 I1<0:1>=BUFX2 in_schematic=false pitch[0,100] 含 A/Z；power_nets vcc/vss；existing_labels/existing_pins 在 I0.A 位置(120,220)有 A_sig 做去重）。schema: top_cell/power_nets/instances[{name,master,origin,pitch?,in_schematic,pins[{name,net,layer,bBox,top_signal?}]}]/existing_labels[{location,name}]/existing_pins[{location,name}]"
        },
        {
            "name": "task_brief.md",
            "source": "task_brief.md",
            "desc": "交付接口说明（≤3 行）：deliverable=outputs/submit.zip 含 port_text_pin_plan.py + plan_A.json；脚本 CLI <spec.json> <plan_out.json>；判分 check(submit.zip,workdir) 双参独立临时目录解 zip 在隐藏 spec_B/B2 上真跑。不写「要做什么」。"
        }
    ],
    "expected_artifacts": ["port_text_pin_plan.py", "plan_A.json"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "ellawu",
            "host": "hfeg0pkn005",
            "session_file": "1791611132079_5vmvu.messages.json",
            "match_count": 165,
            "real_task_summary": "用 Cadence SKILL 维护 CXMT 脚本 cxmt_autoPR_generatePortText.il（把 schematic 端口/网络以 label/pin 生成到 layout 顶层），按 3 条真实需求改它：底层 pin 浮到顶层、创建底层除 vcc/vss 外所有 pin、底层版图位置在 daimanage 体现；澄清为情况B=layout 所有 instance（含 layout-only）的 pin 都处理"
        },
        "domain": "layout_virtuoso",
        "track": "synthesized",
        "level": "L1-boundary",
        "test_rationale": (
            "15 条断言：①(a)submit.zip 合法且含 port_text_pin_plan.py+plan_A.json "
            "②(b)py_compile 通过且仅标准库(禁 pyAether/numpy/skill/virtuoso) "
            "③(c)脚本跑隐藏 spec_B 退出 0 且写出 plan_B.json "
            "④(d)plan_B.json 合法 JSON 含 top_cell/creations/summary/power_nets 键 "
            "⑤(e)summary.n_instances==期望(总线展开计数,含 layout-only 实例) "
            "⑥(f)summary.n_power_skipped==期望(电源 pin vcc/vss/vdd/gnd 被跳过=除 vcc vss) "
            "⑦(g)creations 中无任何 net∈power_nets 的条目 "
            "⑧(h)creations 含 layout-only(in_schematic=false)实例的全部总线 slice(情况B) "
            "⑨(i)每个 creation 的 location==bBox 中心+slice origin(子 cell->顶层坐标变换) "
            "⑩(j)与 existing_label 同位置同名的 creation create_label=False(标签去重) "
            "⑪(k)与 existing_pin 同位置同名的 creation create_pin=False 否则 True(pin 去重) "
            "⑫(l)降序总线 IB<2:0> 展开为 IB<2>/IB<1>/IB<0> 三 slice "
            "⑬(m)无 top_signal 的 pin 用 net 名(总线加 <bit> 后缀,非总线无后缀) "
            "⑭(n)确定性(两次跑 sha256 相同)+无泄漏(输出/源码不含 spec_A/reference/.jsonl/hidden 路径) "
            "⑮(o)跨输入守卫 plan_B2≠plan_B(输出依赖输入非硬编码)且 B2 摘要==1 实例/1 跳过/2 creations"
        )
    }
}

# validate JSON + assert k_rationale == k_check
assert entry["metadata"]["test_rationale"].startswith("15 条断言：")
# count check.py conditions a..o
import re as _re
conds = sorted(set(_re.findall(r"_cond\(\"([a-z]+)\"", check_src)))
assert conds == list("abcdefghijklmno"), conds
print("k_check =", len(conds), " k_rationale = 15")

# idempotency: remove any prior entry with same task_id
kept = []
removed = 0
with open(JSONL) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            kept.append(line); continue
        if o.get("task_id") == entry["task_id"]:
            removed += 1; continue
        kept.append(line)
with open(JSONL, "w") as f:
    for line in kept:
        f.write(line.rstrip("\n") + "\n")
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", entry["task_id"], "removed_prior", removed, "total_lines", len(kept) + 1)
