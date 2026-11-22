# deepread: 1794814550267_x1ekr (shanliny@hfeg0plg107, mc=49, physical_verify/PEX)

- **user**: shanliny — 物理验证工程师，做 PEX/DSPF 后仿真 RC 可视化
- **tool**: rc_viz_gui.py (Tkinter GUI, ~1403 行) + rc_viz_tool2.py (matplotlib PNG 引擎) — 把 DSPF 网表每根走线对地电阻画成 log10(R) 配色 PNG，叠黑点(RC 节点)/彩块(器件)/金★(R 端点)/标记环
- **附件**: rc_viz_gui.py, rc_viz_tool2.py, HD1P_CXN4S1P256X288M1B1C1R1W1BW1RE1.dspf.TYPICAL_-40 (PEX DSPF 网表)
- **187 msgs / 7.8MB**

## U#1 (msg 0) — 扁/窄走线视野钳制（本题取材点）
bug: 走线特别扁(宽>>高, DLB[2] 23.5um×0.119um)或窄(高>>宽)时，`ax.set_aspect("equal", adjustable="box")` 强制等比例 → axes 物理尺寸压成细缝。
- DLB[2] 实测 axes ≈ **6.96 × 0.04 英寸**：
  - log10(R) 色条(挂 axes 上, 高=axes 高/宽=15%) → 0.04in 细缝, 渐变不可见, 刻度叠压
  - 标志物固定磅(黑点 5pt/彩块 10pt/金★ 20pt/标记环 16pt), axes 一细被边缘 clip
- 根因: 视野(xlim/ylim 跨度)纵横比没下限, padding 按数据跨度百分比给, 细长方向换算英寸≈0
- **修复**: `clamp_view_aspect()` 把视野纵横比钳制到 `[1/N, N]`(默认 N=4, `--max-aspect` 可调), 过扁/过窄时**短边方向视野对称外扩**(长边不动, 中心不变)
- 钳制后 DLB[2]: 视野 30.56×7.64, axes ≈ **6.96 × 1.74 英寸** → 色条+标志物均可读
- 正常比例用例输出与 before **完全一致**(1482×553 px 不变)
- 验证: numpy 1.21.6 / matplotlib 3.5.1 / PIL 8.0; before/after 跑批 + 钳制函数单测 + GUI 模块导入

## U#3 (msg 69) — eog 弹图 + GUI 历史
- PNG 输出名留空 → 跑完直接 `eog` 弹临时预览图(/tmp/rc_viz_preview.png, 不占存储); 填了名 → 存正式结果
- `auto_outputs()` 不再自动预填 PNG 输出名(只预填 xlsx); `build_cmd()` 留空走临时+eog; `_finish_run()` 成功且临时模式调 `_eog_open()`(eog 优先, 退回 xdg-open/gio)
- GUI 历史: 每次跑记录全部参数, 可点击恢复

## U#4 (msg 104) — --devices 标注筛选语义改
- 留空 = 一个器件都不标注(原 return True → 现 return False); `*` = 全部标注; 子串过滤不变
- xlsx 总览字段同步(留空显示"不标注", `*` 显示"全部(\*)")

## U#5 (msg 130) — 5 项大重构
1. 历史持久化到**可见文件** + 启动自动读取 + 导入/导出(原只是临时存储, 关程序就丢)
2. 删 PNG 内嵌预览
3. 彻底删 xlsx 相关功能(工具+GUI, 1069→795 行)
4. 交互预览支持**图上单击选节点测 R**(原交互预览没挂画布, 空窗口, 一并补全)
5. PNG **重合节点编号徽章** + 图例注明上下关系(越靠近器件越靠下, n1 与器件 0Ω 直连排最下)

## U#7 (msg 183) — 交互预览坐标吸附 + 路径长度 + 重合图例精简
- 吸附节点时把显示坐标也吸附到节点上
- 测量时展示两点坐标 + 计算两点间路径长度
- 只有**被标记的**点存在重合时才在标签区解释重合点(原无论标不标都展示所有重合点, 臃肿)

## 子型与正交性
- 子型 `rc_viz_view_aspect_clamp`(matplotlib axes 视野纵横比钳制 + 标志物 clip 判定) **首例**
- 与既有 C case 正交: 既有是 LVS/DRC deck 解析/网表枚举/schematic 构建/skill 审查/GDS 操作/pyAether 环境; 本题是 **PEX RC 可视化工具的视野几何钳制**(纯 matplotlib 几何, 不调 EDA API)
- session exit=1(failed_external_process_exit)但交付物落盘

## 合成取向
取 U#1(视野钳制)做档 B reframe fixture-driven: agent 写 `rc_view_clamper.py` 读 trace manifest JSON(bbox/padding/figsize/max_aspect/markers) → 算 raw_view/clamped_view/aspect_before/after/axes_inches/per-marker fits → JSON 报告。
- visible env_A = DLB[2] 扁走线(23.5×0.119um, N=4, figsize 6.96×4.0) — 数值与 trace 原文一致(6.96×0.04in→6.96×1.74in)
- hidden env_B = WLB[3] 窄/高走线(0.15×28um, N=5, figsize 5.0×7.0) — 几何正交(扩 X 不扩 Y), 防 env_A 记忆
- check.py 15 断言(a-o): zip合法/py_compile/env_B运行/13顶层键/原始纵横比<1:N/钳制后∈[1/N,N]/clamp_axis=='x'/X扩H不变/中心不变/all_fit/钳制必要性(raw短边<最大标志物直径)/反硬编(net/design为B值且源码无DLB|23.5)/scale重算/3-seed字节一致/源码>500B
- ref PASS 15/15; 3 neg distinct FAIL: neg_empty→(o) / neg_echo_stub→(e) / neg_hardcode_a(delete-core,钳制neutralized)→(f)
