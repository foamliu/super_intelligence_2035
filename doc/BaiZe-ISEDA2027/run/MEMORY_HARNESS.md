# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2232 monitoring(gateway 200 STABLE·incr_eval R2232 +7全RESOLVED·双报告REGEN R2232)+predict 6/7 alive+自检PASS
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2232·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2231 incr_eval+监控+报告·R2232 incr_eval(7inst全RESOLVED:cline+2·cc+3·hermes+2)+双报告REGEN R2232(gateway 200)
当前动作:     R2232: 自检PASS(CPU load~47/224~21%·无harness>8000%·MEM available1130G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline315f·codex273f·opencode500f DONE·cc422f·pi288f·hermes498f·dsh176f DEAD)+incr_eval R2232 DONE(7inst全RESOLVED:cline sphinx-8638/8721→191·cc sklearn-12682/12973/13124→195·hermes matplotlib-25960/26113→384)+eval(总resolved=1563·总evaluated=1934)+real patches(cline250/315·codex112/273·opencode495/500·cc242/422·pi223/288·hermes430/498·dsh175/176)+双报告REGEN R2232(7way HTTP200+1563res/cline special)+cline C4(315f/250r/191res/65empty·pass75.2%·失败top1=能力差)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0
下一步:       ①本轮commit MEMORY心跳+双报告+push ②predict向500推进(6路alive·opencode已满500·hermes498·cc422·pi288·cline315·codex273·gateway 200=新real持续产·下轮incr_eval新real) ③各路满500后§22:4x两基准7路全交付 ④dsh不重启(silent-exit确定性) ⑤TB-2.1推进 ⑥research日报已查(ACF合规审计=借鉴参考·非新指令)
阻塞:         <各路尚未满500·§22:4x未全交付·dsh silent-exit=dsh binary确定性bug>
ERROR_COUNT:  0
 体积: TASK=21KB / MEMORY=27KB
 cline专项小结: predict_glm53=315files/250real/191resolved/65empty(gateway 200 STABLE·新real patch+1=持续产real·C3 resume fix R1733仍有效·empty=429期产物非归零)·C1:250real/315total(可复算:ls predictions_glm53/cline-patched__*.json|wc -l→315)·C2:failed=能力差(infra=0)·C3:empty=65(gateway 429期产物·非归零·归因红线区分)·C5:报告R2232 REGEN(cline special·191/254=75.2%)·失败top1=能力差(real patch但tests fail)·opencode411/495=83.0%·gap=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [05:08] R2232: 自检PASS(CPU load~47/224~21%·无harness>8000%·MEM available1130G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline315f·codex273f·opencode500f DONE·cc422f·pi288f·hermes498f·dsh176f DEAD)+incr_eval R2232 DONE(7inst全RESOLVED:cline sphinx-8638/8721→191·cc sklearn-12682/12973/13124→195·hermes matplotlib-25960/26113→384)+eval(总resolved=1563·总evaluated=1934)+real patches(cline250/315·codex112/273·opencode495/500·cc242/422·pi223/288·hermes430/498·dsh175/176)+cline C4(315f/250r/191res/65empty·pass75.2%·失败top1=能力差)+双报告REGEN R2232(7way 10313B 05:08/cline special 7652B 05:08)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0
> [05:52] R2233-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~38/224~17%·无harness>8000%·MEM available1.0Ti)+git pull up-to-date+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+**cline C2深度分类(§10:10·7类·占比和=100%)**: 能力67/52.8%·网关额度429 44/34.6%·超时15/11.8%·上游5xx 1/0.8%·适配器0·格式不可解析0·环境依赖0(总127失败=61 real-patch-tests-fail + 66 empty)+证据文件 swebench_verified_full/cline_c2_classification_R2233.json(含top3样本·trace stdout_tail)+复算脚本 c2_cline_R2233.py+gen_cline_special.py增强(动态7类表+top3样本·替代R2062硬编码旧数)+report_harness_cline_special_zh.html REGEN(10944B·title R2233-manual)+归因红线(429/5xx/超时=infra非能力·real-patch-tests-fail=能力)+关键发现: empty主因=网关中文"本次Token额度已用完"(44/66=67%·非HTTP429字面)·resume fix R1733仍有效(C3·empty非归零=429期产物非resume bug)+**未跑incr_eval(避让live loop R2233·防eval_glm53_*.json写冲突)**+未碰7way报告(loop拥有)+未改WAITING/顶部快照(loop拥有)+未完成指令:有(§10:10 C2已实质交付·C1/C3/C4/C5既有·§22:4x进行中各路推进500)·W:0
> [06:4x] R2234-manual(交互式手动wake·与live loop并存·loop cline PID4162360 alive): 自检PASS(CPU load~35/224~16%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+**§10:10 item4 deepseek silent-exit 精细化归因(读progress_glm53_deepseek-harness.json+gw_proxy_dsh日志+run_harness.py:365-456)**: 500题=166real(33.2%)/54 fast-SE(wall<10 rc=0=真silent-exit)/226 long-no-patch(wall≥10 rc=0=跑了数分钟无edit=能力·非silent-exit)/51 timeout/1 rc1(astropy-13454 1.1s=§10:10原hard fault)/4 quota-blocked·63 retried-still-nopatch(重试无效证)+proxy日志4604请求仅208个429(4.5%=少数)+**R2171「325 silent-exit=rc=0~3s dsh binary确定性bug」过粗**: 仅54题真fast(wall<10)·226 long-no-patch=能力(归因红线:非binary-bug)·6 quota=infra(归因红线:非能力)+归因红线flag: 现MEMORY/报告label「dsh binary确定性bug」对ALL no-patch过粗·226 long-no-patch应标能力·6 quota应标infra+证据文件 swebench_verified_full/deepseek_silent_exit_refined_R2234.json(7474B·含refined_attribution+samples+vs_R2171+recommendation)+**未跑incr_eval(避让live loop·防eval_glm53_*.json写冲突)**+未碰7way报告/cline special报告(loop拥有)+未改WAITING/顶部快照(loop拥有)+未完成指令:有(§10:10 item4诊断已精细化·C1-C5既有·§22:4x进行中各路推进500)·W:0



> [04:40] R2231: 自检PASS(CPU load36.57/224~16%·无harness>8000%·MEM available1089G)+gateway 200 RECOVERED(quota reset~04:28如预测)+git pull up-to-date+predict 6/7 ALIVE(cline314f·codex272f·opencode500f DONE·cc415f·pi285f·hermes492f·dsh176f DEAD)+新real patches since R2230(cline+1→249·cc+1→235·hermes+2→424=gateway 200恢复后产real)+incr_eval R2231 DONE(pi django-15380 RESOLVED+hermes matplotlib-25479/25775 双RESOLVED→pi 167/227·hermes 382/428)+eval(总resolved=1556·总evaluated=1927)+real patches(cline249/314·codex111/272·opencode495/500·cc235/415·pi222/285·hermes424/492·dsh175/176)+cline C4(314f/249r/189res/65empty·pass75.9%·失败top1=能力差)+双报告REGEN R2231(7way HTTP200+1556res/cline special·含hermes更新)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0

> [04:22] R2230: 自检PASS(CPU load33.37/224~15%·无harness>8000%·MEM available1089G)+gateway 429 QUOTA(reset~04:28·~6min)+git pull OK(pulled ZhuLong)+predict 6/7 ALIVE(cline312f·codex269f·opencode500f DONE·cc411f·pi283f·hermes489f·dsh176f DEAD·+17files since R2229全empty=429期产物)+backlog SCAN R2230(0 new real backlog·全caught up)+eval(总resolved=1553·总evaluated=1924·无变化)+real patches(cline248/312·codex111/269·opencode495/500·cc234/411·pi221/283·hermes422/489·dsh175/176)+cline C4(312f/248r/189res/64empty·pass75.0%·失败top1=能力差)+双报告REGEN R2230(7way 10389B 04:22/cline special 7738B 04:22·动态gateway 429 status)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计+等算力协议+预注册·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0

> [04:10] R2229: 自检PASS(CPU load32.79/224~15%·无harness>8000%·MEM available1085G)+gateway 429 QUOTA(18min后reset)+git pull up-to-date+predict 6/7 ALIVE(cline310f·codex263f·opencode500f DONE·cc405f·pi282f·hermes487f·dsh176f DEAD·+10files since R2228全empty=429期产物)+backlog SCAN R2229(0 new real backlog·全caught up)+eval(总resolved=1553·总evaluated=1924·无变化)+real patches(cline248/310·codex111/263·opencode495/500·cc234/405·pi221/282·hermes422/487·dsh175/176)+cline C4(310f/248r/189res/62fail/62empty·pass75.0%·失败top1=能力差)+双报告REGEN R2229(7way 10389B 04:10/cline special 7738B 04:10·动态gateway 429 status)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计+等算力协议+预注册·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0
> [04:03] R2228: 自检PASS(CPU load33.33/224~15%·无harness>8000%·MEM available1088G)+gateway 429 QUOTA(25min37s后reset)+git pull up-to-date+predict 6/7 ALIVE(cline309f·codex259f·opencode500f DONE·cc401f·pi281f·hermes485f·dsh176f DEAD·+19files since R2227全empty=429期产物)+backlog SCAN R2228(0 new real backlog·全caught up)+eval(总resolved=1553·总evaluated=1924·无变化)+real patches(cline248/309·codex111/259·opencode495/500·cc234/401·pi221/281·hermes422/485·dsh175/176)+cline C4(309f/248r/189res/62fail/61empty·pass75.0%·失败top1=能力差)+双报告REGEN R2228(7way 9302B 04:03/cline special 6715B 04:03·动态gateway 429 status)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计+等算力协议+预注册·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0
> [03:55] R2227: 自检PASS(CPU load32.31/224~15%·无harness>8000%·MEM available1090G)+gateway 429 QUOTA(37min后reset)+git pull up-to-date+predict 6/7 ALIVE(cline307f·codex252f·opencode500f DONE·cc395f·pi279f·hermes483f·dsh176f DEAD)+backlog SCAN R2227(0 new real backlog·全caught up)+eval(总resolved=1553·总evaluated=1924·无变化)+real patches(cline248/307·codex111/252·opencode495/500·cc234/395·pi221/279·hermes422/483·dsh175/176)+cline C4(307f/248r/189res/62fail/59empty·pass75.0%·失败top1=能力差)+双报告REGEN R2227(7way 10389B 03:53/cline special 7738B 03:53·**动态gateway probe更新:hardcoded"200已恢复"→动态429/200自动检测**)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+未完成指令:有(§10:10+§22:4x)·W:0
> [03:42] R2226: 自检PASS(CPU load34.30/224~15%·无harness>8000%·MEM available1091G)+gateway 429 QUOTA(real key探针=429)+git pull up-to-date+predict 6/7 ALIVE(cline305f·codex247f·opencode500f DONE·cc389f·pi278f·hermes481f·dsh176f DEAD)+backlog SCAN(9 new real uneval:opencode3+pi3+hermes3)+incr_eval R2226 DONE(9inst·418s:opencode sympy-19495/21612/23534全RESOLVED·pi django-13590 failed+13658/13670 RESOLVED·hermes sympy-17139 RESOLVED+django-14631/14725 infra)+eval(cline189/252=75.0%·codex74/111=66.7%·opencode411/495=83.0%·cc192/239=80.3%·pi166/226=73.5%·hermes380/426=89.2%·dsh141/175=80.6%·总resolved=1553↑6·总evaluated=1924)+real patches(cline248/305·codex111/247·opencode495/500·cc234/389·pi221/278·hermes422/481·dsh175/176)+cline C4(305f/248r/189res/62fail/57empty·pass75.0%·失败top1=能力差)+双报告REGEN R2226(7way 10296B 03:38/cline special 7661B 03:38)+backlog=0(post-eval)+磁盘(/data 5.8T 18%·/ 351G 4%)+未完成指令:有(§10:10+§22:4x)·W:0
> [03:19] R2225: 自检PASS(CPU load35.89/224~16%·无harness>8000%·MEM available1090G)+gateway 429 QUOTA+git pull up-to-date+predict 6/7 ALIVE(cline301f·codex237f·opencode500f DONE·cc379f·pi275f·hermes478f·dsh176f DEAD)+backlog=0(+11files全empty=429期)+eval(总resolved=1547·总evaluated=1887)+双报告REGEN R2225+未完成指令:有(§10:10+§22:4x)·W:0
> [03:10] R2224: 自检PASS(CPU load37.62/224~17%·无harness>8000%·MEM available1091G·harness maxRSS5.7GB)+gateway 429 QUOTA_EXHAUSTED(wait unknown·predict stalled)+git pull up-to-date+predict 6/7 ALIVE(cline300f·codex232f·opencode500f DONE·cc374f·pi274f·hermes477f·dsh176f DEAD)+backlog SCAN R2224(0 new real backlog·全caught up·+20files since R2223全empty=429期产物)+eval(cline189/249=75%·codex74/109=67%·opencode408/495=82%·cc192/229=83%·pi164/214=76%·hermes379/416=91%·dsh141/175=80%·总resolved=1547·总evaluated=1887)+cline C4(300f/248r/189res/62fail/52empty·pass75%·失败top1=能力差)+双报告REGEN R2224(7way 10296B 03:10/cline special 7661B 03:10)+TB-2.1(cline10p/90·codex1p/90·opencode35p/120·cc0p/90·pi36p/180·hermes7p/90·dsh11p/90·总100p/750)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(advice=等算力协议+预注册·非新指令·纳入参考)·未完成指令:有(§10:10+§22:4x)·W:0
> [02:56] R2223: 自检PASS(CPU load39.87/224~18%·无harness>8000%·MEM available1091G·harness maxRSS5.6GB)+gateway 429 QUOTA_EXHAUSTED(wait~1h33m·predict stalled)+git pull up-to-date+predict 6/7 ALIVE(cline298f·codex226f·opencode500f DONE·cc368f·pi273f·hermes474f·dsh176f DEAD)+backlog SCAN R2223(0 new real backlog·全caught up·+12files since R2222全empty=429期产物)+eval(cline189/249=75.9%·codex74/109=67.9%·opencode408/495=82.4%·cc192/229=83.8%·pi164/214=76.6%·hermes379/416=91.1%·dsh141/175=80.6%·总resolved=1547·总evaluated=1924)+cline C4(298f/248r/189res/62fail/50empty·pass75.9%·失败top1=能力差)+双报告REGEN R2223(7way 10305B 02:56/cline special 6601B 02:56)+TB-2.1(cline10p/89·codex1p/89·opencode35p/117·cc0p/89·pi36p/178·hermes7p/89·dsh11p/89)+磁盘(/data 5.8T 18%·/ 351G 4%)·未完成指令:有(§10:10+§22:4x)·W:0
> [02:48] R2222: 自检PASS(CPU load45/224~20%·无harness>8000%·MEM available1092G·harness maxRSS5.6GB)+gateway 429 QUOTA_EXHAUSTED(wait~1h41m·predict stalled)+git pull up-to-date+predict 5/7 ALIVE(cline296f·codex221f·opencode500f DONE·cc363f·pi272f·hermes473f·dsh176f DEAD)+backlog SCAN R2222(0 new real backlog·全caught up·+9files since R2221全empty=429期产物)+eval(cline189/252=75.0%·codex74/111=66.7%·opencode408/495=82.4%·cc192/239=80.3%·pi164/226=72.6%·hermes379/426=89.0%·dsh141/175=80.6%·总resolved=1547·总evaluated=1924)+cline C4(296f/248r/189res/62fail/48empty·pass75.0%·失败top1=能力差)+双报告REGEN R2222(7way 9174B 02:48/cline special 6601B 02:48)+TB-2.1(cline10p/89·codex1p/89·opencode35p/117·cc0p/89·pi36p/178·hermes7p/89·dsh11p/89)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(advice=ACF合规审计·非新指令·纳入参考)·未完成指令:有(§10:10+§22:4x)·W:0
> [02:40] R2221: 自检PASS(CPU load43/224~19%·无harness>8000%·MEM available1091G·harness maxRSS460MB)+gateway 429 QUOTA_EXHAUSTED(从R2220 200退化·predict stalled)+git pull up-to-date+predict 5/7 ALIVE(cline295f·codex218f·opencode500f DONE·cc360f·pi271f·hermes472f·dsh176f DEAD)+backlog SCAN R2221(0 new real backlog·全caught up·+14files since R2220全empty=429期产物)+eval(cline189/252=75.0%·codex74/111=66.7%·opencode408/495=82.4%·cc192/239=80.3%·pi164/226=72.6%·hermes379/426=89.0%·dsh141/175=80.6%·总resolved=1547·总evaluated=1924)+cline C4(295f/248r/189res/62fail/47empty·pass75.0%·失败top1=能力差)+双报告REGEN R2221(7way 10296B 02:40/cline special 7661B 02:40)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(advice=ACF合规审计·非新指令·纳入参考)·未完成指令:有(§10:10+§22:4x)·W:0
> [02:29] R2220: 自检PASS(CPU load37/224~17%·无harness>8000%·MEM available1092G·harness maxRSS460MB)+gateway 200 RECOVERED(从R2219 429恢复)+git pull up-to-date+predict 5/7 ALIVE(cline294f·codex213f·opencode500f DONE·cc355f·pi270f·hermes470f·dsh176f DEAD)+backlog SCAN R2220(0 new real backlog·全caught up·+3files since R2219全empty=429期产物)+eval(cline189/252=75.0%·codex74/111=66.7%·opencode408/495=82.4%·cc192/239=80.3%·pi164/226=72.6%·hermes379/426=89.0%·dsh141/175=80.6%·总resolved=1547·总evaluated=1924)+cline C4(294f/248r/189res/62fail/46empty·pass75.0%·失败top1=能力差)+双报告REGEN R2220(7way 10295B 02:29/cline special 7661B 02:29)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(advice=ACF合规审计·非新指令·纳入参考)·未完成指令:有(§10:10+§22:4x)·W:0
> [02:15] R2219: 自检PASS(CPU load39/224~17%·无harness>8000%·MEM available1088G·harness maxRSS460MB)+gateway 429 QUOTA_EXHAUSTED(待~2h12m·predict stalled)+git pull up-to-date+predict 5/7 ALIVE(cline291f·codex206f·opencode500f DONE·cc348f·pi268f·hermes468f·dsh0f DEAD)+incr_eval R2219 SCAN(0 new real backlog·+11files since R2218全empty=429·no docker)+eval(cline189/252=75.0%·codex74/111=66.7%·opencode408/495=82.4%·cc192/239=80.3%·pi164/226=72.6%·hermes379/426=89.0%·dsh141/175=80.6%·总resolved=1547·总evaluated=1924)+cline C4(291f/248r/189res/62fail/43empty·pass75.0%·失败top1=能力差)+双报告REGEN R2219(7way 9173B 02:15/cline special 6601B 02:15)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(无新期·advice=ACF合规审计·非新指令·纳入参考)·未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2209-R2218 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval多轮(+18resolved)·总resolved 1513→1547·gateway 200稳定期·predict推进(cline286→291·codex195→203·cc326→343)·双报告REGEN。需要时再读。

> 📦 R2208 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval 7inst·+5resolved+1failed+1infra·总resolved 1503→1513·hermes RESTARTED PID2677820·predict 2181files·双报告REGEN。需要时再读。

> 📦 R2207 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval +5resolved+1failed(hermes DIED)·总resolved 1498→1503·predict 2168files·双报告REGEN。需要时再读。

> 📦 R2203-R2206 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复(quota周期性耗尽)·incr_eval 0new(eval caught up·1498resolved)·predict 2112→2152files/1859real·opencode满500·cline C4 pass74.9%稳定。需要时再读。

> 📦 R2190-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval +5resolved(1444→1446)·predict 1820→1823real·opencode满500·双报告REGEN·dsh DEAD。需要时再读。

> 📦 R2192-R2202 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429↔200反复·incr_eval catch up(eval 1450→1498·+48)·predict 1828→2126files/1859real·opencode满500·R2193发现并修复incr_eval parser bug(inst_rep=rd.get(iid,rd))·双报告REGEN。需要时再读。
> 📦 R2184-R2191 流水已归档 → daily-memories-harness/2026-11-11.md。结论：incr_eval 累计+19resolved(1420→1446)·predict 1799→1823real·opencode满500·双报告REGEN R2184-R2191·dsh DEAD。需要时再读。
> 📦 R2175-R2183 流水(2026-11-11,incr_eval+监控+双报告+restart stalled routes)已归档 → daily-memories-harness/2026-11-11.md。**关键**:incr_eval多路catch up·hermes +1resolved(sphinx-7985)·total1420·predict 1799real/1927=93.4%·6/7 alive·dsh DEAD(silent-exit)·gateway functional。需要时再读。

> 📦 [09:51] R2165 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+cleanup 4empty+双报告REGENERATED(R2165)。需要时再读。

> 📦 [09:31] R2164 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 5NEW(0resolved·1353不变)+0empty(无需cleanup)+双报告REGENERATED(R2164)。需要时再读。

> 📦 [09:14] R2163 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 9NEW(+6resolved→1353)+cleanup 4empty+stuck R2142 container清理+双报告REGENERATED(R2163)。需要时再读。

> 📦 [08:49] R2162 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 200 STABLE+incr_eval 11NEW(+7resolved→1347)+cleanup 2empty+双报告REGENERATED(R2162)。需要时再读。

> 📦 [08:33] R2161 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway RECOVERED(200)+TB-2.1 opencode rerun COMPLETED(33pass)+cleanup 12empty+incr_eval 0NEW(1340resolved不变)+双报告REGEN(R2161)。需要时再读。

> 📦 R2148-R2160 流水(2026-11-11,~13轮监控+gateway 429→200恢复+codex predict RESTARTED+cleanup多次+TB-2.1 opencode rerun)已归档 → daily-memories-harness/2026-11-11.md。需要时再读。

> 📦 [06:55] R2152 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA持续+predict 1673real不变+cleanup 14empty(429infra)+incr_eval 0NEW(1340resolved不变)+TB-2.1 opencode 82/89done。需要时再读。

> 📦 [05:48] R2147 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 2new(+2resolved→1340)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2147。需要时再读。
> 📦 [05:32] R2146 流水已归档 → daily-memories-harness/2026-11-11.md。结论：gateway 429 QUOTA+incr_eval 5new ALL resolved(+5→1338)+TB-2.1 opencode rerun ALIVE+双报告REGEN R2146。需要时再读。
> 📦 [05:18] R2145: incr_eval轮·①CPU PASS(load40/224·无harness进程>8000%·最高pcpu=191%=claude-code run_single) ②MEM PASS(761G/2Ti·1.1Ti avail·/data 5.8T) ③gateway 200 RECOVERED(gateway_probe.sh HTTP 200·predict加速·+26files since R2144) ④predict 7路ALIVE:cline220·codex136·opencode449·cc239·pi185·hermes393·dsh175=1815files(+26) ⑤incr_eval R2145 RUNNING:opencode9new DONE(362/443↑9·0infra)·hermes9new launching·deepseek2new pending·eval 1326resolved(↑9·opencode362·hermes332·cline153·cc151·pi135·dsh129·codex64) ⑥TB-2.1 opencode rerun ALIVE(31p/89t·harbor PID3984113) ⑦research日报2026-11-10已查·harness建议=异构判官>重复跑(已在7way中) ⑧cline C4:220files/206real/153resolved/14empty·C2失败top1=能力差(real patch but tests fail) ⑨双报告REGEN R2145(glm53_7way 9.0KB+cline_special 6.6KB)·清理3个orphan incr_eval进程(仅保留PID3163523)·未完成指令:有(§10:10+§22:4x)⇒W:0
> 📦 [04:56] R2144 流水已归档 → 本文件上半。结论：监控轮·gateway 429·predict +8files·1317resolved UNCHANGED·TB-2.1 opencode rerun ALIVE·MEMORY归档。需要时再读。
> 📦 [04:46] R2143 流水已归档 → 本文件上半。结论：incr_eval R2142 DONE(1317resolved)+TB-2.1 opencode run31p+双报告REGEN+gen_report动态修复+CPU/MEM PASS。需要时再读。
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
