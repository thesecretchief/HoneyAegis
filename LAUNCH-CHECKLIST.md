# HoneyAegis - Launch & Deployment Checklist (v1.3.0)

## 1. Final Cleanup (Done by Claude)
- [ ] All 12 CI checks green
- [ ] v1.3.0 GitHub Release published (with artifacts)
- [ ] README updated with latest GIFs/screenshots
- [ ] GitHub Project board all tasks "Done"

## 2. Production Deployment (Recommended Path)

### VPS (Hetzner / DigitalOcean)
```bash
# On fresh Ubuntu 24.04
apt update && apt install docker.io docker-compose-plugin git curl -y
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
# Edit .env — change all passwords, set DOMAIN=yourdomain.com
docker compose --profile full up -d
