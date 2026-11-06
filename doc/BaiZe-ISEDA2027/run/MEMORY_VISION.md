# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

> 🆕 **【wake #825 · 2026-11-06 18:47】监控巡检·GRPO chain健康(170polls全busy)·GPU满载等pretrain释放·零可执行动作·WAITING=0。** ①GRPO chain PID1365749 alive(ppid=1真守护,etimes≈8294s/138min),chain stdout(/tmp/grpo_chain_relaunch.log)最新18:47:03 busy_util--waiting健康 ②pretrain torchrun PID2612442 etimes=341763s/94.9h,2节点(.12+.29)16GPU,ETA≈11/28(~22天) ③GPU 8×H100 91-100%util ~75GB,vision R9未在跑·铁律禁杀pretrain ④SFT eval pass(format1.0/submit1.0,lt1pct=14%/lt5pct=21%)·ckpt step1000/2000/3000均有adapter_config.json在位·WaveQA-RL oracle 300题在位·grpo_train_wave.py/waveqa_eval.py/run_grpo_wave.sh就绪·auto-launch链全路径就绪 ⑤git sync origin(无ahead/behind)。**结论**:状态无变化,本轮零GPU可执行动作(被健康pretrain占满,ETA≈11/28),不伪造数字。📦体积:TASK=30.5KB(30477B)/MEMORY≈19KB(均≤32KB✓,本轮0归档)。**未完成指令:有**(阶段2 GRPO待GPU释放+阶段3未交付)⇒**WAITING: 0**。

> 📦 wake #824（监控巡检·2026-11-06 18:42）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(165polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #822（预飞行验证巡检·2026-11-06 18:32）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO auto-launch全路径核验PASS(7项)·零GPU可执行动作·等GPU(ETA≈12/24)·WAITING=0。需要时再读。

> 📦 wake #821（监控巡检·2026-11-06 18:23）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 112polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #820（监控巡检·2026-11-06 18:16）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 107polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #819（监控巡检·2026-11-06 18:11）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 102polls全busy)·GPU 8×H100 94-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #818（监控巡检·2026-11-06 18:06）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 98polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #817（监控巡检·2026-11-06 18:02）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 94polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #816（监控巡检·2026-11-06 17:59）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 90polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #815（监控巡检·2026-11-06 17:54）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 86polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #814（监控巡检·2026-11-06 17:49）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 81polls全busy)·GPU 8×H100 95-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #813（监控巡检·2026-11-06 17:43）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 76polls全busy)·GPU 8×H100 93-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #812（监控巡检·2026-11-06 17:37）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 69polls全busy)·GPU 8×H100 96-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #811（监控巡检·2026-11-06 17:31）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 63polls全busy)·GPU 8×H100 95-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #810（监控巡检·2026-11-06 17:27）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 59polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #809（监控巡检·2026-11-06 17:22）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 53polls全busy)·GPU 8×H100 90-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #808（监控巡检·2026-11-06 17:18）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 49polls全busy)·GPU 8×H100 97-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #807（监控巡检·2026-11-06 17:12）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 44polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #806（监控巡检·2026-11-06 17:08）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 40polls全busy)·GPU 8×H100 96-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #805（监控巡检·2026-11-06 17:03）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 35polls全busy)·GPU 8×H100 98-100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #804（监控巡检·2026-11-06 16:56）已归档 → daily-memories-vision/2026-11-06.md；**结论**：GRPO chain健康(GPU-wait 29polls全busy)·GPU 8×H100 100%·零新发现·WAITING=0。需要时再读。

> 📦 wake #803（Phase2管线CPU预验证全PASS·2026-11-06 16:47）已归档 → daily-memories-vision/2026-11-06.md；**结论**：✅6项预验证全PASS(GRPO smoke/WaveQA-RL oracle/2B config/LoRA adapter/4脚本AST/chain log)·零bug·GPU释放后chain自动起训。需要时再读。

> 📦 wake #802（阶段1 SFT验收PASS·2026-11-06 16:30）已归档 → daily-memories-vision/2026-11-06.md；**结论**：✅✅SFT验收PASS(format100%/submit100%)·GRPO chain自动重启(PID1365749,GPU-wait)·报告+EXPERIMENTS§20.20已交付。需要时再读。

> 📦 wake #801（监控巡检·2026-11-06 16:14）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2825/3000 loss0.32 ETA~8min·包装器正确等待·训练健康·WAITING=0。需要时再读。

> 📦 wake #800（监控巡检·2026-11-06 16:10）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2750/3000 loss0.33 ETA~12min·包装器正确等待(waited3570s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #799（监控巡检·2026-11-06 16:05）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2650/3000 loss0.31 ETA~17min·包装器正确等待(waited3180s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #798（监控巡检·2026-11-06 15:57）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2475/3000 loss0.25 ETA~25min·包装器正确等待(waited2700s)·eval修复版已复核正确·训练健康·WAITING=0。需要时再读。

> 📦 wake #797（监控巡检·2026-11-06 15:50）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2350/3000 loss0.28 ETA~31min·包装器正确等待(waited2370s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #796（监控巡检·2026-11-06 15:43）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2200/3000 loss0.295 ETA~38min·包装器正确等待(waited1950s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #795（监控巡检·2026-11-06 15:39）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2100/3000 loss0.31 ETA~43min·step2000 ckpt已存·包装器正确等待(waited1650s)·训练健康·WAITING=0。需要时再读。
>
> 📦 wake #794（监控巡检·2026-11-06 15:33）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step2000/3000 loss0.34 ETA~47min·step2000 ckpt已存·in-training eval submit=0%系已知bug(gating=包装器修复版eval)·包装器正确等待·训练健康·WAITING=0。需要时再读。

> 📦 wake #793（监控巡检·2026-11-06 15:27）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step1900/3000 loss0.33 ETA~52min·post-SFT eval包装器正确等待(waited960s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #792（监控巡检·2026-11-06 15:19）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step1725/3000 loss0.27 ETA~60min·post-SFT eval包装器正确等待(waited480s)·训练健康·WAITING=0。需要时再读。

> 📦 wake #790（eval设计缺陷修复·2026-11-06 14:55）已归档 → daily-memories-vision/2026-11-06.md；**结论**：发现并修复sft_train_wave.py/eval_sft_wave.py的eval只生成第1个assistant turn找submit()→永远0%的bug(改为第4个submit turn检查),step1000 ckpt 10样本测试4/4通过,kill GRPO chain待重跑eval。wake#791已据此部署自动eval包装器。需要时再读。

> 📦 wake #789（监控巡检·2026-11-06 14:35）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step750/3000 loss0.34(plateau) ETA~106min·无eval yet·GRPO chain alive待GPU·pretrain零干扰·WAITING=0。需要时再读。

> 📦 wake #788（监控巡检·2026-11-06 14:27）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step625/3000 loss0.38(plateau) ETA~112min·无eval yet·GRPO chain alive待GPU·pretrain零干扰·WAITING=0。需要时再读。

> 📦 wake #787（监控巡检·2026-11-06 14:17）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step450/3000 loss0.37 ETA~121min·无eval yet·GRPO chain alive待GPU·pretrain零干扰。需要时再读。

> 📦 wake #786（监控巡检·2026-11-06 14:12）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT step300/3000 loss0.38 ETA~127min·eval只查格式⇒0.34epoch极可能通过·GRPO chain alive待GPU·pretrain零干扰。需要时再读。

> 📦 wake #785（阶段1 SFT CPU训练启动·2026-11-06 14:02）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU SFT启动PID2882778,loss1.47→0.64,ETA≈2.4h,GRPO chain待衔接。需要时再读。

> 📦 wake #784（监控巡检·2026-11-06 13:36）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #783（监控巡检·2026-11-06 13:30）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #782（监控巡检·2026-11-06 13:24）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #781（监控巡检·2026-11-06 13:16）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #780（监控巡检·2026-11-06 13:11）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双pollers健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #779（监控巡检·2026-11-06 13:06）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #778（监控巡检·2026-11-06 13:01）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #777（监控巡检·2026-11-06 12:56）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #776（监控巡检·2026-11-06 12:49）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #775（监控巡检·2026-11-06 12:44）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #774（监控巡检·2026-11-06 12:40）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #772（监控巡检·2026-11-06 12:29）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #771（监控巡检·2026-11-06 12:28）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #770（监控巡检·2026-11-06 12:18）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #769（监控巡检·2026-11-06 12:13）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #767（监控巡检·2026-11-06 12:03）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #765（监控巡检·2026-11-06 11:54）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #764（监控巡检·2026-11-06 11:47）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #763（监控巡检·2026-11-06 11:40）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #762（监控巡检·2026-11-06 11:32）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #761（监控巡检·2026-11-06 11:24）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #760（监控巡检·2026-11-06 11:17）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #759（监控巡检·2026-11-06 11:13）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #758（监控巡检·2026-11-06 11:07）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #757（监控巡检·2026-11-06 10:59）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #754~#755（监控巡检·2026-11-06 10:41~10:48）已归档 → daily-memories-vision/2026-11-06.md；**结论**：状态无变化，双poller健康，GPU满载仅待GPU。需要时再读。

> 📦 wake #741（CPU端到端训练循环验证PASS·2026-11-06 09:0x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：_cpu_train_validate.py 7/7 ALL PASS（loss单调下降/LoRA 69.7M/ckpt save+reload/生成合法），Phase1 CPU侧100%验证完成仅待GPU。需要时再读。

> 📦 wake #734（监控巡检+ETA修正·2026-11-06 08:25）已归档 → daily-memories-vision/2026-11-06.md；**结论**：双poller健康，ETA修正12/3→12/25（iter_90000时间戳纠偏18:49→10:09:46,~7.0s/iter）。需要时再读。

> 📦 wake #732（R9已完成修正+GRPO超时扩展+重启·2026-11-06 08:04）已归档 → daily-memories-vision/2026-11-06.md；**结论**：修正R9已于10/2完成,实际GPU阻塞=pretrain S1;GRPO chain SFT_WAIT_MAX 30→90天+重启PID2466702。需要时再读。

> 📦 wake #731（阶段1就绪审计+数据泄漏验证+就绪报告HTML·2026-11-06 07:4x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：CPU侧100%就绪(泄漏PASS/模型加载PASS/报告HTML交付)，但"R9 ETA≈11/25-27"系误判(wake#732已修正：R9 10/2已完成,实际阻塞方=pretrain S1)。需要时再读。

> 📦 wake #275~#753 旧流水（~130条，2026-10-26~11-06，含Phase0 YELLOW/Phase1就绪审计/SFT数据9013条/GRPO CPU冒烟/2B骨干提取/CPU训练循环验证等里程碑+大量监控巡检）已归档 → daily-memories-vision/2026-10-{24..31}.md + 2026-11-{01..06}.md + ARCHIVE_OPERATOR_VISION.md。**结论**：详见各日文件。需要时再读。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🟢 **波形 RL 阶段0交付(YELLOW) + 阶段1 SFT已交付PASS(format100%/submit100%) + Phase 2管线CPU预验证全PASS(零bug) + GRPO chain健康待GPU(PID1365749,GPU-wait,ETA≈12/24)**。wake#803预验证:GRPO smoke PASS/WaveQA-RL oracle PASS/2B模型config OK/LoRA adapter OK/4脚本AST OK/chain log正确。GPU全占(pretrain ETA≈12/24)。阶段2 GRPO待GPU,阶段3未交付。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | 阶段1 SFT验收PASS(wake#802) · 阶段1 SFT CPU训练完成step3000(wake#802) · 阶段1 SFT CPU训练启动(wake#785) · CPU端到端训练循环验证7/7 PASS(wake#741) · 数据泄漏验证+阶段1就绪报告HTML(wake#731) · 全管线就绪审计(wake#714) · GRPO链式启动器修复+启动(wake#626) · GRPO CPU冒烟测试PASS(wake#622) · 2B文本骨干提取1.72B(wake#620) · 数据集均衡化9013条(wake#618) · WaveQA-RL oracle 300题(wake#614) · 波形RL阶段0 YELLOW(wake#609) · 论文改稿(wake#437~#442) · 波形RL计划书(wake#435) · OCR合成10M(wake#275) · ArmE-R2/ArmD-R2 全链路 |
| 当前动作 | **Phase 2管线预验证完成(wake#803)，GRPO chain等待GPU**：CPU侧全验证PASS(GRPO smoke/WaveQA-RL oracle/2B模型config/LoRA adapter/4脚本AST)。GRPO chain PID1365749 alive(GPU-wait轮询,60s间隔,guard:util<10%+mem<5000MiB,3x consecutive)。chain log确认:SFT eval detected→acceptance passed→step3000 ckpt found→GPU-wait。 |
| 下一步 | 等GPU释放(ETA≈12/24)→GRPO chain自动启动阶段2训练(~12 GPU·h,torchrun 8GPU,2B model+step3000 LoRA)→WaveQA-RL 300题评测+回归护栏→阶段2报告+EXPERIMENTS§21。若GPU释放后GRPO训练crash→排查。下轮wake检查GRPO chain日志+GPU状态。 |
| 阻塞 | .12+.29 GPU全占（8×H100 96-100% util / ~75GB，pretrain baize2b ETA≈12/24-25）→ 阶段2 GRPO需GPU（GRPO chain PID1365749自带GPU-wait,释放后自动起训）·.17+.75 SSH不可达 |
| 更新 | **2026-11-06 18:3x (wake #822)**: ✅预飞行验证巡检·GRPO auto-launch全路径核验PASS(SFT eval pass/step3000 ckpt/2B骨干/WaveQA-RL300/chain健康/script args)·GPU 8×H100 91-100%(pretrain PID2612442 etimes≈94.6h ETA≈12/24)·零GPU可执行动作·体积TASK=29.8KB/MEMORY=18.3KB✓·WAITING=0 |