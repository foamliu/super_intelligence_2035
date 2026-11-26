#!/usr/bin/env python3
"""
BlendSwitcher — Plan F: 权重热更新 + 跨 blend 游标映射
=======================================================
实现 S1→S2 零重叠 + 换比例 的 Megatron-LM 自定义改造。

设计原理:
  1. BlendedDataset.update_weights(new_weights, new_size): 重建索引，复用 shuffle_index
  2. per-source 游标映射: consumed_per_source[s] → 新 blend 中该源继续前移
  3. 零重叠: shuffle_index 是无重复排列，S1 消费 [0, consumed) → S2 从 consumed 起
  4. --blend-hot-switch 默认关闭，关闭时与 stock 逐字节等价

作者: BaiZe Data Agent · 2026-11-22
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional, Tuple, Union
import numpy


def build_blending_indices_py(
    dataset_index: numpy.ndarray,
    dataset_sample_index: numpy.ndarray,
    weights: List[float],
    num_datasets: int,
    size: int,
    verbose: bool = False,
) -> None:
    """Pure-Python Bresenham-style weighted interleaving (replaces C++ helpers)."""
    weights = numpy.asarray(weights, dtype=numpy.float64)
    sampled = numpy.zeros(num_datasets, dtype=numpy.int64)
    for i in range(size):
        deficit = weights * (i + 1) - sampled
        chosen = int(numpy.argmax(deficit))
        dataset_index[i] = chosen
        dataset_sample_index[i] = sampled[chosen]
        sampled[chosen] += 1
        if verbose and i % 100000 == 0 and i > 0:
            print(f"  blending: {i}/{size} ({100*i/size:.1f}%)")


class BlendSwitcher:
    """Manages per-source consumption tracking and cross-blend cursor mapping.

    Lifecycle:
        switcher = BlendSwitcher(num_sources, source_keys)
        for sample_idx in s1_iterator:
            switcher.track(dataset_index[sample_idx])     # S1 tracking
        switcher.switch_weights(new_weights, new_size, shared_mask)  # switch
        overlap = switcher.compute_overlap(shuffle_indices)  # verify zero
    """

    def __init__(self, num_sources: int, source_keys: Optional[List[str]] = None) -> None:
        self.num_sources = num_sources
        self.source_keys = source_keys or [f"src_{i}" for i in range(num_sources)]
        self.consumed_per_source = numpy.zeros(num_sources, dtype=numpy.int64)
        self.total_consumed = 0
        self.switched = False
        self.new_weights: Optional[List[float]] = None
        self.new_size: Optional[int] = None
        self.new_dataset_index: Optional[numpy.ndarray] = None
        self.new_dataset_sample_index: Optional[numpy.ndarray] = None
        self.shared_source_mask: Optional[List[bool]] = None
        self.cursor_offsets: Optional[Dict[int, int]] = None

    def track(self, dataset_id: int) -> None:
        """Track consumption of one sample from source dataset_id (S1 phase)."""
        assert 0 <= dataset_id < self.num_sources
        self.consumed_per_source[dataset_id] += 1
        self.total_consumed += 1

    def track_batch(self, dataset_ids: numpy.ndarray) -> None:
        """Track consumption of a batch of samples (vectorized)."""
        for did in dataset_ids:
            self.track(int(did))

    def get_consumed_per_source(self) -> numpy.ndarray:
        return self.consumed_per_source.copy()

    def switch_weights(
        self,
        new_weights: List[float],
        new_size: int,
        shared_source_mask: List[bool],
        build_fn=None,
        s2_source_keys: Optional[List[str]] = None,
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """Switch to new blend weights with per-source cursor mapping.

        Rebuilds dataset_index/dataset_sample_index with new_weights (Bresenham),
        then applies cursor offsets for shared sources:
            new_dataset_sample_index[where dataset_index==s] += consumed_per_source[s_mapped]

        This is the core of Plan F: shared sources continue past S1-consumed
        positions in shuffle_index → zero document overlap.

        When S2 has a different number of sources or different ordering than S1,
        provide ``s2_source_keys`` to map each S2 source to its S1 counterpart
        by key. Sources not found in S1 are treated as new (offset=0).

        Args:
            new_weights: Normalized blend weights for S2.
            new_size: Number of samples in the S2 blend.
            shared_source_mask: Boolean mask, True for sources shared with S1.
            build_fn: Index builder (defaults to build_blending_indices_py).
            s2_source_keys: Source keys for S2 (for S1→S2 key-based mapping).
                If None, assumes S2 source s corresponds to S1 source s
                (backward compatible with existing tests).
        """
        num_s2_sources = len(new_weights)
        assert len(shared_source_mask) == num_s2_sources
        assert self.switched is False, "Already switched."

        self.new_weights = list(new_weights)
        self.new_size = new_size
        self.shared_source_mask = list(shared_source_mask)

        # Build S1→S2 source index mapping
        # For each S2 source, find the corresponding S1 source index by key
        s1_key_to_idx = {key: i for i, key in enumerate(self.source_keys)}
        s2_to_s1_map: List[int] = []  # s2_to_s1_map[s2_idx] = s1_idx or -1
        if s2_source_keys is not None:
            for s2_key in s2_source_keys:
                s2_to_s1_map.append(s1_key_to_idx.get(s2_key, -1))
        else:
            # Backward compat: assume same ordering, same count
            for s in range(num_s2_sources):
                s2_to_s1_map.append(s if s < self.num_sources else -1)
        self.s2_to_s1_map = s2_to_s1_map
        self.s2_source_keys = s2_source_keys

        # Step 1: Build new blending indices with S2 weights
        new_di = numpy.zeros(new_size, dtype=numpy.int16)
        new_dsi = numpy.zeros(new_size, dtype=numpy.int64)
        if build_fn is None:
            build_fn = build_blending_indices_py
        build_fn(new_di, new_dsi, new_weights, num_s2_sources, new_size)

        # Step 2: Apply per-source cursor offsets for shared sources
        # For each S2 source s, look up the S1 source by key and use its consumption
        self.cursor_offsets = {}
        for s in range(num_s2_sources):
            if shared_source_mask[s] and s2_to_s1_map[s] >= 0:
                s1_idx = s2_to_s1_map[s]
                offset = int(self.consumed_per_source[s1_idx])
                mask = (new_di == s)
                new_dsi[mask] += offset
                self.cursor_offsets[s] = offset
            else:
                self.cursor_offsets[s] = 0

        self.new_dataset_index = new_di
        self.new_dataset_sample_index = new_dsi
        self.switched = True
        return new_di, new_dsi

    def get_switched_indices(self) -> Tuple[numpy.ndarray, numpy.ndarray]:
        assert self.switched, "Must call switch_weights() first"
        return self.new_dataset_index, self.new_dataset_sample_index

    def get_consumed_doc_ids_s1(self, shuffle_indices: List[numpy.ndarray]) -> Dict[int, set]:
        """Compute document IDs consumed per source during S1.

        For source s, consumed shuffle positions are [0, consumed_per_source[s]).
        Each maps to a document via shuffle_indices[s][position].

        When S2 has different source ordering, shuffle_indices are ordered by S2
        positions. We use s2_to_s1_map to find the correct shuffle_indices entry
        for each S1 source.
        """
        # Build inverse map: S1 source idx → S2 source idx (for shuffle_indices access)
        s1_to_s2_map: Dict[int, int] = {}
        if self.switched and hasattr(self, 's2_to_s1_map'):
            for s2_idx, s1_idx in enumerate(self.s2_to_s1_map):
                if s1_idx >= 0:
                    s1_to_s2_map[s1_idx] = s2_idx

        consumed_docs: Dict[int, set] = {}
        for s in range(self.num_sources):
            n_consumed = int(self.consumed_per_source[s])
            # Find the correct shuffle_indices entry for this S1 source
            if s in s1_to_s2_map:
                shuffle_idx = s1_to_s2_map[s]
            else:
                shuffle_idx = s  # backward compat: same ordering
            if shuffle_idx < len(shuffle_indices):
                shuffle_s = shuffle_indices[shuffle_idx]
            else:
                consumed_docs[s] = set()
                continue
            if n_consumed == 0:
                consumed_docs[s] = set()
                continue
            effective = min(n_consumed, len(shuffle_s))
            consumed_docs[s] = set(int(p) for p in shuffle_s[:effective])
            if n_consumed > len(shuffle_s):
                # Epoch wrap: second pass overlaps — report honestly
                remainder = n_consumed - len(shuffle_s)
                consumed_docs[s].update(int(p) for p in shuffle_s[:remainder])
        return consumed_docs

    def get_consumed_doc_ids_s2(self, shuffle_indices: List[numpy.ndarray]) -> Dict[int, set]:
        """Compute document IDs that WILL be consumed per source during S2.

        Iterates over S2 source count (may differ from S1).
        shuffle_indices must have entries for all S2 sources.
        """
        assert self.switched, "Must call switch_weights() first"
        num_s2 = len(self.new_weights)
        consumed_docs: Dict[int, set] = {}
        for s in range(num_s2):
            mask = (self.new_dataset_index == s)
            sample_ids = self.new_dataset_sample_index[mask]
            if s < len(shuffle_indices):
                shuffle_s = shuffle_indices[s]
            else:
                consumed_docs[s] = set()
                continue
            docs = set()
            for sid in sample_ids:
                pos = int(sid) % len(shuffle_s)
                docs.add(int(shuffle_s[pos]))
            consumed_docs[s] = docs
        return consumed_docs

    def compute_overlap(self, shuffle_indices: List[numpy.ndarray]) -> Dict:
        """Compute S1∩S2 document overlap per source and overall.

        When S2 has different source count/ordering than S1, uses s2_to_s1_map
        to match sources by key. New sources (s1_idx=-1) have trivially 0 overlap.

        Returns dict with per_source, totals, overlap_rate, epoch_wrap_warnings.
        """
        s1_docs = self.get_consumed_doc_ids_s1(shuffle_indices)
        s2_docs = self.get_consumed_doc_ids_s2(shuffle_indices)

        num_s2 = len(self.new_weights) if self.switched else self.num_sources
        s2_keys = self.s2_source_keys or self.source_keys

        per_source = {}
        total_s1 = 0
        total_s2 = 0
        total_overlap = 0
        warnings = []

        for s in range(num_s2):
            # Map S2 source to S1 source
            s1_idx = self.s2_to_s1_map[s] if (self.switched and hasattr(self, 's2_to_s1_map')) else s
            s1_set = s1_docs.get(s1_idx, set()) if s1_idx >= 0 else set()
            s2_set = s2_docs.get(s, set())
            overlap = s1_set & s2_set
            s1c = len(s1_set)
            s2c = len(s2_set)
            oc = len(overlap)
            rate = oc / max(s1c, 1) if s1c > 0 else 0.0
            source_key = s2_keys[s] if s < len(s2_keys) else f"src_{s}"
            per_source[s] = {
                "source_key": source_key,
                "s1_docs": s1c, "s2_docs": s2c, "overlap_docs": oc,
                "overlap_rate": rate,
                "shared": self.shared_source_mask[s] if self.switched else True,
                "cursor_offset": self.cursor_offsets.get(s, 0) if self.switched else 0,
                "s1_source_idx": s1_idx,
            }
            total_s1 += s1c
            total_s2 += s2c
            total_overlap += oc
            if oc > 0 and s1_idx >= 0:
                shuffle_len = len(shuffle_indices[s1_idx]) if s1_idx < len(shuffle_indices) else 0
                consumed = int(self.consumed_per_source[s1_idx])
                if consumed > shuffle_len:
                    warnings.append(
                        f"Source {source_key}: consumed {consumed} > "
                        f"shuffle_index len {shuffle_len} (epoch wrap), "
                        f"overlap={oc} unavoidable")

        return {
            "per_source": per_source,
            "total_s1_docs": total_s1,
            "total_s2_docs": total_s2,
            "total_overlap_docs": total_overlap,
            "overlap_rate": total_overlap / max(total_s1, 1),
            "epoch_wrap_warnings": warnings,
        }

    def compute_ratio(self, num_batches: int = 5000, micro_batch_size: int = 1) -> Dict:
        """Compute per-source sample ratio over first num_batches of S2."""
        assert self.switched, "Must call switch_weights() first"
        total_samples = min(num_batches * micro_batch_size, self.new_size)
        num_s2 = len(self.new_weights)
        counts = numpy.zeros(num_s2, dtype=numpy.int64)
        for i in range(total_samples):
            counts[int(self.new_dataset_index[i])] += 1
        actual = counts / max(total_samples, 1)
        target = numpy.array(self.new_weights, dtype=numpy.float64)
        s2_keys = self.s2_source_keys or self.source_keys
        per_source = {}
        for s in range(num_s2):
            dev = abs(float(actual[s]) - float(target[s]))
            source_key = s2_keys[s] if s < len(s2_keys) else f"src_{s}"
            per_source[s] = {
                "source_key": source_key,
                "count": int(counts[s]),
                "actual_ratio": float(actual[s]),
                "target_ratio": float(target[s]),
                "deviation_pct": dev * 100,
            }
        max_dev = max(abs(float(actual[s]) - float(target[s])) for s in range(num_s2))
        return {
            "num_samples_analyzed": total_samples,
            "per_source": per_source,
            "max_deviation_pct": max_dev * 100,
            "pass": max_dev * 100 <= 1.0,
        }

    def to_json(self) -> str:
        """Serialize switcher state to JSON (for checkpoint persistence)."""
        return json.dumps({
            "num_sources": self.num_sources,
            "source_keys": self.source_keys,
            "consumed_per_source": self.consumed_per_source.tolist(),
            "total_consumed": int(self.total_consumed),
            "switched": self.switched,
            "new_weights": self.new_weights,
            "new_size": self.new_size,
            "shared_source_mask": self.shared_source_mask,
            "cursor_offsets": self.cursor_offsets,
            "s2_source_keys": getattr(self, "s2_source_keys", None),
            "s2_to_s1_map": getattr(self, "s2_to_s1_map", None),
        }, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "BlendSwitcher":
        """Deserialize switcher state from JSON."""
        data = json.loads(json_str)
        sw = cls(data["num_sources"], data["source_keys"])
        sw.consumed_per_source = numpy.array(data["consumed_per_source"], dtype=numpy.int64)
        sw.total_consumed = data["total_consumed"]
        sw.switched = data["switched"]
        sw.new_weights = data["new_weights"]
        sw.new_size = data["new_size"]
        sw.shared_source_mask = data["shared_source_mask"]
        sw.cursor_offsets = data["cursor_offsets"]
        sw.s2_source_keys = data.get("s2_source_keys", None)
        sw.s2_to_s1_map = data.get("s2_to_s1_map", None)
        return sw


class BlendHotSwitchMixin:
    """Mixin to add update_weights() to BlendedDataset.

    When --blend-hot-switch is OFF, this mixin is not applied and
    BlendedDataset behaves exactly as stock.
    """

    def update_weights(self, new_weights, new_size, switcher, build_fn=None):
        """Hot-update blend weights with per-source cursor mapping."""
        shared_mask = switcher.shared_source_mask or [True] * len(new_weights)
        new_di, new_dsi = switcher.switch_weights(new_weights, new_size, shared_mask, build_fn)
        self.dataset_index = new_di
        self.dataset_sample_index = new_dsi
        self.weights = new_weights
        self.size = new_size
        return new_di, new_dsi


def apply_blend_hot_switch_patch(dataset_class) -> None:
    """Monkey-patch BlendedDataset class to add update_weights().

    When --blend-hot-switch is OFF, do not call this (stock behavior preserved).
    """
    dataset_class.update_weights = BlendHotSwitchMixin.update_weights


class BlendHotSwitchSampler:
    """Per-source progress-driven sampler for post-switch S2.

    Replaces stock MegatronPretrainingRandomSampler's global
    epoch = consumed // active_total logic with sequential iteration
    over pre-built (cursor-offset) indices.
    When --blend-hot-switch is OFF, stock sampler is used instead.
    """

    def __init__(self, dataset, switcher, total_samples, micro_batch_size,
                 data_parallel_rank, data_parallel_size, data_sharding):
        self.dataset = dataset
        self.switcher = switcher
        self.total_samples = total_samples
        self.micro_batch_size = micro_batch_size
        self.data_parallel_rank = data_parallel_rank
        self.data_parallel_size = data_parallel_size
        self.data_sharding = data_sharding
        self.mbs_dp = micro_batch_size * data_parallel_size
        self.last_batch_size = total_samples % self.mbs_dp
        self.active_total = total_samples - self.last_batch_size
        self.consumed_samples = 0

    def __len__(self):
        return self.total_samples

    def __iter__(self):
        start = self.data_parallel_rank * self.micro_batch_size
        step = self.mbs_dp
        batch = []
        for idx in range(start, self.active_total, step):
            batch.append(idx)
            if len(batch) == self.micro_batch_size:
                self.consumed_samples += self.mbs_dp
                yield batch
                batch = []


if __name__ == "__main__":
    print("BlendSwitcher — Plan F: weight hot-update + cross-blend cursor mapping")
    print("Run test_blend_switch.py for validation.")
