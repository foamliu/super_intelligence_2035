# xv1ip — DDR5 TX PODL IO driver 线性区 Ron 表征 + sizing-to-target 深读笔记

- **trace**: `1792647604577_xv1ip.messages.json`，user `alenxu`，host `hfeg0pkn003`，match_count 186
- **规模**: 489 msgs，关键字 hspice:88 / ron:42 / sizing:35 / linear:22 / podl:18 / driver:30
- **领域判定**: characterization + spice_sim（HSPICE DC 线性区 Ron 表征 + W/M sizing-to-target；与 NmosAgeChar/VihTripTune/TaperBufOpt 同 family，本 trace 独特点=IO driver 反相器上拉/下拉 Ron 提取 + 按 Ron∝1/W_total 缩放 finger multiplier 命中目标 Ω）

## 用户 substantive prompts

1. **T0（通道单脉冲响应）**：alenxu 让 agent 对 DDR5 TX PODL 输出驱动器通道做单脉冲响应仿真。
2. **U61（Ron 查询）**：查询反相器上拉（PMOS）/下拉（NMOS）导通电阻。
3. **U115（sizing-to-target）**：「如果需要使上拉下拉导通电阻为 120 欧，n管与p管尺寸为多少」——核心 sizing-to-target 子任务，本 case 抽取的目标。

## flow 主线（agent 做 IO driver Ron 表征 + sizing）

```
读 foundry netlist (ptn_lv/ntn_lv, l=39n) + 模型
  ↓
HSPICE .dc 线性区扫描 (VDS→10mV) 测 baseline Ron = VDS/|Id|
  ↓ PMOS 上拉: source=vddq, gate=0, body=vddq, VDS=vddq−V(drain)
  ↓ NMOS 下拉: source=0, gate=vddq, body=0, VDS=V(drain)
  ↓
解析 .measure id_x/vd_x (SI 后缀 u/n/m)
  ↓
按 Ron∝1/(W·M) (线性区, L 不变) 算 target_totalW = baseline_totalW × (baseline_ron/target_ron)
  ↓ 新 M = round(target_totalW / W), W/L 保持 baseline
  ↓
对 sized 上拉/下拉各再跑 HSPICE .dc 验证 achieved Ron ≈ target
```

trace 用 foundry BSIM 模型（ptn_lv/ntn_lv l=39n，本环境不可移植），agent 手动跑 HSPICE + 解析 + 改 sizing。本 case 抽取「线性区 Ron DC 提取 + 按 Ron∝1/W_total sizing-to-target」这一可复用 L2 内核，便携化为 level-1 Shichman-Hodges MOS + 自生成 corner.lib + HSPICE .dc/.measure harness。

## HSPICE 调用方式（本 case 抽取的可复用子流）

- 二进制：`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice64`
- 调用：`hspice64 -i <stem>.sp -o <stem>`，cwd=deck 所在目录，产物 `<stem>.lis`
- 线性区 Ron deck 结构（PMOS 上拉为例）：
  ```
  .lib 'corner.lib' tt
  Vdd vddq 0 <vddq>
  Vg g 0 0
  M1 d g vddq vddq ptn_lv W=<W>u L=<L>u M=<M>
  Vd d 0 DC 0
  .dc Vd <vddq-0.05> <vddq-0.001> 0.001
  .measure dc id_x find i(Vd) at=<vddq-0.01>
  .measure dc vd_x find v(d) at=<vddq-0.01>
  .end
  ```
  VDS = vddq − V(d) ≈ 10mV（线性区），Ron = VDS/|Id|。
- NMOS 下拉：gate=vddq, source/body=0, sweep Vd 在 0 附近，VDS=V(d)≈10mV。

## .75 HSPICE 排雷（本 case 踩对的关键点）

1. **level-1 MOS 元件必须 `M1` 非 `XM1`**：HSPICE 把 `X` 前缀当 subckt 调用 → 报 model not found。
2. **`.MODEL` 须放 `.LIB tt ... .endl tt` 块 + `.lib 'corner.lib' tt` 加载**：顶层裸 `.MODEL` 在本 build 报 not found。
3. **`.measure` SI 后缀解析**：输出 `id_x = 76.3382u` 带 SI 后缀，须后缀感知 parser（u→1e-6, m→1e-3, n→1e-9），裸 `float()` 把 `76.3382u` 解析成 76.3382 而非 76.3382e-6，Ron 算错 6 个数量级。
4. **check.py run_dir 须 abspath**：相对路径在子进程改 cwd 后断。
5. **线性区 vs 饱和区**：VDS 必须取小值（≈10mV），不是 vddq/2。饱和区 Id 恒定，Ron=VDS/Id 偏大且与 sizing 关系不成立。
6. **PMOS/NMOS 极性**：上拉用 ptn_lv（source=vddq, gate=0, VGS=−vddq ON），下拉用 ntn_lv（source=0, gate=vddq, VGS=+vddq ON）。极性写反 → 管子截止 Id≈0 Ron 失真。

## distinct vs 已有 B case

- NmosAgeChar=单管 Vtlin/Idlin/Idsat 表征
- VihTripTune=判别器翻转点 4 宽度调优
- TaperBufOpt=多级 buffer 驱动比 DOE PDP
- InvTripDelay=testbench 激励撰写（tpd/vtrip measure）
- **本条=IO driver 反相器线性区 Ron 提取 + W/M sizing-to-target 命中目标 Ω**（shard B 首见 sizing-to-Ω-target 子技能）

## 便携化参数（A/B）

- **A（可见）**: vddq=1.2, kp_n=100, kp_p=40, vto_n=0.5, vto_p=−0.5, baseline pu W=10 L=0.5 M=40, pd W=5 L=0.5 M=20, target_ron=120Ω → achieved 119.84Ω (pu&pd)
- **B（隐藏）**: vddq=1.0, kp_n=80, kp_p=35, vto_n=0.45, vto_p=−0.45, baseline pu W=8 L=0.6 M=30, pd W=4 L=0.6 M=15, target_ron=200Ω → achieved pu=196.5Ω / pd=202.3Ω (均 ±12% 内)
- A/B 全异（vddq/kp/vto/baseline sizing/target 全不同），跨输入守卫成立。

## case 交付

- task_id: EDA-Eval-DesignFlow-TxRonSize-001
- check.py: 16 条断言 a-p（zip/py_compile/run/method/keys/baseline-match×2/achieved-match-via-independent-rerun×2/target-hit×2/sizing-changed×2/cross-input-guard/polarity/determinism）
- 候选: tx_ron_size.py（CLI <params.json> <report_out.json>，真跑 HSPICE）
- negatives: 6 个（empty/hardcode_a/print_expected/no_search/swap_polarity/wrong_region）全 FAIL，§4.9 三假全 FAIL
- .75 端到端 negative_selftest ~3.3s：ref **PASS 16/16** + 6 neg 全 FAIL（NEG_RC=1：swap_polarity 与 wrong_region 共享 {f,g,h,i,j,k} 失败集，§4.4 要求全 FAIL 非严格互异，可接受）
- test==disk check.py md5 aee7bb6013ffde25f719f7de5e5a4023 12225B roundtrip OK
- 断言闸门 k_rationale=k_check=16≥8 ✓
- ledger xv1ip claimed→case，covered 44→45，spice_sim 34→35，追加 EDA-Eval-DesignFlow_B.jsonl 第 48 行
