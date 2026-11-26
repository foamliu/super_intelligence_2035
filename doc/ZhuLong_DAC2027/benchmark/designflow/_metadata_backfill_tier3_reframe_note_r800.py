#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r800 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r756_spotcheck35.tsv (batch34, 1/1 keep_reframe case 待 apply;
        spotcheck35 = audit 收口轮, 全集 12 case 中唯一未审 1 case SnmAnalyzerExplain-001).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r799 档3 batch9-33 done (reframe_note 32->234).
本轮 r800 档3 batch34 (r756 spotcheck35, 1 case 待 apply). reframe_note 234->235.

reframe_note text = spotcheck35 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck35 1 case: 1 keep_reframe + 0 keep_faithful):
  - Q&A-driver (explain Q&A -> produce-source-analyzer-tool 给 check 牙): 1 case (100% Q&A-driver)
    SnmAnalyzerExplain (e0030760, Q&A-explain -> produce-source-analyzer-tool)
  - portability-driver: 0 cases
  - harness-driver: 0 cases
  - sub-skill-driver: 0 cases

spotcheck35 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity/k_check/shard/track,
                     仅在 note 文本标注 metadata bug 待 @A 档1/档2 补 sweep):
  - layer=L1 ✓ 已正确 1/1 (metadata 已标 L1, check 仅 subprocess 跑候选 python 解析源码文本+验 JSON, 无 EDA 二进制)
    -- 对照 r799 batch33 出现的缺标应补 L2/误分类双向, 本批 reframe 集 layer 已正确(延续 r797 零 layer bug 形态)
  - **check.py header 误标 k_check=19 应 21** (实际条件 a-u=21, metadata 已正确标 21)
  - k_check=21 ✓ 已标 1/1 (metadata 已标; header/circled 一致性: header 误 19, circled=21)
  - level 缺标 1/1 (应 L1), shard 缺标 1/1 (应 B), track 缺标 1/1 (应 faithful)
  - asset_fidelity ✓ 已标 1/1 (A=trace-verbatim 761 行 + hidden B=synthesized 8T-SRAM)
  - **0 例 pre-existing header != circled-mark count** (1/1 circled=21 ✓; header 误 19 是 header 自身 bug 非 header!=circled)
  - **reframe 受旧规则「Q&A=weak 不可造」驱动, 2026-11-15 令已将 Q&A/explain 恢复为合法任务形态**;
    -v2 A档 explain-Q&A 变体已存在(cases/B/EDA-Eval-DesignFlow-SnmAnalyzerExplain-001-v2.json),
    本 v1 reframe_note 保留作旧规则产物历史对照
  - e0030760 SRAM SNM 三连之一(同 user 同 host pkn004, 与 SnmSquareValidator 同 user-cluster)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-SnmAnalyzerExplain-001":
        "mc_snm_analyzer 源码结构化分析器->produce-tool (Q&A-explain->produce-source-analyzer-tool reframe, §4 有牙必要, r756 spotcheck batch34): 用户 e0030760@hfeg0pkn004 U0 verbatim「这个脚本处理 HSNM、RSNM，和统计结果的逻辑是什么？分别在做什么？」(explain-Q&A 讲解脚本逻辑), trace 金标准(cline 28 msgs): agent 用 read_files 分 4 段读 mc_snm_analyzer.py(761 行 6T SRAM HSPICE MC GUI 分析器)+list_allowed_files+核对 .ms0/.lis/.snm_cache.csv/.butterfly_index 数据格式, 给结构化讲解(总体架构+RSNM/HSNM 蝶形表流式提取状态机+Seevinck 最大内接正方形+14 二分+单调 deque 滑窗+v1.1 单 sample 蝶形查看器 build_lis_index 8MB 块扫+结果缓存+统计 calc_stats n/mean/median/std ddof=1/skew/超额 kurt+sigma 良率 calc_sigma normal sigma/violations/yield/quantile+GUI 60-bin 直方图+8 参数+线程模型+selftest+4 已修复 bug), agent 给文本讲解, A 不可行原因=纯 explain-Q&A(「逻辑是什么？分别在做什么？」=给讲解答案)无 runnable artifact 无 check 牙 -> case 抽取「mc_snm_analyze.py(真跑解析源码产 14-field JSON 报告)」子技能, A 档 verbatim 合规(e0030760 原话逐字含「这个脚本处理 HSNM、RSNM，和统计结果的逻辑是什么？分别在做什么？」+761 行脚本背景+/proj/lacaa/.../MC_hspice/HD_FS_CH252_6T/ttg_25T_0.75V/ 路径), reframe 由 Q&A-driver 非配额驱动; trace 用户=explain-Q&A(给讲解答案), case 收敛为 produce-tool(写 mc_snm_analyze.py 真跑解析源码产 14-field JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B 8T-SRAM 合成变体 node_names/params/data_source_exts/binary_search_iters/histogram_bins/phi_inv_range/phi_inv_iters/stats_fields/sigma_fields/index_block_mb/cache_suffix/index_validation_key/sram_type/fixed_bugs_count 14 字段非 A + §4.4 zip 含脚本+py_compile+可调用入口+hidden B 在位未泄漏+B 上 exit0 产 JSON+3 次重跑 byte-identical+JSON dict+14 schema keys 齐全+A-leak string/numeric 守卫防硬编码 A, check 仅 subprocess 跑候选 python 解析 .py 源码文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 mc_snm_analyzer 源码结构化分析器; check.py 21 断言(a-u)验候选 mc_snm_analyze.py+JSON 报告 => 收敛为 produce-source-analyzer-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。**注: reframe 受旧规则「Q&A=weak 不可造」驱动, 2026-11-15 令已将 Q&A/explain 恢复为合法任务形态, -v2 A档 explain-Q&A 变体已存在(cases/B/...-v2.json)恢复原意图, 本 v1 reframe_note 保留作旧规则产物历史对照**; layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 解析源码文本+验 JSON, 无 EDA 二进制, 原始 trace 跑 HSPICE MC 5000 但 check 阶段不跑 HSPICE), level 缺标应 L1, k_check=21 ✓ 已标(check.py header 误标 19 应 21, 实际条件 a-u=21), asset_fidelity ✓ 已标(A=trace-verbatim 761 行 + hidden B=synthesized 8T-SRAM), shard 缺标应 B, track 缺标应 faithful, domain=spice_sim ✓, e0030760 SRAM SNM 三连之一(同 user 同 host pkn004, 与 SnmSquareValidator 同 verb-homogeneous SNM 分析 user-cluster), metadata bug 待 @A apply 档1/档2 补 sweep。",
}


def main():
    applied = 0
    skipped = []
    for case_id, note in REFRAME_NOTES.items():
        path = os.path.join(CASES_DIR, f"{case_id}.json")
        if not os.path.exists(path):
            skipped.append((case_id, "MISSING FILE"))
            continue
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "reframe_note" in md:
            skipped.append((case_id, "ALREADY HAS reframe_note"))
            continue
        md["reframe_note"] = note
        d["metadata"] = md
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        applied += 1
        print(f"  APPLY {case_id}")
    print(f"\nApplied: {applied} / Skipped: {len(skipped)}")
    for cid, why in skipped:
        print(f"  SKIP {cid}: {why}")


if __name__ == "__main__":
    main()
