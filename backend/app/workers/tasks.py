"""Background tasks for log ingestion and processing."""

from app.workers.celery_app import celery_app


@celery_app.task(name="ingest_cowrie_logs")
def ingest_cowrie_logs(log_path: str) -> dict:
    """Ingest Cowrie JSON logs from the specified path."""
    from app.services.cowrie_parser import parse_cowrie_log_file

    events = parse_cowrie_log_file(log_path)
    return {"status": "ok", "events_parsed": len(events)}


@celery_app.task(name="enrich_session_geoip")
def enrich_session_geoip(session_id: str, src_ip: str) -> dict:
    """Enrich a session with GeoIP data (stub for Iteration 1)."""
    return {"status": "stub", "session_id": session_id, "src_ip": src_ip}
