# 深读笔记 — 1792563679865_57rrw (e0039602@hfeg0pkn003, mc=60)

**真实 trace 溯源**：
- session_file: `1792563679865_57rrw.messages.json`
- user: e0039602 / host: hfeg0pkn003 (10.129.2.12) — 同会话亦在 .75 (NAS 共享 home)
- match_count: 60 (keywords: netlist:194;schematic:1 — 99% D-pure)
- 日期: 2026-10-21
- domain: schematic_netlist

## 项目背景
`/home/e0039602/Documents/netlist_change_v0.2copy` — 一个 **schematic netlist cell-converter agent** 项目。
功能：把 schematic netlist 中**在 simlib 里不存在的 cell**，逐行替换成 simlib 中存在的物理单元，
调用 AI agent（经由 OpenAI 风格 chat/completions 端点）一次性推理出全部映射，输出
"第 N 行 <原始实例> → 转换后 <实例>" 的文本报告。

项目结构：
```
netlist_change_v0.2copy/
  run.py              顶层入口：python run.py [--offline|--prompt-only|--parse-with-llm]
  config.yaml         agent 配置(token/URL/模型/请求风格/路径/429重试) 与 文件路径
  simlib_base.sv      随项目打包的 simlib
  _selftest.py        自检脚本
  netlistfile/newnetlist   待转换的 netlist
  src/
    simlib_lookup.py  读取 simlib 已知模块集合 + 提取指定物理单元源码
    netlist_parser.py 确定性解析：提取缺失 cell 实例(起始行号/端口连接/多行原文)
    llm_parser.py     大模型解析兜底
    offline_mapping.py 离线映射
    report_writer.py  报告写入
    rules_prompt.py   规则 prompt
    agent_client.py   agent 客户端
  outputs/            输出目录(result_map_<时间戳>.txt, rewritten_netlist.sv)
```

## config.yaml 原始内容（关键字段）
```yaml
agent:
  base_url: "http://10.129.8.86:8899/token/v1"
  token: "11_62462_a84a1a5d-c567-43d9-973d-375ff9aa41b9"   # ⚠ 真实 token，case 里需 mask
  model: "glm-5.0"
  endpoint: "chat/completions"
  payload_style: "messages"
  max_tokens: 65536               # 服务端实测接受的最大值(131072会超时)
  temperature: 0.0
  timeout: 600
  wait_on_429: 55
  max_429_retries: 4
  max_grow_tokens: 65536          # 自动扩容也封顶到 65536
  username: "E0039602"
paths:
  netlist: ""
  simlib: "simlib_base.sv"
  output_dir: "outputs"
  report: "outputs/result_map.txt"
  rewritten: "outputs/rewritten_netlist.sv"
```

## 用户意图（两轮）
### 轮 1 (主任务)
> "请你阅读这个项目，看一下config里设定的maxtoken是多少，你尝试一下看看这个maxtoken还有没有扩大的空间"

agent 实际做的事：
1. list_allowed_files 浏览项目结构
2. read_files config.yaml + README.md → 找到 max_tokens=65536, max_grow_tokens=65536
3. search_codebase 搜 "maxtoken/max_token/max_tokens/maxToken"
4. 创建 `_probe_maxtoken.py` — 探测服务端对不同 max_tokens 值的接受情况
   - 测试值序列: [70000, 81000, 98304, 110000, 118000, 131072, 140000, 163840, 200000, 262144]
   - 对每个值发一次最小请求 "Reply with just OK."，记录 HTTP code + elapsed + 响应片段
5. 运行 _probe_maxtoken.py → 实测发现：
   - **服务端对 max_tokens 的校验范围是 [1, 131072]**：131072 及以下全部 200，131073 及以上 400 拒绝
6. 编辑 config.yaml: max_tokens 65536 → **100000**, max_grow_tokens 65536 → **100000**
7. 创建 `_verify_maxtoken.py` — 用新配置发一次最小请求确认 100000 被接受
   - 运行结果: `config max_tokens=100000, max_grow_tokens=100000` / `HTTP 200 elapsed=0.8s`
8. 编辑 README.md — 去掉旧的"65536 是上限 / 131072 会超时"表述，改为"100000 + 服务端校验上限 [1,131072]"

### 轮 2 (清理)
> "把你刚刚创建的探测脚本都给我删了，注意别删错把有用的给我删了"

agent 实际做的事：
1. read_files _probe_maxtoken.py + _verify_maxtoken.py 确认内容
2. list_allowed_files 项目根目录确认现有文件
3. 创建 `_delete_probes.py` — 用 os.remove 精确删除两个探测脚本（无通配符），然后自我删除
4. 运行 _delete_probes.py → `removed _probe_maxtoken.py / removed _verify_maxtoken.py / removed _delete_probes.py`
5. list_allowed_files 确认项目原有文件完好

## 交付件 (DoD)
本轮 case 聚焦**轮 1 主任务**（轮 2 清理是 follow-up，可选）：
1. 修改后的 `config.yaml` — max_tokens 和 max_grow_tokens 都扩大到 >65536 且 ≤131072
2. `probe_maxtoken.py` — 探测服务端 max_tokens 接受范围的脚本（实测多个值，区分 200/400）
3. `verify_maxtoken.py` — 用新配置验证 max_tokens 被服务端接受的脚本（HTTP 200）
4. 更新后的 `README.md` — 同步反映新的 max_tokens 值和服务端校验范围

## 判分设计要点
- **隐藏输入 B**: 一个 mock gateway 脚本（emulates agi-gateway: 1<=max_tokens<=131072 → 200, else 400）
  + 一份 config.yaml_B（base_url 指向 mock gateway，token 为 mock 值）
- check() 把 SUT 提交的 config.yaml 的 base_url/token 替换为 B 的 mock 值，然后跑 SUT 的 probe/verify 脚本
  验证它们能正确区分 200/400 边界
- ≥8 断言：zip 内容、config 扩容、config 在服务端范围内、probe 脚本可编译、verify 脚本可编译、
  probe 实测能区分边界值（≤131072=200, >131072=400）、verify 实测新 max_tokens=200、README 同步更新
- 三假 FAIL: print_only（只打印不实测）、core_deleted（config 不改）、hardcode_a（硬编码 100000 但 probe 不实测）
- B 与 A 不相交: B 用不同 base_url/token/mock 端口，max_tokens 边界值随机化（不固定 131072）

## anti-hardcode 设计
- mock gateway 的 max_tokens 边界值在 B 里随机生成（如 [8192, 99999] 之间随机一个上限），
  SUT 的 probe 脚本必须**实测**才能发现边界——硬编码 131072 会在 B 上 FAIL
- A 档自包含: A 的 config.yaml 用一个 unreachable base_url，SUT 无法从 A 档直接探测真实边界，
  必须靠 probe 脚本逻辑正确（check() 在 B 上验证逻辑）
