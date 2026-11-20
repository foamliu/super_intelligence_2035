# 深读：xppi3 (FsdbMeasRun-001)

- **trace**: 1792551168500_xppi3.messages.json (zongjiuh @ hfeg0pkn001, mc=71, domain=waveform)
- **全文深读**: 见 EDA sandbox session `default_designflow_shardD-427_0` workdir 下 peek 文件 `xppi3.msg.json`（119 msgs, GLM-5.2）
- **任务**: 在 1.4GB FineSim .fsdb 波形（CAS Read sec28 mat0）上跑独立 HSPICE measure 脚本 `cas_rd_sec28_mat0.sp` 的 `.meas tran` 语句集，不重跑仿真，产 `.mt0`
- **trace 关键路径**: U#0 调 finesim-fsdb-reader skill → U#39 给 measure script + fsdb → agent 写 run_meas.py / run_meas_on_fsdb.py / launch_nohup.py 试 fscript `load fsdb` + `meas` → 被 python-runner 全局超时阻断（1.4GB FSDB 太大）→ msg#118 截断无 .mt0 交付
- **资产**: cas_rd_sec28_mat0.sp / finesim.fsdb 在 /rundata/zongjiuh 私有路径，e0031982 无读权限 → B-grade synthesized gold
- **交付**: EDA-Eval-DesignFlow-FsdbMeasRun-001（waveform, B-档 synthesized, L2, k=14, byte-sync sha 6fa9f8f8 size 2973, D.jsonl 238→239）
