# Deep-read: 1788932035519_3dm7z (junxu @ hfeg0pkn005, mc=348)

**Claimed**: 2026-11-23 (shard D, schematic_netlist)
**Trace host/IP**: hfeg0pkn005 (10.129.2.14)
**Session file**: `/home/junxu/.cline/data/sessions/1788932035519_3dm7z/1788932035519_3dm7z.messages.json` (1.28 MB, 338 msgs)
**Keywords**: virtuoso:797;schematic:624;cellview:72;dbopencellviewbytype:56;cadence:47;adexl:12;opamp:4;rtl:3

## 用户真实意图（提炼）

用户（junxu，virtuoso-cli skill 的开发者）报告 `build_fifo.py` 构建的 FIFO 原理图中 **DOUT 和 FULL 两个 output pin 的方向不对，"看上去像是 input pin"**，要求优化 API。

经排查，根因在 virtuoso-cli schematic API 的 `add_pin` 方法（`schematic.py:828`）：**stub wire（短桩线）方向不区分 pin 方向**——无论 input 还是 output，stub 一律向右（+x）延伸。output pin 放在原理图右边缘时，stub 朝外（向右），视觉上和 input pin 的箭头方向一致，无法区分。

用户明确澄清："pin 是对的，不要改成 ipin 和 opin"——即 master cell（`basic/in`、`basic/out`）选择正确，问题纯在 **orient 与 stub 方向**。

## 关键发现 / 工具链

- assistant 最初提议 output → `orient="MY"`（Y 轴镜像），但随后用户澄清 master cell 不变，assistant 修订为更优方案：**保持 R0（因为 basic/in 与 basic/out master 在 R0 下箭头方向本就正确），只修 stub 方向**。
- 最终实现：
  1. `orient` 默认从 `"R0"` 改为 `"auto"`。`"auto"` 对所有方向（input/output/inputOutput/switch）都解析为 `"R0"`。
  2. `_ARROW_DELTA` 映射 effective orient → 箭头增量：R0→(+1,0)、R90→(0,+1)、R180→(-1,0)、R270→(0,-1)、MX→(+1,0)、MY→(+1,0)、MXR90→(0,+1)、MYR90→(0,+1)。
  3. **stub 方向**：input 跟随箭头；output 对箭头 (dx,dy) **同时取反**（指向电路体内）；inputOutput/switch 同 input（不取反）。
  4. `justify="auto"`：stub_dx<0 → `"lowerRight"`，stub_dx>=0 → `"lowerLeft"`。
  5. 显式 orient 覆盖 auto；非法 direction/orient/justify 抛 ValueError。
  6. master_cell 映射不变：input→in、output→out、inputOutput→iopin、switch→iopin。
- 测试新增：`test_add_pin_auto_orient_output`（output auto→R0，stub 朝左）、`test_add_pin_auto_orient_input`（input auto→R0）、`test_add_pin_explicit_orient_overrides_auto`（显式 R180 覆盖）。
- 后半程是 python 环境调试（默认 python 损坏、找 python3.11/3.12、pytest 不可用改用 unittest）——环境噪音，非核心交付。

## 造题方向（已合成）

- **L1 case**：`EDA-Eval-DesignFlow-PinOrientStubFix-001`。
- 附件 A（可见）：`add_pin_bug.py`（buggy 原始实现，展示 API 契约与三处 bug）+ `pin_spec_A.json`（FIFO 7 个 pin：4 input + 3 output）+ `task_brief.md`。
- 隐藏 B：`pin_spec_B.json`（ADC 控制块 10 个 pin：4 input + 3 output(auto) + 1 inputOutput + 1 switch + 1 output(显式 R180)）——与 A 结构性不相交（不同模块、不同 pin 名、不同方向组合、不同数量、含显式 orient）。
- 候选交付 `pin_orient_fix.py`：导出固定后的 `add_pin` + `main(pin_spec_path)` 读 JSON 打印结果数组。
- **check.py 15 条独立断言**（a-o）：zip 合法+py_compile / B 跑通长度=10 / output stub_dx<0 / input stub_dx>0 / inputOutput 不取反 / switch 不取反 / auto→R0 / 显式 R180 覆盖 / master_cell 映射 / justify 解析 / 反硬编码 A 跑通且 pin 数≠B / stub_dy R0 时为 0 / 非法 direction 抛错 / 3 次确定性 md5 一致。
- 自验：reference 15/15 PASS + 3 负样本（print_only/core_deleted/hardcode_a）全 FAIL。

## 本轮处置

- 台账：claim 3dm7z → mark case `EDA-Eval-DesignFlow-PinOrientStubFix-001`。
- D.jsonl 556→557。
- 域：schematic_netlist（L1，离线 Python 复刻 add_pin 方向逻辑 + stub 方向计算）。
