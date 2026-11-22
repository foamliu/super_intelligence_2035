# yn6qg deepread — joeyl CML divider SS130 swing=0.1 起振修复

- **trace**: `1794914803691_yn6qg` (joeyl @ hfeg0plg53, mc190, spice_sim)
- **src**: summary_20261122_172249.tsv; scp `/home/joeyl/.cline/data/sessions/1794914803691_yn6qg/1794914803691_yn6qg.messages.json` (236 msgs / 1.05MB)
- **真实意图 (U0)**: 看 `HANDOFF_divider_3issues.md`，半速率 ss130 corner 即使 swing=0.1 仍无法正常起振，希望在 swing=0.1 下让 divider 正常 ÷2 分频；可从任何角度改 divider（用户给了 4 维分析：①R_load trade-off ②输入/锁存对 gm ③选通管 Vth/Vgs ④偏置管 finger）。
- **agent 诊断 (.op 实测 SS130)**: 选通管 XNM4/XNM5 (nulvt_ckt, Vth≈0.34) 被时钟驱动，时钟低电平=0.6V，源端~0.09V → "关断"选通管 Vgs≈0.5V > Vth，两只选通管几乎全周期同时导通 → 尾电流无法干净切换 → divider 自由振荡(~1.7GHz ring) 而非锁定 ÷2 (3.15GHz)。用户洞察③命中。
- **lever 探索**: resctr=0 反而更差(25mV, ratio 1.0)；提高选通 Vth → ratio 0.272→0.333 (swing 掉到 112mV)；**E8 = 选通 Vth +0.15 (_delvto=+0.150) + 尾管 XNM10 w=19.2e-6 nf=8** → ratio=0.500, 3.15GHz, swing 177mV ✓。
- **5-corner 验证 (half-rate 6.3GHz→3.15GHz, swing=0.1)**: TT45/FF-40/FF130/SS-40/SS130 全部 ratio=0.500 干净 ÷2，startup <0.6ns，quadrature skew 24-29%。full-rate 12.6GHz SS130 仍 speed-limited (E9 减 R 反而崩) → 用户所述 failing case (half-rate) 已解决。
- **最终交付**: DUT 网表 `/home/joeyl/ulvt_delvto/work/Solo_Divider_netlist_div3fix`：选通管 XNM4/XNM5 行尾追加 `_delvto=+0.150`，尾管 XNM10 改 `w=19.2e-6 nf=8`，输入/锁存对保持 `_delvto=-0.05` 不变；CML_divider subckt 定义一次、例化两次(f0/r0)，故单次编辑对称作用于两 divider。
- **reframe (L1 纯 Python)**: `divider_netlist_role_patch.py --netlist <deck> --spec <json> --out <deck> --report <json>` —— 按设备名在指定 subckt 内做多规则编辑(append_param / set_param)，preserve-list 设备不动，未匹配设备字节不动。
- **distinct**: vs DelvtoNetlistModifier-001 (6pm3i, 单 model-class 单值 append _delvto=-0.2) —— 本 case=按设备名多规则 patch (select +0.15 / tail w+nf 重写 / latch preserve)，混合 op + preserve-list，机制不同 ✓。
- **沙盒可达性**: e0031982 无 /proj PDK 读权限 → L1 reframe (不真跑 FineSim)。
