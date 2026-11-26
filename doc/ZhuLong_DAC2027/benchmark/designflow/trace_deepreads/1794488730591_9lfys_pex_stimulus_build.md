# 深读笔记 · 1794488730591_9lfys · SRAM bitcell PEX 后仿刺激文件生成

- **trace**：1794488730591_9lfys.messages.json（e0024852 / hfeg0pkn003 / 10.129.2.12，mc205，schematic:142 netlist:121 hspice:14 calibre）
- **session 格式**：目录式（`1794488730591_9lfys/1794488730591_9lfys.messages.json`，797KB，146 msgs）
- **工具**：get_agent_policy_status×1, list_allowed_files×7, read_files×10, editor×25, run_approved_command×23, ask_question×1

## 用户意图（原话）
「根据这个 /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/CH231_FS_guojing/stimulus_pex_rev06_model_rev04.sp 写一个 CH231_HDT_Bitcell_FS_WiPin.gds 的后仿文件」

## agent 工作流
1. 找参考刺激文件（用户给的 rev06 路径不存在，实际是 rev07：`stimulus_pex_rev07_model_rev06.sp`）。
2. 读参考刺激 + DSPF（`CH231_HDT_Bitcell_FS_WiPin.dspf`，`.SUBCKT hdt_CH231_bitcell VSS WL BLB BL VDD SB S`，6 器件 hdt_*_fs）+ 原理图 netlist（`hd_CH252_bitcell BL BLB S SB VDD VSS WL`，9 测试 cell）。
3. 发现陷阱 1：参考模板 `.include` 了原理图 netlist（例化 hd_CH252_bitcell）+ DSPF，但**从未例化 PEX 子电路**——寄生网表是死代码。
4. 发现陷阱 2：PEX 器件 hdt_*_fs 只在模型库 `*_sram_fs` 分支定义；参考用 `tt_sram_dbc`（只含 *_dbc）会报 undefined subckt。
5. 生成 `CH231_HDT_Bitcell_FS_WiPin_pex.sp`：例化 PEX 子电路（端口按名映射）+ 改 corner。ask_question 让用户选角 → `fs_sram_fs`。
6. 后续用户报 wnm_2/vsnm=0 → agent 查 .ms0/.lis 发现模拟器实际算出 wnm_2=380mV，问题是 .PROBE V(VIN) 节点名错（VIN 是 .PARAM 非节点）。

## 关键产物
- `CH231_HDT_Bitcell_FS_WiPin_pex.sp`（agent 最终交付，5165B/136 行）—— 我从 10.129.2.12 scp 拿到（`/home/e0024852/CH231_HDT_Bitcell_FS_WiPin_pex.sp`，world-readable）。
- 输入文件（pex_subckt.sp / ref_stimulus.sp / schematic_netlist.sp / rev06 stim）从 session tool_results 的 `result` 字段还原（`.75` 上 e0031982 对 /rundata、/proj/lacaa 无读权限，但 session JSON 内已含 agent 以 e0024852 身份读到的全文）。

## case 化
- A 档 trace-faithful，用户原话。
- deliverable = `pex_stimulus_builder.py`（自动化该改造的生成器，固定 5 参 CLI），判分在 hidden B（变体：CH252_HDT_Bitcell_WiPin / 端口序 VDD VSS WL BL BLB S SB / 族 sf→tt_sram_sf / 6 cell）上跑。
- check.py 10 断言，独立复算 PEX 端口映射 + 应选 corner。ref 自验 PASS，3 假 + 2 negative 全 FAIL。
- 验证：我的泛化脚本在 A 上复算出的端口映射与 agent 手工交付**逐 cell 节点完全一致**（仅 PEX 子电路名源不同：我用 .sp 的 CH231_HDT_Bitcell_FS_WiPin，agent 用 .dspf 的 hdt_CH231_bitcell）。
