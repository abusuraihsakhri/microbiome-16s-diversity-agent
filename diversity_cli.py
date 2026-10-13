"""CLI entry point for ASV/OTU diversity computation (independent of audit CLI)."""
import argparse
import csv
import sys
from pathlib import Path

from microbiome_mind.diversity import analyse_counts, read_count_table


def _safe_spreadsheet_cell(value):
    """Avoid treating imported sample identifiers as spreadsheet formulas."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute descriptive alpha diversity and Bray-Curtis from sample-by-feature counts")
    parser.add_argument("input", help="CSV with sample_id column followed by ASV/OTU counts")
    parser.add_argument("--alpha", default="alpha_diversity.csv", help="Alpha diversity output CSV")
    parser.add_argument("--beta", default="bray_curtis.csv", help="Pairwise distance matrix output CSV")
    args = parser.parse_args(argv)
    paths = [Path(v).resolve() for v in (args.input, args.alpha, args.beta)]
    if len(set(paths)) != 3:
        parser.error("Input and output paths must be different")
    try:
        result = analyse_counts(read_count_table(paths[0]))
        with paths[1].open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["sample_id", "reads", "observed", "shannon", "simpson_1_minus_d", "chao1_bias_corrected", "pielou_evenness"])
            for a in result["alpha"]:
                writer.writerow([_safe_spreadsheet_cell(a["sample"]), a["reads"], a["observed"], a["shannon"], a["simpson"], a["chao1"], a["evenness"]])
        with paths[2].open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["sample_id", *(_safe_spreadsheet_cell(x) for x in result["sample_names"])])
            for name, row in zip(result["sample_names"], result["beta"]):
                writer.writerow([_safe_spreadsheet_cell(name), *row])
    except (OSError, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Computed {len(result['alpha'])} samples; wrote {args.alpha} and {args.beta}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
