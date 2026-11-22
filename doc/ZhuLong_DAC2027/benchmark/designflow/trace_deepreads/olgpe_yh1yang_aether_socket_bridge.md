# Deepread: olgpe — yh1yang external pyAether socket-bridge nav (layout_aether)

- **session**: 1795003959776_olgpe (yh1yang@hfeg0plg94/10.129.8.226, mc=189, aether:828/pyaether:614/schematic:239/lib.defs:194 dominant → layout_aether)
- **forked from**: fiknl (carried HANDOFF.md context). 139 msgs/581KB. exit=1 (failed_external_process_exit) but deliverables landed on disk.
- **real intent**: 从外部独立 python 进程控制运行中的 Aether GUI —— 列出/导航当前打开的 schematic（器件、pin、当前路径、下钻/返回）。headless，不刷窗口。

## 三种执行模式（yh1yang 踩出来的选型地图）
| 模式 | 进程 | 拿当前设计 | 适用 |
|---|---|---|---|
| GUI Python Console | 就是 Aether 会话 | `aeGetCurDesign()` 直接拿 | 在已开界面里跑逻辑 |
| `pythone xxx.py` | 另起全新会话 | `emyInitAether`+`aeOpenDesign(lib,cell,view,"readOnly")`（需 CWD `lib.defs`） | 按名字批量处理某库 |
| **官方 socket 桥** ⭐ | 外部进程 → 运行中 Aether | 命令在 Aether 会话内执行，天然拿当前图 | **外部驱动当前界面** |

关键洞见："GUI 里打开了" ≠ "独立进程能读"。`pythone` 另起进程看不到 GUI 已开的设计；跨进程只能靠"同会话"或"官方 socket 桥"。

## 库解析
- `aeOpenDesign("work","lvls","schematic","readOnly")` 里的 `work` 是库名，靠运行目录 `lib.defs` 解析（`DEFINE work /proj/drvqa/V0/workdir/yh1yang/work`）。
- yh1yang 从 `/home/yh1yang/Desktop` 跑 pythone 失败：Desktop/lib.defs 空 → `work` 无法解析 → open design failed。
- `work` 真实路径 `/proj/drvqa/V0/workdir/yh1yang/work`（标准 OA 库，含 cell `lvls/schematic`）。

## 官方 socket 桥（最终采用）
- API: `aeSetCmdPort(PORT)` + `aeRunCmdWithSocket("work","lvls","schematic","","",False,rcb)` + `SleAeSocketRequestCallback` 子类 `funcCbWithReturn(self, request)` 回调 `eval(request, ns)` 返回 `repr`。
- Aether 侧 `server_start.py`：在 GUI Python Console 里 `exec(open('server_start.py').read(), globals())` 启动。回调把外部命令当 pyAether 表达式 `eval`，返回 `repr`（只能单表达式，不能多行语句/赋值）。
- 外部 `client.py`：TCP 连 127.0.0.1:PORT，收首帧 banner，发 `cmd + "\n"`，收 `repr(result)`。
- 端口冲突：10005 被占 → `aeRunCmdWithSocket` 返回真实端口 10015；客户端须连打印的端口。固定用 `aeSetCmdPort(PORT, closeOldPort=True)`。

## 协议指纹（关键发现）
- 官方 `aeRunCmdWithSocket`：客户端一连上，服务器**立刻发明文 `viewer_connected` 信号**（API 文档 Note 原文："Upon establishing a successful socket connection, the server immediately transmits a 'viewer_connected' string signal to the client."）。banner 实测：`viewer_connected hfeg0plg94 10015 hfeg0plg94:1048.0 Empyrean:Aether 4.6 language tcl ...`。
- `10.129.8.226:38813` 是**私有 JSON 桥**（非官方）：首帧是 `{"response":"The code execution failed","error_log":"Failed to receive message length","print_log":""}`（JSON + 长度前缀，字段 response/error_log/print_log，正是 run_code 沙盒桥那套）。`probe_bridge2.py` 测了 4B_BE/4B_LE/8B_BE framing 均对不上 → 判定非官方。
- 判据：首帧 `viewer_connected` 前缀 ⇔ 官方协议；JSON dict 含 `response` ⇔ 私有桥。

## 样例设计 work/lvls/schematic
- 2 R 器件：`I_R_lvlVcc2Vwlpx1_SaCtrol_0` (R_lvlVcc2Vwlpx1_SaCtrol)、`I_R_lvlVcc2Vwlpx1_5` (R_lvlVcc2Vwlpx1)
- 3 pin：PIN0(in)、PIN1(out)、PIN2(out)
- 下钻 `I_R_lvlVcc2Vwlpx1_SaCtrol_0` → 37 内层器件（MP*/MN* mosfets）（HANDOFF 记录，本 session socket 桥只验证了 list/cur，descend/back 留作 ⏳ 后续）

## 落地交付物 /home/yh1yang/coding/p/
- `server_start.py` — Aether 侧官方 socket 服务器（含 SleAeSocketRequestCallback 回调，eval-based）
- `client.py` — 外部官方协议客户端（TCP，banner 收，cmd\n 发，repr 收）
- `lib.defs` — DEFINE work → /proj/drvqa/V0/workdir/yh1yang/work
- `list_insts_standalone.py` — pythone 独立版（aeOpenDesign by name + 列器件，过滤 pin）
- `a.py` — GUI Console 版（aeGetCurDesign 列当前图器件）
- `README.md` — 经验总结 + 三模式对比 + 官方方案用法 + 8 条坑
- 已删：`a.py~`/`probe_bridge*.py`/`lvls`/`.aether_log/`/`_cleanup.py`/`_rm.py`

## 关键坑
1. 库解析靠 CWD `lib.defs`；`pythone` 独立进程必须 `emyInitAether`+`aeOpenDesign`。
2. `aeGetCurDesign()` 只在 Aether 会话内有效。
3. **脚本一律纯 ASCII**：中文在 `exec(open(...).read())` 里 `UnicodeDecodeError: 'ascii' codec`（0xe5）。
4. 缩进别靠粘贴：多行代码拖进 Console 被剥缩进 → IndentationError；用 `exec(open(path).read(), globals())` 从磁盘原样读。
5. 官方协议指纹 = 首帧 `viewer_connected`；私有 JSON 桥（response/error_log/print_log）不是官方。
6. 端口被占时 `aeRunCmdWithSocket` 返回新端口，客户端须连打印的端口。
7. 别反复 `aeOpenDesign` 刷窗口，验证优先复用 `aeGetCurDesign()`/socket。

## 合成方向
档 B reframe fixture-driven — agent 写 `aether_bridge_client.py`（纯标准库）：连 TCP server → 协议指纹检测（viewer_connected 官方 vs JSON 私有桥）→ banner 解析 → 发 pyAether 表达式（newline framing）→ ast.literal_eval repr → 结构化 JSON 导航报告（cur/devices/pins/count_insts/all_insts，sorted 确定性）。check.py 起官方 mock server（hidden env_B: drvqa_lib/AmpTop, 4 devices + 4 pins，不同 banner/host/version/lang）+ 私有 mock server，跑 client 断言。子型 `aether_socket_bridge_nav_client` 首例。
