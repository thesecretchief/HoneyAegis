# Plugin Marketplace

The HoneyAegis Plugin Marketplace is a curated directory of community-contributed plugins. All marketplace plugins are open-source and reviewed for security before listing.

## Browsing Plugins

### Via Dashboard

Navigate to **Settings > Plugins > Marketplace** to browse, search, and install plugins directly from the dashboard.

### Via CLI

```bash
# Search the marketplace
honeyaegis plugin search "ftp"

# List all available plugins
honeyaegis plugin list --remote

# Show plugin details
honeyaegis plugin info community-ftp-honeypot
```

### Via API

```bash
# Browse by category
curl "http://localhost:8000/api/v1/marketplace?category=enrichment" \
  -H "Authorization: Bearer $TOKEN"
```

## Categories

- **Enrichment** -- Threat intel feeds, reputation scoring
- **Response** -- Auto-blocking, ticketing integration
- **Notification** -- Custom alert channels
- **Emulator** -- Additional honeypot service emulators

## Featured Plugins

| Plugin | Type | Description |
|---|---|---|
| **community-ftp-honeypot** | Honeypot | Full-featured FTP honeypot with passive mode support |
| **community-rdp-honeypot** | Honeypot | RDP honeypot with NLA authentication capture |
| **community-mqtt-honeypot** | Honeypot | MQTT broker honeypot for IoT environments |
| **enrichment-greynoise** | Enrichment | GreyNoise IP context integration |
| **enrichment-shodan** | Enrichment | Shodan host enrichment |
| **alert-opsgenie** | Alert | Atlassian Opsgenie alert channel |
| **widget-attack-heatmap** | Widget | Calendar heatmap dashboard widget |
| **auto-ip-blocker** | Response | Block IPs after repeated failed logins |

## Installing Plugins

### From Marketplace

```bash
# Install from the marketplace
honeyaegis plugin install community-ftp-honeypot

# Install a specific version
honeyaegis plugin install community-ftp-honeypot==1.2.0

# Via the API
curl -X POST http://localhost:8000/api/v1/marketplace/install \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"plugin_id": "auto-ip-blocker", "version": "1.0.0"}'

# Restart to activate
docker compose restart backend
```

### From Git Repository

```bash
honeyaegis plugin install --git https://github.com/user/my-plugin.git
```

## Managing Installed Plugins

```bash
# List installed plugins
honeyaegis plugin list

# Update a plugin
honeyaegis plugin update community-ftp-honeypot

# Update all plugins
honeyaegis plugin update --all

# Uninstall a plugin
honeyaegis plugin uninstall community-ftp-honeypot
```

## Publishing a Plugin

Submit your plugin to the community registry:

1. Ensure your plugin passes validation: `honeyaegis plugin validate .`
2. Host the source code on a public GitHub repository with an MIT or compatible license.
3. Submit via the API or open a pull request to the [plugin registry](https://github.com/thesecretchief/honeyaegis-plugins).

```bash
curl -X POST http://localhost:8000/api/v1/marketplace/submit \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "my-plugin",
    "description": "Plugin description",
    "repository": "https://github.com/user/my-plugin",
    "category": "enrichment"
  }'
```

Submissions are reviewed for security and quality before appearing in the marketplace.

## Related Pages

- [Plugin Development](development.md) -- Build your own plugins
- [Plugin Examples](examples.md) -- Example plugin code
- [Configuration](../getting-started/configuration.md) -- Plugin environment variables
