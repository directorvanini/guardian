# 🛡️ Guardian v2.0
### Research Fraud Detection System
**Sanctuary of Ma'at Research Institute · Kenneth Vanini**

> *"The heart is weighed against the feather. No exceptions."*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-maatonly.netlify.app-C9A84C?style=flat-square)](https://maatonly.netlify.app)
[![Hackathon](https://img.shields.io/badge/Complete%20AI%20Hackathon-2026-4299e1?style=flat-square)](https://lablab.ai)
[![Built on](https://img.shields.io/badge/Built%20on-Complete.dev-48bb78?style=flat-square)](https://complete.dev)

---

## What is Guardian?

Guardian is a **multi-agent AI system** that detects research fraud before it reaches print. It routes every manuscript through four specialist agents simultaneously, then synthesizes a single evidence-backed verdict.

**Guardian is the first automated system to include paper mill detection.** The nearest competitor (Morressier) publicly admitted in July 2023 that their paper mill tool is still in development.

---

## Four Specialist Agents

| Agent | Detects | Key Patterns |
|-------|---------|--------------|
| **[S] Statistical** | Data fabrication, p-hacking, impossible variance | Stapel (58 retractions), Wansink (15 retractions) |
| **[C] Citation** | Unsupported absolute claims, citation manipulation | Epistemic overreach preceding fabricated conclusions |
| **[M] Methodology** | Missing ethics approval, no data availability, no preregistration | Boldt (90+ retractions), LaCour (Science retraction) |
| **[P] Paper Mill** | Tortured phrases, round sample sizes, boilerplate ethics, template results | Cabanac & Labbé (2021), Nature investigation |

The **Orchestrator** synthesizes all four agents into a final verdict: `CRITICAL`, `FLAGGED`, or `COMPLIANT`.

---

## Live Demo

🔗 **[maatonly.netlify.app](https://maatonly.netlify.app)**

- Paste any manuscript excerpt
- Load the sample paper to see a CRITICAL verdict in action
- All four agents run in real time
- Every finding links to a documented historical retraction case

*Demo available through March 8, 2026.*

---

## Architecture

```
User / Complete.dev Workspace
         │
         ▼
  ┌─────────────────┐
  │   Orchestrator   │  ← Primary agent (users interact here)
  └────────┬────────┘
           │ routes to
    ┌──────┴───────┐
    ▼              ▼
┌────────┐   ┌──────────┐
│ Stats  │   │ Citation │
└────────┘   └──────────┘
    ▼              ▼
┌─────────────┐  ┌────────────┐
│ Methodology │  │ Paper Mill │  ← NEW: industry-first
└─────────────┘  └────────────┘
           │
           ▼
    Guardian API (Flask)
    guardian_v2.py backend
```

---

## Project Structure

```
guardian/
├── guardian_v2.py          # Core detection engine — all 4 agents + orchestrator
├── guardian_api.py         # Flask REST API — exposes agents as HTTP endpoints
├── FRAUD_DETECTION_ENGINE_v2.py  # Standalone GUI version (tkinter)
├── Guardian_gui.py         # GUI wrapper
├── complete_dev_agents.py  # Complete.dev Agent Builder system prompts
├── requirements.txt        # Python dependencies
└── README.md
```

---

## API Endpoints

```
POST /analyze              — Full 4-agent analysis (primary endpoint)
POST /agents/stats         — Statistical agent only
POST /agents/citations     — Citation agent only
POST /agents/methods       — Methodology agent only
POST /agents/papermill     — Paper Mill agent only  ← industry-first
GET  /health               — Health check
```

### Example

```bash
curl -X POST https://your-deployment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "paste manuscript text here"}'
```

```json
{
  "overall_risk": "CRITICAL",
  "agent_statuses": {
    "Statistical Integrity": "CRITICAL",
    "Citation Integrity": "PASS",
    "Methodology & Ethics": "CRITICAL",
    "Paper Mill": "CRITICAL"
  },
  "all_findings": [...],
  "recommendation": "DO NOT PUBLISH — exhibits patterns from major retracted papers",
  "total_findings": 8
}
```

---

## Deploy in 3 Steps

**1. Clone and install**
```bash
git clone https://github.com/directorvanini/guardian
cd guardian
pip install -r requirements.txt
```

**2. Run locally**
```bash
python guardian_api.py
# API running at http://localhost:5050
```

**3. Deploy publicly** (Railway recommended)
```bash
# Push to GitHub, connect to Railway
# Set env var: ANTHROPIC_API_KEY=sk-ant-...
# Railway auto-detects Flask and deploys
```

---

## Complete.dev Integration

Guardian is built on **[Complete.dev](https://complete.dev)** as part of the Complete AI Hackathon 2026.

Five agents are configured in the Complete.dev workspace using the Agent Builder:

1. `Guardian — Statistical Agent` → `POST /agents/stats`
2. `Guardian — Citation Agent` → `POST /agents/citations`
3. `Guardian — Methodology Agent` → `POST /agents/methods`
4. `Guardian — Paper Mill Agent` → `POST /agents/papermill`
5. `Guardian — Orchestrator` → `POST /analyze` ← primary user-facing agent

System prompts for all five agents are in `complete_dev_agents.py`.

---

## The Problem Guardian Solves

- **$28 billion** is lost annually to irreproducible research (Freedman et al., 2015)
- Retraction Watch documents **hundreds of new retractions each year**
- Paper mills — criminal organizations selling fabricated manuscripts — are a **rapidly growing threat** with no automated detection solution currently in market
- Current tools (iThenticate, StatCheck, Proofig) each address one dimension; **no orchestrated multi-agent solution exists**

Guardian fills that gap.

---

## Built With

- **Complete.dev** — multi-agent workspace and Agent Builder
- **Python** — detection engine (regex + pattern matching)
- **Flask** — REST API layer
- **Anthropic Claude** — AI-enhanced analysis (optional, degrades gracefully)
- **JavaScript** — browser-based lite demo
- **Netlify** — demo deployment

---

## The Ma'at Principle

In ancient Egyptian belief, the heart of the deceased was weighed against the feather of Ma'at — goddess of truth, justice, and cosmic order. No exceptions were made for wealth, prestige, or the number of citations.

Guardian applies the same standard to research papers.

---

**Complete AI Hackathon 2026 · lablab.ai · Kenneth Vanini**  
📧 director_vanini@outlook.com · 🌐 maatonly.netlify.app
