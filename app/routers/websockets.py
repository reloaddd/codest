import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis 
from typing import List

router = APIRouter(tags=["Real-time"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass 

manager = ConnectionManager()
listener_task = None 

async def listen_to_redis_channel():
    
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("submission_updates")
        
        print("Started listening to Redis channel: 'submission_updates'...")
        
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                data = message["data"].decode("utf-8")
                await manager.broadcast(f"{data}")
            
            # control back to the event loop
            await asyncio.sleep(0.1)
                
    except asyncio.CancelledError:
        
        print("Redis listener gracefully stopped.")
    except Exception as e:
        print(f"Redis Listener Error: {e}")
    finally:
        await pubsub.unsubscribe("submission_updates")
        await redis_client.close()

@router.on_event("startup")
async def startup_event():
    global listener_task
    # Start the background task
    listener_task = asyncio.create_task(listen_to_redis_channel())

@router.on_event("shutdown")
async def shutdown_event():
    global listener_task
    
    if listener_task:
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass

@router.post("/test-broadcast")
async def test_broadcast():
    
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    test_message = json.dumps({"submission_id": 999, "status": "Test Broadcast Worked!"})
    
    await redis_client.publish("submission_updates", test_message)
    await redis_client.close()
    
    return {"message": "Test broadcast sent to Redis!"}

@router.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)