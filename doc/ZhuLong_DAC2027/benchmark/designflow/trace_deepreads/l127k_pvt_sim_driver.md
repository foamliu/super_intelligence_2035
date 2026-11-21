# deepread: l127k — shanliny PVT sim driver (1795058492590_l127k)

- **user**: shanliny @ hfeg0plg107, mc=354, spice_sim (aether:538/netlist:443/hspice:254, 无 drc/lvs 噪声 = 纯 spice_sim)
- **session**: 249 msgs / 22 user msgs, 1 轮多回合迭代
- **工作目录**: `/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/racing_check/9_autosim/racing_hd1p/`
- **主线交付**: 重构 `0_run.py` 为 config_pvt.txt 驱动的 HSPICE/FineSim PVT 仿真编排器

## 用户意图（原话时间线）
- U[0]: 看工作目录
- U[17]: PVT_LIST 如何运作（Q&A）
- U[19]: **软链接优化**——「每仿真一个例子就要把网表复制一遍…几十GB大网表徒费空间」
- U[47]: sp 文件声明网表随工艺角变化实则不会变（bug 修正）
- U[103]: **主线任务定义**——config_pvt.txt 格式参数传递 + 网表名(规模名前缀 dspf 参数抽取条件名后缀) + prefix 参数(不传=不仿真/具体名=只仿真该前缀/`*`=全前缀) + RC_CORNER/RC_TEMP 后缀约束 + 前后缀共同满足才仿真 + 每行一种情况 + sp 文件名改 CXN4HC1PS64X8M...
- U[158]: 不要全量仿真验证（耗公共资源），跑一个网表即可
- U[172]: **注释功能**——config_pvt.txt 能注释行不跑 + 多个前缀名怎么输入
- U[174]: **log 目录**——log 文件单独丢 log/ 子目录，别让主目录拥挤
- U[194]/U[196]: 读取文件夹功能效率 + 并行提交 + 旧数据残留清理
- U[222]/U[248]: 跑仿真没启动的 bug 排查

## 关键文件（从 trace read_files 还原）
- `0_run.py` (~935 行): SRAM Characterization 一键启动，CFG 区 + sram_meas_gen 引擎 + per-corner 跑仿真
- `racing_m4b2.sp`: sp 模板，含 `<<PROCESS>>`/`<<spf_path>>`/`<<INST>>`/`<<RC_CORNER>>`/`<<RC_TEMP>>`/`<<VDDP>>`/`<<VDDC>>`/`<<TEMPERATURE>>`/`<<SIM_TIME>>` 占位符；`.inc '<<spf_path>>/<<INST>>.dspf.<<RC_CORNER>>_<<RC_TEMP>>'`；`.option finesim_*`
- `config_pvt.txt`: 8 列 `BITCELL_PROCESS LOGIC_PROCESS VDD VDDP VDDC TEMP RC_CORNER RC_TEMP`（tab 分隔）

## 合成为 case
- **case_id**: EDA-Eval-DesignFlow-PvtSimDriverGen-001
- **A 档 trace-faithful**: prompt 用 shanliny 原话 U[103]/U[172]/U[174]/U[19]
- **harness-for-teeth reframe**: 真实 0_run.py 依赖 sram_meas_gen 引擎 + 真跑 FineSim（无法在离线 check 里验）；reframe 成纯 Python 编排器 `pvt_sim_driver.py`，验编排逻辑（config 解析/前后缀筛选/变量注入/软链接/log 目录/sim_time 派生），不验仿真正确性
- **asset A**: racing_m4b2.sp(真实模板) + config_pvt.txt(4 data line 无注释) + spf_path/(2 前缀×2 后缀=4 网表，PORTS=6/8)
- **hidden B**: config_pvt.txt(4 有效 data line + 2 #注释 + 1 空行) + spf_path/(3 前缀×2 匹配后缀=6 + 2 非匹配后缀 TYPICAL_25/WORST_85 须过滤)，PORTS=4/10/12
- **判分**: check.py 12 条 a..l，B total=12 vs A total=8 anti-hardcode，独立从 B 网表 PORTS 复算 sim_time
- **k_rationale==k_check==12 ✓** (≥8 硬闸门)
