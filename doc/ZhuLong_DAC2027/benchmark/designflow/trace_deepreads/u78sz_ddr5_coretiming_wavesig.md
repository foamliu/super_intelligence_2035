# 深读：1793087996513_u78sz — DDR5 fullchip array coretiming 波形信号提取

- **session**: `1793087996513_u78sz.messages.json` · user `hengbow` · host `hfeg0pgn045` · mc=407
- **keywords**: synopsys:1013（finesim/PrimeSim 仿真 + WaveView/Verdi 波形）
- **trace 位置**: `/home/hengbow/.cline/data/sessions/1793087996513_u78sz/`（目录含 `<id>.messages.json`，511 msgs）
- **真实产物**（`/home/hengbow/zl_job/turboWave/fsdb/`，已 scp 到沙盒存档）:
  - `finesim.fsdb` 2.1GB（DDR5 fullchip PrimeSim/finesim 仿真波形，不打包）
  - `sig_demo.sig` 1069B（用户给的 **格式参考**：`signal = <hier>.v(<name>)`）
  - `_clean.sig` 3367B（**初始/raw 信号列表，混合大小写**：CK_t / CS_n / CA<13> / LDQPad / ColAdr_B0 / ActEn_B_B0 / BlaMq00 …，用户实测**大写信号 load 不到**）
  - `01_top_pad.sig` / `02_read_pad.sig` / `03_controller.sig` / `04_array_addrB0.sig` / `05_array_bl.sig`（按类别拆分的中间产物）
  - `all_signals.sig` 2165B（汇总，含顶层 CA/读 pad/控制器/行地址 Ra10/Ra10GapIn）
  - `coretiming_signals.sig` **2747B（最终交付金标准）**：array coretiming 关键信号，**全小写**，5 节（电源/参考/时钟[注释掉] · SA/均衡/列选 · BL/BLB · WL · Dummy WL）

## 用户真实意图（A 档逐字，仅掩码）

1. 「当前环境如何 mav 软件版本，比如我要用 verdi 看波形，怎么 ma 这个软件」
2. 「你有什么方法可以解析 fsdb 波形吗」
3. 「我有一个 ddr5 fullchip 的仿真波形，想要检查一下 array 中的 coretiming 以及时序有没有违例，需要帮我找到开启的地址对应哪个 wl 和 BL @/home/hengbow/zl_job/turboWave/fsdb/finesim.fsdb」
4. 「@/proj/drvqa/.../仿真环境在这，你帮我找一找，但是不要修改里面的内容因为这是公共目录」
5. 「帮我给出 关键信号的路径 list，这样我在 waveview 下直接 load 就能查看」
6. 「@/home/hengbow/zl_job/turboWave/fsdb/sig_demo.sig 这是我打印的一个 list 示例，你帮我把你找的信号也弄成这种格式，放在这个路径下」
7. 「load 之后只有两个信号有效，其他信号都找不到」← **关键反馈：raw 大写信号 load 不到**
8. 「字母都是小写」← **硬要求：信号名全小写**
9. 「我给的只是参考，不是真实的关键信号，你基于你分析的关键信号重新给」

> A 档任务说明 = 用户提出需求的轮（3/5/6/8/9），不含已指出根因的轮（7「load 之后只有两个信号有效」是根因反馈，作 hint 不进 prompt）。

## assistant 工具链（真实）

- 读 WaveView 文档 `/apps/synopsys/wv/T-2022.06-SP1/doc/wv_docs/index.htm`
- 读仿真目录 `/proj/drvqa/V0/simdir/finesim/drvqaF/MatrixRun/...` 找 hierarchy
- 用 shell grep/awk 解析 netlist 提取 hierarchy 信号路径
- 反复迭代：raw `_clean.sig`（大写）→ 拆分类别 → 全小写 `coretiming_signals.sig`
- WaveView ACE Tcl（`wv -ace_no_gui`）验证信号可 load（sxcmd.log 18661B 记录）

## 关键事实（断言只对这些）

- **格式**：`signal = <full_hierarchy>.v(<signalname>)`，顶层信号 `signal = v(<name>)`
- **小写硬要求**：raw netlist 大写（CK_t / CS_n / CA<13> / LDQPad / S54M0WLEU）→ 必须 lowercase 才能 load
- **array coretiming 5 类**：① SA/均衡/列选(preeqbotin/ocentopin/sapenatopin/isotopin/cslmsaqs) ② BL/BLB(bla/blb) ③ WL(s<sec>m<mq>wle/wlo[u/l]) ④ Dummy WL(dumwl…) ⑤ 电源/参考/时钟(注释掉)
- **A hierarchy 前缀**：`xictop.xi_array8g_t.xi_array1g_bgab01.xi_m512meg_0`；SA 在 `xi_lwdrq_msaq_5455`；BL 在 `xi_lwdrq_msaq_5455.xi_msaq_2sec_0001.xi_msax256_cp00.xi_cxsa_1x16_cbcc_1c2a_1`
- **WL 命名**：`s<sec>m<mq>wle[u/l]` / `s<sec>m<mq>wlo[u/l]`，sec∈{53,54,55}，mq∈{0,2,4,6}；A 共 13 条 WL
- **gold = coretiming_signals.sig**（2747B，真实最终产物）

## 合成方案（A 档 trace-faithful · L1 离线静态 + subprocess 候选）

- **任务说明**：用户原话轮 3/5/6/8/9 拼接（A 档，不补全不脱敏）
- **A 附件**：`sig_demo.sig`（格式参考·真）+ `hierarchy_manifest_A.txt`（raw netlist 信号全路径，**混合大小写**，含顶层/控制器/行地址 decoy + array coretiming 真信号）+ `user_request.md`（用户原话）
- **隐藏 B**（不进 SUT 沙箱）：`hierarchy_manifest_B.txt`（结构性不同：前缀 `xiatop_a1.xi_ary8g_a_t.xi_ary1g_g0.xi_m512meg_b02`、msaq 实例 7777、WL sec/mq 不同 t12/t13/t14、6 条 WL vs A 13 条、BL bit<5> vs <11>、cslmsaqs01<31> vs cslmsaqs00<63>）+ `hidden_manifest.json`
- **交付契约**：`outputs/submit.zip` 含 `coretiming_signals.sig`（A 输出）+ `gen_coretiming_sig.py`（生成器，check 在 B 上 subprocess 重跑）
- **check.py 17 独立标签 (a)-(q)**：zip 完整 / py_compile / .sig 格式 / 全小写 / SA≥4 / 列选 cslmsaqs / BL·BLB / WL≥10 / WL 跨 sec×mq / dummy WL / A 前缀一致 / B 候选 CLI 重跑 / B 前缀≠A / B 小写格式 / B WL 计数匹配 manifest / 无 A 专属 token 泄漏 / B 类别齐全 / 随机化(3 seed shuffle → 信号集合一致)
- **negative**：3 §4.9 假 + 2 naive（fake_empty→c / fake_print_expected[硬编码 A coretiming_signals.sig]→m / fake_core_deleted[不 lowercase]→d / naive_no_wl_filter→h / naive_hardcode_a_wl→o）
- **L1 判分**：offline 静态 .sig 解析 + subprocess 跑候选 python（无 EDA 工具，无需 WaveView/finesim）

## 难度（B 档目标 20–30%）

L1 偏易但断言 ≥8 + 隐藏 B 跨输入 + 随机化 + lowercase 陷阱（raw 大写 netlist）拉到合理难度。A 档试点：忠实原话、不补全「格式/类别/小写」之外的实现提示。
