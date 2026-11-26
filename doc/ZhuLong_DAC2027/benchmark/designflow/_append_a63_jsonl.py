#!/usr/bin/env python3
"""Append IddBlkCmpHighlight-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os

JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"
CHECK = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/IddBlkCmpHighlight-001/check.py"

with open(CHECK) as f:
    check_src = f.read()

entry = {
    "id": "EDA-Eval-DesignFlow-IddBlkCmpHighlight-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": open("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/IddBlkCmpHighlight-001/A/prompt.txt").read(),
    "attachments": [
        "assets/IddBlkCmpHighlight-001/A/prompt.txt",
        "assets/IddBlkCmpHighlight-001/A/task_brief.txt",
        "assets/IddBlkCmpHighlight-001/A/iddblk_A1.csv",
        "assets/IddBlkCmpHighlight-001/A/iddblk_A2.csv",
    ],
    "test": check_src,
    "metadata": {
        "domain": "analog_context",
        "task_name": "IddBlkCmpHighlight",
        "scenario": "DDR5 IDD 电流测量 iddblk.csv 双文件 cellName 级差分高亮: DRAM 验证工程师 jianwang 在 hfeg0pkn001 上对 FineSim 仿真目录 MatrixRun_Netlist_IDD_20260902pm_RevC_JEDEC_OC/ 下两个 corner(x4 idd0RevCx4-6400 vs x8 idd2n-6400)的 iddblk.csv 做 cellName 匹配后按公式 calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64 计算每 cell 指标, 求 diff(f2-f1)+diff_pct, 标记 |diff|>threshold 大差异项, 输出 7 列 CSV 按 |diff| 降序. 实测 88 common cell, 0 only-file, top diff d_banklogic -658.8(-17.5%)/c_cmddec -569.3(-45.1%)/ag_analogbankx2l -356.1(-99.1%). 本用例把专有 /proj FineSim CSV 抽象成纯文本 iddblk.csv(cellName,category,ext_vdd!,ext_vddq!,ext_vpp!,vcc!,vdd1!), 去掉 FineSim/Verdi 依赖, 保留'按列名解析 ext_vdd!/ext_vddq!/ext_vpp! → 公式 calc → cellName 匹配 → diff/pct → 阈值高亮 → 排序输出'这条 EDA 数据流核心.",
        "direction": "csv.DictReader 按列名读 ext_vdd!/ext_vddq!/ext_vpp!(不按列下标硬编码, 忽略 vcc!/vdd1! 等其它轨道) → calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64 → 按 cellName 取两文件 common 行(only-in-one 排除) → diff=calc_f2-calc_f1, diff_pct=diff/calc_f1*100(f1=0 时 0) → big_diff_flag='Y' iff |diff|>threshold(CLI arg, 默认 10.0) → 输出 7 列 CSV(cellName,category,calc_f1,calc_f2,diff,diff_pct,big_diff_flag) 按 |diff| 降序, category 取 file1",
        "layer": "post-sim IDD current CSV diff / cellName-matched formula comparison",
        "topic": "iddblk.csv 双文件 cellName 匹配 + ext_vdd!+ext_vddq!+ext_vpp!*1.64 公式 + diff/pct + 阈值高亮 + 排序输出",
        "difficulty": "L1",
        "design": "B-grade synthesized; A(visible)=prompt+task_brief+iddblk_A1.csv(14行 12 common+2 only-A1)+iddblk_A2.csv(14行 12 common+2 only-A2), cell 名 xa_/xb_/..., SUT 写 idd_blk_cmp.py 跑 A 并打包; B(hidden)=assets/.../hidden/iddblk_B1.csv(23行 20 common+3 only-B1)+iddblk_B2.csv(22行 20 common+2 only-B2), cell 名 yd_/ye_/yf_..., 与 A cell 名/数值全不相交, 不进 SUT 沙盒, 判分器跑 SUT on B 验数值泛化; C(anti-hardcode, 嵌入 check.py)=zf_/zg_ 10 common+1 only-C2, **列顺序打乱**(category,cellName,vdd1!,ext_vpp!,ext_vdd!,vcc!,ext_vddq!,misc)+额外 misc 列, 与 A/B cell 名/数值/列顺序全不相交, naive 按列下标解析或硬编码 A 值在 C 上必败. 关键判别: ①按列下标而非列名 → C 列顺序打乱 cond m FAIL ②硬编码 A cell 名/数值 → B 不同值 cond g/h/m FAIL ③硬编码阈值 10 → cond n/o(threshold 50) FAIL ④不排除 only-in-one → cond e/f(行数/cellName 集合) FAIL ⑤忘 ×1.64 或公式错 → cond g/h FAIL. check.py 16 条件 a-p 独立 oracle(重解析 CSV 不 import SUT)+subprocess 真跑 SUT on A/B/C+3 negatives(empty_stub/print_only_stub/naive_hardcode). python3 标准库可跑, 无 EDA license.",
        "tcr_refs": [],
        "heavy": False,
        "wall_time_sec": 2400,
        "trace_source": {
            "user": "jianwang",
            "host": "hfeg0pkn001",
            "session_file": "1791955659176_a63u6",
            "match_count": 23,
            "real_task_summary": "DDR5 IDD iddblk.csv 双文件差分高亮: jianwang 在 hfeg0pkn001(10.129.32.75)上对 FineSim 仿真目录 /proj/drgqa/V0/simdir/finesim/drgqaF/MatrixRun_Netlist_IDD_20260902pm_RevC_JEDEC_OC/ 下两个 corner 的 iddblk.csv(idd0RevCx4-6400.x4.TT1.166v98c.current/iddblk.csv x4 配置 vs idd2n-6400.x8.TT1.166v98c.current/iddblk.csv x8 配置)要求按 cellName 匹配后计算指标 calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64, 求差值并高亮差异大的项, 再筛 |diff|>10 做柱状图. agent 写 compare_idd.py(csv 按列名读 ext_vdd!/ext_vddq!/ext_vpp!+cellName 匹配+公式 calc+diff/pct+big_diff_flag+输出 CSV+HTML)和 plot_idd_compare.py(matplotlib 柱状图). 实测 88 common cell/0 only-file, top diff d_banklogic 3773.2→3114.4=-658.8(-17.5%)/c_cmddec 1262.3→693.1=-569.3(-45.1%)/ag_analogbankx2l 359.2→3.1=-356.1(-99.1%), |diff|>10 共 26 个. 本用例抽象为纯 stdlib CSV 处理 SUT, A 可见(12 common+2/2 only, xa_/xb_ cell 名), B 隐藏(20 common+3/2 only, yd_/ye_ cell 名不同数值), C 嵌入 check 反硬编码(zf_/zg_ 10 common+1 only-C2, 列顺序打乱+misc 列), 三者 cell 名/数值/列顺序全不相交."
        },
        "test_rationale": "16 条断言：①submit.zip 含 idd_blk_cmp.py 且 py_compile 通过且无禁用 import/call(subprocess/socket/urllib/ctypes/numpy/pandas/eval/exec/os.system/popen/__import__)且源码不泄漏 B/C cell 名前缀(yd_/ye_/yf_/yg_/yh_/yi_/yj_/yk_/yl_/ym_/yn_/yo_/yp_/zf_/zg_) ②SUT 跑可见 A 组 exit 0 且产出非空 7 列 CSV ③SUT 跑隐藏 B 组(--threshold 10) exit 0 且产出非空 CSV ④B 输出 CSV 7 列顺序固定为 cellName,category,calc_f1,calc_f2,diff,diff_pct,big_diff_flag ⑤B 数据行数==20(两文件 common cell; only-in-one 排除) ⑥B cellName 列集合==20 个 common B cell(集合相等) ⑦B 全部 20 行 calc_f1==ext_vdd!+ext_vddq!+ext_vpp!*1.64 独立 oracle(tol 1e-3) ⑧B 全部 20 行 calc_f2==独立 oracle ⑨B 全部 20 行 diff==calc_f2-calc_f1(tol 1e-3) ⑩B 全部 20 行 diff_pct==diff/calc_f1*100(tol 1e-3) ⑪B 行按 |diff| 降序排列 ⑫B 全部 20 行 big_diff_flag=='Y' iff |diff|>10 ⑬反硬编码: SUT 跑嵌入 C(列顺序打乱+额外 misc 列+1 only-C2)行数==10 且全部 calc_f1/f2==C-oracle(证按列名解析非下标+无 A/B 值硬编码) ⑭C --threshold 50 → big_flag==8(证阈值参数化非硬编码 10) ⑮B --threshold 50 → big_flag==15(≠阈值 10 时的 20, 证 --threshold CLI arg 生效) ⑯三种负向(empty_stub/print_only_stub/naive_hardcode)在 B 上全 FAIL(任一产出 20 行且 calc 与 oracle 一致则 cond p FAIL)"
    }
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended. total lines now:", sum(1 for _ in open(JSONL)))

# round-trip verify
o = json.loads(open(JSONL).readlines()[-1])
assert o["id"] == "EDA-Eval-DesignFlow-IddBlkCmpHighlight-001"
assert o["mode"] == "design_flow"
assert o["entry_point"] == "outputs/submit.zip"
assert "ext_vdd!+ext_vddq!+ext_vpp!*1.64" in o["metadata"]["test_rationale"]
assert o["test"].startswith("#!/usr/bin/env python3")
assert o["metadata"]["trace_source"]["session_file"] == "1791955659176_a63u6"
print("round-trip OK")
