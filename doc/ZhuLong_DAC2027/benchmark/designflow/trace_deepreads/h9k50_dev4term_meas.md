# Deepread: 1795083114382_h9k50 (yh1yang @ hfeg0pkn003)

**Source**: r915 698-machine rescan (2026-11-20), session created 2026-11-19 18:11 (after 11/19 17:21 scan).
**trace_source**: user=yh1yang, host=hfeg0pkn003, session_file=1795083114382_h9k50.messages.json, match_count≈518, real_task_summary=见下。
**Domain**: spice_sim (HSPICE device current measurement deck)。
**Size**: 821KB / 286 msgs / 164 user msgs。
**Status**: claimed (r915), 待合成 (DEBT r916)。

## 用户真实意图（原话）

> /home/yh1yang/workspace/V2_TF/leak/test.sp
> 我有一个spice 仿真需求，要求对于多个器件，在指定的电压下测量四端电流，当前我已经写好了器件定义，电压条件，但是meas语句只是示例，并不能测量四端，请你看看，评估下怎么写

> 可以开动，请注意，一切尽量简洁，只要有每个器件四端电流即可，避免错误

**真实任务**：用户已写好 HSPICE deck `test.sp`，包含多行器件（ptnlvio_sa / ntnlvio_sa / ntnlvio_csl / ntnlvio_iso / ntnlvio_preeq / ntnlvio_oc ...），每行器件有 d/g/s/b 四端电压源（vdN/vgN/vsN/vbN）。但 `.meas` 只测了 `idN find i(vdN)`（漏端电流）。要求：为每个器件补齐**四端电流测量**（idN/igN/isN/ibN，分别 find i(vdN)/i(vgN)/i(vsN)/i(vbN) at=0），保持 deck 其余结构（器件定义、电压条件、.lib/.option/.param/.dc）不变，尽量简洁、避免错误。

## 关键产物 / 工具链

- 输入文件：`/home/yh1yang/workspace/V2_TF/leak/test.sp`（HSPICE deck，多器件 bias table）
- agent 动作：editor 逐行插入 `.meas dc igN/isN/ibN find i(vgN|vsN|vbN) at=0`，保留原有 `.meas dc idN` 与器件/电压行
- deck 结构：`.lib ... tt` / `.temp 25` / `.param sweep=0` / `.dc sweep 0 0 1` / 每器件一组 `xN ... vdN/vgN/vsN/vbN` + 4 条 `.meas`
- 模型：V2B_HK_Model_D5_v0d1_Rev02_t01.sp（ptnlvio_sa / ntnlvio_sa / ntnlvio_csl / ntnlvio_iso / ntnlvio_preeq / ntnlvio_oc ...）

## 合成计划（v2 case，待 r916 执行）

- **case_id 拟**：`DevFourTermMeasGen-001`（spice_sim, A 档 trace-faithful）
- **prompt**：用真实用户原话（test.sp 路径 + 四端电流 meas 需求），A 档不脱敏。
- **交付物**：`outputs/submit.zip` 内含改后的 `test.sp`（每个器件 4 条 .meas：id/ig/is/ib）。
- **hidden B**：与 A 不同规模/取值——更多器件行 + 不同 W/L/bias 组合（仍 ptnlvio/ntnlvio 系列），验证脚本泛化。
- **check() 思路（≥8 断言，k 条断言格式）**：
  1. zip 解出含 test.sp
  2. .lib/.temp/.param/.dc 框架保留且与 B 一致
  3. 每个器件行 xN 存在且 dN/gN/sN/bN 四端电压源齐全
  4. 每器件有 `.meas dc idN find i(vdN) at=0`
  5. 每器件有 `.meas dc igN find i(vgN) at=0`
  6. 每器件有 `.meas dc isN find i(vsN) at=0`
  7. 每器件有 `.meas dc ibN find i(vbN) at=0`
  8. meas 总数 = 器件数 × 4（一一对应，无遗漏/无多余）
  9. 器件实例名/模型名/W/L 未被改动（与 B 比对）
  10. 无重复 meas 名、无语法错误（.meas 名唯一）
  - 真跑候选：用 hspice/nanosim 或 grep+parse 解析 .meas 名与 find 目标一一对应；若沙盒有 hspice 可真跑 deck 取 .mt0/meas 输出断言 4 列存在。
- **负样本**：(a) 空壳 test.sp 原样回传 (b) 只补 id 不补 ig/is/ib (c) 把 ig/is/ib 的 find 目标写错（i(vd) 重复）—— 全 FAIL。
- **§4.9 三假**：empty / print-expected / core-removed 全 FAIL。

## 备注

- iyoge (yinyus, hspice:4988) 为下一备选：WaveView 电流数据 → PWL 电流激励（ivblh vblh! 0 pwl(...) 加在 120us 后），任务清晰可造，留 r917。
- joeyl 6jie5/t0xdo/pbkq1/5v4tq/lxzq1 + vckxz(joeyli) 为 opamp characterization 同簇 near-dup（netlist~1100/hspice~93/opamp:24），合成 1 即可，余 park。
- keviny amgmv/sn7gv/chwbc/dd6sb/zynq7/1ajdv/c68lg 7 兄弟同簇（aether:698/pyaether:124），1 造余 park。
