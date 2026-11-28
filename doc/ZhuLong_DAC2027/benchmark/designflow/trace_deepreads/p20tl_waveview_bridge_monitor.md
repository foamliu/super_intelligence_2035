# 深读笔记 — 1795504679287_p20tl (jun1he@hfeg0pkn004, mc=239, waveform)

## 源 trace
- session_file: `1795504679287_p20tl.messages.json` (872KB, 258 msgs, 147 user / 111 asst)
- user: jun1he ; host: hfeg0pkn004 ; NEW D 用户
- domain: waveform (Synopsys WaveView TCL bridge + FSDB/.ma0 monitor plan)
- 关键词: waveview:738;pyaether:209;synopsys:142;analog:128;aether:67;hspice:60

## 用户真实意图（逐字）
- U#0: 「使用python语句操作连接现有的waveview窗口，并进行连通性测试，给出精简的代码」
- U#82: 「使用刚刚的代码打开一个波形文件：.../a15_presim_tran_pvt_Shft_1001.fsdb，画出Vad2BIRef的波形」
- U#133: 打开 PSRR .ma0 测量文件 + 8 个 db_psr_* 测量波形 + 「我想要添加3个cursor monitor,分别为maximum,minimum,avg」
- U#239: 「AVG 列仍为空」(踩坑后反馈)

## 核心（agent 逆向 + 实测）

### 1. WaveView TCL bridge 线协议（实测破解）
- 端点: `~/.cline/data/settings/ip_port.json` 的 `"tcl"` 项 `{"ip","port"}`
- 端口规律: bridge 在 wv 进程内监听 `20000 + (uid*10010) % 45533`
- 请求帧: **4 字节大端长度 + 纯 TCL 载荷**（无 JSON 包装，载荷直接当 TCL 执行）
- 回包: JSON `{"response","error_log","print_log"}`，回完即关连接
- 服务端日志: `~/.zl/waveview/zhulong_wv_server.log`（`SERVER_READY listening on <port>` = 在线）
- 踩坑: 裸文本/换行发 TCL → `invalid message length`；载荷包成 JSON → 整个 JSON 串被当 TCL 执行报 `invalid command name "{\"code\":...`

### 2. 精简客户端 wv_client.py
```python
import json, os, socket, struct
CFG = os.path.expanduser("~/.cline/data/settings/ip_port.json")
def wv_send(tcl, timeout=8.0):
    with open(CFG) as f: ep = json.load(f)["tcl"]
    data = tcl.encode()
    with socket.create_connection((ep["ip"], ep["port"]), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(struct.pack(">I", len(data)) + data)  # 4B BE length + TCL
        out = b""
        try:
            while True:
                chunk = s.recv(65536)
                if not chunk: break
                out += chunk
        except socket.timeout: pass
    return json.loads(out.decode())
# 连通性测试
r = wv_send('puts "ping-from-python [expr {40+2}]"')
# print_log="ping-from-python 42", error_log=""  -> CONNECTED
```

### 3. FSDB/ma0 打开 + 画图序列（实测每步）
```tcl
set f1 [sx_open_sim_file_read "/path/x.ma0"]   ;# 返回文件对象列表
sx_current_sim_file $f1
set wdf [lindex $f1 0]
set w [sx_add_wv]                                ;# 新建 wv 窗口
sx_current_wv $w
# 每信号一 panel:
set p [sx_new_panel]
set wh [sx_find_wave_in_file $wdf "db_psr_100"]
sx_append_line $p $wh
sx_update_wv $w
```

### 4. ★ 关键坑：MAX/MIN/AVG cursor monitor
- `sx_add_monitor <panel> -atype <MAX|MIN>` — 只接受 MAX/MIN
- **`-atype` 完全不校验类型串**：传 `AVG`/`BOGUS` 都返回句柄，但非法类型不参与计算 → **列存在但永远空白**
- AVG 正确做法（Monitor Settings 对话框 token，从 wv 二进制 strings 挖出）：
```tcl
set m [sx_add_monitor $p]                      ;# 不带 -atype
sx_config_monitor $m CursorAverage UsePanelSetting FullSignalRange 1
```
- `sx_config_monitor(monitor_obj, analog_monitor, logic_monitor, x_range, scale_factor)` 五参数与 GUI 对话框字段一一对应；同样不校验，写错 token 静默空列
- Analog Monitor 度量类型 token: `CursorValue` / `OneOverDerivative` / `YDelta` / `CursorAverage` / `PeakToPeak`
- X-axis Range token: `FullSignalRange` / `ZoomedViewRange` / `CursorRange` / `UserDefinedRange`
- Logic Monitor token: `UsePanelSetting` / `RiseEdgeCount` / `FallEdgeCount` / `BothEdgeCount`
- 排查方法论: RAG/API 手册查不到的命令，依次 (1) 对活解释器 `info commands sx_*monitor*` 内省；(2) 无参调用拿 usage 报错；(3) `strings` 翻 GUI 二进制找对话框 token 表

### 5. 其他踩坑
- `_5258ae8_void_pp` 这类句柄有效（void_pp = void 指针类型签名后缀，不是空句柄）；判空看 sx_signal 是否抛错/返回空串，不要 `string match "*void*"`
- 画图不需要句柄：`sx_display "<信号全名>" -auto_new_wv` 按名字直接画
- HSPICE FSDB 节点名被小写化: `Vad2BIRef` → `v(vad2biref)`
- 不要通过 bridge 调 `sx_dump_wv`（窗口图像导出）—— 实测把整个 WaveView GUI 进程搞崩
- `wm title .` 报 `application has been destroyed`：bridge 解释器存活、`sx_*` 命令集完整（374 个），但 Tk 主窗口可能已销毁，GUI 专属 Tk 操作不可用，波形数据操作不受影响

## case 合成（task_id=WvBridgeMonitorPlanProduce-001, LIVE-NA, judge_layers=[L0,L1]）
synthesized-reframe: live WaveView binary + bridge + X display 不可沙盒 → spec 驱动 plan 生成器 `wv_monitor_plan.py`（纯 stdlib）。
- **A**(visible) spec_A.json: bridge 10.129.33.34:29967, sim_file a15_presim_psrr_pvt_Shft_1001.ma0, 8 信号(db_psr_100..1g), monitors=[MAX,MIN,AVG]
- **hidden B**(token-structurally 不同) spec_B.json: bridge 10.129.33.99:30188, sim_file bgr_psrr_ac_pvt_Slow_0500.ma0, **6** 信号(含 db_psr_10, 无 10meg/100meg/1g), **4** monitor(含 PTP) → A 硬编码器在 B 全错
- **reference** wv_monitor_plan_ref.py: build_frame(tcl)=4B BE 长度+TCL / parse_reply(raw)=JSON dict / gen_plan(spec)=TCL 序列 + monitor_records（MAX/MIN 走 -atype，AVG/PTP 走 no-atype + sx_config_monitor CursorAverage/PeakToPeak）
- **check.py 15 conds(a-o)**: a zip 含 py ②b py_compile ③c 反空壳≥400B ④d A 运行产 report_A.json ⑤e 帧协议 ping_frame_hex 前 4 字节 BE 长度==len(PING_TCL) 且 payload==PING_TCL + 独立 gold frame 字节一致 ⑥f sx_open_sim_file_read(spec_A.sim_file) ⑦g sx_add_wv+sx_update_wv ⑧h sx_new_panel 计数==8 + 每信号 sx_find_wave_in_file ⑨i -atype MAX×8 ⑩j -atype MIN×8 ⑪k sx_config_monitor CursorAverage×8 + sx_add_monitor 无-atype≥8 ⑫l 负闸门无 -atype AVG ⑬m 隐藏 B signals/monitors==spec_B ⑭n PTP 走 PeakToPeak×6 + B 引用 B sim_file 非 A + B panel==6 反硬编码 + B 无 -atype AVG/PTP ⑮o pitfalls 提及 AVG -atype 坑
- **negatives**(3): print_expected(硬编码 A，B 面板计数错) / atype_avg_wrong(全用 -atype AVG，负闸门+AVG config 计数 0) / core_deleted(空 report，字段缺失) — negative_selftest 全 FAIL
- 自验: reference PASS(15 conds) + 3 negatives FAIL + harness SKIP_RUN 案例加载/workdir leak 自检通过
