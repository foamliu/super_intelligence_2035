# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

> 🆕 **【wake #801 · 2026-11-06 16:14】📊监控巡检·训练健康·step2825/3000·ETA~8min·包装器正确等待。**训练PID2882778 alive(etimes8230s≈137min,ppid=1,2 dataloader子进程2894887/2894951),step2825/3000,loss0.3191,0.35step/s,ETA8.4min(~16:23完成)。step1000+step2000 ckpt已存(LoRA 278MB)。post-SFT eval包装器PID4104838 alive(ppid=1,30s轮询,waited3780s≈63min)正确等待——日志`[16:14:16] training still running (waited 3780s)`确认健康。eval_results.json尚不存在(训练未到step3000)。GPU全占(8×H100 96-100%util/~75GB,pretrain ETA≈12/24),CPU SFT无GPU冲突。GRPO chain未运行(killed,待eval pass后由包装器setsid重启,自带安全GPU-wait)。📦体积:TASK=30.5KB/MEMORY=13.7KB(均≤32KB✓,本轮0归档)。**未完成指令:有**(阶段1 SFT训练进行中+eval待包装器自动触发)⇒**WAITING: 0**。

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
| PHASE | 🟠 **波形 RL 阶段0交付(YELLOW) + 阶段1 SFT CPU训练进行中(PID2882778,step2825/3000,loss0.32,ETA~8min~16:23) · eval设计缺陷已修复(wake#790,在盘,已复核正确)但运行进程内存仍是旧flawed版(无法热注入) · post-SFT自动eval包装器已部署(PID4104838,setsid,待训练结束触发:跑修复版eval→覆盖flawed eval_results.json→pass则重启GRPO) · GRPO chain已kill(待eval pass后由包装器重启)**。loss稳定0.28-0.33平台(SFT正常收敛)。GPU全占(pretrain ETA≈12/24)。阶段2/3未交付。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | 阶段1 SFT CPU训练启动(wake#785) · CPU端到端训练循环验证7/7 PASS(wake#741) · 数据泄漏验证+阶段1就绪报告HTML(wake#731) · 全管线就绪审计(wake#714) · GRPO链式启动器修复+启动(wake#626) · GRPO CPU冒烟测试PASS(wake#622) · 2B文本骨干提取1.72B(wake#620) · 数据集均衡化9013条(wake#618) · WaveQA-RL oracle 300题(wake#614) · 波形RL阶段0 YELLOW(wake#609) · 论文改稿(wake#437~#442) · 波形RL计划书(wake#435) · OCR合成10M(wake#275) · ArmE-R2/ArmD-R2 全链路 |
| 当前动作 | **CPU SFT训练进行中 + post-SFT eval包装器已部署待触发**：训练PID2882778(.12,64线程),step2825/3000,loss0.32,ETA~8min。step1000+step2000 ckpt已存(LoRA 278MB)。**eval修复在盘(wake#790,已复核正确)但运行进程内存=旧flawed版**⇒step3000会写flawed eval_results.json。已部署`run_post_sft_eval.sh`(PID4104838,setsid,flock):等训练完成→备份flawed→CPU跑修复版eval_sft_wave.py(max_eval=100)覆盖eval_results.json→pass则重启GRPO chain。 |
| 下一步 | 等CPU SFT训练结束(step3000~16:23)→**post-SFT包装器自动触发**:备份flawed eval→CPU跑修复版eval_sft_wave.py覆盖eval_results.json→若pass(fmt≥90%+submit≥70%)→包装器自动重启GRPO chain(待GPU,ETA≈12/24)→若fail→下轮wake重启nsteps=24000。下轮wake检查包装器日志post_sft_eval.log确认eval结果+GRPO是否重启。 |
| 阻塞 | .12+.29 GPU全占（8×H100 96-100% util / ~75GB，pretrain baize2b ETA≈12/24-25）→ 阶段1 SFT已用CPU绕过·阶段2 GRPO仍需GPU（ETA≈12/24,GRPO chain由包装器在eval pass后重启,自带安全GPU-wait）·.17+.75 SSH不可达 |
| 更新 | **2026-11-06 16:14 (wake #801)**: 📊监控巡检——训练健康(step2825/3000 loss0.32 ETA~8min)+包装器正确等待(waited3780s,30s轮询)+eval修复版已复核正确。step1000+step2000 ckpt已存。GPU全占(8×H100 96-100%util,pretrain ETA≈12/24)。体积TASK=30.5KB/MEMORY=13.7KB✓·WAITING=0 |