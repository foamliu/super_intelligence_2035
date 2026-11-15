# Deep-read: s5o5k — EDA 桥接服务 (pyAether) 配置失败根因诊断

**session**: `1794357676593_s5o5k`  
**user**: e0047527 @ hfeg0pkn005 (IP 10.129.2.14 bond0 / 10.129.139.33 bond1)  
**login node**: hfeg0plg103 (IP 10.129.8.235)  
**mc**: 400 (B 池复活候选, 旧判 debug-Q&A reject)  
**trace**: .75 scp 1.58MB, 358 msgs, 29 真实用户轮  
**审计**: r618 reaudit 191 误杀复活池, 本条旧判 "debug-Q&A → reject", 新标准 env-config/setup 恢复可造  
**case**: EDA-Eval-DesignFlow-BridgeCfgDiag-001 (spice_sim L1 便携 debug-Q&A 根因诊断, A 档 trace-faithful)

## 真实用户意图

用户 e0047527 通过 cline/zhulong EDA Agent 使用桥接服务（code-sidecar → pyAether TCP bridge 内嵌于 Aether）
远程操控 Aether 做版图/原理图自动化。从登录节点 hfeg0plg103 经 zl.sh/bsub 提交 job 到计算节点 hfeg0pkn005，
但桥接连接持续 ECONNREFUSED。用户逐个贴报错问 how-to-fix，并最终要求写一份 EDA 桥接配置指南文档。

## 根因链（7 条互相独立）

1. **ip_port.json IP 错位** — zl.sh 在登录节点生成 ip_port.json, IP=10.129.8.235 (登录节点), 但桥接跑在计算节点 → 应为 bond0 IP 10.129.2.14
2. **被测端口 38869 不在配置** — 正确 pyAether 端口 38865 (uid=23237, formula 20000+((23237*10008)%45533))
3. **~/.empyrean/aether.ini 缺失** — Aether 启动用安装目录默认 aether.ini, Py Script=${PY_INIT_FILE}=aetherwings/init.py, CXMT init.py 从未加载 → CXMT_zhulong_EDAAgent.py 桥接模块未加载
4. **CXMT_START_EDA_AGENT_SERVER 未设置** — 桥接 TCP server 自启动门控于此环境变量 (CXMT_zhulong_EDAAgent.py:430)
5. **DEEP_PING 协议版本不匹配** — 新版 code-sidecar 发 DEEP_PING 心跳, 旧版桥接当 Python 执行 → NameError (不影响 run_code)
6. **bond1 网卡 MCP 不可达** — MCP Server 10.129.8.86 在 10.129.x 段, 可达 bond0 (10.129.2.x) 不可达 bond1 (10.129.139.x)
7. **gedit libharfbuzz 冲突** — LD_LIBRARY_PATH 被 Cadence incisive lib 污染, 旧 libfreetype.so.6 缺 FT_Done_MM_Var

## 合成

- A 档 trace-faithful: 保留真实用户名/主机名/IP/端口/环境变量名/文件路径/报错原文
- 形态: reaudit「env-config 多根因诊断」操作化, 7-独立根因-category, 首例桥接配置诊断
- A=workdir/ 含 settings/{ip_port,cline_mcp_settings,identity}.json + env/{actual_host_info,aether_ini_status,env_vars,port_formula}.txt + logs/{conn_test_38869,conn_test_38865,deep_ping_error,gedit_error,aether_log}.log
- hidden B: 计算节点 hfeg0pkn001 (bond0=10.129.2.10), uid=41000 → ports 50137/45604/41071, ip_port.json IP=172.16.8.106, aether.ini exists but wrong_init (aetherwings 非 CXMT), CXMT_START_EDA_AGENT_SERVER=1 (set), 6 项全异 cross-input guard
- 任务: 写 diagnose_bridge_config.py(workdir,out_json) 解析 12 文件产出 diagnostic_report.json(23 顶层键), 打包 submit.zip
- 13 断言 a-m 含 cross-input guard(m: 重跑隐藏 B==oracle_B + A vs B 在 correct_ip/computed_ports/aether_ini_status 三项全异)
- 自验: ref 13/13 PASS + 4 negs 全 FAIL + §4.9 degenerate 全 FAIL + negative_selftest GREEN
- k=13, k_check==k_rationale ✓
