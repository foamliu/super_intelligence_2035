# 深读笔记 · xr6sg · yunfat · WaveView 上升沿 margin 测量

- **trace**: `1794460481537_xr6sg.messages.json`，yunfat @ hfeahpc505(10.129.33.28)，mc=35
- **keywords**: waveview:160;netlist:21;schematic:10;cmos:6;synopsys:4;lvs:4;hspice:4;analog:4
- **nmsgs**: 完整对话流（agent 多轮 search_apis + get_api_details）
- **用户原话（U1）**: 「测量waveview3中两个信号的上升沿margin标注出来」

## 用户意图
在 Synopsys WaveView3 中测量两个信号上升沿之间的 margin（时间差/skew）并在波形上标注出来。

## agent 工具链（真实 trace）
1. `search_apis("measure rise edge timing margin between two signals annotate in waveview", lang=tcl)` → 命中 `sx_meas_risefall`/`sx_gmeas_risefall`/`sx_meas_delay2`
2. `search_apis("skew measurement between two signal rising edges")` → `sx_meas_delay2`
3. `search_apis("probe annotate margin setup hold time between clock and data rising edge draw")` → 探针类
4. `search_apis("trtfProbe setupHoldProbe skewProbe margin measurement waveform highlight")`
5. `get_api_details(["sx_gmeas_risefall","sx_meas_risefall","sx_meas_delay","sx_meas_delay2"])`
6. `search_apis("graphic measure delay draw arrow annotate value between two signals waveview")` → `sx_gmeas_vs_x`/`sx_display`
7. `search_apis("sx_gmeas delay between two line rising edges graphic measurement object")` → **`sx_gmeas_delay`**（图形化 delay 测量，带标注，关键 API）
8. `get_api_details(["sx_gmeas_delay","sx_gmeas_risefall","sx_set_threshold","sx_meas_delay2"])`

## 关键 API 定位
- `sx_gmeas_delay <line_obj> -refline <ref_line>` —— 图形化 delay 测量对象，在两条 line 之间测 delay 并绘制标注（满足"标注"需求）
- `sx_meas_delay2 <sig> -refwave <refsig> -trigger rise` —— 测两信号上升沿 delay（数值）
- `sx_gmeas_risefall` —— 上升/下降沿时间
- `sx_set_threshold` —— 设置穿越阈值

## A 档可行性
不可行。真实 WaveView .fsm/.tr0 波形文件 GB 级 + /rundata 项目目录权限，无法离线复跑 GUI 标注。⇒ **B 档**：把"上升沿 margin 测量"逻辑便携化为纯 Python 脚本——从波形 CSV 采样用线性插值求两条信号上升沿穿越 vref 的时间，margin=target−ref，输出结构化 JSON + annotation 描述。subprocess 真跑 + 独立 ground-truth 复算 + 跨输入 guard 判分。

## 新 archetype 判定（mcguard）
- 既有 spice_sim case：.mt0/.measure 聚合(Mt0MeasureStat)、.md0 光滑度(RonCurveSmoothness)、.lis SNM 抽取(McLisSnmExtractor)、.measure deck 生成(HierMeasIncGen/InstCurrentMeasGen)、stimulus 生成、deck diff 等
- 本 case = **波形采样→上升沿穿越时间线性插值→margin(skew) 计算**，属 WaveView timing-margin 测量便携化，与既有 archetype 不同 ⇒ 非 P-004
- yunfat 新用户（0 既有 case）⇒ mcguard G1-G5 PASS
