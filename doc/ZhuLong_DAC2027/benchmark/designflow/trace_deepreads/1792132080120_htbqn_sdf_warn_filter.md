# 深读：1792132080120_htbqn — SDF Warning 日志过滤+归类（tabtao / verification）

## 元信息
- session: `1792132080120_htbqn`（cline v3 目录式：`<sid>/<sid>.messages.json`）
- user: tabtao · host: hfeg0pkn004 · mc=91 · 224 msgs · 1.04MB messages.json
- model: deepseek-v4-flash · cwd: /home/tabtao · status: failed (terminal: failed_external_process_exit，stale_session_reconciler 收尾，非任务失败)
- domain: **verification**（DDR5/DDR6 前端仿真 SDF annotation 日志处理 + DC 综合/STA debug）
- 工具计数：synthesis:43 主导（实为 SDF/DC/STA 调试对话，关键词命中为主，非纯工具流）

## 用户轮全景（22 条 user_input，按 idx）
- #0: **SDF 日志过滤**：`@/rundata/.../sdf_ss.log 请处理sdf_ss.log的文件，将Warning-为开头，直到遇到空白行之间的内容全部保存到...sdf_noanalog.log文件中，其中如果这部分的内容里面有dram1sc, DFI_RBANK, DFI_WBANK的关键字的，请不要放到sdf_noanalog.log文件中。` — 纯提出需求，无根因/修复 → **合 A档选轮规则**。
- #36: **SDF 日志归类**：`@...sdf_noanalog.log 请处理sdf_noanalog.log的文件，检索到Warning-[*]，按照[*]中的*的内容进行归类，全部保存在上述路径下*.log文件中，有几种就放几个文件。` — 纯提出需求。
- #51/#79/#112: DDR6 model .svp 打印行定位分析（MRUPD_MRW / Enable CSTM / CSTM_FTS_MODE）— 分析题，产物=解释。
- #93/#183/#185/#187: 追问澄清（非新任务）。
- #95: 在 post_sim 新路径重跑 #0+#36 两步。
- #120: DC 综合 `Error: extra positional option '_sel6'` 报错根因分析。
- #165: DC `Warning: Module cfreq_ctrl contains unmapped components` 分析。
- #181: `check_timing.rpt TIM-216` warning 消除问询（用户给方案 A，问 false_path 顺序）— 含修复倾向。
- #189: clock_gating_default violation 分析（always_comb case）。
- #191/#207: PT STA `jtag_csr_max_delay` unconstrained path + 主 SDC `set_clock_groups -async` 分析。
- #220/#222: DC shell `set_max_delay` net=0 现象 + `set_clock_groups -async` 与 `set_max_delay` 冲突问询。

## A档选轮
选 **#0**（idx 0）作为本 case 任务说明：纯「提出需求」，无根因/修复，逐字原文。真实任务 = 处理 1GB SDF annotation 日志 sdf_ss.log，抽取所有 `Warning-` 开头到空白行的 block，剔除含 dram1sc/DFI_RBANK/DFI_WBANK 关键字的 block，写入 sdf_noanalog.log。

## 真实 gold（assistant 真产物，用户接受）
- `process_sdf.py`（msg 19 最终版，从 tool_result 取回完整 101 行）：
  - SRC/DST 硬编码真实路径 `/rundata/lagat/V0_digital/simdir/ethan/2026/sos2/verification/sim/SDF/sdf_ss.log` → `.../sdf_noanalog.log`
  - KEYWORDS = `("dram1sc","dfi_rbank","dfi_wbank")` 小写，case-insensitive（`low = "\n".join(cur).lower()`）
  - 流式逐行读（`for lineno, raw in enumerate(f,1)`，不 readlines），1GB 可处理
  - block 语义：行 `startswith("Warning-")` 开新 block；block 内遇 `line.strip()==""` 空行结束；EOF 无尾空行也 flush
  - 连续 kept block 间以单空行分隔（`if not first_block: out.write("\n")`）
  - 摘要打印：total_blocks / kept_blocks / filtered / per-keyword hit / total_lines / elapsed
- 运行结果（msg 13/23/24）：2,456,487 total blocks → 2,456,344 kept → 143 filtered（dram1sc:47, DFI_RBANK:96, DFI_WBANK:0），14.9s
- 验证（msg 34 validate_sdf2.py）：output 15,931,920 lines，无 bad-start / bad-keyword / orphan
- 归类（msg 44 classify_sdf.py）：6 个 [CODE] — SDFCOM_UHICD(32) / SDFCOM_SWC(411) / SDFCOM_IWSBA(698) / SDFCOM_NL(1,189,826) / SDFCOM_CFTC(1,264,993) / SDFCOM_INF(384)，total 2,456,344，no-code:0
- validate（msg 49）：每 code 文件 block 数与期望一致，sum=2,456,344，PASS

## 输入文件可达性
- 真实 sdf_ss.log = `/rundata/lagat/V0_digital/simdir/ethan/2026/sos2/verification/sim/SDF/sdf_ss.log`（1,078,372,562 bytes ≈ 1GB）
- `/rundata/lagat` NFS 挂载，group `lagat`（drwxr-s--- cadmin:lagat），e0031982 不在 lagat 组 → **permission denied**（.75 与 hfeg0pkn004 均拒）。
- 故 asset A = 忠实合成样本：基于真实 6 个 SDFCOM_* code 名（来自 msg 44 真实计数）+ `Warning-[CODE]` 格式 + 3 个真实排除关键字 + 真实路径引用，构造 ~30 blocks 小样本（含若干含关键字 block 供过滤）。隐藏 B = 结构全异（不同 code 名 / 不同计数 / 不同关键字位置 / 不同路径），不进 SUT 沙箱。

## 合成决策
- A档 / L1-boundary / verification：prompt = #0 逐字原文（不脱敏，路径/关键字保留）；交付 = 可复用 `sdf_filter.py`（参数化 argv：`<input_log> <output_log>`，流式，case-insensitive，3 关键字排除，block 语义忠实 gold）；asset A = sdf_ss_sample.log（A 路径风格 + 6 code + 含关键字 block）；隐藏 B = sdf_ss_B.log（结构全异）；check.py 只跑 B（§4.1），subprocess 真跑候选脚本（§4.2）。
- 断言 ≥8 条：zip 内容 / 跑通 / 输出仅 Warning- block / 无 dram1sc / 无 DFI_RBANK / 无 DFI_WBANK / kept 数 = total-filtered / block 间单空行 / 流式（源码无 readlines/read 全读）/ 参数化（无 A 硬编码路径）/ case-insensitive（B 混合大小写关键字）/ EOF 无尾空行 flush / 跨输入 B code 不同于 A。

## 失败归因预设（A档记账）
- ①交付形态/位置错 → zip 内容 / 跑通断言
- ②结构/语义错 → block 语义 / 空行 / EOF 断言
- ③能力不足（硬编码 A / 非流式 / 大小写敏感）→ 参数化 / 流式 / case-insensitive 断言
- ④判分歧义（对事实严格匹配）→ 计数断言
