# MCP 消融实验：关闭 cimi_search / cimi_fetch / vqa

> 日期：2026-09-15  
> 实验类型：MCP 扩展消融对比  
> 评测模型：5 个大模型配置，每次运行 5 轮，共 25 次评测  
> 按顺序每 5 次分为一组

---

## 1. 实验设置

### 1.1 开启 MCP

扩展了 web search 和 vqa 两组 MCP，对应 `_TOOL_DEFAULTS` 中最下面的 3 个工具为 `True`：

```text
2026-09-11 16:39:57 - app - INFO -   cimi_search                    ON
2026-09-11 16:39:57 - app - INFO -   cimi_fetch                     ON
2026-09-11 16:39:57 - app - INFO -   vqa                            ON
```

对应工具开关：

```python
_TOOL_DEFAULTS = {
    "get_api_details":          True,   # 核心，常开
    "search_apis":              True,   # 核心，常开
    "search_apis_by_keyword":   True,   # 核心，常开
    "run_code":                 True,   # 核心，常开（原 run_pyAether_code_tool，0731 改名）
    "clean_workdir":            False,  # 危险操作，常关
    "query_memory_bank":        _l1_has_content,  # 有 L1 知识才开
    "probe_pyAether_code":      False,  # 默认关闭——Round2 显示 probe 118次多为过度验证开销，C1 改 P1-4 后不再需要。需要时设 EDA_MCP_TOOLS_ENABLED=probe_pyAether_code
    "cimi_search":              True,   # Web 搜索，开启
    "cimi_fetch":               True,   # Web 页面抓取，开启
    "vqa":                      True,   # 图像问答(kimi-k2.6-cloud)，开启
}
```

### 1.2 关闭 MCP

关闭 `_TOOL_DEFAULTS` 最下面的 3 个工具：`cimi_search`、`cimi_fetch`、`vqa`。

```text
2026-09-11 16:39:57 - app - INFO -   cimi_search                    OFF
2026-09-11 16:39:57 - app - INFO -   cimi_fetch                     OFF
2026-09-11 16:39:57 - app - INFO -   vqa                            OFF
```

对应工具开关：

```python
_TOOL_DEFAULTS = {
    "get_api_details":          True,   # 核心，常开
    "search_apis":              True,   # 核心，常开
    "search_apis_by_keyword":   True,   # 核心，常开
    "run_code":                 True,   # 核心，常开（原 run_pyAether_code_tool，0731 改名）
    "clean_workdir":            False,  # 危险操作，常关
    "query_memory_bank":        _l1_has_content,  # 有 L1 知识才开
    "probe_pyAether_code":      False,  # 默认关闭——Round2 显示 probe 118次多为过度验证开销，C1 改 P1-4 后不再需要。需要时设 EDA_MCP_TOOLS_ENABLED=probe_pyAether_code
    "cimi_search":              False,  # Web 搜索，默认关闭
    "cimi_fetch":               False,  # Web 页面抓取，默认关闭
    "vqa":                      False,  # 图像问答(kimi-k2.6-cloud)，默认关闭
}
```

> 结论：关闭最下面 3 个 MCP（`cimi_search`、`cimi_fetch`、`vqa`）后，分数更高。

---

## 2. 汇总对比：开启 MCP

| 组别 | 模型 | 均值 | 标准差（样本） | 有效次数 |
|---:|---|---:|---:|---:|
| 1 | deepseek-v4-pro-fp4 | 0.9284 | 0.0156 | 5 |
| 2 | glm-5.2 | 0.9013 | 0.0113 | 5 |
| 3 | deepseek-v4-flash | 0.8852 | 0.0287 | 4 |
| 4 | doubao-seed-2.0-pro-cloud | 0.6873 | 0.0213 | 5 |
| 5 | kimi-k2.6-cloud | 0.8855 | 0.0140 | 5 |

### 结论

- 第 1 组 `deepseek-v4-pro-fp4` 均值最高（0.9284），且波动较小。
- 第 2 组 `glm-5.2` 均值次之（0.9013），标准差最小（0.0113），表现最稳定。
- 第 3 组 `deepseek-v4-flash` 与第 5 组 `kimi-k2.6-cloud` 均值接近（约 0.885），但 `deepseek-v4-flash` 波动更大。
- 第 4 组 `doubao-seed-2.0-pro-cloud` 均值明显最低（0.6873），与前四组差距较大。

---

## 3. 汇总对比：关闭 MCP

> 关闭 `cimi_search`、`cimi_fetch`、`vqa`。  
> 当前仅整理到第 1 组 `deepseek-v4-pro-fp4` 的结果。

| 组别 | 模型 | 均值 | 标准差（总体） | 标准差（样本） | 有效次数 |
|---:|---|---:|---:|---:|---:|
| 1 | deepseek-v4-pro-fp4 | 0.9399 | 0.0081 | 0.0090 | 5 |

### 结论

- 关闭 `cimi_search`、`cimi_fetch`、`vqa` 后，`deepseek-v4-pro-fp4` 均值从 **0.9284** 提升到 **0.9399**。
- 标准差（样本）从 **0.0156** 降低到 **0.0090**，波动更小。
- 在 `deepseek-v4-pro-fp4` 上，关闭最下面 3 个 MCP 后表现更好。

---

## 4. 附录：开启 MCP 的轮次对应关系

根据 5 个大模型配置，每次运行 5 轮，共 25 次评测。  
按顺序每 5 次分为一组，对应关系如下：

| 组别 | 模型 | 对应评估轮次 |
|---:|---|---|
| 第1组 | deepseek-v4-pro-fp4 | 170153, 195340, 221957, 005959, 033509 |
| 第2组 | glm-5.2 | 055103, 075355, 100506, 120632, 141301 |
| 第3组 | deepseek-v4-flash | 161619, 175834, 204249, 233534, 234423 |
| 第4组 | doubao-seed-2.0-pro-cloud | 234938, 005355, 020315, 025916, 035240 |
| 第5组 | kimi-k2.6-cloud | 045017, 075604, 120021, 151942, 184214 |

---

## 5. 附录：开启 MCP 的分组明细

### 第1组：deepseek-v4-pro-fp4

| 轮次 | PASS_RATE |
|---|---:|
| 170153 | 0.9241 |
| 195340 | 0.9423 |
| 221957 | 0.9367 |
| 005959 | 0.9032 |
| 033509 | 0.9359 |

- 均值：0.9284
- 标准差（总体）：0.0139
- 标准差（样本）：0.0156

### 第2组：glm-5.2

| 轮次 | PASS_RATE |
|---|---:|
| 055103 | 0.8917 |
| 075355 | 0.9097 |
| 100506 | 0.8968 |
| 120632 | 0.9167 |
| 141301 | 0.8917 |

- 均值：0.9013
- 标准差（总体）：0.0101
- 标准差（样本）：0.0113

### 第3组：deepseek-v4-flash

| 轮次 | PASS_RATE |
|---|---:|
| 161619 | 0.8741 |
| 175834 | 0.8882 |
| 204249 | 0.8553 |
| 233534 | 0.9231 |
| 234423 | 无（0 脚本，未产生 PASS_RATE） |

- 有效数据均值（4 次）：0.8852
- 标准差（总体，4 次）：0.0248
- 标准差（样本，4 次）：0.0287

说明：`234423` 因组装出 0 个可执行脚本，Sandbox 报错 ❌ 无可执行脚本（`*.py`），未产生 PASS_RATE，计算时已排除。

### 第4组：doubao-seed-2.0-pro-cloud

| 轮次 | PASS_RATE |
|---|---:|
| 234938 | 0.6835 |
| 005355 | 0.7215 |
| 020315 | 0.6772 |
| 025916 | 0.6646 |
| 035240 | 0.6899 |

- 均值：0.6873
- 标准差（总体）：0.0190
- 标准差（样本）：0.0213

### 第5组：kimi-k2.6-cloud

| 轮次 | PASS_RATE |
|---|---:|
| 045017 | 0.8839 |
| 075604 | 0.8974 |
| 120021 | 0.9020 |
| 151942 | 0.8701 |
| 184214 | 0.8742 |

- 均值：0.8855
- 标准差（总体）：0.0125
- 标准差（样本）：0.0140

---

## 6. 附录：关闭 MCP 的分组明细

> 关闭 `cimi_search`、`cimi_fetch`、`vqa`。

### 第1组：deepseek-v4-pro-fp4

| 轮次 | Pass Rate |
|---|---:|
| 152253 | 0.9427 |
| 180729 | 0.9539 |
| 204303 | 0.9299 |
| 233152 | 0.9367 |
| 020828 | 0.9363 |

- 均值：0.9399
- 标准差（总体）：0.0081
- 标准差（样本）：0.0090

---

## 7. 关键发现

1. **关闭最下面 3 个 MCP 后，deepseek-v4-pro-fp4 分数更高**  
   关闭工具：`cimi_search`、`cimi_fetch`、`vqa`。  
   均值：0.9284 → 0.9399，提升约 **+0.0115**。

2. **关闭最下面 3 个 MCP 后，deepseek-v4-pro-fp4 更稳定**  
   样本标准差：0.0156 → 0.0090，波动明显降低。

3. **开启 MCP 时，模型间差距较大**  
   `deepseek-v4-pro-fp4` 和 `glm-5.2` 领先，`doubao-seed-2.0-pro-cloud` 明显落后。

4. **当前关闭 MCP 仅覆盖第 1 组模型**  
   其余 4 个模型在关闭 `cimi_search`、`cimi_fetch`、`vqa` 下的表现尚未整理，建议后续补齐以形成完整消融对比。

