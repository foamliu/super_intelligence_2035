# trace deepread — 38qa0 xmelab CUVPOM 端口错误诊断

## trace 元信息
- session: 1793940867344_38qa0 (e0039602 @ hfeg0pkn004)
- messages.json: 432KB, 73 msgs, mtime Nov 6 13:26 (dir-based)
- spice keyword matches: 803
- 选取路径: 11-05 重扫令 hfeg0pkn004 cron 盲区 _nil 212 候选, 上轮(18:0x)peek 10 选 873cy 后, 本轮取已 peek 的 38qa0(sp=803, 未 reject/未用)

## 用户轮（逐字）
- U#1 (idx=0, len=32268): 粘贴 127 行 xmelab CUVPOM 报错日志 + 末行「我刚刚跑仿真这个报错是什么意思」—— **提出需求/目标, 无根因/修复 → A-档选轮 ✓**
- U#2 (idx=1): 同 U#1 重复粘贴
- U#3 (idx=29, len=219): 「这里的simlib_drcoa_digital.sv是由 /home/e0039602/Documents/verilog_lib_trans_v2.2/outputs/AIout1106 生成的,是错误的, /home/e0039602/Documents/verilog_lib_trans_v2.2/outputs/AIout 是正确的,请你对比两者的写法有什么区别」—— **给出根因方向(AIout1106 错/AIout 对), 不入 prompt**

## 金标准（assistant 最终分析, idx=72）
xmelab elaboration 阶段报 CUVPOM 后 ELBERR/RUNERR 退出。
- 127 CUVPOM *E: 端口名 'vss_'(64 次, col 107) / 'vcc_'(63 次, col 95) of instance '...FwdM' is invalid or has multiple connections
- 全部 127 条实例后缀 = FwdM; 64 个去重实例层次(每个 FwdM 出 2 条: vss_+vcc_)
- 源: ./libs/simlib_drcoa_digital.sv:1056
- + ELBERR(elaboration 退出) + RUNERR(xrun 退出)
- 根因码 = CUVPOM(频次最高非退出 *E)
- 深层根因(对比 AIout/AIout1106): 正确版 AIout.sv 前向锁存级用传输门 passg_base(无 vcc_/vss_), 错误版 AIout1106.sv 被 AI「重建」为 inven_base FwdM(强接 .vcc_/.vss_), 而 inven_base 不定义 vcc_/vss_ 端口 → CUVPOM。FwdM/FbM/DrvM 各 5 处(passg_base 23→24, inven_base 125→103, inv_base 644→537)

## A-档合成
- prompt = U#1 逐字(报错日志 + 「我刚刚跑仿真这个报错是什么意思」)+ 真实场景说明
- A_xmelab.log = U#1 逐字 130 行(127 CUVPOM + ELBERR + RUNERR + 1 问句)
- task_brief.md = 交付接口(≤3 行): analyze_xmelab_cuvpom.py <log> -o <out.json>, 13 个输出键
- 金标准 = 日志结构化诊断(从日志可自洽达成, 不需 U#3 的文件对比)

## 判分设计 (k=16, a-p)
- 通用化 analyze_xmelab_cuvpom_ref.py 解析任意 xrun/xmelab 日志 → {total_lines, error_summary, total_errors, cuvpom_count, invalid_ports, port_columns, instance_suffix, distinct_instances, source_locations, failed_stage, exit_errors, root_cause_code, exited}
- hidden B = 合成 CUVPOM 日志(结构不同): 36 CUVPOM(gnd x18 col100 / vdd x18 col88), 全 DrvM 后缀, 18 去重实例, ./libs/simlib_gate.sv:2048 + ELBERR + RUNERR, 39 行
- 16 断言: a zip含.py b py_compile c B运行exit0写out.json d dict含13键 e total_lines==39 f error_summary非空计数>0 g total_errors==38 h cuvpom_count==36 i invalid_ports=={gnd:18,vdd:18} j port_columns=={gnd:100,vdd:88} k instance_suffix=={DrvM:36} l distinct_instances==18 m source_locations==[{simlib_gate.sv,2048,36}] n failed_stage==elaboration&exit_errors含ELBERR+RUNERR&root==CUVPOM&exited==True o 交叉输入守卫(A: 129/127/{vss_:64,vcc_:63}/{FwdM:127}/64) p 3次幂等sha256 + 无A专属串硬编码
- negatives: naive_hardcode_a(FAIL e) / print_expected_b(FAIL o) / empty_shell(FAIL c) / core_deleted(FAIL h) — 4 distinct

## 自验
- ref PASS 16/16 ✓
- 4 neg ALL FAIL distinct(e/o/c/h) ✓, NEG_RC=0 ✓
- §4.9 三假(空壳=empty_shell FAIL c / 打印期望=print_expected_b FAIL o / 删核心=core_deleted FAIL h)全 FAIL ✓
- 断言闸门 k_rationale=16==k_check=16≥8 ✓
- jsonl test==disk check.py roundtrip sha 3a1be1316cdb0496fd8cdc7950a3e4ebf43ba32a32fbb1177b2678b6c4ba79fc ✓
- jsonl B 182→183, mark ledger(184→185 covered, spice_sim 145→146)

## 与 873cy(XrunLogErrDiag) 的区分
- 873cy: CUVUNF(缺失接口字段) 诊断, 输出 missing_fields; 根因=monitor 引用不存在字段
- 38qa0: CUVPOM(无效端口名) 诊断, 输出 invalid_ports/port_columns/instance_suffix/distinct_instances; 根因=实例化单元不定义 vcc_/vss_ 端口
- 不同错误码、不同根因模式、不同输出 schema(CUVPOM 端口级 vs CUVUNF 字段级)
