#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r801.py — r801 档2 asset_fidelity backfill batch1.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer normalize 160 cases) done.
      r773-r800 档3 (reframe_note backfill, batch9-batch34, 32→235) done.
      本轮 r801 启动 档2 (asset_fidelity deepread) batch1 — 12 cases (alphabetical first 12 missing).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
分类法 (本批确立 canonical vocabulary):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 / 真实 scp 自内网)
  - synth_deck   : A = 合成 SPICE deck/stim/cell 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config data fixture
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver。
      A-faithful 强信号 = prompt 显式 "真实"/"verbatim"/"逐字摘录"/"现场抽取的真实产物"/"真实 scp 自" 或
                          asset 文件 header 明记 verbatim from trace (含真实内网路径)。
      synth 信号 = track=synthesized / portability reframe / "样本"/"合成"/"self-contained sample" / 通用名文件。

apply: cases/B/<case>.json metadata 新增 asset_fidelity (末位 key, 保留键序),
       indent=2 ensure_ascii=False, round-trip identical 验过;
       B.jsonl 双存储同步 (build_jsonl.py --shard B rebuild, gitignored build product, 本地校验一致)。
post-verify: asset_fidelity present count before→after; 395/395 valid JSON; 字段值分布; test_rationale 未动。
"""
import json, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_B = os.path.join(BENCH, "cases", "B")

# case_id -> (asset_fidelity, rationale)
BATCH = {
    "EDA-Eval-DesignFlow-AOI21ArcChar-001": (
        "synth_deck",
        "cell_a.sp header 'visible A model (level-1 MOS, self-contained)' = 合成自包含 AOI21 样本 cell; "
        "spec_a.json 合成 spec (DUT/sizing/loads/corners/stim/spec_limits); 真实 e0029308 cell 在 /proj 内网不可达; "
        "track=faithful 指 prompt/task 忠实, asset 为合成样本",
    ),
    "EDA-Eval-DesignFlow-AcSimHowtoGuide-001": (
        "no-asset",
        "0 attachment; Q&A how-to (用户 ruminji 两轮原话 verbatim '仿真ac 怎么语句'/'ac仿真语句怎么写'); "
        "workdir docs (scenario.txt + api_docs/*) 由 SUT 从 RAG 搜索 pyAether/SKILL/TCL API 文档生成, 非附件 asset",
    ),
    "EDA-Eval-DesignFlow-AetherAutoloadDiag-001": (
        "synth_data",
        "evidence/ 7 文件 (install/user/workdir_aether.ini + aether_startup.log + env_info.txt + user_script.py + askeda_faq.txt) "
        "合成 fixtures 捕获 Aether ini 优先级/加载顺序根因结构 (Priority 1/2/3, first-read-wins, PY_INIT_FILE); "
        "真实 install path /apps/empyrean/.../aether.ini 与用户配置在 hfeg0pkn005 不可达; reframe=diagnose Q&A->produce",
    ),
    "EDA-Eval-DesignFlow-AetherHierNavAnalyze-001": (
        "synth_data",
        "6 JSON (task_spec/state/level_chain/analyze_result/trace_summary/diagnostic) 合成 replicas 捕获 "
        "aeGetCellView 逐层 cellview 链 + analyze_structure 输出 + 驱动链摘要; 真实 e0017906@hfeg0pkn002 Aether 会话不可达; "
        "reframe=exploratory Q&A->produce",
    ),
    "EDA-Eval-DesignFlow-AetherHowToGuide-001": (
        "synth_doc",
        "manual_excerpt.txt Aether 手册 Chapter 71 Setup 结构化摘录 (71.1-71.7 各小节 Menu/选项); "
        "scenario.txt 用户 how-to 问题; task_meta.txt trace 来源元信息; track=synthesized",
    ),
    "EDA-Eval-DesignFlow-AgingDirSeparateTransform-001": (
        "A-faithful",
        "matrixrun.pl header 明记 'aging section verbatim from trace: user dandans @ hfhds201, session 1791768325372_g13dw / "
        "attached file: matrixrun (127029 bytes, 3524 lines); aging block lines 243-354' = verbatim excerpt 自真实 3524 行 matrixrun 脚本; "
        "reframe_note trace-incomplete 指 trace 不完整非 asset 合成",
    ),
    "EDA-Eval-DesignFlow-AgingScriptAnalyze-001": (
        "A-faithful",
        "doc/matrixrun_aging.pl header 'Aging-relevant excerpt of matrixrun_aging (cxmt_runMatrixSim.pl) / "
        "Source: /proj/drcoa/V0/simdir/finesim/drcoaF/RunFile/Vcap/Aging_Sim/matrixrun_aging (3522 lines) / "
        "Excerpt preserves the verbatim aging-related code sections (line ranges noted inline)' = verbatim excerpt 自真实 /proj 脚本; "
        "track=synthesized 指 case B档 reframe, asset A 为 verbatim excerpt",
    ),
    "EDA-Eval-DesignFlow-AmsConfigViewDiag-001": (
        "synth_data",
        "7 文件 (active.state + xrun.log + config_V1/expand.cfg + config/expand.cfg + healthy_xrun.log + verilog_samples/*.v) "
        "合成 AMS config/log/verilog fixtures; 真实 ADE Maestro TV1_PSENSOR_FS_SIM 会话内部不可达; reframe=portability+Q&A->produce",
    ),
    "EDA-Eval-DesignFlow-AnalogOptPipeline-001": (
        "synth_data",
        "circuit_config_A.json + example_results_A.json 合成 (CS amp 模拟退火优化 5 变量 config + 示例结果); "
        "task_brief.md 交付接口; track=synthesized; reframe=portability+produce-action→produce-tool",
    ),
    "EDA-Eval-DesignFlow-AplmmxGen025RootCause-001": (
        "A-faithful",
        "prompt 明记 'workdir 下已经放好三个现场抽取的真实产物'; aplmmx.err 含真实内网路径 "
        "(/proj/drgqx/V0/simdir/.../tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/netlist, /rundata/totem/drgqx/IR/20261105/...); "
        "netlist_inc_snippet.txt + diag_probe.txt 现场抽取 trace-verbatim; reframe=Q&A-why/debug->produce-diagnoser",
    ),
    "EDA-Eval-DesignFlow-BatchHspiceSubmit-001": (
        "synth_deck",
        "stim_A/*.sp (inv3_chain/nand2_drv/clkdiv + sub/leaf.sp + notes.txt) 合成通用样本 stim 文件 (header 'HSPICE stimulus' 通用名); "
        "track=a-faithful 指 prompt 忠实 (chapinc 原话), asset 为合成样本供格式参考; "
        "reframe=portability produce-action run→produce-tool CLI dry-run (真实 LSF bsub 不可达)",
    ),
    "EDA-Eval-DesignFlow-BisecMt0SmCalc-001": (
        "synth_tree",
        "sample_tree/ 合成样本目录树供参考格式 (C_SenCC_*/group*/RESULT/Input_D0.bisec_mt0 结构); "
        "prompt 引用户 xuelianf 原话 verbatim '请写一个程序...', task 忠实; track=synthesized 指 asset 合成",
    ),
}


def main():
    before = 0
    after = 0
    applied = []
    skipped = []
    for cid, (val, why) in BATCH.items():
        fpath = os.path.join(CASES_B, cid + ".json")
        if not os.path.exists(fpath):
            skipped.append((cid, "file not found"))
            continue
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "asset_fidelity" in md:
            skipped.append((cid, "already has asset_fidelity=%r" % md["asset_fidelity"]))
            continue
        before += 1
        # append as 末位 key (preserve existing key order)
        md["asset_fidelity"] = val
        d["metadata"] = md
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        after += 1
        applied.append((cid, val))

    print("=== 档2 asset_fidelity backfill r801 batch1 ===")
    print("to apply:", len(BATCH), "| applied:", after, "| skipped:", len(skipped))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-55s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIP     %-55s : %s" % (cid, reason))

    # post-verify: full cases/B asset_fidelity coverage
    print("\n--- post-verify: cases/B full coverage ---")
    have = 0
    miss = 0
    dist = {}
    for fname in sorted(os.listdir(CASES_B)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CASES_B, fname), encoding="utf-8") as f:
            dd = json.load(f)
        af = dd.get("metadata", {}).get("asset_fidelity")
        if af is None:
            miss += 1
        else:
            have += 1
            dist[af] = dist.get(af, 0) + 1
    print("have asset_fidelity: %d / 395 | miss: %d" % (have, miss))
    print("value distribution:")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        print("  %-15s : %d" % (k, v))


if __name__ == "__main__":
    main()
