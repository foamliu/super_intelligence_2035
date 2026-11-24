# trace_deepread: yklyt (e04201 @ hfeg0plg18, mc103) → Lp5CmdVectorTableProduce-001

**session**: 1794994099059_yklyt.messages.json (638KB, 152 msgs, subdir sessions/<sid>/<sid>.messages.json)
**user**: e04201 @ hfeg0plg18 (172.16.8.163)
**domain**: verification (LPDDR5 ATE pattern gen, verilog:118+systemverilog:18 dominant, A-pure)
**keywords**: netlist:170;verilog:118;drc:32;systemverilog:18;cmos:14;synopsys:10;schematic:10;pex:3

## 用户真实意图（多轮 Q&A 演化）

- U#0: 读 netlist `/proj/ddjoc/V0/simdir/verilog/PTE/e0014408/.../netlist`，生成能 toggle 信号 `TOP.Chip...I_WrApBaFifoUnit_71.net063` 的测试时序
- U#54: 要用 LPDDR5 JEDEC Truth Table 里规定的 command 生成命令时序
- U#88: 文件里只下 2 次 ACT，后面下了 24 次 WRA，WRA 怎么生效
- U#96: 做 ATE 测试，得通过读取数据判断测试结果
- U#116: **Read 前打开的 Row 已经被 WRA 关闭了，这合理吗？**（关键协议点）
- U#126: 同步
- U#132: 输出的文件在哪里
- U#134: 感觉越写越乱了 → 收敛到 net063_work/README.md 单一入口
- U#144: **不要输出 verilog 格式，输出格式**（关键格式点）
- U#146: 确认 = 命令时序向量表（以 tCK 为单位的命令/地址/期望数据 ASCII 表格，可直接抄进 ATE 脚本）

## 最终交付物

`/home/e04201/net063_work/net063_command_vectors.md` — ASCII per-tCK 命令向量表，含：
1. 编码约定（ACT/WRA/RD/NOP 语义 + CA 字段 + tRCD/nWR/tRP/nRL 参数化）
2. 写侧向量表（ACT→tRCD→WRA(AP=1)→nWR+tRP，bank2/bank0 交替 toggle bit1）
3. 读回向量表（重开行 ACT→tRCD→RD→nRL→比 DQ→PASS/FAIL）
4. ATE 伪代码（loop + 期望值判据，非 Verilog）
5. 协议说明（WRA 自动预充电关行→读前必重 ACT；过早 PRE 截断写突发→后段列读回失配 FAIL）

## 造题决策

- **A档不可行**：真实 netlist 在 `/proj/ddjoc/` 沙箱不可达，638KB trace 远端文件无法沙箱化 → **B档 synthesized**
- 合成 signal_spec（目标信号+bank 对+toggle bit+row/col+BL+fault+cycles）+ jedec_table（命令集+参数化时序）
- A: net063/bank2,bank0/bit1/rowA/col AA/cycles=2/timings tRCD2 nWR4 nRL2
- hidden B: net128/bank3,bank1/bit0/rowC/col 5C/cycles=3/timings tRCD3 nWR6 nRL3（零判别 token 相交）
- 工具 gen_command_vectors.py 通用生成器（读两 JSON→markdown 向量表），check 跑 B 验结构
- 用户明确拒绝 Verilog → check 断言无 verilog 关键字
- 关键协议点（重 ACT/突发截断）作为独立断言
- k=13, ref PASS 13/13, §4.9 三假(empty/print-only/core-deleted)全 FAIL, neg_selftest OK, determinism 3x md5 一致
