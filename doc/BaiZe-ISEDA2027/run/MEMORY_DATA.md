# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ▶️en_v1_4下载受阻(proxy503)+✅/tmp清理完成+✅✅WebMix下完+✅✅RL-2609下完自校通过+✅SFT-2605复核通过+✅✅InternVL-SA1B下完+✅wit_base完成+85M暂停+✅GPIC+✅R3分词→P-8数据层全就绪
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200(ρ=−0.43); s_step归因; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); R3全量分词110/110DONE(1483.91B tok/5.94TB); R3污染扫描30/30DONE(60K,0命中,累计220K全0)→P-8数据层全就绪; ✅GPIC下载完成(8160tar@/nas_inference,12T); ✅85M暂停(用户令10-13); ✅4路HF图文对下载; ✅the_cauldron完成(938parquet/158G); ✅全部4路暂停→恢复断点续传(用户令10-14); ✅wit_base完成(330/330/287G); ✅SFT-2605复核通过(1504jsonl/318990252711B/0incomplete,2026-10-15); ✅✅UltraData-RL-2609下载完成+自校通过(20jsonl/187632276428B=174.75GiB/26files逐文件字节比对全PASS/0incomplete,落盘/nas_env,2026-10-16 01:26完成); ✅✅InternVL-SA1B下载完成(2000tar/1.5T/0incomplete,落盘/nas_user,2026-10-16 21:29); ✅✅WebMix-38M下载完成(3886parquet/1.9T/0incomplete,落盘/nas_user,2026-10-17 15:10); ✅/tmp清理完成(运维令10-17,唤醒511-518,data线>1天残留=0); ✅唤醒501-509多次复核SFT-2605+RL-2609均确认在盘且完整
当前动作:     唤醒519(2026-10-18 02:49) /tmp清理复核+en_v1_4看护:①/tmp data线>1天残留=0(仅en_v1_4_marker 0B活跃标记),运维令10-17已闭合;②en_v1_4:43520par/56461=77.1%/4.1T/0inc,85/110shards done,wrapper PID606504 alive(etimes≈41h),当前shard[99/110]CC-MAIN-2024-30 retry2/5 FAIL(ProxyError 503),proxy huggingface.co HTTP=000 timeout20s❌/github.com HTTP=200✅→基础设施故障持续;wrapper存活重试中,不kill(重启同样503),proxy恢复自动续传,wrapper若退出则下轮重启。85M⏸暂停。📦体积:TASK=32458B(32KB)/MEMORY=30KB
下一步:       ①proxy恢复后en_v1_4自动续传(若wrapper已退出则需手动重启download_en_v1_4.sh); ②85M维持暂停(用户令10-13); ③P-8投料等运维指示; ④RL-2609+SFT-2605+InternVL+WebMix+wit_base+the_cauldron已就绪
阻塞:         proxy 172.19.92.25:13128返回503 Service Unavailable(ERR_CONNECT_FAIL 111),en_v1_4下载受阻,需运维检查.29代理到huggingface.co连通性; 85M暂停(用户令10-13); P-8投料等运维指示
ERROR_COUNT:  7
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [02:49] 唤醒519：/tmp清理复核+en_v1_4看护。①/tmp:data线>1天残留find复核=0(仅en_v1_4_marker 0B活跃标记🚫未动,别线ray/lmms_eval/R5-R9/circuit_sense/terminal-bench等未动),运维令10-17(清理.12的/tmp)已闭合。df /tmp:45G/49G avail(49%,无变化)。②en_v1_4:43520par/56461=77.1%/4.1T/0inc,85/110shards done。wrapper PID606504 alive(etimes=148152s≈41h,ppid=1),log /tmp/en_v1_4_dl.log活跃(4.1MB,02:47更新),当前[99/110]CC-MAIN-2024-30 retry2/5 FAIL:ProxyError 503(huggingface.co tunnel ERR_CONNECT_FAIL 111)。proxy 172.19.92.25:13128:huggingface.co HTTP=000 timeout20s❌,github.com HTTP=200✅→基础设施故障持续。wrapper存活且重试中→不kill(重启同样503),proxy恢复自动续传,wrapper若退出则下轮手动重启download_en_v1_4.sh。③85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=30KB
> [01:23] 唤醒518：/tmp清理收尾+en_v1_4看护(运维令10-17)。①/tmp:find -mtime +1发现2个data线残留:rl2609_verify.log(0B,Oct16)+rl2609_selfcheck_result.txt(3.8K,Oct16),均rm✅,最终find复核data线>1天残留=0(仅余vision/harness线文件🚫未动)。df /tmp:45G/49G avail。②en_v1_4:43520par/56461=77.1%/4.1T/0inc,85/110shards done。shard86(CC-MAIN-2022-27)hf PID1116479(etimes=4874s≈81min)0%CPU+0文件,IO计数器15s不变(rchar=10373848不变)→判定僵死,kill✅。wrapper retry:shard86 FAIL×5,proxy 172.19.92.25:13128返回503 Service Unavailable(ERR_CONNECT_FAIL 111,huggingface.co tunnel失败)。shard86 GIVE UP,wrapper移至shard87(CC-MAIN-2022-33)继续(同样503)。proxy端口open但tunnel503=基础设施故障(proxy可到github.com但不可到huggingface.co)。wrapper PID606504 alive(etimes≈39.9h),遍历剩余shards 87-110(均因proxy503失败)。③85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=32KB
> [00:12] 唤醒517：/tmp清理收尾(运维令10-17「清理.12的/tmp」)。唤醒511已清大项718M(work dirs),515/516已清小项,本轮find -mtime +1深度扫描发现仍残留大量data线>1天旧文件(~29M),分6类全部rm✅:①contam_*.{log,md,txt}×60(Oct1-10,contamination扫描全量报告)②cr3r_*.md×6+finish_contam_r3.{sh,out}(Oct10,R3 contam收尾)③gpic日志/探针/snapshot×10:e1_gpic_count.{log,py}+r11_gpic*.log+r4_gpic.log+r6_gpic_probe.{out,py}+r11f_gpic_snapshot.txt(211K)+.gpic_marker(Oct1-7)④ultrax:ultrax_restart.log+launch_ultrax.sh+ultrax_check/(88K,Oct7)⑤85M:85m_api.json+85M_dl.log(34K,Oct10-13)⑥其他:r2_tokenize_launch.log(Oct9)+_baize_llm_cand.json(Oct4)+sft2605_test/(28M,Oct1)+sft2605_tree.json(330K)+sft2605_dl.log(15K)+sum_sft2605.py(Oct1-2)。find复核:data线>1天残留=0(仅余test_openvision2_data/*.tar=vision线+open_clip_baize_clean.py=vision线,🚫未动)。🚫未动:baize_data_loop.log/last_push/llm_idx(活跃loop)+en_v1_4_dl.log(活跃下载,Oct18 00:05)+webmix38m_dl.log(<1天,Oct17 15:10)+BAIZE2B_mamba2_train.log(pretrain)+lmms_eval_app.t0002965(别用户)+全部别线文件。df /tmp:45G→45G used/49G avail(29M低于df G级精度)。en_v1_4健康巡检:43520par/56461=77.1%/4.1T/0inc,wrapper PID606504(etimes=138836s≈38.6h,ppid=1)✅+hf PID1116479(etimes=468s≈7.8min,CC-MAIN-2022-27,ppid=606504)✅,lastfile00:04 CC-MAIN-2022-21/part-0512(刚下完该CC batch),活跃✅,+287par/~73min≈3.9par/min,ETA~12941par/3.9≈2.3天。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=29823B(29KB)
> [22:59] 唤醒516：/tmp清理补遗(运维令10-17)。唤醒511已清大项718M(work dirs),本轮find -mtime +1扫描发现剩余小项data线旧残留(均>1天未动):4个baize_tokenize_*_par日志目录(Oct7-8,~980K)+BAIZE_DATA_TASK_new.md(Oct7,30K)+hf_probe/search/meta.py(Oct1)+hf_dl_base.log(Oct6)+baize_tokenize_zh*.log(Oct7)+baize_download_ultrax_outer.log(Oct7)+contam_r3_*.md×24(Oct10,~29K)+bothfair_run.log(Oct10)+hf_85m_*.{log,json,txt,py}(Oct11)+hf_env1_4_check.log(Oct11)+check_hf_features.py(Oct13)+cauldron_dl.log(Oct14,399K)+wit_base_dl.log(Oct15,95K)+check_dataset_fix.sh(Apr15)。全部rm✅。find复核:data线>1天残留=0。🚫未动:baize_data_loop.log/last_push/llm_idx(活跃loop文件)+webmix38m_dl.log(<1天,Oct17 15:10)+别线全部文件。df /tmp:45G→45G used/49G avail(小文件~1.5MB,df精度G级无变化)。en_v1_4健康巡检:43233par/56461=76.6%/4.0T/0inc,wrapper PID606504(etimes=134450s≈37.3h,ppid=1)✅+hf PID1380718(etimes=2785s≈46min,CC-MAIN-2022-21 part-0225-of-512)✅,lastfile22:57:47 part-0225,活跃✅,+410par/~72min≈5.7par/min,ETA~13228par/5.7≈1.6天。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=28KB
> [21:47] 唤醒515：en_v1_4健康巡检(运维令10-17 /tmp清理已完成,本轮复核无data线残留)。en_v1_4:42823par/56461=75.8%/4.0T/0inc,wrapper PID606504(etimes=130055s≈36.1h)+hf PID150453(etimes=2857s≈47min,CC-MAIN-2022-05 part-0327-of-512),lastfile21:46:33 part-0327,活跃✅,+503par/~1.1h≈7.6par/min,ETA~13638par/7.6≈1.2天。85M⏸暂停(无进程)。/tmp:45G used/49G avail(无data线残留,du确认最大项为lmms_eval 18G/test_lang_mcore 8.3G等别线文件)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32458B(32KB)/MEMORY=28KB
> [20:36] 唤醒514：en_v1_4健康巡检(运维令10-17 /tmp清理已完成,本轮复核无data线残留)。en_v1_4:42320par/56461=74.9%/4.0T/0inc,wrapper PID606504(etimes=125836s≈34.9h)+hf PID3570013(etimes=2701s≈45min,CC-MAIN-2021-49 part-0340-of-512),lastfile20:36:15 part-0340,活跃✅,+486par/~72min≈6.75par/min,ETA~14141par/6.75≈1.5天。85M⏸暂停(无进程)。/tmp:45G used/49G avail(无data线残留)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=27KB
> [19:24] 唤醒513：en_v1_4健康巡检(运维令10-17 /tmp清理已由唤醒511完成,acf82d12已push)。en_v1_4:41834par/56461=74.1%/3.9T/0inc,wrapper PID606504(etimes=121550s≈33.7h)+hf PID1398554(etimes=3698s≈1h,CC-MAIN-2021-43 part-0363),lastfile19:24 part-0362-of-512,活跃✅,+424par/~72min≈5.9par/min,ETA~14627par/5.9≈1.7天。85M⏸暂停(无进程)。全部已下满数据集在盘确认:SFT-2605✅/RL-2609✅/GPIC✅/WebMix✅/InternVL-SA1B✅/wit_base✅/the_cauldron✅。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)/tmp49%(49G)。📦体积:TASK=32458B(32KB)/MEMORY=26706B(27KB)
> [18:12] 唤醒512：/tmp清理复核(唤醒511已完成,acf82d12已push)——du /tmp无data线残留(45G used/49G avail,与511收尾一致)。en_v1_4健康巡检:41410par/56461=73.3%/3.9T/0inc,wrapper PID606504(etimes=117262s≈32.5h)+hf PID3563885,lastfile18:13 CC-MAIN-2021-39(452par,正在下),+442par/~72min≈6.1par/min,ETA~15051par/6.1≈1.7天,健康✅。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32458B(32KB)/MEMORY=26KB
> [17:00] 唤醒511：执行运维令10-17「清理.12的/tmp」。盘点du /tmp:46G used/98G。识别6项data线旧残留(均app.e0031982所有、>1天未动、fuser确认无进程占用):mix_base_tok_l1_work(143M,10-08)+mix_base_tok_en_work(101M,10-08)+mix_base_tok_ultrax_work(100M,10-08)+mix_base_tok_zh_work(80M,10-07)+base_samples(250M,10-01,含en.parquet)+ablation_weight_ratio_cw1_plw2.log(47M,10-07)。rm -rf全部删除✅。df /tmp:46G→45G used/48G→49G avail(释放~718M)。🚫未动:vision线(R9/R8/r5/r6/r12/r11/lmms_eval/llava/clevr等)、pretrain线(test_lang_mcore/torchinductor/training_4h100/opt*等)、harness线(terminal-bench-repo)、infra(bun/bun-cache/ray/node等)、别用户文件(tmpiwctcvfn=app.t0002965/node.tar.gz=svc.e0027605)、<1天文件(docs_build 15h/mplwork 17h/armA_protb_feats 6h)。en_v1_4健康巡检:40968par/56461=72.5%/0inc,wrapper PID606504+hf PID3563885,lastfile16:59 CC-MAIN-2021-39 part-0008,活跃✅。85M⏸暂停(无进程)。TASK归档⏸暂停块→ARCHIVE(32590→32458B)。📦体积:TASK=32458B(32KB)/MEMORY=25KB
> [15:42] 唤醒510：健康巡检。SFT-2605✅(1504jsonl/0inc@/nas_inference),RL-2609✅(80files=20jsonl/0inc@/nas_env)。**WebMix-38M✅自然完成**(3886par/1.9T/0inc,retry-loop日志"COMPLETE attempt#1"@15:10:36,EXIT@15:10:38,落盘/nas_user,无进程=正常退出非崩溃)。en_v1_4(40498par/56461=71.7%/3.8T/0inc,wrapper PID606504+hf PID1790098/etimes=370s/CC-MAIN-2021-31 part-0047,活跃,+345par/~72min≈4.8par/min,ETA~2.3天)。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=25KB(无需归档)
> 📦 唤醒509 原文已归档 → daily-memories-data/2026-10-17.md（含复核运维令10-15(SFT-2605+RL-2609)+2路下载健康巡检+en_v1_4 40153/56461=71.1%+WebMix 3816par+85M⏸+disk 4盘+体积32KB/24KB）
> 📦 唤醒508 原文已归档 → daily-memories-data/2026-10-17.md（含复核运维令10-15(SFT-2605+RL-2609逐字节复核)+2路下载健康巡检+en_v1_4 39959/56461=70.8%+WebMix 3690par+85M⏸+disk 4盘+体积32KB/22KB）
> 📦 唤醒507 原文已归档 → daily-memories-data/2026-10-17.md（含复核运维令10-15(SFT-2605+RL-2609在盘逐字节复核)+2路下载健康巡检+en_v1_4 39774/56461=70.4%+WebMix 3558par+85M⏸+disk 4盘+体积32KB/22KB）
> [10:52] 唤醒506：复核运维令10-15(SFT-2605+RL-2609在盘验证)+2路下载健康巡检。SFT-2605✅(1504jsonl/298G/0inc@/nas_inference),RL-2609✅(20jsonl/187632280663B=174.75GiB/0inc/80files@/nas_env)。en_v1_4(39589par/56461=70.1%/3.7T/0inc,wrapper PID606504+hf PID1050608/etimes=4380s,lastfile10:52 CC-MAIN-2021-21/part-0165,活跃,+165par/~73min≈2.3par/min,ETA~5.1天),WebMix(3433par/1.6T/1inc,wrapper PID606513+hf PID607568/etimes~25h,lastfile10:52 yfcc15m-000010540001,活跃,+131par/~73min≈1.8par/min)。2路全健康无kill/restart。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=21103B(20KB,无需归档)
> [09:39] 唤醒505：复核运维令10-15(SFT-2605+RL-2609在盘验证)+2路下载健康巡检。SFT-2605✅(1504jsonl/318990252711B=297.08GiB/0inc@/nas_inference),RL-2609✅(20jsonl/187632277660B=174.75GiB/0inc/27files@/nas_env,26files=Code×12+Knowledge×2+Long_Context×2+Math×4+4meta+2assets+1gitattributes+1manifest)。en_v1_4(39424par/56461=69.9%/3.6T/0inc,wrapper PID606504+hf PID1050608/etimes=34s(刚为CC-MAIN-2021-21重启,ppid=606504),lastfile09:38 CC-MAIN-2021-17/part-0512,活跃,+162par/~75min≈2.2par/min,ETA~5.3天),WebMix(3302par/1.6T/1inc,wrapper PID606513+hf PID607568/etimes~24h,lastfile09:39 yfcc15m-000009240001,活跃,+118par/~75min≈1.6par/min)。2路全健康无kill/restart。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=20747B(20KB,无需归档)
> 📦 唤醒505 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39424/56461=69.9%/3.6T+WebMix 3302par/1.6T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒504 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39262/56461=69.5%/3.6T+WebMix 3184par/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒503 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39123/56461=69.3%/3.6T+WebMix 3061par/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒502 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38982/56461=69.1%/3.6T+WebMix 2936par/1.4T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒501 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38827/56461=68.8%/3.6T+WebMix 2809par/1.3T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒500 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38646/56461=68.4%/3.6T+WebMix 2686par/1.3T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒499 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38478/56461=68.1%/3.5T+WebMix 2556par/1.2T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒498 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38299/56461=67.8%/3.5T+WebMix 2434par/1.1T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒497 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38038/56461=67.3%/3.5T+WebMix 2270par/1.1T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒496 原文已归档 → `daily-memories-data/2026-10-16.md`（含2路下载健康巡检+en_v1_4 37705/56461=66.8%/3.4T+WebMix 2066par/1023G+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒495 原文已归档 → `daily-memories-data/2026-10-16.md`（含2路下载健康巡检+InternVL-SA1B✅完成确认+en_v1_4 37344/56461=66.1%+WebMix 1850par/976G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒494 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37230/56461=66.0%+WebMix 1761par/956G+InternVL 1923tar/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒493 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37124/56461=65.8%+WebMix 1669par/936G+InternVL 1849tar/1.4T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒492 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37028/56461=65.6%+WebMix 1591par/919G+InternVL 1771tar/1.3T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒491 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36918/56461=65.4%+WebMix 1501par/892G+InternVL 1700tar/1.3T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒490 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36820/56461=65.2%+WebMix 1420par/882G+InternVL 1624tar/1.2T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒489 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36710/56461=65.0%+WebMix 1330par/862G+InternVL 1559tar/1.2T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒488 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36614/56461=64.9%+WebMix 1250par/845G+InternVL 1496tar/1.1T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒487 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36513/56461=64.7%+WebMix 1164par/826G+InternVL 1423tar/1.1T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒486 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36421/56461=64.5%+WebMix 1089par/805G+InternVL 1352tar/1013G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒485 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载全部429假死→已重启+全3路PID已死+en_v1_4 36363/56461=64.4%+WebMix 1040par/769G+InternVL 1298tar/971G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒484 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36313/56461=64.3%+WebMix 1027par/759G+InternVL 1274tar/953G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒483 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36222/56461=64.2%+WebMix 976par/722G+InternVL 1226tar/917G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒482 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36031/56461=63.8%+WebMix 940par/696G+InternVL 1214tar/908G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒481 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35934/56461=63.6%+WebMix 901par+InternVL 1160tar+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒480 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35724/56461=63.3%+WebMix 879par+InternVL 1116tar+disk 4盘+体积32KB/14KB）
> 📦 唤醒479 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35271/56461=62.5%+WebMix 877par+InternVL 1114tar+RL-2609✅+disk 4盘+体积32KB/14KB）
> 📦 唤醒478 原文已归档 → `daily-memories-data/2026-10-16.md`（含RL-2609全程监控至20/20完成+自校26/26字节比对PASS+3路进度+disk 4盘+体积32KB/14KB）
> 📦 唤醒477 原文已归档 → `daily-memories-data/2026-10-16.md`（含巡检4路下载+RL-2609 8/20jsonl/119.4GB+part-09下载中+3路进度+disk 4盘+体积32KB/14KB）
> 📦 唤醒475 原文已归档 → `daily-memories-data/2026-10-15.md`（含验证SFT-2605通过+RL-2609四盘皆无→启动下载PID980464/980491+3路既有下载健康+disk 4盘+体积29KB/14KB）
> 📦 唤醒474 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 34951/56461=61.9%+WebMix 733par/542G+InternVL 992tar/741G+disk 4盘+体积29KB/14KB）
> 📦 唤醒473 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 wrapper重启hf+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒472 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 wrapper重启hf+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒471 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒470 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/17KB）
> 📦 唤醒469 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒468 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒467 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载+wit_base完成确认(330/330/287G,12:19自然退出)+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒466 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base仍在下载317parquet+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒465 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base wrapper自动重启hf确认+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒464 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒463 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒462 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒460 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/32KB）
> 📦 唤醒459 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒458 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒451-457 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+WebMix/wit_base速率趋零kill+restart+4路进度对比表+disk 4盘+体积29KB/30~31KB，详见各条目）
> 📦 唤醒444-450 原文已归档 → `daily-memories-data/2026-10-14.md` ~ `2026-10-15.md`（含恢复全部4路下载setsid启动+巡检+wrapper自动重启+en_v1_4 wrapper自动重启+4路进度对比表，详见各日文件）
> 📦 唤醒428-443 原文已归档 → `daily-memories-data/2026-10-14.md`（含第7~17次复核暂停态+进度表6路+.incomplete保留+disk 4盘，详见各日文件）
> 📦 唤醒427及更早（唤醒296-427）流水指针已归档 → `daily-memories-data/2026-10-10.md` ~ `2026-10-14.md`（含6路下载巡检全链+暂停/恢复+the_cauldron完成+GPIC完成+85M移交/暂停+en_v1_4进度29%~58%+4路图文对启动+R3分词+BO R2等，详见各日文件）


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