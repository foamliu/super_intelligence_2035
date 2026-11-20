# Deepread: 1792562522433_6kbdj — schematic add TESTPIN

- **trace**: colinxu @ hfeg0plg81 (also hfeg0pgn041/hfeg0plg54 via NFS home), mc=269, 157 msgs
- **domain**: schematic_netlist (pyAether schematic pin creation)
- **clean need round**: U#0 (msg 0)「帮我在drcqa_analog lib - AG_AmpsUpBankFar cell - schematic view内添加一个TESTPIN这个pin」— A-faithful 提需求轮，未给根因/方案。U#5/8「请继续」延续。U#73「我没有找到TESTPIN，并且为什么这个schematic被锁住了」是问题反馈轮（非提需求）。U#135「还是上锁状态？」持续反馈。
- **agent tool chain**: RAG_MCP_Server__search_apis/get_api_details (dbCreateSchPinEx, dbOpenCVByType, dbFindTermByName, emyPointF, dbCheckAndSaveDesign, emyTermGetPinFigs, emyFigGetPinName, dbCVIsLocked, dbGetPath) → SandBox_MCP_Server__run_code (pyAether 探查+创建+保存+验证) → editor (写 add_schematic_pin.py + probe/release shell) → run_approved_command (shell-runner: ls/grep/strings/rm cdslck/ps/kill) → ask_question (用户授权删锁/kill)

## 真实 gold (磁盘 /home/colinxu/agentdir/train/V0_NCG_HF_Aether/add_schpin.py 已 ssh cat 读取)

`add_schematic_pin(lib, cell, view, pin_name, direction='input', master_lib='basic', master_cell='in', point=(1.0,1.0), save=True)`:
1. `cv = dbOpenCVByType(lib, cell, view, 'schematic', 'a')` — append 模式打开目标 schematic
2. `existed = dbFindTermByName(cv, pin_name)` — **幂等守卫**：pin 已存在则跳过创建、返回现有 term
3. `master = dbOpenCVByType(master_lib, master_cell, 'symbol', 'symbol', 'r')` — 打开 pin master symbol（input→basic/in，验证可写；非 basic/ipin）
4. `pt = emyPointF(point[0], point[1])`; `before = cv.termCount`
5. `pin = dbCreateSchPinEx(cv, master, pin_name, direction, pt)` — 创建 pin（term + symbol inst）
6. 反向验证：`cv.termCount == before+1` 且 `dbFindTermByName(cv, pin_name) is not None`
7. `save`: `dbCheckAndSaveDesign(cv=cv)`；只读重开确认 `dbFindTermByName(cv_ro, pin_name) is not None` 持久化

## 关键事实（磁盘/沙箱实证）

- **目标 cell**: drcqa_analog / AG_AmpsUpBankFar / schematic（OA 格式 sch.oa，路径 /proj/train/V0_NCG_HF_Aether/libs/drcqa_analog/AG_AmpsUpBankFar/schematic）
- **原 termCount=30**（TESTPIN 不存在），创建后 **31**（TESTPIN 为第 27 个 term）
- **原 30 term 名**（msg 57 实读）：
  `VblhSFREn_W, VwlpDetect_R, VblhRef_R, VblhActPrime_V, VblhRef_L, VblhActPrime_U, Vblh2Vcc_L, VblhCcomR, VblhSFREn_U, PwrOn3_R, VblhActDis_R, VblhSFREn_V, VblhActEn_W, cm1_ag_BiasAct_L<1:0>, VblhAmpOutR, VblhAmpOutMid, Vblh2Vcc_R, VblhAmpOutL, VblhSFR_L, VblhActEn_U, VblhActDis_L, VwlpDetect_L, VblhRef_Mid, VblhActPrime_W, cm1_ag_BiasAct_R<1:0>, VblhCcomMid, VblhSFR_R, VblhCcomL, VblhActEn_V, PwrOn3_L`
- **pin fig 自动命名 P__61**（TESTPIN）；既有 pin 也是 P__xx（VblhSFREn_W→P__62, VblhAmpOutR→P__48, cm1_ag_BiasAct_L<1:0>→P__44）— term 名（用户可见）≠ pin fig 名（自动分配）
- **input pin master = basic/in/symbol**（PIN331 等；非 basic/ipin，agent 验证两者都可打开但选 basic/in 与既有结构一致）
- **direction='input'**（用户未指定方向，agent 默认 input；sch.oa strings 显示 `Pin "TESTPIN": floating inputOutput` — 实际落盘为 inputOutput，与 dbCreateSchPinEx direction 参数语义有关）
- **OA 编辑锁问题**（次要剧情，非 U#0 核心需求）：沙箱 aether -adv 后端进程 PID 18505 (hfeg0plg81) 持续持有 sch.oa.cdslck，删后重建；最终 kill 18505 解锁。TESTPIN 确认落盘（sch.oa 95052 字节，grep TESTPIN count 4）。

## 降级方案（真实 pyAether 不可移植到评测沙箱）

真实 add_schpin.py 依赖活 Aether DB（drcqa_analog 库 + basic/in master + OA lock），评测沙箱无此环境 → 降级为**确定性 Python 生成器** `gen_add_schpin.py`：
- 读 `config.json`（lib/cell/view/pins 列表/existing_terms/save/next_pin_fig_seq）
- 对每个 pin：若 name ∈ existing_terms → 幂等跳过（created=false, term_count 不变）；否则 created=true, term_count_after=before+1, pin_fig_name="P__<seq++>"
- 写 `add_schematic_pin.py`（faithful pyAether 脚本，参数化 lib/cell/view/pin/direction/master/point）
- 写 `pin_report.json`（每 pin：name/direction/master/point/created/idempotent/term_count_before/term_count_after/pin_fig_name/persisted + summary）
- 核心逻辑保留：幂等守卫、termCount 增量、auto pin fig 命名（P__xx）、direction/master 参数化、save+只读重开验证

## A/B 资产

- **A**（faithful，单 pin）：config_A.json — lib=drcqa_analog, cell=AG_AmpsUpBankFar, view=schematic, pins=[TESTPIN/input/basic/in/(1.0,1.0)], existing_terms=真实 30 名, next_pin_fig_seq=61 → create 路径
- **B**（hidden，结构不同，2 pin 测两分支）：config_B.json — lib=analog_qa, cell=AmpDiffPair, view=schematic, pins=[DIAGPIN/output/basic/out/(5.0,3.0) → create; VblhAmpOutR/input/basic/in/(2.0,4.0) → 幂等跳过(在 existing_terms 中)], existing_terms=24 名(含 VblhAmpOutR), next_pin_fig_seq=88
