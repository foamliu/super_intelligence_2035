#!/usr/bin/env python3
"""setup_compaction_arm_dirs.py — 为压缩机制消融构建两臂独立 cline data-dir。

按 ZHULONG_TASK.md §11 step(2) 的口径，并修正两处与现网不符的缺项：
  1. models.json 现网不含 `deepseek-v4-pro-cloud`（仅 flash/pro-fp4）→
     必须新增该条目并把 maxInputTokens 设为 32000，否则 32K regime 对评测模型不生效。
  2. ~/.cline/data/settings/providers.json 当前被别线改成 minicpm5-2b@localhost:8098 →
     必须把两臂 providers.json 改回评测基座 deepseek-v4-pro-cloud@/cloud/v1。

两臂除 compactionStrategy / --compaction 外逐字节一致，便于审计。
"""
import json, os, shutil, sys, hashlib

BASE_SETTINGS = os.path.expanduser("~/.cline/data/settings")
DEST_ROOT = "/nasdata/app.e0031982/compaction_ablation"
MAX_INPUT_TOKENS = 32000
CONTEXT_WINDOW = 1000000  # §11.2: contextWindow 可保留 1M；生效预算=min(两者)=32K

# 评测基座（与 B_en_r1 重跑 2026_1112_161042 对齐）
PROVIDER_SETTINGS = {
    "provider": "openai-compatible",
    "apiKey": "02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e",
    "model": "deepseek-v4-pro-cloud",
    "maxTokens": 16384,
    "baseUrl": "http://agi-gateway.cxmt.com/cloud/v1",
    "reasoning": {"enabled": False},
}

CAPS = ["streaming", "tools", "images"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def make_models_json():
    """models.json: 新增 deepseek-v4-pro-cloud 条目；所有模型 maxInputTokens=32000。"""
    src = os.path.join(BASE_SETTINGS, "models.json")
    d = json.load(open(src))
    prov = d["providers"]["openai-compatible"]
    # 确保 deepseek-v4-pro-cloud 在目录里
    models = prov.setdefault("models", {})
    models["deepseek-v4-pro-cloud"] = {
        "id": "deepseek-v4-pro-cloud",
        "name": "deepseek-v4-pro-cloud",
        "contextWindow": CONTEXT_WINDOW,
        "maxInputTokens": MAX_INPUT_TOKENS,
        "capabilities": CAPS,
    }
    # 所有模型 maxInputTokens 统一 32000（§11 step(2) 口径）
    for m in models.values():
        m["maxInputTokens"] = MAX_INPUT_TOKENS
    return d


def make_providers_json():
    """providers.json: 评测基座 deepseek-v4-pro-cloud（覆盖别线残留的 minicpm5-2b）。"""
    src = os.path.join(BASE_SETTINGS, "providers.json")
    d = json.load(open(src))
    d["lastUsedProvider"] = "openai-compatible"
    d["providers"]["openai-compatible"] = {
        "settings": PROVIDER_SETTINGS,
        "updatedAt": "2026-11-12T21:5x:00.000Z",
        "tokenSource": "compaction-ablation-setup",
    }
    return d


def make_global_settings(arm):
    src = os.path.join(BASE_SETTINGS, "global-settings.json")
    d = json.load(open(src))
    d["compactionEnabled"] = True
    d["compactionStrategy"] = arm  # basic | agentic
    return d


def main():
    arms = ["basic", "agentic"]
    log_lines = []
    for arm in arms:
        dest = os.path.join(DEST_ROOT, arm)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.makedirs(os.path.join(dest, "settings"))

        # 复制不变的设置文件
        for fn in ["cline_mcp_settings.json"]:
            s = os.path.join(BASE_SETTINGS, fn)
            if os.path.exists(s):
                shutil.copy(s, os.path.join(dest, "settings", fn))

        # secrets.json / globalState.json 在 ~/.cline/data/ (非 settings/)
        data_root = os.path.expanduser("~/.cline/data")
        for fn in ["secrets.json", "globalState.json"]:
            s = os.path.join(data_root, fn)
            if os.path.exists(s):
                shutil.copy(s, os.path.join(dest, fn))

        # 生成各臂差异化的设置文件
        json.dump(make_models_json(),
                  open(os.path.join(dest, "settings", "models.json"), "w"),
                  ensure_ascii=False, indent=2)
        json.dump(make_providers_json(),
                  open(os.path.join(dest, "settings", "providers.json"), "w"),
                  ensure_ascii=False, indent=2)
        json.dump(make_global_settings(arm),
                  open(os.path.join(dest, "settings", "global-settings.json"), "w"),
                  ensure_ascii=False, indent=2)

        # 留证：sha256 + compactionStrategy
        for fn in ["models.json", "providers.json", "global-settings.json"]:
            p = os.path.join(dest, "settings", fn)
            log_lines.append(f"{arm} {fn} sha256={sha(p)}")
        gs = json.load(open(os.path.join(dest, "settings", "global-settings.json")))
        mj = json.load(open(os.path.join(dest, "settings", "models.json")))
        mt = mj["providers"]["openai-compatible"]["models"]["deepseek-v4-pro-cloud"]["maxInputTokens"]
        log_lines.append(f"{arm} compactionStrategy={gs.get('compactionStrategy')} "
                         f"maxInputTokens(deepseek-v4-pro-cloud)={mt}")
        print(f"[{arm}] data-dir ready: {dest}")

    # 写 P0 配置留证
    log_path = "/tmp/COMP_p0_cfg.log"
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines) + "\n")
    print(f"\n=== P0 cfg log -> {log_path} ===")
    for line in log_lines:
        print(line)


if __name__ == "__main__":
    main()
