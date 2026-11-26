# Deepread — 1791513539900_7bxtm (adaml @ hfeg0pkn002, mc21, spice_sim)

**trace**: 154 msgs / 849KB, scp'd via eda_flow from 10.129.2.11:/home/adaml/.cline/data/sessions/1791513539900_7bxtm/
**r679 revival #58** — 旧判 parked "gvim_encoding_howto" (r618 reaudit 复活; 2026-11-15 用户令: env-config/howto/Q&A 全部恢复可造)

## 用户真实意图（4 轮 user_input，verbatim）
1. `linux环境下，gvim打开文件，中文乱码，怎么办？` — how-to: gvim 中文乱码
2. `检查一下我的系统和个人目录，找到最合适的方案，帮我解决问题` — 让 agent 探环境并落地修复
3. `现在打开gvim打开文件，字符间距有点大，排版不好看` — 比例字体导致间距问题
4. `还有个小问题，中文字体很奇怪，有时候带衬线，有时候不带` — fontconfig 随机回退衬线/无衬线
（+ 第 5 轮 `当前系统，用什么命令打开 Markdown文件最合适？` 偏题，本 case 取主轴 1-4）

## agent 工具链（policy 禁 raw run_commands，用 list_allowed_files/read_files/search_codebase/editor）
- list_allowed_files: /home/adaml, /usr/share/fonts(各子目录), /usr/share/vim, /etc, /usr/share/applications, /usr/bin
- read_files: /etc/locale.conf (LANG=en_US.UTF-8), .bashrc/.bash_profile/.cdsinit, vim80/defaults.vim
- search_codebase: vimrc/locale/encoding 模式
- editor: 创建 /home/adaml/.vimrc（insert_line）→ 3 轮迭代编辑（guifont 比例→等宽；加 guifontwide 固定无衬线）
- 关键真值（trace + .75 ssh 复核）：
  - locale = en_US.UTF-8
  - Vim 8.0 (/usr/share/vim/vim80)
  - CJK 字体: Noto Sans CJK SC + Noto Serif CJK SC (/usr/share/fonts/google-noto-cjk/)
  - 等宽字体: DejaVu Sans Mono + Liberation Mono
  - 用户无 ~/.vimrc（乱码根因）
  - 最终 .vimrc: set encoding=utf-8 + fileencodings=ucs-bom,utf-8,cp936,gb18030,gbk,big5,euc-jp,euc-kr,latin1 + guifont=DejaVu\ Sans\ Mono\ 11 + guifontwide=Noto\ Sans\ CJK\ SC\ 11 + desert/dark + tabstop=4

## 合成决策
- archetype = env-config/how-to Q&A → 生成式配置 + 结构化诊断报告（fixture-parseable：system_manifest 即 fixture，可解析产 B-可重跑结构化结果）
- A 档 trace-faithful: system_manifest.json 字段全部取自 trace 真实探查
- hidden B: 合成 tianjiao @ hfeg0pkn008 / zh_CN.UTF-8 / Vim 9.0 / WenQuanYi Micro Hei Mono + Source Han Sans SC / Source Code Pro + Inconsolata / tabstop=2 / light / morning（结构异构于 A）
- cross-input guard: user/host/locale/vim_version/fonts/tabstop/background/colorscheme 全部 cross-input；A-leak 11 token
- 任务: 写 gvim_cjk_config_gen.py(workdir,out_dir) 解析 doc/ 产 gvim_cjk_config.vimrc + gvim_cjk_config_report.json(14 顶层键)
- check.py: 21 断言（a-u）: zip含脚本 + py_compile + SUT在B上exit0产双文件 + JSON dict + 14键 + user==B + host==B + locale==B + vim_version==B + cjk_fonts==B + mono_fonts==B + root_cause含B primary_issue + .vimrc encoding=utf-8 + fileencodings含utf-8+CJK + guifont∈B mono + guifontwide∈B cjk + tabstop==B + background==B + colorscheme==B + A-leak守卫 + 确定性3 rerun
- 自验: ref 21/21 PASS + 4 negs(空壳/print-only/hardcode-A/deleted-core)全 FAIL + A/B 双跑确认 ref 通用解

## infra-block 纠正（重要）
r678 报 "INFRA-BLOCK: ssh+eda_flow 阻塞 (t0002997 sandbox 身份无 e0031982 免密)" 是**误报**：r678 用 pyAether host=aether（sandbox t0002997）测试，非正确 eda_flow 通道。本轮经 eda_flow run_commands 在 .75 实测：whoami=e0031982、/home/t0002965/log 可读、ssh 10.129.32.75/10.129.2.10/10.129.2.11 全 OK。trace scp 成功（849KB）。⇒ r678 infra-block 结论作废，B 线 trace-based casemaking 通道正常。
