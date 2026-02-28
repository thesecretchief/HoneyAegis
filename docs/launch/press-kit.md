# HoneyAegis Press Kit

## One-Liner

HoneyAegis is a free, open-source honeypot platform that turns any server or Raspberry Pi into a professional deception network in under 5 minutes.

## Elevator Pitch (100 words)

HoneyAegis is a Docker-native, self-hosted honeypot platform that deploys in a single command. It captures full attacker sessions (SSH/Telnet keystrokes with video replay), enriches them with local AI threat analysis via Ollama, and delivers real-time dashboards with attack maps and trend analytics. Designed for security teams, MSPs, and homelabbers, it supports multi-tenant isolation, Raspberry Pi edge sensors, Kubernetes deployments, and integrations with every major SIEM. MIT-licensed, no cloud dependency, no subscriptions — full data sovereignty. HoneyAegis is StingBox but 10x better and free forever.

## Key Facts

- **License:** MIT (open source, free forever)
- **First release:** v1.0.0
- **Deployment:** Docker Compose (one command), Helm/K8s, Raspberry Pi
- **Languages:** Python (FastAPI), TypeScript (Next.js)
- **RAM requirement:** 2 GB minimum (light), 4 GB (full with AI)
- **Platforms:** linux/amd64, linux/arm64
- **Repository:** https://github.com/thesecretchief/HoneyAegis

## Feature Highlights

1. **One-command deploy** — `docker compose up -d` on any Linux machine
2. **Full session capture** — SSH/Telnet keystrokes recorded, exportable as MP4/GIF
3. **Local AI analysis** — Ollama-powered threat summaries with MITRE ATT&CK mapping
4. **Real-time dashboard** — live attack map, incident timeline, trend analytics
5. **Multi-sensor fleet** — manage RPi sensors across locations from one console
6. **Plugin ecosystem** — extend with custom honeypot emulators and enrichers
7. **MSP-ready** — multi-tenant isolation, white-label client portals, PDF reports
8. **SIEM integration** — export to Splunk, QRadar, ArcSight via CEF/Syslog/JSON
9. **Prometheus + Grafana** — built-in monitoring dashboards
10. **Hardware kits** — pre-built RPi sensor nodes ($89 BOM)

## Comparison Table

| Feature | HoneyAegis | StingBox | T-Pot | Canary |
|---------|------------|----------|-------|--------|
| Self-hosted | Yes | Cloud-only | Yes | Hybrid |
| AI summaries | Local (Ollama) | Cloud AI | No | No |
| Deploy time | < 5 min | Varies | 15-30 min | Hardware |
| Session video | Native MP4/GIF | Limited | No | No |
| Multi-tenant | Yes | No | No | Limited |
| ARM64 (RPi) | Yes | No | Partial | Hardware |
| License | MIT | Proprietary | GPL | Proprietary |
| Cost | Free | $$$/mo | Free | $$$/unit |
| RAM minimum | 2 GB | N/A | 8 GB | N/A |
| Plugin system | Yes | No | Limited | No |

## Target Audiences

1. **Security teams** — deploy deception networks alongside production infrastructure
2. **MSPs/MSSPs** — white-label honeypot monitoring for client sites
3. **Homelabbers** — learn about real-world attacks on your own network
4. **Researchers** — capture and analyze attack patterns and malware samples
5. **CTF/Training** — teach defensive security with live attacker data

## Logo & Brand Assets

- **Primary color:** `#f59e0b` (amber)
- **Dark background:** `#030712` (gray-950)
- **Font:** System default (Inter for web, monospace for terminal)
- **Naming:** Always "HoneyAegis" (capital H, capital A, no space)

## Contact

- **GitHub:** https://github.com/thesecretchief/HoneyAegis
- **Issues:** https://github.com/thesecretchief/HoneyAegis/issues
- **Discussions:** https://github.com/thesecretchief/HoneyAegis/discussions
