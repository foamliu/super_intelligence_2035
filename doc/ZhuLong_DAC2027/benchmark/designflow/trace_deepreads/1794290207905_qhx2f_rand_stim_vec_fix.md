# Deepread — 1794290207905_qhx2f (cliu @ hfhds209, mc336)

- **session**: 1794290207905_qhx2f, user cliu, host hfhds209 (autofs 镜像多 host), scan ssh_eda_search_20261113_131349
- **规模**: 515 msgs / 278 user-role / 22 real user_input turns
- **域**: digital (verilog std-cell TB stimulus generator); summary 的 lvs:1560/drc:501/netlist:637 关键词来自 simlib_drcoa_stdcells.sv cell 名含 LVS/DRC 字样, 非实际 LVS/DRC 工具调用
- **可读性**: ssh hfhds209 cat /home/cliu/.cline/data/sessions/<sid>/<sid>.messages.json 目录格式 OK

## 会话主线
cliu 用 rand_stim_gen.py 为 std-cell 网表生成受约束随机激励 SV TB。脚本解析 `celldefine/endcelldefine` 块、module 端口方向、识别互补对(base/baseN)、时钟主脚、异步脚、rail 供电脚, 生成带反相/异步/tie 约束的 K 个随机向量 + 自包含 TB。

### real user turns (节选)
- U#1: 「请参考 @/home/wellesc/runStdCellTB/tb_family 把 @rand_stim_gen.py 测试下 @tb_oai21CSColx2.sv」(首次测试)
- U#2/U#3: 生成波形 / 波形改 .trn
- U#4: 同法测试 tb_invLV_DQx2.sv, .trn
- U#5/U#6: 用 rand_stim_gen.py 测试 simlib_drcoa_stdcells.sv 里的 latqYx1/nand2IOLVx1_pc60_wrap/invGF_EccStage12, 结果打印 @/home/cliu/rand_test/result
- **U#7 (核心 produce-task)**: 「发现，lat/latn输入非相反的关系，且不管任何cell，Vec都是64，应该根据module的input pin来组合出Vec帮忙修正脚本@/home/cliu/rand_test/rand_stim_gen.py脚本，新脚本命名为rand_stim_gen_new.py」
- U#8/U#9/U#10: 用修正后的 rand_stim_gen_new.py / 原 rand_stim_gen.py 继续测各 cell
- U#11: 调试 rules_prompt02.py (gateway 503)
- U#12/U#13: 看 rules_prompt.py 不能转 final_merged_netlist_digitial_lose.v 的 cell
- U#14: 分析 [MISMATCH] xrun.log
- U#15-U#22: 「把 cell 仿真波形出来放 /home/cliu/rand_test_1111@, .trn 格式」(批量复用)

### U#7 agent 修正 (rand_stim_gen.py → rand_stim_gen_new.py, diff 93 行)
两处核心 bug 修正:
1. **时钟脚不再反相 (修正 A)**:
   - compl_pairs: 若 base 匹配 CLK_RE(lat/clk/ck 等) → continue, 不建反相对; B 后缀也不配对。数据互补对(A/AN, S/SN, En/EnN, D/DN)仍配对。
   - clock_main: 恒为 ''(不再设时钟主脚), lat/latn 作为独立输入进 drive_pins。
   - 注释明确: 「lat/latn、clk/clkn、ck/ckn 等时钟脚不是互补关系, 一律不配对」
2. **Vec 按 input pin 全组合 (修正 B)**:
   - 新增 _expand(model, v) helper: 反相派生 + 异步去使能 + 缺省 0
   - gen_vectors(model, n, seed, tie): n<=0 → 对 drive_pins 全组合 K=2^W(code 0..2^W-1, bit 取 drive_pins 顺序); n>0 → 按 seed 随机 n 个
   - --n 默认 64 → 0; print 加 K/W/drive/compl/clock/async
- 其余(split_netlist, RAIL, emit_tb, run_one, main CLI)不变

## B档合成决策
- deliverable = 改 /home/cliu/rand_test/rand_stim_gen.py → 私有路径, SUT 沙盒不可达 → INFEASIBLE → B档合成
- A-faithful: 用户给脚本+网表+bug 描述+修正方向, 未给解析算法/全组合实现/CLK_RE → 合格
- 自包含: 原脚本 NET 硬编码 /home/wellesc/ 路径 → B档改 --net <path> CLI; 保留 split_netlist/CellModel/compl_pairs/clock_main/gen_vectors 结构与 bug
- A/B 网表: cell 名零重叠(A-suffix vs B-suffix), pin 名模式同(lat/latn, A/AN, clk/clkn, En/EnN, R/RN), 一 supply 脚不同(vcc vs vss)
- 判分: import SUT 脚本 → split_netlist(B) + CellModel + gen_vectors 函数级验证 + subprocess 真跑 CLI --dump 解析; 18 条件

## case
- EDA-Eval-DesignFlow-RandStimVecFix-001 (digital L1-B, k=18, archetype=stdcell-stimulus-generator-clock-indep-and-exhaustive-vec-fix)
- 自验: ref SELFTEST PASS 18/18; 5 neg + 3 fake 全 FAIL(NEG_RC=0)
- ledger: 1794290207905_qhx2f → case
