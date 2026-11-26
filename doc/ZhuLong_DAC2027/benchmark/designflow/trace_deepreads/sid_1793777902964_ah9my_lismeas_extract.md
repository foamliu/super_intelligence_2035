# Deepread — sid_1793777902964_ah9my (e0024852 @ hfeg0pkn002 / 10.129.2.11)

- sessionId: `1793777902964_ah9my`, agent=lead, 185 msgs, mtime 2026-11-04, spice 305/354=0.862, mc=213
- fresh（不在 ledger 178 anchors 内），spice 主导 ✓
- trace 路径（remote 10.129.2.11）：`/home/e0024852/.cline/data/sessions/1793777902964_ah9my/1793777902964_ah9my.messages.json`（677KB；注意 cline 把文件放在与 session 同名的子目录里，不在 sessions/ 根下）

## 对话弧（user 文本轮，去 tool_result）
- USER#0「when I run /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/hd_CH252_bitcell/hd_CH252_bitcell_post_rev06 how can i sure the the level of hspice tell me in chinese」—— 纯需求：如何确认某 simdir 跑的 hspice level（explanation 类，非交付脚本）
- USER#28「I want add spice level 6 in stimulus_pex_rev06_model_rev04.sp」—— 想加 .option runlvl=6
- USER#40「.option runlvl=6」—— 给出修复方案（.option 行原文）→ 非 A 档
- **USER#42（A-档选用轮，纯需求）**「jiexi /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/hd_CH252_bitcell/hd_CH252_bitcell_post_rev06/sim_result_pex_rev06_model_rev04_hspice/stimulus_pex_rev06_model_rev04.lis de Ireak and Ileak SNM tell me in chinese」—— 要求解析 HSPICE .lis 文件里的 Iread / Ileak / SNM 测量值。用户只说"要什么"（解析哪些量），未给根因/未给修复 → 合格 A 档任务说明 ✓
- USER#55「我想抽取寄生 请问我应该修改 [pex dir] 下面的什么内容」—— PEX 抽取咨询（GloryEX gxrc，非 spice_sim 域）
- USER#63–138：用户反复粘贴 gxrc 报错日志（EXT_SUBSTRATE NO / 35H captab syntax error / DEVICE_FIN_MODEL syntax error），assistant 调试 gxrc 命令文件 —— PEX 调试，非本 case 取材
- USER#148「我就是要使用06版本的寄生提取 不要给我改了」—— 指定用 Rev06
- USER#171「解析 [.lis] 中的 Iread」—— 再次要求解析 .lis 的 Iread
- USER#179「Ilead and WNM_1 WNM_2」/ USER#181「Iread Ilead WNM_1 WNM_2」/ USER#183「Ileak = Ilead」—— 用户细化要解析的量名（Ilead=Ileak 笔误澄清）

## assistant 工具链（针对 .lis 解析弧）
read_files(simdir 结构) → list_allowed_files → read_files(stimulus_pex_rev06_model_rev04.sp) → read_files(.lis) → 定位 "Measurement Summary" 区段（6140–6144 行）→ 用正则/逐行抽取 `.MEASURE` 结果（Iread/Ileak/WNM_1/WNM_2/Iwrite）→ 中文表格汇报数值+换算+取点条件

## 用户实际接受的结果（金标准来源）
ASST#184 给出最终一组（TT/25°C/VVDD=0.75V/run level 6/PEX Rev06+Model Rev04）：
- **Iread ≈ 27.21 µA**（`-2.7205368e-05 A`，I(V_READ) @ VDD/2）
- **Ileak ≈ 32.67 pA**（`-3.2669647e-11 A`，I(V_STANDBY) @ VDD/2）
- **WNM_1 = 0.2856 V / WNM_2 = 0.2856 V**（`.MEASURE DC ... when ...=0 cross=1`）
- Iwrite ≈ 6.16 pA
USER#183「Ileak = Ilead」接受（确认笔误澄清），无后续追问 ⇒ 用户接受该解析结果。

## case 取材裁定
- **A-档任务说明 = USER#42 逐字原文**（解析 .lis 的 Iread/Ileak/SNM，要中文）。金标准 = 一个能从 HSPICE .lis 抽取 `.MEASURE` 结果的通用解析器（产出结构化 JSON {name: SI_value}），与 trace 末尾用户接受的"抽取并汇报测量值"一致。
- **域**：characterization（SRAM bitcell 特征指标 Iread/Ileak/WNM/SNM；与 CapCharProps 同域，平衡 domain 计数 20 vs spice_sim 76）
- **档位/层级**：A-faithful · L2（check.py 在隐藏 B 上真跑 hspice 生成 .lis，再跑候选解析器，断言解析值）
- **A/B 切分**：A=asset .lis（hspice stub A：1V/1k/2k 分压，iread=166.67u/ileak=166.67u/wnm_2=166.67m/snm=333.33m）；hidden B=stub deck（1V/1k/1k，iread=250u/ileak=250u/wnm_2=125m/snm=250m）。同名 measure、不同电路→不同值（跨输入护栏）。check.py 真跑 hspice B deck → B.lis → 候选解析 → 断言。
- 🚫 USER#0 是 explanation 类（无脚本交付），USER#40 给修复方案，均不用作 A 档任务说明。
