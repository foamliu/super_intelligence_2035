# Deep-read: 1795435313529_e5zcs — LP6TOP ntn_m/ptn_m/ntk/ptk 6 层器件清单统计

- **session**: `1795435313529_e5zcs`
- **user / host**: shushengz / hfeg0plg93
- **match_count**: 371 (scan `ssh_eda_search_20261124_023802/summary.tsv`)
- **session file**: `/home/shushengz/.cline/data/sessions/1795435313529_e5zcs/1795435313529_e5zcs.messages.json` (1,298,104 bytes, world-readable, 416 messages)
- **agent**: lead
- **domain**: schematic_netlist (shard D)
- **case produced**: `EDA-Eval-DesignFlow-MosTypeHierCount6Lvl-001`

## 真实任务流（25 段用户输入）

1. **U1 (idx 0)**: 「统计一下这个 /proj/dejoa/V0/libs/dejoa_digital/DoutFIFOTopM6/schematic block 内使用 ntn_m/ptn_m 和 ntk/ptk 管子类型 和数量和尺寸」 — 初始任务：DoutFIFOTopM6 block 器件清单。
2. **U2 (idx 210)**: 「在这个 block 里面找下 ntn_m ptn_m 和 ntk 相关的器件 的数量和比例 /proj/dejoa/V0/libs/dejoa_top/LP6TOP/schematic」 — 切到更大的 LP6TOP block，要数量+比例。
3. **U3-U7 (idx 254-286)**: 用户让 agent load 自写 SKILL `count_mos_types_v2.il` / `analyze_block.il`，跑 `analyzeDevices("dejoa_top" "LP6TOP" "schematic")` — SKILL 直连 OA 库拿实例。
4. **U8 (idx 292)**: 「找到使用 ntn_m cell 对应的 hier」 — 要 hierarchy 路径。
5. **U14-U24 (idx 326-380)**: SKILL 路径超时无输出，agent 转向 shell：`trace_hier.sh` (BFS 用 `strings` 扫二进制 OA layout.oa 提 cell 引用) / `count_ntn.sh` / `analyze_block_v3.il` / `analyze_diag.il`。run_approved_command profile=shell-runner/python-runner 多次超时 (SIGKILL)。
6. **关键数据产出 (idx 392, 398, 410, 414)**:
   - ChanMid/layout: 6 个 ntn_m (I_ntn_m_0/3/466/468/470/472)
   - LP6TOP 顶层无直接器件；BFS 在 depth 3-6 的 analogIP 子模块 (LvlShftVdd2c2VdlyRstLIP=7 refs, VbpIPTop=2, VMonAmpDqLIPTop=2, …) 找到大量 ntn_m refs
   - ptn_m / ntk / ptk 在 layout flatten 后 = 0
7. **U25 (idx 402)**: 「往下遍历6层 还要统计使用的数量」 — 最终需求定型：6 层 BFS + 精确计数。
8. **最终报告 (idx 415)**: 每层 ntn_m 计数表 + 完整 hierarchy 路径树 (LP6TOP→Channel→{ChanMid,ChanEdgeL→SealRingDetIP,ChanEdgeR→VcctoVwlpClampRIP,ChanSC0/1→VMonAmpDqL/RITop}→analogIP 子模块)。

## 痛点（固化价值）

- `strings` 扫二进制 OA 脆弱、超时严重（Python BFS 整个被 SIGKILL）。
- SKILL `analyzeDevices` 依赖活体 Virtuoso + OA 库，环境不可复跑。
- 拿不到 W/L（OA 二进制 `strings` 不含尺寸参数），用户要的「尺寸」最终空缺。
- 多重性/层级计数靠手写 shell 串联，易错。

## 固化方案

把「层级 schematic 器件清单统计」固化成**离线文本分析器** `mos_hier_counter.py`：
- 输入：文本化 SPICE 网表 `netlist.sp`（每行一个 `XI_<type>_<id> … W=<w>u L=<l>n M=<m>` MOS 器件）+ `hierarchy.json`（cell→子单元清单）。
- 输出：`mos_hier_report.json` —— top_cell(自动推导) / device_types / total_counts(按 M + hierarchy 多重性展开) / per_level_counts / instances(完整路径) / size_summary(去重 W,L)。
- 根除痛点：纯文本解析（无 OA 依赖 / 无超时）、W/L 显式可拿、计数确定性、6 层 BFS 可复跑。

## 防背题设计

- **隐藏变体 B**（SUT 不可见，check 只在 B 上跑）：同族 LP6TOP 网表，cell 结构变（去 ChanEdgeR/VcctoVwlpClampRIP、加 LvlShftVdd2c2VdlyRstLIP）、器件数/ID/W/L 变、含 ptk。A: ntn_m=20/ptn_m=4/ntk=5/ptk=0；B: 35/7/3/2。
- **A-prime 变体**（reference/_aprime_*，SUT 不可见）：完全不同 cell 名 (PLLTOP/AnalogMux/ClkTree/VcoCore/BiasGen/Div2Stage/PulseGen)、不同根 (PLLTOP)、不同尺寸 (L=35nm)、不同总数 (13/4/3/1)。击穿 smart B-hardcode stub。
- **A 专属 cell 名守卫**：ChanEdgeR / VcctoVwlpClampRIP (A 有 B 无)，出现在 B 报告路径即判硬编码 A。

## check 19 条断言（k_check=19）

a zip 解含 mos_hier_counter.py ｜ b B 上退出码 0 ｜ c JSON 存在可解析 ｜ d 8 顶层键 ｜ e source_file=="netlist.sp" ｜ f top_cell=="LP6TOP"(B 根动态推导) ｜ g device_types 顺序一致 ｜ h total_counts 与 check 独立重算 B 精确相等 ｜ i per_level_counts 精确相等 ｜ j len(instances)==独立重算 ｜ k instance 字段完备 type∈types m>=1 ｜ l size_summary distinct_wl 精确相等 ｜ m 3 次重跑字节一致 ｜ n 无 A 专属 cell 名泄漏 ｜ o A-prime 退出码 0+合法 JSON ｜ p A-prime top_cell=="PLLTOP" ｜ q A-prime total_counts 精确相等 ｜ r A-prime ntn_m distinct_wl 精确相等 ｜ s A-prime per_level_counts 精确相等。

## 验证

- reference solution `mos_hier_counter.py` 自检 PASS（19 条全过，B + A-prime）。
- 5 个 negative 全 FAIL：empty_shell / print_only / core_deleted(跳 ntk,ptk) / naive_hardcode_a(硬编码 A) / neg_fake_hardcode_b(smart B-hardcode stub，在 p/q/r/s 击穿)。
