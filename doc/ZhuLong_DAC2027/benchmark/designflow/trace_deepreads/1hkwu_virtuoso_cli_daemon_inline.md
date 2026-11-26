# Deepread — trace 1787122881271_1hkwu (junxu@hfeg0plg79, mc1950, layout_virtuoso)

## 真实任务

junxu 写了一个 `virtuoso-cli` skill：通过一个 Python **daemon**（TCP bridge）
让外部客户端把 SKILL 代码送到正在运行的 Cadence Virtuoso 里执行。daemon 是被
Virtuoso 通过 `ipcBeginProcess` 拉起的子进程，部署时被**单独拷贝**到
`~/.virtuoso-cli/daemon.py`。

用户报告 skill "跑不通"：`virtuoso-cli test` 返回 `connected: false`，daemon
起不来。

## 根因

`daemon.py` 顶部：

```python
from virtuoso_cli.protocol import STX, NAK, RS
```

但 daemon 被 Virtuoso 经 `ipcBeginProcess` 单独拉起时，`virtuoso_cli` 包**不在
`sys.path` 上**（它只在 skill 源码目录里）。于是 daemon 启动即崩：

```
ModuleNotFoundError: No module named 'virtuoso_cli'
```

bridge 永远起不来 → `connected: false`。

`STX / NAK / RS` 是 wire 协议的三个二进制帧标记常量（成功/错误/记录分隔），
定义在 `protocol.py` 里，daemon 只读它们的值。

## 修复思路

写 `fix_daemon.py`：
1. 读 broken daemon + protocol.py；
2. 去掉对 `virtuoso_cli` 包的 import；
3. 从 protocol.py 解析 STX/NAK/RS 的值，内联进 daemon（顶层赋值）；
4. 其余 daemon 逻辑（`serve` / `_frame` / `_handle` / `_log` / `_LOG_PATH`）
   一字不动。

修复后的 daemon 自包含，可单独部署到 `~/.virtuoso-cli/`，不再依赖
`virtuoso_cli` 包在 `sys.path` 上。

## case 抽象

- **类型**：produce-tool（写一个修复脚本），纯 Python，无 EDA 工具调用 →
  `judge_layers = ["L0", "L1"]`（mock）。
- **调用接口**：`python3 fix_daemon.py <broken_daemon.py> <protocol.py> -o <fixed_daemon.py>`
- **交付**：`outputs/submit.zip`（顶层 `fix_daemon.py`）。

## 防硬编码设计（A/B 差异）

| | A（visible 调试用） | B（hidden 评测用） |
|---|---|---|
| import 行顺序 | `STX, NAK, RS` | `RS, STX, NAK` |
| STX | 0x02 | 0x01 |
| NAK | 0x15 | 0x16 |
| RS | 0x1E | 0x1F |

- B 用**不同 import 顺序** → 防正则硬匹配固定顺序。
- B 用**不同常量值** → 防硬编码 A 的值。
- check.py 第 k 条：同一 `fix_daemon.py` 跑 A 必须得 STX=0x02（证明从
  protocol.py 读取，而非硬编码 B 的 0x01）→ 真·泛化性断言。

## 判分（11 条独立断言 a–k）

a. `fix_daemon.py` 自身 `ast.parse` 通过
b. `fix_daemon.py` 在隐藏 B 输入上 exit 0 + 产出非空 `fixed_B.py`
c. `fixed_B.py` `ast.parse` 通过
d. `fixed_B.py` 不再含任何 `from virtuoso_cli` / `import virtuoso_cli` 行
e. `fixed_B.py` 中 STX/NAK/RS 三个常量都被顶层赋值
f. STX == B 的 0x01（防硬编码 A 的 0x02）
g. NAK == B 的 0x16
h. RS == B 的 0x1F
i. daemon 结构保留（`serve` / `_frame` / `_handle` / `_LOG_PATH` / `_log`）
j. 确定性：连跑 3 次 md5 完全一致
k. A != B 防硬编码泛化：跑 A 得 STX=0x02，且 A/B STX 不同

## 自验

- ref self-test：`check.py submit_ref.zip` → **PASS**（11/11）
- neg_selftest：4 neg 全 FAIL，首失败条件 distinct
  - empty → b（runs 无输出）
  - print-stub → e（无 STX/NAK/RS 赋值）
  - copy（原样拷 broken daemon）→ d（仍含 import）
  - hardcode-A 值 → f（STX=0x02 ≠ B 的 0x01）
- §4.9 trio（empty/print/copy）3-distinct：b / e / d
- harness SKIP_RUN：workdir 建 OK，leak CLEAN（无 check.py/reference/hidden）

## 文件

- `cases/C/EDA-Eval-DesignFlow-VirtuosoCliDaemonInlineFix-001.json`
- `reference/EDA-Eval-DesignFlow-VirtuosoCliDaemonInlineFix-001/{check.py, fix_daemon.py, negative/*}`
- `assets/EDA-Eval-DesignFlow-VirtuosoCliDaemonInlineFix-001/{daemon_A.py, protocol_A.py, task_context.md, hidden/{daemon_B.py, protocol_B.py, hidden_manifest.json}}`

## ledger

`trace_ledger_C.tsv`：1787122881271_1hkwu → case (EDA-Eval-DesignFlow-VirtuosoCliDaemonInlineFix-001)
