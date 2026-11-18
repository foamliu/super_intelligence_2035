# cd2b8 deepread — PDK dummy deck 目录脚手架 + 软链接

- **session**: `1793871192062_cd2b8` (xinqiaoz@hfhds201 / 10.129.32.75, mc=55)
- **keywords**: pdk:306;drc:114;.gds:75;calibre:24 (cwd = PDK_QA 项目，关键词来自 cwd 非 task)
- **domain**: physical_verify (PDK QA dummy DRC deck 脚手架；与 xk5uw=DrcRuleDeckAnalyze 同一 PDK_QA 轨道)
- ** msgs**: 37 (user 8 real / assistant 29)
- **file**: `/home/xinqiaoz/.cline/data/sessions/1793871192062_cd2b8/1793871192062_cd2b8.messages.json` (本地 .75)

## 用户真实意图（两轮，逐字）

**U#0 (idx 0)**：
> 我期望你帮我在 /home/pdk/xinqiaoz/01_dummy/ 中创建一个 V4_mPV_X0S0F/ 的子目录，再建立这个子目录的目录结构，结构可以参考 /home/pdk/peiyaoz/00_Dummy/deck/V4_mPV_X0S0F/。只需要创建目录，不需要创建和复制文件。

**U#23 (idx 23, 末轮主任务)**：
> 帮我在 /home/pdk/xinqiaoz/01_dummy/V4_mPV_X0S0F/chip/V4_dummy_X0S0F_v0d1_Rev01/ 目录放一个指向 /home/pdk/peiyaoz/00_Dummy/deck/V4_mPV_X0S0F/chip/V4_dummy_X0S0F_v0d1_Rev01/ 的软链接，frame 目录也作类似的操作。

中间 U#24 助手 ask_question 选项「整目录软链接/别名 ref/别名 src/逐文件链接」→ 用户选「与源目录同名：软链接名 = V4_dummy_X0S0F_v0d1_Rev01，整目录软链接」（U#25）。

## 助手工具链

list_allowed_files (探查参考结构 depth 3→6，QA 子目录) → editor 写 JOURNAL + .tmp/SHELL_CMD_AGENT.txt (mkdir -p 两行) → run_approved_command shell_generic_pdkqa 执行 mkdir → list_allowed_files 验证 → editor 写 ln -s 命令 → run_approved_command 执行 → list_allowed_files 验证软链接 → editor 更新 JOURNAL 完成。

## trace-end-gold (A#36)

```
/home/pdk/xinqiaoz/01_dummy/V4_mPV_X0S0F/
├── chip/
│   └── V4_dummy_X0S0F_v0d1_Rev01/
│       ├── QA/                                                    (real dir)
│       └── V4_dummy_X0S0F_v0d1_Rev01 -> /home/pdk/peiyaoz/00_Dummy/deck/V4_mPV_X0S0F/chip/V4_dummy_X0S0F_v0d1_Rev01
└── frame/
    └── V4_dummy_X0S0F_v0d1_Rev01/
        ├── QA/                                                    (real dir)
        └── V4_dummy_X0S0F_v0d1_Rev01 -> /home/pdk/peiyaoz/00_Dummy/deck/V4_mPV_X0S0F/frame/V4_dummy_X0S0F_v0d1_Rev01
```

要点：
1. 只建目录，不建/复制文件（U#0 红线「只需要创建目录」）
2. 参考结构 QA 子目录下只有文件无嵌套子目录 → 完整骨架 = chip/.../QA + frame/.../QA
3. 软链接 = 整目录软链接，名称 = 源目录同名 `V4_dummy_X0S0F_v0d1_Rev01`，放在 chip/frame 各自的 `V4_dummy_X0S0F_v0d1_Rev01/` 目录内
4. 软链接目标 = peiyaoz 对应源目录绝对路径

## reframe（离线可验核心）

真实任务操作 `/home/pdk/...` 文件系统，SUT 沙盒不可达；参考树在 .75 peiyaoz home 亦不可经 MCP 透传给 SUT。抽离离线可验核心 = **给定参考目录树 manifest（JSON：dirs 列表 + symlinks 列表 + target_root），生成脚手架脚本 `pdk_dummy_scaffold.py`**，执行后：
- 在 target_root 下按 manifest.dirs 创建目录（仅目录，无文件）
- 按 manifest.symlinks 创建整目录软链接（名称 = 源目录 basename，目标 = manifest 给定绝对路径）
- 输出 JSON summary（created_dirs / created_symlinks / counts）

check() 在独立临时目录跑脚本于 **隐藏 B** manifest（结构不同：不同 dir 名 / 不同软链接数 / 不同 target_root），断言目录集合精确匹配 + 无文件 + 软链接名/目标正确 + 无多余 + 幂等 + 错误处理 + summary 结构 + anti-hardcode。

档 B-synthesized（输入 manifest 合成；真实路径保留于 manifest 内，不脱敏；意图 trace-faithful）。
子型: pdk-dummy-deck-dir-scaffold。

## 选料理由

- r794 guidance「优先非 xinqiaoz 候选增加用户多样性」—— 本候选仍为 xinqiaoz，但 r795 已用 y6ito (binwenh)，本轮 fresh 非 xinqiaoz 候选（mwqz9）经深读确证 wrong-domain（project-sync rsync 脚本，非 physical_verify）已 parked；其余 fresh 候选（gxf18/yd21d=meta Q&A 无牙；5n196=skill-dev；w5gg8=file-compare Q&A；rppe1=migration SOP；lmn7f=DRC compile-switch 逻辑复杂 reframe 风险高）中，cd2b8 拥有最干净的可验交付物（目录树+软链接，结构精确可断言，hidden B 易构造 anti-hardcode）。
- 2026-11-15 §二 reaudit：setup/env-config 现合法；PDK dummy deck 脚手架属 setup 类真实用户意图，可造。
