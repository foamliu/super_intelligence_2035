# gjycn — 反向器原理图搭建 (inverter schematic build via pyAether)

- trace: `1793878889580_gjycn` · cong3li @ hfeg0plg72 · mc=288
- tools: 329 schematic / 182 pyAether / 69 `"lang":"pyAether"` / 47 dbGet / 47 cellview / 18 dbCreateInst / 1 dbCreateRect
- 155 msgs / 3 user turns / 46 SandBox_MCP_Server__run_code + 16 RAG search_apis + 7 get_api_details + 4 read_files + 3 editor
- session file: `/home/cong3li/.cline/data/sessions/1793878889580_gjycn/1793878889580_gjycn.messages.json` (691KB)

## 用户意图（3 轮，逐字原文）
- U0: `帮我搭建一个反向器电路`
- U1: `现在把原本的反向器删掉，重新用一个NMOS管和一个PMOS管搭建一个反向器`
- U2: `把现在这个schematic的layout画好`（layout 部分跨 shard C，本案只取 schematic 搭建维度 U0+U1）

## 真实工作流（agent 成功交付 schematic）
1. `emyInitAether("-adv")` → 探测环境 `dbGetAllLibs` / `aeGetCurDesign`（当前设计 `AdamLi test_zhulong schematic`，空原理图 0 实例）
2. RAG `search_apis`/`get_api_details` 查"放置实例""建原理图""加 pin""连线"API
3. `dbGetAllCells(lib)` 扫 `basic/TECHLIB/drgqa_cmos_stdcells/stdcells_ac/drgqa_cmos_core/drgqa_cmos_digital/AdamLi` 找 `inv`/`nmos`/`pmos` 单元；`dbAllCellViews` 查 views
4. `dbOpenCV(lib,cell,"symbol","r")` 打开 symbol，`dbSchGetPinOrder`/`inst.instTerms` 探端子名/方向
5. U0：`aeCreateInstance("inv",(0,0),libName="TECHLIB",viewName="symbol",instName="XINV",orient="R0")` 放整反相器
6. `dbCreateSchPinEx(cv, masterin, "A","input",(-0.9,0),'R0','signal')` / `"Y","output"` / `"vcc","input","power"` / `"vss","input","ground"`（master 来自 `dbOpenCV("basic","ipin"/"opin","symbol","r")`）
7. `dbCrtSchWire(cv, [emyPointF(...)], wireSnapping=False)` / `aeCreateWire([emyPointF...],drawMode='Route',lockAngle='AnyAngle',wireSnapping=0)` 画 4 条线（A→设备 A、设备 Y→Y、vcc、vss）；`dbDeleteAll(vector1D_p_emyFig)` 删旧线重画
8. 验证连通性：`cv.instances` / `cv.terminals`(name,direction) / `cv.nets`(name) / `inst.instTerms[i].net.name`
9. U1：删原 inv，改用单个 NMOS + 单个 PMOS 搭反相器 → 扫库找 `ntn/ptn/nmos/pmos` 单元（`dbGetAllCells` 多库扫描，keys=[nmos,pmos,nfet,pfet,nch,pch,ntn,ptn,...]）

## 真实挑战点
- pyAether API 发现成本高：agent 用 16 次 RAG search_apis + 7 次 get_api_details 才确定 `aeCreateInstance`/`dbCreateSchPinEx`/`dbCrtSchWire`/`aeCreateWire`/`emyPointF`/`dbSchGetPinOrder` 的签名
- 几何连线易错：`dbCrtSchWire` 需 `emyPointF` 列表 + `wireSnapping=False` 保坐标精确，首版 wireSnapping 默认开导致坐标漂移；`aeCreateWire` 替代
- 端子名/位置需从 master symbol 探测（`inst.instTerms[i].name`、`getTermPosition`），不能假设
- U1 要求从整 `inv` 单元拆成 NMOS+PMOS 晶体管级搭建（源/栅/漏/衬底四端子分别接 VDD/GND/IN/OUT）

## 合成决策（B-grade synthesized L2, schematic_netlist）
- 私有 Aether 环境（`AdamLi/test_zhulong`、`TECHLIB/inv`、真实 PDK 器件库）不可复刻 → B-grade synthesized 自包含
- 提供 mock pyAether 模块（check.py 注入 sys.modules），SUT 写 `build_inverter.py` 用 mock API 搭建 NMOS+PMOS 反相器原理图并导出 `inverter_netlist.json`
- 可见 A（cong3li 环境）：`TECHLIB/ptn`(pmos) + `TECHLIB/ntn`(nmos)，端子 D/G/S/B，pin master `basic/ipin`+`basic/opin`，pin 名 IN/OUT/VDD/GND
- 隐藏 B（不同工程师环境）：`analogLib/pmos4` + `analogLib/nmos4`，端子 d/g/s/b（小写），pin master `basic/ipin4`+`basic/opin4`，pin 名 A/Y/VCC/VSS —— 反硬编码（脚本须读 env.json 通用化 lib/cell/term/pin 名）
- 判分：check.py 注入 mock、用 B env 跑 SUT `build_inverter.py`、独立从导出 JSON 验证反相器拓扑（2 管 pmos+nmos / 4 pin 方向 / 栅极共 IN / 漏极共 OUT / pmos S+B=VDD / nmos S+B=GND / 4 net 无短路 / 反硬编码 A 重跑正确 / 3-seed 字节稳定）
- U1「NMOS+PMOS 晶体管级」是关键（非整 inv 单元），B 亦要求晶体管级 → 拓扑验证成立

## 选料弃用记录（本轮 peek 11 fresh 顶候选）
- tsn3o/hzyu6 (fernandoy): 首条是「Context summary」续写 UVM 仿真环境，非 fresh produce
- focjw/r2yjr/icxnw/pzo6g/rv1g2/8go01/2izm6/dlrpg/4cefq/qvr6i/ikg9e/2b5i8 (e0039602): 同 verilog_lib_trans 项目，已 6 case，过度重复
- vbmpm (nevinrao): 网表 testmode 信号 hier 路径查找 = #463 NetlistSignalHierTrace-001 同意图，弃
- xinm9 (e0025522): 「启动业务场景:仿真与验证」泛启动 prompt，弃
- l64el (kailiu): 「你有抽一个cell的spf文件的功能吗」Q&A，弃
- taaak/gorts (e0039102): 「启动 Aether」infra，弃
- 7l4sx (e0017906): 「当前电路层级是什么」Q&A，弃
- abprg (e0017906): SKILL.md 编排 cm1 信号作用分析，依赖私有 SKILL.md，弃
- 0si6a/kegkw/mpszz: NO_FILE/FETCH_ERR/低工具数，弃
- kjb39 (cong3li): SA 电路搭建，沙箱未启动 agent 未真跑（落 SPICE netlist + 脚本），mock 复杂度同且未真交付 schematic，备选次于 gjycn
