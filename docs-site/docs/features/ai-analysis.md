# AI Threat Analysis

HoneyAegis uses Ollama to run a local LLM that generates threat summaries for captured sessions. All inference runs on your hardware -- no data leaves your network.

## Overview

When a honeypot session ends, a Celery worker sends the session transcript to Ollama for analysis. The LLM produces:

- A plain-language summary of attacker behavior
- MITRE ATT&CK technique mapping
- A risk score (0-10)
- Recommended response actions

## Enabling AI Analysis

AI analysis requires the full profile with Ollama:

```bash
# Enable in .env
OLLAMA_ENABLED=true
OLLAMA_MODEL=phi3:mini

# Deploy with full profile
docker compose --profile full up -d
```

On first startup, Ollama automatically pulls the configured model. The `phi3:mini` model requires approximately 1.5 GB of RAM during inference.

## Supported Models

| Model | Size | Speed | Quality | RAM |
|---|---|---|---|---|
| `phi3:mini` | 2.3 GB | Fast | Good | 1.5 GB |
| `llama3.1:8b` | 4.7 GB | Medium | Better | 4 GB |
| `mistral:7b` | 4.1 GB | Medium | Better | 4 GB |
| `gemma2:9b` | 5.4 GB | Slow | Best | 6 GB |

Change the model in `.env`:

```bash
OLLAMA_MODEL=llama3.1:8b
```

## Example AI Summary

For a session where an attacker performs reconnaissance:

```json
{
    "summary": "The attacker connected via SSH using brute-forced credentials (root/admin123), then performed system reconnaissance by examining OS version, network interfaces, and running processes. They attempted to download a cryptominer from a known malicious domain but the connection was blocked by the honeypot sandbox.",
    "mitre_techniques": [
        "T1078 - Valid Accounts",
        "T1082 - System Information Discovery",
        "T1016 - System Network Configuration Discovery",
        "T1496 - Resource Hijacking"
    ],
    "risk_score": 7.5,
    "recommended_actions": [
        "Block source IP at firewall",
        "Check for compromised credentials matching root/admin123",
        "Monitor for connections to the C2 domain"
    ]
}
```

## Custom Prompts

You can customize the analysis prompt via the configuration API:

```bash
curl -X PUT http://localhost:8000/api/v1/config/ai-prompt \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "You are a senior SOC analyst. Analyze this honeypot session transcript and provide a threat assessment.",
    "output_format": "structured_json"
  }'
```

## Performance Considerations

- AI analysis runs asynchronously and does not block session capture.
- On a 4-core CPU, `phi3:mini` processes a typical session in 2-5 seconds.
- GPU acceleration is supported if Ollama detects a compatible NVIDIA GPU.
- Sessions longer than 4096 tokens are truncated with a summary of omitted content.

## Related Pages

- [Configuration](../getting-started/configuration.md) -- Ollama environment variables
- [Data Flow](../architecture/data-flow.md) -- Where AI fits in the enrichment pipeline
- [Session Replay](session-replay.md) -- View sessions alongside AI summaries
