#!/usr/bin/env python
"""Custom lmms-eval model wrapper for BaiZe-LLaVA (BaiZe ViT + MLP projector + Qwen3-4B LoRA).

Registers as model name "baize_llava" in lmms-eval.
"""

import os, sys, math, torch, torch.nn as nn
from typing import List, Tuple, Optional
from PIL import Image
from torchvision import transforms as T

from lmms_eval.api.model import lmms
from lmms_eval.api.registry import register_model
from lmms_eval.api.instance import Instance

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from mllm_bridge.modeling_baize_vision import BaizeVisionModel
from mllm_bridge.modeling_llava_baize import BaizeMultiModalProjector
from mllm_bridge.open_clip_vitb16_768 import create_baize_vitb16_768, BAIZE_VITB16_WIDTH
from mllm_bridge.open_clip_vitl14_1024 import create_baize_vitl14_1024, BAIZE_VITL14_WIDTH

IMAGE_TOKEN_ID = 151655
NUM_IMAGE_TOKENS = 196
LLM_HIDDEN_SIZE = 2560
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

@register_model("baize_llava")
class BaizeLLaVA(lmms):
    """BaiZe-LLaVA: BaiZe ViT (frozen) + 2-layer MLP projector + Qwen3-4B (LoRA)."""

    is_simple = False  # chat model: supports generate_until + loglikelihood

    def __init__(self, ckpt="/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt",
                 stage2_ckpt="/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2/step3500",
                 llm_path="/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507",
                 device="cuda", batch_size=1, max_new_tokens=128,
                 vision_backend="baize_4ep", **kwargs):
        """vision_backend:
             'baize_4ep' -> BaizeVisionModel.from_baize_checkpoint(ckpt)  (512-d, ④-4ep tower)
             'armB'      -> create_baize_vitb16_768(pretrained=ckpt)       (768-d, open_clip ViT-B/16)
        """
        super().__init__()
        self.vision_backend = vision_backend
        # ---- Multi-GPU support via accelerate (LOCAL_RANK) ----
        local_rank = int(os.environ.get("LOCAL_RANK", -1))
        if local_rank >= 0:
            device = f"cuda:{local_rank}"
            torch.cuda.set_device(local_rank)
        self._device = torch.device(device if torch.cuda.is_available() else "cpu")
        self._batch_size = batch_size
        self._max_new_tokens = max_new_tokens
        self.dtype = torch.bfloat16
        self.task_dict = {}  # set by evaluator before generate_until/loglikelihood
        self.transform = T.Compose([T.Resize(int(224*1.15)), T.CenterCrop(224), T.ToTensor(), T.Normalize(CLIP_MEAN, CLIP_STD)])
        self.tokenizer = AutoTokenizer.from_pretrained(llm_path, trust_remote_code=True)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.eot_token_id = self.tokenizer.eos_token_id
        if self.vision_backend == "armE":
            # armE: open_clip ViT-L/14, 1024-d patch tokens [B,256,1024]
            self.vision, _, _ = create_baize_vitl14_1024(pretrained=ckpt, device="cpu")
            vision_width = BAIZE_VITL14_WIDTH  # 1024
            print(f"[BaizeLLaVA] vision_backend=armE (open_clip ViT-L/14, 1024-d) ckpt={ckpt}")
        elif self.vision_backend in ("armB", "armC", "armD"):
            # armB/armC/armD: open_clip ViT-B/16, 768-d patch tokens [B,196,768]
            self.vision, _, _ = create_baize_vitb16_768(pretrained=ckpt, device="cpu")
            vision_width = BAIZE_VITB16_WIDTH  # 768
            print(f"[BaizeLLaVA] vision_backend={self.vision_backend} (open_clip ViT-B/16, 768-d) ckpt={ckpt}")
        else:
            # ④-4ep: BaiZe OpenVision2 ViT, 512-d patch tokens [B,196,512]
            self.vision = BaizeVisionModel.from_baize_checkpoint(ckpt)
            vision_width = self.vision.config.width  # 512
            print(f"[BaizeLLaVA] vision_backend=baize_4ep (BaiZe ViT, {vision_width}-d) ckpt={ckpt}")
        self.vision = self.vision.to(device=self._device, dtype=self.dtype)
        for p in self.vision.parameters(): p.requires_grad = False
        self.vision.eval()
        self.projector = BaizeMultiModalProjector(vision_width, LLM_HIDDEN_SIZE).to(device=self._device, dtype=self.dtype)
        proj_path = os.path.join(stage2_ckpt, "projector.pt")
        if os.path.exists(proj_path):
            ck = torch.load(proj_path, map_location="cpu", weights_only=False)
            sd = ck.get("projector", ck) if isinstance(ck, dict) else ck
            sd = {k.replace("module.", "", 1) if k.startswith("module.") else k: v for k, v in sd.items()}
            self.projector.load_state_dict(sd, strict=True)
        else:
            raise FileNotFoundError(f"Projector not found: {proj_path}")
        self.projector.eval()
        llm = AutoModelForCausalLM.from_pretrained(llm_path, torch_dtype=self.dtype, device_map={"": str(self._device)}, trust_remote_code=True)
        adapter_config = os.path.join(stage2_ckpt, "adapter_config.json")
        if os.path.exists(adapter_config):
            self.llm = PeftModel.from_pretrained(llm, stage2_ckpt, is_trainable=False)
            # ★ Critical: merge LoRA weights into base model before generate().
            # PeftModel.generate() with inputs_embeds may not properly apply LoRA
            # adapters across the autoregressive loop (step 1 uses inputs_embeds,
            # steps 2+ use input_ids).  merge_and_unload() bakes LoRA deltas into
            # the base weights so the standard HF generate() path is used,
            # guaranteeing LoRA-adapted weights at every step.
            try:
                self.llm = self.llm.merge_and_unload()
                print(f"[BaizeLLaVA] LoRA adapters merged into base model (merge_and_unload)")
            except Exception as e:
                print(f"[BaizeLLaVA] WARNING: merge_and_unload failed ({e}), keeping PeftModel wrapper")
        else:
            self.llm = llm
        self.llm.eval()
        print(f"[BaizeLLaVA] Model loaded on {self._device} (local_rank={local_rank})")



    @property
    def device(self): return self._device
    @property
    def batch_size(self): return self._batch_size
    @property
    def rank(self): return int(os.environ.get("LOCAL_RANK", 0))
    @property
    def world_size(self): return int(os.environ.get("WORLD_SIZE", 1))

    def _prepare_image(self, visual):
        if isinstance(visual, Image.Image):
            img = visual.convert("RGB")
        elif isinstance(visual, str):
            img = Image.open(visual).convert("RGB")
        elif isinstance(visual, torch.Tensor):
            return visual.unsqueeze(0).to(device=self._device, dtype=self.dtype)
        elif isinstance(visual, dict):
            # HF datasets often stores images as {'bytes': ..., 'path': ...}
            if "image" in visual:
                inner = visual["image"]
                if isinstance(inner, Image.Image):
                    img = inner.convert("RGB")
                elif isinstance(inner, str):
                    img = Image.open(inner).convert("RGB")
                elif isinstance(inner, dict) and "bytes" in inner:
                    import io
                    img = Image.open(io.BytesIO(inner["bytes"])).convert("RGB")
                else:
                    raise ValueError(f"Cannot parse image from dict['image']={type(inner)}")
            elif "bytes" in visual:
                import io
                img = Image.open(io.BytesIO(visual["bytes"])).convert("RGB")
            elif "path" in visual and visual["path"]:
                img = Image.open(visual["path"]).convert("RGB")
            else:
                raise ValueError(f"Cannot parse image from dict keys={list(visual.keys())}")
        else:
            img = Image.fromarray(visual).convert("RGB")
        return self.transform(img).unsqueeze(0).to(device=self._device, dtype=self.dtype)

    def _expand_image_tokens(self, ids, num_expansion=NUM_IMAGE_TOKENS):
        result = []
        for tid in ids:
            if tid == IMAGE_TOKEN_ID: result.extend([IMAGE_TOKEN_ID] * num_expansion)
            else: result.append(tid)
        return result

    def _inject_image_features(self, input_ids, image_features):
        embed_tokens = self.llm.get_input_embeddings()
        inputs_embeds = embed_tokens(input_ids)
        B, S, H = inputs_embeds.shape
        # Ensure image_features match dtype
        image_features = image_features.to(inputs_embeds.dtype)
        for b in range(B):
            img_mask = (input_ids[b] == IMAGE_TOKEN_ID)
            n_img = img_mask.sum().item()
            if n_img == 0: continue
            n_feat = image_features.shape[1]
            if n_img == n_feat: inputs_embeds[b, img_mask] = image_features[b]
            elif n_img > n_feat: inputs_embeds[b, img_mask][:n_feat] = image_features[b]
            else: inputs_embeds[b, img_mask] = image_features[b, :n_img]
        if not hasattr(self, '_debug_inject'):
            self._debug_inject = True
            print(f"  [inject] inputs_embeds dtype={inputs_embeds.dtype}, img_feat dtype={image_features.dtype}")
            print(f"  [inject] inputs_embeds shape={inputs_embeds.shape}, img_mask sum={n_img}")
            print(f"  [inject] img_feat stats: min={image_features.min():.3f}, max={image_features.max():.3f}, mean={image_features.mean():.3f}")
            # Compare text embedding stats (non-image positions)
            text_mask = ~(input_ids[0] == IMAGE_TOKEN_ID)
            print(f"  [inject] text_embed stats: min={inputs_embeds[0][text_mask].min():.3f}, max={inputs_embeds[0][text_mask].max():.3f}, mean={inputs_embeds[0][text_mask].mean():.3f}")
        return inputs_embeds

    def _get_visuals(self, req):
        """Extract visuals using task_dict (set by evaluator at lm.task_dict[task]=dataset)."""
        args = req.args
        # Debug: print actual arg types/values for first call
        if not hasattr(self, '_debug_printed'):
            self._debug_printed = True
            for j, a in enumerate(args):
                print(f"  args[{j}] = {type(a).__name__}: {repr(a)[:200]}")
        # In lmms-eval 0.7.1:
        #   ConfigurableTask:           args = (ctx, gen_kwargs, doc_to_visual, doc_id, task, split)
        #   ConfigurableMessagesTask:   args = (ctx, doc_to_messages, gen_kwargs, doc_id, task, split)
        # Detect by type: callable at [1] → messages task; dict at [1] → visual task
        raw_1 = args[1] if len(args) > 1 else {}
        raw_2 = args[2] if len(args) > 2 else None
        if callable(raw_1) and isinstance(raw_2, dict):
            # ConfigurableMessagesTask: extract images from chat messages
            doc_to_messages, gen_kwargs = raw_1, raw_2
            doc_id = args[3] if len(args) > 3 else 0
            task = args[4] if len(args) > 4 else None
            split = args[5] if len(args) > 5 else None
            if task is None:
                return []
            try:
                doc = self.task_dict[task][split][doc_id]
                messages = doc_to_messages(doc) if callable(doc_to_messages) else doc_to_messages
                if not hasattr(self, '_debug_msg'):
                    self._debug_msg = True
                    print(f"  messages type={type(messages).__name__}, len={len(messages) if isinstance(messages, list) else 'N/A'}")
                    for mi, msg in enumerate(messages if isinstance(messages, list) else [messages]):
                        print(f"  msg[{mi}] keys={list(msg.keys()) if isinstance(msg, dict) else type(msg).__name__}")
                        if isinstance(msg, dict):
                            c = msg.get("content")
                            print(f"    content type={type(c).__name__}, val={repr(c)[:300]}")
                visuals = []
                for msg in (messages if isinstance(messages, list) else [messages]):
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content", [])
                    if isinstance(content, str):
                        continue
                    for item in (content if isinstance(content, list) else [content]):
                        if isinstance(item, dict):
                            # {'type': 'image', 'image': PIL.Image} or {'type': 'image', 'url': PIL.Image}
                            if item.get("type") == "image":
                                img = item.get("image") or item.get("url")
                                if img is not None:
                                    visuals.append(img)
                        elif isinstance(item, Image.Image):
                            visuals.append(item)
                return visuals
            except Exception as e:
                print(f"[BaizeLLaVA] WARNING: visual extraction from messages failed (task={task}, doc_id={doc_id}): {e}")
                return []
        else:
            # ConfigurableTask: args[2] is doc_to_visual
            gen_kwargs, doc_to_visual = raw_1, raw_2
            doc_id = args[3] if len(args) > 3 else 0
            task = args[4] if len(args) > 4 else None
            split = args[5] if len(args) > 5 else None
            if doc_to_visual is None or task is None or not callable(doc_to_visual):
                return []
            try:
                doc = self.task_dict[task][split][doc_id]
                visuals = doc_to_visual(doc)
                return visuals
            except Exception as e:
                print(f"[BaizeLLaVA] WARNING: visual extraction failed (task={task}, doc_id={doc_id}): {e}")
                return []

    def generate_until(self, requests):
        """Batched generation: processes self._batch_size requests in a single
        generate() call for high GPU utilization.  Uses left-padding so all
        sequences in the batch share the same prefill length.
        """
        n_reqs = len(requests)
        res = [None] * n_reqs
        bs = max(1, self._batch_size)
        pad_id = self.tokenizer.pad_token_id
        im_end_id = self.tokenizer.convert_tokens_to_ids("<|im_end|>")
        if im_end_id is None or im_end_id == self.tokenizer.unk_token_id:
            im_end_id = 151645

        for batch_start in range(0, n_reqs, bs):
            batch_idx = list(range(batch_start, min(batch_start + bs, n_reqs)))
            B = len(batch_idx)

            # ---- Phase 1: per-request setup (CPU, no GPU work) ----
            batch_ids = []          # list[list[int]]  expanded token IDs
            batch_img_feats = []     # list[Tensor[N,196,D] or None]
            batch_gen_kw = []

            for idx in batch_idx:
                req = requests[idx]
                args = req.args
                context = args[0] if len(args) > 0 else ""
                raw_gk = args[1] if len(args) > 1 else {}
                raw_dv = args[2] if len(args) > 2 else None
                if callable(raw_gk) and isinstance(raw_dv, dict):
                    gen_kwargs = raw_dv
                else:
                    gen_kwargs = raw_gk if isinstance(raw_gk, dict) else {}
                visuals = self._get_visuals(req)
                has_image = len(visuals) > 0
                img_feat = self._process_images(visuals)
                clean_ctx = context.replace("<image>", "").strip()
                prompt_text = ("<|image_pad|>\n" + clean_ctx) if has_image else clean_ctx
                prompt = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
                ids = self.tokenizer(prompt, add_special_tokens=False)["input_ids"]
                expanded = self._expand_image_tokens(ids)
                batch_ids.append(expanded)
                batch_img_feats.append(img_feat)
                batch_gen_kw.append(gen_kwargs)

            if batch_start == 0:
                print(f"[BaizeLLaVA] Batched generate: B={B}, seq_lens={sorted(set(len(x) for x in batch_ids))[:5]}")

            # ---- Phase 2: left-pad to max length ----
            max_len = max(len(ids) for ids in batch_ids)
            padded = []
            masks = []
            for ids in batch_ids:
                pl = max_len - len(ids)
                padded.append([pad_id] * pl + ids)
                masks.append([0] * pl + [1] * len(ids))

            input_ids_t = torch.tensor(padded, dtype=torch.long, device=self._device)
            attn_t = torch.tensor(masks, dtype=torch.long, device=self._device)

            # ---- Phase 3: batched image features → inputs_embeds ----
            has_any_img = any(f is not None for f in batch_img_feats)
            if has_any_img:
                ref = next(f for f in batch_img_feats if f is not None)
                D = ref.shape[-1]
                batched_feat = torch.zeros(B, NUM_IMAGE_TOKENS, D,
                                           device=self._device, dtype=self.dtype)
                for b, f in enumerate(batch_img_feats):
                    if f is not None:
                        batched_feat[b] = f[0]          # first image per sample
                inputs_embeds = self._inject_image_features(input_ids_t, batched_feat)
            else:
                embed_tokens = self.llm.get_input_embeddings()
                inputs_embeds = embed_tokens(input_ids_t)

            # ---- Phase 4: batched generate() ----
            max_new = max(gk.get("max_new_tokens", self._max_new_tokens)
                          for gk in batch_gen_kw)
            with torch.no_grad():
                output = self.llm.generate(
                    inputs_embeds=inputs_embeds,
                    attention_mask=attn_t,
                    max_new_tokens=max_new,
                    do_sample=False, temperature=1.0, top_p=1.0,
                    num_beams=1,
                    pad_token_id=pad_id,
                    eos_token_id=im_end_id,
                )

            # ---- Phase 5: decode + post-process per sample ----
            in_len = inputs_embeds.shape[1]
            for b, idx in enumerate(batch_idx):
                if output.shape[1] > in_len:
                    new_tokens = output[b][in_len:]
                else:
                    new_tokens = output[b]
                text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                if batch_start == 0 and b < 2:
                    print(f"[BaizeLLaVA] sample {b}: gen_text='{text[:80]}'")
                until = batch_gen_kw[b].get("until", None)
                if until:
                    if isinstance(until, str): until = [until]
                    for stop in until:
                        if stop in text: text = text[:text.index(stop)]
                res[idx] = text

        return res

    def generate_until_multi_round(self, requests):
        return self.generate_until(requests)

    def loglikelihood(self, requests):
        res = []
        for req in requests:
            args = req.args
            context = args[0] if len(args) > 0 else ""
            raw_cont = args[1] if len(args) > 1 else ""
            raw_dv = args[2] if len(args) > 2 else None
            # For loglikelihood: (ctx, doc_to_target, doc_to_visual, doc_id, task, split)
            # doc_to_target can be a string (key) or a function
            doc_id = args[3] if len(args) > 3 else 0
            task = args[4] if len(args) > 4 else None
            split = args[5] if len(args) > 5 else None
            if callable(raw_cont) and task is not None:
                try:
                    doc = self.task_dict[task][split][doc_id]
                    continuation = raw_cont(doc)
                except Exception:
                    continuation = ""
            elif isinstance(raw_cont, str):
                continuation = raw_cont
            else:
                continuation = ""
            visuals = self._get_visuals(req)
            has_image = len(visuals) > 0
            image_features = self._process_images(visuals)
            clean_ctx = context.replace("<image>", "").strip()
            ctx_text = ("<|image_pad|>\n" + clean_ctx) if has_image else clean_ctx
            ctx_prompt = f"<|im_start|>user\n{ctx_text}<|im_end|>\n<|im_start|>assistant\n"
            full_prompt = ctx_prompt + continuation
            ctx_ids = self.tokenizer(ctx_prompt, add_special_tokens=False)["input_ids"]
            full_ids = self.tokenizer(full_prompt, add_special_tokens=False)["input_ids"]
            ctx_exp = self._expand_image_tokens(ctx_ids)
            full_exp = self._expand_image_tokens(full_ids)
            ctx_len = len(ctx_exp)
            full_ids_t = torch.tensor([full_exp], dtype=torch.long, device=self._device)
            labels = full_ids_t.clone()
            labels[0, :ctx_len] = -100
            with torch.no_grad():
                if image_features is not None:
                    inputs_embeds = self._inject_image_features(full_ids_t, image_features)
                    attn = torch.ones_like(full_ids_t)
                    outputs = self.llm(inputs_embeds=inputs_embeds, attention_mask=attn, labels=labels)
                else:
                    outputs = self.llm(input_ids=full_ids_t, labels=labels)
            n_cont = (labels[0] != -100).sum().item()
            ll = -outputs.loss.item() * max(1, n_cont)
            logits = outputs.logits[0]
            pred = logits[ctx_len - 1:-1].argmax(dim=-1)
            cont_tokens = full_ids_t[0, ctx_len:]
            is_greedy = torch.equal(pred, cont_tokens)
            res.append((ll, is_greedy.item()))
        return res

    def flatten(self, input):
        new_list = []
        for i in input:
            for j in i: new_list.append(j)
        return new_list


    def _process_images(self, visuals):
        if not visuals: return None
        pixel_values = []
        for v in visuals:
            try: pixel_values.append(self._prepare_image(v))
            except Exception as e:
                print(f"[BaizeLLaVA] WARNING: visual failed: {e}")
                continue
        if not pixel_values: return None
        pixel_values = torch.cat(pixel_values, dim=0)
        with torch.no_grad():
            vis_feat = self.vision(pixel_values)
            return self.projector(vis_feat)
