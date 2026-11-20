# 深读: 1790840542058_430uk (mike @ hfeg0plg003 / 10.129.32.80, mc=105)

- **trace_source**: user=mike, host=hfeg0plg003, session_file=1790840542058_430uk, match_count=105, tools=netlist 289 / pyAether 18 / schematic 8
- **NMSG**: 470; 真实 user 轮 19 (其余为工具结果)
- **domain**: analog_context (cosim 仿真激励文件夹脚手架)
- **A-faithful 选轮**: U#0 + U#2 + U#3 均为「提出需求/表达目标」轮（用户描述期望操作 + 补充规格），非根因/修复 → 合规

## 用户原话（逐字）

**U#0** (msg#0):
> /ai_sandbox/dscqa/V0/agentdir/mike/finesim zhege mulu xia youge finesim仿真 的文件夹 ，我接下来想做一件事，/ai_sandbox/dscqa/V0/agentdir/mike/logic_cosim_0929/eddr6_cxsh_20260928 把这个目录下的 .list文件，每个生成一个文件夹，命令用前缀加上 刚才的文件夹；接下来plan模式工作

**U#2** (msg#16):
> 比如DSDM_TRAIN_stimulus.list ，我会把 cankao wenjianjia Vcap_20260924PM_DDR6TOP copy成 DSDM_TRAIN_Vcap_20260924PM_DDR6TOP ，然后 copy后wenjianjiazhongde stimulus.list tihuancheng DSDM_TRAIN_stimulus.list, ranhou ba wenjianjiazhongde  .vec "stimulus.list"  huancheng DSDM_TRAIN_stimulus.list;

**U#3** (msg#18):
> .tran 10ps              95552114ps   还有一步,zhegcanshu xuyao tihuan ,要查看DSDM_TRAIN_stimulus.list ,这个激励最后一行是 89186489 ，单位是ps，我们在这个基础上加上500 000 然后替换掉之前的参数

## 任务理解（从 trace + thinking 还原）

1. **finesim 目录** (`/ai_sandbox/.../mike/finesim`) 含参考仿真文件夹 `Vcap_20260924PM_DDR6TOP/`（内含 `stimulus.list` ~230MB、`sim.sc` 等）
2. **源目录** (`/ai_sandbox/.../logic_cosim_0929/eddr6_cxsh_20260928`) 含多个 `*_stimulus.list` 文件（CA_TRAIN/CS_TRAIN/DSDM_TRAIN/.../ZQCAL，共 ~18 个）
3. **对每个 .list**:
   - prefix = .list 文件名去掉 `_stimulus.list`（如 `DSDM_TRAIN_stimulus.list` → `DSDM_TRAIN`）
   - 输出文件夹名 = `<prefix>_<参考文件夹名>`（如 `DSDM_TRAIN_Vcap_20260924PM_DDR6TOP`）
   - 复制参考文件夹 → 输出文件夹
   - 删除输出文件夹内的旧 `stimulus.list`
   - 把源 .list 复制进输出文件夹（保留原文件名，如 `DSDM_TRAIN_stimulus.list`）
   - 在 `sim.sc` 中把 `.vec "stimulus.list"` 改成 `.vec "<list文件名>"`
   - 读 .list 最后一行（时间戳 ps），+500000，替换 `sim.sc` 里 `.tran 10ps <endtime>ps` 的 endtime

## 为什么 B-grade synthesized

- 真实 `stimulus.list` ~230MB 不可附加；真实 `/ai_sandbox` `/proj` 路径不可附加
- 合成小型 .list（含激励行 + 末行时间戳）+ 合成参考文件夹（sim.sc 含 .vec/.tran + stimulus.list 占位 + run.sh + config.cfg）
- 金标泛化 `gen_sim_folders.py`：CLI `<source_dir> <reference_folder> <output_dir>`，按上述规则处理每个 .list

## case ID: EDA-Eval-DesignFlow-CosimStimFolderGen-001
