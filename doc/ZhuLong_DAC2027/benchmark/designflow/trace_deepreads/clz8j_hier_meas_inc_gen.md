# Deepread: 1794480714010_clz8j (reedchen / hfeg0pkn003 / mc75)

**trace**: 167 msgs / 595KB / dir-format / scp .75 10.129.2.12
**user**: reedchen (新用户, 0 既有 B case)
**keywords**: netlist:246; schematic:79; hspice:25; cmos:16; drc:9; aether:3
**tools**: 218 netlist / 79 schematic / 4 hspice
**domain**: spice_sim (功耗 .measure deck 生成)

## 用户意图（两步 produce-task）

**U1**（提取层级）:
> 「我先在希望你帮我整理出来一个 signallist 里面是 128 个 instance 的完整 hierachy，
> 比如 XI0.XI212.XI6.XMMP15 这个 PMOS，他的 Gate 端连接着 PPubN 这个信号，这样的 PMOS 在这个网表里有 128 个，
> XI0 是例化的整个 TB，XI212 是 DqDbusDrv_x_rev0 模块，这个模块有 8 个，每一个里面有 16 个 DbusDrv_NN_x_dq，
> 我希望你把这 128 个 instance 的完整 hireachy 抓出来」

**U2**（生成 .measure inc.sp）:
> 「现在我要你依据这个 list 写出一个 inc.sp 文件，里面有 128 行
> .measure tran I_vintcore_stat_loss avg isub(xi0.xi108.xi0.xmmp26.src) from '10n' to '30n'
> 这样的 measure 语句，写好后 cp 在 .../sim_current/ 文件夹下面」

## 网表结构
顶层例化 XI0 = TB（Dbus_tb_0810_1010_write）→ 8 个 DqDbusDrv_N_rev0 group → 每个 16 个 DbusDrv_NN_x_dq driver cell → 每个 cell 内 1 个 Gate=PPubN 的 PMOS（X 例化, model ptn*/atn* 族）= 8×16=128。

## agent 工作链（从 .75 抓的 extract_final.py / gen_inc.py）
1. parse_subckts: 扫 .SUBCKT/.ENDS 建块
2. 找 DqDbusDrv_N_rev0 → 收集 DbusDrv_NN driver cells
3. 每个 driver cell 找 X 例化 MOS（model ptn/atn），Gate(端口序2)==PPubN → cell_pmos[cell]={dev,D,G,S,B}
4. TB 里找 DqDbusDrv_N_rev0 例化 → dq_inst_cell
5. 每个 DQ group 遍历 16 driver 例化 → dbus bit + drv_nm + drv_cell + dev → 全路径 XI0.X<dq>.X<drv>.X<dev>
6. gen_inc: 同解析 → 输出 `.measure tran I_vintcore_stat_loss_<idx> avg isub(<小写路径>.src) from '10n' to '30n'`
agent 迭代修复：extract1-5 + extract_final（warning no PPubN → 修 cell 匹配 → 成功 128 行 PPubN_PMOS_128.txt）

## 判定
- **新 archetype**（层级提取驱动 spice .measure deck 生成）: 非 P-004。对照既有 B case: NetlistModSummary(2397x)=网表模块摘要; SpiceMeasInjector(g0x1k)=既有 .sp 注入 .measure; 均不同。
- **A 档不可行**: /rundata/ddgoa/V0/simdir/finesim/.../netlist_org 真实 5000 行 IP 网表 + 项目目录权限。
- **B 档**: 合成忠实自包含网表（同 3 层结构, 缩小规模, 泛化信号名 gate_sig 从 config 读）。
- 跨域误判排除: tools 218 netlist 看似跨域, 但产出是 spice .measure deck（hspice 功耗测量语句）⇒ B 域 spice_sim produce-task。
