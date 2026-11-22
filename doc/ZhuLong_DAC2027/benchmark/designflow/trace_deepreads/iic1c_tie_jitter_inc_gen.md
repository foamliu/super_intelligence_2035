# Deepread: iic1c — Tie_jitter HANDBOARD + .inc generator

**session**: 1794297825345_iic1c (joeyl @ hfeg0pkn004 / 10.129.2.13, mc8, spice_sim)
**scan**: ssh_eda_search_20261122_172249
**scp**: /home/joeyl/.cline/data/sessions/1794297825345_iic1c/1794297825345_iic1c.messages.json (181KB, 23 msgs)

## 对话流

- **U0** [act]: 「可以帮忙看下noise_generator中哪些程序是必须的，哪些程序是一次性脚本么？」
  - assistant list_allowed_files → read_files 读 noise_generator/ 7 个文件
  - **分析结论**: 必需 2 个 (generate_noise_pwl.py 参数化 CLI + HANDBOARD.md), 一次性 4 个 (硬编码 /rundata/drgqa/V0/.../2_tt.sp 路径, inspect_tb.py 等)
- **U8** [act]: 「行，直接删掉就好，另外，我还把一个Tie jitter生成程序迁移到/home/joeyl/Tie_jitter了，可以仿照noise_generator写一个handboard么？需要确保新的AI能够直接执行该程序。有需要讨论的部分请直接与我沟通，不要擅自决定或简化功能」
  - assistant skills(写规范) + read_files(Tie_jitter.pl 110 行被截断) + 补读 + run_approved_command(删一次性脚本)
  - **发现 3 处注释/行为不一致**, ask_question 与用户讨论
- **U22** [act]: 「改注释不改行为：修正 Tie_jitter.pl 头注释和 tie.cfg 使文档与代码一致，HANDBOARD 按实际行为写」
  - assistant 交付 HANDBOARD.md + 修正后的 Tie_jitter.pl/tie.cfg

## Tie_jitter.pl 核心机制 (301 行 Perl)

- **CLI**: 3 等价形式 — `perl Tie_jitter.pl <cfg>` / `<cfg> <out.inc>` / `gen <cfg> <out.inc>`
- **config 5 必需键** (key=value, `#` 注释, key 大小写不敏感): signal(逗号分隔), delay, speed(Hz, T=1/speed), count, vthr(数字或带单引号 HSPICE 表达式)
- **signame 推导**: signal 最后一个 `.` 后的段 (xi_io_dqrcv.dqsummerout → dqsummerout); 冲突 die
- **.inc 结构**:
  1. `.param vthr / tper / t0`
  2. `vref_tie n_tie_ideal 0 pulse(0 vthr t0 1p 1p 'tper/2' tper)` — 理想参考时钟(内部节点, 不接被测电路)
  3. 每信号每沿: `.measure tran tie_<name>_<i> trig v(n_tie_ideal) val=vthr rise=<i>` + `+ targ v(<signal>) val=vthr rise=<i>`
  4. 中间统计: tie_sum / mean_tie / tiedev / tiedev2 / tiedev2_sum
  5. 末尾集中: `rms_tie_<name>` = sqrt(tiedev2_sum/count) (de-meaned) + `rms_tie_raw_<name>` = sqrt(Σtie²/count) (raw)
- **只用 trig/targ** (HSPICE/FineSim 均兼容, 不依赖 cross/from/to)
- **parse_num**: 支持 HSPICE 后缀 t/g/meg/k/m/u/n/p/f/a + 科学计数法

## reframe 决策

取**核心工具(.inc 生成)**做 **L1 Python 复刻**: 实现 `tie_jitter_inc_gen.py` 读 config 生成结构正确的 .inc。
- 不做 HANDBOARD 文档题(check 难有牙); 不做注释一致性题(主观)
- .inc 生成结构高度可验证(12 条独立断言)
- A = joeyl 真实 config (4 DQS, delay=5n, speed=2E9, count=500, vthr=0.4375)
- hidden B = 5 重 anti-hardcode: 3 信号(含 '.' 层级路径 xi_clk.rx_clk_n 等) / delay=12n / speed=4E9 / count=200 / vthr='vddq/2' (表达式 vs 数值)
- check 12 条: zip+size / B exit0+.inc / .param 三键 / vref_tie pulse / trig 计数==count×信号 / B 信号路径在 targ / tiedev2_sum / rms_tie+rms_tie_raw / de-meaned vs raw 公式 / anti-hardcode(vthr expr quoted + A 0.4375 absent) / anti-hardcode(max idx==B count + A 500 absent) / 3-seed 确定性

## 自验

- REF: 12/12 PASS ✓
- 3 negs (空壳/硬编A/删核心-rms): 全 FAIL ✓ (分别击中 a-b / f-g-h-i-j-k / g-h-i)
- §4.9 三假 (a)空壳(b)硬编码A(c)删核心 全 FAIL ✓
- case = EDA-Eval-DesignFlow-TieJitterIncGenProduce-001, k_rationale=12=k_check=12

## 原始文件 (scp 自 .75)

- Tie_jitter.pl (301 行) — 原始 Perl 程序
- tie.cfg (54 行) — joeyl 真实 config 样例
- HANDBOARD_tie.md (262 行) — assistant 交付的手册
- HANDBOARD_noise.md (333 行) — noise_generator 手册(参考模板)
