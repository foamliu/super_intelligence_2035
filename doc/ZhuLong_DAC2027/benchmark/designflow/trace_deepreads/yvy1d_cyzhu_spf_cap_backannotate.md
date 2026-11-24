# deepread: yvy1d — cyzhu SPF parasitic cap back-annotate

- **session**: `/home/cyzhu/.cline/data/sessions/1795414075340_yvy1d/1795414075340_yvy1d.messages.json`
- **user/host**: cyzhu @ hfeg0pgn124 (mc=140, keywords pex:633;pyaether:6;netlist:6;lvs:5 — pure physical_verify/pex)
- **NMSG**: 242 (133 user)
- **cwd**: `/home/cyzhu`
- **真实任务演进**:
  1. (msg 0-2, 用户重复 3x) 基于 `/home/cyzhu/modify_dum_hbl.py`, 更新一版 SPF (path `.../edge_T.spf_RCC`): 根据 dum BLa 与 BLb 的差距, ①以 BLa 为基准修改 BLb 的 `vss!` 后面的电容 ②把修改后的 BL→vss 电容更新到 `|NET HBL*<*> *` 总电容, 保证与 dum BLa 一致。
  2. (msg 101) 修正: 修改的 BLb 增加的 vss! 电容差值正好 = BLa 与 BLb 的 gap。
  3. (msg 141) 换 base SPF (`edge_T_modify_HBL_v2.spf_RCC`), 再次增加 BLb 的 vss! 电容使差值 = gap, 生成新路径不替换原文件。
  4. (msg 170/194) 在 v2 基础上再叠一层 gap (二次增加电容), 用户给出 252~263 每根线的 BLa/BLb 值。
  5. (msg 222, 关键更正) "不是增加 gap, 是需要分别增加我给的 BLa BLb 的增加量, 我给的是每根线增加的量" → 即每根线 (per-idx) BLa 和 BLb 各自独立增加指定 fF。
- **agent 交付**: `add_ff_v5.py` (msg 229) + `verify_v5.py` (msg 237)。输出 `edge_T_modify_HBL_v5.spf_RCC`, verify 24 条全部 OK (msg 241)。
- **add_ff_v5.py 核心逻辑**:
  - `SRC = edge_T_modify_HBL_v2.spf_RCC`, `DST = edge_T_modify_HBL_v5.spf_RCC` (新路径, 备份 .bak)
  - `ADD = {'BLa':{252:0.19,...}, 'BLb':{252:0.13,...}}` (fF)
  - `net_re = ^\*\|NET (HBL[ab])<(\d+)>\s+([0-9.eE+\-]+)PF`
  - 对每个 target (net, idx):
    - 正增量: 追加 `C{idx}_vss_add_{group} {net}<{idx}> vss!:0 {fF*1e-15:.8e}`
    - 负增量: 已有 vss! 行按比例缩放 (`factor = (old_sum + delta_F)/old_sum`)
    - 更新 `*|NET` total: `new = old + fF*1e-3` (PF)
  - 单位: *|NET total 在 PF (皮法), 电容行值在 F (法拉); 1 fF = 1e-3 PF = 1e-15 F
- **case 合成**: `EDA-Eval-DesignFlow-SpfCapIncrementBackAnnotate-001` (physical_verify/pex)
  - 离线 Python deliverable (纯 stdlib SPF 文件变换, 无需 StarRC/沙盒)
  - `solve.py <input_spf> <config_json> <output_spf>` 读 config.targets, 对每个 (net,idx) 应用增量
  - 公开 A (sample_a): idx 52..63, 12 idx/group, 17 正增量, 混合正负
  - 隐藏 B (env_b): idx 10..20, 11 idx/group, 14 正增量, 不同 idx/量/结构 (主判分)
  - 隐藏 B2 (env_b2): idx 100..105, 6 idx/group, 全正, count≠B (反硬编)
  - k=12 全闸门: ref 12/12 PASS + 4neg (noop/print_only/delete_core/hardcode_a) 全 FAIL distinct
  - §4.9 三假 (空壳/只print/删核心) 全 FAIL; §4.1 hidden 不进 SUT; §4.2 真跑 subprocess on B; §4.5 3-run md5 一致 + 期望值由 config 实算; §4.7 独立临时目录; §4.8 泄漏隔离 (attachments 仅 sample_a 3 文件)
- **区别**: C 域 physical_verify pex/SPF 寄生电容回标首例 (SPF 文件变换子型), 与 ParasiticDiodeBackAnnotate-001 (schematic 反标二极管)/DrcResultsItemCollect-001 (DRC results 解析)/CalibreDrcRunsetPatch-001 (runset patch) 产物/断言/trace 全不同。
