# trace_deepread: z9qr1 (dorisz · hfeahpc505 · spice_sim)

- session: `1795081207513_z9qr1` (10.129.33.28, hfeahpc505), 56 msgs / 128KB
- user: dorisz; scan: r915 698-rescan 41 fresh B-domain sids, ranked #2 by hspice score=9
- domain: spice_sim (DDR5 Vblhbk PDN 仿真 PWL 电流激励 deck 编辑)

## 真实任务（3 步 user_input）

**msg0 — 重组 iload_all → AIiload**:
> `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/dorisz/ddgoa/Vblhbk/pdn1/iload_all` 帮我把这个文件里边：
> 1.a和b标志行的<14><15><10><11>，c和d标志行的<0><1><4><5>；
> 2.a和b标志行的<12><13><8><9>，c和d标志行的<2><3><6><7>；
> 3.a和b标志行的<0><1><4><5>，c和d标志行的<14><15><10><11>；
> 4.a和b标志行的<2><3><6><7>，c和d标志行的<12><13><8><9>；
> 整理一下，分别放在一起，中间分隔，建立一个新文件叫AIiload

真实输入 `iload_all`（67 行）= iloada/b/c/d 四段×16bit PWL 电流激励行，双 Tab 分隔：
`iloada<0>\t\tiloada<0>\t\t0\t\tpwl\t\tpwlfile='./iload64' td=100u r=0n`（`<10>`+ 行带行尾 Tab）。
agent 用 `make_aiiload.py` 按 4 组 bit 表重组 → AIiload（64 数据行 + 6 空行 = 70 行，组间 2 空行）。

**msg22 — 每组行尾 td/r 参数化**:
> 把生成的这个文件第一组每行的 td=100u r=0n 改成 td='t_delay+tager*0' r=280n，第二组 *1，第三组 *2，第四组 *3

agent 用 `modify_aiiload.py` regex 替换 `td=\S+ r=\S+` → `td='t_delay+tager*K' r=280n`，每组 16 处。

**msg30 — PDN.ploc 纵坐标修改**（本 case 未取，留作另题）:
> pdn2/PDN.ploc 所有 iloada 行纵坐标改成 1724.17，所有 iloadb 行纵坐标改成 1693.45

## 合成决策

取 (1)+(2) 做 **参数化生成器** `aiiload_gen.py`（reframe-harness-for-teeth）：
- 一次性 deck 编辑 → 参数化 `iload_all + spec.json -> AIiload`
- hidden B 异信号名(iporte/iportf/iportg)/异 bit 数(12)/异组数(3)/异 pwlfile(./port_pulse)/异 td-r 方案(td_phaseK, r=150/150/200) → 验通用性 + anti-hardcode-A
- 用户真实意图（PWL deck 重组 + 按组 td/r 参数化）保留

## 真实性证据

- 经 .75 SSH scp 取回 z9qr1.messages.json 全文（128KB/56msg）
- 从 read_files tool_result (msg9) 逐行重建真实 iload_all（64 行 + 分段空行 + 行尾 Tab 全保真）
- 从 msg28 重建真实 AIiload（参数化后）→ 参考解 aiiload_gen.py 在 A 上产出与真实 AIiload 结构逐行一致
- prompt 含 dorisz 原话逐字（msg0 重组表 + msg22 td/r 参数化）
- 路径/信号名/pwlfile/采样值全保真，未脱敏

## 质检

- check.py 15 断言 (a-o)，参考解 PASS 15/15 on hidden B
- 5 negatives (empty/print/core/hardcode_a/nosort) 全 FAIL
- §4.9 三假 (empty+print+core-removed) 全 FAIL
- k_rationale == k_check == 15 (≥8 闸门 ✓)
- trace_source 齐全，判分器不入 SUT workdir (check 读 assets/hidden/B，SUT 只见 A)
