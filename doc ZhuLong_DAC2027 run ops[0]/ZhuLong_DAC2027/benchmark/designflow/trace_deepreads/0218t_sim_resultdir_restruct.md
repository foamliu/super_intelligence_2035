# Deepread · 0218t · xuelianf @ hfeg0pkn002 · spice_sim

**session**: `1794187811534_0218t.messages.json` (40 msgs, 375KB, mtime 11-09 13:19)
**trace_source**: user xuelianf, host hfeg0pkn002 (10.129.2.11), mc=13 (full-file spice kw)
**discovery**: 11-05 重扫令 path(d) fresh-window 直扫 11-09 12:55+ extended window on 6 spice-marker hosts (pkn001-005+hfhds234) → 0218t NEW un-ledgered, kw_full=13, stable (mtime 13:19, not active)

## 用户意图（A-faithful 选轮）
- **U#0**「请阅读一下下面的两个文件，运行后输出的文件夹为什么不一致
  文件1：/rundata/sim_cloud/CRG/cyzhu/ACA/DRGQA_5SEC_SM/REVC/21_check_256datatopo/normal_CMOS0831_ArySPF_OPT5_BLR_SenCC_200aF/run_group123.py
  文件2：/rundata/sim_cloud/CRG/Duowang/0827_1001/LT_0p93_sen1001_TG256_SenCC/run.py」
- **U#2**「请按照文件2生成输出文件夹的方式修改文件1的程序（不修改group范围），以D0为例，例如文件1生成的输出文件全都在all_sim_result_D0，而文件2生成的输出文件会在文件夹all_sim_result_D0内再生成一层各自的文件夹（例如result_D0_11111111）输出文件」
- U#0/U#2 都是「提出需求/表达目标」轮，用户未给根因或修复方案 → 符合 A-faithful 选轮规则。

## 真实工具链
list_allowed_files×7, editor×4, read_files×3, run_approved_command×2, get_agent_policy_status×1
（agent 受 policy 限制不能 editor 写 /rundata，改用 python-runner profile 跑 patch 脚本完成修改）

## 根因分析（assistant M#3/M#15）
- File1 (run_group123.py) 用 pathlib 绝对路径 + 不 chdir；bsub 无 -n/-R；primesim -o 绝对路径时部分输出文件（.log/.fsdb）散落在 all_sim_result_D0 平层。
- File2 (run.py) 用 os.chdir + 相对路径；bsub -n 16 -R "span[hosts=1]"；输出全在 result_D0_<bin>/ 子目录内。

## 金标准（用户接受的实际产物）
- agent 写 patch_run_group123.py（python-runner profile），备份原文件 → run_group123.py.bak，重构 run_group123.py：
  - `os.chdir(bl_path)` + 相对路径 glob `-i`/`-o`
  - `GROUPS = ["group1","group2"]` 保留（不修改 group 范围）
  - 输出 `output_dir = os.path.join(result_root_rel, "result_{}_{}".format(prefix, bin_id)) + os.sep` → 嵌套 result_D0_<bin>/
  - 运行前 `shutil.rmtree(d0_result_root/d1_result_root)` 清理旧结果
  - bsub `["bsub","-q",QUEUE,"-n","16","-R","\"span[hosts=1]\"","-J",...,"primesim","-spice","-i",sp_file,"-o",output_dir,"-np",NP]`
  - D0 sort_sp_files reverse=False（升序），D1 reverse=True（降序），min_count 配对
  - DRY_RUN flag
- patch 报告：Original SHA256 44ecff6b..., New SHA256 d336d17e...（trace 内版本，GROUPS=["group1","group2"]）
- 磁盘现状（11-09 14:26 取）：108 行，SHA 5eff38a8...，但 GROUPS 被后续编辑改为 ["group1","group2","group3"]——**group3 是 trace 之后的独立编辑，不属于本任务**。trace-faithful 金标准 = GROUPS=["group1","group2"]（用磁盘版回退 GROUPS 行）。
- U#33 用户问「新生成的程序中有在运行前清除 result 文件内原有文件的功能吗」→ assistant 确认第 69~73 行 `for rp in (d0_result_root, d1_result_root): if os.path.exists(rp)... if not DRY_RUN: shutil.rmtree(rp)`（cleanup 行为被用户接受）。

## 资产获取
- file1 原始（167 行）：从 trace M#15 editor old_text 提取（/rundata 直读 .bak 为空，权限/不存在）
- file2 参考 run.py（143 行）：从 /rundata 经 .75 ssh 直读（e3b0... wait, e286721... 实读成功 143 行）
- gold（108 行）：从 /rundata 读 patched run_group123.py，回退 GROUPS → ["group1","group2"]

## case 合成
- **EDA-Eval-DesignFlow-SimResultDirRestruct-001** (spice_sim, A-faithful, L1, k=12)
- 可见 A：run_group123.py（待修改）+ run.py（参考）
- 隐藏 B：3 seed 随机合成 BG workspace（不同 bin_id/BL 子集，含 stale 文件测 cleanup）
- check.py 12 条独立断言(a-l)：交付形态/os.chdir/GROUPS不变/rmtree清理/bsub -n span标志/DRYRUN -i相对/-o嵌套带尾分隔/嵌套result_D0_*创建/嵌套result_D1_*创建/cleanup移除stale/D0升序/D1降序
- 自验：ref PASS + 4 neg 全 FAIL（NEG_RC=0）+ §4.9 三假(stub×2/nomakedirs)全 FAIL + jsonl test 字段与磁盘 check.py byte-sync(sha bbef2492...)
