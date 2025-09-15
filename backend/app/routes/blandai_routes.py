from fastapi import APIRouter, Depends, Body, HTTPException, status, WebSocket, WebSocketDisconnect
from app.schemas import MakeCallRequest, CallDetailRequest
from app.services.blandai_service import make_call, end_call, get_call_transcript, get_call_status
import logging
from rich import print
import asyncio
import json
from typing import Dict, Set

router = APIRouter(prefix="/api", tags=["BlandAI"])

# Store active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}

@router.post("/assistant-initiate-call")
async def make_call_route(request: MakeCallRequest):
    try:
        print(f"Initiating call with request: {request.__dict__}")
        
        result = make_call(
            objective=request.objective,
            context=request.context,
            caller_number=request.caller_number,
            caller_name=request.caller_name,
            caller_email=request.caller_email,
            phone_number=request.phone_number,
            language_code=request.language_code,
            name_of_org=request.name_of_org
        )
        
        # Return consistent response structure
        return {
            "call_sid": result.get("call_id") or result.get("call_sid"),
            "status": "initiated",
            "message": "Call initiated successfully"
        }
        
    except Exception as error:
        logging.error(f"Error in make_call_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to initiate call: {str(error)}"
        )

@router.get("/call-status/{call_id}")
async def call_status_route(call_id: str):
    try:
        result = get_call_status(call_id)
        return {
            "call_id": call_id,
            "status": result.get("status", "unknown"),
            "data": result
        }
    except Exception as error:
        logging.error(f"Error in call_status_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get call status: {str(error)}"
        )

@router.get("/call-transcript/{call_id}")
async def call_transcript_route(call_id: str):
    try:
        result = get_call_transcript(call_id)
        return {
            "call_id": call_id,
            "transcript": result.get("transcript", ""),
            "data": result
        }
    except Exception as error:
        logging.error(f"Error in call_transcript_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transcript: {str(error)}"
        )

@router.post("/end-call/{call_id}")
async def end_call_route(call_id: str):
    try:
        result = end_call(call_id)
        
        # Notify all WebSocket connections for this call
        await notify_call_ended(call_id, result)
        
        return {
            "call_id": call_id,
            "status": "ended",
            "message": "Call ended successfully",
            "data": result
        }
    except Exception as error:
        logging.error(f"Error in end_call_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end call: {str(error)}"
        )

async def notify_call_ended(call_id: str, data: dict):
    """Notify all WebSocket connections that a call has ended"""
    if call_id in active_connections:
        message = {
            "event": "call_ended",
            "call_id": call_id,
            "email_send": True,  # Adjust based on your logic
            "call_duration": data.get("duration", "Unknown"),
            "data": data
        }
        
        # Create a copy of connections to avoid modification during iteration
        connections = list(active_connections[call_id])
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logging.error(f"Failed to send message to WebSocket: {e}")
                # Remove failed connection
                active_connections[call_id].discard(websocket)
        
        # Clean up if no connections left
        if not active_connections[call_id]:
            del active_connections[call_id]

@router.websocket("/ws/live-transcript")
async def websocket_live_transcript(websocket: WebSocket):
    await websocket.accept()
    call_id = None
    
    try:
        # Wait for initial message with call_id
        initial_data = await websocket.receive_text()
        initial_message = json.loads(initial_data)
        
        if initial_message.get("event") == "start":
            call_id = initial_message.get("call_sid")
            if not call_id:
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "message": "call_sid is required"
                }))
                return
            
            # Add connection to active connections
            if call_id not in active_connections:
                active_connections[call_id] = set()
            active_connections[call_id].add(websocket)
            
            # Send confirmation
            await websocket.send_text(json.dumps({
                "event": "connected",
                "call_id": call_id
            }))
            
            # Start monitoring the call
            await monitor_call_transcript(websocket, call_id)
        else:
            await websocket.send_text(json.dumps({
                "event": "error",
                "message": "Expected 'start' event with call_sid"
            }))
            
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for call_id: {call_id}")
    except Exception as error:
        logging.error(f"Error in websocket_live_transcript: {error}")
        await websocket.send_text(json.dumps({
            "event": "error",
            "message": str(error)
        }))
    finally:
        # Clean up connection
        if call_id and call_id in active_connections:
            active_connections[call_id].discard(websocket)
            if not active_connections[call_id]:
                del active_connections[call_id]
        await websocket.close()

async def monitor_call_transcript(websocket: WebSocket, call_id: str):
    """Monitor call transcript and send updates via WebSocket"""
    last_transcript = ""
    last_status = ""
    
    try:
        while True:
            # Check call status first
            status_data = get_call_status(call_id)
            current_status = status_data.get("status", "")
            
            # If call is completed, send final message and break
            if current_status in ["completed", "ended", "failed"]:
                await websocket.send_text(json.dumps({
                    "event": "call_ended",
                    "call_id": call_id,
                    "status": current_status,
                    "email_send": True,  # Adjust based on your logic
                    "call_duration": status_data.get("duration", "Unknown")
                }))
                break
            
            # Send status updates
            if current_status != last_status and current_status:
                await websocket.send_text(json.dumps({
                    "event": "call_status",
                    "call_id": call_id,
                    "status": current_status
                }))
                last_status = current_status
            
            # Get and send transcript updates
            transcript_data = get_call_transcript(call_id)
            transcript_text = transcript_data.get("transcript", "")
            
            if transcript_text and transcript_text != last_transcript:
                await websocket.send_text(json.dumps({
                    "event": "call_in_process",
                    "call_id": call_id,
                    "transcription": transcript_text
                }))
                last_transcript = transcript_text
            
            # Send periodic ping to keep connection alive
            await websocket.send_text(json.dumps({
                "event": "ping",
                "timestamp": asyncio.get_event_loop().time()
            }))
            
            await asyncio.sleep(2)  # Poll every 2 seconds
            
    except Exception as error:
        logging.error(f"Error monitoring call {call_id}: {error}")
        await websocket.send_text(json.dumps({
            "event": "error",
            "message": str(error)
        }))