# r993 deepread — fjy8k (chili@hfeg0pgn145) — Xcelium AutoMSIE 波形 dump 失效诊断

- **session**: `1795078103891_fjy8k.messages.json` (1.0 MB, 156 msgs: 80 user / 76 assistant, 74 tool_uses)
- **user**: chili @ hfeg0pgn145 (10.129.35.244) — NEW user, A-pure verification profile (verilog:577;netlist:237;binary:90;cadence:70;aether:66;vhdl:47;systemverilog:46)
- **match_count**: 157

## User intents (verbatim, mode=act)

- **U#0** (×3 retries same text): 「在环境/rundata/dscqa_sim2/V0/simdir/verilog/chili/verilog.ddr6.dscqa.tbtest中执行仿真/.../run_build时，生成到波形/.../ncsim.shm里波形的worklib.ddr6_package::中到timing参数显示不出值，但是环境display是有值的，请帮我分析下原因」
- **U#36**: 「那么为什么timing里成员的值不对呢？」
- **U#48**: 「第一个方案需要改动的太多了，这不是所有变量都要备份么；帮我研究下方案2怎么实现，应该怎么做」
- **U#146**: pasted `TYPE_odt_param odt_timing = '{...}` struct literal, asked 「这个怎么增加packed」

## Session main thread

DDR6 DScQA 数字后仿 Xcelium (xrun) 环境，`-automsie -xmsienumpartitions 10`，SHM 波形里 `worklib.ddr6_package::` scope 存在但 `timing` 结构体变量成员显示不出值，`$display` 能打印值。Agent 多轮深度诊断。

## Tool chain

`skills(aether-tool-qa)` → `list_allowed_files`×2 / `read_files`×2 (env dir + ddr6_package.sv + probe.tcl + xrun.log) → `SandBox_MCP_Server__run_code`×1 (pyAether 沙箱未启动) → `editor`×34 + `run_approved_command(python-runner)`×33 (迭代 `analyze_wave.py` / `analyze_wave2.py` 解析 ncsim.dsn 二进制 + xcelium 安装树扫描 + PDF 提取)。

## Trace gold (root-cause chain)

1. `ddr6_package.sv:3116` 声明 `(* msie_share *)TYPE_SpecTiming timing;` —— **结构体变量**（非 parameter），带 `msie_share` 属性。
2. xmelab 告警：
   - `*W,IEMTRG (./ddr6_package.sv,3116|41): Object not shared between partitions (timing).`
   - `*W,IEMTRG (./odt_parameter.sv,1|1): Object not shared between partitions (odt_timing).`
   - `*W,IESHPK: [MSIE] Package ddr6_package used in multiple primary snapshots.`
3. `probe.tcl:20` 的 `probe -create ddr6_package::timing -depth all -packed 0` 执行成功（`Created probe 14`）。
4. `ncsim.dsn` (2.7 GB SHM 设计信息文件)：`worklib.ddr6_package::` scope 名字**存在**，但 `TYPE_SpecTiming` 成员名（`ODTLon_WR`/`DQS2DQI_min`/`tWOSCO`/`tODTLon_WR`/`tWPRE`/`tCK2DQO`）**全 COUNT=0**（probe 创建成功但成员没登记进波形数据库）。
5. **决定性发现**：`msie_share` 属性 token 在 xmelab/xmvlog/xmsim/xrun 二进制 + 所有 `.so` + `files/etc/src/share/inca` 配置目录中**完全不存在独立 token**（只有 `cu_msie_shared_package_*` 内部函数名）。SV LRM 规定未知 attribute 被静默忽略 → `(* msie_share *)` 是 no-op。
6. 旁证三连：
   - 兄弟 run (15:08 更早) IEMTRG 列号也是 41 —— 加属性前后告警完全一样。
   - 没加 `msie_share` 属性的 `odt_timing`（`Project/odt_parameter.sv:1` 裸声明）同样报 IEMTRG。
   - `nochip` run（单分区）IEMTRG = 0 —— 问题 100% 与多分区绑定。
7. `timing` 在 tb `$unit` 代码里被引用 ~3600 处（ddr6_timing.sv 1302 / timing_load.sv 1262 / ddr6_test.sv 610 / ddr6_tasks.sv 325）—— 跨分区引用来源。

## Fix (方案2)

- 把 typedef 从 `struct {` 改成 `struct packed {`（TYPE_SpecTiming 254 成员全是 packed 类型含 packed 多维数组 `bit signed [DQ_BITS-1:0][31:0] tCK2DQO`，TYPE_odt_param 26 成员全 int → 整体宽度 832 bit，packed struct 语法满足；3600+ `.member` 访问零改动）。
- **配套**：`probe.tcl` 的 `-packed 0` 改成 `-packed 4096`（否则 packed struct 成员塌成一个大向量不被逐个 dump）。
- 验证：重跑后 IEMTRG 消失 + 波形显示值；若仍报 → fallback 在 TOP 里加镜像变量 `TYPE_SpecTiming wv_timing; always_comb wv_timing = timing;` + `probe -create TOP.wv_timing -depth all`。
- 用户在 session 期间已自行把两处 typedef 改成 packed（ddr6_package.sv mtime 14:00）。

## Distinctness from r992 XrunTranCrashDiagnoseQA

- r992: xmelab `*F,INTERR sss_hname - no pib` **崩溃**（tran/trireg 网络 + specify IOPATH，sbl_process_tran_to）。
- r993: xmelab `*W,IEMTRG` **告警**（非崩溃）+ msie_share 属性不被识别 + probe `-packed 0` 误用 + dsn 成员 COUNT=0。

不同 root-cause 类、不同消息家族、不同 fix 路径，无 intent-dup。

## Case artifact

- task_id: `EDA-Eval-DesignFlow-MsieWaveDumpDiagnoseQA-001`
- domain: verification, A档 trace-faithful debug-Q&A → diagnose produce-task + hidden-B
- k_check = k_rationale = 23, §4.9 三假全 FAIL
- A: ddr6_package / 10 分区 / timing+odt_timing / TYPE_SpecTiming+TYPE_odt_param / ODTLon_WR… / probe ddr6_package::timing -packed 0
- hidden B: arb_package / 6 分区 / config+aux_config / TYPE_Config+TYPE_AuxConfig / CFG_LAT/CFG_VOLT/CFG_MODE… / probe arb_package::config -packed 0 (全 concrete 值异于 A, 同 root-cause 类)
