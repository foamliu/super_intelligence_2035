# deepread: lnkot — FSDB SpfBA+PowerFill waveform catalog (jackjia@hfeg0pkn002, mc=535)

trace: /home/jackjia/.cline/data/sessions/1794143890547_lnkot/ (450 msgs, 245 user / 205 assistant, 2.38MB)
domain: waveform (DRAM FSDB 波形目录编目)
date: 2026-11-08

## 用户意图链（produce 轮）
- U#211: "我现在想要利用现成仿真文件 /rundata/drcoa/V0/simdir/finesim/drcoaF/MatrixRun/MatrixRun_Netlist_SpfBA_..._PowerFill_.../primesim.Writeleveling004_.../raw 每种下面都有fsdb 所以我们的rundata/drgqa/也是同..." → 要在 drgqa 对应 rundata 下找可用 fsdb
- U#251: "MatrixRun_Netlist_SpfBA 要这种" → 只要 SpfBA 类
- U#264: "要求不多大概是writelatancy或者gap可以用的就行" → 筛 Writeleveling/gap
- U#297: "/MatrixRun_Netlist_SpfBA 加上PowerFill的 限制" → SpfBA + PowerFill 双过滤
- U#303: "Write Latency +Golden001这条吧" → 在 SpfBA+PowerFill 下取 Writeleveling + Golden001

→ **最终 produce**：解析 fsdb.list 清单 → 过滤 MatrixRun_Netlist_SpfBA_* + 名含 PowerFill → 在这些 run-dir 下取 Writeleveling 和 Golden001 的 fsdb 路径 → 发路径给用户。

## 关键产物（agent 真实工具链）
- 发现 `/rundata/drgqa/V0/simdir/finesim/drgqaF/MatrixRun/fsdb.list`（58329 行，项目维护的全量 fsdb 清单）
- 写 shell 脚本 `fsdb_spfba.sh`：grep '^./MatrixRun_Netlist_SpfBA_' → 25886 条 SpfBA fsdb，454 个 run-dir
- `fsdb_wlgap.sh`：grep write/gap/latency → Writeleveling001/002/003、Golden001、Multi8bank、Timing 等
- PowerFill 过滤：run-dir 名含 `PowerFill`（如 `SpfBA_20251212PM_Fullchip_PowerFill_V1_Aging_10yr_Step2`、`SpfBA_20260203PM_Fullchip_Array2G_PowerFill_Twincell`）

## fsdb.list 行格式（真实）
```
./MatrixRun_Netlist_SpfBA_<date>PM_Fullchip_<variant>/primesim.<TestName>_<corner>.fsdb
```
- TestName: Writeleveling001/002/003, Golden001/002/003/007, Multi8bank001/002/003, DFT, Timing001-009, odt001, PPR001, raw, finesim
- corner: SS0.94v-40C / FF1.3V130C / TT0.94v25C / SS1 / TT1 / FF1，后缀 X4/X8/X16
- 非目标 run-dir：MatrixRun_Netlist_Vcap(27161) / SpfIN / IDD / cfgIDD（干扰项）

## 合成决策（B-grade synthesized）
- 私有 rundata（NFS + 权限）不可复刻 → B 档合成
- A: ~280 行合成 fsdb.list（真实格式，含 SpfBA/PowerFill/非SpfBA 混合 + Writeleveling/Golden001/Multi8bank/DFT/raw 等测试）
- 隐藏 B: 不同 run-dir/日期/测试/计数，反硬编码
- SUT 交付 `fsdb_catalog.py`（CLI 解析清单 → JSON：total_lines / spfba_dirs / spfba_powerfill_dirs / writeleveling_fsdb / golden001_fsdb / writeleveling_golden001_dirs）
- check.py 12 条件 a-l：跑通B出JSON/六顶层键/total_lines对/spfba_dirs只含SpfBA且计数对/powerfill子集+名含PowerFill/writeleveling路径在powerfill下且含Writeleveling/golden001同理/wlgolden001_dirs=既有Writeleveling又有Golden001的powerfill dir/跨输入B计数不同且B集合正确/确定性sha+源码无A硬编码
