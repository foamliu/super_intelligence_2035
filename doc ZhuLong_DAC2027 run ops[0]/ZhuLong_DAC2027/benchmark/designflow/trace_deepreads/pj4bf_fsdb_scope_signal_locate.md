# trace_deepreads/pj4bf_fsdb_scope_signal_locate.md — pj4bf (huifangg@hfeg0pkn004)

## trace meta
- session: 1794020447053_pj4bf.messages.json (huifangg@hfeg0pkn004)
- mtime: 2026-11-07 11:00, 147 msgs, 730KB, spice keyword count=520
- agent: lead (zhulong), FSDB 波形分析

## 用户轮（A-faithful 选轮）
- U#1: "你可以看到这个路径下的波形文件吗" — 询问能否访问 FSDB（铺垫轮）
- U#6: "如果我让你分析该波形文件中某个模块的波形，应该怎么提示你" — 元问题（不入 prompt）
- **U#12: "你可以看到controller层级下的odt"** — 提出需求（查看 controller 层级下的 odt 信号），无根因/修复 → A-档选轮 ✓
- 后续轮为澄清/追问，不入 prompt

## 金标准（assistant 末轮完整诊断）
仿真工具 = FineSim + Custom WaveView ADV T-2022.06-SP1；FSDB=finesim.fsdb (~3GB)

### ① FSDB 层次结构（从 sxcmd.log 的 wv_expand_tree_item/wv_select_tree_item 解析，@分隔）
```
D0:finesim.fsdb(0)
  └── toplevel(0)
        ├── xi0(0)
        ├── xi5(5)
        ├── xi15(15)
        │     └── xi_yioarybnkprcm5gut_2(0)
        ├── xiatop(48)          ← 地址/命令通路
        │     ├── xi_channel_nicap(2)
        │     ├── xi_ary16g_a_t(1)
        │     └── xi_ary16g_a_b(0)
        └── xictop(49)          ← 控制通路（≈ controller top）
              ├── xi_channel(3)
              │     └── xi_bcenter(0)
              │           └── xi_bcenterdq_695(5)
              │                 ├── xi5(0), xi12(1), xi93(3), xi103(4), xi122(6), xi798(29)
              ├── xi_t_sealringpath2_237(28)
              ├── xi_io_dqldmdl_232(26)
              └── xi_io_zqldmdl_234(27)
```

### ② controller 模块 — 不存在
- toplevel 直接子 scope = {xi0, xi5, xi15, xiatop, xictop}，无 "controller"
- xictop ≈ controller top（ctop = controller top），是语义最近匹配（但非子串匹配）

### ③ odt 信号 — 不存在
- `*odt*` 搜索 MATCHED: 430483，全是内部 `_*_void_pp` 节点
- `odt` 精确 / `*ODT*` / `*odt_en*` / `*rtt*` / `*termination*` 全 0 匹配
- 结论：该仿真未导出 odt 层级化信号

## 工具链
- read_files(sxcmd.log) → 解析层次
- run_approved_command(python-runner, waveview-fsdb-readerV2-2.py) → 信号搜索
- read_files(.err) → 读取 LSF 作业输出（MATCHED + void_pp 列表）

## 合成 case
- EDA-Eval-DesignFlow-FsdbScopeSignalLocate-001 (spice_sim A-faithful L1 k=14)
- A = sxcmd_A.log(真实 400 行 WaveView 命令日志) + sigsearch_A.log(真实 MATCHED:430483 + void_pp 样本)
- hidden B = sxcmd_B.log(合成不同层次 toplevel→xi0/xi3/xi21/xiaddr/xidqtop) + sigsearch_B.log(合成 *wen* MATCHED:5280 + _wen_int) + hidden_manifest.json(target=arbiter/wen)
- reference = analyze_fsdb_scope_signal_ref.py(解析 wv_*_tree_item @ 路径建层次树 + 解析 MATCHED + 内部信号判定)
- check.py 14 断言(a-n): 含交叉输入守卫(m: A scope_exists==false & count==430483 & A top_scopes=={xi0,xi5,xi15,xiatop,xictop}) + 3 次幂等(n)
