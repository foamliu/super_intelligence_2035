# Deepread: cv1d2 — Keepalive→Popup pyAether script patch

- **session**: `1789889636409_cv1d2.messages.json`
- **user/host**: ziyuny @ 10.129.8.236 (hfeg0pkg118 段)
- **match_count**: 40 (D-pure: aether:215 / pyaether:61 / schematic:24 / synopsys:11 / analog:4; non-D drc:3+verilog:4 = 7)
- **msgs**: 57 (264 KB), 2 user turns, glm 模型
- **domain**: analog_context (pyAether skill-script 编辑, Aether GUI/cellview API)
- **ledger**: shard D, claimed r827, status → case `EDA-Eval-DesignFlow-KeepaliveToPopupPatch-001`

## 真实任务 (2 turns, 均 mode=act)

**Turn 1 (MSG 0)**: `/home/ziyuny/.cline/skills/auto-group-generator/scripts/group_generate.py` 这个脚本中，最后打开 layout 和 schematic 之前，想要换 aether 的版本，版本的更换方式是使用 `module load empyrean/aether`。

**Turn 2 (MSG 15)**: 同一脚本，最后的窗口不用保留，在跑完
```python
save_ret = ae.aeSaveDesign()
info("aeSaveDesign -> %r" % (save_ret,))
if save_ret is False:
    fail("aeSaveDesign 返回 False, 结果未保存")
```
之后就可以了。最后给一个弹窗显示这个信息
```python
print("GROUP GENERATE DONE: %s/%s/%s" % (args.lib, args.cell, args.view))
```

## 原始 group_generate.py (input A, 140 行, 完整)

流程: `emyInitAether('-adv')` → `aeOpenDesign` → `aeLoadGroupGeneratorConfigFile` → `aeCstAnalysisFromDesign` → `aeCstRealizeAllFromDesign` → `aeSaveDesign` → 打印 `GROUP GENERATE DONE` → **第 4 段 GUI 保活循环**:

```python
# --- 4) GUI 保活 (默认行为, 与 test.py 一致): 关闭所有窗口后进程才退出 ---
if args.no_keep_gui:
    info("--no-keep-gui, 进程直接退出")
    return
info("进入保活事件循环, 用户关闭所有 GUI 窗口后进程退出 ...")
while True:
    ae.qtexec()
    time.sleep(0.2)
    cur_gu = ae.emyArray_p_GuDrawArea()
    ae.aeGetWindowList(cur_gu)
    if not [x for x in cur_gu]:
        info("所有窗口已关闭, 进程退出")
        break
```

依赖: `import time` (仅被保活循环使用)。arg: `--no-keep-gui` (store_true, "生成完成后直接退出, 不保活 GUI 窗口")。

## agent 推导与改动 (关键技术内容)

1. **Turn 1 结论**: 版本切换无法在进程内完成 —— `import pyAether` 一旦执行, so 库已加载, `module load` 只影响新进程的环境变量。版本切换应放在启动 shell (`run_group_generate.sh`→`setup.bash`) 里, 而非 pythone 脚本内。agent 探测确认 `module load empyrean/aether` 模块存在 (modulecmd/lmod 可用, module show 输出 setenv AETHER_ROOT 等)。(本 turn 因策略/超时未落盘改动, 但环境探测结论正确。)

2. **Turn 2 核心**: 把第 4 段保活循环替换为完成弹窗:
   - 删除 `while True: ae.qtexec() ... break` 保活循环
   - 删除随之无用的 `import time`
   - 保留 `aeSaveDesign` + `GROUP GENERATE DONE` 打印 (日志标记, run 脚本 grep 验收不变)
   - 在打印后调用 pyAether 官方弹窗 API:
     ```python
     dlg = ae.aeDisplayMessageBox(
         name="group_generate_done",
         banner="Group Generator",
         text=done_msg + "\n结果已 aeSaveDesign 保存, 点击 OK 关闭窗口并退出。",
         dialogType=ae.pycInformationDialog,
         modal=True,
         buttonLayout=ae.pycOK,
     )
     ```
     modal 弹窗阻塞至用户点击 OK, 之后进程退出、design 窗口自动关闭。
   - `--no-keep-gui` 保留但语义改为 "无人值守时跳过弹窗直接退出" (否则无人值守会被弹窗卡住)
   - 弹窗整体包 try/except: 即使弹窗 API 失败, 不影响已保存结果, 进程正常退出
   - 同步更新 `run_group_generate.sh` / `SKILL.md` 的 "保活→弹窗" 描述

3. **API 调研** (RAG_MCP_Server search_apis/get_api_details):
   - `aeDisplayMessageBox` / `aeDisplayUserMessageBox` / `aeMessageBoxOK` 候选
   - 选定 `aeDisplayMessageBox(dialogType=pycInformationDialog, modal=True, buttonLayout=pycOK)` —— modal 信息弹窗, 单 OK 按钮, 阻塞至点击

4. **策略墙**: skills 目录不可写 (writableRoots 仅 `/home/ziyuny/.cline/scripts/data`), editor 写 skills 目录被拒, run_commands 被禁, patch 脚本审批被拒。agent 写了 `patch_popup.py` (唯一匹配替换 + .bak 备份) + `verify_popup.py` (py_compile + 断言) 在可写 data 目录, 但最终未能落盘。会话以 "请用户改策略后继续" 结束。

## casemaking 决策

- **框架**: design_flow tool-generation (同 GrDecPwrSwitchTbGen-001 模式)。SUT 须写一个**通用保活→弹窗补丁工具** `keepalive_to_popup.py --input <script> --output <patched>`, 对任意带保活循环的 pyAether skill 脚本做改造。
- **A (可见)**: 原始 `group_generate.py` (140 行) + task_brief + prompt
- **B (隐藏)**: `design_check.py` —— 同保活模式但不同命名/消息/flag: DONE 消息 `DESIGN CHECK COMPLETE`, args `--library/--cellname/--viewname/--headless`, 循环 var `cur`/`w`, sleep(0.3), log() 函数
- **check**: 跑 patcher 于 B, 对 patched B 文本断言 12 条 (保活循环移除 / import time 移除 / aeDisplayMessageBox / pycInformationDialog / modal=True / buttonLayout=pycOK / B DONE 消息进弹窗 text / headless 跳过弹窗 / try-except 包裹 / aeSaveDesign 保留 / 反硬编码 A 串不泄露 / py_compile 通过)
- **反硬编码**: A 专有串 (GROUP GENERATE DONE / group_generate / args.lib / args.cell / args.view / no_keep_gui / auto-group-generator) 不得出现在 patched B
- **degenerate FAIL**: 空 zip / print-only / 原样拷贝(不删保活循环) 三者均 FAIL
