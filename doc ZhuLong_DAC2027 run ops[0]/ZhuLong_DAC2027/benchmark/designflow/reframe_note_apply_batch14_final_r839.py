#!/usr/bin/env python3
"""r839 reframe_note backfill batch14-FINAL — close last 4 empty reframe_note B cases.

All 4 are keep_faithful (track=faithful/spice_char, asset_fidelity=A-faithful):
  - WaveViewPanel-001           (k=12, layer=L2 already)
  - WriteDqPsdMappingExtract-001 (k=15, layer=L1 already)
  - XrunLogErrDiag-001           (k=15, layer=None -> also补 L1)
  - ZqCodeLinExtract-001         (k=14, layer=L1 already)

Inserts reframe_note right before the `"asset_fidelity"` key (text insertion,
no json round-trip). For XrunLogErrDiag also inserts `"layer": "L1"` after the
`"track"` line. r839 closes reframe_note 391/395 -> 395/395 = 100%.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

NOTES = {
    "WaveViewPanel-001": (
        None,  # no layer change (already L2; flagged in note as 待@A复核)
        'keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r839 reframe_note backfill batch14-final): 用户 rongjiez@hfeg0pkn005 (sess 1790241096712_s0t3i, mc=23, spice_char 域) 在 ModelQA_0924170807 调试老脚本 openWave.pl 的 WaveView panel 高度 bug——9 个 panel 全设 150 但最后 2 个保持默认矮高度; 根因=尚未 realize 的 panel widget 上 wv_set_size 被默认几何覆盖; 终解=暂存 wv_select_wv_item/wv_set_size 到 @heightCmdList, 循环后先 update idletasks 强制 Tk 几何布局 realization 再统一设高度; 意图形态=produce-action(修 openWave.pl 让 panel 高度全生效); 可便携性=高(real openWave.pl Perl source + .sw0 波形目录结构 scp 便携, asset_fidelity=A-faithful); case 交付修好的 openWave.pl(同形, A-faithful, track=spice_char); reframe_note=None→补(faithful 意图零偏移, produce-action 修脚本属合法任务形态, trace 意图 "panel 高度全生效" 与 case 交付 update idletasks+延迟 wv_set_size 同形映射, asset A-faithful 因 Perl source+波形目录结构便携); check.py 12 断言验 zip 含 openWave.pl + perl -c 通过 + hidden B 上 exit0 生成 openSignal.tcl + Tcl 含 update idletasks + 首条 wv_set_size 出现在 update idletasks 之后(高度命令延迟) + cross-input guard(A≠B 波形目录不同) + 退化 stub FAIL + 确定性一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess(perl 真跑) 保证, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 perl -c+跑 .pl 生成 Tcl 文本无 EDA 二进制, 严格 r747 应 L1, 但沿用既有标不在 reframe_note scope, 留 layer-normalize track 处置)。',
    ),
    "WriteDqPsdMappingExtract-001": (
        None,
        'keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r839 reframe_note backfill batch14-final): 用户 tongfanl@hfhds201 (sess 1791796775106_b1w28, mc=222, spice_sim 域) U#0 逐字「/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local，帮我整理一个表格，当没有定义DQSEL_LH时，write task中的传入参数和PSD0DQ[5:0]、PSD1DQ[5:0]的mapping关系，分成1P12、1P6、2P6、2P3」——提出需求(无 root-cause/fix)整理 Write-task dq-param-bit 到 PSD0DQ/PSD1DQ 的映射表; 金标准=assistant 解析 specdef mode/DQ_BITS + test.sv drive_dq split/sc-branch + genvector column order; 意图形态=produce-tool(解析 SystemVerilog specdef/interface/test/genvector 输出结构化 JSON mapping); 可便携性=高(real .sv source scp 便携, asset_fidelity=A-faithful); case 交付 extract_dq_psd_mapping.py(同形, A-faithful); reframe_note=None→补(faithful 意图零偏移, produce-tool 解析 .sv 出映射表属合法任务形态, trace 意图 "dq-bit→PSD mapping 表" 与 case 交付 JSON modes/sc/psd 映射同形映射, asset A-faithful 因 .sv source 便携); hidden B 用不同 mode 名(M1P8/M1P4/M2P4/M2P2)+不同 DQ_BITS(8/4)+不同 split point(4)+不同 bonded pins(2) 防 hardcoding; check.py 15 断言验 zip 含 .py + py_compile + hidden B exit0 产 JSON + JSON modes 恰 4 模式 + M1P8 dq_bits=8 + sc0/psd0/psd1 映射 + cross-input guard(A≠B mode 名) + 退化 stub FAIL + 确定性 => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1(check 仅 subprocess 跑候选 python 解析 .sv 文本, 不启动 EDA 二进制), k_check=15==k_rationale=15 ✓, 无 reframe, 保留。',
    ),
    "XrunLogErrDiag-001": (
        "L1",
        'keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r839 reframe_note backfill batch14-final): 用户 e0014036@hfeg0pkn004 (sess 1793949945535_873cy, mc=1493, spice_sim 域) 在 /rundata/drcoa/V0/simdir/verilog/e0014036/verilog.ddr5.drcoa.pte.1015/test_nt/noregression.x8 目录下要求「找到 xrun.log 文件，读取内容，检测内部报错」——xrun/xmelab 仿真日志错误诊断; 金标准=assistant check_xrun_log.py 正则 *E,CODE 统计 68 errors(CUVUNF=66/ELBERR=1/RUNERR=1), CUVUNF 根因=monitor 引用 3 个接口字段不存在(tREFI3P9D/ace_flag_count/PracUE_Flg), xmelab elaboration 阶段退出; 意图形态=produce-tool(解析 xrun.log 输出结构化错误诊断 JSON); 可便携性=高(real xrun.log 文本 scp 便携, asset_fidelity=A-faithful); case 交付 check_xrun_log.py(同形, A-faithful); reframe_note=None→补(faithful 意图零偏移, produce-tool 解析 log 出诊断 JSON 属合法任务形态, trace 意图 "读 log 检测报错" 与 case 交付 error_summary/root_cause_code JSON 同形映射, asset A-faithful 因 xrun.log 文本便携); hidden B 用不同 xrun.log(B_xrun.log, 不同 error code 分布); check.py 15 断言验 zip 含 .py + py_compile + B 上 exit0 产 out.json + JSON 含 7 必需键(total_lines/error_summary/total_errors/failed_stage/exit_errors/root_cause_code/missing_iface_fields) + error_summary 统计 + root_cause_code 正确 + cross-input guard(A≠B error 分布) + 退化 stub FAIL + 确定性 => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1(check 仅 subprocess 跑候选 python 解析 log 文本, 不启动 EDA 二进制, r839 layer backfill batch14 补), k_check=15==k_rationale=15 ✓, 无 reframe, 保留。',
    ),
    "ZqCodeLinExtract-001": (
        None,
        'keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r839 reframe_note backfill batch14-final): 用户 clarawu@hfeg0pkn004 (sess 1793781925131_ud2zs, mc=118, spice_sim 域) 为 DDR4 Ron 表征做 zq-code 提取, U#2 逐字「@...Ron_global.ms0 帮我写个脚本，功能和@...extract_zqcode_lin.py一样」——为 PrimeSim HSPICE 多行列式 .ms0 格式(22 列跨 7 物理行/记录)写功能等同于单行 .md0 版 extract_zqcode_lin.py 的脚本: 解析 .ms0→找 rpu_50 最接近 230 的行(PU)和 rpd_50 最接近 230 的行(PD)→输出 pu_zqcode_lin + pd_zqcode_lin; 金标准=assistant extract_zqcode_lin_ms0.py(多行 header 累积直到 alter# + 数据 token 累积成 22 列记录), 跑通 64 条记录; 意图形态=produce-tool(解析 .ms0 输出 zq-code 提取表); 可便携性=高(real .ms0 文本 scp 便携, asset_fidelity=A-faithful); case 交付 extract_zqcode_lin_ms0.py(同形, A-faithful); reframe_note=None→补(faithful 意图零偏移, produce-tool 解析 .ms0 出 zq-code 表属合法任务形态, trace 意图 "多行 .ms0 zq-code 提取" 与 case 交付 pu/pd_zqcode_lin 表同形映射, asset A-faithful 因 .ms0 文本便携); hidden B 用不同 .ms0(B_ron_global.ms0, 不同 rpu/rpd 值与 alter# 标签); check.py 14 断言验 zip 含 .py + py_compile + B 上 exit0 + pu/pd_zqcode_lin 各 2 行(表头+1 数据) + 表头含 zqpu5..zqpu0/zqdec/rpu_50/rpu_lin20/50/75/al + 数据行 rpu_50≈230 + cross-input guard(A≠B 值) + 退化 stub FAIL + 确定性 => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1(check 仅 subprocess 跑候选 python 解析 .ms0 文本, 不启动 EDA 二进制), k_check=14==k_rationale=14 ✓, 无 reframe, 保留。',
    ),
}


def apply_one(name, layer, note):
    fn = f"EDA-Eval-DesignFlow-{name}.json"
    path = os.path.join(CASES_DIR, fn)
    txt = open(path, encoding="utf-8").read()
    c = json.loads(txt)
    md = c["metadata"]
    if md.get("reframe_note"):
        return "SKIP_HAS_NOTE"
    out = txt
    # 1) insert layer (if needed) after the "track": ... line
    if layer is not None and md.get("layer") is None:
        anchor_track = '\n    "track":'
        ti = out.find(anchor_track)
        if ti < 0:
            return "NO_TRACK_ANCHOR"
        # find end of track line
        eol = out.find("\n", ti + 1)
        insertion = f',\n    "layer": "{layer}"'
        # need to check if track line already ends with comma
        line_end = out[ti:eol]
        if line_end.rstrip().endswith(","):
            insertion = f'\n    "layer": "{layer}",'
        else:
            insertion = f',\n    "layer": "{layer}"'
        # simpler: insert a new line after eol with layer
        out = out[:eol] + f'\n    "layer": "{layer}",' + out[eol:]
    # 2) insert reframe_note right before "asset_fidelity"
    anchor_asset = '\n    "asset_fidelity":'
    ai = out.find(anchor_asset)
    if ai < 0:
        return "NO_ASSET_ANCHOR"
    # build the reframe_note line; json-escape the note value
    note_json = json.dumps(note, ensure_ascii=False)  # adds surrounding quotes + escapes
    insertion = f'\n    "reframe_note": {note_json},'
    out = out[:ai] + insertion + out[ai:]
    # verify valid json
    try:
        json.loads(out)
    except Exception as e:
        return f"JSON_ERR:{e}"
    open(path, "w", encoding="utf-8").write(out)
    return "OK"


def main():
    for name, (layer, note) in NOTES.items():
        status = apply_one(name, layer, note)
        print(f"  {name:45s} -> [{status}]")
    # verify
    print("\n# verify:")
    empty = []
    for name in NOTES:
        fn = f"EDA-Eval-DesignFlow-{name}.json"
        c = json.load(open(os.path.join(CASES_DIR, fn)))
        md = c["metadata"]
        rn = md.get("reframe_note")
        mark = "✓" if rn else "✗"
        print(f"  {mark} {name:45s} reframe_note={'set ('+str(len(rn))+' chars)' if rn else 'EMPTY'} layer={md.get('layer')}")
        if not rn:
            empty.append(name)
    # total reframe_note coverage
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    has = sum(1 for f in files if json.load(open(os.path.join(CASES_DIR, f)))["metadata"].get("reframe_note"))
    print(f"\n# reframe_note coverage: {has}/{len(files)} (empty={len(files)-has})")


if __name__ == "__main__":
    main()
