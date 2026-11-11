# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2179 incr_eval DONE(+10resolved→total1419:codex69/opencode392/hermes356/pi143)+双报告REGEN R2179+CPU/MEM/disk PASS+gateway functional
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2178·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2178 incr_eval+监控+报告+restart stalled routes·R2179 incr_eval DONE(11ids·+10resolved→total1419)+双报告REGEN R2179
当前动作:     R2179: 自检PASS(CPU无harness>8000%·最高cline15.7%/run_single~1核·非本线llama-server366%/pretrain145%不碰·MEM全<6GB·cline hub daemon5.7GB)+gateway functional(agi-gateway/models=200 0.018s·gw_proxy9092/9093=200·agents产新patch=活)+incr_eval R2179 DONE(11ids evald·+10resolved:codex+2→69/opencode+5→392/claude-code+0+1fail→162/pi+1→143/hermes+2→356→total1419)+6/7 ALIVE(cline240r226e14/codex137r101e36/opencode489r481e8/cc232r207e25/pi204r194e10/hermes409r398e11/dsh176r175e1 DEAD)+predict advancing(real1782/3500=50.9%)+cline C4(240f/226r/167res/58fail/14empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2179(7way 10099B/cline special 7658B)·W:0
下一步:       ①本轮commit MEMORY+push ②predict向500推进(6路alive·opencode489近500·cline240/codex137远) ③新real-patch累积后启动incr_eval ④各路满500后§22:4x两基准7路全交付 ⑤dsh不重启(silent-exit确定性·fix需dsh binary/SDK) ⑥research日报2026-11-11建议:报告加6列纳入下轮(2-3天·用现有trace回填不重跑) ⑦TB-2.1 opencode rerun推进
阻塞:         <各路尚未满500(1782real/3500=50.9%)·§22:4x未全交付·dsh silent-exit=dsh binary确定性bug(非crash·非gateway)·git pull阻塞(news线stale冲突文件非本线未碰·HEAD==origin/main已current)>
ERROR_COUNT:  0
 体积: TASK=21.1KB / MEMORY=26.5KB(均<32KB)
 cline专项小结: predict_glm53=240files/226real/167resolved/58failed/14empty(全429quota历史·infra非能力·非resume bug·C3 resume fix R1733仍有效)·C1:226real/240total(real/empty可复算:ls predictions_glm53/cline-patched__*.json|wc -l→240)·C2:58failed=100%能力差(1 infra-attributed)·C3:empty=14(429quota历史·非归零·归因红线区分)·C5:报告R2179 current(cline special 6598B·grep验证R2179)·失败top1=能力差(real patch但tests fail)

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [16:13] R2179: 自检PASS(CPU无harness>8000%·最高cline15.7%/run_single~1核·非本线llama-server366%/pretrain145%不碰·MEM全<6GB·cline hub daemon5.7GB)+gateway functional(agi-gateway/models=200 0.018s·gw_proxy9092/9093=200·agents产新patch=活)+incr_eval R2179 DONE(11ids evald·+10resolved:codex+2→69/opencode+5→392/claude-code+0+1fail→162/pi+1→143/hermes+2→356→total1419·setsid detach保活)+6/7 ALIVE(cline240r226e14/codex137r101e36/opencode489r481e8/cc232r207e25/pi204r194e10/hermes409r398e11/dsh176r175e1 DEAD)+predict advancing(real1782/3500=50.9%)+cline C4(240f/226r/167res/58fail/14empty·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+双报告REGEN R2179(7way 10099B/cline special 7658B)+dsh silent-exit确定性bug(不重启)+git pull阻塞(news线stale冲突非本线未碰·HEAD==origin/main已current·只提交本线文件)+体积TASK21.1KB/MEMORY27.0KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [15:47] R2178: 自检PASS(CPU无harness>8000%·eval容器~100%=1核·MEM全<500MB)+gateway 9092/9093/agi-gateway均HTTP200+incr_eval R2178 DONE(7ids全RESOLVED:cline pydata__xarray-3993 +1res→167/opencode django-12209/12262/12276/12406全res +4→387/hermes sklearn-10297/10844全res +2→354→total1409)+6/7 ALIVE(cline239r226e13/codex137r100e37/opencode487r476e11/cc230r206e24/pi203r195e8/hermes409r396e13/dsh176r175e1 DEAD)+predict advancing(real1779/3500=50.8%)+cline C4(239f/226r/167res/58fail/13empty·失败top1=能力差·xarray-3993本轮新增RESOLVED✅)+双报告REGEN R2178(7way 10098B/cline special 7658B·grep验证R2178)+dsh silent-exit确定性bug(不重启)+自检PASS(非本线llama-server/pretrain不碰)+体积TASK21.1KB/MEMORY25.8KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [15:06] R2177: 自检PASS(CPU无harness>8000%·MEM全<500MB)+gateway 9092/9093/agi-gateway均HTTP200+incr_eval R2177 DONE(2ids:cline pydata__xarray-3305+0res+1fail(能力)/hermes pytest-dev__pytest-8399+1res→352→total1402)+6/7 ALIVE(cline237r225e12/codex135r100e35/opencode479r472e7/cc225r206e19/pi202r194e8/hermes405r394e11/dsh176r175e1 DEAD)+predict advancing(real1766/3500=50.5%)+cline C4(237f/225r/166res/57fail/12empty·失败top1=能力差)+双报告REGEN R2177(7way 10097B/cline special 7658B·grep验证R2177)+research日报2026-11-11已读(建议=报告加6列·已纳入下轮2-3天)+dsh silent-exit确定性bug(不重启)+自检PASS(非本线pretrain144%不碰)+体积TASK21.1KB/MEMORY24.9KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0
> [14:50] R2176: 自检PASS(CPU无harness>8000%·MEM全<500MB)+gateway 9092/9093/agi-gateway均HTTP200+restart opencode predict(PID3728910·478/500· stalled since ~13:15·原因=process exited not crash)+restart claude-code predict(PID3837566·224/500·stalled since ~13:14)+incr_eval check(0 new real-patch unevaluated·全已evaluated→total1401resolved不变)+6/7 ALIVE(cline237r225e12/codex134r100e34/opencode478r470e8/cc224r204e20/pi201r193e8/hermes404r393e11/dsh176r163e13 DEAD)+cline C4(237f/225r/166res/57fail/12empty·失败top1=能力差)+CPU PASS(无harness>8000%·各run_single~1核·cline66%=0.7核)+MEM PASS(全<500MB)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报2026-11-11已读(harness建议=报告加6列·纳入下轮2-3天)+dsh silent-exit确定性bug(不重启)+自检PASS(非本线llama-server372%/pretrain144%不碰)+体积TASK21.1KB/MEMORY22.9KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0

> [14:33] R2175: incr_eval R2175 DONE+merged(14:32:58·5ids 4harness:cline1(xarray-3095)+1resolved/codex2(django-12039+1res·django-12050+1fail)/pi1(django-13023+0res+1fail)/hermes1(pytest-7982+1res)·+3resolved+2failed+0infra→total1401:cline166/codex67/opencode383/cc162/pi142/hermes351/dsh130)+双报告REGEN R2175(7way=10097B·cline special=7658B·grep验证R2175+1401resolved)+predict advancing(real1764/3500=50.4%:cline235r224e11/codex134r100e34/opencode478r472e6/cc224r206e18/pi201r194e7/hermes404r393e11/dsh176r175e1·4路alive:codex/cline/hermes/pi·opencode478近500·cc224停滞·dsh DEAD)+gw_proxy 9092 UP HTTP200/9093 UP HTTP200(predict走proxy正常·gateway_probe rc=000=agent无proxy非真实宕机)+CPU PASS(无harness>8000%·run_single各~1核·cline hub daemon 27%=0.3核)+MEM PASS(所有predict run_single<500MB·cline hub daemon 5.1GB=agent自身非predict)+磁盘(/data 5.8T 18%·/ 351G 4%)+dsh silent-exit确定性bug(不重启·fix需dsh binary/SDK)+自检PASS(内存/CPU红线均未触发·非本线llama-server375%/pretrain144%不碰)+体积TASK21.1KB/MEMORY22.7KB均<32KB·未完成指令:有(§10:10+§22:4x)·W:0


> [13:51] R2174: incr_eval R2174 LAUNCHED(21new:cline1(matplotlib-23314)/codex1(django-11999·R2173排除现已safe)/opencode2(cc2)/pi1/hermes2/dsh12(sympy·dsh DEAD但pred文件stable可eval)·setsid detached PID3809015·max_workers=3·13:51·全21ids确认非in-flight)·merge_R2174_glm53.py就绪(eval完自动merge)+gateway RECOVERED HTTP200(429 cleared·agi-gateway+gw_proxy9092均200→predict恢复产real patch·cline233→234files)+predict 6/7 ALIVE(cline234·codex130·opencode478·cc224·pi198·hermes400·dsh DEAD=完成500 real≈1759/3500=50.3%)+eval pre-R2174 total1395resolved(cline165/codex65/opencode383/cc162/pi142/hermes348/dsh130)+CPU PASS(matplotlib pytest124%=1.2核·load39/224·远低8000%阈值)+MEM PASS(773G/2Ti·1094G avail·/data 5.8T 18%)+gw_proxy 9092 UP HTTP200/9093 LISTEN+C4:cline 234f/224r/165res/57fail/10empty(全429quota·infra非能力·非resume bug·C3 resume fix R1733仍有效)+脚本incr_eval_R2174.sh+merge_R2174_glm53.py已commit·未完成指令:有(§10:10+§22:4x)·W:0
> [13:36] R2173 DONE: incr_eval R2173 DONE(1inst:claude-code sympy-20801 +1resolved→162·total1395↑1·13:35-13:36·codex django-11999 EXCLUDED in-flight re-predict)+双报告REGEN(R2173·7way=10094B·cline special=7657B·mtime13:36)+predict 6/7 ALIVE(cline233·codex130·opencode478·cc224·pi198·hermes400·dsh176 real≈1757/3500=50.2%)+gateway 429 QUOTA_EXHAUSTED(predict stalled·infra非能力·归因红线)+CPU PASS(load35/224·无harness进程>8000%)+MEM PASS(768G/2Ti·1090G avail·/data 5.8T 18%)+gw_proxy 9092 UP/9093 LISTEN+C4:cline 233f/223r/165res/57fail/10empty(全429quota·infra非能力·非resume bug·C3 resume fix R1733仍有效)·research日报2026-11-11(报告加6列·2-3天工作量·用现有trace回填)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [13:10] R2172 DONE: incr_eval R2171 DONE(5inst:cline+1→165/opencode+0fail→383/pi+1→142/hermes+1→348/dsh+1→130=4resolved·1failed·PID3387079 exited clean·total1394↑4·13:05-13:09)+双报告REGEN(R2172·7way=10088B·cline special=7610B·mtime13:09)+predict 6/7 ALIVE(cline223·codex97·opencode472·cc205·pi193·hermes390·dsh175 real=1755/3500=50.1%)+gateway 429 QUOTA_EXHAUSTED(wait~20min·predict stalled·infra非能力·归因红线)+CPU PASS(load32/224·无harness进程>8000%·pretrain144%=非本线不碰)+MEM PASS(768G/2Ti·1099G avail·/data 5.8T 18%)+gw_proxy 9092 UP/9093 LISTEN+C4:cline 223f/223r/165res/57fail/0empty(全real·cleanup有效·C3 empty归零)·research日报2026-11-11(报告加6列)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [12:47] R2171 DONE: incr_eval R2171 LAUNCHED+RUNNING(PID3387079 setsid-detached·5new:cline matplotlib-25287[heavy pytest test_axes.py in progress]+opencode sympy-18199+pi django-12708+hermes pytest-5631+dsh astropy-14598·cc sympy-20801 EXCLUDED in-flight PID970422)+deepseek silent-exit诊断(predict COMPLETED 500 at 10:38非crash·175real/325silent-exit=dsh binary rc=0~3s 0B·gate_predict_deepseek-harness.log证据·re-run won't help·fix需dsh binary/SDK·不重启)+cleanup 0removed+predict 6/7 ALIVE(cline223·codex97·opencode472·cc205·pi193·hermes390 real·dsh DEAD=完成500)+eval 1390resolved(pre-incr_eval)+1755real/3500target(50.1%)+gateway 429 QUOTA_EXHAUSTED(wait~47min·predict stalled·infra非能力·归因红线)+CPU PASS(load31/224·max eval pytest 893%=9核)+MEM PASS(764G/2Ti·/data 18%)+gw_proxy 9092 UP/9093 LISTEN+C4:cline 225f/223r/164res/57fail/2empty(429infra)·research日报2026-11-11(报告加6列)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [12:30] R2170 DONE: incr_eval R2168 DONE(PID4095939 exited·5路evald:cline221/164·codex97/65·opencode469/383·cc203/161·pi191/141·hermes389/347·dsh174/129·total=1390resolved↑7)+双报告REGEN(R2170·7way=9025B·cline special=6311B)+cleanup 0removed+predict 7/7 ALIVE(cline223·codex97·opencode472·cc205·pi192·hermes390·dsh175 real)但gateway 429 QUOTA_EXHAUSTED(wait~57min·predict stalled·infra非能力·归因红线)+CPU PASS(load32.77/224)+MEM PASS(767G/2Ti·/data 5.8T 18%)+gw_proxy 9092 UP/9093 LISTEN+C4:cline 224f/223r/164res/57fail/1empty(429 infra)·research日报2026-11-11建议(报告加6列continuous_score/workflow_calls/tokens/usd)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [12:25] R2169 DONE: incr_eval R2168 RUNNING(PID4095939·24min·cline+5res→164✅opencode+4res+1fail→383✅cc 5NEW eval in progress·pi/hermes/dsh pending)+双报告REGEN(R2169·10090B+7342B·mtime12:24·7way=1383total/cline164/opencode383/hermes345/cc156/pi141/dsh129/codex65·cline special)+predict 7/7 ALIVE(cline222·codex97·opencode467·cc200·pi190·hermes387·dsh174)+CPU PASS(load41/224)+MEM PASS(766G/2Ti·/data 5.8T 18%)+gw_proxy 9092 UP/9093 LISTEN(dsh alive·silent-exit=known hard fault·1 timeout astropy14182 32min)+C4:cline 222f/222r/164res/57fail/0empty·research日报2026-11-11建议(WorkflowArena:报告加6列)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [12:09] R2168 DONE: incr_eval LAUNCHED(setsid detached PID4095939·12:00:56·cline 217evald/222real/5NEW eval RUNNING·matplotlib-24627 test suite 重·~9min/instance·CPU PASS eval容器100%=1核·host load37/224)+cleanup 0empty+双报告REGEN(R2168·10090B+7342B·mtime12:09·7way=1374total/cline159/opencode379/hermes345·cline special)+predict 7/7 ALIVE(cline219·codex97·opencode464·cc198·pi189·hermes386·dsh174)+MEM PASS+gw_proxy 9092/9093 UP·C4:cline 222f/219r/159res/57fail/0empty·research日报2026-11-11建议(WorkflowArena:报告加6列continuous_score/workflow_calls/tokens/usd)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [11:43] R2167 DONE: incr_eval完成(9NEW eval:cline2→1res+1fail·opencode5→4res+1fail·cc1→1res·hermes1→0res+1fail=+5resolved 1369→1374·11:36→11:42·6min)+cleanup 4empty(cc2/pi2)+deepseek predict RESTARTED(PID2093585·gw_proxy_dsh 9093 UP HTTP200·dsh adapter silent-exit patch=0 known hard fault)+predict 7/7 ALIVE(首次全活)+CPU PASS(swebench 0.5核)+MEM PASS(763G/2Ti·/data 5.8T 18%)+双报告REGEN(R2167·10092B+7344B·mtime11:43·7way=1374/cline159/opencode379/hermes345·cline special)·gw_proxy 9092/9093 UP·C4:cline 219f/219r/159res/57fail/0empty·research日报2026-11-11建议(报告加6列continuous_score/workflow_calls/tokens/usd)已纳入下轮·未完成指令:有(§10:10+§22:4x)·W:0

> [10:52] R2166 DONE: incr_eval完成(12NEW eval:cline4→+3res+1infra·codex1→+1res·opencode6→+6res·cc1→+1res·pi4→+4res·hermes1→+1res=+16resolved 1353→1369·10:29→10:51·22min)+cleanup 9empty(cc5/cline1/codex1/hermes2)+双报告REGEN(R2166·7way=1369/cline158/opencode376/hermes345·cline special)·CPU PASS(pytest 1.1核)·MEM PASS·predict 6/7 ALIVE(dsh DEAD)·gw_proxy 9092/9093 UP·C4:cline 215f/215r/158res/56fail/1infra/0empty·未完成指令:有(§10:10+§22:4x)·W:0

> 📦 [09:51] R2165 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+cleanup 4empty+双报告REGENERATED(R2165)。需要时再读。

> 📦 [09:31] R2164 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+0empty(无需cleanup)+双报告REGENERATED(R2164)。需要时再读。

> 📦 [09:14] R2163 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 9NEW(+6resolved→1353)+cleanup 4empty+stuck R2142 container清理+双报告REGENERATED(R2163)。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 [06:55] R2152 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA持续+predict 1673real不变+cleanup 14empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 82/89done。需要时再读。

> [05:48] R2147: incr_eval轮·①CPU PASS(load35/224·无harness>8000%·最高pcpu=27.4%=cline-hub-daemon非eval) ②MEM PASS(759G/2Ti·1109G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict stalled) ④predict 7路ALIVE:cline-patched223·codex147·opencode453·cc243·pi187·hermes401·dsh176=1830files(+5) ⑤incr_eval R2147 DONE:hermes+1→343/381·opencode+1→365/446·eval 1340resolved(↑2) ⑥TB-2.1 opencode rerun ALIVE(105done/35pass/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=指令/配置/证据审计(已被R1739代际审计覆盖) ⑧cline C4:223f/206r/153res/53fail/17empty(↑3empty=429quota) ⑨双报告REGEN R2147(glm53_7way 9.0KB+cline_special 7.7KB)·gen_report TB-2.1计数修复(task-level result.json→pass=35非31)·未完成指令:有(§10:10+§22:4x)⇒W:0
> [05:32] R2146: incr_eval轮·①CPU PASS(load33/224·无harness>8000%·最高harness=cline-patched predict 156%) ②MEM PASS(759G/2Ti·1109G avail·/data 5.8T) ③gateway 429 QUOTA_EXHAUSTED(predict stalled·eval不需gateway) ④predict 7路ALIVE:cline-patched220·codex137·opencode452·cc239·pi187·hermes398·dsh175=1825files ⑤incr_eval R2146 DONE:5new ALL resolved(opencode+2→364/443·hermes+3→342/380·0failed 0infra)·eval 1338passed/1669evaluated(↑12) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220f/206r/153res/53fail/14empty·失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2146(glm53_7way 10.1KB+cline_special 7.7KB)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [05:18] R2145: incr_eval轮·①CPU PASS(load40/224·无harness进程>8000%·最高pcpu=191%=claude-code run_single) ②MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T) ③gateway 200 RECOVERED(gateway_probe.sh HTTP 200·predict加速·+26files since R2144) ④predict 7路ALIVE:cline220·codex136·opencode449·cc239·pi185·hermes393·dsh175=1815files(+26) ⑤incr_eval R2145 RUNNING:opencode9new DONE(362/443↑9·0infra)·hermes9new launching·deepseek2new pending·eval 1326resolved(↑9·opencode362·hermes332·cline153·cc151·pi135·dsh129·codex64) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220files/206real/153resolved/14empty·C2失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2145(glm53_7way 9.0KB+cline_special 6.6KB)·清理3个orphan incr_eval进程(仅保留PID3163523)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:56] R2144 流水已归档 → 本文件上半。结论：监控轮·gateway 429·predict +8files·1317resolved UNCHANGED·TB-2.1 opencode rerun ALIVE·MEMORY归档。需要时再读。
> 📦 [04:46] R2143 流水已归档 → 本文件上半。结论：incr_eval R2142 DONE(1317resolved)+TB-2.1 opencode run31p+双报告REGEN+gen_report动态修复+CPU/MEM PASS。需要时再读。
> [04:46] R2143: incr_eval R2142 DONE(all7routes merged·末尾cosmetic traceback[log() got flush= kwarg]忽略·eval工作已全部完成):opencode6new→353↑5·cc1new→151↑1·pi4new→135↑2·hermes1new→332↑1·dsh1new→129·cline0·codex0=9new resolved·total1317(↑9)+TB-2.1 opencode完成run 31p/89t(02-50·20h43m·finished_at已写)+新run仍在跑(14-27·72/89·25p·n_running=1)+双报告REGENERATED(R2142:glm53_7way 10.1KB+cline_special 6.6KB)+gen_report_glm53_7way.py修复4处stale硬编码→动态(TB totals/SWE-bench按pass rate排序/cline-opencode rate/Round变量)+CPU PASS(load35/224·无>8000%·xarray pytest 264%=2.6核远低阈值)+MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T)+predict 7路ALIVE:cline219·codex135·opencode444·cc238·pi185·hermes387·dsh173=1781files·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:17] R2141 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2141(7new·4new resolved)+双报告regen+gateway RECOVERED(429清除)+7路ALIVE(1768files)+TB-2.1 99p。需要时再读。
> 📦 [03:45] R2140 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2140(10new·6new resolved)+双报告regen+gateway 429 QUOTA_EXHAUSTED+7路ALIVE(1728files)+TB-2.1 79p。需要时再读。
> 📦 [02:55] R2138 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval R2138(pi 2new both failed=能力·0new resolved·全7路eval caught up)+双报告regen+7路ALIVE(1662files)+TB-2.1 79p。需要时再读。
> 📦 R2134-R2137 流水已归档 → daily-memories-harness/2026-11-11.md。结论：R2134 incr_eval(+1resolved)+双报告regen·R2135 CPU KILL(sklearn 180核)+重启3停滞orch→7路ALIVE·R2136 incr_eval(+4resolved→1297)+双报告regen·R2137 opencode eval merge(django-11734→fail)+双报告regen。需要时再读。
> 📦 [01:31] R2133 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1603real(↑5)+incr_eval R2133(1inst·+1resolved)+eval 1292resolved(↑5)+cleanup 1empty(429)+双报告REGENERATED(R2133)+TB-2.1 79p。需要时再读。
> 📦 [01:16] R2132 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1598real(↑9)+incr_eval R2132(6inst·+4resolved)+eval 1287resolved(↑4)+cleanup 3empty(429)+双报告REGENERATED(R2132)+TB-2.1 79p。需要时再读。
> 📦 [01:00] R2131 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1589real(↑3)+incr_eval R2131(3inst·+1resolved)+eval 1283resolved(↑1)+双报告REGENERATED(R2131)+TB-2.1 78p。需要时再读。
> 📦 [00:47] R2130 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1586real(↑7)+cleanup 0empty+incr_eval R2130(11inst·+9resolved)+eval 1282resolved(↑9)+双报告REGENERATED(R2130)+TB-2.1 77p。需要时再读。
> 📦 [00:33] R2129 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1579real(↑9)+cleanup 2empty+incr_eval R2129(4inst)+eval 1273resolved(↑3)+双报告REGENERATED(R2129)+merge_R2129_glm53.py修复deepseek model_dir。需要时再读。
> 📦 [00:15] R2128 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+predict 1570real(↑4)+cleanup 1empty+incr_eval R2128(5inst)+eval 1270resolved(↑6)+双报告REGENERATED(R2128)。需要时再读。
> 📦 [00:05] R2127 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1566real(↑14)+cleanup 4empty+incr_eval R2127(22inst)+eval 1264resolved(↑22)+双报告REGENERATED(R2127)。需要时再读。
> 📦 [23:25] R2125 流水已归档 → daily-memories-harness/2026-11-10.md。结论：gateway 200 STABLE+predict 1526real(↑9)+cleanup 3empty+incr_eval R2125(28inst)+eval 1234resolved/1502evaluated+TB-2.1 82p/682t+双报告REGENERATED(R2125)。需要时再读。
> 📦 R2013-R2118 流水(2026-11-09~10,~100轮监控+gateway 429反复+incr_eval+TB-2.1+双报告+多次CPU KILL)已 bulk 归档 → daily-memories-harness/2026-11-09.md / 2026-11-10.md。**关键**:gateway 429/QUOTA反复→恢复·predict 1250→1455real·incr_eval多路catch up·TB-2.1 40→85p·cline empty=能力差非429·gen_report动态状态行修复。需要时再读。
> 📦 R1958-R2012 流水(2026-11-09,~25轮监控+gateway 429/QUOTA_EXHAUSTED+incr_eval+TB-2.1)已 bulk 归档 → daily-memories-harness/2026-11-09.md。**关键**:gateway 429反复·QUOTA_EXHAUSTED reset~02:24·predict 2680/3500·TB-2.1 123p·incr_eval 7/7DONE。需要时再读。

> 📦 R1885-R1957 流水(2026-11-08,~30轮监控+incr_eval+TB-2.1+双报告更新)已 bulk 归档 → daily-memories-harness/2026-11-08.md。**关键**:gateway 429反复→200恢复·predict 1561→2061/3500·real 662→790·TB-2.1 62→69p·codex TB-2.1 84err=适配器(wire_api)·deepseek proxy修复。需要时再读。

> 📦 R1788-R1884 流水(2026-11-07~08,incr_eval全量+TB-2.1 7路全交付+双报告R1785-R1820)已 bulk 归档 → daily-memories-harness/2026-11-07.md。**关键里程碑**:SWE-bench eval 7/7全done·cline356/opencode401·TB-2.1 cline 89/89DONE 7pass·hermes 89/89DONE 5pass·§15:2x判据MET✅。需要时再读。

> 📦 R1612-R1787 流水(2026-11-05~07,~50轮 incr_eval/监控/TB4/quiet)已 bulk 归档 → daily-memories-harness/2026-11-05/06/07.md。**关键**:cline rerun 356/500=71.3%·deepseek→212·kimi全7路100%·TB4全量66×7·R1685 cline低分归因(86%能力差)·R1695 proxy修复。需要时再读。

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
