# Deepread: 1795071241845_e1gmg — Virtuoso 启动排障 → 启动脚本生成器

- **trace**: `/home/e0049049/.cline/data/sessions/1795071241845_e1gmg/1795071241845_e1gmg.messages.json` (1,560,386 bytes, 368 msgs)
- **user/host**: e0049049 @ hfeg0plg56 (RHEL 8.10 远程桌面)
- **mc**: 427 (virtuoso:2872 / rtl:373 / synopsys:157 / aether:152 / cadence:137 / schematic:135)
- **domain**: schematic_netlist (virtuoso = 原理图工具环境)
- **判定**: LIVE-NA（shell 脚本 = 文本交付，结构化解析判分，无真实 EDA 工具产物依赖）

## 真实用户意图

用户 e0049049 在远程桌面启动 Cadence Virtuoso，CIW 窗口弹出后过一会自动退出。整个 trace 是一轮反复排障，跨 368 条消息：

1. 列目录 `/proj/lacaa/TV1_FS_Virtuoso`（权限被拒，750 lacaa 组）
2. virtuoso 如何启动 GUI / 为什么启动不了
3. 按方案一配置修改（设 OA_UNSUPPORTED_PLAT=linux_rhel60）
4. 启动后过一会自动退出
5. 参考其他用户 `/home/e0047343` 为什么能打开
6. 反复试错：env -i 清空环境 → license 丢失（LMC-01902）→ 加 CDS_LIC_FILE → CDS.log 被锁 → killall+rm 清锁 → .cdsinit 覆盖 exit(1)
7. 发现其他用户全用 IC617ISR23 而非 IC618.320
8. **最终根因**：OA 平台名 `linux_rhel60` 是错的！IC617ISR23 的 OA 库目录是 `linux_rhel50_gcc48x_64/opt`（存在），`linux_rhel60_64/opt` 不存在 → 启动即崩。正确名是 `linux_rhel50_gcc48x`。
9. 最终可用命令（msg 363）：`export OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x && /apps/cdsmgr/CRB/IC617ISR23/tools/dfII/bin/virtuoso -64`
10. CIW 弹出但仍有 ARGUS server.tcl 关闭 + 项目检查 exit(1) 问题（trace 末尾仍在迭代）

## 多层根因汇总

| 层 | 问题 | 修复 |
|---|---|---|
| **OA 平台名（关键）** | `OA_UNSUPPORTED_PLAT=linux_rhel60` → 找不存在的 `linux_rhel60_64/opt` | 改 `linux_rhel50_gcc48x`（IC617ISR23 实际目录） |
| Aether 冲突 | `LD_PRELOAD`/`OA_LIB_PATH`/`AETHER_OA_HOME`/`OA_OBSERVER_DEFERABORTPOLICY` 污染 OA | `unset` 这 4 个 |
| 残留锁 | `CDS.log` 锁 + `.cdslock*` → `File is already locked` | `killall -9 virtuoso` + `rm -f` 锁文件 |
| License | env -i 清空了 license | `export CDS_LIC_FILE=5980@hl07:...` |
| 站点初始化 | CDS_SITE 丢失 → Library Manager 不显示 | `export CDS_SITE=...` + `CDS_LOAD_ENV=CSF` |
| 公司 .cdsinit | `innoGlobalVar.il` 项目检查 exit(1) | .cdsinit 覆盖 `CXMTutGenerateProjVerInfoList()`（trace 末尾仍在迭代） |

## case 合成（synthesized-reframe）

真实意图 = 把排障经验固化成**通用 Virtuoso 启动脚本生成器**。

- **task_id**: VirtuosoLaunchScriptProduce-001
- **deliverable**: `gen_launch_script.py(spec) -> start_<design>.sh`
- **judge_layers**: [L0, L1]（LIVE-NA，文本解析判分）
- **A**（visible spec_A.json）: IC617ISR23 / cds_home=/apps/cdsmgr/CRB/IC617ISR23 / oa_platform=linux_rhel50_gcc48x / license=5980@hl07:... / display=:1084.0 / cds_site=/apps/imctf/cad/init/settings_cdns / cds_load_env=CSF / unset 4 个 Aether 变量 / clean_locks=true / lock_files=CDS.log+.cdslock* / kill_stale=virtuoso / run_mode=foreground / design=virtuoso
- **hidden B**（token-structurally 不同）: IC618.320 / oa_platform=linux_rhel60 / license=5280@lic01:5280@lic02:5280@lic03 / display=:0.0 / cds_site=/tools/cad/site_init / cds_load_env=CDS / cds_home=/apps/cdsmgr/CRB/IC618.320 / run_mode=background / design=cds / lock_files=/home/opsadm/cds.log+.cdslock*

## check.py 13 conds (a-m)

- a) zip 含 gen_launch_script.py + .sh
- b) gen py_compile
- c) A gen 产 start_<design>.sh 含全部 8 export 变量名
- d) A unset 行含全部 4 冲突变量
- e) A 清理：killall <kill_stale> + rm -f 每个 lock_files
- f) A OA_UNSUPPORTED_PLAT 值 == spec_A oa_platform（关键根因修复 linux_rhel50_gcc48x）
- g) A 启动行含 virtuoso_binary + args，foreground 无尾随 &
- h) A 四阶段顺序：unset < export CDSHOME < launch，clean < launch
- i) A 引用 A token（cds_version + license + display）
- j) B gen 产 start_<design_B>.sh 含 B token（cds_version + license + display + cds_home）
- k) B 不含 A-only token（反硬编码）
- l) gen 源码参数化（引用 spec key，不硬编码 A 字面常量）
- m) run_mode 遵从（B 后台尾随 &，A 前台无 &）

## negatives（6 neg, §4.9 trio full + 3 extra）

| neg | 期望 first-fail | 说明 |
|---|---|---|
| negative_empty | c | 空 .sh 无 export |
| negative_skip_clean | e | 跳过 killall/rm 清理 |
| negative_wrong_platform | f | oa_platform 硬编码 linux_rhel60（A 应为 linux_rhel50_gcc48x） |
| negative_core_deleted | g | 有 unset/clean/export 但删了 launch 行 |
| negative_print_only | j | 硬编码 A 脚本，B 无 B token |
| negative_hardcode_a | k | 除 oa_platform 硬编码 A 值外全参数化，B 泄漏 A-only token |

§4.9 trio: empty→c / print_only→j / core_deleted→g（全 distinct）

## 自验

- ref check.py on reference_submit.zip → PASS
- negative_selftest: 6 neg ALL-FAIL distinct first-fail {c,e,f,g,j,k}
- 3-way sha sync: disk==JSON test==metadata.check_sha256=6fab5436... size 12628
- k_check=13=k_rationale=13
- D jsonl 588→589 含本条
- 无 workdir leak（attachments 仅 spec_A + task_brief，hidden/spec_B 不进 SUT）
