# trace_deepreads — r1240 fresh C-domain candidate audit (4 sessions, all parked)

> 本轮 r1240：扫 summary_20261124_023802 C-domain mc 20-600 pool，对照 4-shard ledger dedup，
> 取 4 个 **真 fresh**（不在任何 shard ledger）C-domain lead，全部 claim + deepread + park。
> 与 r1239 (u03z0+qikhb 双 park) 同模式：mc 池顶部全饱和，新 fresh lead 多为 debug/analysis-Q&A
> 无 produce-task deliverable，teeth-fail risk。

## 1. 3oryk — shwanlai@hfeg0plg87, mc150, drc:1549/aether:1300/lvs:629/virtuoso:592/calibre:167
- 文件: 1143116 bytes, 96 msgs
- 用户意图: 9 user turns ALL env-config/debug-Q&A
  - U#1: "vir启动后所创建的相关配置及文件路径在哪？vir启动时的变量有吗，我想根据变量设置一些快捷指令"
  - U#2-8: 已将快捷指令加 .bashrc 但 vir 启动后不管用；排查 $WORK/$PROJ_NAME/$Ver 变量为空；work 大小写；删 .cfg_prj 无效
  - U#9: "这个正则表达式我想学习一下，请详细解释一下"
- 判定: env-config + regex-explain Q&A, NO produce-task deliverable. drc/lvs/aether keywords 来自
  assistant ctx (用户问的是 vir launcher 环境变量) 不是用户意图. **park** (teeth-fail risk).

## 2. e7fik — ganli@hfeg0pkn002, mc142, skipper:3801/drc:238/aether:154/calibre:77/lvs:63/pex:26
- 文件: 436221 bytes, 89 msgs
- 用户意图: 1 user text "skipper怎么实现clip" = how-to/doc-search Q&A
- assistant 全程: cimi-kb-search / ask-eda / grep workspace 找 skipper clip 实现，
  list_allowed_files /home/ganli/{ZL,Script,release,PCell}, read drc_rule.py/drc_sum2.py/exclude_layer.tcl/map_layer.tcl
- 判定: doc-search Q&A, agent hunts workspace for skipper clip impl. NO produce-task deliverable. **park**.
- skipper:3801 keyword 是 agent 在 ctx 中频繁检索的工具名，非用户产 task 意图。

## 3. 1x7j0 — rockyf@hfeg0plg95, mc149, drc:380/cellview:352/pyaether:109/schematic:105/dbget:34
- 文件: 502565 bytes, 81 msgs
- 用户意图: 2 user turns
  - U#1: 给出 hier inst path (DDR5TOP > I_Channel > I_BnkGTopX4_Top > I_BnkGTopX4_gut >
    I_BnkGTop_AC > I_D_BankLogicx2_B01 > I_D_BankLogic_B0 > I_R_RasBnkLogic > I_R_SaCntrlBnk)
    "读取这个电路模块，分析2 step Sa信号的工作逻辑"
  - U#2: "继续"
- 判定: analysis-Q&A (hier 电路模块 2-step Sa 信号逻辑分析), deliverable=分析解释 not produce-script.
  teeth-weak (gold=explanation, §4.9c core-deleted neg 难构造 distinct). **park**,
  may revive as structural-hier-extract produce-task 若后续需补 hier 遍历类 case.

## 4. 6878r — e0047488@hfeg0plg54, mc149, drc:498/pex:32/synopsys:12/aether:4/skipper:3
- 文件: 1044965 bytes, 405 msgs
- 用户意图: 2 user text ("test" + "viewer视图界面没有正常加载，提示{\"detail\":\"Not Found\"}")
  405 msgs 中 ~403 是 tool_results = 长链 agent debug GUI viewer HTTP 404
- 判定: debug-Q&A (GUI viewer 加载 404 排查), NO produce-task deliverable. drc/pex keywords
  来自 agent ctx. **park** (teeth-fail).

## 总结
- 4/4 fresh lead 均 park，0 case 交付。模式同 r1239。
- mc 20-600 C-domain pool: top (mc≥150) 全 case-built 或 cross-shard parked；
  fresh mid-band (mc 142-150) 4 个样本 100% debug/analysis-Q&A 无 produce-task。
- 数据依据: summary_20261124_023802 cand_c.txt (mc≥20 waveview-excluded, 1482 unique sessions),
  4-shard ledger dedup, 4 deepread 全 park。
- 未触发正式止损（r1239+r1240 累计 6 fresh < 阈值 10），但池饱和信号持续加强。
- 下轮建议: (a) 扫 mc 5-20 fresh（量更大但质量更低，预期更多 Q&A）; 或 (b) 转不依赖新候选的
  产出（§4.9 anti-hardcode 自查 / test_rationale 断言清单补全 / 已有 case L2.live hardening）。
