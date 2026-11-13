# Deepread: 1794396977405_rawgv — xrun log status + .shm crosscheck

- **trace**: 1794396977405_rawgv, e0014036 @ hfeg0pkn005[10.129.2.14], mc104, digital (verilog:230/drc:156)
- **size**: 306KB / 60 msgs / 35 user-role / ~6 real turns
- **claim**: r471, shard A

## User intent (real turns)
- U0 核心 produce-task: 「1.写一个脚本，检测指定路径下的log是否有报错；2.写一个脚本检测指定路径下的.shm文件是否有」
- U6: 给失败 sim 目录 `/rundata/dscqa/.../debug/1109_1951/pte_test_DDR6_hPPR_DQL_Sim.X2P3_11600_dualpsd`
- U10: 读 xrun.log 和 ncsim.shm/ 内容
- U13: 给正确结束的 log+shm 路径作对照 `.../debug/1104_1129/pte_test_DDR6_SPPR_Undo_Sim...`
- U28: check_log_errors.py 存到 debug 路径下

## Agent deliverables (3 scripts, stdlib only)
1. **check_log_errors.py** — xrun/EDA log 行级分类器
   - 致命标记 (fatal): `*F,` / `FATSEV` / `Simulation terminated via $fatal` / `Aborted:`(不含 `$fatal(`) / `errors: N`(N>0)
   - 正常结束 (done): `is done @` / `(total: `
   - 噪声排除 (noise): `Annotation completed with 0 Errors and` / `errors: 0`(每模块统计) / `*W,`(Xcelium 警告) / 源码 `$fatal("` 定义串
   - 退出码: 0=全OK / 1=有FAIL / 3=UNCERTAIN(无fatal无done) / 2=IO错误
2. **check_shm.py** — .shm 目录/文件检测 + 交叉校验
   - Xcelium .shm 通常是目录(ncsim.shm/ 含 ncsim.dsn + ncsim.trn)
   - 关键洞察: 仿真即使 FATAL 中止也会写出近满尺寸 .shm → "shm 存在/够大" != "仿真有效"
   - --check-log: 找同目录 xrun.log 复用 classify 判定有效性
   - 退出码: 0=找到 / 1=未找到 / 5=找到但 log FAIL / 2=IO
3. **inspect_simdir.py** — 定向读 xrun.log(大小/行数/头尾/关键字命中) + ncsim.shm/ 文件(大小+十六进制头)

## A-faithful 判定
合格: 用户给任务描述(2条)+失败/对照路径, 未给分类规则/噪声排除/退出码方案/交叉校验逻辑 → agent 自主设计 classify 规则 + noise 排除 + exit code scheme + .shm≠validity 洞察。
deliverable = 写脚本到私有 /home/e0014036/Desktop/DRCOA_AI/AI_Result/ + /rundata/dscqa/.../debug/ → INFEASIBLE(私有路径, .75 Permission denied) → B档合成。

## B档合成方向
archetype = `xrun-log-status-classifier-with-shm-crosscheck` (新, 区别于 OdtErrScan 的字段级解析)。
单脚本 xrun_log_status_check.py: --log/--shm/--check-log/--json, 行级 classify + .shm 检测 + 交叉校验 + JSON 输出 + 退出码。
A/B 零重叠: 不同 fatal marker 行、不同 cell/test 名、不同噪声 decoy、不同 .shm 尺寸、B 含 UNCERTAIN + Aborted-with-$fatal( 边界。
判分: import SUT 脚本 → 在 B 上跑 → 断言分类/噪声排除/交叉校验/退出码/跨输入守卫/3-seed。
