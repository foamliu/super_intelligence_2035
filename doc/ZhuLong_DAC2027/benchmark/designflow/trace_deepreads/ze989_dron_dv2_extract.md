# trace_deepread: 1794991410253_ze989 (dRONdV2 extract produce-modify)

- session: `1794991410253_ze989`，user `clarawu` @ `10.129.2.14`，18 msgs，11 user turns，D-domain 命中 mc=33 (analog_context / schematic_netlist / waveform)。
- 模型 GLM-5.2，agent=lead。

## 真实意图（verbatim）

- U#0（act）：`参考@/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_FinalDrv_Ron_cio_leakage_versionD/hspiceD/schematic/netlist/stimulus_file_for_metrics/dRONdT/extract_dRONdT.py修改/proj/.../dRONdV2/extract_dRONdV2.py`
- U_last（act）：`你分析的对，把修改后的脚本复制到@/.../dRONdV2/extract_dRONdV2.py`

单意图会话：把成熟脚本 `extract_dRONdT.py`（rpu/rpd 对温度 temper 的中心差分斜率 dR/dT 提取器）改编成 `extract_dRONdV2.py`（扫变量换成 vvdd，求 dR/dV2）。无其它歧义分支。

## 真实资产（trace read_files 工具结果，逐字提取到 .75 沙箱 `ze989_clean/`）

1. `extract_dRONdT.py` (10102 chars) — 参考脚本，py_compile 通过。结构：
   - `parse_run` 解析 `run` 中 `bsub ... -i stimulus.sp -o wv_dRONdT/x` 行
   - `parse_stimulus` 取 `.param Tref/VVDD/VVDDQ` + `.lib` corner 名
   - `parse_md0`（HEADER_WANTED="temper"），按 alter# 分组、组内按 temper 升序
   - `central_slope(vals, temps) = (R(T+1)-R(T-1))/(T+1-(T-1))`
   - 输出 CSV `Tref,VVDD,VVDDQ,process,dRpu/dT(%),dRpd/dT(%)` + 2 行 MAX，RON_NOM=230
2. `dRONdV2_0P85V.md0` — 真实 dRONdV2 测量：表头 `vvdd rpu rpd temper alter#`，3 alter × 3 vvdd 点(0.849/0.850/0.851)，temper=25。alter1 rpu=228.59 rpd=230.32（**vvdd 间恒定**——标定场景真实形态，斜率≈0）。
3. `stimulus_dRONdV2_0P85V.sp` — `.param VDD2CS=0.85`/`.param VVDD='VDD2CS'`/`.param VVDDQ=0.5`，`.dc ... sweep VVDD POI 3 'VDD2CS-0.001' 'VDD2CS' 'VDD2CS+0.001'`，`.lib` 引 ZQCODE corner。
4. `dRONdT_25C.md0` — 原 dRONdT 参考数据（表头 temper rpu rpd alter#）。
5. `run_A` — bsub 0P82V/0P85V/0P88V 三档。

## 改编映射（dRONdT → dRONdV2）

| 维度 | dRONdT | dRONdV2 |
|---|---|---|
| HEADER_WANTED | `temper` | `vvdd` |
| 分组内排序键 | temper↑ | vvdd↑ |
| central_slope x 轴 | temps | vvdds |
| OUTPUT_DIR | wv_dRONdT | wv_dRONdV2 |
| 输出首列 | Tref | VVDD2CS |
| 斜率列名 | dRpu/dT(%) dRpd/dT(%) | dRpu/dV2(%) dRpd/dV2(%) |
| RON_NOM | 230 | 230（不变） |

## A-faithful 重构决策

- 真实资产 /proj/m2701/... 属 clarawu 私有，不可进 SUT 沙箱；但 trace 中 read_files 已把 5 个文件逐字吐出 → **A 档 trace-verbatim**：直接用真实文件内容作为附件。
- extract_dRONdT.py 经二进制安全通道（eda_flow.read_file + write 工具，非 shell echo|base64）转移以保证中文注释不损坏（曾因 echo 转义损坏出现"未数据的数据任何数据"乱码导致 SyntaxError，已修复）。
- 隐藏 B 合成：2 文件(VVDD2CS=0.82/0.88) × 4 alter(FF/TT/SS/FS) × 3 vvdd 点；rpu/rpd 随 vvdd 线性变化（斜率 50/80/120/-30 ohm/V）使 dR/dV2 非零可验；MAX dRpu=52.17% MAX dRpd=39.13%（均 alter3）。

## case 落地

- case_id: `EDA-Eval-DesignFlow-DronDv2ExtractProduce-001`
- shard D jsonl: 523 行（r983 追加）
- check.py: 13 条独立断言（脚本存在/py_compile/B跑通exit0/表头5列含dRpu dRpd/数据行数=8/dRpu逐行比对/dRpd逐行比对/MAX dRpu/MAX dRpd/反硬编码A字面量/3次确定性md5/空数据目录exit非零/zip结构）
- 验证：ref solution PASS 13/13；3 negatives(empty_shell/print_expected/delcore) 全 FAIL；空 zip FAIL。
