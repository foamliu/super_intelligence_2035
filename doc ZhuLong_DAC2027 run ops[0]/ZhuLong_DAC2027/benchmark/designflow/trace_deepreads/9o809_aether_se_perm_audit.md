# 深读笔记 — 9o809 (e0047722 Aether SE 脚本/权限审计)

- **session**: 1793324531319_9o809 · user `e0047722` (E0047722, LuoRoy, roy.luo@cxmt.com) · host hfeg0pkn002 (10.129.8.125) · mc=332 · 210 msgs (120 user / 90 assistant, agent=lead)
- **trace 源**: cline messages.json 2.5MB，真实抓取自 10.129.8.125

## 用户真实意图链（逐字）

- U#0: 「帮我分析下 /apps/imctf/cad/init/settings_aether/python_ae/se/ 目录下的脚本工具运行机制」
- U#19: 「这些工具是集成到本机的哪个软件里的，该软件如何启动？」
- U#62: 「帮我找下 V0_Austin 是本机 Aether 哪个项目的版本」
- U#96: 「能区分出本机的哪些 proj 本用户是有权限打开 Aether SE 的吗？」
- U#102: 「我的用户名是 E0047722」
- U#154-166: 启动 Aether / 工具未加载的配置排障
- U#195-206: 脚本→agent 桥接方案（CLI wrapper / skill 封装），最终 U#206 要求生成「方案设计说明书（模块设计/时序图/交互流程图）」

## agent 实际工具链（permission/version audit 段 #97-#153）

1. `read_files` 读 `/apps/imctf/cad/init/initProj/project.table`（3787 行，列：Proj Version Process Workdir Group WorkSite RefSites EDAPlatform InitEnv TechLibName LayerSet Is_Trail_Proj Is_SOS_Proj）
2. 推导 Aether SE 判据：`EDAPlatform==Aether` 且 `InitEnv==df2_LP_ae`（共 645 条）
3. 读 `/apps/imctf/cad/init/initProj/df2/df2_LP_ae` 启动脚本，提取权限检查：
   `lcproj=${proj,,}; case $lcproj in train|...) 直通 ;; *) if [[ id $USER |grep -i $lcproj ]] then ok else "Wrong project name or have no permission" fi ;; esac`
4. 用户身份：`id`/`groups` → e0047722 UID 205260，LDAP 管理，仅属 `guest` 组（GID 555），项目组在 LDAP 不在 /etc/group
5. `run_approved_command` 跑自制 `user_groups.py` → 确认仅 guest 组

## agent 最终交付（#153，用户接受）

- 权限判据：用户组必须匹配项目（组）名
- e0047722 仅在 `guest` 组 → **对全部 Aether 项目 0 权限**
- V0_Austin：**未在中央 project.table 注册**（可能是用户本地工作版本）
- Aether 项目示例：drcoa / drcpa / dscqa / decqa / lacaa / drgqa / ddcpc / ddgoa / ...

## 旧规则 parking（2026-11-08）→ 11-15 重审复活

- 旧 parked 理由：「env-recon+prose design doc (CLI wrapper 方案设计说明书); final deliverable msg#209 prose 30KB violates §4.2/§4.3」
- 11-15 任务初心：env-config / setup / Q&A / explain 类全部恢复为可造；本 trace 是典型被旧规则误杀的 B 类
- 本 case 取**可计算子意图**（U#62/U#96/U#102 权限+版本审计），reframe 为纯 stdlib compute produce-task，判分有牙；非 prose-doc 框架（prose-doc 难给 check() subprocess 牙）

## reframe = aether-se-permission-audit（mock-behavioral 家族新子型）

- 真实 Aether SE 项目权限机制 path-dependent → 离线可判分：解析 project.table（列对齐 whitespace）→ 过滤 Aether 行 → 解析 /etc/group 风格组文件 → 用户组归属交叉 → 输出 JSON 权限审计报告 + V0 查找
- distinct vs r719 ClineSkillRegPathRewrite=skill 注册路径重写 / r718 AutoViaRunnerPrep=skill 可运行包 / r717 LayerShapeDeleteCount=cellview 图形删除计数 = 本例 **Aether SE 项目权限矩阵审计 + 版本查找**
- 11-15 task初心 B 类复活实证：env-config/permission-audit 类真实任务旧规则判 weak 不可造，11-15 令 §二全部恢复为可造
