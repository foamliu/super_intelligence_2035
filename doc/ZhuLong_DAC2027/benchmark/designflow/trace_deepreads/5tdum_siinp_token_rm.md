# trace deepread — 5tdum (mike @ hfeg0plg05) — FineSim si.inp T_mBistOsc token removal

## 源
- session: `1789611712575_5tdum.messages.json`（51 msgs / 1 user turn）
- user: mike · host: hfeg0plg05 · spice marker count: 3368
- 桾取方式：scp 5tdum.json 到 .75 workdir（1.57MB，4s）→ 本地 python3 peek_userturns 解析（182ms）

## 用户轮（A-faithful 选轮）
- **U#0（逐字拼音，唯一用户轮，提出需求无根因/修复 → A 档 ✓）**：
  `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta  zhegelujingxia you henduo mulu ,meige muluxia youge si.inp wenjian ,bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan`
  译：「这个路径下有很多目录，每个目录下有个 si.inp 文件，帮我写个命令，我要删掉 si.inp 中 T_mBistOsc 字符串」

## assistant 工具链 + 关键产物
1. search_codebase 找 T_mBistOsc / si.inp（71 files, No results for combined pattern）
2. list_allowed_files depth=1 列出 root 子目录（25 个 subdirs + 1 runFsm）
3. read_files 采样多个 si.inp → 确认 **line 55** 一致模式：
   `.option finesim_ignore = "R_RasEnOsc R_SrefAnlgOsc R_SrefOsc T_IsmOsc T_mBistOsc AG_TSOsc AG_ThickVfsblnOsc R_RHROsc R_SrefAnlgOsc R_RHROscTrimCap1"`
4. 尝试 apply_patch / editor 编辑 25 个 si.inp → 全部 `Write target is outside policy.writableRoots`（policy 仅允许 /ai_sandbox + /home，目标在 /rundata）
5. read agent-policy.json 确认 writableRoots 限制
6. **最终交付（msg_MTSgZiyu）**：因策略禁写，给用户命令自行运行：

## 金标准（msg_MTSgZiyu — 3 方法，推荐方法一）
```bash
# 方法一（推荐）：删除所有 si.inp 中 T_mBistOsc（含尾随空格）
find <root> -name 'si.inp' -type f -exec sed -i 's/T_mBistOsc //g' {} \;

# 方法一（精确版，仅改那一行）
find <root> -name 'si.inp' -type f -exec sed -i '/^\.option finesim_ignore = "R_RasEnOsc/s/ T_mBistOsc//' {} \;

# 方法二：grep 确认受影响文件再替换
grep -rl 'T_mBistOsc' <root>/*/si.inp | xargs sed -i 's/T_mBistOsc //g'

# 方法三：备份 + 替换
find <root> -name 'si.inp' -type f -exec cp {} {}.bak \;  # 备份后同方法一
```

**关键行为**：从 `.option finesim_ignore = "..."` 行删除独立标记 `T_mBistOsc `（含尾随空格），其余标记/行不变。
真实数据中 T_mBistOsc 总在标记列表中间（后跟 AG_TSOsc + 空格），故 `s/T_mBistOsc //g`（子串+尾随空格）正确工作。

## 通用化（siinp_rm_ref.py）
- 接口：`python3 solution.py <root>` → os.walk root 找所有 si.inp → `content.replace("T_mBistOsc ", "")` 原地写回
- 与金标准 sed `s/T_mBistOsc //g` 等价

## 案例合成
- A（可见）：matrix_run_A/ 8 子目录各含 si.inp，标记集旋转 + A_EndGuard 尾标记保证 T_mBistOsc 非末位
- hidden B：matrix_run_B/ 12 子目录 = 10 含目标（标记集旋转 + B_OnlyTkn 尾标记 + 2 个含子串 decoy T_mBistOscTail）+ 2 无目标 decoy
- check.py 14 断言(a-n) + 4 negative + negative_selftest
- 自验：ref PASS 14/14 ✓ + 4 negative 全 FAIL distinct ✓ + §4.9 三假全 FAIL ✓ + 断言闸门 14==14≥8 ✓
- 追加 EDA-Eval-DesignFlow_B.jsonl (197→198) + mark ledger (199→200 covered, spice_sim 157→158)
