# trace_deepread — 1793776902021_xvnac (laryu @ hfeg0pkn001, mc=139) — Calibre SVRF DFM vss 打孔

## trace 概览
- **session**：`/home/laryu/.cline/data/sessions/1793776902021_xvnac/1793776902021_xvnac.messages.json`（10.129.2.10 = hfeg0pkn001），257 msgs（170 assistant / 172 user，其中 34 条 real user，其余 tool_result 包装）。
- **agent**：lead；keywords `calibre:121 / netlist:3`；纯 physical_verify（Calibre SVRF training/debugging），NEW user **laryu**（不在饱和名单）。
- **真实任务流**：laryu 在 `/proj/drgqa/V0/workdir/laryu/SVRF_training/` 下学习/调试 Calibre SVRF——翻译 PG_PTAP_TOUCH_EDGE 表达式、修 getSizeGate.rule 的 LAY7/LOC2 报错、调试 flatten GDS 输出不生效、读 svrf_ur.pdf/manual 解释 DFM SPEC FILL SHAPE / OPTIMIZER / FILLSHAPE / OUTPUT、写 vss 打孔 rule、改 getVia.rule 的 DFM159 报错。
- **gold 产物**：`/home/laryu/vss_punch.rule`（assistant 用 DFM SPEC FILL SHAPE RECTFILL + NET vss! + DFM RDB GDS 输出定稿的 vss M1-M2 打孔 deck，详见 REAL#26）。

## 选轮（REAL#26, idx=198）—— A/B 档判据
用户原话（提出需求，给目标 + 4 个数值参数，**未**给根因/修复方案）：

> /home/laryu/vss_punch.rule，需要孔的大小为0.045 0.045，孔与孔的间距为0.092，孔到M1的间距为0.0025，孔到M2的间距为0.0025

✅ 符合 A 档「提出需求/表达目标」；🚫 不取 REAL#1/2/7/29（用户已贴报错根因 → 给修复）、🚫 不取 REAL#3/4/5（追问/澄清，给方向）。

## 为何做成「参数化生成器」(B-synthesized)
原任务「用 4 个固定数值改写 vss_punch.rule」的交付物是**带固定参数的静态 deck**——数值本身就是题面，A/B 不能在数值上区分（否则变成两道不同的题），不满足 §4.1 隐藏输入 B「取值/结构不同」+ §4.2「subprocess 在 B 上执行候选脚本」。故 B 档重定义为：**写一个参数化生成器 `gen_vss_punch_rule.py`，读 JSON config 吐出完整 deck**；B/B2/B3 用不同 config（precision/路径/primary/net/via 尺寸/pitch/enc/层号）独立运行，断言输出 deck 携带各自 config 的精确值（防硬编码）。grounded 于真实 SVRF 结构（DFM SPEC FILL SHAPE / NET / CONNECT / DFM RDB GDS），不反推答案。

## gold deck 结构（来自 vss_punch_final.rule）
PRECISION / LAYOUT SYSTEM+PATH+PRIMARY / LAYER MAP(M1,V1,M2 drawing+pin) / VIRTUAL CONNECT / TEXT LAYER / ATTACH / CONNECT M1_drawing M2_drawing BY V1_drawing / M1_vss=M1_drawing NET "vss!" / M2_vss=M2_drawing NET "vss!" / via_region=SIZE(M1_vss AND M2_vss) BY -enc / DFM SPEC FILL SHAPE "vss_via" RECTFILL 0 0 w h STEP pitch pitch / DFM SPEC FILL vss_punch INSIDE OF LAYER via_region FILLSHAPE OUTPUT "vss_via_gen" "vss_via" / V1_hole=DFM FILL vss_punch / out_put{DFM RDB GDS out_gds M1_vss 88 0 M2_vss 91 0 V1_hole 90 0 PROPERTIES APPEND _vss_punched}。

## 域/层
- domain = **physical_verify**（Calibre SVRF DFM deck 生成）。
- L1（离线 Python 生成 deck；判分用 subprocess 在隐藏 config 上跑候选脚本 → 满足 §4.2）。
- k = 16 条断言（a–p），与 check.py 16 个独立条件一一对应。

## DISTINCT from 现有 physical_verify 系
r242 SaqpIntAngleEqSplit(INT(ANGLE)==重写)/r241 SvrfPvrsRuleTranslate(SVRF→PVRS)/r240 WlAdjacentPairParse(.rep PAIR)/r239 DrcRuleTimeRank(log per-rule time)/r237 DrcLogTeardownReport(log 拆解)/r220 SvrfTvfLayerMapGen/r208 DrcUnusedVarClassify——本案**首次 ground on Calibre DFM SPEC FILL 参数化打孔 deck 生成器**（RECTFILL/STEP/SPACE via 阵列 + NET 抽取 + DFM RDB GDS），与既有 deck 解析/翻译/重写类不同。
