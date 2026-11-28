# Deepread: 1789563641964_4bnkb (ivyli @ hfeg0plg79, mc489, physical_verify)

- Source: scp plg79 PATH-FIX sub `1789563641964_4bnkb/1789563641964_4bnkb.messages.json` (1.0MB / 290 msgs, Sep16-17).
- User ivyli 维护 SKILL `cxmt_layout_fastShortCheck.il` + 新建 pyAether Python port `cxmt_layout_fastShortCheckLVS.py`，对当前 layout 跑快速 LVS short-check。

## User asks (实质 design_flow)
1. **U[0]**: 改 SKILL，往 `lvsShortCheckRunsetFile` 里加 LVS 配置：
   `*lvsRunWhat: HNE` / `*lvsIncludeCmdsType: SVRF` / `*lvsSVRFCmds:{fake_seedLayer = V1_drawing AND V1_prohibit_fill} {DEVICE fake_dev fake_seedLayer M1net(POS) M1net(NEG)} {LVS SELECT DEVICE BY SEED LAYER fake_seedLayer}`
2. **U[41]**: 把 runset 里 `*cmnTemplate_RN: /proj/drjqa/V0/ver/lvs/%L/%l` 改成 `.../lvs/fastCheck/%L/%l`。
3. **U[67]**: 生成对应 pyAether Python 脚本（按 SKILL 语义）。
4. **U[139]**: pyAether 里 `leGlobalVariables` 也存在，SKILL 的 `leGlobalVariables->project` 在 python 是 `leGlobalVariables.project`，全部改。
5. **U[168]**: UnicodeDecodeError 'ascii' codec (pyAether load_utils exec 读文件 ascii 解码 0xe2) → 脚本须 ascii-safe。
6. **U[192]**: 所有函数名改成 `cxmt_layout_*` 前缀。
7. **U[216]**: `*cmnTemplate_RN: /proj/ddgoa/V0/ver/lvs/%L/%l hasn't been changed in python script` —— bug：早期 python 把 project 硬编码 drjqa，实际 project 是 ddgoa，sed 不匹配没改。修：用 runtime `leGlobalVariables.project` 填 `{proj}` 占位。

## 关键摩擦 / 学习点
- 原 `.il` 文件 0444 只读 → editor 失败 → 新建 `_updated.il`。
- SKILL `sprintf` 里 `%L`/`%l` 是格式符 → 须 `%%L`/`%%l` 才能产出字面 `%L`/`%l` 给 sed。
- sed BRE 里 `*` 是量词 → 须 `\*` 匹配字面 `*`（`^\*cmnTemplate_RN`）；用 `|` 作分隔避免路径 `/` 冲突。
- U[216] anti-hardcode：sed 模板须用 runtime project 占位 `{proj}`，不能硬编码 drjqa（否则 ddgoa project 的 runset 不匹配）。

## 最终 Python 算法 (`cxmt_layout_fastShortCheckLVS()`, ~150 行)
1. `proj = ae.leGlobalVariables.project`（runtime，非硬编码）
2. `ver = os.environ["Ver"]`, `user = os.environ["USER"]`
3. 路径：`lvs_runset_file=/proj/{proj}/{ver}/ver/lvs/{user}/lvsRunset`；`run_dir=.../lvsShortCheck/`；`shortcheck_runset=run_dir/lvsRunset.sh`
4. 校验原 runset 存在
5. `os.makedirs(run_dir)`; `cp -f` 原 runset → shortcheck_runset
6. **sed -i** patch cmnTemplate_RN：`s|^\*cmnTemplate_RN: /proj/{proj}/V0/ver/lvs/%L/%l|*cmnTemplate_RN: /proj/{proj}/V0/ver/lvs/fastCheck/%L/%l|`（`{proj}`=runtime project；`%L`/`%l` 字面保留；`\*` 锚定字面 *；`|` 分隔）
7. **append** LVS_CONFIG_BLOCK（HNE/SVRF/fake_seedLayer AND/DEVICE fake_dev/LVS SELECT DEVICE BY SEED LAYER）
8. `os.environ["MGC_CALIBRE_LVS_RUNSET_FILE"]=shortcheck_runset` + `ae.aeSetSubProcessEnv(...)`
9. `ae.aeRunCmdWithSocket(cv.libName,cv.cellName,cv.viewName,'calibre -gui -drc','',True)` 跑 Calibre
10. 还原 env var 回原 runset

## 关键抽象决策
真实跑需活 pyAether 会话 + leGlobalVariables + /proj FS + Calibre 许可 ⇒ 抽成纯 Python `lvs_shortcheck_patcher.py`：
- `build_shortcheck_runset(base_runset_text, project, ver, user, out_dir)`：在 out_dir 建目录、写 patched runset、设 env、返回结构化结果。
- `patch_runset_text(text, project)`：纯文本 patch（cmnTemplate_RN sed 语义 + append HNE/SVRF block），保留 `\*`/`%L`/`%l`/`|` 语义，runtime project 占位。
- 忠实保留：路径模板 `/proj/{proj}/{ver}/ver/lvs/{user}/lvsShortCheck/lvsRunset.sh`、cmnTemplate_RN 用 `V0`（非 {ver}，与真实 runset 一致）、HNE/SVRF/fake_seedLayer/M1net(POS)/M1net(NEG)/LVS SELECT DEVICE BY SEED LAYER 全串、env var 名 `MGC_CALIBRE_LVS_RUNSET_FILE`、还原语义。

## L0/L1 静态可判 LIVE-NA（Q2 不被骗）
- hidden B 用不同 project（ddgoa）+ 不同 Ver/USER + 不同 cmnTemplate_RN 原 path → 硬编码 A 的 project 的 stub 在 B 下 sed 不匹配（cmn_patched=False）→ c 挂。
- empty_stub（不 append block）→ HNE/SVRF 断言挂。
- print_only（不写文件）→ file-exist 挂。
- core_deleted（删 LVS SELECT）→ c 挂。
- sed-escape-broken（`*` 不锚定 / `%L` 被 Python format 吃掉）→ cmnTemplate_RN 残留或 %L 丢失 → c 挂。
- 独立复算 patched text 逐行比对，形状对内容错必挂。

claim: 4bnkb (ivyli/plg79, mc489, physical_verify). FRESH.
