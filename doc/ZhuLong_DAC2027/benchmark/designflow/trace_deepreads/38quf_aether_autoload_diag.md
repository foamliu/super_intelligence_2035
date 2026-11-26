# 深读笔记：38quf — Aether 本地脚本自动加载诊断

- **session**: 1793353212592_38quf
- **user**: gurmanli @ hfeg0pkn005 (10.129.2.14)
- **agent**: lead (非 cline)
- **mc**: 597, domain=spice_sim (reaudit), keywords aether:5988/pyaether:758/schematic:134/netlist:132
- ** msgs**: 304, user msgs 163 (多数空/工具结果), 14 真实用户轮
- **旧判**: parked "aether_load_howto" → r618 reaudit 改判 可造(how-to Q&A)
- **文件**: /home/gurmanli/.cline/data/sessions/1793353212592_38quf/1793353212592_38quf.messages.json (1.4MB)

## 真实用户意图

用户 gurmanli 是版图工程师，在 vir 项目环境(/proj/drvqa/V0)下用 Aether 做版图。
他写了 pyAether 脚本 `aether_select_adjacent_vias.py`（注册 F1 bindkey 选相邻 via），
想让 Aether 启动时**自动加载**该脚本。问题：手动启动 Aether 时脚本生效（F1 可用），
但**vir 启动项目环境后脚本不生效**。

## 关键用户轮

- U#0: 「目前项目启动的时候，aether可以load本地脚本吗」
- U#3: 「/home/gurmanli/script/aether_select_adjacent_vias.py 自动加载这个脚本」
- U#14: 「vir启动项目环境以后目前是不生效」
- U#51-53: 用户自己分析出 PID 38609(vir启动)脚本未加载 vs PID 49999(手动)F1成功执行
- U#61: 「项目级 aether.ini 文件我们可以改动吗」
- U#72: 「重启aether尝试并没有成功」
- U#108: 贴出 PY_INIT_FILE 环境变量值
- U#139: 「如果多个脚本需要load，目前处理的是一个」
- U#148: 「把之前改动全部取消」(最终用户要求回滚所有修改)

## 助手诊断链（完整根因）

1. **aether.ini 三级搜索优先级**：安装目录 > $HOME/.empyrean > 运行目录(workdir)
   - 日志实证：3 行 "Load setting file" 依次加载三个 ini
2. **Py Script 键"先读先生效"**：安装级 `Py Script=${PY_INIT_FILE}` 先读取→优先生效
   → 用户级/workdir 级的 Py Script 被忽略
3. **PY_INIT_FILE 环境变量**：由 vir 设置，冒号 `:` 分隔（不是分号）
   - `PY_INIT_FILE = aetherwings/setup/init.py : ada/pyaether/init.py`
4. **vir 每次启动重新生成 workdir/aether.ini**：从模板复制→用户定制被擦掉
   - 实证：第一次重启 workdir ini 有用户脚本，第二次重启后被抹掉只剩 2 个公司脚本
5. **Tcl Script 键突破口**：安装级和 workdir 级的 `Tcl Script=` 都是空值→空值不遮挡
   → 用户级设置 Tcl Script 能生效（日志实证 `source aether.tcl` 成功）
6. **Tcl/pyAether 不能混用**：AskEDA FAQ 明确「mixing pyAether and TCL interfaces is not supported」
   → `pyAether::load` Tcl 命令不存在→aether.tcl 被 source 但脚本没加载
7. **Py Script 多脚本用分号 `;` 分隔**：workdir 模板第 158 行 `Py Script=init.py;CXMT_pcpreload_0.py`
8. **正确修复方案**：用 Tcl Script 钩子(空值不遮挡) + 向 PY_INIT_FILE 追加(冒号分隔)
   + Python bindkey 注册自动重试(防 layout 未就绪)
9. 用户最终要求「把之前改动全部取消」→助手回滚全部修改

## 可操作化判定

- **形态**：debug-Q&A 根因诊断 → 产出生成式诊断报告 JSON
- **B 档 synthesized**：真实 aether.ini/log 文件未完整落盘（助手只读了片段），
  按 trace 诊断链结构忠实合成证据文件（保留真实键名/优先级/分隔符/机制名）
- **check 验**：报告 JSON 的诊断结论字段（搜索优先级/先读先生效/env_var/分隔符/vir 擦除/
  Tcl 钩子/Tcl-pyAether 不混用/多脚本分号/正确修复路径），stub/空壳必 FAIL
- **新形态**：reaudit「aether-env-config 诊断」操作化首例 + aether.ini 三级优先级解析首例 +
  PY_INIT_FILE 冒号分隔首例 + Tcl Script 空值突破口首例 + vir 模板擦除机制首例
