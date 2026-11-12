# 深读笔记 · njt15 (1793427492496_njt15) · tongfanl · DDR6 CRC 注错诊断

> r416 选料深读。**A-faithful 合格**（用户问「为什么」未给根因）。clean produce-task（agent 写并迭代 probe_access.py 50+ 次 editor+run_approved_command）。**B 档合成候选**（trace 数据在 /proj/dscqa 私有路径，沙盒不可达 → 需 synthesized 输入）。
> 下一轮第一件事：据此笔记合成 case + 自验 + 落 jsonl。

## trace 元数据
- session: `1793427492496_njt15` ｜ user: tongfanl ｜ host: hfhds201(10.129.32.75)（NFS home，多机可见）
- mc=367 ｜ keywords: verilog:422;analog:402;systemverilog:17;aether:14;pyaether:11;netlist:7;synopsys:4;cadence:3
- 文件: `/home/tongfanl/.cline/data/sessions/1793427492496_njt15/1793427492496_njt15.messages.json`（1,384,406 B / 254 msgs / 129 user·125 assistant / 71 assistant text / 126 tool_use）
- 同 user 往期 case: r373 SimIncludeMissDiag-001、r415 VecgenProbeDiag-001（proven DDR6 diagnosis produce-task user）

## 3 个用户 prompt（原话）
- **U#1 (idx0)**: `这个路径中的结果，为什么xrun.log中的DATAT0（3189行）和波形中的数值对不上。你可以向我提问以保证准确交付。`（路径: `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/log/stimulus_tongfanl/WTM_fsm_1030/WTM004_block_check_..._X2P6_12800`）
- **U#2 (idx146)**: `我抽激励的脚本是：/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local 运行runsti/gen_stimulus_ltf 为啥UI16~23 的 DQ2 会被 pad 清零？？？`
- **U#3 (idx216)**: `DQ5的最后几位，CRC注错是随机的吗？`

## agent 工具链（clean produce-task）
- `list_allowed_files` / `read_files` / `search_codebase` 读 xrun.log、vecgen 配置、ddr6_tasks.sv、ddr6_test.sv、WTM004_block_check.v
- **`editor` 写并迭代 `/home/tongfanl/DDR6/DSCQA/analogsim/WTM/probe_access.py`**（diff-based: path/old_text/new_text/insert_line，~50 次 editor + ~50 次 `run_approved_command` 跑脚本，文件已不在磁盘）
- `SandBox_MCP_Server__run_code` 跑过一次

## 核心技术结论（agent 最终答案，三层）— 可作为判分锚点
### 1. CRC 码字本身：**不随机**（数据算出）
- CRC-8 由 `crc_method`（ddr6_tasks.sv:2200-2232，固定 XOR 抽头）从写数据算出
- 输入非 UI 顺序，而是 **DQ 串行化重排**后 144bit（`wr_reorganize_dq`, ddr6_tasks.sv:1994-1999）：
  - **`dq_org[24×n + j] = dq[6×j + n]`**  （n = DQ 0..5, j = UI 0..23 → D[0..143]）
- 两段排除在 CRC 计算外：
  - **D[64..71] = DQ2 的 UI16~23（pad 位）** — Write 任务 1256 行 + crc_method 内 2148-2150 行清零
  - **D[136..143] = DQ5 的 UI16~23（CRC 位自身）** — 不在抽头里（抽头最大到 D[135]），避免循环依赖
- 同样数据 → 同样 CRC。agent 复算 write0 「干净」CRC = **`[0,0,1,0,1,0,1,0]`**（crc_dq[0..7]）

### 2. 注错翻哪一位：**随机**
```systemverilog
// ddr6_test.sv:1352-1367  if(tbcontrol.wrcrc_errforce)
    else if (dutconfig.dqmode==X1P6||dutconfig.dqmode==X2P6) begin
        wrcrc_err_bit = $urandom_range(7);      // 8 位 CRC 均匀随机选 1 位
    end
    crc_dq[wrcrc_err_bit] = ~crc_dq[wrcrc_err_bit];
```
- X2P6/X1P6: `$urandom_range(7)`（8-bit）
- X2P3: `$urandom_range(3)` 或 `(7)`
- X1P12: `$urandom_range(15)`（16-bit）
- 随机数受 sim seed 约束（本 run `-seed 843426151`，同 seed 可复现，换 seed 注错位变）

### 3. 哪些写被注错：**固定**（非随机选写）
- pattern 里 `tbcontrol.wrcrc_errforce=1` 显式置位仅两处/套 WTM 序列：
  - **write 0**（WTM004_block_check.v:95-97，注释 `//CRC error`）
  - 序列末尾读回后最后一个写（158-161 行，用 `wtm_wr_data[1]`）
- 本跑 2 套序列 → 共 4 个写被强制 CRC 注错，其余写 CRC 干净

### 嵌入公式
- **`dq[143-6i] = crc_dq[7-i]`**  → **crc[0]→UI16, crc[1]→UI17, …, crc[7]→UI23**（落在 DQ5）

### 实测验证表（write0 第一套序列，t≈593.3ns 突发）
| | crc[0] UI16 | crc[1] UI17 | crc[2] UI18 | crc[3] UI19 | **crc[4] UI20** | crc[5] UI21 | crc[6] UI22 | crc[7] UI23 |
|---|---|---|---|---|---|---|---|---|
| 计算干净 CRC | 0 | 0 | 1 | 0 | **1** | 0 | 1 | 0 |
| 向量实际驱动 | 0 | 0 | 1 | 0 | **0** | 0 | 1 | 0 |
- **恰好一位不同：crc[4] (UI20)** → 确认注错翻 bit4

## 中间发现（agent 自纠错过程，可作 case 噪声/负样本灵感）
- agent 初算 CRC 与观察值差 2 位（bit4、bit6）→ 发现是**自己转录错误**：UI22 原始行 = 111011 → DQ5=1（误写成 0）→ 修正后 diff 仅剩 1 位
- LFSR pattern: `LFSR_dq<k> = L_data[28:5] ^ L_data[28-k:...-k]`（每 DQ 不同偏移），PRBS24 多项式 x^24+x^20+x^11+x^5+1
- DATAT0 mismatch 根因（U#1）: 6-bit 元素 bit 序 DQ0=MSB（非 LSB），与波形读序相反 → 这部分可另立 case

## 建议合成方案（B 档，digital L1 log-parser/diagnosis）
**task_id**: `CrcErrBitDiag-001` ｜ **k=10~12 目标**

**deliverable**: `crc_err_bit_diag.py`（纯 stdlib）— 给定一组 write burst 的 DQ×UI bit 矩阵 + 每个 burst 的干净 CRC（8bit，预计算输入）+ dqmode + errforce 标记，脚本：
1. 重排 `dq_org[24n+j]=dq[6j+n]` → 144-bit 串行流 D[0..143]
2. 识别 pad 段 D[64..71]（DQ2 UI16-23）并断言全零
3. 识别 CRC 段 D[136..143]（DQ5 UI16-23）
4. 嵌入 `dq[143-6i]=crc_dq[7-i]` → 期望驱动 DQ5 UI16-23
5. 比 expected vs actual driven → diff bits
6. 分类: is_single_bit_error（恰好 1 位差 = 注错）vs multi-bit（真 mismatch）
7. dqmode → valid bit range（X2P6/X1P6→7, X2P3→3, X1P12→15）报 JSON
8. errforce 标记 → 强制注错写计数

**判分独立条件（≥8）草案**:
- (a) zip 含脚本+output.json  (b) 脚本在 B 上跑通出 JSON
- (c) JSON 含必需键  (d) DQ 重排正确（D[24n+j]=dq[6j+n]）
- (e) pad 段 D[64..71] 识别+全零断言  (f) CRC 段 D[136..143] 识别
- (g) 嵌入公式正确（crc[i]→UI16+i on DQ5）  (h) diff_bits 正确
- (i) is_single_bit_error 在单注错 burst=True  (j) is_single_bit_error 在多 bit burst=False（跨输入守卫，击败 hardcoded）
- (k) dqmode→bit range 映射正确  (l) errforce 写计数正确
- 独立 oracle: check.py 用**不同实现**（按位索引重算，非 ref 的矩阵法）避免同 bug 互掩

**A/B 差异**: A = 2 burst（1 单注错 X2P6 + 1 干净）；B = 3 burst（单注错 X1P6 不同翻位 + 多 bit mismatch + 干净），数据值/CRC/dqmode/errforce 全不同；B 含多 bit burst 击败 hardcoded_A

**负样本**: naive_empty / print_only / core_removed（删 diff 分类）/ hardcoded_A（用 A 的 CRC 硬编码，被 B 多 bit burst + 不同 CRC 击败）

## 待确认 / 风险
- **CRC-8 抽头多项式未提取到**（ddr6_tasks.sv:2196-2280 的 X2P6 抽头位）→ 合成方案把干净 CRC 作为**输入**给脚本，规避需要抽头（诚实：tap 提取是另一独立子任务）。若下轮想含 CRC 计算，需先 ssh 读 ddr6_tasks.sv 该段。
- trace 数据在 /proj/dscqa 私有 NFS，沙盒不可达 → 必须 synthesized 输入（B 档理由充分）
- 用户名/路径原值保留（不脱敏）
