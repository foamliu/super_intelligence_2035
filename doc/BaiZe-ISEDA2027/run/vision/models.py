"""BaiZe Stage(iii) vision encoders (from-scratch). See get_vision_tower()."""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from mamba_ssm import Mamba as _MambaSSM
    HAS_MAMBA = True
except Exception:
    HAS_MAMBA = False

EMBED_DIM = 512


class LayerNorm(nn.LayerNorm):
    def forward(self, x):
        return F.layer_norm(x, self.normalized_shape, self.weight, self.bias, self.eps)


class SwiGLU(nn.Module):
    def __init__(self, dim: int, hidden: int):
        super().__init__()
        self.gate = nn.Linear(dim, hidden, bias=False)
        self.up = nn.Linear(dim, hidden, bias=False)
        self.down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        return self.down(F.silu(self.gate(x)) * self.up(x))


class Attention(nn.Module):
    def __init__(self, dim: int, heads: int, qkv_bias: bool = False):
        super().__init__()
        assert dim % heads == 0
        self.heads = heads
        self.head_dim = dim // heads
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim, bias=False)

    def forward(self, x, attn_mask=None):
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask)
        out = out.transpose(1, 2).reshape(B, N, C)
        return self.proj(out)


class AttentionBlock(nn.Module):
    def __init__(self, dim: int, heads: int, mlp_dim: int):
        super().__init__()
        self.norm1 = LayerNorm(dim)
        self.attn = Attention(dim, heads)
        self.norm2 = LayerNorm(dim)
        self.mlp = SwiGLU(dim, mlp_dim)

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x


class MambaBidirBlock(nn.Module):
    def __init__(self, dim: int, d_state: int = 16, d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.norm = LayerNorm(dim)
        assert HAS_MAMBA, "mamba_ssm not available"
        self.mamba_fwd = _MambaSSM(d_model=dim, d_state=d_state, d_conv=d_conv, expand=expand)
        self.mamba_bwd = _MambaSSM(d_model=dim, d_state=d_state, d_conv=d_conv, expand=expand)

    def forward(self, x):
        x = self.norm(x)
        fwd = self.mamba_fwd(x)
        bwd = self.mamba_bwd(torch.flip(x, dims=[1]))
        bwd = torch.flip(bwd, dims=[1])
        return x + 0.5 * (fwd + bwd)


class MoEBlock(nn.Module):
    """Sparse MoE FFN on top of standard attention. Each expert is a dense
    SwiGLU FFN of width `expert_ff`; top-k experts are routed per token and
    their outputs weight-summed. Expert-loop implementation keeps memory low
    (shared per-expert weights, no per-token gather).
    """
    def __init__(self, dim: int, heads: int, expert_ff: int, n_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.norm1 = LayerNorm(dim)
        self.attn = Attention(dim, heads)
        self.norm2 = LayerNorm(dim)
        self.n_experts = n_experts
        self.top_k = top_k
        self.router = nn.Linear(dim, n_experts, bias=False)
        self.gate = nn.Parameter(torch.empty(n_experts, dim, expert_ff))
        self.up = nn.Parameter(torch.empty(n_experts, dim, expert_ff))
        self.down = nn.Parameter(torch.empty(n_experts, expert_ff, dim))
        for p in (self.gate, self.up, self.down):
            nn.init.kaiming_uniform_(p, a=math.sqrt(5))

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        h = self.norm2(x)
        B, N, C = h.shape
        h_flat = h.reshape(B * N, C)
        S = h_flat.shape[0]
        logits = self.router(h_flat)                       # (S, E)
        topk_vals, topk_idx = logits.topk(self.top_k, dim=-1)  # (S, top_k)
        probs = F.softmax(topk_vals, dim=-1)               # (S, top_k)

        # Flatten the (token, slot) dispatch and sort by expert so each expert's
        # tokens form a contiguous run (fewer scattered gathers than per-expert
        # nonzero scans; single argsort per block).
        flat_expert = topk_idx.reshape(-1)                 # (S*K,)
        flat_token = torch.arange(S, device=h.device, dtype=torch.long).repeat_interleave(self.top_k)
        flat_weight = probs.reshape(-1)                    # (S*K,)
        order = torch.argsort(flat_expert, stable=True)
        s_expert = flat_expert[order]
        s_token = flat_token[order]
        s_weight = flat_weight[order]

        counts = torch.bincount(s_expert, minlength=self.n_experts)
        offsets = torch.cumsum(counts, dim=0).tolist()      # one sync per block

        out = torch.zeros_like(h_flat)
        prev = 0
        for e in range(self.n_experts):
            end = offsets[e]
            if end == prev:
                continue
            t = s_token[prev:end]                          # (T_e,)
            w = s_weight[prev:end]                         # (T_e,)
            h_e = h_flat[t]                                # (T_e, C)
            a = F.silu(h_e @ self.gate[e]) * (h_e @ self.up[e])   # (T_e, ff)
            o = a @ self.down[e]                           # (T_e, C)
            out.index_add_(0, t, o * w.unsqueeze(1))
            prev = end
        x = x + out.reshape(B, N, C)
        return x


class PatchEmbed(nn.Module):
    def __init__(self, image_size: int, patch_size: int, width: int):
        super().__init__()
        self.grid = image_size // patch_size
        self.conv = nn.Conv2d(3, width, patch_size, patch_size, bias=False)
        self.pos = nn.Parameter(torch.randn(self.grid * self.grid, width) * (width ** -0.5))

    def forward(self, x):
        x = self.conv(x).flatten(2).transpose(1, 2)
        return x + self.pos


class ReadoutHead(nn.Module):
    def __init__(self, width: int, embed_dim: int = EMBED_DIM):
        super().__init__()
        self.norm = LayerNorm(width)
        self.proj = nn.Linear(width, embed_dim, bias=False)

    def forward(self, x):
        x = x.mean(dim=1)
        return self.proj(self.norm(x))
# --------------------------------------------------------------------------- #
# Architecture 1: OpenVision2 (pure attention ViT)
# --------------------------------------------------------------------------- #
class OpenVision2(nn.Module):
    def __init__(self, image_size: int = 224, patch_size: int = 16,
                 width: int = 1024, depth: int = 30, heads: int = 16, mlp_dim: int = 4096):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.embed = PatchEmbed(image_size, patch_size, width)
        self.blocks = nn.ModuleList([AttentionBlock(width, heads, mlp_dim) for _ in range(depth)])
        self.norm = LayerNorm(width)
        self.head = ReadoutHead(width)

    def forward(self, x, return_patch: bool = False):
        x = self.embed(x)
        for b in self.blocks:
            x = b(x)
        x = self.norm(x)
        pooled = self.head(x)
        return (pooled, x) if return_patch else pooled


# --------------------------------------------------------------------------- #
# Architecture 2: MambaEye (pure visual SSM, Vim-style bidirectional)
# --------------------------------------------------------------------------- #
class MambaEye(nn.Module):
    def __init__(self, image_size: int = 224, patch_size: int = 16,
                 width: int = 1024, depth: int = 40, d_state: int = 16,
                 d_conv: int = 4, expand: int = 2):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.embed = PatchEmbed(image_size, patch_size, width)
        self.blocks = nn.ModuleList(
            [MambaBidirBlock(width, d_state, d_conv, expand) for _ in range(depth)])
        self.norm = LayerNorm(width)
        self.head = ReadoutHead(width)

    def forward(self, x):
        x = self.embed(x)
        for b in self.blocks:
            x = b(x)
        return self.head(self.norm(x))


# --------------------------------------------------------------------------- #
# Architecture 3: MoEViE (sparse MoE ViT)
# --------------------------------------------------------------------------- #
class MoEViE(nn.Module):
    def __init__(self, image_size: int = 224, patch_size: int = 16,
                 width: int = 1024, depth: int = 30, heads: int = 16,
                 expert_ff: int = 512, n_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.embed = PatchEmbed(image_size, patch_size, width)
        self.blocks = nn.ModuleList(
            [MoEBlock(width, heads, expert_ff, n_experts, top_k) for _ in range(depth)])
        self.norm = LayerNorm(width)
        self.head = ReadoutHead(width)

    def forward(self, x):
        x = self.embed(x)
        for b in self.blocks:
            x = b(x)
        return self.head(self.norm(x))


# --------------------------------------------------------------------------- #
# Architecture 4: DeepEncoderV2 (Attention + SSM hybrid, ordered pattern)
# --------------------------------------------------------------------------- #
class DeepEncoderV2(nn.Module):
    """Nemotron-H style ordered hybrid. `pattern` like 'AAMM' (A=attention, M=Mamba),
    repeated cyclically to `n_blocks` total blocks."""
    def __init__(self, image_size: int = 224, patch_size: int = 16,
                 width: int = 1024, heads: int = 16, mlp_dim: int = 4096,
                 d_state: int = 16, d_conv: int = 4, expand: int = 2,
                 pattern: str = 'AAMM', n_blocks: int = 34):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.embed = PatchEmbed(image_size, patch_size, width)
        blocks = []
        i = 0
        while len(blocks) < n_blocks:
            ch = pattern[i % len(pattern)]
            if ch == 'A':
                blocks.append(AttentionBlock(width, heads, mlp_dim))
            elif ch == 'M':
                blocks.append(MambaBidirBlock(width, d_state, d_conv, expand))
            else:
                raise ValueError(f"bad pattern char {ch!r}")
            i += 1
        self.blocks = nn.ModuleList(blocks)
        self.norm = LayerNorm(width)
        self.head = ReadoutHead(width)

    def forward(self, x):
        x = self.embed(x)
        for b in self.blocks:
            x = b(x)
        return self.head(self.norm(x))


# --------------------------------------------------------------------------- #
# Architecture 5: AIMv2 (Apple, arXiv:2411.14402) — vision trunk = pre-norm ViT
# --------------------------------------------------------------------------- #
class VitGeluBlock(nn.Module):
    """Standard pre-norm ViT block with 4x GELU MLP (AIMv2 trunk uses the
    standard ViT encoder, unlike OpenVision2's SwiGLU variant)."""

    def __init__(self, dim: int, heads: int, mlp_dim: int):
        super().__init__()
        self.norm1 = LayerNorm(dim)
        self.attn = Attention(dim, heads)
        self.norm2 = LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_dim), nn.GELU(), nn.Linear(mlp_dim, dim))

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x


class AIMv2(nn.Module):
    """AIMv2's *vision encoder* is a standard pre-norm ViT (the paper pre-trains it
    autoregressively on patch+text tokens, but the trunk itself is plain ViT).
    Scaled from AIMv2-L (w=1024, d=24, ~304M) to ~505M by deepening 24 -> 40 with
    the official GELU 4x MLP (NOT SwiGLU), keeping width/heads at AIMv2-L values."""

    def __init__(self, image_size: int = 224, patch_size: int = 16,
                 width: int = 1024, depth: int = 40, heads: int = 16, mlp_dim: int = 4096):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.embed = PatchEmbed(image_size, patch_size, width)
        self.blocks = nn.ModuleList([VitGeluBlock(width, heads, mlp_dim) for _ in range(depth)])
        self.norm = LayerNorm(width)
        self.head = ReadoutHead(width)

    def forward(self, x):
        x = self.embed(x)
        for b in self.blocks:
            x = b(x)
        return self.head(self.norm(x))


# --------------------------------------------------------------------------- #
# Architecture 6: FastViTHD (Apple FastVLM vision tower) — conv stem + attention
# --------------------------------------------------------------------------- #
class ConvFFN(nn.Module):
    """FastViT 'RepMixer' conv FFN (2D): depthwise 3x3 + 1x1 expand + GELU + 1x1 shrink."""

    def __init__(self, ch: int, expand: int = 4):
        super().__init__()
        self.dw = nn.Conv2d(ch, ch, 3, 1, 1, groups=ch, bias=False)
        self.pw1 = nn.Conv2d(ch, ch * expand, 1, bias=False)
        self.pw2 = nn.Conv2d(ch * expand, ch, 1, bias=False)
        self.act = nn.GELU()

    def forward(self, x):
        return self.pw2(self.act(self.pw1(self.dw(x))))


class RepMixer(nn.Module):
    """Conv-only mixing block (early FastViT stages; no attention)."""

    def __init__(self, ch: int, expand: int = 4):
        super().__init__()
        self.norm = nn.GroupNorm(1, ch)
        self.ffn = ConvFFN(ch, expand)

    def forward(self, x):
        return x + self.ffn(self.norm(x))


class HybridAttnBlock(nn.Module):
    """Late-stage FastViT block: token-mixer attention (2D->seq->2D) + conv FFN."""

    def __init__(self, ch: int, heads: int, expand: int = 4):
        super().__init__()
        self.norm1 = nn.GroupNorm(1, ch)
        self.attn = Attention(ch, heads)
        self.norm2 = nn.GroupNorm(1, ch)
        self.ffn = ConvFFN(ch, expand)

    def forward(self, x):
        B, C, H, W = x.shape
        r = self.norm1(x).reshape(B, C, H * W).transpose(1, 2)  # (B, N, C)
        r = self.attn(r).transpose(1, 2).reshape(B, C, H, W)
        x = x + r
        return x + self.ffn(self.norm2(x))


class FastViTHD(nn.Module):
    """Conv stem + hierarchical conv/attention hybrid, faithful to FastViT-HD's macro
    (conv stem / depthwise RepMixer conv-FFN / token-mixer attention), scaled to ~500M.
    224 -> 28x28 conv stem (8x down) -> 4 RepMixer conv blocks -> downsample 28->14 ->
    37 hybrid attention blocks at 14x14 (ViT-token cost) -> global pool -> ReadoutHead."""

    def __init__(self, image_size: int = 224, patch_size: int = 16, width: int = 1024,
                 conv_depths: int = 4, attn_depths: int = 37, heads: int = 16, expand: int = 4):
        super().__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.stem = nn.Sequential(
            nn.Conv2d(3, width // 2, 4, 4, bias=False),        # 224 -> 56
            nn.GroupNorm(1, width // 2), nn.GELU(),
            nn.Conv2d(width // 2, width, 2, 2, bias=False),    # 56 -> 28
        )
        self.pos = nn.Parameter(torch.zeros(1, width, image_size // 8, image_size // 8))
        self.conv_blocks = nn.ModuleList([RepMixer(width, expand) for _ in range(conv_depths)])
        # FastViT is hierarchical: late attention stages run at lower resolution.
        self.down = nn.Sequential(
            nn.Conv2d(width, width, 2, 2, bias=False),         # 28 -> 14
            nn.GroupNorm(1, width), nn.GELU(),
        )
        self.attn_pos = nn.Parameter(torch.zeros(1, width, image_size // 16, image_size // 16))
        self.attn_blocks = nn.ModuleList([HybridAttnBlock(width, heads, expand)
                                          for _ in range(attn_depths)])
        self.head = ReadoutHead(width)  # ReadoutHead applies the final LayerNorm over width

    def forward(self, x):
        x = self.stem(x)
        x = x + self.pos
        for b in self.conv_blocks:
            x = b(x)
        x = self.down(x) + self.attn_pos
        for b in self.attn_blocks:
            x = b(x)
        x = x.mean(dim=[2, 3]).unsqueeze(1)  # (B,1,width) -> ReadoutHead mean(dim=1)
        return self.head(x)


class CrossAttention(nn.Module):
    """Multi-head cross attention: queries from `x` attend to keys/values from `ctx`."""

    def __init__(self, dim: int, heads: int, qkv_bias: bool = False):
        super().__init__()
        assert dim % heads == 0
        self.heads = heads
        self.head_dim = dim // heads
        self.q = nn.Linear(dim, dim, bias=qkv_bias)
        self.kv = nn.Linear(dim, dim * 2, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim, bias=False)

    def forward(self, x, ctx):
        B, N, C = x.shape
        q = self.q(x).reshape(B, N, self.heads, self.head_dim).transpose(1, 2)
        kv = self.kv(ctx).reshape(B, ctx.shape[1], 2, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        k, v = kv[0], kv[1]
        out = F.scaled_dot_product_attention(q, k, v)
        out = out.transpose(1, 2).reshape(B, N, C)
        return self.proj(out)


class CoCaDecoderBlock(nn.Module):
    """Causal self-attn -> cross-attn to vision patches -> MLP (CoCa-style caption decoder block)."""

    def __init__(self, dim: int, heads: int, mlp_dim: int):
        super().__init__()
        self.norm1 = LayerNorm(dim)
        self.self_attn = Attention(dim, heads)
        self.norm2 = LayerNorm(dim)
        self.cross_attn = CrossAttention(dim, heads)
        self.norm3 = LayerNorm(dim)
        self.mlp = SwiGLU(dim, mlp_dim)

    def forward(self, x, ctx, causal):
        x = x + self.self_attn(self.norm1(x), attn_mask=causal)
        x = x + self.cross_attn(self.norm2(x), ctx)
        x = x + self.mlp(self.norm3(x))
        return x


class CoCaDecoder(nn.Module):
    """Self-written CoCa-style caption decoder (contrastive + autoregressive caption).

    A causal transformer decoder conditions on vision *patch* features via cross-attention
    and predicts caption tokens left-to-right, giving per-token dense supervision. The input
    token embedding is a frozen CLIP token embedding (shared with the frozen text tower, kept
    out of the optimizer); only pos_embed / vision_proj / decoder blocks / output head train.
    """

    def __init__(self, dim: int = 768, heads: int = 12, depth: int = 4, mlp_dim: int = 2048,
                 vocab_size: int = 49408, max_len: int = 77, vision_width: int = 512,
                 token_embed: nn.Module = None):
        super().__init__()
        self.dim = dim
        self.max_len = max_len
        if token_embed is None:
            token_embed = nn.Embedding(vocab_size, dim)
            nn.init.normal_(token_embed.weight, std=0.02)
        self.token_embed = token_embed
        self.pos_embed = nn.Parameter(torch.randn(max_len, dim) * (dim ** -0.5))
        self.vision_proj = nn.Linear(vision_width, dim, bias=False)
        self.blocks = nn.ModuleList([CoCaDecoderBlock(dim, heads, mlp_dim) for _ in range(depth)])
        self.norm = LayerNorm(dim)
        self.head = nn.Linear(dim, vocab_size, bias=False)
        nn.init.normal_(self.head.weight, std=0.02)

    def forward(self, ids, ctx_patches):
        B, T = ids.shape
        ctx = self.vision_proj(ctx_patches)
        x = self.token_embed(ids) + self.pos_embed[:T]
        causal = torch.tril(torch.ones(T, T, dtype=torch.bool, device=ids.device))
        for b in self.blocks:
            x = b(x, ctx, causal)
        return self.head(self.norm(x))


def get_vision_tower(name: str, width: int = None, depth: int = None,
                     heads: int = None, mlp_dim: int = None) -> nn.Module:
    """Construct a vision tower. `width/depth/heads/mlp_dim` are scale overrides
    currently honoured by OpenVision2 (R9 shrink-tower pilot: w512/w768/w1024 ->
    ~126M / ~284M / 505M). Other towers ignore them and keep their default config."""
    towers = {
        'openvision2': OpenVision2,
        'mambaeye': MambaEye,
        'moevie': MoEViE,
        'deepencoder_v2': DeepEncoderV2,
        'aimv2': AIMv2,
        'fastvithd': FastViTHD,
    }
    if name not in towers:
        raise ValueError(f"Unknown tower '{name}'. Options: {list(towers)}")
    if name == 'openvision2':
        w = width if width is not None else 1024
        d = depth if depth is not None else 30
        h = heads if heads is not None else max(1, w // 64)
        m = mlp_dim if mlp_dim is not None else (4 * w)
        return OpenVision2(width=w, depth=d, heads=h, mlp_dim=m)
    return towers[name]()


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def active_param_count(model: nn.Module) -> int:
    """Approx active params for a single forward (MoE top-k expert subset)."""
    moe_ids = set()
    n = 0
    for m in model.modules():
        if isinstance(m, MoEBlock):
            for p in m.parameters():
                moe_ids.add(id(p))
            # attention + router + top_k fraction of experts
            n += sum(p.numel() for p in m.attn.parameters())
            n += m.router.weight.numel()
            nl = m.gate.numel() + m.up.numel() + m.down.numel()
            n += int(m.top_k / m.n_experts * nl)
    for p in model.parameters():
        if id(p) not in moe_ids:
            n += p.numel()
    return n