# r1123 deepread: 6mbnf — HSPICE 模型库 Rev05→Rev06 diff 断言核验

- **trace**: `1795415354499_6mbnf.messages.json` (ziangw@hfeg0pkn001, mc274, 159msgs/1.12MB)
- **session path 坑**: 文件在子目录 `/home/ziangw/.cline/data/sessions/1795415354499_6mbnf/1795415354499_6mbnf.messages.json`（session id 即目录名），直接 `/sessions/<sf>` 找不到，需 `find ... -name '*6mbnf*' -ls` 定位。
- **真实任务流**:
  - U#0: 对比 `/apps/imctf/models/35H/model_local/35H_DBCFS_Model_PF_v0d1_Rev06/hspice/` vs `...Rev05/hspice/` 差异（递归 diff 两目录）
  - U#26: 聚焦 model.lib 的 DBC 段差异
  - U#38/44: 拿另一 AI（Windows 端、只能看用户粘贴的文本）的 7(model.lib)+8(model_setup_dbc.lib)=15 条 diff 断言清单，逐条回到服务器原始 .lib 文件核验，输出 ✅/❌/⚠️ 报告
  - U#157: "不要在查了 回报一下目前的结果" → U#158 最终核验报告（14/15 正确，1 计数笔误，1 小遗漏）
- **assistant 行为**: 前 25 msg 正常（list_allowed_files + 自写 compare_rev05_rev06.py 递归对比 + 三轮定向 diff）；U#38 后陷入 read_files 循环 bug（反复读 corner/dbc|fs/*_cor.lib L46-50 共 ~30 次，msg 75-155），最后 U#157 用户叫停才出报告。
- **reframe**: trace 的有效意图 = HSPICE .lib 结构化 diff 断言核验器。抽 5 类可解析断言：vt_families（`*_default` include 提取 VT 家族计数）/ section_presence（`.lib <name>` section 存在性）/ include_in_section（`.lib '<path>' <sec>` 引用存在性）/ param_in_section（`.param <p>=` 存在性）/ totalmod_count（`totalmod_*=0` 行计数）。verdict = confirmed/partial/refuted。
- **case = EDA-Eval-DesignFlow-HspiceLibDiffClaimVerify-001**（L1 纯 Python，k=12 a-l）
  - **A**(faithful Rev05→Rev06): 8→4 VT 家族(svt/mvt/lvt/llvt/ulvt/elvt/io12/mos_esd → svt/lvt/ulvt/elvt)，rnd_mc+mc_flag，globalmc/globalmc_localmc/tt_ind section 新增，var12_tt 删除，ttg totalmod 16→8
  - **hidden B**(五重 anti-hardcode): 6→3 VT 家族(svt/mvt/lvt/ulvt/elvt/io33 → svt/lvt/ulvt)，mc_global+mc_enable(异 A 的 rnd_mc/mc_flag)，mccorner/mclocal/tt_cap section(异 A 的 globalmc/tt_ind)，var33_tt(异 var12)，ttg totalmod 12→6。verdict 模式异 A：c1 partial vs A confirmed、c7 partial vs A confirmed、c9 confirmed vs A partial。
- **自验**: REF 12/12 PASS；§4.9 三假(empty_shell→c/print_only_hardcode_A→d/core_removed→i)全 FAIL；negative_selftest PASS；3-seed sha256 ✓。
- **台账**: 6mbnf claim→mark case ✓（顺带修了 5ew0s 的 stale claimed→case）。
