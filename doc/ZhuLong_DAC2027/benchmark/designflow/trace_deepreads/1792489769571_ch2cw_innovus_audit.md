# trace_deepread: 1792489769571_ch2cw (johnl / hfeg0plg49 / mc=255 / domain=pnr_signoff)

## trace 概况
- session: `1792489769571_ch2cw`，cline lead agent，158 msgs，949KB messages.json
- 用户轮仅 2 条真实输入：#0 全文审计提示词（提出需求）、#135「继续」。无用户指出根因/给修复方案的轮 → 符合 A 档选轮规则（10-31 令 ①）。
- 工具链：innovus 启动验证（run_approved_command 跑 innovus_verify*.sh）+ editor 写审计脚本 + 大量只读侦察。innovus=233 命中（PNR 主导）。

## 真实任务
全定制环境下用 Innovus 做 `addr_to_rowcol_v7`（纯组合，input[8:0] N / output[3:0] row / output[4:0] col / output valid，107 实例，18 个 *LVSx* 组合单元）的完整数字后端**能力审计**——只调查可行性、不实现。要求区分必须项/条件项/非必须项，给阶段能力表，定位真实缺项，最后明确「未进行正式实现」。

## 金标准（trace 末尾用户实际接受的工具产物）
- `innovus_audit/AUDIT_REPORT.md`（5762B，仍存于 .75:/home/johnl/.../dc_addr_to_region/out/innovus_audit/）+ 30 个只读侦察 .sh/.py。
- 关键事实结论：
  - Innovus v23.32-s091_1 真实启动验证 OK（compatlib 绕开沙箱 LD_PRELOAD 注入）
  - 时序库 SS_0p98_m40c_lvs.db（SS/0.98V/-40C），Innovus 可读 .db
  - **唯一硬缺口 = tech.lef + 单元 abstract LEF**（须 genlef/ski-genlef 从 OA layout 生成）
  - 纯组合 → CTS 不适用（不虚构时钟）
  - OA layout 覆盖 18/18 master；PEX（Calibre LPE/StarRC/QRC/Quantus）+ DRC/LVS（cxmtG5_CIP runset + Argus）+ 等价（Formality/Conformal/LEC）齐
  - 审计纪律：未正式实现

## case 合成（A 档 trace-faithful / L1-boundary / pnr_signoff）
- prompt.txt = 用户原话逐字（仅说明本地副本位置；路径/用户名/SPICE 原文保留，无脱敏）
- 交付 = `run_audit.py`（参数化：--netlist/--manifest/--outdir → AUDIT_REPORT.md），对任意同族电路通用
- A 输入 = mapped.v（v7/107/SS/min缺）+ lib_manifest.json + mapped.sdc
- 隐藏 B = mapped.v（v6/91/FF/min具/含and2LVSx1 不含nand3*/oai211*/invLVSx6）+ B manifest —— 来自同批 dc_addr_to_region_36rtl/v01_baseline（真实兄弟电路，同 PDK 同单元族，结构不同）
- check.py 在 B 上跑候选脚本，校验 14 条事实断言（顶层/端口/实例/单元/纯组合+CTS不适用/三分类/≥8阶段/角/min库/审计纪律/LEF硬缺口），含 5 条跨输入守护（反硬编码 A）
- gold 的「真跑商业工具」= Innovus v23.32 启动验证在金标准创建期于 .75 完成；check.py 本地静态 + subprocess 跨输入守护（与本 bench L1-boundary 惯例一致）

## 失败归因预设（A 档试点口径）
- ①交付形态/位置错：submit.zip 无 run_audit.py 或脚本不在根 → (a)/(b)
- ③能力不足：硬编码 A 事实、不解析 B → (c)(e)(g)(k)(l) 跨输入守护 FAIL
- ④判分歧义：本 case 判分对事实（顶层名/实例数/单元集/角）严格匹配，不对措辞
