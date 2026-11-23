# trace_deepread: dp66k — legendd stdcell fixed IO pin placement

- **session**: `1795400459450_dp66k.messages.json` (456 msgs, 1.9MB)
- **user/host**: legendd @ hfeg0plg106 (10.129.8.238)
- **cwd**: legendd, pyAether Aether stdcell inverter layout
- **keywords**: pyaether:1115; aether:255; rtl:223; dbopencv:156; schematic:99; dbget:83; lvs:69; drc:67
- **match_count**: 470
- **整体目标**: 学习像人一样从原理图绘制标准单元（stdcell）版图，可扩展到其他单元格。长会话教学型，含多个子任务（floorplan/routing/M0U stub/via 打孔/打 pin）。

## 本 case 选取子任务（MSG idx 306-456）：打 IO pin 规则

用户在 floorplan+routing 完成后（USER #36, idx 306）开始讲打 pin 规则。

### 真实任务（USER #37-#50）
- USER #37 (idx 308): vcc!/vss!/vbp!/vbn! 4 个 pin 每个 stdcell 都有、位置固定，找出来描述位置、试着理解规则。
- USER #38 (idx 328): pin shape size 都是 0.195×0.195；vcc!/vss! 一边分别与 M1 rail 中心线对齐；vbp!/vbn! 与 M1 rail 的一个角对齐。
- USER #40 (idx 345): 用到的层次不对，要用 purpose pin，同时还要有相应的 label；用户在 cell 外放了 vss!a 示例。
- USER #41 (idx 364): label 要和 pin/term 名字联动（改 pin 名 label 跟着变），不是独立 label。
- USER #49 (idx 433): label 的 justification 用 centercenter，坐标放到 rect 中心。
- USER #50 (idx 441): 输入和输出 pin 用到的最高层来打 pin，宽度与 path 一样，纵向位置在 MOS 的中间。

### agent 已验证的几何（assistant idx 327/333/344/363/380）
spacer M1 rail：顶部 VDD rail y6.300~7.120（中心 6.710），底部 VSS rail y-0.410~0.410（中心 0.000）。

| pin | 层 | y 范围 | size | 对齐 |
|:--|:--|:--|:--|:--|
| vss! | M1 | 0.000~0.195 | 0.195² | 底边(y0)=底部 M1 rail 中心(0.000) |
| vcc! | M1 | 6.515~6.710 | 0.195² | 顶边(y1)=顶部 M1 rail 中心(6.710) |
| vbn! | PW | 0.215~0.410 | 0.195² | 上角(y1)=底部 M1 rail 角(0.410) |
| vbp! | NW | 6.300~6.495 | 0.195² | 下角(y0)=顶部 M1 rail 角(6.300) |

- 全部位于左边缘 x=0~0.195，purpose=pin。
- label = AttrDisplay（跟随 pin 名，ctrl+P / leGuiCreatePin 生成）；脚本等价：dbCrtRect(purpose=pin) + dbAddFigToPin 把 label 挂到 pin。justification=centercenter，origin=rect 中心。
- 信号 pin：用到的最高层、宽=path 宽、纵向放 MOS 中间。

### 关键 API 链
aeGetCurDesign → emyScalarTerm.getPins → emyPin.getFigs → 读 layer/bbox；dbCrtRect(purpose=...)、dbCrtLabel、dbAddFigToPin(fig, pin)、dbGetPinFigName 验证关联；leGuiCreatePin (ctrl+P)。

## 合成为离线 Python case
- **case**: EDA-Eval-DesignFlow-StdcellFixedPinPlace-001 (layout_aether / stdcell_fixed_pin_place)
- real Aether session 不可达 → 离线 Python 合成：pin_place.py 读 config.json 输出 pin list JSON。
- 公开 config_a = trace 真实值（pin_size 0.195, rail top 6.710/6.300, bottom 0.000/0.410, mos_middle 3.355, 信号 A/Y M2 w0.1）。
- 隐藏 config_b（rail 5.500/5.100, 0.500/0.900, pin_size 0.200, mos_mid 3.000, 信号 M3 w0.15）主判分；config_c（rail 4.000/3.600, 1.000/1.400, pin_size 0.180, 信号 IN/OUT/EN M2/M4/M3）cross-input 反硬编守卫。
- k=18 全闸门通过：ref PASS + 4 neg (empty/print_only/hardcode_a/delete_core) 全 FAIL distinct（cond3/cond3/cond7/cond10）；§4.9 三假 (a)(b)(c) 全 FAIL；ref 在 config_a 输出 4 固定 pin rect 与 trace verbatim 一致。
- 区别：C 域 layout_aether 子型 stdcell 固定 IO pin 放置首例，与 M0uReservedTrackMark-001(text:drawing1 track 标识)/AetherHiliteCmd-001(高亮) 产物/断言/trace 全不同。
