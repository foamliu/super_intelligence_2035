# Deepread: 1795420854701_fxwte (yh1yang @ hfeg0plg94)

**Session**: 1795420854701_fxwte.messages.json
**User**: yh1yang
**Host**: 10.129.8.226 (hfeg0plg94)
**mc**: 164 (aether:1202;pyaether:648;cellview:335;netlist:69;schematic:59;dbget:26;waveview:24;calibre:23)
**Domain**: layout_aether
**Msgs**: 97
**Date**: 2026-11-23

## Task arc

1. **[msg 0-29] GUI bridge listing**: 用户要求通过 aether bridge 列出当前打开页面的 instance。assistant 搜索 API 发现 `aeGetWndCellViewId` → `emyDesign.instances` → `emyInst.{name,libName,cellName,viewName}`。编写 `list_current_window_instances()`，在沙箱中测试成功，列出 `work/lvls/schematic` 的 5 个 instance（2 个 drvqa_cmos_core 电平移位器 + 1 输入 pin + 2 输出 pin）。`design.instCount`（5）与 `len(instances)`（5）交叉验证一致。

2. **[msg 30-38] 代码讲解**: 用户问 py 代码实现。assistant 讲解三步：定位设计 → 遍历实例 → 提取信息。

3. **[msg 39-63] 独立进程调试**: 用户反馈本地 `python list_current_window_instances.py` 报错。assistant 深入排查：
   - 发现沙箱 Python 父进程 = `/apps/.../bin/aether -adv`（PID 25818）→ **沙箱代码跑在 Aether GUI 进程内部**
   - 独立进程 `aeGetWndCellViewId` 返回 None（无 GUI 上下文）
   - `emyInitAether('-adv')` 初始化本进程 Aether 环境（加载 aether.ini/display.drf），但**不连接已运行 GUI**
   - 之后 `aeGetWndCellViewId` 仍返回 None，报错 "The wnd is not specified"

4. **[msg 64-76] emyDesign.open 解决方案**: 改用 `emyDesign.open(lib, cell, view, 'r')` 从磁盘读 cellview。
   - 第一版直接传 raw string → SWIG 重载解析失败（C++ 原型要求 `emyScalarName` 类型）
   - 查找 `emyNativeNS`（原生命名空间构造器）+ `emyScalarName(ns, name)` 包装
   - 修正后 `pythone list_instances_by_name.py work lvls schematic` **独立进程成功列出 5 个 instance**，与 GUI 内查询一致

5. **[msg 77-96] 架构讨论**: 用户追问 bridge vs TCP 协议、自建 server 的取舍。assistant 解释：
   - `aeGetWndCellViewId()` 等是官方 API（SWIG 封装 C++ 层）
   - bridge run_code 是 in-process 执行通道，TCP 只是传输
   - bridge 适合 agent（可容忍 fetch-correct-resubmit 循环）
   - pyAether API 文档在服务器上（685 HTML 文件）

## Key APIs

| API | 用途 |
|---|---|
| `aeGetWndCellViewId(focus=False)` | GUI bridge: 获取当前窗口 design（仅 GUI 进程内可用） |
| `emyInitAether('-adv')` | 独立进程初始化 Aether 环境 |
| `emyNativeNS()` | 构造原生命名空间 |
| `emyScalarName(ns, name)` | 将 str 包装为 emyScalarName（SWIG 严格类型要求） |
| `emyDesign.open(lib, cell, view, 'r')` | 从磁盘以只读方式打开 cellview（类方法） |
| `emyDesign.instances` | 返回所有 instance 的元组 |
| `emyDesign.instCount` | instance 总数 |
| `emyInst.{name,libName,cellName,viewName}` | instance 属性 |

## Deliverable

最终脚本 `list_instances_by_name.py`：
- `emyInitAether('-adv')` → `emyNativeNS()` → `emyScalarName(ns, lib/cell/view)` → `emyDesign.open(...)` → `design.instances` → 提取属性

## Case synthesis

**Case ID**: AetherStandaloneInstList-001
**Domain**: layout_aether
**Track**: B (hidden B design, anti-hardcode B2)
**k_check**: 14
**Mock approach**: check.py 注入 mock pyAether 模块（模拟 API + 记录 call log），在纯 Python 环境验证 API 调用链 + 输出正确性，无需真实 Aether。
