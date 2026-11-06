# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

> 🆕 **【wake #790 · 2026-11-06 14:41→14:55】🔧关键修复·发现并修复eval设计缺陷+验证fix有效。CPU SFT step1150/3000 loss0.29 ETA~88min。**发现`evaluate_format_and_submit`(sft_train_wave.py)和`evaluate`(eval_sft_wave.py)只生成第一个assistant turn(=open(file))就在其中找submit()——但submit()在第4个assistant turn⇒submit_success_rate永远=0%=纯eval bug非训练问题。已修复两文件:format检查在第1个assistant turn,submit检查在GT含submit()的assistant turn(第4个)。step1000 ckpt上10样本测试:4/4 fmt=True sub=True(rel_err 0.034~5.15,step1000数值精度尚低但格式全对)⇒**fix验证通过**。已kill GRPO chain PID2466702(防止它捡到训练结束时的flawed eval_results.json pass=false后退出)。**计划**:训练step3000(~16:19)结束后→用修复版eval_sft_wave.py重跑eval→写正确eval_results.json→重启GRPO chain。GPU全占(8×H100 100%,pretrain ETA≈12/24)。📦体积:TASK=30.5KB/MEMORY=11.5KB(均≤32KB✓)。**未完成指令:有**(阶段1 SFT进行中+eval修复待step3000后重跑)⇒**WAITING: 0**。

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
| PHASE | 🟠 **波形 RL 阶段0交付(YELLOW) + 阶段1 SFT CPU训练进行中(PID2882778,step1150/3000,loss0.29,ETA~88min~16:19) · eval设计缺陷已修复(wake#790) · GRPO chain已kill(待step3000后重跑eval+重启)**。loss已稳定在0.29-0.39平台(SFT正常收敛)。**eval_results.json(旧flawed版)会在step3000写入——需用修复版eval_sft_wave.py重跑覆盖**。GPU全占(pretrain ETA≈12/24)。阶段2/3未交付。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | 阶段1 SFT CPU训练启动(wake#785) · CPU端到端训练循环验证7/7 PASS(wake#741) · 数据泄漏验证+阶段1就绪报告HTML(wake#731) · 全管线就绪审计(wake#714) · GRPO链式启动器修复+启动(wake#626) · GRPO CPU冒烟测试PASS(wake#622) · 2B文本骨干提取1.72B(wake#620) · 数据集均衡化9013条(wake#618) · WaveQA-RL oracle 300题(wake#614) · 波形RL阶段0 YELLOW(wake#609) · 论文改稿(wake#437~#442) · 波形RL计划书(wake#435) · OCR合成10M(wake#275) · ArmE-R2/ArmD-R2 全链路 |
| 当前动作 | **CPU SFT训练进行中+eval修复完成**：PID2882778(.12,~53核,nice-n10),step1150/3000,loss0.29,ETA~88min。**eval设计缺陷已修复**(sft_train_wave.py+eval_sft_wave.py):旧版只生成第1个assistant turn找submit()→永远0%;修复版在第4个assistant turn(submit turn)检查submit()。step1000 ckpt测试4/4 fmt=True sub=True。GRPO chain PID2466702已kill。 |
| 下一步 | 等CPU SFT训练结束(step3000~16:19)→用修复版eval_sft_wave.py重跑eval(覆盖flawed eval_results.json)→若pass(fmt≥90%+submit≥70%)→重启GRPO chain(待GPU,ETA≈12/24)→若fail→重启nsteps=24000 |
| 阻塞 | .12+.29 GPU全占（16×H100 88-100% util / ~75GB，pretrain baize2b ETA≈12/24-25）→ 阶段1 SFT已用CPU绕过·阶段2 GRPO仍需GPU（ETA≈12/24）·.17+.75 SSH不可达 |
| 更新 | **2026-11-06 14:55 (wake #790)**: 🔧关键修复:发现并修复eval设计缺陷(只生成第1个assistant turn找submit()→永远0%)→修复版在第4个turn检查submit()→step1000 ckpt测试4/4通过→已kill GRPO chain待重跑eval·CPU SFT step1150/3000 loss0.29·WAITING=0 |