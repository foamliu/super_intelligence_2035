# c4wsu — /block-design 8-bit 3-depth FIFO (junxu@hfeg0pkn005)

## trace 溯源
- session: `1788845188396_c4wsu` · user `junxu` · host `hfeg0pkn005` (10.129.2.14) · mc=155
- model `glm-5.2` (cxmt-glm52), interactive, 2026-09-08 05:26 → 09-09 01:11 (~20h), status=failed (exit 1, stale_session_reconciler)
- cwd `/home/junxu/.cline/skills/virtuoso-cli`, 112 msgs, messages.json 749554 B
- scan keywords: virtuoso:663 schematic:494 cellview:39 dbopencellviewbytype:21 cmos:21 dbcreaterect:10

## 用户真实意图（逐条用户消息）
1. msg0: `/block-design 在 cli_test_lib 中设计一个 8 位，3 深度的 FIFO` — 用 virtuoso-cli skill 在 Cadence 库 cli_test_lib 里设计一个 8 位宽、3 深度的 FIFO 原理图
2. msg47: `FIFO FIFO 是先进先出队列，不是移位寄存器` — 纠正 agent 第一版做的移位寄存器
3. msg50: `是有现成的 D 触发器可以用的，你再仔细检查一下` — 纠正 agent "库只有锁存器" 的误判
4. msg67: `把构建脚本放到 /home/junxu/Agents/cli_test` — 指定交付路径
5. msg70: `1. 你在滥用 stub 桥接 2. connect_by_name 可以自动决定 stub 方向` — 纠正布线滥用

## agent 工具链与产物
- 读 SKILL.md + Python API 参考 → 连 Virtuoso → dbOpenCellViewByType 探 cli_test_lib（含 1 个 stub_test 单元，仅 1 个 invx1）
- 搜 stdcells_am 标准单元库：先只找到 latqx1/latrqx1（锁存器）+ mx2x1，**误判无 DFF**
- 第一版：用 2×latqx1 拼主从 DFF 做"移位寄存器 FIFO"（8 位 3 级 + WE），schCheck 0 错 → 用户否决（msg47）
- 用户提示后找到 ffrqx1/ffsqx1/ffrsqx1 DFF（D,Ck,CkN,Q,RN 异步复位正沿），以及 mx3x1(3:1)/mx4x1(4:1) one-hot mux
- 第二版（真正 FIFO）：3×8 ffrqx1 存储阵列 + 2 位 wptr/rptr（0→1→2→0 回绕）+ 2 位饱和 up/down count(0..3) + EMPTY=(count==0)/FULL=(count==3) + 写 one-hot 译码(WE0/1/2 gated by inc=WE&~FULL) + 读 3:1 mux(mx3x1 per bit, one-hot RS0/1/2)
- 布线迭代：26 错 → 9 → 5 → 0 错（修正 connect_by_name stub 滥用 + 不显式指定 dir1 + dy≥5 间距）→ 删 2 个多余 count 反相器 → 0 错 0 警 → 生成 symbol view + 连接性验证全过
- 交付：`/home/junxu/Agents/cli_test/build_fifo_8x3.py`（443 行，已在该 session 后被清理，但完整架构见 msg55/59/111）

## 关键设计事实（用于合成 case）
- 库 cli_test_lib + stdcells_am；cells: ffrqx1(D,Ck,CkN,Q,RN) / mx3x1(S0,S1,S2,A0,A1,A2,Y) / mx4x1 / invx1/2/4 / and2x1 / or2x1 / xor2x1 / nand2x1 / nor2x1 / bufx1 / latqx1
- 8 位 3 深：storage=3×8=24 ffrqx1；ptr_bits=2（值 0,1,2 回绕 2→0）；count_bits=2（0..3）；read mux=8×mx3x1；write one-hot=3（WE0/1/2）；ports DIN<7:0>/DOUT<7:0>/CLK/RSTN/WE/RD/EMPTY/FULL
- 用户核心纠错三连：① 必须是指针式 FIFO 不是移位寄存器 ② 库里有现成 DFF ③ 不要滥用 stub 桥接

## 合成方向
- case_id: EDA-Eval-DesignFlow-FifoStructNetlistGen-001（shard D / schematic）
- 内核：可离线判分的 FIFO 结构化网表生成器。SUT 写 `gen_fifo_netlist.py`，读 spec(width,depth)+cell_catalog，产出结构化 netlist.json（instances[inst,cell,pins] + ports + pointer{wrap_at,next_state} + flags + decode）
- A: width=8 depth=3（mx3x1）；hidden B: width=4 depth=4（mx4x1，ptr wrap at 4 自然二进制）
- check 真跑 SUT 脚本于 B，断言：①storage=width*depth 全 DFF ②wptr DFF 数 ③rptr DFF 数 ④count DFF 数 ⑤read mux=width 个 depth:1 mux ⑥ports 齐全 ⑦pointer.wrap_at==depth（非 2^ptr_bits）⑧flags empty/full 表达式 ⑨write one-hot=depth gated by inc ⑩3 次确定性 md5 ⑪B 与 A 结构性不相交（反 hardcode_a）
- §4.9 三假：print_only(硬编码 A 网表)→⑪ FAIL；core_deleted(空壳)→① FAIL；hardcode_a→⑪ FAIL
