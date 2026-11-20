# deepread: 21ltn — Totem-SC run.py 数据流依赖 Q&A

**session**: 1793070301949_21ltn
**user**: thomasz @ hfeg0pkn002 (10.129.2.10)
**match_count**: 17, domain: schematic_netlist (waveform dependency)
**trace**: 37 msgs, 190KB, agent=lead, 2026-10-27

## 用户意图（verbatim）

U#0 (ts=1793070302395):
> /rundata/totem/dscqa/IR/20261017/DDR6TOP_IDD5B_11600_TT1.025v70c_fix_moscap/ 读一下run.py，elmv跑完后的步骤还会用到finesim文件夹下的波形吗

U#19 (ts=1793070741340):
> 我现在有elmv的数据库，但finesim波形被破坏了，会影响到elmv之后的步骤吗

## gold answer (assistant msg#36, 2325 chars)

1. **fsdb 实际状态**: 文件还在 ~12.8GB, companions (.chain/.slist/.xlist/.tlist) 在, 但 mtime(1793069552) 比 elmv 生成时间(1793004138)晚 → fsdb 在 elmv 建好后被改写/触碰 (与 run.log `PrimeSim received SIGTERM` 对应, 推测后一次 finesim 被中断覆盖原 fsdb)

2. **elmv 已物化波形**: `db/elmv/aplmmx_sc/DDR6TOP.spcurrent.spcdb/` 含:
   - `spcurrent.ex` / `.ex.bin` / `.ex.idx` (544/395/150MB) — 电流源波形数据库
   - `uuid2varid.bin` (~1.09GB) — 按变量 id 存波形数据
   - `cdev.bin` + `cdev.net` (451MB) — decap/自定义电流器件模型
   - `Persist.bin` / `PseudoPersist.bin` (4/1.5MB) — 持久化电流数据
   - `aplWaveMgr.config` (第一行 `finesim.fsdb 0 -1 0`, 6.3MB) — 波形管理器注册表
   - `finesim.fsdb` — symlink → finesim 目录原始 fsdb

3. **结论**: 大概率不影响 elmv 之后的步骤, 但有风险:
   - ✔️ 主要流程不受影响: scn/av/pem_dc/rms/peak/data_mining/heatmap (run.py L57-91) 消费 elmv 已物化的 spcurrent 数据, 不重读 fsdb
   - ⚠️ 风险点: aplWaveMgr.config 仍注册 finesim.fsdb 为波形源 + elmv 库有 symlink; 如果下游步骤重新打开波形管理器拉取数据会失败
   - ⚠️ run_fix.py 重建 elmv 时会基于 nlv + aplmmx.config 的 SIM_OUTPUT_FILE 读 fsdb (真实依赖)

## run.py 流程 (92 行)

```
L4-6:  include ttsc_args/setup_server_env/utils
L11:   db = gp.open_db("./db")
L17:   nlv = db.create_device_netlist_view(tag="nlv", **nlv_args)
L23-26: while wait for aplmmx → os.system primesim → -o finesim/.../raw/finesim
L32:   elmv = db.create_electrical_model_view(tag="elmv", device_netlist_view=nlv, **elmv_args)
L38-49: nv/phmv/macro/lv/dv0/dv/ev/tv (base views, elmv 作为 phmv 的 elec_model_view 输入)
L56-58: sv/scn/av (sim/scenario/analysis views, scn 的 electrical_model_view=elmv)
L64-66: pem_dc/pem_rms/pem_peak (EM views, analysis_view=av)
L72:   totem.data_mining("db")
L80-92: node_hm = av.get_node_voltage_heatmap() → write_image_file
```

**关键依赖链**: nlv → primesim(产 finesim.fsdb) → elmv(消费 fsdb 建 spcurrent) → scn/av/pem_*/data_mining/heatmap(消费 elmv, 不直接读 fsdb)

## 资产可达性

run.py + ttsc_args.py 在 trace read_files tool_results 中完整内联 (run.py 5845 chars, ttsc_args.py 11911 chars). 从 trace 重建 asset A, 无需 ssh 源盘.

## 造题套式

code-grounded dataflow-dependency Q&A (套 #254 v2 code-grounded pattern, 同 r789 GuiScriptExplainQA-001 族):
- candidate.py 读 run.py + question → 解析 flow steps (var = db.create_*_view) + os.system sim step + dependency chain → 输出结构化 JSON
- check.py 12 断言: flow_steps≥7 / sim_step含raw / elec_model_step识别 / post_em≥5 / sim_consumers含elmv / conclusion正确 / cited grounded于B / anti-hardcode不泄A标识符 / 3-run确定性
- hidden B = identifier-renamed 同结构变体 (finesim→spcsim, elmv→emv, create_*→build_*, DDR6TOP→TOP6DDR, 零标识符重叠)
