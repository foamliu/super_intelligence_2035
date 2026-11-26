# waveview_real_cases.jsonl — WaveView 真题导出（vision 用）

> 生成：2026-11-15（designflow shard D，用户令 2026-11-15 07:2x「把 waveview 真题整理成单独 jsonl，给 vision 后续使用」）
> 来源：`waveview_need_image_handoff.md`（α4+β7=11 交底，β5 不存在 → 10 真题）+ `waveview_baseline_results.{D,B}.json` + 4 shard jsonl + assets/reference 磁盘核对
> 用途：vision 侧度量多模态增益（无多模态基线 fail → 上 VQA 后 pass 的差值）

## 统计

| 项 | 值 |
|:--|:--|
| 题数 (N) | 10 |
| shard 分布 | {'D': 8, 'B': 2} |
| asset_fidelity 分布 | {'synthesized-image-restored': 10} |
| image_kind 分布 | {'eye_png': 1, 'wave_png': 9} |
| 图片总数 | 10（visible A，不含 hidden B） |
| 图片总字节 | 644228 |
| 基线 pass / fail / unrun | 0 / 10 / 0 |
| failure_mode_tier 分布 | {'A': 5, 'C': 3, 'B': 2}（A=did-not-engage / B=engaged-text-only / C=engaged-but-could-not-read-image） |
| 基线模型 | minicpm5-2b-sft-v39-final（2B text-only SFT surrogate, NO multimodal）|

## 字段说明

| 字段 | 含义 |
|:--|:--|
| `case_id` | 用例唯一 ID（= jsonl `id`/`task_id`）|
| `case_name` | α/β 编号 + 题名（waveview handoff 清单编号）|
| `source_shard` | 来源 shard（去重后单元素；同 case 跨 shard 只留 1 条）|
| `domain` | jsonl metadata.domain（注意：3 题 domain≠waveform——TempThreshChar=analog_context, RiseEdgeMarginMeas/FsdbWrDqMeas=spice_sim——但均属 waveview 原意图需看图集，按 handoff 清单收录）|
| `requires_image` | 是否原意图需要看图（全部 true）|
| `image_paths` | visible A 图片相对路径（benchmarks/EDA-Eval-DesignFlow/ 下，SUT 需读此图）|
| `image_sha256` | 每图 sha256（校验完整性）|
| `image_kind` | 图类型（eye_png=眼图 / wave_png=波形图）|
| `check_path` | check.py 相对路径（benchmarks/EDA-Eval-DesignFlow/ 下）|
| `k_conditions` | check.py 独立断言数（与 metadata.k_check / check.py 标注 (a)-(m) 一致）|
| `baseline_pass` | 无多模态基线结果（TRUE/FALSE/UNRUN；本批全 FALSE=正确）|
| `baseline_source` | 基线来源 json |
| `failure_mode_tier` | 失败模式分层（A/B/C，见上）|
| `failure_mode_short` | 失败模式简述 |
| `asset_fidelity` | 素材保真度（全部 synthesized-image-restored：真实私有波形/FSDB 不可复刻，由已知参数经 .75 沙盒 matplotlib 合成真数据图，无数据标签，需从坐标轴读数）|
| `trace_source` | 真实 trace 溯源（user/host/session_file/match_count）|
| `hidden_b_images` | hidden B 图片（反硬编码 provenance，**不进 SUT 沙箱**，仅供 vision 参考）|
| `grade` | 用例等级（全部 B-grade synthesized）|
| `notes` | 备注 |

## 复算/校验命令

```bash
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow

# ① 题数
wc -l /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl

# ② 每题 image_paths 全部 test -f
python3 -c "
import json
for line in open('/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl'):
    r=json.loads(line)
    for p in r['image_paths']:
        import os; print('test -f', p, '->', os.path.isfile(p))
"

# ③ 每题 sha256 校验
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow
python3 -c "
import json,hashlib,os
for line in open('/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl'):
    r=json.loads(line)
    for p,exp in r['image_sha256'].items():
        h=hashlib.sha256(open(p,'rb').read()).hexdigest()
        print(p, 'sha256', 'OK' if h==exp else 'MISMATCH')
"

# ④ 逐题 k_conditions 与 check.py 标注一致（抽查）
grep -H "independent conditions" reference/EDA-Eval-DesignFlow-*/check.py
```

## 口径说明

- **收录口径**：原意图需要看图的 WaveView 用例（来自 `waveview_need_image_handoff.md` α4+β7=11 交底清单，β5 `FsdbNetToggleDiag-001` 经 convener r508 核实从未造题 → 实际 10 题）。全部经 WAVEVIEW_COLLAB task1 恢复为 image-required 形态（移除文本替身 .rep/.tbl/.csv，改用 matplotlib 合成真数据图 PNG），无多模态基线全 FAIL = 正确行为。
- **去重**：每题仅存在于 1 个 shard，无跨 shard 重复。
- **domain 字段**：3 题 jsonl domain≠waveform（TempThreshChar=analog_context / RiseEdgeMarginMeas+FsdbWrDqMeas=spice_sim），但均属 waveview handoff 原意图需看图集，按 handoff 清单收录（domain 字段原样保留，未改）。
- **未放宽判据**：k_conditions 直接取 check.py 独立断言数（与 metadata.k_check / check.py 头部 "(a)-(l)" 标注一致），导出不改 check.py、不降门槛。
- **未跑 inflate**：基线全来自 `waveview_baseline_results.{D,B}.json`（2026-11-14 实跑），未重跑；全 FALSE。
- **其他 image-bearing case（未收录）**：`EDA-Eval-DesignFlow-IRReportPdf-001`（C shard, domain=pg_layout, 14 visible PNG）不在 waveview handoff 清单（IR voltage-drop heatmap，非波形识图），按 §零「domain=waveform 且原意图需看图」口径排除。vision 如需可另列。
- **图缺失**：本批 10 题图全部存在（test -f 通过），无图缺失条目。
