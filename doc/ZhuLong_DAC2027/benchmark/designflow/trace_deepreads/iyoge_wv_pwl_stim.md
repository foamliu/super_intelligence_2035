# Deepread: 1795086710598_iyoge (yinyus @ hfeahpc505)

**Source**: r915 698-machine rescan (2026-11-20), session created 2026-11-19 19:11 (after 11/19 17:21 scan).
**trace_source**: user=yinyus, host=hfeahpc505, ip=10.129.33.28, session_file=1795086710598_iyoge, match_count≈4988, real_task_summary=见下。
**Domain**: spice_sim (HSPICE 瞬态电流激励 / WaveView 电流波形 → PWL)。
**Size**: 910KB / 216 msgs / 6 user msgs / 112 tool_use。
**Status**: claimed (r917), 合成落库为 EDA-Eval-DesignFlow-WvCurPwlStimGen-001。

## 用户真实意图（原话）

> msg[0]: /proj/drcpa/V0/simdir/hspice/yinyus/vblh_SF/sim/tran/current_ability/ivblh_idd5b2.sp 读取这个文件 然后写成电流激励 形式仿照ivblh vblh! 0 pwl(0 0 120u 0 120.001u 2mA) 规则如下 将上面的数据写成的电流激励加在120us之后
>
> msg[3]: (同上) 文件保存为 .../ivblh_iloadIDD.sp
>
> msg[35]: 对这个进行修改 改成挂在200us之后 直接改文件
>
> msg[50]: 从 finesim.fsdb 提取 isub(inh_vblh) 高精度波形，再按上面要求修改 ivblh_iloadIDD.sp
>
> msg[185]: 总结你这里转化的操作 用到skil了吗
>
> msg[187]: 你这个做的就很好，帮我转化生成skill，注意特别是关于代码建立一个可复用的...

**核心原始意图 (msg[0]/msg[3])**：把 Custom WaveView 导出的电流表 `ivblh_idd5b2.sp` 转成 HSPICE PWL 电流激励，整条波形平移到 120us 之后开始，t=0 给 0 锚点，每个采样点 `t_i -> t_i + shift`，保存为 `ivblh_iloadIDD.sp`。msg[35/50/187] 是后续衍生（改 200us / 高精度重提 / 转 SKILL），本 case 取原始核心意图。

## 关键产物 / 工具链

- 输入文件：`/proj/drcpa/V0/simdir/hspice/yinyus/vblh_SF/sim/tran/current_ability/ivblh_idd5b2.sp`（Custom WaveView 表：`#format table` 头 + `XVAL xi_...isub(inh_vblh)` 信号行 + 13829 个 `时间[s] 电流[A]` 采样点，时间 0..202.46us，电流 -1.65mA..125mA）
- agent 动作：editor 写 `gen_ivblh_pwl.py`（解析 WaveView 表 → 发射 `ivblh vblh! 0 pwl(` 头 + `0 0` 锚点 + 每点 `(t+SHIFT, v)` 科学计数法 + `)`），SHIFT=120e-6（后改 200e-6）；写 `validate_ivblh_pwl.py` 自验（点数/严格递增/时间范围/min-max current）。
- 输出格式（agent 实现，用户 msg[187]「做的就很好」认可）：
  ```
  ivblh vblh! 0 pwl(
  0 0
  <shift+t0> <v0>
  ...
  )
  ```
  锚点 `0 0` + 平移后的全部采样点，时间 `%.12e` 科学计数法，严格递增。

## 合成计划（已执行 r917）

- **case_id**：`EDA-Eval-DesignFlow-WvCurPwlStimGen-001`（spice_sim, A 档 trace-faithful, layer L1）
- **reframe**：harness-for-teeth — trace 原意图=one-off deck 生成；判分有牙需参数化通用 CLI，故 reframe 成 produce 参数化 `pwl_current_gen.py`（任意电流表/平移量/节点名）。
- **CLI**：`python3 pwl_current_gen.py <input_wv> <output_sp> --shift <SEC> --isrc <NAME> --nodep <P> --noden <N>`
- **asset A（可见）**：`ivblh_idd5b2.wv`（真实 WaveView 表，下采样 37 点，0..1.17us，-0.85mA..68mA，isub(inh_vblh) 信号）+ `task_brief.md`。
- **hidden B**：合成 WaveView 表，120 点（0..5.95us 严格递增 50ns 步进，-1.5mA..80mA 脉冲，isub(ivdd) 信号），shift 150us，isrc iload / nodes vdd,0。与 A 在信号/点数/时间范围/电流范围/平移量/节点全异 → anti-hardcode-A。
- **check.py 12 断言 (a-l)**：zip 含脚本 / B 上 exit0 非空 / 确定性 / 头行匹配 CLI / `0 0` 锚点 / `)` 末行 / 对数=N_B+1 / 时间严格递增 / 每点平移正确(t_i+SHIFT,v_i) / 数据 token 科学计数法 / 无重复时间 / shift-respect+anti-hardcode-A（SHIFT2=200us 重跑时间==t_i+SHIFT2，B 点数 120≠A 37）。
- **负样本 (5)**：neg_empty(§4.9a) / neg_print(§4.9b 硬编码 A 37 点) / neg_core(§4.9c 只发头+锚点+尾无数据) / neg_noshift(忽略 --shift) / neg_hardcode(硬编码 A 数据)。
- **自验**：ref PASS 12/12；NEG 5/5 全 FAIL（含 §4.9 三假 empty/print/core-removed 全 FAIL）；确定性（两次运行逐字节一致）。in-place check.py selftest PASS。

## 真实性

- 经 .75 SSH scp 取回真实 messages.json（910KB/216msg），解析 6 条 user 原话 + 112 tool_use。
- 真实输入文件 ivblh_idd5b2.sp 因权限 e0031982 不可直读，从 trace 的 read_files tool_result 提取真实内容（1661 行可见段，#format table 头 + XVAL isub(inh_vblh) 信号 + 真实采样点），下采样 37 点作 asset A（真实值保真非脱敏）。
- trace_source 可溯源：user=yinyus / host=hfeahpc505 / session=iyoge / mc=4988 / r915 rescan ranked #1。

## 备注

- iyoge 为 r915 rescan 41 fresh 之一（ranked #1 by hspice kw 4988）；本 case 用 1，余 40 fresh。
- 下次候选：r915 ranked #2 qlvgs(xiuqiy hspice:4986) — 同 hfeahpc505 同项目，需先 peek 判是否与 iyoge near-dup。
