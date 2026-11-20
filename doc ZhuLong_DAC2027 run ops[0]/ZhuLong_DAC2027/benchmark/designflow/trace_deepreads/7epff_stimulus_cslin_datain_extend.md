# deepread: 1794464572535_7epff — SPICE stimulus cslin + Datain<16:31> 扩展

- **session**: 1794464572535_7epff (ghyang @ hfeg0plg93, mc9, eda_other, netlist:52/stimulus:38/datain:24/vcslin:18/cslin:18/spice:14)
- **agent**: lead (r772/r779 教训复用：lead 标签本身 NOT buildability disqualifier；本案 read_files tool_results **含完整文件内容**, editor tool_use 含 old_text/new_text)
- **liveness**: 目录式 session（`1794464572535_7epff/` 含 `1794464572535_7epff.messages.json` 356KB / 58 msgs, agent=lead），ALIVE @ hfeg0plg93 (10.129.8.225)
- **msgs**: 58 (agent=lead), user turn0 是真实意图，其余为 tool_result

## 用户真实意图（单轮原话 verbatim）

> 在这个路径下/proj/ddgoa/V0/workdir/ghyang/DDGOA/有Yiotwist_case5spf*8个文件夹，每个文件夹中有三个stimulus_Pattern*文件，需要你检查里面csl相关的这两行
> vcslin<17> cslin<17> 0 pulse (pvss pvcsl 'tdelay-tdelay1*2' trise trise 'thold-tdelay1*2' tperiod)
> vcslin<16> cslin<16> 0 pulse (pvss pvcsl 'tdelay-tdelay1*2' trise trise 'thold-tdelay1*2' tperiod)
> 按照同样的格式在后面补充vcslin<15>到vcslin<0>的16行；之后在stimulus_Pattern1a3.sp和stimulus_Pattern2a4.sp文件中分别按照各自的规律，仿照现有的16位VDatain信号周期规律，排布16-31的后16位

两件事：
1. **cslin 扩展**（3 个文件都做）：在 `vcslin<16>` 行后按同格式补 `vcslin<15>`..`vcslin<0>` 共 16 行
2. **Datain<16:31> 扩展**（只 1a3 + 2a4，Pattern1.sp 已含完整 Datain<0:31>）：仿各自现有 16 位 VDatain 周期规律排布后 16 位

→ **produce-task: 编辑 SPICE stimulus 文件**

## agent 工具链

list_allowed_files（8 个 Yiotwist_case5spf* 文件夹）→ read_files（3 个 stimulus_Pattern*.sp）→ editor 写 `patch_stimulus.py`（批量 patch 8 文件夹）→ run_approved_command 执行（cslin+Datain 全加，但 1a3 Datain period 漏引号）→ read_files 验证发现 `'tperiod*4)` 漏闭合引号 → editor 写 `fix_quotes.py` → run_approved_command 二次修补 → read_files 验证通过 → 中文总结

## A 资产（SUT 看到，从 trace 重建）

- `stimulus_Pattern1.sp` — 完整 32 位 Datain 参考文件（含 VDatain<0:31> + vcslin<17:16>），只需 cslin 扩展
- `stimulus_Pattern1a3.sp` — 16 位 Datain（VDatain<0:15> + vcslin<17:16>），需 cslin + Datain<16:31> 扩展（按 1a3 自身周期规律）
- `stimulus_Pattern2a4.sp` — 16 位 Datain（VDatain<0:15> + vcslin<17:16>），需 cslin + Datain<16:31> 扩展（按 2a4 自身周期规律）
- `task_brief.md` — 任务说明 + 周期规律推导 + 用户原话

## ground-truth（从 A 原始 0..15 推导，非硬编码）

### cslin<15:0> 格式（与现有 vcslin<17>/<16> 完全一致）
```
vcslin<{i}> cslin<{i}> 0 pulse (pvss pvcsl 'tdelay-tdelay1*2' trise trise 'thold-tdelay1*2' tperiod)
```
i 从 15 递减到 0，追加在 `vcslin<16>` 行后。3 个文件都做。

### Datain<16:31> 周期规律（从 A 原始 0..15 推导）

格式：`VDatain<{i}> Datain<{i}> 0 pulse (pvcc pvss 'tdelay-0.7n+tperiod' trise trise {pw} {period})`

- **Pattern1a3**: delay=`'tdelay-0.7n+tperiod'`, pw=`'thold*2'`
  - period 4 位一组：gs=(i//4)*4；gs∈{16,24} → `'tperiod*4'`；gs∈{20,28} → `'tperiod*2'`
- **Pattern2a4**: delay=`'tdelay-0.7n+tperiod'`
  - gs∈{16,24} → pw=`'thold*2+tperiod*2'`, period=`'tperiod*6'`
  - gs∈{20,28} → pw=`'thold*2'`, period=`'tperiod*2'`

## 真实 trace agent bug（→ neg4 复现）

agent 首次补 1a3 的 Datain<16:31> 时，period 参数漏了单引号闭合：
- 错误：`... 'thold*2' tperiod*4)` （`tperiod*4` 未加引号，且 `)` 前缺 `'`）
- 正确：`... 'thold*2' 'tperiod*4')`

后用 `fix_quotes.py` 二次修补（`re.sub(r"(thold\*2'\s+)tperiod", r"\1'tperiod")` + `re.sub(r"('tperiod\*\d)\)", r"\1')")`）。

## B hidden variant（specificity oracle，不在 SUT sandbox）

- 参数名：`tperiodB=8n` / `tholdB=2.4n`（vs A 的 tperiod/thold）
- 信号名：`vcslx` / `cslx` / `Dqin`（vs A 的 vcslin/cslin/Datain）
- 位域：`Dqin<32..47>`（vs A 的 Datain<16..31>）
- delay：`tdelay-1.5n`（vs A 的 tdelay-0.7n）
- net：`pvcslB`（vs A 的 pvcsl）
- B-only tokens：`Dqin`, `vcslx`, `cslx`, `tperiodB`, `tholdB`, `2.4n`, `tdelay-1.5n`, `Dqin<32>`, `Dqin<47>`, `pvcslB`, `tdelay=35n`
- check.py cond9 断言 SUT 的 A 提交不含任一 B-only token（防背题/防抄 B/防 generic 输出）

## case 产出

- **case_id**: EDA-Eval-DesignFlow-StimulusPatternExtend-001
- **shard**: A (eda_other)
- **k_check = k_rationale = 10**
- **自验证**: ref submit.zip → CHECK PASS 10/10; 5 negatives 全 FAIL (neg1 noop→② / neg2 print-expected→② / neg3 core-deleted→⑤a / neg4 引号 bug→⑤a / neg5 B-leak→⑨); §4.9 a/b/c 全 FAIL
- A.jsonl 392→393
