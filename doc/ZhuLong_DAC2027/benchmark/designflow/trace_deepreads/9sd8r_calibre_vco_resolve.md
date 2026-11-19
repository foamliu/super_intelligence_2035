# 9sd8r — CalibreVcoResolve reframe (r830, shard C)

## trace facts
- session: `1794969582427_9sd8r.messages.json`
- user: steveny @ hfeg0pnd001 (10.129.32.189)
- mc: 294, domain: physical_verify
- keywords: `calibre:2426;drc:881;lvs:429;.gds:131;pyaether:76;pdk:38;gdsii:25;aether:17`
- 289 msgs (148 user mostly tool_results, 141 assistant)
- freshness: verified NOT in any of 4 ledgers / 4 jsonls / intent_audit_C / 5283-sid used set
- ledger row: `case EDA-Eval-DesignFlow-CalibreVcoResolve-001` (r828)

## user asks (real)
- U#1: eda_agent skill trigger
- U#2: 参考命令 `bsub -I -R "select[ncpus>=64...]" -n 64 -q pv calibre -drc -hier -turbo 64 calibreDRC.rule | tee rundrc.log`
- U#3: 总结一下当前的情况吧
- U#4: `CALIBRE BIN=.../aoi_cal2020.1_36.18/bin/calibre | bsub -q_pv -env "USE_CALIBRE_VCO=aoi" -o drc.log $CALIBRE_BIN -hier -drc wl_adjacent.drc` 有人这么说，你看看

## real task
想在登录节点通过 LSF `bsub -q pv` 提交 Calibre DRC，但 `calibre -version` 报：
`ERROR: Current execution environment is VCO=aok. Software tree is for environment VCO=aoi.`

## assistant 的源码级调研结论（grounding 依据）
1. **VCO 由 OS 派生**（calibre_env 第 43-45 行注释 + 实测）：
   - `aoi` — Intel x86, RHEL 6+, RHEL 7+, SLES 11 SP2+, SLES 12 SP3（不要求 AVX2）
   - `aok` — Intel x86, RHEL 8+（要求 AVX2）
   - `ixl` — 更旧回退
   - 实测：RHEL 8.10 → aok；CentOS 7.8 → aoi
2. **MGC_VCO 不是输入覆盖**：line 124 `MGC_VCO=`strict_vco_check=yes $MGC_HOME/bin/calibre_vco``
   是输出赋值。实测 `MGC_VCO=aoi` 仍报 `VCO=aok` 错误。
3. **USE_CALIBRE_VCO 强制覆盖**（calibre_vco 第 77-79 行）：优先级高于 OS 探测。
   实测 `USE_CALIBRE_VCO=aoi` 在 pv 节点 `Successfully completed`。
4. **autoswitch 判定**（calibre_env 第 138 行）：
   `echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_' && autoswitch='no'`
   即 tree 或 detected 任一在 `aoj..aoz` → 禁止自动切换 → 不匹配即 ERROR。
5. **逐字错误**（calibre_env 第 186 行）：
   `ERROR: Current execution environment is VCO=$MGC_VCO. Software tree is for environment VCO=$SW_WKSTN.`
6. **合法 VCO 集合**（`calibre_vco -vcos`）：`aoi aoj aok ixl`
7. pv 队列 CentOS 7.8 节点原生 VCO=aoi，登录节点 RHEL 8.10 → aok（环境硬限制）。
8. 旁支：`LD_PRELOAD` 注入 eda-agent 自带 libstdc++.so.6 覆盖节点系统库 → unset 后链路通。

## reframe
纯标准库 `vco_resolve.py`，读 env.json（uname_s/r/m + redhat_release + os_release_id/version
+ env{USE_CALIBRE_VCO, MGC_VCO, CALIBRE_HOME} + tree_vco），按上述 6 条规则解析 VCO。
不做真实 OS 探测 / 不 subprocess / 不联网。CLI：`<env.json> [--json]` + `-vcos`。

## case
- case_id: `EDA-Eval-DesignFlow-CalibreVcoResolve-001`
- k_check = 15 (a-o), k_rationale = 15
- 7 fixtures: A(visible RHEL8.10 ERROR) / B(hidden CentOS7 SUCCESS) / B2(cross-input UC=aoi 覆盖 SUCCESS) /
  C(UC=zzz 非法回退) / D(MGC_VCO=aoi 忽略) / E(tree=ixl autoswitch) / F(CALIBRE_HOME path parse)
- gold check PASS 15/15；4 negatives FAIL distinct (c/l/g/k)
- 三假提交 (空 zip / wrong-name / print('aoi') stub) 全 FAIL
- 确定性 + 幂等 验证通过

## lesson
真实 calibre_env 在 SUT 沙盒不可访问，但 wrapper 脚本语义（OS→VCO 派生 + 覆盖优先级 +
autoswitch 正则 + 逐字错误）是完整、可复现、可判分的算法核心 —— 完美的 mock-behavioral
reframe：剥离真实文件系统依赖，保留语义。MGC_VCO「看起来像覆盖变量但不是」是天然的反硬编
陷阱；USE_CALIBRE_VCO 的合法值判定 + 同 OS 不同覆盖结果（A vs B2）构成天然交叉保护。
