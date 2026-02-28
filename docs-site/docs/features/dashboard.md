# Real-Time Dashboard

The HoneyAegis dashboard provides a live operational view of all honeypot activity across your sensors.

## Overview

The dashboard is built with Next.js 15 (App Router), Tailwind CSS, and shadcn/ui components. It connects to the backend via WebSocket for real-time event streaming with zero polling.

## Dashboard Panels

### Live Attack Map

An interactive Leaflet map showing attack origins in real time. Each marker is color-coded by risk score:

- **Green (0-3)** -- Low-risk activity (scanners, bots)
- **Yellow (4-6)** -- Medium-risk activity (credential brute-force)
- **Red (7-10)** -- High-risk activity (malware deployment, lateral movement)

### Session Timeline

A chronological feed of active and recent sessions with:

- Source IP and GeoIP country flag
- Protocol (SSH, Telnet, HTTP, SMB)
- Command count and duration
- AI-generated summary (if Ollama is enabled)
- Risk score badge

### Statistics Cards

Summary cards across the top of the dashboard:

| Card | Description |
|---|---|
| **Active Sessions** | Currently connected attackers |
| **Sessions (24h)** | Total sessions in the last 24 hours |
| **Unique IPs (24h)** | Distinct source IPs |
| **Malware Captures** | Files captured by Dionaea |
| **Alerts Sent** | Notifications dispatched today |

### Attack Trends Chart

A Recharts time-series chart showing session volume over the last 7 days, broken down by protocol.

## WebSocket Connection

The frontend establishes a WebSocket connection on page load:

```typescript
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    switch (message.type) {
        case "new_session":
            addSession(message.data);
            break;
        case "session_update":
            updateSession(message.data);
            break;
        case "alert":
            showNotification(message.data);
            break;
    }
};
```

## Dark Mode

The dashboard supports both dark and light themes, toggled via the theme switcher in the navigation bar. The default theme is dark (slate).

## Filtering and Search

- Filter sessions by protocol, country, risk score, or time range
- Full-text search across commands, IP addresses, and AI summaries
- Save custom filter presets per user

## Internationalization

The dashboard is available in five languages: English, Spanish, German, French, and Greek. Set the language in user preferences or via the `HONEYAEGIS_LOCALE` environment variable.

## Related Pages

- [Data Flow](../architecture/data-flow.md) -- How events reach the dashboard
- [Session Replay](session-replay.md) -- Replay captured sessions
- [Configuration](../getting-started/configuration.md) -- Dashboard environment variables
