# HoneyAegis v1.1 — Announcing the Intelligent Honeypot Platform

*The open-source honeypot that fights back with AI.*

---

## TL;DR

HoneyAegis is now a production-grade deception platform with threat intelligence, malware sandboxing, enterprise RBAC, SSO, high availability, and a full documentation site. Deploy in 5 minutes. Free forever. MIT licensed.

---

## What's New in v1.1

### Threat Intelligence Aggregation
Query MISP, AlienVault OTX, AbuseIPDB, and VirusTotal from a single API. Every attacker IP is automatically enriched with reputation data, confidence scores, and category tags. Results are cached for 1 hour to minimize API calls.

### Malware Sandbox
Every file captured by the honeypot is automatically analyzed: hashing (MD5/SHA-1/SHA-256), entropy analysis, magic byte detection, pattern matching (12 YARA-like rules), and IOC extraction. Risk scores from 0-100 with clean/suspicious/malicious verdicts. Optional Cuckoo/CAPE integration for dynamic analysis.

### Advanced AI (RAG + Multi-LLM)
Retrieval-augmented generation pulls context from recent captured sessions before querying the local LLM. Multi-model routing selects the best model for each task: phi3:mini for quick summaries, llama3.2:3b for detailed analysis, mistral:7b for complex threat intelligence. All processing stays on your hardware.

### Enterprise Features
- **RBAC** — Four roles (superadmin, admin, analyst, viewer) with 25+ granular permissions
- **SSO/OIDC** — Stubs for Keycloak, Okta, Azure AD, Google Workspace
- **Advanced Reporting** — Executive dashboards with risk scoring, compliance metrics, trend analysis
- **High Availability** — Redis Sentinel (3-node), PostgreSQL replication, Celery Flower monitoring
- **Audit Logging** — Structured JSON, CEF, and Syslog formats for SIEM integration

### Documentation Site
Full MkDocs Material documentation site at [thesecretchief.github.io/HoneyAegis](https://thesecretchief.github.io/HoneyAegis/). Auto-deployed via GitHub Pages on every push.

### Internationalization
Dashboard available in 5 languages: English, Spanish, German, French, and Greek. Browser auto-detection with persistent locale selection.

## By the Numbers

- **280+ tests** passing
- **30+ API endpoints**
- **5 backend services** (threat intel, sandbox, AI, reporting, benchmarks)
- **5 languages** supported
- **4 RBAC roles** with 25+ permissions
- **4 threat intel feeds** (MISP, OTX, AbuseIPDB, VirusTotal)
- **3 SIEM export formats** (ELK, Splunk HEC, TheHive) + JSON, CEF, Syslog
- **12 malware detection patterns**
- **0 cloud dependencies**

## Get Started

```bash
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis && cp .env.example .env
docker compose up -d
```

Dashboard at `http://localhost:3000`. Default login: `admin` / `changeme`.

## What's Next

HoneyAegis is MIT licensed and free forever. We're building the honeypot platform that every security team deserves — no vendor lock-in, no subscriptions, full data sovereignty.

Contributions welcome: [github.com/thesecretchief/HoneyAegis](https://github.com/thesecretchief/HoneyAegis)

---

*Built with purpose. Open source forever.*
