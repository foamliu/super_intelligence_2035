#!/usr/bin/env python3
# _append_viafill_svrf_gen_001.py — append EDA-Eval-DesignFlow-ViaFillSvrfGen-001
# to EDA-Eval-DesignFlow_C.jsonl (shard C, physical_verify).
import json, os, sys

CASE = "EDA-Eval-DesignFlow-ViaFillSvrfGen-001"
ROOT = os.path.dirname(os.path.abspath(__file__))  # .../benchmark/designflow
# designflow -> benchmark -> ZhuLong_DAC2027 -> doc -> super_intelligence_2035 -> code
BENCH = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "..", "..", "EDA-Flow-Bench", "benchmarks", "EDA-Eval-DesignFlow"))
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
CHECK = os.path.join(BENCH, "reference", CASE, "check.py")

with open(CHECK, encoding="utf-8") as f:
    test_src = f.read()

case = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": open(os.path.join(BENCH, "assets", CASE, "prompt.txt"), encoding="utf-8").read(),
    "attachments": [
        "assets/%s/prompt.txt" % CASE,
        "assets/%s/task_brief.md" % CASE,
        "assets/%s/bundle/rule_spec.txt" % CASE,
        "assets/%s/bundle/layer_map.txt" % CASE,
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["outputs/submit.zip"],
    "test": test_src,
    "budget": {"max_turns": 20},
    "metadata": {
        "domain": "physical_verify",
        "task_name": "Calibre-SVRF-DFM-SPEC-FILL-via-fill-gen",
        "scenario": (
            "ellawu/3duob trace: 用户给 Calibre DFM SPEC FILL（MA/M2 通孔填充）设计规则"
            "（V1 层 90:0/16/24，方形 0.045×0.045，矩形 0.045×0.090，V1-to-V1 space 0.225，"
            "M1/M2 enclosure 0.0025，M1 3D 短线<0.108，线长 0.108-0.461 + 相邻≥0.476，seal_ring 排除，"
            "block=OR PG_drawing AT4_DUMMY2），agent 多轮迭代产 SVRF deck vFinal。"
            "B-档 synthesized：把确认值打包 rule_spec.txt+layer_map.txt，要求 SUT 写 python 生成器"
            "viafill_svrf_gen.py 读规格 emit SVRF DFM SPEC FILL deck（含候选区/两段 fill/STEP 计算/DRC 验证/GDS 输出），"
            "隐藏 B 用 V2/M2-M3 不同层号/尺寸/间距/enclosure 杀硬编码。"
        ),
        "direction": "physical_verify",
        "layer": "calibre-svrf-dfm-spec-fill-via-fill",
        "topic": "svrf-dfm-spec-fill-rule-generation",
        "difficulty": "L1-boundary",
        "design": "B-synthesized",
        "tcr_refs": ["1789520357933_3duob"],
        "heavy": "offline-stdlib",
        "wall_time_sec": 600,
        "trace_source": {
            "user": "ellawu",
            "host": "hfeg0pkn005",
            "session_file": "1789520357933_3duob.messages.json",
            "match_count": 335,
            "real_task_summary": (
                "ellawu/hfeg0pkn005(10.129.8.235), mc=335, tools calibre:508/schematic:14/virtuoso:5/pyAether:3 "
                "(keywords cmos:3023 netlist:1320 aether:740 schematic:622 analog:178 hspice:76 pyaether:46), "
                "47 msgs/1.23MB, agent cline(lead), cwd /home/ellawu. "
                "USER#0(A-档 seed 提出目标未给根因)「DFM SPEC FILL SHAPE」→USER#3「在svrf中用DFM SPEC FILL对MA和M2层打孔怎么写」"
                "→USER#4 完整规则规格(V1 90:0/16/24, 0.045×0.045/0.045×0.09, M1 3D<0.108, 线长0.108-0.461+相邻≥0.476, seal_ring排除, M2/M1 enclosure)"
                "→USER#5-9 参数确认(V1-to-V1 space 0.225, M2/M1 enclose 0.0025µm)。"
                "agent: editor 多版 SVRF deck 迭代(v1 STEP 0.135 错→vFinal STEP 0.270=size+space 对)，无真实 calibre 运行。"
                "gold(人工复核 msg#46 vFinal): calibre_M1M2_ViaFill.rule — INCLUDE calibre.layer; 层声明 MA/M2/V1=LAYER 90 0/16/24/seal_ring/block=OR PG_drawing AT4_DUMMY2; "
                "候选区 cand=MA AND M2 NOT V1/flat/stop NOT seal_ring NOT block SIZE BY -enc AREA>=0.005; "
                "DFM SPEC FILL V1_fill_sq(FILL_OPEN_AREAS, SIZE 0.045×0.045, STEP 0.270×0.270, ORIGIN 0.0225); "
                "DFM SPEC FILL V1_fill_rec(SIZE 0.045×0.090, STEP 0.270×0.315); V1_fill=sq OR rec; V1_merge=V1 OR V1_fill; "
                "DRC: ENC V1_fill M2<0.0025, ENC V1_fill MA<0.0025, EXT V1_fill<0.225 OPPOSITE, M1 3D/line-mid checks; "
                "GDS: DFM RDB GDS M1M2_ViaFill.gds 90 0 APPEND _vfill NOEMPTYDB(+merge/errors); DRC SELECT CHECK。"
                "gold 依赖 live calibre 运行验证→不可行(license/路径) → B-档 synthesized L1-boundary(离线 spec+layermap fixture→python 生成器→静态 SVRF 结构/参数校验+生成器执行, stdlib-only, 确定性, 不硬编码层号/尺寸/间距/enclosure)。"
                "hidden B(V2/M2-M3, 层91:0/16/24, 方形0.050×0.050, 矩形0.050×0.100, space 0.250→STEP 0.300×0.300/0.300×0.350, enc 0.0030, M2 3D 0.120, 线长0.120-0.500+相邻≥0.520, block M0_drawing/AT5_DUMMY3)→杀硬编码 A 的 90/0.045/0.225/0.0025/0.270。"
            ),
        },
        "test_rationale": (
            "21 条断言：①(a) zip 含 viafill_svrf_gen.py ②(b) 生成器 A 跑 exit0 产非空 .rule "
            "③(c) A.rule 含 INCLUDE 语句 ④(d) V1 drawing 层声明 LAYER 90 0 ⑤(e) V1 平仓层 LAYER 90 16 "
            "⑥(f) V1 止损层 LAYER 90 24 ⑦(g) MA 与 M2 层声明齐全 ⑧(h) 候选区 MA AND M2 重叠 "
            "⑨(i) 排除已有 V1 三子层(NOT V1/NOT V1_flat/NOT V1_stop) ⑩(j) 排除 seal_ring(NOT seal_ring) "
            "⑪(k) 排除 block(OR PG_drawing AT4_DUMMY2) ⑫(l) DFM SPEC FILL + FILL MODE FILL_OPEN_AREAS "
            "⑬(m) 方形 fill WINDOW SIZE 0.045 BY 0.045 ⑭(n) 方形 fill WINDOW STEP 0.270 BY 0.270(=0.045+0.225 计算非硬编码) "
            "⑮(o) 矩形 fill WINDOW SIZE 0.045 BY 0.090 ⑯(p) 矩形 fill WINDOW STEP 0.270 BY 0.315 "
            "⑰(q) M2 enclosure DRC ENC V1_fill M2<0.0025 ⑱(r) M1 enclosure DRC ENC V1_fill MA<0.0025 "
            "⑲(s) V1-to-V1 间距 DRC EXT V1_fill<0.225 OPPOSITE ⑳(t) GDS 输出 DFM RDB GDS "
            "㉑(u) 跨输入守门: 生成器跑隐藏 B 规格产 B.rule 含 LAYER 91 0 + 方形 STEP 0.300 BY 0.300(0.050+0.250) + SIZE 0.050 BY 0.050 + ENC<0.0030(杀硬编码 A)"
        ),
    },
}

# dedup guard: skip if task_id already present
existing = []
if os.path.exists(JSONL):
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if e.get("task_id") == CASE:
                    print("SKIP: %s already in jsonl" % CASE)
                    sys.exit(0)
                existing.append(e["task_id"])
            except Exception:
                pass

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("APPENDED %s to %s (jsonl now %d cases)" % (CASE, JSONL, len(existing) + 1))
