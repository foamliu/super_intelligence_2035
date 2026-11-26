# Deepread: genvz — emy2netlist CDL extraction (adaml @ 10.129.2.11)

- **session**: 1793857741122_genvz (adaml @ 10.129.2.11 / hfeg0pkn002, mc 183)
- **keywords**: netlist:831 aether:707 lvs:430 schematic:375 lib.defs:283 pyaether:260 calibre:254 verilog:106
- **tools**: 495 netlist, 332 schematic, 224 calibre, 131 pyAether, 16 hspice
- **结构**: 98 msgs / 55 user / 43 assistant。真实用户任务轮 = msg#23。
- **U#0** = `<skill_instructions name="calibre-lvs">` (HLMC 22nm Calibre LVS skill 触发，非任务)
- **U#23**（真实任务）: 「[calibre-lvs] /proj/drvsa/V0/workdir/kaixuanx/4PGen_Sleep/Idle_enable 用API接口 emy2netlist试试看抽取上面这个cell的CDL，这次是eather的EDA」
  - 意图：用 Aether (pyAether) 的 emy2netlist API 把 cell 4PGen_Sleep/Idle_enable 的 schematic 抽成 CDL 网表，供 Calibre LVS 用。
- **U#56** = `<skill_instructions name="ai-skill-optimizer">` (任务后自省优化 skill，非任务)
- **assistant 工具链** (msg#1-55):
  1. skills(eda_agent) → RAG search emy2list/emy2netlist → search_codebase
  2. run_approved_command(grep_aether.py) grep /apps/imctf/cad/init/settings_aether/python_ae/
  3. SandBox run_code: 在 pyAether 沙箱里找 emy2netlist 定义 → 命中 `cxmt_schematic_batchGenerateCDLNetlist.py`
  4. 读 `leGlobalVariables.cdlIncFile` = `/apps/imctf/runset/calibre/cxmtG6_1C2A/current/common/empty_device.spi`
  5. 建 runDir `/proj/drvsa/V0/workdir/adaml/emy2list_Idle_enable`，写 lib.defs（DEFINE 4PGen_Sleep）
  6. 跑 emy2netlist → 排坑：库找不到(cwd lib.defs) / Unbound instance MN1/MP1(缺 INCLUDE /proj/drvsa/V0/lib.defs 的 TECHLIB/basic) / -ignoreCheck 无效
  7. 拷贝完整 kaixuanx lib.defs → RC=0 `Successfully exported design 4PGen_Sleep/Idle_enable/schematic!`
- **真实产物**: `/proj/drvsa/V0/workdir/adaml/emy2list_Idle_enable/Idle_enable.cdl` (2439 字节)。assistant 在 msg#55 贴出顶层网表：
  ```
  .SUBCKT Idle_enable DLLLock Idle IdleB IdleEN LMDone ReadEN VDD VSS
  *.PININFO DLLLock:I Idle:O IdleB:O IdleEN:I LMDone:I ReadEN:I VDD:B VSS:B
  XI0 DLLLock LMDone VDD VSS net5 / nand_x1
  XI1 net5 ReadEN VDD VSS net3 / nor_x1
  XI2 net3 IdleEN VDD VSS IdleB / nand_x2
  XI3 IdleB Idle VDD VSS / inv_x2
  .ENDS Idle_enable
  ```
  子电路 nand_x1/nor_x1/nand_x2/inv_x2 全部展开（含 ptn_lv_pc60/ntn_lv_pc60 器件 W/L/nf），.INCLUDE empty_device.spi。
- **关键命令（可复现）**:
  ```bash
  emy2netlist 4PGen_Sleep Idle_enable schematic \
    -t cdl -ntlviewlist auCdl schematic -ntlstoplist auCdl \
    -o Idle_enable.cdl -resThrhd 2000 -pow VDD! -gnd GND! -pin \
    -cdlIncFile /apps/imctf/runset/calibre/cxmtG6_1C2A/current/common/empty_device.spi
  ```

## A-faithful 判定
- ✅ U#23 是 clean produce（用户提需求，未给根因/修复）。
- ✅ user-accepted 产物存在（Idle_enable.cdl, RC=0, assistant 报 Success）。
- ❌ 真实 /proj/drvsa/V0/workdir/adaml/... 属 adaml 私有，e0031982 ssh 读 → EXIT=1 permission denied（已验证，同 #353 cuij 模式）。
- ❌ live Aether emy2netlist 不可移植（需 kaixuanx lib.defs + /proj/drvsa 库 + Aether license）。
- → **B 档 synthesized**：CDL 网表生成器（gen_cdl_netlist.py --spec <spec.json> --outdir），spec 描述 cell/pins(含方向)/instances(subckt or mos)/subckts(subckt 定义含 MOS 器件)，生成器产 <cell>.cdl（.SUBCKT/*.PININFO/XI|M 行/.ENDS/展开 subckt/.INCLUDE）。check 验 CDL 结构（拓扑/方向/实例/master 绑定/跨输入/确定性），不跑 live Aether，L1 离线可验。

## 合成 plan
- **A (visible)** = Idle_enable（真实顶层）：8 pins (DLLLock:I Idle:O IdleB:O IdleEN:I LMDone:I ReadEN:I VDD:B VSS:B)，4 XI 实例 (nand_x1/nor_x1/nand_x2/inv_x2，真实连接)，4 stdcell subckt 展开 (ptn_lv_pc60/ntn_lv_pc60 MOS)，.INCLUDE empty_device.spi。
- **hidden B** = DataClkGate（不同 cell/不同 masters）：6 pins (CLK:I EN:I RSTN:I GCLK:O VDD:B VSS:B)，2 XI 实例 (oai21_x1/inv_x1，全新 masters 不在 A)，subckt 展开含 MOS。
- **hidden B2** = InvRaw（MOS-only 分支）：4 pins (IN:I OUT:O VDD:B VSS:B)，2 M 实例 (MP0 ptn_lv_pc60 / MN0 ntn_lv_pc60)，无 XI、无 subckt def。测 mos 分支（不输出 M 行者 n/l FAIL）。
- **反硬编码轴**: cell 名 (Idle_enable/DataClkGate/InvRaw)、masters (nand_x1/oai21_x1/ptn_lv_pc60)、pin 名 (DLLLock/CLK/IN)、实例数 (4/2/0 XI)、结构 (subckt vs mos) 全不同。
- **check 16 条件 a-p**: zip 结构(no leak) / py_compile / B 真跑 subprocess / .SUBCKT header(cell+pins) / *.PININFO(全 pin+方向) / .ENDS / XI 计数 / XI masters / XI 连接 / subckt 定义齐全 / 无 unbound master / MOS M 行(B2) / 跨输入 A(Idle_enable 顶层) / 跨输入 B2(纯 M 行 0 XI) / 3 次确定性 sha256 / 反硬编码(源码无 A 标记)。
