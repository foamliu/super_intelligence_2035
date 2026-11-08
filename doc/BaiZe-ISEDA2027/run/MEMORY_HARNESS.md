# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R1910 监控轮(gateway quota耗尽但predict仍产real·predict 1860/3500(53.1%)·real=775·TB-2.1 3DONE+4RUN·cc+1p·CPU/MEM PASS)
已完成:       H-B✅·Gate7/7·TB报告✅·full500✅·cline专项C1-C5+报告R1785-R1896·TB4 0passed(能力)·TB-2.1 oracle5/5✅·§15:2x判据MET✅·R1789 eval 7/7DONE✅·R1804双报告交付✅·R1814-R1909 predict推进+TB-2.1并行·R1909监控轮
当前动作:     R1910:①CPU/MEM PASS(load89/95/111·本线最高<1核·mem avail1.1Ti) ②体积:TASK=30KB(30306B)/MEMORY=31KB·均≤32KB✅ ③硬盘:/data 18%(5.8T)/ 4%(352G) ④gateway:quota耗尽(直接探针"等待2h")但predict仍产real patch(最近5文件全REAL)·TB-2.1例外率低(1/30min) ⑤predict 7路全alive 1860/3500(53.1%·real=775·+5sinceR1909):cline211(104r/107e=49.3%)·codex359(31r/328e=8.6%)·opencode266(210r/56e=78.9%best)·cc382(62r/320e=16.2%)·pi157(60r/97e=38.2%)·hermes358(237r/121e=66.2%)·dsh127(71r/56e=55.9%) ⑥TB-2.1:oracle5/5✅·3DONE(dsh21t/14p·codex13t/7p·hermes108t/5p)+4RUN alive(cline164t/11p·opencode76t/20p·cc66t/9p+1·pi85t/23p best=31.5%) ⑦报告R1896需更新(cc TB-2.1 8→9p)→下轮或满路后更新 ⑧research日报11-08已读·建议:0passed四分类(高)+TB-2.1报告补wall-clock/timeout列(中)+题目难度分归因基线(中) ⑨cline C4:real=104/empty=107/失败top1=empty_no_error(quota耗尽但real仍产) ⑩未完成指令:有(§22:4x+§10:10)⇒W:0
下一步:       ①监控predict 7路→每路达500 ②TB-2.1:4路running(cline164t/opencode76t/cc66t/pi85t)待完成→汇总best→更新报告(cc+1p需更新) ③待predict满后增量更新报告+重跑eval ④research日报建议纳入:0passed四分类(高)+TB-2.1报告补wall-clock/timeout列+题目难度分归因基线(中优先)
阻塞:         无(gateway quota耗尽但predict仍产real·TB-2.1例外率低·进程全alive)
ERROR_COUNT:  0
  📦 体积：TASK=30KB(30306B) / MEMORY=31KB（均≤32KB✅·R1864-R1909已归档→daily-memories-harness/2026-11-08.md）
  🔍 cline专项小结: predict cline211(104r/107e=49.3%·quota耗尽但real仍产)·R1789 eval cline35/46=76.1% 0 empty_patch(C3✅)·TB-2.1 cline 11p(164trials·run2 still running)·C2最近empty全为empty_no_error(quota耗尽非能力)·复算:python3 -c"import json,glob;f=glob.glob('swebench_verified_full/predictions_glm53/cline-patched__*.json');r=sum(1 for x in f if (lambda d:(d[0] if isinstance(d,list) else d).get('model_patch','').strip())(json.load(open(x))));print(f'real={r} empty={len(f)-r}')"
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水

> [18:23] R1910 监控轮(gateway quota耗尽但predict仍产real·predict 1860/3500(53.1%)·real=775·TB-2.1 3DONE+4RUN·cc+1p·CPU/MEM PASS):①CPU/MEM PASS(load89/95/111·本线最高<1核·mem avail1.1Ti) ②体积:TASK=30KB/MEMORY=31KB✅ ③硬盘:/data 18%(5.8T)/ 4%(352G) ④gateway:quota耗尽(直接探针"等待2h2m")但predict仍产real patch(最近5文件全REAL·TB-2.1例外率低1/30min) ⑤predict 7路全alive 1860/3500(real=775·+5sinceR1909):cline211(104r/107e=49.3%)·codex359(31r/328e=8.6%)·opencode266(210r/56e=78.9%best)·cc382(62r/320e=16.2%)·pi157(60r/97e=38.2%)·hermes358(237r/121e=66.2%)·dsh127(71r/56e=55.9%) ⑥TB-2.1(oracle5/5✅):3DONE(dsh21t/14p·codex13t/7p·hermes108t/5p)+4RUN alive(cline164t/11p·opencode76t/20p·cc66t/9p+1sinceR1909·pi85t/23p best=31.5%) ⑦报告R1896需更新(cc 8→9p)→下轮或满路后更新 ⑧research日报11-08已读·建议:0passed四分类(高·来自research日报2026-11-08)+TB-2.1报告补wall-clock/timeout列(中)+题目难度分归因基线(中) ⑨cline C4:real=104/empty=107/失败top1=empty_no_error(quota耗尽但real仍产·非能力问题) ⑩归因:quota耗尽=infra(直接探针blocked但proxy路径仍通)·TB4全0=能力·TB-2.1 pass=能力·pi TB-2.1 23p/85t=27.1%(verifier_runs73/23p=31.5%best among 4RUN) ⑪未完成指令:有(§22:4x+§10:10)⇒W:0

> 📦 R1909 流水(18:15,监控轮·gateway 200·predict 1855/3500·real=770·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1908 流水(18:10,监控轮·gateway 200·predict 1848/3500·real=764·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1907 流水(18:01,监控轮·gateway 200·predict 1835/3500·real=754·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1906 流水(17:51,监控轮·gateway 200·predict 1825/3500·real=744·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1905 流水(17:38,监控轮·gateway 200·predict 1813/3500·real=739·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1904 流水(17:30,监控轮·gateway 200·predict 1803/3500·real=731·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1903 流水(17:23,监控轮·gateway 200·predict 1794/3500·real=723·TB-2.1 3DONE+4RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1902 流水(17:14,监控轮·gateway alive·predict 1788/3500·real=717·TB-2.1 7路全RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1901 流水(17:07,监控轮·gateway 200·predict 1786/3500·real=715·TB-2.1 2DONE+5RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1900 流水(16:58,监控轮·gateway 200·predict 1785/3500·TB-2.1 2DONE+5RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1899 流水(16:51,监控轮·gateway 200·predict 1778/3500·TB-2.1 2DONE+5RUN·CPU/MEM PASS)已归档 → daily-memories-harness/2026-11-08.md。

> 📦 R1893-R1897 流水(15:35~16:30,监控+报告轮·gateway 429→200恢复·TB-2.1 3DONE+5RUN·predict推进至1760/3500·三报告R1896更新)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429→200恢复·predict 50.3%·real=693·TB-2.1 cline7p/codex4p(84err)/hermes3p DONE+5路RUN·codex TB-2.1 84err=适配器级(config.toml wire_api=responses→CLI启动即退出)。需要时再读。

> 📦 R1892 流水(15:18,监控轮,gateway 429,predict 1640/3500,real冻结662,TB-2.1 3DONE+4RUN)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429持续·predict 46.9%·real冻结662=429铁证·TB-2.1 codex DONE@15:03(84err=429)。需要时再读。

> 📦 R1891 流水(15:10,监控轮,gateway 429,predict 1630/3500,TB-2.1 786result/69passed,hermes完成全部89题非死)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 46.6%·TB-2.1 69p·hermes 89/89DONE(5p)·codex predict alive。需要时再读。

> 📦 R1890 流水(14:55,监控轮,gateway 429,predict 1614/3500,TB-2.1 746result/69passed,hermes误判死实为88/89接近完成)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 46.1%·TB-2.1 69p·R1890监控轮(hermes状态误判已R1891修正=完成全部89题非死)。需要时再读。

> 📦 R1889 流水(14:44,监控轮,gateway 429,predict 1603/3500,TB-2.1 763result/78passed(计数误差已修正为746/69))已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 45.8%·TB-2.1 69p(修正)·R1889监控轮。需要时再读。

> 📦 R1888 流水(14:38,监控轮,gateway 429,predict 1591/3500,TB-2.1 721result/69passed)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 45.5%·TB-2.1 69p·R1888监控轮。需要时再读。

> 📦 R1886 流水(14:22,监控+三报告刷新,gateway 429,predict 1576/3500,TB-2.1 272s/62p,三报告R1886)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 45.0%·TB-2.1 62p·三报告R1886交付。需要时再读。

> 📦 R1885 流水(14:12,监控+三报告刷新,gateway 429,predict 1561/3500,TB-2.1 271s/62p,三报告R1885)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 44.6%·TB-2.1 62p·三报告R1885交付。需要时再读。
> 📦 R1884 流水(14:05,监控+三报告刷新,gateway 429,predict 1548/3500,TB-2.1 271s/62p,三报告R1884)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 44.2%·TB-2.1 62p·三报告R1884交付。需要时再读。
> 📦 R1883 流水(13:44,监控+三报告刷新,gateway 429,predict 1529/3500,TB-2.1 322s/69p,三报告R1883)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 43.7%·TB-2.1 69p·三报告R1883交付。需要时再读。
> 📦 R1882 流水(13:35,监控+三报告刷新,gateway 429,predict 1518/3500,TB-2.1 314s/69p,三报告R1882)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 43.4%·TB-2.1 69p·三报告R1882交付。需要时再读。
> 📦 R1881 流水(13:20,监控+三报告刷新,gateway 429,predict 1502/3500,TB-2.1 305s/69p,三报告R1881)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 42.9%·TB-2.1 69p·三报告R1881交付。需要时再读。
> 📦 R1880 流水(13:15,监控+报告刷新,gateway 429,predict 1490/3500,TB-2.1 298s/69p,双报告R1880)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 42.6%·TB-2.1 69p·双报告R1880交付。需要时再读。
> 📦 R1879 流水(12:53,监控+codex predict重启+报告刷新,gateway 429,predict 1475/3500,TB-2.1 291s/69p,2DONE+5run)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 429·predict 42.1%·TB-2.1 69p·codex predict重启恢复。需要时再读。
> 📦 R1878 流水(12:42,监控+报告刷新,gateway 200/429间歇,predict 1472/3500,TB-2.1 290s/69p,2DONE+5run)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 200/429间歇·predict 42.1%·TB-2.1 69p·cline C2:429=0/能力=80。需要时再读。
> 📦 R1877 流水(12:35,监控+报告刷新,gateway 200,predict 1463/3500,TB-2.1 537s/464u/64p,2DONE+5run)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 200·predict 41.8%·TB-2.1 64p·cline C2:429=0/能力=80。需要时再读。

> 📦 R1864-R1874 流水(10:15~12:02,11轮监控+报告刷新,gateway 200稳定,predict 1316→1440/3500,TB-2.1 32→55p,3路DONE+4路running)已归档 → daily-memories-harness/2026-11-08.md。结论：gateway 200持续·predict 41.1%·TB-2.1 55p(3DONE+4run)·cline C2:429=0/能力=全empty=能力铁证。需要时再读。

> 📦 R1855-R1861 流水(08:05~09:31,5轮:cline专项R1855-R1857+research日报建议落地+gateway 429→200监控+predict 1144→1238+TB-2.1 198→371/32p)已归档 → daily-memories-harness/2026-11-08.md。**关键**:R1789 eval 7/7 ALL 0 empty_patch(C3✅确认)·gateway 429持续~3.3h后09:33恢复·research 2611.08285+2611.08417建议落地(难度分+超时列+13易题分析+TB维护债标注)·TB-2.1 cline90/7p DONE。需要时再读。


> [07:55] R1854 监控+cline专项R1854(predict 1087/3500(31.1%)·TB-2.1 198scored/32pass(16.2%)·gateway 200OK·CPU/MEM PASS):①CPU/MEM PASS(load115/224·无本线失控>80核·top=pretrain llama-server非本线) ②体积:TASK=30KB/MEMORY=26KB·均≤32KB✅ ③硬盘:/data 18%·/ 4% ④**gateway 200OK**(v1/models=200+9092=200+9093=200) ⑤**predict 7路alive**1087/3500(31.1%):cline124(71r·57.3%·rec10=80%✅)·opencode184(159r·86.4%·rec10=90%·best)·hermes228(164r·71.9%·rec10=50%⚠)·dsh84(56r·66.7%·rec10=80%)·cc208(45r·21.7%·rec10=20%⚠⚠恶化)·pi84(39r·46.4%·rec10=20%⚠)·codex175(16r·9.2%·rec10=20%) ⑥**TB-2.1**:cline88/7p DONE·hermes54/3p(STALLED 281min·36无reward=Docker down期infra)·opencode14/5p·pi23/6p·codex7/3p·cc5/3p·dsh7/5p·合计198s/32p(16.2%)·5ALIVE+1DONE+1STALLED ⑦**报告✅**:cline专项R1854(8.3KB·C1-C5+cc升级警报+hermes STALLED) ⑧Docker运行中(5容器active) ⑨归因:429=infra(已解)·TB4全0=能力·cc rec10恶化=适配器疑似(网关200OK)·hermes 36无reward=Docker down(infra) ⑩未完成指令:有(§22:4x+§10:10)⇒W:0

> [07:45] R1853 监控+cline专项R1853(predict 1070/3500(30.6%)·TB-2.1 2DONE+5running(197scored/32pass=16.2%)·gateway 200OK·CPU/MEM PASS):①CPU/MEM PASS(load115/224=51%·无本线失控>80核·top=pretrain llama-server非本线·mem785G/avail1100G) ②体积:TASK=30KB(30306B)/MEMORY=31KB(归档R1849-R1850)·均≤32KB✅ ③硬盘:/data 18%·/ 4% ④**gateway 200OK**(v1/models=200+9092=200+9093=200) ⑤**predict 7路alive**1070/3500(30.6%):cline123(70r/53e=56.9%·rec10=80%✅)·codex171(16r/155e=9.4%)·opencode183(159r=86.9%·best)·cc200(45r/155e=22.5%)·pi84(39r/45e=46.4%·rec10=20%⚠)·hermes226(164r=72.6%)·dsh83(55r=66.3%) ⑥**TB-2.1**:cline88s/7p DONE·hermes54s/3p DONE(36无reward)·opencode13s/5p·pi23s/6p·codex7s/3p·cc5s/3p·dsh7s/5p·合计197s/32p(16.2%) ⑦**报告✅**:cline专项R1853(8.1KB·C1:7路real/empty+recent10+C2:4类失败分类(网关200OK)+C3:resume fix✅rec10=80%+C4心跳+C5:pi+cc警报+TB-2.1全7路快照) ⑧归因:429=infra(已解·历史遗留)·TB4全0=能力·codex 9.4%=能力循环·pi rec10=20%⚠(无429⇒疑似能力/超时)·cc 77.5%empty⚠需排查 ⑨未完成指令:有(§22:4x+§10:10)⇒W:0

> [07:20] R1852 监控+cline专项R1852+TB-2.1报告R1852更新(predict 1060/3500(30.3%)·TB-2.1 194/623scored/29pass·gateway 200OK·CPU/MEM PASS):①CPU/MEM PASS(load68/224=30%·top=pretrain非本线·mem773G/avail1112G) ②体积:TASK=30KB/MEMORY=30KB·均≤32KB✅ ③**gateway 200OK**(v1/models=200+9092=200+9093=200) ④**predict 7路alive**1060/3500(30.3%):cline123(70r/56%·rec10=80%✅)·codex171(16r/9%)·opencode179(155r/86%)·cc199(44r/22%)·pi82(38r/46%·rec10=10%⚠)·hermes224(163r/72%)·dsh82(54r/65%) ⑤**TB-2.1**:cline88s/7p DONE·hermes54s/3p DONE(35err)·opencode13s/5p·pi23s/6p·codex6s/2p·cc5s/3p·dsh5s/3p·合计194s/29p(14.9%) ⑥**报告✅**:cline专项R1852(6.3KB·C1:7路real/empty统计+C2:5类失败分类+C3:resume fix验证rec10=80%+C4心跳+C5差距来源含pi警报)+TB-2.1报告R1852(更新§2快照+合计194/29p) ⑦归因:429=infra(已解)·TB4全0=能力·codex 9%=能力循环·pi rec10=10%⚠需排查 ⑧未完成指令:有(§22:4x+§10:10)⇒W:0

> [07:08] R1851 监控+TB-2.1报告R1851更新(predict 1040/3500(29.7%)·TB-2.1 2路DONE+5路running·gateway 200OK·CPU/MEM PASS):①CPU/MEM PASS(load75/224=34%·无本线失控>80核·top=pretrain llama-server 696%非本线·mem770G/avail1113G) ②体积:TASK=30KB(30306B)/MEMORY=29KB(29337B)·均≤32KB✅ ③硬盘:/data 18%·/ 4% ④**gateway 200OK**/v1/models=200+gw_proxy:9092=200✅ ⑤**SWE-bench predict 7路alive**1040/3500(29.7%):cline120(68r/52e=56.7%)·codex169(14r/155e=8.3%·recent5全empty=能力循环已诊断)·opencode172(148r=86%·best)·cc198(43r=21.8%)·pi81(38r=46.9%)·hermes219(160r=73.1%)·dsh81(54r=66.7%)·全7路alive(latest文件均<25min前) ⑥**TB-2.1 reward聚合✅**(修正parser·bare 0/1):cline89/88s/7p DONE✅·hermes89/54s/3p DONE·opencode24/13s/5p·pi18/17s/5p·codex13/6s/2p·cc11/3s/1p·dsh16/4s/3p·合计260/185s/26p(14.1%) ⑦**TB-2.1报告R1851已更新✅**(report_harness_tb21_7way_zh.html·11KB·含§0切换判据[TB4 0p=能力⇒切换]·§1oracle5/5·§2 7路快照·§3归因红线·§4不可比说明·时间预算声明[research 2611.08417]·single-run标注[2611.08285]) ⑧归因:429=infra(已解)·TB4全0=能力·TB-2.1 cline7/hermes3=能力·codex 8.3%=模型重复循环(能力) ⑨未完成指令:有(§22:4x predict未满500+TB-2.1 5路未完+§10:10)⇒W:0

> 📦 R1846-R1850 流水(06:05~06:59,监控轮+codex根因诊断+research日报+TB-2.1 reward提取)已归档 → daily-memories-harness/2026-11-08.md。结论：research日报2篇(TB-2.1审计+失败归因)·codex 8.3%real=glm53重复循环(能力)·3路auto-restarted·predict 991→1035/3500。需要时再读。
> [06:00] R1845 监控轮(全进程alive·无异常·gateway OK·progress稳步推进):①CPU/MEM PASS(load83/224=37%·无本线失控>80核·top=pretrain llama-server 710%非本线·mem781G/avail1104G) ②体积:TASK=30KB/MEMORY=27KB✅ ③硬盘OK ④**gateway OK**gateway_probe=GATEWAY_OK ⑤**SWE-bench predict 7路alive**986/3500(28.2%):real=485·empty=501(cline114/63r PID1160476·codex167/14r PID56035·opencode161/137r PID694674·cc191/40r PID3706273·pi79/37r PID613394·hermes200/146r PID539198·dsh74/48r PID1025117·全alive无zombie) ⑥eval 7/7 DONE✅ ⑦**TB-2.1**:cline89/7p DONE✅·hermes89/3p DONE(35no-reward)·opencode13/89 run(2.8h)·codex1/89 rerun(32min)·cc/pi/dsh 1/89 just started(10min·harbor PID332585/332586/332584·docker容器已起) ⑧报告R1820/R1839/glm53_7way current ⑨C1-C5✅ ⑩research日报11-07=informational ⑪未完成指令:有(§22:4x+§10:10)⇒W:0
> [05:52] R1844 监控+**TB-2.1 cc/dsh/pi 3路并行启动✅**(serial launcher卡在opencode·cc/dsh/pi排队13h未起·发现Docker权限问题(user在docker组但当前shell未激活)·sg docker解决·3路harbor已起PID332585cc/332584dsh/332586pi·Docker容器已创建·5路concurrent):①CPU/MEM PASS(load78/224=35%·mem787G/avail1098G) ②体积:TASK=30KB/MEMORY=26KB✅ ③硬盘OK ④gateway OK 9092/9093=200 ⑤**SWE-bench predict 978/3500**:real=479·empty=499(cline112/62r·codex167/14r·opencode158/134r·cc191/40r·pi78/37r·hermes199/145r·dsh73/47r) ⑥eval 7/7 DONE✅ ⑦**TB-2.1全7路ACTIVE**:cline88/7p DONE·hermes54/3p·opencode2/1p run(2.5h)·codex1/0p run(rerun)·cc/dsh/pi并行启动✅(sg docker) ⑧R1820/R1839 current ⑨C1-C5✅ ⑩research日报11-07:harness=Scientist World(informational) ⑪未完成指令:有⇒W:0
> [05:35] R1843 监控轮(gateway OK via gw_proxy·predict 967/3500=27.6% 469real·TB-2.1 cline88/7pass DONE·hermes90/54reward/3pass·opencode12/89 running·codex2/89 rerun·cc/dsh/pi queued):①CPU/MEM PASS(load82/224=37%·无本线失控>80核·top=pretrain llama-server非本线·mem788G/2015G·avail1097G) ②体积:TASK=30KB/MEMORY=25KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**gateway OK**gw_proxy 9092=200·9093=200(direct probe 401=需key正常) ⑤**SWE-bench predict 7路alive**967/3500:real=469·empty=498(cline112/62r·codex166/14r·opencode154/130r·cc190/39r·pi78/37r·hermes196/142r·dsh71/45r·etimes~20h·slow progressing) ⑥**SWE-bench eval 7/7 DONE✅** ⑦**TB-2.1**:oracle5/5✅·cline88/7pass DONE✅·hermes90/54reward/3pass(35 no-reward=errored)·opencode12/89 running(latest break-filter-js exit code1=env fail non-429)·codex2/89 rerun alive(400s)·cc/dsh/pi queued(launcher PID2141834 alive 48303s=13.4h) ⑧报告R1820/R1839仍current ⑨cline专项C1-C5✅ ⑩归因:429=infra(已解)·TB4全0=能力·cline7/hermes3=能力 ⑪research日报11-08 06:00未发 ⑫未完成指令:有(§22:4x+§10:10)⇒W:0

> 📦 R1836-R1842 流水(04:30~05:29,网关429→恢复·codex rerun启动·predict 871→959files·TB-2.1 cline/hermes DONE)已归档 → daily-memories-harness/2026-11-08.md。结论：网关429 05:26恢复后predict复产real·codex TB-2.1 rerun PID2853985启动·cc/dsh/pi 3路并行启动(sg docker)。需要时再读。

> [04:20] R1835 监控轮(网关429持续ETA~05:25·predict 854files/3500·TB-2.1 cline/hermes DONE·opencode 6tasks running(429·0reward)·codex FAILED需重跑·cc/dsh/pi queued·进程均alive):①CPU/MEM PASS(load82/224=37%·top=llama-server pretrain eval非本线·无失控>80核·无proc>8000%·mem786G/2015G·avail1100G) ②体积:TASK=30KB(30306B)/MEMORY=17KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429持续**curl real key→「等待1小时4分钟23秒后重试」ETA~05:25 ⑤gw_proxy 9092=200✅·9093=200✅(proxy健康·上游429) ⑥**SWE-bench eval 7/7 DONE✅**不变 ⑦**predict 7路alive但429烧空patch**file counts:cline99/codex138/opencode146/cc157/pi70/hermes181/dsh63=854total ⑧**TB-2.1**:oracle5/5✅·cline88reward(7pass=7.9%)DONE·hermes54reward(3pass·35errored=429)DONE·opencode 6tasks started(429·0reward·build-pov-ray当前task)·codex FAILED(trace=Docker daemon not running·docker now up·需重跑)·cc/dsh/pi queued·launcher PID2141831 alive(43816s)·dockerd alive ⑨报告R1820仍current(real未变) ⑩cline专项C1-C5✅ ⑪归因红线:429=infra·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑫research日报11-07已读(harness建议=可执行环境verifier对照·已通过TB4→TB-2.1切换解决) ⑬未完成指令:有(§22:4x+§15:2x+§10:10)⇒W:0


> [04:12] R1834 监控轮(网关429持续ETA~05:25·predict1618/3500(+797全empty/quota·429快速退出烧patch)·real冻结458·TB-2.1 cline/hermes DONE·opencode 5tasks running(429·0reward)·codex 20tasks无reward(docker down·需重跑)·launcher+dockerd均alive):①CPU/MEM PASS(load67/224=30%·无失控>80核·无proc>8000%·mem789G/2015G·avail1.1T) ②体积:TASK=30KB(30306B)/MEMORY=16KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429持续**curl real key→「请等待1小时16分钟37秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429烧空patch**total1618/3500(+797sinceR1833·**real冻结458(+0)**=infra铁证):cline177(62r·3quota·112nopatch)·codex366(14r·345quota!·7nopatch)·opencode185(127r·2quota·56nopatch)·cc363(38r·5quota·320nopatch)·pi135(37r·77quota·21nopatch)·hermes277(138r·110quota·29nopatch)·dsh115(42r·1quota·65nopatch·7timeout) ⑦**TB-2.1**:cline88(7pass=7.9%)DONE·hermes54(3pass=3.4%)DONE·opencode 5tasks running(PID1468883 alive·429·0reward)·codex20tasks无reward(docker down时跑·需重跑)·cc/dsh/pi queued·launcher PID2141831 alive·dockerd PID1480217 alive·oracle5/5✅ ⑧报告R1820仍current ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪未完成指令:有(§22:4x+§15:2x+§10:10)⇒W:0

> [04:03] R1833 监控轮(网关429持续ETA~05:25·predict821/3500(+13全empty)·real冻结459·TB-2.1 cline/hermes DONE·opencode harbor alive 48min 0reward(429·docker内npm install)·codex 0done(docker down时跳过需重跑)·launcher+dockerd均alive):①CPU/MEM PASS(load68/224=30%·无失控>80核·无proc>8000%·mem785G/2015G·avail1101G) ②体积:TASK=30KB(30306B)/MEMORY=14KB(14552B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429持续**curl chat/completions→「请等待1小时24分钟49秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total821/3500(+13sinceR1832·**real冻结459(+0)**):cline96·codex128·opencode144·cc147·pi67·hermes178·dsh61 ⑦**TB-2.1**:cline88(7pass=7.9%)DONE·hermes54(3pass=3.4%)DONE·opencode harbor alive 48min 0reward(429)·codex0done(docker down·需重跑)·cc/dsh/pi queued·launcher PID2141831 alive·dockerd PID1480217已恢复·oracle5/5✅ ⑧报告R1820仍current ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪research日报11-07已读(harness建议=2611.08478·TB4已弃仅备查) ⑫未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> [03:52] R1832 监控轮(网关429确认ETA~05:25·predict808/3500·real冻结459·TB-2.1 cline/hermes DONE·opencode stuck 4tasks exception=429·codex需重跑·进程alive):①CPU/MEM PASS(load72.6/224=32%·无失控>80核·top=pretrain llama-server非本线·mem804G/2015G·avail1082G) ②体积:TASK=30KB(30306B)/MEMORY=13KB·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**curl real key→「请等待1小时33分钟23秒后重试」ETA~05:25 ⑤**SWE-bench eval 7/7 DONE✅**不变:cline35/46(76.1%)·codex6/8·opencode80/102(78.4%)·cc27/36·pi26/34·hermes124/131(94.7%)·dsh33/40(82.5%) ⑥**predict 7路alive但429受阻**total808/3500(+21sinceR1831·**real冻结459(+0)**=infra铁证):cline95(62r·33e·65.3%)·codex124(14r·110e·11.3%)·opencode143(127r·16e·88.8%)·cc143(38r·105e·26.6%)·pi66(37r·29e·56.1%)·hermes177(138r·39e·78.0%)·dsh60(43r·17e·71.7%) ⑦**TB-2.1**:cline88reward(7pass=7.9%)DONE·hermes54reward(3pass=3.4%·35errored=429)DONE·opencode stuck(4tasks started·all exception code1=429·0reward)·codex0done(需重跑)·3路queued(cc/dsh/pi)·oracle5/5✅ ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证)·TB4全0=能力·TB-2.1 cline7pass/hermes3pass=能力 ⑪未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> [03:40] R1831 监控轮(网关429确认ETA~05:24·predict787/3500·real冻结459·TB-2.1 cline/hermes DONE·codex需重跑·进程alive):①CPU/MEM PASS(load66.7/224=30%·无失控>80核·top=pretrain llama-server非本线·mem799G/2015G) ②体积:TASK=30KB(30306B)/MEMORY=12KB(12172B)·均≤32KB✅ ③硬盘:/data 5.8T(18%)·/ 352G(4%) ④**网关429确认**curl chat/completions→「本次Token额度已用完，请等待1小时43分钟51秒后重试」ETA~05:24 ⑤**SWE-bench eval 7/7 DONE✅**不变 ⑥**predict 7路alive但429受阻**total787/3500(+11sinceR1830·**real冻结459(+0)**=infra铁证):cline92(62r·30e)·codex118(14r·104e)·opencode142(127r·15e)·cc137(38r·99e)·pi65(37r·28e)·hermes174(138r·36e)·dsh59(43r·16e) ⑦**TB-2.1**:cline88reward(7pass=7.9%)DONE·hermes54reward(3pass=3.4%·35errored=429)DONE·codex0done(429blocked·73jobfiles/0reward·**需手动重跑**)·opencode running 0done(429)·3路queued(cc/dsh/pi)·oracle5/5✅ ⑧报告R1820仍current(real未变) ⑨cline专项C1-C5✅ ⑩归因红线:429=infra(real+0=铁证) ⑪research日报11-07已读(harness建议=TB4 verifier+trace记录法·TB4已弃故仅备查) ⑫未完成指令:有(§22:4x+§15:2x+§10:10)⇒WAITING:0

> 📦 R1829-R1830 流水(03:19~03:35,监控轮+网关429 ETA~05:27+predict 752→776/3500·real冻结459=infra铁证+TB-2.1 hermes89/89DONE)已归档 → daily-memories-harness/2026-11-08.md。结论：429=infra(real+0铁证)·TB-2.1 hermes 3pass·cline 7pass。需要时再读。
> 📦 R1817-R1828 流水(01:07~03:09,~12轮监控+网关429反复+predict 549→752/3500+TB-2.1 hermes 62→89/89DONE(3pass)+双报告R1817-R1822更新+research日报11-07已读)已归档 → daily-memories-harness/2026-11-08.md。**关键里程碑**:hermes TB-2.1 89/89DONE(3pass=3.4%·mean=0.0337·36errored)·predict real冻结459(429全程)·三报告R1820交付(cline_special+glm53_7way+tb21_7way)。需要时再读。

> 📦 R1811-R1816 流水(23:58~00:55,监控轮+deepseek eval完成+TB-2.1 cline89/89+hermes推进+网关429滚动+双报告多次更新)已归档 → daily-memories-harness/2026-11-08.md。**关键里程碑**:deepseek eval 33/40=82.5%(SWE-bench eval 7/7全done)·TB-2.1 cline89/89DONE(7pass=7.9%)·hermes 22→49/89(2pass→0pass)·网关429→200→429滚动·predict 530→542/3500。需要时再读。

> 📦 R1788-R1811 流水(19:33~23:58,监控轮+deepseek eval启动→完成+TB-2.1 cline89/89+hermes推进+网关429反复+双报告多次更新)已归档 → daily-memories-harness/2026-11-07.md。**关键里程碑**:deepseek eval 33/40=82.5%完成(SWE-bench eval 7/7全done)·TB-2.1 cline 89/89 DONE 7pass=7.9%·hermes 22→32/89·网关429反复(keyB额度耗尽)·§15:2x判据MET✅。需要时再读。
> 📦 R1761-R1787 流水(13:50~19:18,监控轮+cline专项报告R1761-R1763+网关429恢复+TB-2.1 cline 3→5passed+predict全量推进)已归档 → daily-memories-harness/2026-11-07.md。结论：网关429恢复后cline复产real patch·空patch归零·TB-2.1 5/68passed=7.35%·SWE-bench predict cline/codex/opencode达500。需要时再读。
> 📦 R1750-R1755 流水(13:07~13:35,cline专项统计+C3验证+报告R1747)已归档 → daily-memories-harness/2026-11-07.md。结论：cline空patch=100%infra(429额度)·C3 resume fix生效·适配器正常时27/27=100%real。需要时再读。
> 📦 R1743-R1749 流水(12:15~13:12,cline专项C2修正+SDK崩溃分类+429额度ETA+报告R1743-R1747)已归档 → daily-memories-harness/2026-11-07.md。结论：TB4全0=能力(verifier已运行·reward=0非None)·cline空patch=100%infra(429额度65%+SDK崩溃25%+连接6%)·适配器正常时cline 27/27=100%real·resume fix生效(R1744)·报告R1743-R1747交付。需要时再读。
> 📦 R1739-R1740 流水(09:33~10:53,predict重启+exit-code修复+cline专项)已归档 → daily-memories-harness/2026-11-07.md。结论：killed 7旧predict后gateway恢复·cleanup 423空patch·resume fix生效·exit-code修复(cline_patched.py:201)·TB4 rerun2启动。需要时再读。
> 📦 R1738 流水(09:08,监控轮)已归档 → daily-memories-harness/2026-11-07.md。结论：gateway耗尽ETA09:20·cleanup dry-run=372空·TB4 hermes60reward全0=能力·运维预判overlay根因=错误。需要时再读。
> 📦 R1612-R1734 流水(2026-11-05~07,约50轮 incr_eval/监控/TB4启动/quiet轮)已 bulk 归档 → daily-memories-harness/2026-11-05/06/07.md。**关键里程碑**:cline rerun 356/500=71.3% · deepseek→212 · kimi全7路100% · TB4全量66×7启动 · R1685 cline低分归因(86%能力差) · R1695 proxy修复 · R1714-15 TB4 pip修复。需要时再读。

## 🗣️ 运维问答

> **Q1 (09:0x令): Terminal-Bench 一共多少题？**
> **A**: 89 题（全量）。`ls ~/terminal-bench/` = 89 个任务目录。之前 7×15 = 105 trials 是因本地只有 15 个镜像，**非任务集只有 15 题**。

> **Q2 (09:0x令): 为什么只有 15 题参与？**
> **A**: 本地只有 15 个 `alexgshaw/*:20251031` 镜像（Docker Hub pull 来的）。其余 74 个之前没拉成功——但**根因不是"MITM proxy blocks"**，而是当时 daemon.json proxies 可能还没配或 daemon 没重启。**现在 daemon.json 已配 172.19.92.25:13128，实测 docker pull 成功**。

> **Q3 (09:0x令): 能不能把剩下 74 个镜像拉下来？**
> **A**: **能！** 实测 `docker pull alexgshaw/circuit-fibsqrt:20251031` 成功（392MB）。已启动 `_pull_all_tb_images.sh`（PID 2611629）批量拉取 73 个缺失镜像。共享 base layer 已缓存，预计 ~1-2h 完成。/data 剩余 6.4TB，空间充足。

> **Q4 (09:0x令): 改成 7 并发？**
> **A**: **已完成！** R479 (16:21) 启动 7x89 并发：7 harnesses × 87 tasks = 609 trials, 7-way concurrent。每 harness 独立 jobs-dir 在 /tmp（避免 NFS stale handle），共享 gw_proxy (9090/9091)。v2 串行已 kill（部分结果已保存）。ETA ~2.5-3h。口径声明：7-way concurrent（与之前串行结果不可直接比）。

> **Q5 (09:2x令): 同事通过 92.25 代理成功拉过 Docker 镜像？**
> **A**: **确认！** daemon.json `proxies` 字段已配 `http://172.19.92.25:13128`，Docker 27.5.1 支持。实测 pull 成功。**无需额外配 systemd drop-in**（daemon.json proxies 已足够）。

> 📦 R113-R202 (2026-10-04~09, 早期 SWE-bench 横评 + SWEBENCH_COMPARE 监控 + 7-way harness 横评) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-09.md。需要时再读。

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 R35-R112 (2026-10-02~04, H-B 源码分析启动 + SWE-bench 可行性核查) 已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-04.md。需要时再读。最新流水见上方「本唤醒流水」。
