# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

PHASE:        R2255 自检+incr_eval5inst(4resolved+1failed)+cleanup5empty+双报告REGEN轮·自检PASS
已完成:       H-B OK·Gate7/7·TB报告·cline专项C1-C5 R1785-R2255·TB4 0passed(能力)·TB-2.1 oracle5/5·R1789 eval 7/7DONE·R1804双报告交付·R1969-R2254 incr_eval+监控+报告·R2255 incr_eval5inst(+4resolved+1failed)+cleanup5empty+双报告REGEN(R2255)
当前动作:     R2255-manual: 自检PASS(CPU load~41/224~18%·无harness>8000%·MEM available1084G)+gateway functional(predict产real)+predict 5/7 ALIVE(cline·codex·cc·pi·hermes alive·opencode DONE at495·dsh DEAD)+incr_eval R2255 pass1(3inst:cline sympy-17139 RESOLVED+cc sympy-15875 RESOLVED+hermes sympy-24443 RESOLVED→+3resolved)+cleanup 2空patch+pass2(2inst:codex xarray-6992 FAILED+cc sympy-17139 RESOLVED→+1resolved+1failed)+cleanup 3空patch+eval(总resolved=1624↑4·总n=2003·cline202/268·codex79/117·opencode411/495·cc209/258·pi175/237·hermes407/453·dsh141/175)+双报告REGENERATED(R2255·7way 9169B·cline special 10603B)+empty=0全路+cline C4(262f/262r/202res/0empty·pass202/262real=77.1%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(无新增)+未完成指令:有(§10:10+§22:4x)·W:0
下一步:       ①本轮commit MEMORY心跳+incr_eval+双报告+push ②predict向500推进(5路alive·opencode495 DONE·hermes449近满·cline262/cc253/pi232/codex115远·dsh DEAD不重启) ③predict产real→incr_eval拾取→报告更新 ④各路满500后§22:4x两基准7路全交付 ⑤dsh silent-exit=能力(R2234) ⑥TB-2.1推进
阻塞:         <各路尚未满500·§22:4x未全交付·dsh silent-exit=能力(R2234精细化)>
ERROR_COUNT:  0
 体积: TASK=21KB / MEMORY=30KB
 cline专项小结: predict_glm53=262files/262real/202resolved/0empty(gateway functional产real·C3 resume fix R1733仍有效)·C1:262real/262total(可复算:ls predictions_glm53/cline-patched__*.json|wc -l→262)·C2:failed=能力65/50.0%·429 44/33.8%·超时15/11.5%·5xx 1/0.8%(R2233分类)·C3:empty=0(gateway functional·无新空patch)·C5:报告R2255(cline special·202/262real=77.1%)·失败top1=能力差(real patch但tests fail)·opencode411/495=83.0%·gap=能力差

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。
### 本唤醒流水
> [10:42] R2255-manual(交互式手动wake): 自检PASS(CPU load~41/224~18%·无harness>8000%·MEM available1084G)+gateway functional(predict产real)+predict 5/7 ALIVE(cline·codex·cc·pi·hermes alive·opencode DONE at495·dsh DEAD)+incr_eval R2255 pass1(3inst:cline sympy-17139 RESOLVED+cc sympy-15875 RESOLVED+hermes sympy-24443 RESOLVED→+3resolved)+cleanup 2空patch(codex xarray-6938+cc sympy-16597)+pass2(2inst:codex xarray-6992 FAILED+cc sympy-17139 RESOLVED→+1resolved+1failed)+cleanup 3空patch(cc sympy-16792/17318+pi django-16631)+eval(总resolved=1624↑4·总n=2003·cline202/268·codex79/117·opencode411/495·cc209/258·pi175/237·hermes407/453·dsh141/175)+双报告REGENERATED(R2255·7way 9169B·cline special 10603B)+empty=0全路+cline C4(262f/262r/202res/0empty·pass202/262real=77.1%·失败top1=能力差)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(无新增)+未完成指令:有(§10:10+§22:4x)·W:0
> [10:14] R2254-manual(交互式手动wake): 自检PASS(CPU load~39/224~18%·无harness>8000%·MEM available1085G)+gateway functional(predict产real)+predict 5/7 ALIVE+cleanup 3空patch+incr_eval R2254(2inst:cline sympy-16886 RESOLVED+pi django-16612 RESOLVED→+2resolved)+eval(总resolved=1620↑2·总n=1998)+双报告REGENERATED(R2254)+empty=0全路+cline C4(262f/262r/201res/0empty·pass201/262real=76.7%)+未完成指令:有(§10:10+§22:4x)·W:0
> 📦 R2252-R2253b 流水(2026-11-12,incr_eval多路catch up+双报告REGEN)已归档 → daily-memories-harness/2026-11-12.md。结论：R2253b +6resolved+1failed·R2252 +4resolved·gateway 200恢复·双报告REGEN。需要时再读。
> 📦 R2249-R2251 流水(2026-11-12,gateway 429 quota恢复轮·cleanup空patch·incr_eval)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429恢复→200·real patches 1963→1967r·cleanup空patch·incr_eval多路catch up·双报告REGEN。需要时再读。
> 📦 R2246-R2249 流水(2026-11-12,gateway 429 quota stalled轮·cleanup 648+17空patch·real未变·双报告REGEN R2246-R2248)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429/403反复·real patches不变(1963r)·cleanup空patch·backlog 0·双报告R2248 current。需要时再读。
> 📦 R2244-R2245 流水(2026-11-12,gateway 429 quota stalled轮)已归档 → daily-memories-harness/2026-11-12.md。结论：gateway 429持续·real patches不变(1963r)·cleanup空patch·backlog 0·双报告REGEN。需要时再读。
> [08:09] R2243-manual(交互式手动wake): 自检PASS(CPU load45/224~20%·无harness>8000%·MEM available1086G)+gateway 429 QUOTA_EXHAUSTED(predict stalled·wait~1h20m)+git pull up-to-date+predict 6/7 ALIVE(cline328f·codex290f·opencode500f DONE·cc445f·pi303f·hermes500f DONE·dsh176f DEAD;429期新文件=空patch)+incr_eval backlog全0(新文件均空patch·real patch数未变)+eval(总resolved=1608·总evaluated=1985)+real patches(cline259/328·codex114/290·opencode495/500·cc248/445·pi228/303·hermes444/500·dsh175/176)+双报告REGEN R2243(7way 10392B 08:09/cline special 12113B 08:09)+cline C4(328f/259r/199res/69empty·pass76.8%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [07:02] R2238-manual(交互式手动wake): 自检PASS(CPU load~39/224~18%·无harness>8000%·MEM available1086G)+gateway 200 STABLE+git pull up-to-date+predict 5/7 ALIVE(cline324f·codex277f·opencode500f DONE·cc432f·pi299f·hermes500f DONE·dsh176f DEAD)+incr_eval R2238 DONE(hermes pytest-7324/7432/7571全RESOLVED→hermes 444n/398res)+eval(总resolved=1599·总evaluated=1975)+real patches(cline256/324·codex113/277·opencode495/500·cc246/432·pi228/299·hermes440/500·dsh175/176)+双报告REGEN R2238(7way 10313B 07:07/cline special 12051B 07:06)+cline C4(324f/256r/197res/68empty·pass75.2%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0
> [07:14] R2239-manual(交互式手动wake): 自检PASS(CPU load~39/224~18%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+predict 5/7 ALIVE(cline324f·codex277f·opencode500f DONE·cc433f·pi299f·hermes500f DONE·dsh176f DEAD)+无新incr_eval backlog(全caught up)+eval(总resolved=1599·总evaluated=1975)+real patches(cline256/324·codex113/277·opencode495/500·cc247/433·pi228/299·hermes440/500·dsh175/176)+双报告REGEN R2239(7way 10313B 07:14/cline special 12051B 07:14)+cline C4(324f/256r/197res/68empty·pass75.2%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0
> [07:30] R2240-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~50/224~22%·无harness>8000%·MEM available1085G)+gateway 200 STABLE+git pull up-to-date+predict 5/7 ALIVE(cline326f·codex279f·opencode500f DONE·cc433f·pi300f·hermes500f DONE·dsh176f DEAD)+incr_eval R2240 DONE(4inst:cline sympy-11618 FAIL+sympy-12096 RESOLVED·codex django-16662 RESOLVED·cc sphinx-11445 RESOLVED→+3resolved+1failed)+backlog全0+eval(总resolved=1602·总evaluated=1979)+real patches(cline258/326·codex114/279·opencode495/500·cc247/433·pi228/300·hermes440/500·dsh175/176)+双报告REGEN R2240(7way 10313B 07:30/cline special 12051B)+cline C4(326f/258r/198res/68empty·pass75.6%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(方法论借鉴·非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [07:47] R2241-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~43/224~19%·无harness>8000%·MEM available1088G)+gateway 200 STABLE+git pull up-to-date+predict 5/7 ALIVE(cline327f·codex279f·opencode500f DONE·cc433f·pi300f·hermes500f DONE·dsh176f DEAD)+incr_eval R2241 DONE(5inst全RESOLVED:cline sympy-12419·cc sphinx-11510·hermes sphinx-7454/7590/8056→+5resolved全PASS·backlog全0)+eval(总resolved=1607·总evaluated=1977)+real patches(cline259/327·codex114/279·opencode495/500·cc248/433·pi228/300·hermes443/500·dsh175/176)+双报告REGEN R2241(7way 10392B 07:47/cline special 12113B 07:47)+cline C4(327f/259r/199res/68empty·pass76.8%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0
> [07:58] R2242-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load46/224~21%·无harness>8000%·MEM available1084G)+gateway 429 QUOTA_EXHAUSTED(predict stalled)+git pull up-to-date+predict 4/7 ALIVE(cline327f·codex285f·opencode500f DONE·cc440f·pi302f·hermes500f DONE·dsh176f DEAD;429期codex+2/cc+2新文件=空patch)+incr_eval R2242 DONE(1inst:hermes sphinx-doc__sphinx-8475 RESOLVED→+1resolved=1608)+backlog全0+eval(总resolved=1608·总evaluated=1985)+real patches(cline259/327·codex114/285·opencode495/500·cc248/440·pi228/302·hermes444/500·dsh175/176)+双报告REGEN R2242(7way 10392B 07:58/cline special 12113B 07:58)+cline C4(327f/259r/199res/68empty·pass76.8%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+未完成指令:有(§10:10+§22:4x)·W:0

> [05:08] R2232: 自检PASS(CPU load~47/224~21%·无harness>8000%·MEM available1130G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline315f·codex273f·opencode500f DONE·cc422f·pi288f·hermes498f·dsh176f DEAD)+incr_eval R2232 DONE(7inst全RESOLVED:cline sphinx-8638/8721→191·cc sklearn-12682/12973/13124→195·hermes matplotlib-25960/26113→384)+eval(总resolved=1563·总evaluated=1934)+real patches(cline250/315·codex112/273·opencode495/500·cc242/422·pi223/288·hermes430/498·dsh175/176)+cline C4(315f/250r/191res/65empty·pass75.2%·失败top1=能力差)+双报告REGEN R2232(7way 10313B 05:08/cline special 7652B 05:08)+TB-2.1(100p/740t)+磁盘(/data 5.8T 18%·/ 351G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+未完成指令:有(§10:10+§22:4x)·W:0
> [05:52] R2233-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~38/224~17%·无harness>8000%·MEM available1.0Ti)+git pull up-to-date+research日报11-12已查(ACF合规审计=借鉴参考·非新指令·纳入参考)+**cline C2深度分类(§10:10·7类·占比和=100%)**: 能力67/52.8%·网关额度429 44/34.6%·超时15/11.8%·上游5xx 1/0.8%·适配器0·格式不可解析0·环境依赖0(总127失败=61 real-patch-tests-fail + 66 empty)+证据文件 swebench_verified_full/cline_c2_classification_R2233.json(含top3样本·trace stdout_tail)+复算脚本 c2_cline_R2233.py+gen_cline_special.py增强(动态7类表+top3样本·替代R2062硬编码旧数)+report_harness_cline_special_zh.html REGEN(10944B·title R2233-manual)+归因红线(429/5xx/超时=infra非能力·real-patch-tests-fail=能力)+关键发现: empty主因=网关中文"本次Token额度已用完"(44/66=67%·非HTTP429字面)·resume fix R1733仍有效(C3·empty非归零=429期产物非resume bug)+**未跑incr_eval(避让live loop R2233·防eval_glm53_*.json写冲突)**+未碰7way报告(loop拥有)+未改WAITING/顶部快照(loop拥有)+未完成指令:有(§10:10 C2已实质交付·C1/C3/C4/C5既有·§22:4x进行中各路推进500)·W:0
> [06:4x] R2234-manual(交互式手动wake·与live loop并存·loop cline PID4162360 alive): 自检PASS(CPU load~35/224~16%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+**§10:10 item4 deepseek silent-exit 精细化归因(读progress_glm53_deepseek-harness.json+gw_proxy_dsh日志+run_harness.py:365-456)**: 500题=166real(33.2%)/54 fast-SE(wall<10 rc=0=真silent-exit)/226 long-no-patch(wall≥10 rc=0=跑了数分钟无edit=能力·非silent-exit)/51 timeout/1 rc1(astropy-13454 1.1s=§10:10原hard fault)/4 quota-blocked·63 retried-still-nopatch(重试无效证)+proxy日志4604请求仅208个429(4.5%=少数)+**R2171「325 silent-exit=rc=0~3s dsh binary确定性bug」过粗**: 仅54题真fast(wall<10)·226 long-no-patch=能力(归因红线:非binary-bug)·6 quota=infra(归因红线:非能力)+归因红线flag: 现MEMORY/报告label「dsh binary确定性bug」对ALL no-patch过粗·226 long-no-patch应标能力·6 quota应标infra+证据文件 swebench_verified_full/deepseek_silent_exit_refined_R2234.json(7474B·含refined_attribution+samples+vs_R2171+recommendation)+**未跑incr_eval(避让live loop·防eval_glm53_*.json写冲突)**+未碰7way报告/cline special报告(loop拥有)+未改WAITING/顶部快照(loop拥有)+未完成指令:有(§10:10 item4诊断已精细化·C1-C5既有·§22:4x进行中各路推进500)·W:0
> [06:27] R2235-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~39/224~17%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline323f·codex276f·opencode500f DONE·cc430f·pi297f·hermes500f DONE·dsh176f DEAD)+incr_eval R2235(cline 3done: sphinx-9461 FAIL·sphinx-9591 RESOLVED·sphinx-9602 FAIL→197res/262eval·cc 3 eval bg scikit-learn·pi 4 eval pending·hermes 3 eval pending)+eval(总resolved=1584·总evaluated=1958)+real patches(cline256/323·codex113/276·opencode495/500·cc246/430·pi227/297·hermes435/500·dsh175/176)+双报告REGEN R2235(7way 10310B 06:27/cline special 12051B 06:27)+cline C4(323f/256r/197res/67empty·pass75.2%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [06:43] R2236(loop wake·cline PID2775968): 自检PASS(CPU load~38/224~17%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline323f·codex276f·opencode500f DONE·cc430f·pi297f·hermes500f DONE·dsh176f DEAD)+incr_eval R2236 DONE(cc sphinx-doc__sphinx-10466 RESOLVED→cc n=251 resolved=203·1inst 1resolved)+eval(总resolved=1596·总evaluated=1971)+real patches(cline256/323·codex113/276·opencode495/500·cc246/430·pi227/297·hermes437/500·dsh175/176)+双报告REGEN R2236(7way 06:43/cline special 06:43)+cline C4(323f/256r/197res/67empty·pass75.2%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+**MEMORY归档R2219-R2231→daily-memories-harness/2026-11-12.md(9.5KB·31KB→16KB)**+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+未完成指令:有(§10:10+§22:4x)·W:0
> [06:54] R2237-manual(交互式手动wake·与live loop并存): 自检PASS(CPU load~38/224~17%·无harness>8000%·MEM available1087G)+gateway 200 STABLE+git pull up-to-date+predict 6/7 ALIVE(cline324f·codex276f·opencode500f DONE·cc430f·pi299f·hermes500f DONE·dsh176f DEAD)+incr_eval R2237 DONE(pi django__django-15732 FAIL/capability→pi 233n/171res)+eval(总resolved=1596·总evaluated=1972)+real patches(cline256/324·codex113/276·opencode495/500·cc246/430·pi228/299·hermes437/500·dsh175/176)+双报告REGEN R2237(7way 10313B 06:54/cline special 12051B 06:54)+cline C4(324f/256r/197res/68empty·pass75.2%·失败top1=能力差)+TB-2.1(100p)+磁盘(/data 5.8T 18%·/ 352G 4%)+research日报11-12已查(ACF合规审计=借鉴参考·非新指令)+未完成指令:有(§10:10+§22:4x)·W:0



> 📦 R2219-R2231 流水已归档 → daily-memories-harness/2026-11-12.md。结论：incr_eval多轮·总resolved 1553→1584·gateway 429↔200反复·predict推进(cline314→323·cc411→430·pi283→297·codex269→276·hermes489→500 DONE)·双报告REGEN。需要时再读。
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
