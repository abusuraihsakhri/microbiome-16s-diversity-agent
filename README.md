# Microbiome 16S Diversity Agent

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** CAP / CLSI / ISO Standards, QIIME 2 / Earth Microbiome Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Microbiome 16S Diversity Agent** is an advanced analytical and computational platform implementing Shannon entropy, Chao1 richness & Weighted UniFrac phylogenetic distance evaluation. It provides multi-worker consensus evaluation with tamper-evident audit logging and Zero-PHI outbound protection.

The system consists of two main modules:

- **`agents/`** - Enterprise clinical decision support with multi-worker evaluation, HMAC-SHA256 audit trail, and PHI guard
- **`microbiome_mind/`** - Alpha & beta diversity profiler (UniFrac / Shannon) for biomedical scientific discovery

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Multi-Worker Consensus**: Three specialized workers (QC Invariant, Safety Escalation, Protocol Conformance) evaluate each task.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.

---

## 💻 CLI Quickstart & Usage

### Installation

```bash
pip install fastapi uvicorn pydantic pytest
```

### 1. Run Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `--task-id` | string | TASK-2026-001 | Unique task / case identifier |
| `--target` | string | KEY-TARGET-01 | Entity, patient key, or genomic target |
| `--primary` | float | 28.5 | Primary domain measurement or score |
| `--secondary` | float | 14.2 | Secondary kinetic or confidence score |
| `--critical` | flag | False | Emergency escalation or high priority trigger |
| `--status` | string | DISCORDANT | Status code or phenotype descriptor |
| `-i / --input` | path | required | Input CSV file path for batch processing |
| `-o / --output` | path | results.csv | Output CSV file path for batch processing |

### Input Data Schema (CSV Batch Mode)

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `task_id` | string | Yes | Unique task identifier |
| `target_identifier` | string | Yes | Target entity key |
| `primary_metric` | float | Yes | Primary measurement value |
| `secondary_metric` | float | Yes | Secondary measurement value |
| `is_critical_flag` | boolean | No | Critical escalation flag (true/false/1/0/yes) |
| `status_descriptor` | string | No | Status descriptor (NOMINAL, DISCORDANT, ANOMALY, etc.) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Integrity verified by re-computing HMAC signatures.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit signing | Random per-session (set for production) |
| `MODEL_PROVIDER` | LLM provider (mock, ollama, claude, openai) | mock |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

Run security audit:

```bash
python -c "from agents.base import AuditLogger; assert AuditLogger.verify_integrity(); print('Security Audit Passed!')"
```

---

## 🐳 Container Deployment

```bash
docker build -t microbiome-16s-diversity-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key microbiome-16s-diversity-agent
```

Or using Docker Compose:

```bash
echo "AUDIT_SECRET_KEY=your-secure-key" > .env
docker-compose up -d
```

### REST API Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus-compatible metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Query supervisory chat |
| `/api/audit/logs` | GET | Retrieve audit trail |

---

## 📁 Project Structure

```
microbiome-16s-diversity-agent/
├── agents/                    # Enterprise clinical decision support
│   ├── __init__.py
│   ├── api.py                 # FastAPI REST server
│   ├── base.py                # PHI guard, HMAC audit trail
│   ├── learning.py            # Bayesian calibration engine
│   ├── llm_factory.py         # LLM provider factory
│   ├── metrics.py             # Prometheus metrics collector
│   ├── models.py              # Pydantic data models
│   ├── streamer.py            # WebSocket telemetry broadcaster
│   ├── supervisor.py          # Multi-worker orchestrator
│   └── workers.py             # Specialized evaluation workers
├── microbiome_mind/           # Alpha & beta diversity profiler
│   ├── __init__.py
│   ├── agents.py              # Sub-agents & coordinator
│   ├── cli.py                 # CLI entry point
│   ├── engine.py              # Core algorithmic engine
│   ├── models.py              # Data models
│   └── server.py              # FastAPI server factory
├── tests/                     # Automated test suite
├── cli.py                     # Main CLI entry point
├── simulator.py               # High-throughput stress testing
├── enrichment.py              # Feature enrichment engines
├── Dockerfile                 # Container build
├── docker-compose.yml         # Multi-service orchestration
├── pyproject.toml             # Package configuration
└── README.md                  # This file
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
