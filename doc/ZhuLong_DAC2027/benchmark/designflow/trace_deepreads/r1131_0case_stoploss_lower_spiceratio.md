# r1131 (2026-11-24) — 0-case stop-loss 轮 · B-spice fresh 池低 spice-ratio 段耗尽确认

## 背景
r1130 在 b_fresh_r1126_xshard_dedup.tsv (200 真 fresh) 的 **spice-ratio≥35% 段** peek 4 候选，1 produce (reedchen lbsbf → QuotedUnitValueNormalize-001 落库)，3 reject。MEMORY 指示「下轮探更低 spice-ratio 或等新 scan」。

本轮执行：① 检查新 scan（无，最新仍 20261124_023802，r1130 同源）② 系统性 peek 低 spice-ratio 段（spice≥5，ratio<35%，排除已 peeked）的全部真 fresh B-spice 候选。

## 选料
- 源池：`designflow/b_fresh_r1126_xshard_dedup.tsv`（200 真 fresh，4-shard 台账 dedup 后）
- 过滤：spice_kw count≥5，排除 r1114/r1124/r1125/r1126/r1130 已 peeked 集合（23 sids）
- 候选：43 条；按 spice ratio 降序 peek

## peek 明细（本轮 15 候选，全 reject）

### 高 spice-ratio 段（ratio 0.38–0.22，3 条）
| sid | user | mc | spice | ratio | 判定 |
|---|---|---|---|---|---|
| 5qlyc | reedchen | 41 | 17 | 0.10 | **doc-Q&A 拒**: U0 "output.ic 是什么文件，为什么后仿能加速这么多" → assistant 读 FineSim output.log 解释 DC checkpoint 机制，纯讲解无 produce (34msgs/103KB) |
| yetqt | krisluo | 13 | 8 | 0.22 | **analysis-Q&A 拒**: U0 "后仿文件激励写法" → 全程 Q&A: PU vs VPULSE/vin_xx 编号/dc=显式 vs 隐式/RCC 端口来源，无 produce (19msgs/115KB) |
| tadz1 | t0002801 | 4 | 5 | 0.38 | **vague 拒**: U0 "生成检查STD的tcl模板 TT/1.8V/25C" 未指明工具(Liberate/PT/ALPS?)/检查项，assistant 仅澄清未产出，mc4 噪声 (6msgs/14KB) |

### 中低 spice-ratio 段（ratio 0.20–0.07，12 条）
| sid | user | mc | spice | ratio | 判定 |
|---|---|---|---|---|---|
| 4adps | caozhang | 8 | 8 | 0.20 | **doc-Q&A 拒**: "nanospice option 未知值默认值/未知态信号初始值" (45msgs) |
| xy7vv | joeyl | 9 | 9 | 0.15 | **workspace-cleanup 拒**: "工作目录乱文件清理" 非 spice produce (33msgs) |
| yjwjo | zhenglu | 12 | 5 | 0.14 | **Q&A 拒**: "dtech_spice 目录有无 sram model/网表 x 开头器件" (45msgs) |
| p7mti | e0041392 | 4 | 10 | 0.12 | **skill-mgmt 拒**: ask-eda skill 调用上下文 (4msgs) |
| nwnuw | shanliny | 23 | 10 | 0.11 | **meta-tooling 拒**: "开发脚本访问指定目录操作" 非 B 域 spice produce (162msgs) |
| 527j4 | shanliny | 24 | 6 | 0.11 | **complex-continuation deferred**: SRAM M4B2 64×8 RM/WM meas 引擎 sram_meas_gen.py **真交付** ✓，但依赖 80MB DSPF + 前序 session state + 3 处未确认定义(xdec 方向/bit 左右缘/SA 归属)，单轮不可自包含封装；deferred 待专项 build 轮 (135msgs/650KB) |
| xwi92 | steveny | 14 | 15 | 0.10 | **git-commit 拒**: "把该提交提交到 git" 非 spice produce (32msgs) |
| v5bel | serwing | 8 | 6 | 0.10 | **analysis-Q&A 拒**: "ptn_lv/ntn_pv 温度特性+RC延迟链 ff/ss corner delay 温度反相分析" (17msgs) |
| wfszb | e0039816 | 4 | 10 | 0.09 | **vague-analysis 拒**: "从两份文件拿数据分析" 2msgs 无具体意图 |
| 1ju7i | alrenc | 7 | 11 | 0.08 | **launch-app 拒**: "帮我打开 solido 软件" 非 produce (49msgs) |
| yqtos | rowanl | 17 | 5 | 0.08 | **trivial 拒**: "hello/为什么输入不了中文" (48msgs) |
| k6clp | reedchen | 2 | 15 | 0.11 | **continuation+skill-mgmt 拒**: U2 "把工作更新到 skill"，mc2 archive 噪声 (177msgs 但 archive mc2) |

## reject 分类统计
- doc-Q&A / analysis-Q&A: 5 (5qlyc/yetqt/4adps/yjwjo/v5bel)
- vague / 噪声: 3 (tadz1/wfszb/k6clp)
- 非 B 域 produce (cleanup/git/launch/meta-tooling/skill-mgmt/trivial): 6 (xy7vv/p7mti/nwnuw/xwi92/1ju7i/yqtos)
- 真交付但不可自包含封装: 1 (527j4, deferred)

## 结论
- **b_fresh_r1126_xshard_dedup.tsv 的 spice≥5 段（43 候选）已系统性 peek 完**：扣除 r1114/r1124/r1125/r1126/r1130 已 peeked 23 条 + 本轮 15 条 = 38 条已核验，残存 5 条为 spice<5 或 mc≤2 极低密度噪声（非真 produce 意图）。
- r1125「扩池无效」结论经本轮在**低 spice-ratio 段** rigorously reconfirm：r1125/r1126 仅核验高 mc + spice≥20 段；本轮补完 spice 5–20 + ratio<35% 段，结论一致——残存真 fresh B-spice produce 密度趋 0。
- **唯一真交付候选 527j4** 是 continuation session，需 80MB DSPF + 前序 state + 3 未确认定义，单轮（40min 预算）不可自包含封装为 check()-able case。deferred 待专项 build 轮（需先 scp 完整 session + DSPF + 前序 0rh2t session 重建上下文）。
- scan 池自 r1110 (1123_064315) → r1123 (1124_023802) 后无新 scan 到达。

## 动作
- 15 候选 claim + park 入台账（防复检）
- 台账 B: 1739 → 1758（+15 parked，parked 1151→1166）
- 📊 covered=592/4529=13.1%(mc>=10, 不变，无新 case)
- 🎯 最近20条 20/20=100%(观察值,不变)
- DEBT:0

## 下一步建议
1. **等待新 scan** 注入高 mc hspice/finesim/spectre/siliconsmart-dominant 段（r1125/r1126/r1131 三轮 stop-loss 后，当前 1124_023802 池 fresh B-spice produce 密度已耗尽）
2. **527j4 专项 build 轮**（可选，高成本）：需 scp 完整 527j4 session (650KB) + 前序 0rh2t session + 80MB DSPF + 全部 config 文件，重建 SRAM M4B2 RM/WM meas 引擎上下文，方可合成自包含 case。预估 2–3 轮。
3. **§4.9 跨 shard 审计**（A/C/D 的 negative_selftest.py 完整性，r1126 已确认 B 100%）
4. 新 scan 到达后用 r1126 的 4-shard 台账 dedup 方法重建 fresh 池（避免 stale dedup 坑）
