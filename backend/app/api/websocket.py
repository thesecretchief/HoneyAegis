"""WebSocket endpoint for real-time event broadcasting."""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

# Connected WebSocket clients
_clients: set[WebSocket] = set()


async def broadcast_event(data: dict):
    """Broadcast an event to all connected WebSocket clients."""
    if not _clients:
        return

    message = json.dumps(data)
    disconnected = set()

    for ws in _clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)

    _clients.difference_update(disconnected)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time dashboard updates."""
    await websocket.accept()
    _clients.add(websocket)
    logger.info("WebSocket client connected (%d total)", len(_clients))

    try:
        while True:
            # Keep connection alive, handle client messages (e.g., pings)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(websocket)
        logger.info("WebSocket client disconnected (%d remaining)", len(_clients))
