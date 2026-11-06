# Deepread: 1793361216165_nqgxe (hbpeng @ hfeg0pkn005, mc=206, physical_verify, A-faithful)

## 用户原话 (U#0, 逐字)
`/home/pdk/hbpeng/code/scriptDevelop/tools/version/RunsetVersionFinder.py 特殊处理：针对文件夹/apps/imctf/runset/calibre/td/LDDB/，版本文件夹取/apps/imctf/runset/calibre/td/LDDB/*/data的一级子文件夹`

## 真实 trace
- nmsg=327, 1.42MB. Single-focus: add LDDB special-case to OOP runset version-folder scanner.
- 工具链: read_files (RunsetVersionFinder.py + .bak), list_allowed_files (/apps/imctf/runset/calibre/td/LDDB/*), write_to_file (modified script).
- 真实 LDDB 结构 (.14:/apps/imctf/runset/calibre/td/LDDB/): LDDB_G4/{data/{0.1,0.1.3,0.1.2_update_20240827,...,0.2.4},common}, LDDB_G4B/data/{0.0.1,...,LDDB2.0_package_0.1.16}, LDDB3.0/{common only, 无data}, frozen/{G3,G4,G4B,CWJFA,...}.
- 原脚本 (#2/#64 read): FileUtils/VersionScanner/RunsetScanner/TechlibScanner; `appendVersionDir` 第49-51行有**空if体语法错误**(`if "LDDB" in versionDir:` 后空白行); `_scanProject`/`_collectFromNested` **无 lddb 分支** -> LDDB 落入 _collectFromNested, 而 listSubdirs skip={common,runset} 使 data/<ver> 结构被错误遍历(_collectFromGeneral 找 .rule, 但 data/0.1 下是 02_cmdFile/01_TechLib 无顶层 .rule -> 漏报版本).
- 用户接受的金标准 (#72 read, 最终版): `appendVersionDir` 修复(去掉空if); 新增 `_scanProject` 的 `elif il=="lddb"` 与 `_collectFromNested` 的 `elif sl=="lddb"` 路由到新方法 `_collectFromLDDB(path,vlist,prefix,depth)`: 遍历 LDDB 子目录, `data/`->一级子目录全列入 release (`{prefix}/data/{ver}`), `frozen/`->一级子目录列入 beta, `common/package/current/git_repo` 跳过, hasRule->release, else 递归. 保留 VersionScanner/RunsetScanner/TechlibScanner 公开类与 scan()->(releaseVersions,betaVersions) 接口.

## case 设计 (L1-boundary, 离线 stdlib)
- 候选 = 修改后的 RunsetVersionFinder.py (在 submit.zip 内). check.py 导入候选模块, 用 `TechlibScanner(baseDir=fixture)` 在 fixture_A(可见)+fixture_B(隐藏) 上跑 scan(), 断言 release/beta 集合.
- asset A (可见, SUT sandbox): 原始 RunsetVersionFinder.py(空if语法错误, 待修) + fixture_A/(td/LDDB/LDDB_G4/data/{0.1,0.1.3,0.2.0_cmdFile}, LDDB_G4B/data/{0.0.1,0.1.10}, LDDB3.0/common(无data), frozen/{G3,G4}, NormalProj/{v1.0,v2.0}, CurrProj/current/c1, FrzProj/frozen/FZ1) + prompt.txt + task_brief.md.
- 隐藏 B (assets/.../hidden/fixture_B, 不进 SUT): qa/LDDB/LDDB_X/data/{alpha,beta_ver,gamma}, LDDB_Y/data/{delta,eps}, LDDB_Z/common(无data), LDDB_W/data(空), frozen/{F1,F2}, Proj2/{p1,p2}, Proj3/current/g1, FrzProjB/frozen/FZ9. 名称与A完全不同 -> 反硬编码.
- 陷阱/边界: LDDB3.0/LDDB_Z(无data)与LDDB_W(空data)均不产版本; nested frozen(FrzProj/frozen)经_collectFromNested归release(非beta); listSubdirs skip={common,runset} 使 runset/ 命名目录被跳过(原脚本设计).
- 判分 **14 条 ①-⑭ a-n**: (a)zip+py_compile捕获未修语法错 (b)TechlibScanner+scan二元组 (c)A LDDB_G4 data三版本 (d)A LDDB_G4B data两版本 (e)A LDDB3.0无data不产版本 (f)A LDDB frozen->beta且beta-only (g)A NormalProj默认路径回归 (h)A current->general (i)A 嵌套frozen归release (j)B LDDB_X跨输入三版本 (k)B LDDB_Y+LDDB_Z/W双边界 (l)B frozen beta+Proj2 normal (m)反硬编码B不含A独有basename (n)源码含_collectFromLDDB+stdlib-only+不硬编码A字面量.
- 自验: ref reference_submit.zip -> check() PASS True; 5 negatives (fake_empty/fake_print_expected/fake_core_deleted/naive_only_original/naive_hardcode_a) ALL FAIL NEG_RC=0; §4.9 三假(空壳/print期望/删core)全FAIL. k_rationale=k_check=14>=8 GATE PASS.
