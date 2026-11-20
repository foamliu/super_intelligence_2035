# Deepread — 1793943889492_yg26n (shanliny @ hfeg0pkn001) · Monte-Carlo .mt0 stats

- session: `/home/shanliny/.cline/data/sessions/1793943889492_yg26n/1793943889492_yg26n.messages.json` (95 msgs / 314KB)
- host: hfeg0pkn001 (10.129.2.10), reachable at 00:5x via .75 ssh
- domain: spice_sim (HSPICE Monte-Carlo 仿真结果聚合), A-档 faithful, L1 (offline Python)
- match_count: 95 (nmsgs proxy; gap-window session not in 11-05 summary)

## USER#0 verbatim (纯需求轮, 给目标+方法, 未给根因/修复 ✓ A-档②合规)
> 我发给你的两个文件，一是1_run，这个是monte仿真执行脚本，里面output_dir注明了结果文件所在的目录，然后io_d0_template_1_50.mt0这是结果文件目录中具体的结果文件名，我希望你能构建一个python脚本，然后像1_run中循环并递进参数投递仿真一样，我能够通过向这个python本中传递参数然后递进地读取每一个mt0结果文件，并统计mt0结果文件中index后七个参数的平均值和标准差(正态分布)，最后在脚本当前目录下生成montesum.mt0文件，里面注明index后所有参数的平均值及标准差

附件: `1_run`（monte 仿真提交脚本）+ `io_d0_template_1_50.mt0`（结果样例）。

## USER#1 (后续增量需求, 不入 prompt, 仅记录)
> 你再帮我集成一个功能，那就是讲这些数据全部抓到xlsx文件中，同时，在这个功能下我可以指定抓哪一个index后的变量
（xlsx 导出 + 选变量；本轮 case 只取 USER#0 核心交付，xlsx 为增量不在判分范围）

## 1_run 结构（真实, shanliny 的 IO_sim/sim_11_3）
- BASE_DIR=/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/IO_sim/sim_11_3
- loop i=1..20: num1=(i-1)*50+1, num2=50*i; 生成 io_d0_template_${num1}_${num2}.sp (sed fromnum/endnum)
- bsub -q lacaa_sram hspice <sp> -o ${RESULT_DIR}/${base_name}/ -mt 8
- 结果 .mt0 位于 ${RESULT_DIR}/io_d0_template_${num1}_${num2}/io_d0_template_${num1}_${num2}.mt0

## .mt0 格式（HSPICE V-2023.12, PrimeSim）
```
$DATA1 SOURCE='PrimeSim HSPICE' VERSION='V-2023.12 linux64' PARAM_COUNT=1
$OPTION MEASFORM=1
$index=1 is a nominal sample in Monte Carlo.
.TITLE ' '
index t_outb_r v_blb_fall1 v_bl_fall1 v_dv v_df_sat_sac v_df_bl_blb v_df_b_s temper alter#
1  1.076125e-06  0.6751653  0.6675309  7.634389e-03 -7.336521e-03 -7.329546e-03  6.974813e-06  -40.0000000 1
...
```
- index 后 9 列 = 7 个测量参数(t_outb_r..v_df_b_s) + temper(常量) + alter#(常量)
- USER 要 "index 后七个参数" → 前 7 列测量参数 (排除 temper/alter#)

## trace 中 assistant 产物
- 写 `/home/shanliny/montesum.py`：mirror 1_run 分块循环 → 定位每个 .mt0 → 聚合 → 对 index 后每列算 mean + stddev(normal) → 写 montesum.mt0。带 `--params N` 选项控制前 N 列。
- 金标准 = USER#0 spec 正确实现：分块发现 + .mt0 解析(跳 $/. 行, header=列名, 数据行 float) + 前 7 列 mean/stdev(n-1) + montesum.mt0 输出。

## 合成计划（便携 A / 隐藏 B）
- A: chunk_size=4, 3 chunks (1-4/5-8/9-12), prefix=io_d0_template, temper=-40, alter=1, 12 samples
- hidden B: chunk_size=5, 2 chunks (1-5/6-10), prefix=io_mc_test, temper=85, alter=2, 10 samples, 不同数值量级
- 交付=通用 `montesum.py --result-dir --prefix --chunk-size --index-start --index-end --params 7 --output`
- check.py 14 断言 a-n: zip 含 py / compile / --help / 跑 B exit0 / 7 参数名齐 / index/temper/alter# 不入统计 / mean t_outb_r 对 / mean v_bl_fall1 对 / stddev t_outb_r 对 / stddev v_bl_fall1 对 / 全 7 mean 对 / 全 7 stddev 对 / nsamples==10 / 跨输入 A≠B
- 自验：REF PASS 14/14 + 5 neg 全 FAIL + §4.9 empty-zip FAIL

## distinctness（防 dup）
- vs VmMhlAlterStats-001：后者 .csv 按 .alter 分组求 min/max/mean；本 case .mt0 分块循环 + mean+stddev(n-1 正态) + montesum.mt0 + --params 7 排除 temper/alter#
- vs McRonMismatch-001：后者 .md0 求 6σ/rpu mismatch 单一指标；本 case .mt0 7 参数 mean+stddev 聚合
- vs DelaySigma-001：后者 sizing 优化；本 case 纯统计聚合（无 sim、无优化）
