# 深读笔记 — jnf1q (jasonxu @ hfeg0plg93, mc=470)

- session: `1792551272867_jnf1q.messages.json` (1.66MB, 317 msgs, agent=lead, 180 user/137 assistant)
- 域：schematic_netlist (ALPS netlist 解析) + analog_context (DRAM readout CM search)
- 工具分布：editor×84 / read_files×31 / run_approved_command×22 / list_allowed_files×16

## 用户意图演进（16 个实质 user 文本轮）

- U[0/17/116]：skill-creator meta（创建 skill 的写作指南，非任务本体）
- U[3/4]：`readsigCM_search, drvqa_cmos_digital, T_ReadSigLeft`（初版触发，pyAether 原理图版）
- U[5/6]：**关键转向**——「上述问题可能是因为你无法访问项目文件。现在我给你提供模块的 netlist，请你首先编写一个工具对 netlist 进行分析和提取，并 copy 一份 ReadsigCM.py 在该脚本基础上修改」。从 pyAether 原理图扫描改为**直接解析 ALPS netlist 文本**。
- U[8]：输出文件保存路径默认与 netlist 路径放在一起，不要写死
- U[9/10]：skill 改名 `jasonxu-analogkit`（readsigCM 仅是小功能，后续丰富）
- U[11]：一次执行**多个 netlist**，各自输出 + 最后合并；路径不要写死（drvqa→drvsa 等）
- U[12]：改为**清单文件**输入（所有待分析 netlist 路径放在一个文件中），输出全部放在清单所在目录
- U[14/15]：**后处理 4 步**——仅留 fnReadSigGrpSel10 行 → 排序 0000000..1111111 → 删前两列 + DecOut 去 fnReadSig 前缀与 En 后缀 → 非 fnReadSig token 置 spare
- U[15]（最终版，覆盖 U[14]）：步骤 3 的 En 处理改为「去 En* 后缀（EnY/EnV/En 等）」，**取消** U[14] 的「EnY/EnV 结尾整行删除」
- U[16]：`readsigCM_search, /proj/drvqa/V0/simdir/hspice/jasonxu/09_readout/readsig_netlist`（最终验收调用）

## netlist 实例格式（从 _inspect_netlist.py / _readsigcm_netlist.py / netlist.map 推得）

```
X<inst> <net_A0> <net_A1> <net_A2> <net_A3> <net_A4> <net_A5> <net_A6> <net_A7> <DecOut_net> <cell>
```
- cell ∈ {T_ReadSigDecVcc, T_ReadSigDecVccp, T_ReadSigDecVccp_1, T_ReadSigDecVdd1} → type {vcc, vwlp, vwlp, vdd1}
- 引脚列序（去行首实例名后，0-based）：A0=col0..A6=col6, A7=col7, DecOut=col8（来自 netlist.map 的 `P 引脚 序号`）
- 位编码：A0..A6 的 net 名匹配 `r'([a-zA-Z])<\d+>'` → 字母 D 记 '1'，其他字母记 '0'，不匹配记 'NA'
- A7 = 地址选通 net（fnReadSigGrpSel10 / fnReadSigGrpSel00 等）
- DecOut = 该地址选中的读出信号 net（fnReadSigXxxEn / net42<0> / spare_1111000 等）

## 最终脚本逻辑（idx=276 main + idx=282 En 处理 patch，idx=290 运行 127 行用户接受）

1. collect_netlists(arg)：arg 为清单文件/目录/netlist。清单文件每行（去 # 注释）为 netlist 路径，**相对清单文件目录解析**；目录则找 netlist/netlist.presim/netlist_org/*.netlist
2. extract_readout(nl)：扫 `X.. <cell>` 实例行 → {a7, bits[7], type, decout}
3. 合并所有 netlist 的行 → raw_rows
4. 后处理（内存，不落盘中间文件）：
   - 仅留 a7 == "fnReadSigGrpSel10"
   - DecOut 清洗：若 startswith("fnReadSig") → body = decout[9:]；body = re.sub(r'En[A-Za-z0-9]*$', '', body)（等价 rfind('En') 截断）→ newtok = body；否则 newtok = "spare"
   - final.append(bits + [type, newtok])
   - 按 7 位二进制 0000000..1111111 升序排序
5. 输出：`<清单目录>/digitalPinInfo_final_<时间戳>.csv`，每行 `<b6>..<b0> <type> <decout_cleaned>`（9 token）

## 真实金标准（用户接受，idx=291 stdout，exit 0）

`/proj/drvqa/V0/simdir/hspice/jasonxu/09_readout/digitalPinInfo_final_20261021_194117.csv`（127 行，2 设计 Left+CenterR 合并）。逐行取自 trace idx=291 的 run_approved_command stdout。注意：0000000 行缺席（127 = 2^7 - 1）。

## 合成（B 档）

- **netlist A**（可见，2 设计 T_ReadSigLeft + T_ReadSigCenterR）：22 行 GrpSel10 + GrpSel00 decoys + EnY/EnV/no-En/spare DecOut 变体，复刻真值位模式与 fnReadSig 命名
- **netlist B**（隐藏，2 设计 T_ReadSigLeftB + T_ReadSigRightB）：23 行 GrpSel10，命名/位模式/DecOut/spare/EnY/EnV/EnX 全异于 A，跨输入守卫
- 参考 ReadsigCM_ref.py 复刻最终 4 步逻辑；check.py 15 条件 a–o（含跨输入守卫 n + 多 netlist 合并 m + En 后缀剥离 h）

## 坑

- 权限：/proj/drvqa/... 在 hfeg0plg93 上 jasonxu 私有，e0031982 不可读 → 无法取真实 netlist，改用 gen_netlist.py 从 trace 结构 + 金标准派生
- En 处理版本演进：idx=249/257/265（U[14] 版，EnY/EnV 整行删除）→ idx=276/282（U[15] 最终版，En* 后缀剥离保留行）。金标准 127 行来自最终版
- 清单相对路径：必须相对清单文件目录解析，否则跨工程（drvqa→drvsa）失败
