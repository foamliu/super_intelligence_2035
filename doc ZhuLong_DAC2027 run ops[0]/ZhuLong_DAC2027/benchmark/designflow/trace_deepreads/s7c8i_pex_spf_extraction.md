# 深读笔记 — 1795081151863_s7c8i_pex_spf_extraction (PARKED)

- **trace**: `1795081151863_s7c8i.messages.json` (dsgao / hfeahpc505 / 10.129.33.28 / mc=22 / 237 msgs / 842KB / 125 user turns)
- **session path**: `/home/dsgao/.cline/data/sessions/1795081151863_s7c8i/1795081151863_s7c8i.messages.json`
- **tools profile**: drc:876 netlist:601 mixed-signal:320 aether:252 schematic:69 floorplan:34 hspice:22 virtuoso:18
- **domain**: spice_sim (B 过滤命中 hspice) — 实为 PEX 物理提取，边界偏 C

## 用户真实意图（U0，原话）
> `/proj/drcpa/V0/ver/pex/dsgao/R_XdecGap_35p5/R_XdecGap_35p5.cdl，/proj/drcpa/V0/ver/lvs/drcpa_sactrl_1119_backup/R_XdecGapp_35p5/R_XdecGap_35p5.gds 抽个 TT corner, RCC, 95C 的 spf`

**意图 = 交付一个 .spf 文件**（PEX 寄生参数提取，TT corner / RCC 模式 / 95C），输入是 CDL(LVS netlist) + GDS(layout)。

## 助手工具链（237 msg，50+ editor 写脚本）
pex_probe*.py → pex_show*.py → pex_setup_check → pex_find_runset → pex_corners → pex_setup_run → pex_write_config → pex_wrapper*.py → pex_calibre*.py → pex_final_verify*.py → pex_finalize.py。大量 list_allowed_files 探索 + run_approved_command 跑 StarRC `runlpe` 封装。

## 关键事实（assistant 最终总结 msg[236]）
1. **用户路径有 typo**：`R_XdecGapp_35p5`（双 p）实际是 `R_XdecGap_35p5`（单 p）。真实成对 CDL+GDS 在 `/proj/drcpa/V0/ver/lvs/drcpa_sactrl_1119_backup/R_XdecGap_35p5/R_XdecGap_35p5.{cdl,gds}`，已拷到 pex 目录，顶层 cell = `R_XdecGap_35p5`。
2. **95C 不是合法工艺角**：`cxmtG5_CIP`/`drcpa` 的 corners.smc 里 TT(TYP) 只有 **-40/0/25/98/125°C**。经用户确认改用 **98°C**，输出名 `R_XdecGap_35p5.spf.TYP_98_RCC`。
3. **抽取流程只跑到 LVS 前一步**：`runlpe`（StarRC 站点封装 `/apps/imctf/cad/script/runlpe/runlpe`）识别到 TYP_98/RCC、下载 `lpe_RCC.rule`/`corners.smc`，差 `calibre -lvs` 这一步。
4. **最后一步卡住 = 环境限制**：agent 主机 `hfeg0pkn003`（RHEL 8.10 / glibc 2.28，无显示器），所有装好的 Calibre `aoi` 平台树起不来（`VCO=aok` vs `aoi` 不匹配），逐版本（2020.1/2020.4/2023.3）+ 清 LD_LIBRARY_PATH/LD_PRELOAD 验证，与 env 无关，是计算节点 glibc/平台与 Calibre 编译平台不匹配。过往成功 run 都在交互式桌面（Aether PEX GUI）启动，留有 `.aether_log` + `xmessage` 弹窗痕迹。

## 交付物（assistant 声称）
在 `/proj/drcpa/V0/ver/pex/dsgao/R_XdecGap_35p5/` 下：
- `.lpe.config` — 完整正确配置（process/project/version/cdl/gds/top/POWER_NETS/...）
- `run_pex.sh` — 可直接运行的 launcher（在配置正确的 run 目录里）
- **但实际 .spf 未产出**（最后一步 calibre -lvs 跑不了）

## 判定：PARKED（不可造，有真实工具链阻塞）

**理由（符合任务初衷铁律）**：
1. **任务形态 = 用户意图（铁律 1）**：用户要的是 `.spf` 文件（PEX 提取结果），不是配置文件。reframe 成「生成 .lpe.config + run_pex.sh」改变了任务形态，违反铁律 1。
2. **交付结果 = 判分对象（铁律 2）**：trace 里参考交付物（.spf）**从未产出**（环境阻塞）；SUT 沙盒无 Calibre/StarRC PEX 工具链，无法生成或校验真实 .spf。check() 无法区分「真交付 .spf」与「没交付」——判分没有牙。
3. **不是时间压力**：是真实的工具链/环境阻塞（与 trace 里 assistant 遇到的同一阻塞），符合 park 标准（类比「aether 超时」）。

## 备选（若未来 SUT 沙盒接入 Calibre PEX）
可复活为 L3 真跑 case：asset A = 真实 CDL+GDS（小 cell）+ corners.smc，hidden B = 异 cell/异 corner，check 真跑 PEX 后解析 .spf 结构（*SUBCKT/*RES/*CAP 节点数/端口）。需 PDK + Calibre license。

## 41 fresh 状态更新
本轮 s7c8i park ⇒ 41 fresh: 7 case + 16 park = 23，余 18。
