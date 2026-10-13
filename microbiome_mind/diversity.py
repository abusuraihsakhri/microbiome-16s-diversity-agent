"""Descriptive alpha and beta diversity from ASV/OTU count tables.

This module does not perform phylogenetic UniFrac, PERMANOVA, rarefaction,
or statistical inference. Each CSV row is one sample and each feature is
an integer read count.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Union

MAX_SAMPLES = 100
MAX_FEATURES = 500


def read_count_table(path: Union[str, Path]) -> Dict[str, list]:
    """Read a sample-by-feature CSV; reject missing, invalid and empty counts."""
    source = Path(path)
    if source.stat().st_size > 3_000_000:
        raise ValueError("CSV exceeds 3 MB size limit")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = [column.strip() for column in next(reader)]
        except StopIteration as exc:
            raise ValueError("Count table is empty") from exc
        if len(header) < 2 or header[0].lower() != "sample_id":
            raise ValueError("First column must be sample_id and remaining columns features")
        if len(header) - 1 > MAX_FEATURES or not all(header) or len(header) != len(set(header)):
            raise ValueError("Feature names must be unique, nonempty and within the size limit")
        samples: List[Dict[str, object]] = []
        seen = set()
        for line_no, row in enumerate(reader, 2):
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != len(header):
                raise ValueError(f"Row {line_no}: wrong number of columns")
            sample_id = row[0].strip()
            if not sample_id or sample_id in seen:
                raise ValueError(f"Row {line_no}: duplicate or empty sample_id")
            seen.add(sample_id)
            counts = []
            for value in row[1:]:
                value = value.strip()
                if not value or not value.isascii() or not value.isdecimal():
                    raise ValueError(f"Row {line_no}: counts must be nonnegative integers")
                count = int(value)
                if count > 2**53 - 1:
                    raise ValueError(f"Row {line_no}: count exceeds safe browser integer range")
                counts.append(count)
            depth = sum(counts)
            if not 0 < depth <= 2**53 - 1:
                raise ValueError(f"Row {line_no}: sample read depth must be positive")
            samples.append({"name": sample_id, "counts": counts, "depth": depth})
            if len(samples) > MAX_SAMPLES:
                raise ValueError("Maximum 100 samples per table")
    if not samples:
        raise ValueError("At least one sample is required")
    return {"features": header[1:], "samples": samples}


def analyse_counts(table: Dict[str, list]) -> dict:
    """Calculate Shannon, Simpson, Chao1, Pielou and relative Bray-Curtis."""
    samples = table["samples"]
    features = table["features"]
    if not samples or not features:
        raise ValueError("Count table must contain samples and features")
    alpha = []
    for sample in samples:
        counts = sample["counts"]
        depth = sample["depth"]
        if len(counts) != len(features) or depth <= 0:
            raise ValueError("Inconsistent count table")
        present = [count for count in counts if count > 0]
        observed = len(present)
        singletons = sum(count == 1 for count in present)
        doubletons = sum(count == 2 for count in present)
        shannon = -sum((count / depth) * math.log(count / depth) for count in present)
        simpson = 1 - sum((count / depth) ** 2 for count in present)
        chao1 = observed + (singletons * (singletons - 1)) / (2 * (doubletons + 1))
        alpha.append({
            "sample": sample["name"], "reads": depth, "observed": observed,
            "shannon": shannon, "simpson": simpson, "chao1": chao1,
            "evenness": shannon / math.log(observed) if observed > 1 else 0.0,
        })
    beta = []
    for left in samples:
        beta.append([sum(abs(a / left["depth"] - b / right["depth"])
                         for a, b in zip(left["counts"], right["counts"])) / 2
                     for right in samples])
    return {"alpha": alpha, "beta": beta, "sample_names": [s["name"] for s in samples]}
