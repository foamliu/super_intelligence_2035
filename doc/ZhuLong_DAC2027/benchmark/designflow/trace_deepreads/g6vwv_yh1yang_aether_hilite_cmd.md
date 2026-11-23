# deepread — g6vwv yh1yang Aether socket 桥 hilite/unhilite 命令扩展

- session: `1795004863729_g6vwv.messages.json`
- user: yh1yang @ hfeg0pkn004 (10.129.2.13)
- mc: 148 (aether:852 / pyaether:158 / schematic:60 / floorplan:17)
- agent: lead, cwd `/home/yh1yang/coding/p/`
- round: r1030 (shard C, layout_aether)
- case: `EDA-Eval-DesignFlow-AetherHiliteCmd-001`

## 真实任务

yh1yang 已有一套**跑通**的 Aether socket 桥：
- `server_start.py` 在 Aether GUI Python Console 里 `exec` 运行，起 `aeRunCmdWithSocket`
  回调服务器（`SleAeSocketRequestCallback` 子类 `RequestCB`），外部 python 经 TCP 发命令
  字符串，`dispatch(token)` 路由到 `h_<cmd>(arg)` 处理器，回 JSON 一行。
- `aether_client.py` 是外部 `AetherClient` 类，`_send(cmd)` 发一行命令、读一行 JSON。

现有命令：`cur / path / insts / all_insts / nets / desc / descend=NAME /
goto=/a/b / back / uptop / ping / shutdown / eval=EXPR`。

本轮新增 **hilite / unhilite** 命令（用户与团队成员确认的契约）：

1. `hilite=NAME` 单名 → 先 `aeClearHighLight()`，再 `aeAddHighLightObj(type="Id",
   id=[inst], color=N)` 高亮，**并** `aeSelectObject(inst)` 选中。
2. `hilite=N1,N2,N3` 多名 → 先清高亮，再批量 `aeAddHighLightObj`，**不**调
   `aeSelectObject`（多选取无意义）。
3. `unhilite` → `aeClearHighLight()`。
4. `@color` 后缀：`red=1, green=4, yellow=3, blue=5, magenta=6, cyan=8`，缺省
   `yellow(3)`，未知色名回退 `yellow(3)`。
5. **API 选择**：用 `aeAddHighLightObj`（画可见高亮），**禁用**
   `aeMakeProbeWithColor`（返回 None、不渲染）。
6. 高亮不合并进 `goto`（下钻后父层不渲染，高亮无意义）。

## 源文件捕获（.75 ssh）

host hfeg0pkn004 路径 `/home/yh1yang/coding/p/`：
- `server_start.py` 9335B — 含 `HILITE_COLORS` / `h_hilite` / `h_unhilite` /
  `aeAddHighLightObj(type="Id", id=list, color=N)` / `aeClearHighLight` /
  单名 `aeSelectObject`，多名跳过 select。
- `aether_client.py` 4545B — `AetherClient.hilite(*names, color=None)` 拼
  `",".join(names)` + `@color`，空名不发包；`unhilite()` 发 `"unhilite"`。
- `README.md` 12141B — 命令词汇表 + 用法。

源文件为 ASCII-clean（中文仅注释，已英文重写进 ref）。

## case 设计

- **公开 config A**（`assets/.../env_A/`，SUT 可见）：
  `task_spec.md` + `server_start_base.py`（base 无 hilite）+ `aether_client_base.py`
  （base 无 hilite/unhilite）+ `pyaether_mock.py`（录制型 mock，env_A 样例 instance
  MP0/MN0/MP1/PIN0）。
- **隐藏 config B**（`assets/.../hidden/`，不进 SUT）：`design_manifest_B.json`
  6 器件 PM0/PM1/NM0/NM1/R0/C0（lib=hilite_bench/cell=AmpDiff，与 A 全不同）+
  `hidden_manifest.json`。
- **判分**：`reference/.../check.py` 把隐藏 mock（env_B 6 器件 + 录制 CALLS）内联，
  子进程跑候选 `server_start.dispatch("hilite=...")` / `dispatch("unhilite")`，
  查 `CALLS` 序列 + 返回 dict；进程内 import `aether_client` + 假 socket 验客户端
  `hilite()/unhilite()` wire token；3-seed 随机子集（PYTHONHASHSEED=1/2/3）dispatch
  hilite=<env_B 随机 2-5 名> 验 n/names/color + 单名选/多名不选。
- **k=11 全闸门通过**：ref solve.py PASS + 3 negatives（empty/print-only/delete-core）
  全 FAIL + §4.9 三假全 FAIL + env_B 隐藏防 echo + 真子进程跑候选 dispatch + 客户端
  token 字节级断言。

## 与 r1023 AetherSocketBridgeNav-001 区别（防 intent-dup）

同 user（yh1yang）同 host，但：
- session 不同（g6vwv 1795004863729 vs olgpe 1795003959776）。
- 任务不同：r1023 = **新建**外部客户端做协议指纹检测 + 导航脚本执行（首帧
  viewer_connected banner vs 私有 JSON 桥 response/error_log/print_log 拒绝）；
  r1030 = 在**已跑通**的 socket 桥上**扩展** hilite/unhilite 命令（单名选+高亮、
  多名只高亮、aeAddHighLightObj vs aeMakeProbeWithColor 选型）。
- 判分不同：r1023 起 mock TCP 服务器跑客户端；r1030 子进程跑服务端 dispatch +
  假 socket 跑客户端 token，断言 API 调用序列（aeClearHighLight 先于
  aeAddHighLightObj、aeSelectObject 单名调/多名不调、颜色映射）。
