#!/usr/bin/env python3
"""
PreTokenizedSFTDataset — loads pre-tokenized parquet (input_ids, attention_mask,
loss_mask, position_ids as list columns) and returns tensors in __getitem__.

This bypasses MultiTurnSFTDataset's slow per-example tokenization (18 apply_chat_template
calls per 9-turn conversation in DataLoader workers).

Usage with verl:
  data.custom_cls.path=/path/to/baize_posttrain_pretokenized_dataset.py
  data.custom_cls.name=PreTokenizedSFTDataset
  data.multiturn.enable=false
"""
from typing import List, Union
import torch
from torch.utils.data import Dataset


class PreTokenizedSFTDataset(Dataset):
    """Loads pre-tokenized parquet with input_ids/attention_mask/loss_mask/position_ids."""

    def __init__(self, parquet_files: Union[str, List[str]], tokenizer, config=None):
        config = config or {}
        if not isinstance(parquet_files, List):
            parquet_files = [parquet_files]

        # verl's copy_local_path_from_hdfs handles NFS/local paths
        try:
            from verl.utils.fs import copy_local_path_from_hdfs
            self.parquet_files = [
                copy_local_path_from_hdfs(f, verbose=True) for f in parquet_files
            ]
        except Exception:
            self.parquet_files = parquet_files

        self.tokenizer = tokenizer

        import pandas as pd
        dataframes = [pd.read_parquet(f) for f in self.parquet_files]
        self.dataframe = pd.concat(dataframes, ignore_index=True)

        self.input_ids = self.dataframe["input_ids"].tolist()
        self.attention_mask = self.dataframe["attention_mask"].tolist()
        self.loss_mask = self.dataframe["loss_mask"].tolist()
        self.position_ids = self.dataframe["position_ids"].tolist()

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, item):
        return {
            "input_ids": torch.tensor(self.input_ids[item], dtype=torch.long),
            "attention_mask": torch.tensor(self.attention_mask[item], dtype=torch.long),
            "loss_mask": torch.tensor(self.loss_mask[item], dtype=torch.long),
            "position_ids": torch.tensor(self.position_ids[item], dtype=torch.long),
        }
