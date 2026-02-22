"""WebSocket endpoints for real-time updates."""

from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger
import json

from app.api.dependencies import get_current_user_from_token


router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # user_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for dead_conn in dead_connections:
                self.active_connections[user_id].discard(dead_conn)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time updates.
    
    Usage:
        ws://localhost:8000/ws?token=<access_token>
    
    Message formats:
        - Report status update: {"type": "report_status", "report_id": "...", "status": "..."}
        - Schedule trigger: {"type": "schedule_trigger", "schedule_id": "..."}
        - Error: {"type": "error", "message": "..."}
    """
    user = None
    
    try:
        # Authenticate using token from query parameter
        if token:
            user = await get_current_user_from_token(token)
        
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        await manager.connect(websocket, str(user.id))
        
        try:
            while True:
                # Receive messages from client (for ping/pong or client requests)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                # Add more message handlers as needed
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, str(user.id))
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket, str(user.id))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")


async def notify_report_status(user_id: str, report_id: str, status: str, error: str = None):
    """
    Notify user about report status change.
    
    Args:
        user_id: User ID to notify
        report_id: Report ID
        status: New status
        error: Error message if failed
    """
    message = {
        "type": "report_status",
        "report_id": report_id,
        "status": status,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    if error:
        message["error"] = error
    
    await manager.send_personal_message(message, user_id)


async def notify_schedule_trigger(user_id: str, schedule_id: str, report_id: str):
    """
    Notify user about schedule trigger.
    
    Args:
        user_id: User ID to notify
        schedule_id: Schedule ID
        report_id: Generated report ID
    """
    message = {
        "type": "schedule_trigger",
        "schedule_id": schedule_id,
        "report_id": report_id,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    await manager.send_personal_message(message, user_id)
