# Session Replay

HoneyAegis captures full TTY sessions from SSH and Telnet honeypots and provides a browser-based terminal replay.

## How It Works

1. **Cowrie** records every keystroke and terminal output in its native `ttylog` format.
2. The backend converts `ttylog` files into a JSON timeline of terminal frames.
3. The frontend renders the replay in a browser-based terminal emulator (xterm.js) with play/pause controls.
4. Optionally, sessions can be exported as MP4 video or animated GIF for reports and presentations.

## Viewing a Session Replay

Navigate to **Sessions** in the dashboard, then click any session row to open the detail view. The **Replay** tab shows the terminal player.

### Player Controls

| Control | Description |
|---|---|
| Play / Pause | Start or pause the replay |
| Speed (1x, 2x, 4x, 8x) | Adjust playback speed |
| Timeline scrubber | Jump to any point in the session |
| Fullscreen | Expand the terminal to fullscreen |
| Download | Export as MP4, GIF, or raw ttylog |

## Video Export

Sessions can be converted to video formats for sharing or archiving:

```bash
# Export via the API
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/export \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "mp4", "speed": 2}'
```

Supported export formats:

| Format | Use Case | Size |
|---|---|---|
| **MP4** | Reports, presentations | ~2 MB/min |
| **GIF** | Embedding in tickets, Slack | ~5 MB/min |
| **asciicast** | asciinema-compatible playback | ~50 KB/min |
| **ttylog** | Raw Cowrie format for re-analysis | ~20 KB/min |

Video conversion runs as a Celery background task. Large sessions may take 10-30 seconds to render.

## Session Metadata

Each session replay includes a metadata panel showing:

- Source IP, port, and GeoIP location
- Session start/end time and duration
- Authentication attempts (username/password pairs)
- Commands executed with timestamps
- Risk score and AI summary
- Threat intelligence hits (if configured)

## Configuration

```bash
# Enable automatic MP4 generation for all sessions
SESSION_AUTO_EXPORT=true
SESSION_EXPORT_FORMAT=mp4
SESSION_EXPORT_SPEED=4

# Maximum session recording length (seconds)
SESSION_MAX_DURATION=3600
```

## Related Pages

- [Dashboard](dashboard.md) -- Live session monitoring
- [Sessions API](../api/sessions.md) -- Programmatic session access
- [AI Analysis](ai-analysis.md) -- AI-generated session summaries
