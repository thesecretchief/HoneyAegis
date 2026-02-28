# HoneyAegis Launch Announcement Templates

## Twitter/X Thread

**Tweet 1 (hook):**
> Introducing HoneyAegis — a free, open-source honeypot platform that turns any server into a professional deception network in under 5 minutes.
>
> One command. Full session capture. Local AI analysis. No cloud. No subscriptions.
>
> github.com/thesecretchief/HoneyAegis

**Tweet 2 (features):**
> What you get with HoneyAegis:
>
> - Full SSH/Telnet session capture with video replay
> - Local AI threat analysis (Ollama, no data leaves your network)
> - Real-time attack map + dashboard
> - Multi-sensor fleet management
> - SIEM export (CEF, Syslog, JSON)
> - Runs on Raspberry Pi ($89 sensor kit)

**Tweet 3 (comparison):**
> How HoneyAegis compares:
>
> vs StingBox: Free, self-hosted, AI included
> vs T-Pot: 2GB RAM (not 8GB), session video, multi-tenant
> vs Canary: MIT license, no per-unit cost, plugin system
>
> MIT licensed. Open source forever.

**Tweet 4 (CTA):**
> Get started in 60 seconds:
>
> ```
> git clone github.com/thesecretchief/HoneyAegis
> cd HoneyAegis && cp .env.example .env
> docker compose up -d
> ```
>
> Star the repo, try it out, and tell us what you think.
> PRs welcome — we're building this in the open.

## Reddit Post (r/netsec, r/homelab, r/selfhosted)

**Title:** HoneyAegis: Free, open-source honeypot platform with AI analysis, session replay, and multi-sensor fleet management

**Body:**

Hi everyone,

I'm excited to share HoneyAegis, a Docker-native honeypot platform I've been building. It's MIT-licensed, self-hosted, and deploys with a single `docker compose up -d`.

**What it does:**

- Captures full SSH/Telnet attacker sessions (keystrokes, commands)
- Exports sessions as MP4/GIF video replays
- Local AI threat analysis via Ollama (MITRE ATT&CK mapping, threat scoring)
- Real-time dashboard with attack map, trends, and live event feed
- Multi-sensor fleet management (RPi sensors at each site)
- Multi-tenant isolation for MSPs with white-label client portals
- SIEM integration (CEF, Syslog, JSON export)
- Prometheus + Grafana monitoring
- Plugin system for custom honeypot services
- Honey tokens (decoy credentials that alert on use)
- Auto-response webhooks (Slack, Discord, PagerDuty)

**Why I built it:**

Commercial honeypot solutions are expensive and cloud-dependent. T-Pot is great but requires 8GB+ RAM and lacks session video. I wanted something that runs on a $55 Raspberry Pi, gives you full visibility into attacker behavior, and doesn't send your data to anyone's cloud.

**Tech stack:** FastAPI (Python), Next.js 15 (TypeScript), PostgreSQL, Redis, Cowrie, Docker Compose.

**Requirements:** 2GB RAM minimum (light profile), 4GB for full profile with AI.

**Links:**

- GitHub: https://github.com/thesecretchief/HoneyAegis
- Docs: https://github.com/thesecretchief/HoneyAegis/tree/main/docs
- Hardware kit guide: https://github.com/thesecretchief/HoneyAegis/blob/main/docs/hardware-kit-guide.md

I'd love feedback, bug reports, and contributions. The roadmap is public and we're actively developing.

## Hacker News Post

**Title:** Show HN: HoneyAegis – Open-source honeypot platform with local AI analysis

**Body:**

HoneyAegis is a Docker-native honeypot platform that deploys in a single command. It captures full attacker sessions, analyzes them with a local LLM (Ollama), and delivers a real-time dashboard.

Key differentiators:

1. Runs on 2GB RAM (Raspberry Pi compatible)
2. AI analysis stays local — no cloud dependency
3. Full session video replay (MP4/GIF export)
4. Multi-tenant for MSPs
5. Plugin system for custom honeypots
6. SIEM export (CEF/Syslog/JSON)

MIT licensed. Free forever. No telemetry by default.

https://github.com/thesecretchief/HoneyAegis

## YouTube Demo Script Outline

**Duration:** 5-7 minutes

1. **Intro** (30s) — What is HoneyAegis? Why honeypots matter.
2. **Deploy** (60s) — Clone, configure `.env`, `docker compose up -d`. Show services starting.
3. **Dashboard tour** (90s) — Stats cards, attack map, live feed, session list.
4. **Session replay** (60s) — Click a session, watch attacker commands in real-time.
5. **AI analysis** (60s) — Show Ollama-generated threat summary, MITRE mapping.
6. **Video export** (30s) — Export session as MP4/GIF, show output.
7. **Fleet management** (45s) — Register an RPi sensor, show it coming online.
8. **Honey tokens** (30s) — Create a decoy credential, show alert when triggered.
9. **Outro** (30s) — Links, star the repo, community.
