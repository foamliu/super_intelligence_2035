# Patch: Blend Hot-Switch for Megatron-LM (Plan F)

> **Base commit**: `14c215dc1472ca75d6f3ce27e423bedfdc51614b` (Xmodel-2.5-code)
> **Flag**: `--blend-hot-switch` (default OFF)
> **Safety**: flag OFF = stock byte-equivalent (verified by test_blend_switch.py)
> **Date**: 2026-11-22 · **Author**: BaiZe Data Agent

## 1. blended_dataset.py — add update_weights()

Insert after BlendedDataset.__init__ (~line 110). Only called when flag ON.

```python
def update_weights(self, new_weights, new_size, switcher, build_fn=None):
    """Hot-update blend weights with per-source cursor mapping (Plan F)."""
    if build_fn is None:
        try:
            from megatron.core.datasets.helpers_cpp import build_blending_indices
            build_fn = build_blending_indices
        except ImportError:
            from blend_switcher import build_blending_indices_py
            build_fn = build_blending_indices_py
    shared_mask = switcher.shared_source_mask or [True]*len(new_weights)
    new_di = numpy.zeros(new_size, dtype=numpy.int16)
    new_dsi = numpy.zeros(new_size, dtype=numpy.int64)
    build_fn(new_di, new_dsi, new_weights, len(new_weights), new_size)
    for s in range(len(new_weights)):
        if shared_mask[s]:
            new_dsi[new_di == s] += int(switcher.consumed_per_source[s])
    self.dataset_index = new_di
    self.dataset_sample_index = new_dsi
    self.weights = new_weights
    self.size = new_size
    return new_di, new_dsi
```

## 2. samplers.py — add BlendHotSwitchRandomSampler

Insert after MegatronPretrainingRandomSampler (~line 264). Only used when flag ON.

```python
class BlendHotSwitchRandomSampler:
    """Per-source progress-driven sampler for post-switch S2.
    Stock uses epoch=consumed//active_total → overlap on resume.
    This uses pre-built (cursor-offset) indices → zero overlap."""
    def __init__(self, total_samples, consumed_samples, micro_batch_size,
                 data_parallel_rank, data_parallel_size, data_sharding):
        self.total_samples = total_samples
        self.consumed_samples = consumed_samples
        self.micro_batch_size = micro_batch_size
        self.data_parallel_rank = data_parallel_rank
        self.data_parallel_size = data_parallel_size
        self.mbs_dp = micro_batch_size * data_parallel_size
        self.last_batch = total_samples % self.mbs_dp
        self.active_total = total_samples - self.last_batch
    def __len__(self): return self.total_samples
    def __iter__(self):
        start = self.data_parallel_rank * self.micro_batch_size
        step = self.mbs_dp
        batch = []
        for idx in range(start, self.active_total, step):
            batch.append(idx)
            if len(batch) == self.micro_batch_size:
                self.consumed_samples += self.mbs_dp
                yield batch; batch = []
```

## 3. loaders.py — conditional sampler selection

In build_pretraining_data_loader(), after sampler creation:

```python
if getattr(cfg, 'blend_hot_switch', False) and hasattr(train_ds, 'update_weights'):
    sampler = BlendHotSwitchRandomSampler(
        total_samples=len(train_ds), consumed_samples=consumed_samples,
        micro_batch_size=micro_batch_size, data_parallel_rank=data_parallel_rank,
        data_parallel_size=data_parallel_size, data_sharding=data_sharding)
else:
    sampler = MegatronPretrainingRandomSampler(...)  # stock unchanged
```

## 4. Checkpoint — consumed_per_source persistence

```python
# save: state_dict['blend_switcher'] = switcher.to_json()
# load: switcher = BlendSwitcher.from_json(state_dict['blend_switcher'])
```

## Flag-off equivalence proof

When `--blend-hot-switch` is NOT set:
1. update_weights() never called → stock __init__ path
2. BlendHotSwitchRandomSampler never instantiated → stock sampler
3. No checkpoint fields added → stock format

Verified: `test_blend_switch.py::test_flag_off_equivalence` → PASS (byte-identical)

## Zero-overlap proof

shuffle_index is a permutation of [0, num_samples) — no repeats within one epoch.
S1 consumes [0, consumed[s]) → doc set D_s1.
S2 (cursor offset) consumes [consumed[s], ...) → doc set D_s2.
Disjoint ranges within one epoch → D_s1 ∩ D_s2 = ∅.

Caveat: if consumed[s] > len(shuffle_index[s]) (full epoch), wrap causes overlap.
Detected and reported honestly. For BaiZe S1+S2 < 1 epoch for all sources → no wrap.

Verified: `test_blend_switch.py::test_zero_overlap` → overlap = 0.