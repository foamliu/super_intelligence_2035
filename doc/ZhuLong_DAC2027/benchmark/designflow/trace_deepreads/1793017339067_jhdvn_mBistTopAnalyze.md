# Deepread: 1793017339067_jhdvn (mBistPat/mBistTop circuit analysis)

- **user**: t0002805 @ hfeg0pgn145  | **mc**: 492 | **domain**: characterization
- **session_file**: `1793017339067_jhdvn.messages.json` (298 msgs, 2.7MB)
- **旧判定 (reaudit 前)**: `circuit analysis (schematic+netlist explanation), no sim` → 旧规则判 weak/不可造
- **新判定 (r618 reaudit)**: 可造 → analysis Q&A → 造「电路/脚本分析报告」check 验关键模块/行为/指标覆盖
- **处置 r671**: 复活池变现 #51，造 EDA-Eval-DesignFlow-MBistTopAnalyze-001

## 用户真实意图（原话）
- 「你可以帮我分析电路吗」
- 「virtuoso 但是我截图不了给你啊」
- 「这个电路图在 /proj/ddgoa/V0/libs/ddgoa_cmos_digital/mBistPat下」
- 「网表我抽了 在这个文件夹下 /proj/ddgoa/V0/workdir/t0002805/simulation/ddgoa_cmos_digital_mBistPat_schematic_20260901_ALPS」
- 「你从上往下帮我详细的说一下」
- 后续多轮追问：mbiststart 信号、load cm vs clear cm（测试模式）、两级 D 触发器 toggle、I_mBistLdCm cell、PartialArrayEnInt、mBistColFastWr/mBistRowFast 工作条件、RA/CA 地址清零、retention、mbist 与外部电路交流、ControllerM5、测试图案如何写到对应地址、Bistwritedata cell、写→读→比对校验、比较电路在哪、从哪个端口送出

## agent 工具链
list_allowed_files（探库目录）+ read_files（分段读 mBistPat/mBistTop 分层网表 netlist/netlist_org/netlist.map）+ search_codebase + RAG_MCP_Server__search_apis。读 mBistPat netlist 821-2056 行、netlist_org 4003-4606(Bistwritedata 定义)、map 文件多段。

## 关键技术发现（agent 实证）
1. **mBistTop 顶层实例化 5 子模块**：mBistCmdGen(命令/CA 奇偶产生)、mBistAddrGen(地址产生)、mBistPat(命令状态机)、Bistwritedata(写图案数据产生)、Spare_mBist(空占位)。
2. **mBistAddrGen 内含地址计数器**：mBistRACnt(RA<8:0>)、mBistCACnt(CA<5:0>)、mBistRAMsbCnt(行 MSB)、mBistBACnt_WtRdRef(Bank+读写/刷新)；端口有 RABegin/RAEnd/CABegin/CAEnd/BABegin/BAEnd + PartialArrayEn（部分阵列使能）。
3. **mBistPat 输出 6 个计数时钟**：CACntCK/RACntCK/BACntCK/RASecCntCK/RAMsbCntCK/RARefCntCK + **仅 BACntRst 复位**（XI365 invLx4 net340→BACntRst），**无 RACntRst/CACntRst**——RA/CA 复位靠 Reset/ResetN + 计数时钟控制间接完成。
4. **Bistwritedata = 写图案产生器**：cm0_ts_BistData<7:0> → BistDecoder38(3-8 译码) → DataLat(锁存) → Data<7:0>/GrpData<0~15><7:0>；内部 BistDataInv/mxi3x1/xor2x2。**无读回数据输入端口**（只产生写入图案，不做比对）。
5. **比对电路不在 mBistTop**：顶层无 cmp/compare cell；CompFailBGNHigh/CompRdBGx/ErrCnt 等比较信号在更上层 ChanMid。
6. **MBIST 流程**：写(Bistwritedata 产生图案) → 读(mBistPat 发 ReadStart/ReadEn) → 比对(上层 ChanMid 把读回数据 vs 期望图案 XOR)。
7. mBistPat 本身「不知道测试图案也不产生地址值」——只发命令时序 + 计数时钟驱动外部计数器。

## 合成决策
- **形态**：analysis Q&A → 电路网表分析报告（与 reaudit 拟造任务形态一致）
- **A 档 trace-faithful**：doc/mbist_top.netlist 用 trace 真实命名(mBistTop/mBistCmdGen/mBistAddrGen/mBistPat/Bistwritedata/Spare_mBist + 真实信号 CACntCK/RACntCK/BACntCK/RASecCntCK/RAMsbCntCK/RARefCntCK/BACntRst + mBistRACnt/mBistCACnt/mBistRAMsbCnt/mBistBACnt_WtRdRef + BistDataInv/BistDecoder38/DataLat/mxi3x1/xor2x2)，task_spec 含用户原话。
- **hidden B cross-input**：合成 MbistTopInt 同构网表——同 archetype 同结构约定(*Begin/*End=*地址范围端口、*CntCK=计数时钟、*CntRst=复位、内部 Dec+Lat=图案产生器)，但名字/数量不同：5 计数时钟(A=6)、3 地址计数器(A=4)、4 图案部件(A=5)；BankCntRst(仅 BA 复位，同 A)。
- **判分有牙**：22 断言，subprocess 在 B 上真跑，cross-input 值/数量守卫，A-leak 词边界守卫，确定性 3 rerun，4 假提交全 FAIL。
