# gpya9 deepread — netlist missing-ref diagnosis (r974)

- **session**: 1795074929427_gpya9 @ hfeahpc505 (10.129.33.28), user t0002607 (HuQinyu), mc=163, spice_sim
- **trace size**: 894529 bytes / 135 messages
- **picked at**: r973 triage (strongest makeable in fresh queue), claimed+合成 r974

## 用户意图（真实 trace 流）
主线 sub-task 1 (msgs 0-34): nanospice 跑 HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu 报
`Error: no reference ckt rm2cb_fs for xi_cds_thru_0  (line 1226)`。用户怀疑 .lib 挂载。

agent 排查链（人工固化为本 case 的脚本逻辑）:
1. 定位实例: netlist 1226 行 `HCSP_LEAF_TIEHL_CORNER` 内 `XI_cds_thru_0 TRKWL TRKWL_BCK rm2cb_fs w=31e-9 l=300e-9 mr=1 rctmod=rctmod_res` (X 子电路调用, master=rm2cb_fs)。
2. 追 .lib 挂载链: `model_tt.sp` → `.lib './nanospice/model.lib' tt_res_fs` → model.lib 1731 行 `.lib tt_res_fs` → `model_setup_fs.lib`(res_default+res_tt) → `.lib './res/res_fs.mdl' res`。逐级验证链路完整, 排除挂载问题。
3. grep res_fs.mdl 列已定义金属电阻: rm1ca/rm1cb, rms2ca/rms2cb, rms3ca/rms3cb, rmx4ca/rmx4cb, rmx5ca/rmx5cb, rmy6~rmy10 (共 15 个 _fs 后缀)。**没有 rm2cb**。
4. 全版本兜底: /proj/lacaa/TV1_FS/model 下 Rev03~Rev05/DBCFS/SRAM Rev04~06/ALS 全递归搜 rm2cb = 0 命中。
5. 结论: 根因 = 模型名 rm2cb 在库中不存在, 非挂载问题。

后续 sub-task (msgs 35-134): SVS 网表比对 (dbsvs/Argus SVS 只比 OA schematic, 不比 netlist 文件) → agent 自写 netcmp.py (SVS-like 结构化 SPICE 网表比对器: .SUBCKT 集合差异 + 每 cell 端口/实例/连接/参数, 数值归一化 31e-9==31n==0.031u, 格式容忍 / 分隔符+总线 [] / <> 归一+M↔X 前缀配对)。比对 tiling 版网表时发现同位置 `RI_cds_thru_0 ... rms2cb_fs` → **证实 rm2cb 是 rms2cb 笔误 (漏 s)**。

## reframe (harness-for-teeth)
trace 主线诊断步骤固化成通用 `missing_ref_diagnose.py`: 读 deck/netlist/error_log/model_lib_dir → 解析 "no reference ckt <name> for <inst>" → 定位实例(行/节点/master/参数) → section-aware 递归追踪 .lib 链 → 收集 .SUBCKT/.model 定义 → 标记缺失 → Levenshtein 笔误建议 → 输出 diagnosis.json+diagnosis.txt。

## A 档 (trace-faithful, 可见)
netlist_A.sp 含 `HCSP_LEAF_TIEHL_CORNER` + `XI_cds_thru_0 ... rm2cb_fs ...`; deck_A.sp `.lib './model.lib' tt_res_fs`; model_lib_A/ 三级链 model.lib→model_setup_fs.lib→res_fs.mdl (15 个电阻 .SUBCKT, 无 rm2cb_fs); error_log_A.txt = nanospice 报错。

## hidden B (判分, 不进沙箱)
电容族 (.model 格式), 异 subckt HCSP_LEAF_DECOUPLE, 异实例 XCD_cpl0, 异笔误 cm2n_fs (real cm2m_fs, d=1 唯一最近), 异 .lib 链 cap.lib/cap_setup_fs.lib/cap_fs.mdl (5 个 .model)。结构同 A (通用 CLI 可跑) 但模型族/格式/名/实例/节点/参数/链全异, 非"换文件名"。

## 自验
- reference missing_ref_diagnose.py 跑 A: missing=rm2cb_fs, inst=XI_cds_thru_0 line4, chain_intact=True, 15 defined, missing_in_defined=False, suggestions top2 = rm1cb_fs(d1)+rms2cb_fs(d1) (并列, trace 答案 rms2cb_fs 在 top) ✓
- reference 跑 B: missing=cm2n_fs, inst=XCD_cpl0 line4, nodes=[VDD,VSS], master=cm2n_fs, chain_intact=True, best=cm2m_fs, defined=5 caps ✓
- check.py (ref as submit.zip on B): PASS 15/15 (a-o) ✓
- negative_selftest: ref PASS; neg_empty FAIL[b], neg_print FAIL[b], neg_core_removed FAIL[l], neg_hardcode_a FAIL[d] ✓ (§4.9 三假全 FAIL + hardcode-A FAIL)
- k_rationale == k_check == 15 (≥8 硬闸门) ✓
- anti-hardcode-A: 11 个 A-only token 守门 ✓

## 备注
- A 档 best_suggestion 是 rm1cb_fs (与 rms2cb_fs 并列 d=1, 字母序 rm1cb_fs 在前) — 这是 edit-distance 的固有局限, trace 的" definitive rms2cb_fs"来自 tiling 网表交叉印证 (超出本工具范围), 故 A 不由 check() 判; B 的 cm2m_fs 是 d=1 唯一最近, check(l) 可硬断言。
- 真实 trace ip=10.129.33.28 (summary.tsv 该行 ip 字段为 0.0.0.0 占位, 经 .75 SSH getent hosts 补全)。
