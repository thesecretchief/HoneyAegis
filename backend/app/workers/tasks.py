"""Background tasks for log ingestion, enrichment, and alerting."""

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="ingest_cowrie_logs")
def ingest_cowrie_logs(log_path: str) -> dict:
    """Ingest Cowrie JSON logs from the specified path."""
    from app.services.cowrie_parser import parse_cowrie_log_file

    events = parse_cowrie_log_file(log_path)
    return {"status": "ok", "events_parsed": len(events)}


@celery_app.task(name="enrich_session_geoip")
def enrich_session_geoip(session_id: str, src_ip: str) -> dict:
    """Enrich a session with GeoIP data."""
    import asyncio
    from app.services.geoip_service import lookup_ip

    loop = asyncio.new_event_loop()
    try:
        geo = loop.run_until_complete(lookup_ip(src_ip))
    finally:
        loop.close()
    return {"status": "ok", "session_id": session_id, "geo": geo}


@celery_app.task(name="enrich_session_abuseipdb")
def enrich_session_abuseipdb(session_id: str, src_ip: str) -> dict:
    """Enrich a session with AbuseIPDB reputation data."""
    import asyncio
    from app.services.abuseipdb_service import lookup_abuse_score

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(lookup_abuse_score(src_ip))
    finally:
        loop.close()
    return {"status": "ok", "session_id": session_id, "abuse": result}


@celery_app.task(name="send_session_alert")
def send_session_alert(session_data: dict) -> dict:
    """Send alert notification for a new honeypot session."""
    from app.services.alert_service import send_alert, format_session_alert

    title, body = format_session_alert(session_data)
    success = send_alert(title, body, notify_type="warning")
    return {"status": "sent" if success else "failed", "title": title}


@celery_app.task(name="send_malware_alert")
def send_malware_alert(download_data: dict) -> dict:
    """Send alert notification for captured malware."""
    from app.services.alert_service import send_alert, format_malware_alert

    title, body = format_malware_alert(download_data)
    success = send_alert(title, body, notify_type="failure")
    return {"status": "sent" if success else "failed", "title": title}
