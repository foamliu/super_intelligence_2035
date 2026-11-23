# r1115 深读: foqm7 (duowang@hfeg0plg99, mc10, spice_sim) — DSPF 寄生耦合电容提取

## trace 溯源
- session: `1795163298798_foqm7.messages.json` (49 msgs / 28 user / 554KB)
- user: duowang, host: hfeg0plg99, match_count=10 (transistor:40;analog:3;hspice:2;synopsys:1;calibre:1)
- scan: ssh_eda_search_20261123_064315
- 真实任务: 从 432MB StarRC DSPF 1.3 寄生网表 `msaq_E_spf.spf_RCC_mm` 提取 `Cslin<63>` 到 BL252/253/254/255 各自 BLA/BLB 的寄生耦合电容总值，输出 CSV

## 用户意图（原话）
> /rundata/sim_cloud/CRG/Duowang/1118Csl_bl/msaq_E_spf.spf_RCC_mm是文件，帮我找到文件中Cslin<63>和BL255/253/251/249的BLA和BLB的寄生电容，并且整理到我到文件夹中以.csv文件的形式，并且计算出Cslin<63>分别到BL252/253/254/255的BLA和BLB的寄生电容，注意是分别计算出，例如展示出到BLB252的寄生电容总值，然后又展示出到BLA252的寄生电容总值，要放到文件中

## assistant 工具链与关键产物
1. `list_allowed_files` 探工作区 → 发现已有 `build_csv.py`（前次会话遗留）+ 已有 CSV
2. `read_files` 读前次 CSV + SPF 头 60 行 → 确认 DSPF 1.3 格式，`*|NET <name> <total>PF` 段头，cap 行 `C<id> term1 term2 val`，接地 `Cg<id> term 0 val`
3. `inspect_spf2.py` 流式扫描 432MB → 确认网络命名: `cn00bla<N>`(BLA)/`cn00blb<N>`(BLB)，cn00~cn15 共 16 组
4. **关键发现（核心齿）**: 前次脚本正则 `(\S+:\d+)` 只匹配 `net:数字` 端点，**漏掉实例引脚端点** `XI_msax256_cp00.XI_CXSA_1x4_0<63>.XMMN0b:SRC`（这些引脚经 `*|I <inst> <pin> <net>` 声明挂在 cn00bla/blb<252-255> 上）→ 8 个 XMMN SRC 引脚 + 54 个 XRRI0:A 引脚的耦合电容被漏
5. `extract_csl63_bl_caps_final.py` 两遍扫描: pass1 建 `*|I inst:pin→net` 映射 + 收集 Cslin<63> 段内所有 cap; pass2 解析每条 cap 的端点（net:node 直取 net; inst:pin 查 *|I 映射），按 BL 网络分组求和
6. `verify_csl63_caps.py` 对账: 段内耦合 5.335fF + 接地 1.533fF + 段外引用 1.058fF = 7.9256fF == 声明总电容 0.00792562PF（分毫不差）→ 证实每个耦合电容只列一次（列在两相关网络中后出现的那段）
7. `hunt_residual.py` 残差定位: 0.003fF 残差是 StarRC 阈值下舍入，非 BL
8. 输出 2 CSV: `Cslin63_BL252_253_254_255_cap_totals.csv`（每 BL×BLA/BLB: cap 数 + 总值 F/PF/fF + BLA+BLB 合计 + 校验列）

## 产出结果（真实数值，A 用）
Cslin<63>→BL252/253/254/255:
| BL | BLA fF (n_cap) | BLB fF (n_cap) |
|252| 0.135422 (19) | 0.186864 (22) |
|253| 0.128638 (14) | 0.186779 (17) |
|254| 0.179812 (27) | 0.137374 (17) |
|255| 0.186687 (17) | 0.176876 (19) |
- BL 网络族: cn00bla/cn00blb（仅 cn00 组，cn01~cn15 的 249-255 与 Cslin<63> 无耦合）
- 总电容对账: 7.925620 fF = 0.00792562 PF

## reframe（spec 驱动 L1 纯 Python DSPF 耦合电容提取器）
**case = EDA-Eval-DesignFlow-DspfCouplingCapExtractProduce-001**

输入: `<dspf_file>` + `<spec.json>` {source_net, bl_prefix, bl_indices, output_csv}
输出: CSV，每行一个 (BL_Num, BL_Type) 组合: BL_Num, BL_Type, BL_Net_Name, Cap_Count, TotalCap_F, TotalCap_fF

规则:
1. 解析 DSPF: 收集 `*|I <inst> <pin> <net>` 实例引脚→网络映射
2. 定位 `*|NET <source_net> <total>PF` 段（到 `*|ENDNET` 或下一 `*|NET`）
3. 段内每条耦合 cap 行 `C<id> term1 term2 value`（非 Cg 接地）:
   - term 若为 `net:node` → net 直接取 `:` 前
   - term 若为 `inst:pin` → 查 `*|I` 映射得 owning net
   - 一条 cap 的两端: 一端属 source_net，另一端属 target net
4. target net 形如 `<bl_prefix>bla<N>` 或 `<bl_prefix>blb<N>` 且 N ∈ bl_indices → 计入; 其余 target（非 BL 或 N 不在请求集）跳过
5. 按 (N, BLA/BLB) 分组: Cap_Count = 条数, TotalCap_F = 求和, TotalCap_fF = ×1e15
6. 输出 CSV（请求集内每个 N 两行 BLA+BLB，即使 0 也要输出）

**核心齿（判分牙）**: pin-form 端点必须经 `*|I` 映射解析。naive 正则只匹配 `net:digit` 的 parser 会漏掉 pin-mediated cap → Cap_Count 偏小 + TotalCap_F 偏小 → FAIL。这是判分核心区分点。

## anti-hardcode 设计
- **A**（faithful）: source=Cslin<63>, bl_prefix=cn00, bl_indices=[249,251,252,253,254,255], pin 实例 XI_msax256_cp00.XI_CXSA_1x4_0<63>.XMMN*b:SRC, XI60<63>.XRRI0:A, 真实量级 fF
- **hidden B**: 五重异 ①source=Cslin<47> ②bl_prefix=cn03 ③bl_indices=[100,102,104,106] ④pin 实例 XI_msax256_cp00.XI_CXSA_1x4_0<47>.XMMN*a:DRN + XI60<47>.XRRI1:B ⑤cap 值/条数/BLA-BLB 分布全异
- B 生成器 `_gen_B.py` 内嵌 reference 计算（独立于 candidate），check 用其做期望值

## check 12 条断言（k=12 a-l）
①(a) zip+compile+size ②(b) B exit0+非空 csv ③(c) CSV 列头齐全 ④(d) 行数==请求集×2(BLA+BLB) ⑤(e) BL_Num 集合==请求集 ⑥(f) BL_Type 集合=={BLA,BLB} ⑦(g) 每 (N,type) TotalCap_F == 期望（独立计算）**核心齿** ⑧(h) 每 (N,type) Cap_Count == 期望 **核心齿（pin-mediated 必计入）** ⑨(i) TotalCap_fF == TotalCap_F×1e15 ⑩(j) 至少一组 (N,type) Cap_Count > naive net:digit-only 计数 **核心齿证明** ⑪(k) anti-hardcode: A 的 source/bl_prefix/pin 实例 token 不在 B 输出 ⑫(l) 3-seed sha256 一致

## 3 negs
- empty: 空脚本 → a/b FAIL
- print_only: 硬编 A 的数值输出 → g/h/k FAIL（B 值不匹配 + A token 出现）
- core_removed: 真解析 B 但 pin-form 端点不解析（仅 net:digit 正则）→ h/g FAIL（Cap_Count 偏小，pin-mediated cap 漏）+ j FAIL
