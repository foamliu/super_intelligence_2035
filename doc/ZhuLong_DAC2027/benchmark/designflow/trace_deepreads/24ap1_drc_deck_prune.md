# Deepread: 1795586032370_24ap1 — Calibre DRC rule deck 按 target .ev 裁剪

- **trace**: kenwang @ hfeg0plg54, 291 msgs, mc=387, domain=physical_verify
- **真实任务**: 用户整理了一个 18 万行的 Calibre DRC rule deck (`35H_..._DRC_Cal_V0d1_Rev14_S1.drc`, 8.7MB), 只需保留 `1_1_1_DBC_H280.ev` 对应的 rule code, 要求:
  1. 删除多余 rule code (保留 DBC_H280 族)
  2. 不能全删 layer 定义 — 只删未被目标 rule 用到的, 用到的保留
  3. 原始 drawing layer 定义全部保留
- **真实工具链**: 用户用 cline + deepseek-v4-flash, assistant 先读 .drc 和 .ev 理解结构 (LAYER MAP/LAYER 定义/drawing layer/derived layer/rule block/INCLUDE), 后因 python locale 问题改用 awk/shell 写裁剪脚本, 最终产出 `35H_DBC_H280_ONLY.drc` (268KB, 原 8.7MB 的 3%)
- **真实文件结构** (从 plg54 fetch 确认):
  - deck: header 注释 + #DEFINE 开关 + VARIABLE + LAYOUT setup + LAYER MAP/LAYER 定义(drawing `_drawingi` + 非 drawing) + derived layer(`Name = expr`) + rule block(`Name { ... }`) + INCLUDE "xxx.ev"
  - target .ev: `#IFDEF` + derived layer + rule block (DBC_H280_CB_W_1 等)
  - INCLUDE "../1_1_1_DBC_H280.ev" 在 deck line 9715
- **case 设计决策**:
  - 抽象成纯 Python 文本处理题 (LIVE-NA, L0/L1) — deck 是文本, 裁剪是 parse+dependency-analysis+rewrite, 不需真跑 calibre
  - 自包含 representative deck (~110 行, 8 drawing + 4 非 drawing + 6 derived + 5 rule + 2 INCLUDE) 而非 ship 8.7MB 真实文件
  - 核心算法挑战 = derived layer 传递依赖闭包: 从 target rule body 引用的 layer 名出发, 展开 derived layer 定义表达式, 迭代到 fixpoint
  - hidden B 用不同 layer 族 (NW/AA/GT/M0/M1/V0 vs A 的 DNW/NW/AA/GT/BS_6/BS_8/M1/M2) + 不同 target 族 (FS_H300 vs DBC_H280) 防 hardcode
- **交付**: EDA-Eval-DesignFlow-DrcDeckPrune-001, `drc_prune.py <deck> <target.ev> <output>`, check.py 14 断言 (B 主判 + A 反硬编码 cross-input), 5 negative (empty_stub c3 / print_only c4 / copy_all c6 / core_deleted c8 / keep_all_layers c9, 全 distinct), judge_layers [L0,L1], LIVE-NA
- **自验**: REF check PASS 14/14 + negative_selftest OVERALL_RC=0 (5 neg 全 FAIL distinct) + §4.9 trio (empty/print/core-deleted → c3/c4/c8 distinct) + SKIP_RUN eval/run_one.sh 框架接受 (attachments 全部署, workdir leak 自检通过) + build_jsonl.py --shard C 重建 C.jsonl 640 active 本 case 入列
