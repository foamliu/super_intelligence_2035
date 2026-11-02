# trace_deepread: jnf1q — readsigCM netlist address-table extraction

- **session**: `1792551272867_jnf1q.messages.json` (jasonxu @ hfeahpc501, mc=470)
- **agent**: deepseek-v4-flash, 317 msgs, status=failed (skill kept being invoked despite failed session flag)
- **tools**: editor×84, read_files×31, run_approved_command×22, list_allowed_files×16, SandBox_MCP(run_code pyAether)×3
- **domain**: characterization (analog readout address table) — shard B

## 用户意图演进（16 个有效用户轮）

1. msg[0] "我需要创建一个skill" → skill-creator 启动
2. msg[17] **提出需求**：把 `/home/jasonxu/script/ReadsigCM.py`（pyAether `TransferInfoToReport(lib,cell)`，查原理图模拟 readout 地址 + 读出 net + 排序）打包成 skill，触发词 `readsigCM_search, 库名, 电路名`
3. msg[46]/[56] 触发 `readsigCM_search, drvqa_cmos_digital, T_ReadSigLeft` → pyAether 连接失败（项目文件不可读）
4. msg[60]/[70] **提出需求（关键转折）**："现在我给你提供模块的 netlist，请你首先编写一个工具对 netlist 进行分析和提取，copy 一份 ReadsigCM.py 在其基础上修改…当用户输入 `readsigCM_search, netlist路径`，就开始执行" —— 从原理图版迁到 netlist 解析版
5. msg[116] 触发 `readsigCM_search, /proj/.../netlist`
6. msg[122] 提需求：输出文件默认存 netlist 同目录（不写死工程名）
7. msg[136]/[139] 提需求：skill 改名 `jasonxu-analogkit`
8. msg[164] 提需求：一次跑多个 netlist，各自输出 + 合并文件，路径不写死
9. msg[196] 提需求：清单文件式输入（`readsig_netlist` 内每行一个 netlist 路径），输出全在清单目录
10. msg[246] **给出修复方案（4 步后处理 spec v1）**：① 仅保留 fnReadSigGrpSel10 行 ② 排序 0000000→1111111 ③ 删前两列 + 末 token 去 fnReadSig/En ④ 无 fnReadSig 前缀→spare ⑤ EnY/EnV/En* 结尾整行删
11. msg[269] **给出修复方案（v2，最终）**：同上但去掉 step 5，改为 step 3 把 EnY/EnV/En* 作为后缀一并剥离（行保留）。示例 `fnReadSigGrpSel10 0 0 0 0 0 0 1 vwlp fnReadSigVbgrD2En` → `0 0 0 0 0 0 1 vwlp VbgrD2`
12. msg[316] 再次触发 `readsigCM_search, /proj/.../09_readout/readsig_netlist` → 产出 127 行最终 CSV（隐式接受）

## agent 真实产物（gold）

- 最终脚本 `/home/jasonxu/script/ReadsigCM.py`（347 行，netlist 解析版）+ skill `jasonxu-analogkit` 部署在 `~/.cline/skills/jasonxu-analogkit/`
- 算法：
  - **extract**：扫 netlist，匹配 `X<inst> <net0..net8> <cell>`，cell ∈ {T_ReadSigDecVcc/Vccp/Vdd1/Vccp_1}；A7=col7（fnReadSigGrpSel10/00），A0..A6=col0..6（`D<n>`→'1', 其它字母<n>→'0', 无匹配→'NA'），type=vcc/vwlp/vdd1，DecOut=col8
  - **post-process**（USER[269] 最终）：① 仅留 A7==fnReadSigGrpSel10 ② 按 7-bit 升序 ③ 删前两列 + DecOut 去 fnReadSig 前缀 + 去尾部 En/EnY/EnV/EnX（`En[A-Za-z]*$`）④ 无 fnReadSig 前缀的 DecOut → "spare"
  - 输出 `digitalPinInfo_final_<ts>.csv` 落清单目录
- 09_readout（3 netlist 合并）实跑 127 行（tr_291）：含 EnY 剥离（RefSpareD2EnY→RefSpareD2，行保留）、En 剥离（VbgrD2En→VbgrD2）、无前缀→spare（net10/spare_1111000→spare）、GrpSel00 decoy 已滤

## 可复现性判定

- 真实 netlist `/proj/drvqa/V0/simdir/hspice/jasonxu/09_readout/` 对 e0031982 **permission denied**（不可读 jasonxu 项目）
- 子技能 = netlist 解析 + 4 步后处理，**纯 Python L1**，完全可移植（无 pyAether/HSPICE 依赖）
- 选为 **B 档 synthesized**：资产按 ALPS netlist 格式合成（含 fnReadSig 命名约定、GrpSel10/00、EnY/EnV/EnX、spare 情况），gold 由本仓 clean reference 实现产出
- A 档 faithful 不适用：USER[60] 提需求轮过于宽泛（"编写一个工具对 netlist 进行分析和提取"），且真实 netlist 不可读，无法逐字复刻

## 已有 case 区分度

- SubcktExtract-001（spice_sim L1）：.SUBCKT 段流式提取 + 一层 X 实例/端口/网解析，discriminator = '+' 续行。本 case 是 **readout 地址表抽取 + 4 步后处理**（bit 编码、A7 过滤、二进制排序、fnReadSig/En 剥离、spare 替换、多 netlist 合并），discriminator 完全不同。shard B 此前无 readout 地址表征子技能，L1 补牙合规。

## 陷阱烤进

1. **A7 过滤**：GrpSel00 decoy 必须滤掉（不能把所有 readout 实例都输出）
2. **bit 编码**：`D<n>`→'1'，其它字母<n>→'0'，无匹配→'NA'（不能把 A<n> 也当 '1'）
3. **7-bit 二进制排序**：A6..A0 是 MSB→LSB，不是字符串序、不是 LSB→MSB
4. **fnReadSig 前缀剥离**：`fnReadSigVbgrD2En`→`VbgrD2` 不是 `fnReadSigVbgrD2`
5. **En/EnY/EnV/EnX 后缀剥离**：`En[A-Za-z]*$`，行保留（USER[269] v2，不是 v1 的整行删除）
6. **spare 替换**：无 fnReadSig 前缀的 DecOut（net10/spare_1111000）→ 字面 "spare"，不是原样保留
7. **清单路径相对解析**：相对清单目录，不写死工程名；输出落清单目录
8. **多 netlist 合并**：清单多行 → 合并所有 readout 实例再后处理
