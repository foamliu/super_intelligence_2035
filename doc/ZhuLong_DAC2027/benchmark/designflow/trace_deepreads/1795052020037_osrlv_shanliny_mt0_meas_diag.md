# Deepread — 1795052020037_osrlv (shanliny@hfeg0pkn003, mc=121, characterization)

session: `1795052020037_osrlv.messages.json` (65 msgs, 1.09 MB)
host: hfeg0pkn003 = 10.129.2.12
scan: ssh_eda_search_20261119_172105/summary.tsv (B fresh list, truly fresh vs ledger_B at r907)
keywords: hspice:433; aether:194; .def:80; waveview:56; mosfet:46; synopsys:35; netlist:12; transistor:3

## 用户意图流（user messages）
- U0 (act): 「帮我看 /proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/racing_check/9_autosim/racing_hd1p」→ 探索 SRAM racing-check 自动化仿真工作目录
- U8 (act): 「sim_results/CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS/tt_0p75v_25c/finesim_out 下你会看到 mt0 文件有测量失败的地方，结合 fsdb 文件告诉我发生了什么事情」→ 诊断 .mt0 测量失败
- U16: meta-反馈「看文件夹的功能如何，消耗上下文太快」
- U18: 「你改进吧」
- U50 (act): 「[[刷新]]，你说错了，现在会有 fsdb 不过是我刚刚和你说话的时候又跑了一遍而已…现在有 fsdb 了，给我看看 mt0 里有测不出来的是怎么回事」→ 重看新跑的 mt0+fsdb
- U64 (act, 用户纠正根因): 「蠢货，你的 vec 写错了，WM_a 要能测得必须需基于 minm0:g 和 minm1:g 的翻转，你写的东西和 SRAM 存的数据一样那还翻转什么？当然触发不了 meas」

## 关键产物（assistant）
- A7: 完整目录结构分析（SRAM CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS, MUX=4 Bank=2 Words=64 Bits=8 Redundancy=1, WM/RM/Racing/Logic-racing 表征）
- A63: 最终 mt0 诊断报告
  - pass/fail 矩阵: xic0(ll) 全 pass; xic_re(lr→lcrc)/xic_re(rl→rcrc)/xic3(rr) 的 WM_a 全 error; WM_b 与 RM 全 pass
  - 128/512 pass = ll 列; 384/512 fail = lr/lcrc/rl/rcrc/rr 列
  - 根因: .meas 的 WM_a `trig v(cell.minm2:g) val=pwr50 rise=1` (WL 上升沿), `targ v(cell.minm0:g)=v(cell.minm1:g) cross=1` (BT==BB cell 翻转); _a fail = bitcell 从未翻转; WL 脉冲正常(_b 有值)
  - 根因链: vec 驱动 D[7:0]=0x00 → DIN1=DIN2=0 (互补写总线无差分) → 写驱动器无法产生 BL=0/BLB=VDD 翻转条件 → bitcell 不翻转 → WM_a meas 触发不了 → error
- 工具: list_allowed_files / read_files / run_approved_command / skills (WaveView, 但 license down 没看成 fsdb)

## .mt0 文件（从 trace tool_result 逐字恢复）
路径: `sim_results/CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS/tt_0p75v_25c/finesim_out/CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS_tt_0p75v_25c.mt0`
- FineSimPro V-2023.12-1, Generated Thu Nov 19 09:05:42 2026, Hostname hfeg0pkn043, Username shanliny
- 720 测量 (180 wm_a + 180 wm_b + 180 wm_base + 180 rm)
- bank 分组: bk0d/bk0u/bk1d (+bk1d_rr 部分); 列: ll/lr/rl/rr
- wm_a error 132 (lr/rl/rr 列各 bank); wm_b error 0; rm error 0; wm_base error 132 (派生随 _a)
- ll 列全 pass (48 wm_a pass)

## reframe 决策
- 形态: debug-Q&A/诊断（看 .mt0 + fsdb 定位测量失败根因）→ 按任务初衷属合法真实用户意图
- 可便携性: 高（纯 .mt0 文本后处理，不依赖 fsdb 二进制/vec/SRAM 专属知识）
- reframe 成 produce 型参数化 .mt0 诊断器 `mt0_meas_diag.py` (L1)
- hidden B1 = 反相模式 (rm 全 error → rm_read_path_failure); B2 = 真实 A (wm_a lr/rl/rr error → wm_cell_flip_failure); cross-input guard
- 资产保真: mt0_A.mt0 = 真实 trace 恢复的 FineSim .mt0 (非合成), 保留原始 header

## 去重检查
- shanliny 同 user 已有 case: yg26n(MonteMt0Stats), xtse5(MeaNetPathDiag), vxf3o(RcVizTreeAnalyzer), 97z71(WmMt0Diag)
- 97z71 (WmMt0Diag, mc137) 同 shanliny@pkn003, 关键词高度相似 → 近邻风险已查: 97z71 是 WmMt0Diag (不同 case_id), 本 case 是 Mt0MeasDiag (pass/fail 诊断器, 通用 .mt0 分类+根因模式检测, 不限于 WM/mt0 单一测量), 形态不同 (97z71 偏 WM .mt0 单测诊断, 本 case 是全测量 pass/fail 分类+两种根因模式判别). case_id 与形态均不重.
- 与 vincentz VtargetBisecAggregate-001 (.bisec_mt0 vtarget 列聚合+矩阵) 不同 (此为 .mt0 pass/fail 诊断+根因模式).
