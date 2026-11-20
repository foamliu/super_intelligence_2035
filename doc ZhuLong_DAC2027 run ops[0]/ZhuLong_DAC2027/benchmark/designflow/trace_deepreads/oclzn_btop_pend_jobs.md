# trace_deepread: 1794221830421_oclzn — BtopPendJobs-001

- **trace**: `1794221830421_oclzn` / dandans @ hfhds201 (10.129.32.75, .75 本机)
- **mc**: 94 (candidates_mc10.tsv, eda_other, A-domain pure)
- **session**: 762KB / 96 msgs / 3 user turns / mtime Nov 16 (活会话, .75 本机直接可达, 无 rotation 风险)
- **选料**: r716 §II 完结后的 fresh full-pipeline 候选; 从 pool_reaudit_A.tsv "可造 pending deepread" reserve 中按 recent+本地.75+mc 适中 选出 (oclzn 在 r503 被旧 'trivial/flow-driving' 筛子误 park, 11-15 §II 标 可造 revived: default)

## 用户真实意图 (3 turns, 逐字)
- **U#0** (msg#0, ts=1794221830894): `<user_input mode="act">dandans@hfds2: /proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_..._Aging_*` 列出 6 个 MatrixRun aging/HLTOL corner 目录 (HLTOL_RDBI_1008hr / blv / Aging_10yr / 42hr / 3650hr), 要求 **「把上述文件夹中的job全部置顶上去，用btop」**.
- **U#2** (msg#75, ts=1794222312255): 又给 2 个 Pre 目录 (Aging_Pre / Aging_ODT_Pre), **「文件中的job也btop上去」**.
- **U#3** (msg#94, ts=1794791736730): **「总结一下，以便下次执行任务时快速准确。」** (要可复用的流程).

## agent 流水线 (assistant tool_use 序列)
1. `list_allowed_files` 浏览 MatrixRun 父目录 + 各 corner 子目录
2. `read_files` 读各 corner 的 `111` 文件 (LSF bjobs 输出表)
3. `ask_question` (msg#18) 确认 btop 是 LSF 的 btop (提高优先级到 top), 用户选「对，就是 LSF 的 btop，把所有 PEND job 置顶」
4. `editor` 生成 `extract_pend_jobs.py` + `run_btop.sh` + `btop_aging.sh` + `btop_aging2.sh`
5. `run_approved_command` 实跑 (python-runner / shell-runner)

## 关键坑 (实跑发现, 必须进判分)
1. **btop 一次只接受一个作业**: msg#53 实跑 `btop j1 j2 j3 ...` (40 个作业一批) 报 `Command syntax error: too many arguments. Usage: btop [-h] [-V] [-u] jobId | "jobId[index]" [position]` — 全部 FAILED. msg#73 改成逐个 `btop <jobid>` 才 OK/FAILED. **这是 produce-task 判分的核心反批量断言**.
2. **111 文件两种版式**: 真实 grep 用了两条正则: `^\d{5,}(?=\s+PEND\s)` (JOBID STAT, 无 USER) + `^\d{5,}(?=\s+\S+\s+PEND\s)` (JOBID USER STAT). parser 必须都支持.

## 最终可工作脚本 (btop_aging2.sh, msg#68-92)
```bash
BASE="/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun"
FOLDERS=( "MatrixRun_..._Aging_Pre" "MatrixRun_..._Aging_ODT_Pre" )
for folder in "${FOLDERS[@]}"; do
    for fname in "111" "222"; do
        fpath="$BASE/$folder/$fname"
        if [ -f "$fpath" ]; then
            grep -oP '^\d{5,}(?=\s+PEND\s)' "$fpath"
            grep -oP '^\d{5,}(?=\s+\S+\s+PEND\s)' "$fpath"
            break
        fi
    done
done | sort -u | while IFS= read -r job; do
    echo -n "btop $job ... "
    btop "$job" 2>/dev/null && echo "OK" || echo "FAILED"
    sleep 0.1
done
echo "All done."
```
实跑输出: `btop 2027707 ... FAILED` / `btop 2027728 ... OK` ... `All done.` (286 unique PEND, 逐个调).

## produce-task 化
- 交付物: `btop_pend_jobs.py` (Python 标准库, --base/--folders/--dry-run/--json/--report/--sleep/--btop-cmd)
- 通用化: 任意 base + folder 列表 + 任意 111/222 bjobs 文件 -> 提取 PEND jobid, 跨目录去重, 逐个 btop (或 --dry-run 仅报告)
- A=真实 DDR6 Aging corner 名 + 合成结构真实 bjobs 111 (4 folders, 20 unique PEND, 2022xxx, 标准版式)
- B=DDR5 ODT corner 变体 (5 folders, 20 unique PEND, 3099xxx, 混合版式+缺111+零PEND), B 永不进 SUT
- check.py 12 条独立断言, 嵌独立 reference parser, subprocess 跑 B (--dry-run --json + 纯文本)

## 跨 shard 互斥
- B 于 2026-11-09 20:29 误 park 本 session 为 "trivial flow-driving" (旧 r503 weak 筛子, 11-15 §II 已废)
- 实为 eda_other flow-driving (LSF 作业调度自动化), 非 analog/spice, A-domain
- 按 r708/r715 --force hatch, A mark 覆盖, note 记原因
