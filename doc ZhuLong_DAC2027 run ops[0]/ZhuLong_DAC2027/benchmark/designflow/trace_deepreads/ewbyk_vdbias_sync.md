# Deepread: ewbyk — tongfanl FineSim aging pvdias 同步脚本

- session: 1795137757784_ewbyk
- user: tongfanl @ hfeg0pgn072 (10.129.35.171)
- mc: 20 (r915 rescan 41 fresh B-domain sids, ranked score=20)
- domain: spice_sim
- messages: 629KB / 114 msgs / 9 user msgs

## 用户真实意图（原话）
- U[0] (grill-me 触发): stress-test 一个计划 — FineSim aging 仿真 Pre vs Aging step2 文件夹一致性检查
- U[1]: 「必须都是vdbias且值要一样。我有的step2丢的时候vdbias变成不一样了...可以让step2每个子文件夹下的step2吃的si.inp中的vsbias和Pre中一样。适合批量实现？」
- U[2]: 「idbias的我已经重新丢了，你做的脚本只用管：把step2的si.inp中的vdbias改成Pre中的vdbias」
- **U[3] (核心 spec)**: 「做的脚本有要求：传入两个文件夹Pre和Step2，脚本做的内容对Step2下的每个子文件见遍历，找到Pre中对应的文件夹，对比Step2的si.inp的vdbias和Pre中的si.inp的vdbias是否一致，如果不一致，则把Step2的改成Pre中的。」
- U[4]: 询问 --backup 作用
- U[5]: 跑 --apply 后发现 si.inp 被清空(实为误判)+权限变化
- U[6]/U[7]: 报告 si.inp 空文件 + 权限从 -rw-rw-r-- 变 -rw------- (mkstemp 0600 bug)
- U[8]/U[9]: 让 agent 校验已改的 10 个文件夹

## assistant 交付
- fix_vdbias.py: 传入 <Pre> <Step2>, 遍历 Step2 子文件夹, 剥 _step2 后缀找匹配 Pre, 读 .param pvdias= 比较, 不一致则用 tempfile.mkstemp 在同目录写新文件(只替换 pvdias 行)→ os.chmod(tmp, 原 mode) → os.replace 原子替换
- --apply 才改写(默认 dry-run 只打印 FIX current→target), --backup 先 shutil.copy2 存 .orig
- 无 si.inp / 无匹配 Pre 跳过报告不崩溃
- 修了 mkstemp 临时文件权限 0600 bug(改写前 chmod 保持原 mode 0o664)

## 真实参数/值
- pvdias 值: Pre 0.8676, Step2 0.8615 (Bias); 0.873/0.8665, 0.891444/0.883336, 0.9361/0.9295 (CRG001)
- 文件夹: Aging001_step2_10yr_bls, Aging001_step2_3650hr_bls, RDBI_*, Solo_Divider, Divider_and_C2C, WCKTop
- 子文件夹样例: primesim.CRG001_Sec47_24_PRAC_coretiming_SC0_WPre_4s4t_WPst_4p5_tCH50_sc0_2b16g_BLs_11600_FF_FSMSHORT.X2P6_11600.FF1.23V-10C.X2P6_step2

## 合成决策
- A 档 trace-faithful: 用户原话(U[3])作 prompt; 真实行为来自 trace
- reframe harness-for-teeth: one-off 修 /rundata → 参数化通用脚本(任意 Pre/Step2 对)
- hidden B: RX0-4 异 subfolder 名/异 pvdias 值/异目录数 + 边界(无 si.inp/无匹配 Pre) → 验通用性 + anti-hardcode-A
- L1 静态 + subprocess 跑候选(无需 FineSim)
- k=14 断言

## dedup
- ewbyk(tongfanl) 与既有 tongfanl 案例(SkillDocGen/MatrixJobStatusParse 等)主题全异, 非 near-dup
- 本轮另 park 4 个 session: pbkq1/5v4tq/lxzq1(joeyl)=near-dup DelvtoNetlistMod-001; vckxz(joeyli)=C域 Aether
