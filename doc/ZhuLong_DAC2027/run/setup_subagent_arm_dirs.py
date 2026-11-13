#!/usr/bin/env python3
"""setup_subagent_arm_dirs.py — 为 subagent 消融实验构建 9 臂独立 cline data-dir。

臂设计:
  A0: baseline (spawn off)        — 复用 compaction basic 数据, 不新建
  A1: spawn-on (自主 spawn)       — enableSpawnAgent=true, 无 configured agent
  B1: cfg-same (同基座)            — researcher.yaml modelId=dsv4-pro-cloud
  B2: cfg-dsv4-flash              — researcher.yaml modelId=dsv4-flash
  B3: cfg-doubao-pro              — researcher.yaml modelId=doubao-seed-2.0-pro-cloud
  B4: cfg-doubao-mini             — researcher.yaml modelId=doubao-seed-2.0-mini-cloud
  B5: cfg-doubao-lite             — researcher.yaml modelId=doubao-seed-2.0-lite-cloud
  C1: cfg-iter5                   — researcher.yaml maxIterations=5 (dsv4-flash)
  C2: cfg-iter30                  — researcher.yaml maxIterations=30 (dsv4-flash)

P0 预检关键修正:
  1. configured agent 文件必须用 .yaml 扩展名 (cline isYamlFile 限制)
  2. tools 字段必须用完整 MCP 工具名 (pyAether_MCP_server__search_apis)
  3. doubao 3 档走同一 gateway 但 API key 各异, 需注册 3 个独立 provider entry
"""
import json, os, shutil, sys, hashlib

BASE_SETTINGS = os.path.expanduser("~/.cline/data/settings")
DEST_ROOT = "/nasdata/app.e0031982/subagent_ablation"
CONTEXT_WINDOW = 1000000
MAX_INPUT_TOKENS = 32000  # 与 compaction 实验一致 (natural-128K regime)

# 评测基座 (主 agent, 所有臂恒定)
MAIN_PROVIDER_SETTINGS = {
    "provider": "openai-compatible",
    "apiKey": "02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e",
    "model": "deepseek-v4-pro-cloud",
    "maxTokens": 16384,
    "baseUrl": "http://agi-gateway.cxmt.com/cloud/v1",
    "reasoning": {"enabled": False},
}

# doubao 3 档 (subagent 弱基座, 各自独立 API key)
DOUBAO_PROVIDERS = {
    "doubao-pro": {
        "apiKey": "02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f",
        "model": "doubao-seed-2.0-pro-cloud",
    },
    "doubao-mini": {
        "apiKey": "02_088EE9051AAE4BF0ABFC7130331BF697_caa8bffa-b976-47f5-acc3-4141f6c5b90f",
        "model": "doubao-seed-2.0-mini-cloud",
    },
    "doubao-lite": {
        "apiKey": "02_088EE9051AAE4BF0ABFC7130331BF697_78b81092-7e90-436e-aa8a-5ab8510567fe",
        "model": "doubao-seed-2.0-lite-cloud",
    },
}

CAPS = ["streaming", "tools", "images"]

# researcher.yaml system prompt (所有臂共用)
RESEARCHER_SYSTEM_PROMPT = """你是 pyAether API 探索研究员。主 agent 会给你一个或多个 API 名称或任务描述，
你需要用 search_apis 和 get_api_details 工具查询每个 API 的文档，
返回结构化摘要：

## 输出格式（对每个 API）
### API: <name>
- **签名**: 函数签名（参数类型 + 返回类型）
- **参数**: 每个参数的含义和约束
- **返回值**: 返回类型和含义
- **副作用**: 是否修改 design/库/文件
- **示例**: 文档中的示例代码（如有）

## 规则
1. 只用 get_api_details 返回的真实 API，不臆造
2. 不写代码、不运行代码、不调用 run_pyAether_code_tool
3. 如果 API 不存在，明确报告 "API not found"
4. 查完所有 API 后返回完整摘要，不要中途建议写代码
"""

# 臂定义
ARMS = {
    "A1": {"spawn": True, "researcher": None, "label": "spawn-on 自主构建"},
    "B1": {"spawn": True, "researcher": {"providerId": "openai-compatible", "modelId": "deepseek-v4-pro-cloud", "maxIter": 15}, "label": "cfg-same 同基座"},
    "B2": {"spawn": True, "researcher": {"providerId": "openai-compatible", "modelId": "deepseek-v4-flash", "maxIter": 15}, "label": "cfg-dsv4-flash"},
    "B3": {"spawn": True, "researcher": {"providerId": "doubao-pro", "modelId": "doubao-seed-2.0-pro-cloud", "maxIter": 15}, "label": "cfg-doubao-pro"},
    "B4": {"spawn": True, "researcher": {"providerId": "doubao-mini", "modelId": "doubao-seed-2.0-mini-cloud", "maxIter": 15}, "label": "cfg-doubao-mini"},
    "B5": {"spawn": True, "researcher": {"providerId": "doubao-lite", "modelId": "doubao-seed-2.0-lite-cloud", "maxIter": 15}, "label": "cfg-doubao-lite"},
    "C1": {"spawn": True, "researcher": {"providerId": "openai-compatible", "modelId": "deepseek-v4-flash", "maxIter": 5}, "label": "cfg-iter5"},
    "C2": {"spawn": True, "researcher": {"providerId": "openai-compatible", "modelId": "deepseek-v4-flash", "maxIter": 30}, "label": "cfg-iter30"},
}


def make_researcher_yaml(arm_config):
    """生成 researcher.yaml (configured agent 定义)."""
    r = arm_config["researcher"]
    return f"""---
name: researcher
description: pyAether API 探索研究员。在写代码前必须调用此 agent 查询所需 API 的文档，获取签名、参数、返回值等关键信息。
tools:
  - pyAether_MCP_server__search_apis
  - pyAether_MCP_server__get_api_details
providerId: {r['providerId']}
modelId: {r['modelId']}
maxIterations: {r['maxIter']}
---

{RESEARCHER_SYSTEM_PROMPT}
"""


def make_models_json(arm_config):
    """models.json: 主基座 + doubao provider (如果该臂的 researcher 用 doubao)."""
    src = os.path.join(BASE_SETTINGS, "models.json")
    d = json.load(open(src))
    prov = d["providers"]["openai-compatible"]
    models = prov.setdefault("models", {})
    # 确保主基座在
    models["deepseek-v4-pro-cloud"] = {
        "id": "deepseek-v4-pro-cloud", "name": "deepseek-v4-pro-cloud",
        "contextWindow": CONTEXT_WINDOW, "maxInputTokens": MAX_INPUT_TOKENS, "capabilities": CAPS,
    }
    # 所有 deepseek 模型 maxInputTokens 统一
    for m in models.values():
        m["maxInputTokens"] = MAX_INPUT_TOKENS

    # 如果该臂用 doubao subagent, 注册 doubao provider 到 models.json
    if arm_config["researcher"]:
        r = arm_config["researcher"]
        pid = r["providerId"]
        if pid.startswith("doubao"):
            mid = r["modelId"]
            d["providers"][pid] = {
                "provider": {
                    "name": f"Doubao {pid.split('-')[1].title()}",
                    "baseUrl": "http://agi-gateway.cxmt.com/cloud/v1",
                    "defaultModelId": mid,
                },
                "models": {
                    mid: {
                        "id": mid, "name": mid,
                        "contextWindow": 128000, "maxInputTokens": MAX_INPUT_TOKENS,
                        "capabilities": ["streaming", "tools"],
                    }
                },
            }
    return d


def make_providers_json(arm_config):
    """providers.json: 用 compaction basic 的验证过的模板作为基础, 追加 doubao provider.
    ⚠️ 不能从 ~/.cline/data/settings/providers.json 构建 (那里是别线的 minicpm5-2b);
    必须用 compaction basic 的模板 (已验证能跑 cline)."""
    template_path = "/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json"
    d = json.load(open(template_path))
    d["lastUsedProvider"] = "openai-compatible"

    # 如果该臂用 doubao subagent, 追加 doubao provider
    if arm_config["researcher"]:
        r = arm_config["researcher"]
        pid = r["providerId"]
        if pid in DOUBAO_PROVIDERS:
            db = DOUBAO_PROVIDERS[pid]
            d["providers"][pid] = {
                "settings": {
                    "provider": "openai-compatible",
                    "apiKey": db["apiKey"],
                    "model": db["model"],
                    "maxTokens": 16384,
                    "baseUrl": "http://agi-gateway.cxmt.com/cloud/v1",
                    "headers": {},
                    "timeout": 30000,
                    "reasoning": {"enabled": False},
                },
                "updatedAt": "2026-11-13T18:00:00.000Z",
                "tokenSource": "subagent-ablation-setup",
            }
    return d


def make_global_settings():
    """global-settings.json: compaction=basic (已选定为优)."""
    src = os.path.join(BASE_SETTINGS, "global-settings.json")
    d = json.load(open(src))
    d["compactionEnabled"] = True
    d["compactionStrategy"] = "basic"
    return d


def main():
    log_lines = []
    for arm_name, arm_config in ARMS.items():
        dest = os.path.join(DEST_ROOT, arm_name)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.makedirs(os.path.join(dest, "settings"))

        # 复制不变的设置文件
        for fn in ["cline_mcp_settings.json"]:
            s = os.path.join(BASE_SETTINGS, fn)
            if os.path.exists(s):
                shutil.copy(s, os.path.join(dest, "settings", fn))

        # secrets.json / globalState.json
        data_root = os.path.expanduser("~/.cline/data")
        for fn in ["secrets.json", "globalState.json"]:
            s = os.path.join(data_root, fn)
            if os.path.exists(s):
                shutil.copy(s, os.path.join(dest, fn))

        # 生成差异化设置文件
        # ⚠️ providers.json: 不能从 BASE_SETTINGS 复制再改 (cline auto-migration 会覆盖)；
        #    必须直接写入完整的评测基座配置
        json.dump(make_models_json(arm_config),
                  open(os.path.join(dest, "settings", "models.json"), "w"),
                  ensure_ascii=False, indent=2)
        json.dump(make_providers_json(arm_config),
                  open(os.path.join(dest, "settings", "providers.json"), "w"),
                  ensure_ascii=False, indent=2)
        json.dump(make_global_settings(),
                  open(os.path.join(dest, "settings", "global-settings.json"), "w"),
                  ensure_ascii=False, indent=2)

        # 生成 researcher.yaml (如果该臂有 configured agent)
        if arm_config["researcher"]:
            agents_dir = os.path.join(dest, "agents")
            os.makedirs(agents_dir, exist_ok=True)
            yaml_content = make_researcher_yaml(arm_config)
            with open(os.path.join(agents_dir, "researcher.yaml"), "w") as f:
                f.write(yaml_content)
            log_lines.append(f"{arm_name} researcher.yaml: providerId={arm_config['researcher']['providerId']} "
                           f"modelId={arm_config['researcher']['modelId']} maxIter={arm_config['researcher']['maxIter']}")
        else:
            log_lines.append(f"{arm_name} no configured agent (spawn only)")

        # 记录 provider keys
        prov_keys = list(json.load(open(os.path.join(dest, "settings", "providers.json")))["providers"].keys())
        log_lines.append(f"{arm_name} providers: {prov_keys}")
        print(f"[{arm_name}] data-dir ready: {dest} ({arm_config['label']})")

    # 写 P0 配置留证
    log_path = "/tmp/SUBAGENT_p0_cfg.log"
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"\n=== P0 cfg log -> {log_path} ===")
    for line in log_lines:
        print(f"  {line}")


if __name__ == "__main__":
    main()
