# BaiZe MLLM Bridge — Vision Tower HF Wrapper

This directory provides the HuggingFace-compatible wrapper for the BaiZe
vision tower (OpenVision2 ViT) and a custom LLaVA modeling file for
Stage(iv) MLLM alignment.

## Directory Structure

```
mllm_bridge/
├── __init__.py                      # Package init
├── configuration_baize_vision.py    # HF PretrainedConfig (model_type: baize_vision)
├── modeling_baize_vision.py         # HF PreTrainedModel (BaizeVisionModel)
├── modeling_llava_baize.py          # Custom LLaVA modeling (projector + LlavaBaizeModel)
├── config.json                      # HF config for the vision tower
├── test_wrapper_cpu.py              # CPU unit tests (no GPU needed)
└── README.md                        # This file
```

## Architecture (④-4ep checkpoint)

| Parameter | Value | Note |
|:--|:--|:--|
| `image_size` | 224 | Fixed for Stage-1 |
| `patch_size` | 16 | |
| `width` | **512** | (OpenVision2 class default is 1024; ④-4ep uses w512) |
| `depth` | 30 | |
| `heads` | 8 | = 512 // 64 |
| `mlp_dim` | 2048 | = 4 × 512 |
| `embed_dim` | 768 | ReadoutHead output; loaded but **skipped** in MLLM forward |
| `spatial_merge_size` | 1 | **No spatial merge** (196 tokens direct) |
| `num_patches` | 196 | = (224/16)^2 = 14^2 |
| `total_params` | 126.78M | (includes ReadoutHead ~0.39M) |

### Projector

| Parameter | Value |
|:--|:--|
| Architecture | 2-layer MLP: Linear(512->2560) -> GELU -> Linear(2560->2560) |
| Params | 7.87M |
| Input | `[B, 196, 512]` (patch features) |
| Output | `[B, 196, 2560]` (LLM hidden size for Qwen3-4B) |

## Usage

### Load the vision tower from checkpoint

```python
from mllm_bridge.modeling_baize_vision import BaizeVisionModel

model = BaizeVisionModel.from_baize_checkpoint(
    "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
)
# Output: [BaizeVision] load_state_dict(strict=True): matched=277/277, missing=[], unexpected=[]

import torch
x = torch.randn(1, 3, 224, 224)
patch_features = model(x)  # [1, 196, 512]
```

### Build the full LLaVA model (vision + projector + LLM)

```python
from transformers import AutoModelForCausalLM
from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import LlavaBaizeModel

vision = BaizeVisionModel.from_baize_checkpoint("vision.pt")
llm = AutoModelForCausalLM.from_pretrained("Qwen3-4B-path", torch_dtype="auto")
llava = LlavaBaizeModel(vision_tower=vision, llm_hidden_size=2560, language_model=llm)
image_embeds = llava.get_image_features(pixel_values)  # [B, 196, 2560]
```

### Run CPU unit tests

```bash
cd run/vision
python mllm_bridge/test_wrapper_cpu.py
```

## Key Differences from RICE ViT (LLaVA-OV1.5)

| Aspect | RICE ViT (LLaVA-OV1.5) | BaiZe OpenVision2 |
|:--|:--|:--|
| Architecture | patch14/d24/w1024/h16, GELU MLP | patch16/d30/w512/h8, SwiGLU MLP |
| Resolution | 336px (dynamic) | 224px (fixed Stage-1) |
| Patch tokens | 576 (24^2) | 196 (14^2) |
| Spatial merge | Yes (size=2 -> 576/4=144 tokens) | **No** (size=1 -> 196 tokens direct) |
| Projector | RicePatchMerger (inside vision tower) | Separate 2-layer MLP (512->2560) |
| CLS token | Yes | No (mean-pool in ReadoutHead, skipped) |
| ReadoutHead | N/A | Loaded for strict=True, **skipped** in MLLM forward |
| Params | 304M (vision only) | 126.78M (vision + head) |

## Checkpoint Path

```
/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt
```

Format: `{'vision': state_dict, 'config': {...}, ...}` — 277 keys, strict=True: 277/277 matched.

## Integration with ms-swift

ms-swift loads via `AutoModelForCausalLM.from_pretrained()` using `auto_map`
in `config.json`.  The `image_token_id` (151655) and template format follow
LLaVA-OneVision-1.5 conventions.  Key difference: 196 image tokens (vs
RICE's 144 after spatial merge).
