# 深读笔记 · 1793762292369_ue8qf · xxchen @ 10.129.2.11 · mc=12 · analog_context

**trace_source**: session_file `1793762292369_ue8qf`，user `xxchen`，host `10.129.2.11`，match_count=12
（keywords: netlist:29;synopsys:1;rtl:1）。kanban streaming log
`/home/xxchen/.cline/apps/kanban/sessions/1793762292369_ue8qf.jsonl`（1.59MB / 2360 行 stream）。
`.cline/data/sessions/` 下 `.messages.json` 已不在，user 原话不可逐字恢复（kanban 仅记录
model-side stream：chat_reasoning / chat_text / chat_tool_call_start/end / chat_done）。

## 真实任务（从 chat_done + tool_call 还原）

用户（xxchen）维护一个 SPF/DSPF 电阻追踪工具 `traceSPFresNode.py`，本轮需求：
**当 SPF 文件头部存在 `*LAYER_MAP` 块时，给电阻追踪结果的电阻表自动增加两列反标信息**：

- **layer**：由电阻行的 `$lvl=N` 参数回到 `*LAYER_MAP` 映射列表
  （形如 `*52 PCU_M0net ITF=PCU`）反查得到层名；无 `$lvl` 显示 `-`；映射表中不存在的编号显示 `lvl=N`。
- **spf_line**：电阻在 SPF 文件中的物理行号，可直接跳转编辑器定位。

输出表头（有 LAYER_MAP 时）：
```
# name           node1            node2            value_ohm    layer            spf_line
R4_241095      vdd2dq!:160054   vdd2dq!:158770   36.6465      PCU_M0net        2039684
R4_244005      vdd2dq!:283100   vdd2dq!:160054   126.669      PCNnet           2042594
R4_23563       XI_IO_...MMP1:DRN vdd2dq!:288516  0.001        PDnet_MOS        1822152
```

## 工具链 / 关键产物

- `traceSPFresNode.py`：流式 SPF parser（phase1_locate / phase2_parse_net / write_report_path / write_report_full）。
- 修改点：`phase1_locate` 捕获 `*LAYER_MAP` 映射表（70 层）+ 记录目标网 `*|NET` 行号；
  `phase2_parse_net` 新增 `net_line`/`want_meta` 参数，仅当存在 LAYER_MAP 时记录每个电阻的 `(行号, $lvl)`
  （无 LAYER_MAP 的文件零开销）；`write_report_*` 电阻表增加 layer + spf_line 列；报告头增加 `layer_map` 状态行。
- selftest：新增 11 项检查（映射条目解析、$lvl 提取、层名解析），共 25/25 PASS。

## 验证（agent 自报，chat_done）

1. selftest 25/25 PASS。
2. `DqPad.spf` + 指定节点（`XI_IO_DqIoTop...MMP1:DRN`，net `vdd2dq!`，424124 电阻）：路径 214 个电阻全部标注；
   独立交叉核对——用独立解析的 LAYER_MAP 对 214 行原始 SPF 行重新解析 $lvl 比对，layer 与行号全部一致。
3. 用户示例验证：`R4_241095` 的 `$lvl=52` → `PCU_M0net` ✓；`R4_23563` → `PDnet_MOS` 行 1822152 ✓。
4. 回归：`Channel_clips.spf`（无 LAYER_MAP）保持原 4 列格式不变。
5. full 模式：398484 个网络电阻同样带 layer/spf_line 列。

## B-grade 合成设计（SpfLayerAnnotate-001）

- **难度 L1**：纯 stdlib SPF 文本解析 + LAYER_MAP 反查 + 行号标注，无 EDA 运行时（与 D 域 #518-#535 parse-only 一致）。
- **A/B/C 不相交**：A（task_A.spf，可见，layer num 1-52，PCU_M0net/PDnet_MOS/...，R_A1-15，vdd2dq!/netA-M）/
  B（task_B.spf，hidden，layer num 2-68，VDD0net/GND0net/...，R_B1-15，vdd!/sa-mg）/
  C（嵌入 check.py 反硬编码，layer num 4-71，PWRAnet/GNDXnet/...，R_C1-15，pwra/extra）——
  layer 编号、层名、电阻名、节点名、值、物理行号**全不相交**，硬编码 B 必在 C 上失败。
- **回归子例**：no_layermap.spf（无 `*LAYER_MAP`）→ SUT 必须退化到 4 列（name/node1/node2/value_ohm），
  不加 layer/spf_line，验证向后兼容（对应 agent selftest #4 Channel_clips.spf 回归）。
- **边缘覆盖**：mapped $lvl（→层名）/ missing $lvl（→`-`）/ unknown lvl（→`lvl=N`）/ 0.001Ω short 电阻 / 多电阻同 $lvl。
- **check.py 15 条件 a-n + C**：独立 oracle 重新解析 B 计算 layer+spf_line（不 import SUT、不硬编码），
  逐列逐行比对；反硬编码 C 变体防 B 答案硬编码。

## 维度正交（非 dup）

vs D 域既有 SPF 家族：
- #506 SpfResPathTrace-001：min-total-R **路径**优化（Dijkstra）——本 case 是 **layer 反标**，机制不同。
- #509 SpfCapResAnomaly-001：cap/res **异常检测**——本 case 是 **元数据回填**。
- #516 SpfRccShieldDiff-001：两文件 **RCC shielding 差异**——本 case 单文件 **LAYER_MAP 映射**。
- #534 SpfTrueShortScan-001：per-element **0.001Ω true-short 分类**——本 case **层名+行号标注**。
本 case 维度 = SPF LAYER_MAP back-annotation（layer name via $lvl + physical spf_line），与上述四者正交，非重复。
