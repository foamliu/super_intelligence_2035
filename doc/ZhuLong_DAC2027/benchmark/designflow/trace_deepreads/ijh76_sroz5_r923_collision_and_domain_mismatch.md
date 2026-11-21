# r923 deepread — ijh76 + sroz5 (BOTH REJECTED, 0-case round)

> round r923 (2026-11-21 23:00–23:30, shard C, 0-case flow-correction round)
> 两候选均 REJECT：ijh76 跨 shard 语义串台；sroz5 操作域错配（schematic/D 非 layout/C）。

## 候选 1: ijh76 (junxu @ hfeg0plg79, mc=1393, virtuoso:5882 dominant) — REJECT 串台

### trace 真实意图
junxu 维护自建 virtuoso-cli SKILL daemon skill 的 `find-python.sh` 跨机 Python 发现脚本。
核心 bug 演化（msg 424–604, 670–707）：
- `setup --python /usr/bin/python3` 把 agent 主机绝对路径写进 `RB_PYTHON_PATH`，但
  Virtuoso daemon 跑在另一台主机（NFS 共享 home 不共享系统目录）→ daemon exec
  `/usr/bin/python3` 报 `No such file or directory` / `status=126`。
- `find-python.sh` 缓存文件 `$CACHE_DIR/python-path` 不含 hostname → NFS 共享目录里
  缓存的绝对路径在别的机器上失效。
- `2>/dev/null` 吞掉所有候选失败信息，搜索失败只看到笼统 "No working Python found"。
- 候选路径硬编码 `/apps/local/python/python3.11.9/bin/python3.11` 等，不动态扫描。
- `set -eu` 在 `sh` 下 `command -v` 返回非零会直接退出。

### gold 修复（trace 最终落地，文件已 scp 确认 byte-identical 于 wv-cli 副本）
1. **per-host cache**：`CACHE_FILE="$CACHE_DIR/python-path.$HOSTNAME"`，每台主机
   独立缓存条目。
2. **`VB_DEBUG=1` 诊断**：`_debug()` 输出 `[find-python] ...` 到 stderr，每个候选
   TRY/SKIP/OK/FAIL 带原因。
3. **动态 glob `/apps`**：用 shell glob（非 `find`，避免 NFS 大目录 30s+ 扫描）
   `/apps/local/python*/bin/python3*` + `/apps/local/anaconda*/bin/python3*` 等。
4. **不吞 stderr**：版本检查 `env -u PYTHONHOME -u PYTHONPATH "$c" -c '...' 2>&1`
   捕获到 `_errout`，FAIL 时输出首行。
5. **`set -u` only**（去掉 `-e`）。
6. **删 `--python` setup 参数**：`RB_PYTHON_PATH` 永远指向 `find-python.sh`，
   Python 发现完全交给运行时。
7. **unify virtuoso-cli + wv-cli**：两 skill 各存一份 byte-identical `find-python.sh`
   （独立安装但实现统一）。

### REJECT 原因：跨 shard 语义串台
shard D 已落库 commit `9cba28b0d r955 shard D: VcliPyenvFix-001`，trace `ogspt`
(`1789435102785_ogspt`, **同用户 junxu @ hfeg0plg79**, mc=517)，覆盖**同一
virtuoso-cli skill 的跨机 Python 发现**，**同一批文件** (`find-python.sh` +
`setup_cmd.py` + `skill_bridge.il`)：
- VcliPyenvFix teeth ⑤⑥ 直接检 `find_python.sh` 内容（unset PYTHONHOME/PYTHONPATH
  + version>=3.8 guard）—— 与本 case 的 find-python.sh teeth 重叠。
- VcliPyenvFix 检 `setup_cmd.py` 部署 `find_python.sh` 到 NFS home —— 与本 case
  的 setup_cmd.py teeth 重叠。
- 一个解过 VcliPyenvFix 的 SUT 手上已有 `setup_cmd.py` + `find_python.sh`，近乎
  能直接通过本 case —— 串台。

**ledger 互斥查重只能按 session_file 查重（ijh76 ≠ ogspt），查不出同 skill 同文件
的语义串台。** 这是 r912 "选题前必先 claim" 铁律的盲区：claim 防的是同 session
重复，防不了同 skill 跨 session 串台。

### lesson
- **claim 前必须做语义串台检查**：对候选 trace 的 (user, skill, 核心文件) 三元组，
  grep 全 4 shard 的 jsonl `trace_source` + reference 目录，确认没有已落库 case
  覆盖同一 skill 的同一批文件。本例 ijh76 (find-python.sh) 与 ogspt/VcliPyenvFix
  同 (junxu, virtuoso-cli, find-python.sh+setup_cmd.py) —— 应在 deepread 前查。
- junxu 的 virtuoso-cli **skill-infra** 池（find-python / setup / skill_bridge /
  daemon / cli.py）已被 r915(sjzm0 daemon review) / r919(508od layout label) /
  r920(1hkwu no-instance JSON) / D-VcliPyenvFix(ogspt pyenv) 密集覆盖，剩余
  skill-infra 子任务大概率串台，应避开 junxu skill-infra 池。

## 候选 2: sroz5 (junxu @ hfeg0plg79, mc=1101, virtuoso:3211 dominant) — REJECT 域错配

### trace 真实意图
junxu 优化 virtuoso-cli skill 的 **schematic API** (`api/schematic.py`) 的 label
放置 + pin 方向：
- msg 0–523：label 总打在 net 右侧，pin 在器件左侧时 label 与器件重叠；纵向 net
  的 label 应纵向放置（R90/R270）。操作 `schCreateLabel` / `schCreatePin` /
  schematic net wires，文件 `api/schematic.py`，用户语 "电路图"。
- msg 802–847：`build_fifo.py` 构建的 DOUT/FULL out pin 方向不对（像 input pin），
  `dbOpenCellViewByType "fifo_work" "fifo_8x3" "schematic"` —— schematic 域。

### REJECT 原因：操作域 = schematic (shard D)，非 layout (shard C)
keyword `virtuoso:3211` dominant 但**实际操作全在 schematic**（`schCreateLabel` /
`schCreatePin` / `schematic` cellview）。按 r919 lesson "trace 域归属要按操作域而
非 keyword 域"：sroz5 = shard D (schematic_netlist)，非 shard C (layout)。

### lesson
- **claim 前必须 deepread 前 5 条 user input + assistant 前 3 个 editor target**
  确认操作域：本例 sroz5 msg 0 就指向 `api/schematic.py` + "电路图"，msg 1 assistant
  read `schematic.py` —— 一眼可判 schematic/D。我在 claim 前只看了 keyword
  breakdown（virtuoso:3211 dominant）就判 layout/C，重犯了 r919 记录的错。
- junxu 的 **layout** 池实际只有 508od（已 r919 case）；其余 junxu session
  (sstk3/fbz0w/sroz5/m6imc) 都是 schematic/spice 域。junxu 池对 shard C 已枯竭。

## r923 结论：0-case flow-correction round

两候选 REJECT，不强制造 case（质量闸门 k≥8 独立齿 + 无串台 优先于 1-case 数量）。
r912 precedent：0-case 流程纠偏轮合法且有价值。下轮 r924 必须：
1. **避开 junxu 池**（skill-infra 串台 + layout 已枯竭）。
2. **claim 前语义串台检查**：grep 全 4 shard jsonl `trace_source.user` +
   `trace_source.real_task_summary` 关键词 + reference 目录 case-ID，确认无同 skill
   同文件 case。
3. **claim 前操作域确认**：deepread 前 5 user input + 前 3 editor target，按操作域
   （schCreate*=D / dbCreate*=C / calibre+drc=physical_verify C / hspice+netlist=B）
   而非 keyword 域判 shard。
4. 优先选**非 junxu** 的 mid-mc (5–800) C-dominant 候选（drc/calibre/lvs/gds/.gds
   dominant 用户如 e0014566/xinqiaoz/miccao/ziyuny —— 但需查 ledger 是否已 parked，
   parked-with-note 的可重审 revival）。
