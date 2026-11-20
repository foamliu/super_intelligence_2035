#!/usr/bin/env python3
# Append EDA-Eval-DesignFlow-Vcc2scVarJudge-001 to EDA-Eval-DesignFlow_B.jsonl
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-Vcc2scVarJudge-001"

check_src = open(os.path.join(BENCH, "reference", CID, "check.py")).read()

record = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": (
        "/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scstdby_tran.sp 用 bsub -q fqueue3 finesim -i Vcc2scstdby_tran.sp "
        "-o /proj/dscqa/V0/simdir/hspice/tongni/7_Vcc2scStdby/261019sim_Vcc2scStdby_tran/ 这个语句丢仿真，"
        "/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scstdby_tran_SPEC.sp这个是我们的SPEC，variation 是 所有corner的电压的分布范围要小于5mV，"
        "所以你要读取measure的文件，做判断，并给出优化策略\n"
        "assets/Vcc2scstdby_tran.mt0\n"
        "assets/Vcc2scstdby_tran_SPEC.sp\n"
        "assets/Vcc2scstdby_tran.sp"
    ),
    "attachments": [
        "assets/EDA-Eval-DesignFlow-Vcc2scVarJudge-001/Vcc2scstdby_tran.mt0",
        "assets/EDA-Eval-DesignFlow-Vcc2scVarJudge-001/Vcc2scstdby_tran_SPEC.sp",
        "assets/EDA-Eval-DesignFlow-Vcc2scVarJudge-001/Vcc2scstdby_tran.sp",
        "assets/EDA-Eval-DesignFlow-Vcc2scVarJudge-001/prompt.txt",
        "assets/EDA-Eval-DesignFlow-Vcc2scVarJudge-001/task_brief.md",
    ],
    "test": check_src,
    "budget": {"max_turns": 30, "timeout_sec": 2400},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "domain": "spice_sim",
        "tier": "L2",
        "track": "faithful",
        "trace_source": {
            "user": "tongni",
            "host": "hfeg0pkn001",
            "ip": "10.129.2.10",
            "session_file": "1792373325953_z6mt7.messages.json",
            "match_count": 83,
            "real_task_summary": (
                "tongni @ hfeg0pkn001 上对 Vcc2scStdby(待机电源切换)做多 PVT corner 瞬态仿真后要求读取 measure 文件、"
                "判断 variation(所有 corner 电压分布范围)<5mV 的 SPEC、并给出优化策略。用户首轮意图(逐字)：用 bsub finesim 跑 "
                "Vcc2scstdby_tran.sp，SPEC 在 Vcc2scstdby_tran_SPEC.sp，variation<5mV，读取 measure 文件做判断并给优化策略。"
                "trace 里 agent 经 list_allowed_files/read_files/run_approved_command 读 SPEC.sp(2 行：Vcc2sc_unload/Vcc2sc_load1mA "
                "Variation<5mV)+tran.sp(.tran 1n 300u, iload PWL 0→0.1mA→1mA, 两条 .MEASURE TRAN AVG V(Vcc2sc!) FROM=60u/110u)+"
                "check_vcc2sc_stdby_var.py(金标准判定器)，修 LSF/LD_PRELOAD 环境坑 + license 转发后跑通 finesim job 993022(121 PVT corner, "
                "2.8h)，修判定器大小写敏感 bug(finesim 把 Vcc2sc_load1mA 小写化成 vcc2sc_load1ma)，最终判定 FAIL：Vcc2sc_unload "
                "variation=5.130mV(超 2.6%)，Vcc2sc_load1mA variation=15.260mV(超 3 倍)；按温度拆分定位 -40°C unload 3.70mV / 130°C "
                "load1mA 15.26mV 为主要超标点；优化建议提高环路增益+输出级驱动+温度补偿。本 case 抽取其「解析 finesim .mt0 measure "
                "文件→逐指标计算跨 corner variation(max-min)→大小写不敏感匹配 SPEC→PASS/FAIL 判定+按温度拆分+根因+优化建议→结构化 "
                "JSON」这一可复用判定子流，要求交付通用 judge_vcc2sc_var.py(CLI)。真实 .mt0 在 /proj/dscqa 权限拒，A 资产按 trace "
                "read_files 恢复的真实格式($DATA1/.TITLE/列头 vcc2sc_unload vcc2sc_load1ma temper alter#)忠实复现 121 corner "
                "匹配金标准统计(min 0.89724/max 0.90237/var 5.130mV；load1mA min@alt115/max@alt83 均 130°C, var 15.260mV)；"
                "hidden B 不同结构(81 corner/3 温区 25,-40,125°C/不同指标名 vcc2sc_vout_light,vcc2sc_vout_full/SPEC 限 4mV/"
                "light PASS 2.6mV + full FAIL 8.6mV)强制泛化防硬编码。"
            ),
        },
        "test_rationale": (
            "14 条断言：①(a) submit.zip 有效且含 judge_vcc2sc_var.py 且 py_compile 通过 "
            "②(b) 候选在隐藏 B 上 exit 0/1 且产出合法 report.json(dict) "
            "③(c) report.json 含全部 7 个顶层必需键(n_corners_total/metrics/per_temperature/overall_judgement/root_causes/optimization_suggestions/method) "
            "④(d) 隐藏 B 的 n_corners_total==81(非 A 的 121, 防硬编码) "
            "⑤(e) 隐藏 B 的 overall_judgement==FAIL(full 超标致整体 FAIL) "
            "⑥(f) 隐藏 B 的 Vcc2sc_vout_light judgement==PASS 且 variation≈2.6mV<4mV 限 "
            "⑦(g) 隐藏 B 的 Vcc2sc_vout_full judgement==FAIL 且 variation≈8.6mV>4mV 限 "
            "⑧(h) 隐藏 B 的 per_temperature 恰含 {25,-40,125} 三个温区键 "
            "⑨(i) 隐藏 B 的 full 指标 min_corner.temper==125 且 alter==75(唯一最差角点) "
            "⑩(j) root_causes 非空且含 metric==Vcc2sc_vout_full 的 FAIL 条目 "
            "⑪(k) optimization_suggestions 非空且引用 FAIL 指标 "
            "⑫(l) 跨输入守卫: 候选在可见 A 上非崩溃且 overall==FAIL(A 为 FAIL/FAIL) "
            "⑬(m) 跨输入守卫: A 的 Vcc2sc_unload variation≈5.13mV 且 Vcc2sc_load1mA variation≈15.26mV 且 n_corners==121(证明解析器跨输入泛化, 非硬编码 B 的 81/2.6/8.6) "
            "⑭(n) 大小写不敏感 SPEC→列匹配: A 的 measure 列名小写 vcc2sc_load1ma 而 SPEC 用 Vcc2sc_load1mA, 必须 present==True 且定位到 load1mA min@alter115/T=130, max@alter83/T=130(trace 金标准最差角点, 证明修了 trace 里真实的大小写匹配 bug)"
        ),
        "k_rationale": 14,
        "k_check": 14,
    },
}

jsonl_path = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
with open(jsonl_path, "a") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")
print("appended", CID, "to", jsonl_path)

# verify count
n = sum(1 for _ in open(jsonl_path))
print("jsonl_B lines now:", n)
