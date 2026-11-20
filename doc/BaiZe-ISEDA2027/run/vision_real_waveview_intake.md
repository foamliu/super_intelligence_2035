# WaveView 真题检出 intake (任务书 §2026-11-15 07:2x 任务②)

> 生成: 2026-11-15 08:3x · vision 线 · 自行 SSH 到 36.15 检出(用户放行)
> 机器可读: `run/vision/real_waveview_index.json` · 真题 PNG 只读复制: `run/vision/real_waveview_images/<case>/`
> 数据出处: 36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/` + `WAVEVIEW_COLLAB.md` 交付记录 + `waveview_baseline_results.{D,B}.json`

## 结论

- **实际可用 = 10 道** (designflow 已恢复原形态的 image-required WaveView 真题: D8 + B2)。
- 未达 >10: 交底清单原写 11(α4+β7), 但 **β5 `FsdbNetToggleDiag-001` 案例不存在**(convener r508 核实, 4 shard jsonl 全量 grep 0 命中), 故真·可恢复分母 = **10**, 不是 11。🚫 未拿合成集冒充。
- 另有 5 个 wave 名 case(`SimFailDiagnose-001`/`SimFailParse-001`/`TempSelInfer-001`/`WaveviewModuleUpdate-001`/`WaveViewPanel-001`)有 check.py 但 assets 下**无 visible PNG**, 不在已恢复看图集, 不计入。
- 每题: domain=waveform(α2/β7 实为 spice_sim 但系 wave 图像题)、**case 目录内真有 PNG**、**有 check.py**、**已跑过基线(全 FAIL = 正确无多模态基线)**。
- check.py **原样未改**(只读复制, 未触碰 designflow 题目/图片/check)。

## 检出方法

1. `.17` 经 `ssh -p 3333 app.e0031982@localhost` 登 36.15(hfeg0tedaap02)。
2. 在 36.15 `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/` 下: `assets/<case>/` 列 PNG, `reference/<case>/check.py` 取 k 条件, `EDA-Eval-DesignFlow_{A,B,C,D}.jsonl` 定 shard/domain。
3. 基线 PASS·FAIL / failure_mode_tier 取自 `waveview_baseline_results.{D,B}.json`(designflow 落盘)。
4. visible-A PNG `sha256sum` 后 tar-over-ssh 只读复制到 `run/vision/real_waveview_images/<case>/`; 本地复算 sha256 与 36.15 源**全 10 题一致**(见 index `local_sha256_verified=true`)。

## 逐题登记

| # | α/β | case_id | shard | domain | 图(visible A) | img sha256(前12) | check.py k | 基线 | tier | 轮次 |
|:-:|:-:|:--|:-:|:--|:--|:--|:-:|:-:|:-:|:-:|
| 1 | α1 | EyeApertureSelect-001 | D | waveform | eye_sweep_A.png | 775c2a789976 | 12 | FAIL | A | r650 |
| 2 | β9 | WaveMaxFind-001 | D | waveform | wave_vb_A.png | 2be588077390 | 12 | FAIL | C | r651 |
| 3 | α4 | TempSelWaveform-001 | D | waveform | sel_wave_A.png | 4bcbddf280c1 | 12 | FAIL | B | r652 |
| 4 | β8 | WaveView-002 | D | waveform | wv_sigs_A.png | c06fbd14066c | 12 | FAIL | C | r653 |
| 5 | β10 | TempThreshChar-001 | D | analog_context | thresh_char_A.png | 0afd31cd29ef | 12 | FAIL | C | r654 |
| 6 | β11 | SimFailFsdbProbe-001 | D | waveform | sim_fail_A.png | 6b3d93cc1fad | 12 | FAIL | B | r655 |
| 7 | α3 | DqReadPathWaveDebug-001 | D | waveform | dq_readpath_A.png | e78fabfe78f2 | 13 | FAIL | A | r657 |
| 8 | β6 | WaveCmpWrap-001 | D | waveform | wave_cmp_A.png | 23612a8266f2 | 13 | FAIL | A | r658 |
| 9 | α2 | RiseEdgeMarginMeas-001 | B | spice_sim | rise_margin_A.png | 7e67e262430d | 12 | FAIL | A | r550 |
| 10 | β7 | FsdbWrDqMeas-001 | B | spice_sim | wr_dq_A.png | a91588c2ea50 | 13 | FAIL | C | r551 |

tier 释义: A=did-not-engage(模型未读 prompt/PNG) · B=engaged-text-only · C=engaged-but-could-not-read-image(预期 +VQA 主翻转源)。

## 防作弊口径不变

- 只读复制 visible-A PNG(hidden-B 未复制, 保留 designflow anti-hardcode)。
- 🚫 不改 designflow 题目/图片/check.py(只 `ls`/`sha256sum`/`tar` 读出)。
- VQA 调用禁 PIL·OCR·base64·搜答案(与任务书一致)。

## 下一步

用这 10 道真题(visible-A PNG)重跑三段对照(无 VQA / 有 VQA / agent 臂, 同口径),
原地覆盖更新 `reports/report_vision_waveview_selftest_agent_zh.html`。
