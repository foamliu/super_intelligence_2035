# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ 运维令13:3x DONE（唤醒690,15:0x）**：分词 SFT-2605(94 shard/18.89B tok/75.87GB)+Agent-2609(13 shard/5.97B tok/23.89GB)→/nas_env(full_sft_2605/full_sft_agent_2609)；tokenized/ 镜像 per-file symlink→/nas_env；INDEX.tsv 922 shard triplet全OK inode_ok；DATA_MAPPING.md(10603B)行11-12=镜像完整；report_data_mapping_zh.html(20764B)12源全量更新；commit 44b512316 pushed。

> 🟢 **✅ 迁移5/5源全DONE**：math_l3✅+code_l3✅+math_l1✅+ufw_l3✅+code_l2✅(5源574bins/4.24TB全迁/nas_env,软链接全建好,源已删)。
> 🟢 **✅ 3稳定源迁移FINALIZE(唤醒678,00:3x)**：l1_en_hq(94shards)+zh(4)+AICC(1)→build_tokenized_mirror.py改symlink指向/nas_env/full_*→INDEX.tsv rebuild(815shard全triplet=OK inode=OK,3源storage=symlink)→DATA_MAPPING.md regen(指纹2953/7f2a09fb2920/00:34)→report_data_mapping_zh.html全量更新(总17.47TB,df 85%/82%)。源文件run4已删。
> 🟢 **✅ ufw_en迁移DONE(唤醒682,05:2x)**：ufw_en 32 shard / 3,222,004,397,626 B / 905.92B tokens → /nas_env/full_ufw_en/。text/源文件已删,tokenized/ 96 hardlink → per-file symlink指向/nas_env。build_tokenized_mirror.py改ufw_en ENTRIES(src_dir→/nas_env,storage=symlink)→INDEX.tsv rebuild(storage=symlink,triplet=OK,inode_ok=32)→DATA_MAPPING.md regen(bytes=3,222,004,397,626,storage=symlink)→gen_report_data_mapping_html.py新增报告生成脚本→report_data_mapping_zh.html重生成(9 symlink+1 hardlink,correct bytes)。commit ace6fac0b pushed。
> 🟢 **✅ 4源迁移全部完成**：ufw_en(32)+l1_en_hq(94)+zh(4)+AICC(1)=131 shard ≈ 4.05 TB → /nas_env。连同此前5源(574 shard/4.24TB)，/nas_env共承载9源/705 shard/~8.3TB；env14(110 shard)仍hardlink留/nas_train。
> 🟢 **✅ df实测(05:2x)**：/nas_train 174T已用/34T可用(84%,较迁移前177T/86%释放~3TB)；/nas_env 8.2T已用/1.8T可用(83%)。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅运维令10:1x暂停下载DONE.无活跃下载/迁移进程(.12验),12源全部镜像完整.例行巡检中
已完成:       ✅运维令10:1x暂停下载(pgrep验.12无download_85m/hf/rsync/wget/aria2进程,判据满足);✅运维令13:3x SFT分词全DONE;✅运维令08:3x刷新两文件;✅12源全部镜像完整(922shard)
当前动作:     唤醒868(2026-10-30 14:43):例行心跳巡检(上次心跳@14:26距今~17min)→①git fetch=up to date,无data新令✓;②pgrep验无下载/迁移进程✓;③df /nas_train 173T/84%(35T可用)+/nas_env 8.3T/84%(1.7T可用)✓;④体积MEMORY 22.4KB/TASK 35.7KB→均在限内✓;⑤ops/inbox=RUN_ID224(pretrain重启,非data令)✓;⑥更新心跳+日报+commit+push
下一步:       待「恢复下载」新令.此前不发起新下载/迁移.WAITING:1
阻塞:         无
ERROR_COUNT:  10
未完成指令:   无(所有运维令已DONE)→WAITING:1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [14:43] 唤醒868：例行心跳巡检(上次心跳@14:26距今~17min) → ①git fetch=up to date,无data新令✓;②pgrep验无下载/迁移进程✓;③df /nas_train 173T/84%(35T可用)+/nas_env 8.3T/84%(1.7T可用)✓;④体积MEMORY 22.4KB/TASK 35.7KB→均在限内✓;⑤ops/inbox=RUN_ID224(pretrain重启,非data令)✓;⑥更新心跳+日报+commit+push.未完成指令:无(所有运维令已DONE)→WAITING:1
>
> 📦 唤醒867(10-30 14:26)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒866(10-30 14:08)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒865(10-30 13:49)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒864(10-30 13:31)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒862(10-30 12:56)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒860(10-30 12:21)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒859(10-30 12:03)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒858(10-30 11:46)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒856(10-30 11:08)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒854(10-30 10:32)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒853(10-30 10:15)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒852(10-30 09:57)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒849(10-30 09:04)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒847(10-30 08:29)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒846(10-30 08:12)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒845(10-30 07:55)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒843(10-30 07:21)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒842(10-30 06:47)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒841(10-30 06:30)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒840(10-30 06:13)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒839(10-30 05:56)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒838(10-30 05:38)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒837(10-30 05:21)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒836(10-30 05:04)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒834(10-30 04:30)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒833(10-30 04:13)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒831(10-30 03:38)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒830(10-30 03:21)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒828(10-30 02:46)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒827(10-30 02:28)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒826(10-30 02:10)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒825(10-30 01:52)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒823(10-30 01:18)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒822(10-30 01:00)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒821(10-30 00:42)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒820(10-30 00:25)原文归档 → daily-memories-data/2026-10-30.md（例行巡检,详见日文件）
>
> 📦 唤醒817(10-29 23:33)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒816(10-29 23:15)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒814(10-29 22:40)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒813(10-29 22:22)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒812(10-29 22:05)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒810(10-29 21:30)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒808(10-29 20:57)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒806(10-29 20:05)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒804(10-29 19:31)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒802(10-29 18:55)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒801(10-29 18:37)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒797(10-29 17:10)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒796(10-29 16:52)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒795(10-29 16:35)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒794(10-29 16:16)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒793(10-29 15:58)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒792(10-29 15:40)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒789(10-29 14:47)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒788(10-29 14:29)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒787(10-29 14:11)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒786(10-29 13:52)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒785(10-29 13:35)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒784(10-29 13:18)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒783(10-29 13:00)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒782(10-29 12:43)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒781(10-29 12:25)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒780(10-29 12:08)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒776(10-29 10:41)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒775(10-29 10:23)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒774(10-29 10:05)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒773(10-29 09:47)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒771(10-29 09:10)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒770(10-29 09:02)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒769(10-29 08:45)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒768(10-29 08:27)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒767(10-29 08:09)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒765(10-29 07:35)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒764(10-29 07:18)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒762(10-29 06:44)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒761(10-29 06:26)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒760(10-29 06:09)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒759(10-29 05:52)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒758(10-29 05:35)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒757(10-29 05:17)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒756(10-29 05:00)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒755(10-29 04:43)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒752(10-29 03:35)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒751(10-29 03:18)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒750(10-29 03:01)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
> 📦 唤醒749(10-29 02:43)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒748(10-29 02:20)原文归档 → daily-memories-data/2026-10-29.md（例行巡检+归档旧流水降MEMORY体积,详见日文件）
>
> 📦 唤醒747(10-29 02:02)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒746(10-29 01:45)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒745(10-29 01:27)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒744(10-29 01:09)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒743(10-29 00:52)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒742(10-29 00:33)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒741(10-29 00:15)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒740(10-28 23:57)原文归档 → daily-memories-data/2026-10-29.md（例行巡检,详见日文件）
>
> 📦 唤醒739(10-28 23:40)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒737(10-28 23:04)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒736(10-28 22:48)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒735(10-28 22:28)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒734(10-28 22:10)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒732(10-28 21:33)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒731(10-28 21:15)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒729(10-28 20:40)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒728(10-28 20:22)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒726(10-28 19:44)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒725(10-28 19:27)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒724(10-28 19:09)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒723(10-28 18:51)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒722(10-28 18:33)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒721(10-28 18:16)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒632-719(10-24~10-28)原文归档 → daily-memories-data/2026-10-{24,25,26,27,28}.md（例行巡检+SFT分词+迁移+暂停下载全程,详见各日文件）

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。
### ①-⑧ 已归档（详见 `daily-memories-data/2026-10-06.md`）

| # | 主题 | 结论 | 日期 |
|:--|:--|:--|:--|
| ① | SFT-2605 重下 | ✅ 1504 jsonl / 318.99 GB，与 HF 官方清单逐字节一致 | 10-02 |
| ②-④ | D-CLEAN-1/2/3 | ✅ 盘点 + 删除 servers(974G)+nemo R1(310G)+laion(7.8G)+pip(3.3G) ≈1.3T；nemo R2 ckpt 保留 | 10-03 |
| ⑤ | 下载白名单 | ✅ 停 en_v1_4，只下 l1_en_hq+zh+GPIC | 10-03 |
| ⑥-⑦ | D-CLEAN-4 + LLaVA ckpt | ✅ 盘点：本用户可回收 ≈11.4TiB(含 LLaVA-OV 22TiB iter ckpt)，待运维拍板 | 10-04 |
| ⑧ | LIT_IDEAS HTML | ✅ 产出 `LIT_IDEAS_2026-10-05.html`（52 entries/0 unverified/62% turnover），含成本专章+ISEDA投稿要求(4-6页) | 10-04 |
> 📦 §⑨ 配比实验可行性核查 + §⑩ 运维三问 + 旧状态头（2026-10-05~07）已归档 → `daily-memories-data/2026-10-10.md`（唤醒305归档）；**结论**：⑨GPU2-7当时被P-9.8/9.9占满(现已释放)⑩三问已答(GPIC无加速/base下载全满/BO波次锯齿非I/O)。需要时再读。

> 📦 §⑪ 分词5worker+85M线路（2026-10-24 用户质询）已归档 → daily-memories-data/2026-10-24.md；**结论**：Q1=5worker因串行+剩余shard少,升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT)。需要时再读。

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **✅ 已下满并核验一致（2026-10-02 唤醒 37）**：落盘 **1504 jsonl / 318,990,252,711 B = 318.99GB（297.08 GiB）**，`.incomplete` = 0，**与 HF 官方清单（1504 文件 / 318,990,252,711 B）逐字节完全一致**；逐子目录 `no_think` 855✓（CG 50/Code 300/IF 20/Kn 80/Math 300/ML-Kn 50/ML-Math 55）+ `think` 649✓（CG 50/Code 279/IF 20/Kn 50/Math 250）。token `hf_lqLxH…`（用户 foamliu）。

> 📦 旧流水（唤醒111-145, S0a训练+分词+kill改道全程）已归档 → `daily-memories-data/2026-10-05.md` 及 `2026-10-06.md`
> 关键结论：①base分词22.05B tok✅ ②SFT-2605 20.97B+Agent-2609 全4shard✅ ③S0a 2.2B单臂浪费~100 GPU·h→改道proxy BO搜索 ④proxy模型92.7M(d=512/L=14)标定s/step=1.5s ⑤smoke test✅

> 📦 §s_step归因实验（2026-10-06）已归档 → `daily-memories-data/2026-10-06.md`；**结论**：MBS=16使s_step 1432ms→166ms(8.6×),overhead-bound,D=0.5B/trial→205trial/24h。需要时再读。
## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污�