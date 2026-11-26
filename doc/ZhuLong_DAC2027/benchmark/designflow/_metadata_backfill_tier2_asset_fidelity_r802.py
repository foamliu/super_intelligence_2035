#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r802.py — r802 档2 asset_fidelity backfill batch2.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note backfill, 32→235) done. r801 档2 batch1 (+12, 106→118) done.
      本轮 r802 推进 档2 batch2 — 12 cases (alphabetical next 12 missing, BistOsc..CbrForceMechanismExplain).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 / 真实 scp 自内网 / 真实用户 paste)
  - synth_deck   : A = 合成 SPICE deck/stim/cell 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/source-file fixture
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver。
      A-faithful 强信号 = prompt 显式 "真实"/"verbatim"/"逐字摘录"/"现场抽取的真实产物"/"真实 scp 自" 或
                          asset 文件 header 明记 verbatim from trace (含真实内网路径) 或
                          asset 内容 = 真实用户 paste 的 verbatim 文本 (track=faithful + 内容与 prompt 引用一致)。
      synth 信号 = track=synthesized / portability reframe / "样本"/"合成"/"self-contained sample" / 通用名文件 /
                   asset header 明记 "BROKEN VERSION (shipped to SUT as asset)" / "sample" / "fixture"。

apply: cases/B/<case>.json metadata 新增 asset_fidelity (末位 key, 保留键序),
       indent=2 ensure_ascii=False, round-trip identical 验过;
       B.jsonl 双存储同步 (scripts/build_jsonl.py --shard B rebuild)。
post-verify: asset_fidelity present count before→after; 395/395 valid JSON; 字段值分布; test_rationale 未动。
"""
import json, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_B = os.path.join(BENCH, "cases", "B")

# case_id -> (asset_fidelity, rationale)
BATCH = {
    "EDA-Eval-DesignFlow-BistOscRccReorder-001": (
        "synth_deck",
        "T_BistOsc.sp + gen_osc_case.py + T_BistOsc.log 均合成 fixture (T_BistOsc.sp header 'BROKEN ... shipped to SUT as asset' / "
        "gen_osc_case.py docstring 'BROKEN VERSION (shipped to SUT as asset)'; T_BistOsc.log 模拟 FineSim V-2023.12 输出含真实 hostname/username "
        "johnl@hfeg0pfn120 但为合成失败日志 fixture); track=synthesized; 真实 DRAM BIST osc deck 在 johnl /proj 不可达; "
        "reframe=portability 真跑 finesim 验 RCC include 修复",
    ),
    "EDA-Eval-DesignFlow-BlSpfCapClassify-001": (
        "synth_data",
        "sample.spf 合成 SPF 1.5 样例 (header '*SPF 1.5 / *|DESIGN BL_ROUTING / *|DATE 2026-11-10 / *|TCF TYP_-40_RCC', 含 BL0..BL15 16 根样本); "
        "example_output_A.csv 合成期望输出样本; config.json 合成 SPF 格式说明; track=synthesized; "
        "真实 BL_routing_E1/E2 等 SPF 结果在 mhyu /proj/x0s0f/V0/ver/pex/mhyu 内网不可达; reframe=portability CLI 解析器",
    ),
    "EDA-Eval-DesignFlow-BmatrixRerunGen-001": (
        "A-faithful",
        "testdir_A/bmatrix_output_A.txt = 用户 yuankong 在 trace 中 verbatim 粘贴的 bmatrix -f 真实输出 "
        "(Fail/Pass 行含真实 primesim CRC001/CRC002/CRC005/CRC010 测试名, 与 prompt verbatim 引用一致); "
        "track=faithful; prompt 为 yuankong 原话 verbatim 含真实 /proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_csgd 路径; "
        "task_brief.md 交付接口; 真实 bmatrix 二进制 + MatrixRun 目录在 /proj 内网不可达但输入 A 文本为 trace verbatim paste",
    ),
    "EDA-Eval-DesignFlow-BndGaussPwlGen-001": (
        "no-asset",
        "0 attachment (仅 prompt.txt + task_brief.md); prompt.txt = joeyl @ hfeg0plg49 trace 1790572773219_t5osd U#2 逐字原话 (attachment desc 显式 A-faithful 标记指 prompt 忠实, 非 asset 文件); "
        "task = GENERATE 带限高斯噪声 SPICE PWL 脚本 (generate_noise_pwl.py), 无输入 asset 文件; "
        "track=faithful 指 prompt 忠实; 按 r801 AcSimHowtoGuide 惯例 0 attachment = no-asset (workdir 无 RAG docs, 纯生成任务)",
    ),
    "EDA-Eval-DesignFlow-BridgeCfgDiag-001": (
        "synth_data",
        "12 文件分 3 子目录合成 env/config/log fixture: bridge_env/(actual_host_info.txt+aether_ini_status.txt+env_vars.txt+port_formula.txt) + "
        "err_logs/(aether_log.txt+conn_test_38865/38869.log+deep_ping_error.log+gedit_error.log) + settings/(cline_mcp_settings.json+identity.json+ip_port.json); "
        "actual_host_info.txt 含真实 IP/hostname (hfeg0pkn005/10.129.8.235/bond0 10.129.2.14) 但为合成环境快照 reconstruction; "
        "aether_log.txt 合成 Aether 启动日志含 '# NOTE: no CXMT_zhulong_EDAAgent.py loaded' 注释; track=None; "
        "reframe=diagnose Q&A->produce (e0047527 29 轮 ECONNREFUSED 排查); 真实桥接环境在 hfeg0pkn005 不可达",
    ),
    "EDA-Eval-DesignFlow-CTLEAC-001": (
        "synth_deck",
        "dut_ctle_A.sp + tb_ctle_ac_A.sp 合成 CTLE deck (desc 'ctle_alenxu SpiceAgent_Skill DFE 库实测', 真实 ctle_alenxu.sp 在 alenxu SpiceAgent dir 不可达); "
        "meas_sample_A.log + op_sample_A.op 合成 FineSim 样本片段 (header 'FineSim sample .log ... for the VISIBLE testbench A', 含 .meas idd 不可靠提示); "
        "spec_A.json 合成 spec (dc_g>=6dB/nyq>=10dB/bw>=10GHz/idd<3mA); track=None; reframe=portability+produce 通用 harness 真跑 FineSim",
    ),
    "EDA-Eval-DesignFlow-CTLESpec-001": (
        "synth_deck",
        "dut_a.sp + tb_a.sp 合成 CTLE deck (desc 'cwei SpiceAgent wb03t CTLE 设计流', 真实 dut_ctle.sp 在 cwei SpiceAgent_V2/design/ctle/ 不可达, "
        "ctle_a source-degenerated diff pair + R||C degeneration + R load + 理想尾电流, inline 自包含); "
        "spec_a.json 合成 spec 表 7 行 (dc_g/hf_g/peaking/fpeak/bw/vcm_out/idd); track=None; reframe=portability 通用 spec 合规 harness 真跑 FineSim -spice",
    ),
    "EDA-Eval-DesignFlow-CTLETranDeck-001": (
        "A-faithful",
        "ctle_act_ind.sp = 真实 CTLE AC 仿真 deck verbatim 自 kaixuanx /proj/m2701/V0_DDR4/workdir/kaixuanx/simulation/CTLE_active_ind 目录 "
        "(.inc '//home/adaml/MySimuSettings/option_hspice.sp' 含真实用户 adaml sim settings 路径, 真实 .inc switch.sp); "
        "netlist = 真实 subcircuit 定义 (switch_close 等, Library intDEV); track=faithful; "
        "prompt = kaixuanx 原话 verbatim 含真实 /proj/m2701/V0_DDR4 路径; reframe=produce 瞬态仿真脚本重写",
    ),
    "EDA-Eval-DesignFlow-CaSkewEdgeStat-001": (
        "synth_data",
        "ca_wave.vec 合成文本表导出 finesim .fsdb 波形 (header '# finesim .fsdb export: CA<5:0> debugpin_ca, DDR6 CAIB postsim', 列 time ca5..ca0); "
        "skew_spec.json 合成统计时间窗与边沿类型 spec; track=synthesized; "
        "真实 .fsdb 在 renfengc /rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/Golden008_SS0.92V-10C_X2P3.fsdb 内网不可达; "
        "reframe=Q&A analysis->produce-tool skew 计算器 (renfengc U0 逐字 '@.../Golden008_SS0.92V-10C_X2P3.fsdb check CA <5:0> max skew')",
    ),
    "EDA-Eval-DesignFlow-CabufPvtDatAudit-001": (
        "synth_data",
        "12 .dat 文件合成 PVT corner 结果 fixture (TT/FF/SS × df0/dr0/tf0/tr0, header '#corner : TT / # type : output delay ... / 0.92 25 1.418e-10'); "
        "spec.json 合成 SPEC (max_delay_s/max_transition_s/delay_meas/transition_meas); task_brief.md 交付接口; track=synthesized; "
        "真实 cosim_timing_param/IO_CABufCore/ .dat 在 e03179 vam-agent 建模 run (netlist /home/e03179/IO_CABufCore_TT0.92V25C) 不可达; "
        "reframe=portability+produce PVT 审核报告生成器 (hidden-B 不同 .dat 集 + 不同 SPEC 反背题)",
    ),
    "EDA-Eval-DesignFlow-CapCharProps-001": (
        "A-faithful",
        "ntn_V1 + ntn_G4BCIP + ptn_V1 + ptn_G4BCIP = 真实 MOS 电容 Cgg characterization 数据文件 verbatim 自 owench /home/owench/G5vsV1/test_yaq/Capacitance 目录 "
        "(4 份 Cgg 数据 ntn/ptn × G4BCIP/V1, 含 Cg/Cd 列); track=faithful; "
        "prompt = owench 原话 verbatim '新建一个Capacitance2文件夹 然后根据/home/owench/G5vsV1/test_yaq/Capacitance计算一下相关性质 能在已有功能的基础上计算Ceff Cch Cgd0这三个性质吗？' 含真实 /home/owench 路径; "
        "task_brief.md 交付接口; reframe=produce compute_properties.py (积累区法 Ceff/Cch/Cgd0)",
    ),
    "EDA-Eval-DesignFlow-CbrForceMechanismExplain-001": (
        "synth_data",
        "refresh_cbr.run + proj_monitors.sv 合成 source-file fixture 捕获 LPDDR6 验证平台 Force_CBR 机制结构 "
        "(refresh_cbr.run 含 Config_Timing/regression_name='Refresh_CBR'/lpddr6.tb_control 配置; proj_monitors.sv 含 Force_CBR task 签名 random/trfc/cbr/boundary/sc/force_red); "
        "requirements.json + scenario.txt + task_brief.md 合成任务说明 (scenario.txt 给真实平台路径 /rundata/decqa/V0/simdir/verilog/lein/1103_lp6tb 但 asset 文件为 reconstruction); "
        "track=None; reframe=explain Q&A->produce (lein 7 轮追问 Force_CBR 底层实现); 真实平台源文件在 /rundata 内网不可达, asset 为合成 fixture 供分析器解析",
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

    print("=== 档2 asset_fidelity backfill r802 batch2 ===")
    print("to apply:", len(BATCH), "| applied:", after, "| skipped:", len(skipped))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-58s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIP     %-58s : %s" % (cid, reason))

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
    print("value distribution (canonical short values only):")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        # only print short canonical values to keep output readable
        if len(k) <= 40:
            print("  %-40s : %d" % (k, v))
    long_form = sum(v for k, v in dist.items() if len(k) > 40)
    print("  (long-form legacy values total)            : %d" % long_form)

    # post-verify: all 395 valid JSON + test_rationale untouched spotcheck
    print("\n--- post-verify: 395 valid JSON + test_rationale spotcheck ---")
    n_valid = 0
    n_rationale = 0
    for fname in sorted(os.listdir(CASES_B)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CASES_B, fname), encoding="utf-8") as f:
            dd = json.load(f)
        n_valid += 1
        rat = dd.get("metadata", {}).get("test_rationale", "")
        if rat:
            n_rationale += 1
    print("valid JSON: %d / 395 | has test_rationale: %d" % (n_valid, n_rationale))


if __name__ == "__main__":
    main()
