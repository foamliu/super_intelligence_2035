# 深读 c39j4 — NANDFP missing named-arg diagnosis (spice_sim A-faithful L1)

## trace
- anchor: 1792201884887_c39j4
- user: tongfanl @ hfhds201
- 67 msgs, 580KB
- dir-based session

## U#0（任务说明轮，逐字作 prompt · A-档选轮：提出需求"帮我看下啥原因"，无根因/修复）
```
抽激励报错，帮我看下啥原因。
抽激励脚本：./runsti/gen_stimulus_Aging
报错信息：
[COMMAND] /proj/.../bin/vsim -p dscqa/V0 -s -r Poststress001_Perbank_Datapath_..._FS -f 11600 -d "ANALOGVEC NOCHIP DOCKSYNCOFF SC0 MD_16b FS" -b X1P6 -l log/stimulus_tongfanl/Aging_1017_bank0_11600 --tool xrun -q rscalc
cp: cannot stat `/proj/.../sdf/*': No such file or directory
Job <901525> is submitted to queue <rscalc>.
...
xmvlog: *E,NANDFP (patterns/analogsim/Poststress/Poststress002_Perbank_Controller.v,101|82): Named argument not defined in formal argument list [SystemVerilog].
... (23 NANDFP errors total)
xrun: *E,VLGERR: An error occurred during parsing. ...
```

**NANDFP 错误分布（23 条）**：
- Poststress002_Perbank_Controller.v: lines 101,102,103,104,105,107,109,111 = 8
- Poststress003_Perbank_Controller.v: lines 5,8 = 2
- Poststress005_Perbank_IO.v: lines 54-66 = 13
- 总计 8+2+13 = 23

## 金标准 = assistant M#21 结论

**根因**：pattern 文件给 `Load_Mode` task 传了 `.ca43(...)` 命名参数，但 `Load_Mode` 的形参列表里没有 `ca43` → 全部 NANDFP (Named Argument Not Defined in Formal Parameter list)。

### 证据链
1. **`Load_Mode` 形参（ddr6_test.sv line 2674，symlink → bakup/bakup0929/ 9/29 版本）**：
```systemverilog
task Load_Mode(reg[MODEMA_BITS-1:0] ma, reg[MODEOP_BITS-1:0] op, reg bc=0, reg psd=0,
               reg[MODEOP_BITS-1:0] op_mark='1, bit rstall=0,
               bit forcewrite=1'b0, bit rank=0, bit cw=0, bit parity_errinject1=0, bit parity_errinject2=0,
               integer enops=0, bit wica_update=1, bit cmdcancel=0,
               bit get_lock=1, bit put_lock=1, bit psd_lock=1);
```
→ 17 个形参：ma, op, bc, psd, op_mark, rstall, forcewrite, rank, cw, parity_errinject1, parity_errinject2, enops, wica_update, cmdcancel, get_lock, put_lock, psd_lock
→ **没有 ca43**

2. **`MRR` 形参（ddr6_test.sv line 2936）有 ca43**：
```systemverilog
task MRR(reg[MODEMA_BITS-1:0] ma, bit termit=0, bit cw=0, ..., bit[1:0] ca43 = 1); // TODO: ca43 is not used!!!!!
```

3. **ddr6_test.sv.bak 注释（line 8185）**：
```
// TODO: tomtang change in 0929: ca43 not exist in Load_Mode anymore.
// Load_Mode(.ma('d130), .op({4'b0000,select_id}), .op_mark('b0000_1111) ,.ca43('d2) );
```
→ 9/29 改动把 ca43 从 Load_Mode 移除（迁到 MRR）

4. **23 处 `.ca43` 调用 ↔ 23 条 NANDFP 错误**（一一对应，一条不多一条不少）：
   - Poststress002: 101,102,103,104,105,107,109,111 (8)
   - Poststress003: 7,10 (2)
   - Poststress005: 54-66 (13)

## 合成设计

**通用化工具** `diag_nandfp.py <error_log> <task_def.sv> <pattern_dir> -o out.json`：
1. 解析 error_log：提取 NANDFP 错误 → {file, line, col}[]
2. 解析 task_def.sv：提取 `task <Name>(<params>)` 形参名
3. 解析 pattern_dir/*.v：找 task 调用的 `.name(value)` 命名参数
4. 交叉比对：调用中用了但形参里没有的命名参数 → missing_args
5. 输出 root_cause {task, missing_arg, call_count, error_count}

**A（真实）**：
- A_error.log = U#0 的 23 条 NANDFP 错误
- A_ddr6_test.sv = Load_Mode(无ca43) + MRR(有ca43) + MRUPD 三个 task 定义
- A_poststress/ = Poststress002/003/005 .v 节选（含 23 处 .ca43 调用）

**hidden B（合成，挡硬编码）**：
- B task = `Load_Cfg`（形参 10 个，无 `dqs_sel`）+ `Read_Cfg`（有 `bit dqs_sel=0`）
- B patterns = 不同文件名/行号，15 处 `.dqs_sel(1'b1)` 调用
- B error.log = 15 条 NANDFP 错误（不同文件/行/列）
- 缺失参数名 dqs_sel ≠ ca43，调用数 15 ≠ 23，task 名 Load_Cfg ≠ Load_Mode

## 判分 14 断言 (a-n)
a: zip 含 script + py_compile exit0 + out.json
b: py_compile exit 0
c: out.json 是 dict 含必需键
d: A 错误解析 = 23 条 NANDFP
e: Load_Mode 形参提取 = 17 个，无 ca43
f: MRR 形参含 ca43
g: .ca43 调用找到 = 23
h: root_cause.task == "Load_Mode"
i: root_cause.missing_arg == "ca43"
j: root_cause.call_count == 23
k: root_cause.error_count == 23（errors 与 calls 1:1 对应）
l: 交叉输入守卫：候选在 B 跑 → missing_arg=="dqs_sel" + call_count==15 + task=="Load_Cfg"（证泛化，挡硬编码 ca43/23）
m: A-only 未泄漏：B 输出无 ca43/Load_Mode/Poststress002
n: 3 次幂等 sha256 一致
