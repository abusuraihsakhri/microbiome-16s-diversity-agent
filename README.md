# Microbiome 16S Diversity Agent

A local-first research utility for descriptive alpha and beta diversity analysis of 16S amplicon **ASV/OTU read-count tables**. Includes a static browser application and a dependency-light Python calculation module, alongside the repository's pre-existing audit and API utilities.

## Browser application

Open the site's `index.html` in a static web server, or use the GitHub Pages deployment once it is enabled. The application accepts pasted or uploaded CSV, displays per-sample diversity and a pairwise distance matrix, and exports both tables as CSV. No data is sent to an application server; calculations and downloads occur in the browser. There are no remote runtime dependencies.

The input is **samples in rows** and **ASVs/OTUs in columns**. The first column must be `sample_id`; counts must be nonnegative integers, and each sample must contain at least one read.

```csv
sample_id,ASV_1,ASV_2,ASV_3
Sample_A,12,8,0
Sample_B,1,4,10
```

[Example dataset](example_counts.csv). The browser currently supports up to 100 samples, 500 features, and 3 MB per CSV.

## Metrics and scope

| Output | Definition |
| --- | --- |
| Observed richness | Number of features with nonzero counts |
| Shannon | `-Σ pᵢ ln(pᵢ)` with natural logarithms |
| Simpson | `1 - Σ pᵢ²` |
| Chao1 | Bias-corrected `S_obs + f₁(f₁ − 1) / [2(f₂ + 1)]` |
| Pielou evenness | Shannon / ln(observed richness), 0 for richness ≤ 1 |
| Bray–Curtis | Half the sum of absolute differences of sample **relative abundances** |

These are descriptive metrics; sequencing depth and preprocessing choices affect interpretation. **Weighted/unweighted UniFrac is not implemented**, because a phylogenetic tree is required. **PERMANOVA, rarefaction, significance testing, and clinical decision support are not implemented** in the diversity calculator. The existing threshold-based `agents/` and `microbiome_mind/` audit paths are preserved for compatibility but must not be confused with phylogenetic diversity or clinical validation.

## Python installation and CLI

Python 3.10+ is required. From the repository root:

```bash
python -m pip install -e '.[server,test]'
python -m diversity_cli example_counts.csv --alpha alpha.csv --beta beta.csv
# or after installation:
microbiome-diversity example_counts.csv --alpha alpha.csv --beta beta.csv
```

The diversity calculation uses the Python standard library; the package also installs Pydantic for its existing audit command. Use `pip install -e .` if FastAPI and pytest are not needed.

The original audit functionality remains available:

```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

These audit inputs are **generic numeric thresholds**, not microbiome diversity indices. The FastAPI endpoints (`/health`, `/metrics`, `/api/audit`, `/api/chat`, `/api/audit/logs`) are separate from the static browser calculator. The `/metrics` endpoint returns JSON, not Prometheus exposition text. `/api/chat` uses a deterministic mock response, not a remote model. Do not submit patient-identifiable information; regex-based screening does not guarantee de-identification.

## Testing and deployment

```bash
python -m pytest -q
node --test web/diversity.test.mjs
node --check web/app.mjs
node --check web/diversity.mjs
python -m http.server 8001
```

Then visit `http://127.0.0.1:8001/` for the static UI. Node.js 22 is used by CI tests, but no Node dependencies are required for running the app. CI runs Python 3.10–3.12 tests and Node tests. The GitHub Pages workflow packages only the static `index.html` and `web/` assets when changes are pushed to `master`.

Docker runs the existing FastAPI service, **not** the GitHub Pages app:

```bash
docker build -t microbiome-16s .
docker run -p 127.0.0.1:8000:8000 microbiome-16s
```

## Privacy, compatibility, and license

Browser analysis is client-side and does not need accounts, cookies, network APIs, or external fonts. Exports are initiated locally; spreadsheet-formula-leading sample IDs are escaped in exported CSV. Modern browsers supporting JavaScript modules and `File.text()` are required. Static Pages cannot host the Python API or run server-side Python. Existing audit logs are in-memory and not a production-compliant patient record system.

Licensed under the [MIT License](LICENSE).
