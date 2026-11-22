# r992 deepread — kyu2s (cliu@hfhds221) — xrun tran-IOPATH crash diagnosis

## Trace identity
- session: `1794794874395_kyu2s.messages.json` (cliu@hfhds221 / 10.129.32.105, mc78)
- keywords: verilog:1699;netlist:487;drc:25;cadence:25;analog:19;transistor:15;cmos:14;lvs:10;... → **A-pure verification** (verilog 压倒性主导, drc/lvs 极低)
- 84 msgs, 3 干净用户问 (act mode), NEW user cliu (首次使用)
- scp 625KB messages.json (ssh e0031982@hfhds221 身份)

## 用户真实意图 (逐字, 3 轮)
- U#0: 「帮忙分析下面路径中sim fail的原因@/home/cliu/xrun_debug/d6/xrun.log」
- U#17: 「帮忙定位下哪个cell写的不对导致的」
- U#63: 「根据提示已经修正了对应cell还是仿真fail」

## trace gold (agent 诊断结论)

### 崩溃签名
- `xmelab: *F,INTERR: INTERNAL EXCEPTION` / `MESSAGE: sss_hname - no pib`
- 发生在 AUTOMSIE 的 **Channel 分区** elaboration (worklib.Channel:verilog -SNAPSHOT Channel)
- backtrace: `tim_dotiming → tim_posttchk (×2) → sbl_process_tran_to → sss_hname → serror/vserror`
- 退出: `xrun: *E,ELBERR ... status 255` + `xrun: *E,RUNERR ... status 1`

### 运行配置 (关键)
- `xrun -automsie -msie_usepartitionfile partition.txt -primtop V0_DDR6TOP -sdf_cmd_file sdf.cmd -USESDFX -negdelay -xmsdf_verbose`
- 9 个 primary partition (Array2G_PSD0/PSD1, Channel, Array32GTop, PhyTop, DQTop, ACBuf, ZQCal, DLLTop)
- POST 网表级 + SDF 后仿
- 复用旧 partition.txt (日志 `Using exiting partition file`)

### 崩溃前奏 (告警刷屏)
- `*W,SDFIEIN`: port `...I_AbusDrvWPU_T_1.D` "has interconnect sources in another MSIE partition. Using MAXIMUM of all source delays" (3000+ 条, 跨分区 interconnect 延迟)
- `*W,TRNSCP`: "Ignoring IOPATH delays (...), output driver ...D of the tran network and IOPATH source ... in different scopes" (跨 scope/分区 tran 网络 IOPATH)

### 根因 cell 写法 (AbusDrv, simlib_dscqa_digital.sv)
```systemverilog
module AbusDrv ( Pdn, PupN, Y, ..., D, S);
    trireg (medium) #(1,1,100) Y;          // ① Y 是 trireg
    nn  M29 (.D(Y), .B(inh_vbn), .G(Pdn), .S(inh_vss));   // ② 开关 nn/pp 驱动 Y
    pp  M31 (.D(Y), .B(inh_vbp), .G(PupN), .S(inh_vcc));
    fgc_pwrstate_monitor ISPMONITOR4 (...);  // ③ 电源监视 tran 也挂 Y
    specify
        (D => Y) = (tFRise, tFFall);         // ④ 在 tran/trireg 驱动的 Y 上加 IOPATH (错!)
        (S => Y) = (tFRise, tFFall);
    endspecify
endmodule
```
问题: **把 SDF/path-delay IOPATH 加在 tran/trireg 开关网络驱动的输出 Y 上**, MSIE+SDF 不支持.

### 主责 cell 族
- `BCDbusDrvWPU_T` (实例 `I_AbusDrvWPU_T_1`) — SDFIEIN 刷屏来源 (DQ 总线写上拉)
- 同类: `AbusDrvWPU_T`, `AbusDrv` (源), `T_PMinvLVx1pgP/N` (`I0.genblk2.m2.D`/`MN0.D`), `T_invLV_pc60x1pgP_PM`, `T_invLVIOx1pgN_PM` (`_PM` 电源监视逆变器), `T_PMinvGFx1pgNI`, `ChanPSDBufBot` (I152/I154), `SplatsqLx2`/`latsqLx2` (I0.clk)
- 带 `fgc_pwrstate_monitor` 实例在 6 个库 ~1.3 万处 (analog/array/digital/io/stdcells/stdcells_ac)

### 为什么"改一个 cell 还 fail" (U#63 回答)
- 3 次重跑 (10:16/10:31/10:45, PID 29021/30714/32188) 全部在 Channel_mkprim 同一 `sss_hname - no pib` 崩, 栈仍是 `tim_dotiming→tim_posttchk→sbl_process_tran_to→sss_hname`
- 用户改的 DQ WPU 生效 (Channel DQ-Mux TRNSCP 少了), 但崩溃挪到下一批同写法 cell: `_PM`/PMinv 逆变器, `DccOscDutyAdjStgIP` (VST dump 反复出现, 带巨大条件 IOPATH), `dlyg2*_gut*` (带 fgc_pwrstate_monitor ISPMONITORs)
- 结论: **不是单 cell 问题, 是整库"tran 网络 + specify IOPATH"写法普遍存在**, 改一个只是让崩溃挪到下一个

### fix 建议
- 运行级验证 (最快): 去 `-negdelay` (sbl_process_tran_to 由 negdelay/SDF 触发); 或去 `-automsie` 单进程跑; 或 sdf.cmd 只对数字 stdcell 标 SDF 跳过模拟/IO 驱动 cell
- 真修 (长期): 不要把 `specify (X=>Out)=(tRise,tFall)` 加在开关/tran/trireg 驱动输出 net 上; 改生成器脚本批量重生成 (这些 cell 是批量生成的, 时序是 `*`CDLYW` 占位默认值)

## case 合成

**case_id**: EDA-Eval-DesignFlow-XrunTranCrashDiagnoseQA-001
**domain**: verification (debug-Q&A → diagnose produce-task)
**形态**: produce-task + hidden-B, A档 trace-faithful

**脚本**: `diagnose_xrun_crash.py <xrun_log> <output.json>` → 结构化 JSON (15 键)
- 解析 *F,INTERR + MESSAGE → fatal_error{code,message,line_number}
- worklib.<PART>:verilog → crash_partition
- backtrace block → crash_stack (含 sbl_process_tran_to)
- *W,SDFIEIN/*W,TRNSCP 行单引号串 → driver paths → counts + distinct
- leaf 实例 I_<Cell>_<num>.<pin> 正则 → root_cause_cells + primary_cell (频次最高)
- root_cause_pattern = tran_switch_iopath (stack 含 sbl_process_tran_to + TRNSCP>0)
- is_pattern_wide = distinct_drivers>3 (回答 U#63: 单 cell 修无效)
- fix_approach: specify IOPATH + negdelay/automsie

**A** (可见): xrun_A.log — Channel 分区, 主责 BCDbusDrvWPU_T, 18 SDFIEIN + 13 TRNSCP
**hidden B**: xrun_B.log — Array2G_PSD1 分区, 主责 DccOscDutyAdjStgIP, 10 SDFIEIN + 8 TRNSCP (同 root-cause 类, 全 concrete 值异于 A)

**check.py**: 23 断言 (①-㉓), 含反硬编码 (B partition/cell/counts ≠ A), 反泄漏 (B root_cause_cells 不含 AbusDrvWPU_T), §4.9 三假 FAIL (空壳/print-A值/core-deleted), 确定性 3×md5
**ref**: PASS 23/23, 3 neg 全 FAIL (neg_empty/neg_print_only_A/neg_core_deleted)
**A.jsonl**: 451→452
