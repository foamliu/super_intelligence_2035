# SFT/RL 训练数据污染隔离审计 (Contamination-Isolation Audit)

> 红线 (§5.1): 158 eval 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集;
> 允许用 API 参考文档合成训练对, 但必须按 **API 名 / 函数签名** 隔离。

## 汇总

| 项 | 值 |
|:--|--:|
| eval 任务数 | 158 |
| PyAether 全量 API 池 | 4022 |
| 禁用 API 名 (出现在 eval 任务) | 111 |
| 　其中在池内 | 92 |
| 　其中不在池内 (动态/拼写) | 19 |
| 禁用函数签名数 | 158 |
| **可供 SFT 使用的 API 数 (池 − 禁用)** | **3930** |
| 可用 API 占池比例 | 97.71% |

## 禁用 API 频次 Top 30

| API | 出现任务数 |
|:--|--:|
| `md` | 43 |
| `dbGetAllLibs` | 24 |
| `dbDelLib` | 24 |
| `dbCreateLib` | 23 |
| `dbNewCV` | 21 |
| `dbCloseCV` | 20 |
| `dbOpenCVByType` | 16 |
| `Training Material` | 12 |
| `emyBoxF` | 8 |
| `dbCrtInst` | 8 |
| `emyPointArrayF` | 6 |
| `dbCrtRect` | 5 |
| `emyBitArray` | 4 |
| `emyCdbaNS` | 3 |
| `emyViaExtEncParam` | 3 |
| `dmGetObj` | 3 |
| `emyUnixNS` | 3 |
| `emyStringGetNumUniqueBits` | 2 |
| `emyPointF` | 2 |
| `dbSaveCV` | 2 |
| `EmyLPPHeader` | 2 |
| `MdePlatSession` | 2 |
| `MdePlatParamSweepCenterSpan` | 2 |
| `EmyNtlUtil` | 2 |
| `MdePlatDonauJobPolicy` | 2 |
| `MdePlatLSFJobPolicy` | 2 |
| `MdePlatOGEJobPolicy` | 2 |
| `MdePlatLocalJobPolicy` | 2 |
| `emyString` | 2 |
| `dbCrtNet` | 2 |

## 禁用 API 按 eval 类别分布

| 类别 | API 引用次数 |
|:--|--:|
| Design Content Query & Edit | 93 |
| Design Content Creation | 86 |
| Geometry Operation & Analysis | 56 |
| Database & Design Management | 56 |
| Simulation & Analysis Configuration | 27 |
| Utilities | 16 |

## 隔离规则 (预注册 · 先定后用)

1. **API 名隔离**: held-out SFT/RL 训练任务只能使用 `available_for_sft_apis` 中的 API; 禁止使用 `forbidden_api_frequency` 列出的任一 API。
2. **函数签名隔离**: 训练任务的 `def <name>(<args>)` 不得与 `per_task[*].signatures` 任一条逐字相同。
3. **prompt/断言隔离**: 训练任务的 prompt 文本与断言代码不得复制 158 eval 任务的对应内容。
4. **可合成**: 允许用 API 参考文档 (来自 `available_for_sft_apis`) 合成 doc→code 训练对, 并按上述规则隔离。
5. **复检**: 生成训练集后用本脚本重跑, 确认 `forbidden_api_set ∩ 训练集API = ∅`。

## 诚实性 / 局限

- API 名提取基于正则匹配 `pyScript.<Name>(` / `pyAether.<Name>(` / 下标访问; 极少数动态拼接 API 名可能漏提取 (见 `forbidden_apis_not_in_pool`)。
- 全量 API 池来自 `api_summary_api_only.json`; 若池更新需重跑本审计。
- 本审计只做隔离边界界定, 不生成训练数据; 不碰 GPU/协议/题面/check.py/超时/-p。
