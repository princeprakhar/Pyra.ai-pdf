

from fastapi import APIRouter, Depends, Body, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from app.schemas import MakeCallRequest, CallDetailRequest
from app.services.blandai_service import (
    blandai_service, make_call, end_call, get_call_transcript, get_call_status
)
import logging
from rich import print
import asyncio
import json
from typing import Dict, Set, Optional, List
from datetime import datetime

router = APIRouter(prefix="/api", tags=["BlandAI"])

# Store active WebSocket connections and call metadata
active_connections: Dict[str, Set[WebSocket]] = {}
call_metadata: Dict[str, Dict] = {}
class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, call_id: str):
        # Don't accept here - already accepted in main function
        if call_id not in self.active_connections:
            self.active_connections[call_id] = set()
        self.active_connections[call_id].add(websocket)
        logging.info(f"WebSocket connected for call_id: {call_id}. Total connections: {len(self.active_connections[call_id])}")

    def disconnect(self, websocket: WebSocket, call_id: str):
        if call_id in self.active_connections:
            self.active_connections[call_id].discard(websocket)
            if not self.active_connections[call_id]:
                del self.active_connections[call_id]
        logging.info(f"WebSocket disconnected for call_id: {call_id}")

    async def send_to_call(self, message: dict, call_id: str):
        if call_id in self.active_connections:
            connections = list(self.active_connections[call_id])
            logging.info(f"Sending message to {len(connections)} connections for call {call_id}")
            for websocket in connections:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logging.error(f"Failed to send message to WebSocket: {e}")
                    self.active_connections[call_id].discard(websocket)

connection_manager = WebSocketConnectionManager()

# SIMPLE WEBHOOK ENDPOINTS (NO SECRET VERIFICATION)

@router.post("/assistant-initiate-call")
async def make_call_route(request: MakeCallRequest):
    """Initiate a new call with simple webhook"""
    try:
        print(f"Initiating call with request: {request.__dict__}")
        
        # Simple webhook URL (replace with your actual domain)
        webhook_url = "https://d10deff31156.ngrok-free.app/api/webhooks/blandai-simple"
        
        result = blandai_service.make_call(
            objective=request.objective,
            context=request.context,
            caller_number=request.caller_number,
            caller_name=request.caller_name,
            caller_email=request.caller_email,
            phone_number=request.phone_number,
            language_code=request.language_code,
            name_of_org=request.name_of_org,
            webhook_url=webhook_url
        )
        
        call_id = result.get("call_id") or result.get("call_sid")
        
        # Store call metadata
        call_metadata[call_id] = {
            "caller_name": request.caller_name,
            "caller_email": request.caller_email,
            "phone_number": request.phone_number,
            "organization": request.name_of_org,
            "started_at": datetime.utcnow().isoformat(),
            "status": "initiated"
        }
        
        return {
            "call_sid": call_id,
            "status": "initiated",
            "message": "Call initiated successfully with webhook",
            "webhook_url": webhook_url
        }
        
    except Exception as error:
        logging.error(f"Error in make_call_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to initiate call: {str(error)}"
        )

@router.post("/webhooks/blandai-simple")
async def simple_webhook_handler(request: Request):
    """Enhanced simple webhook handler with better error handling"""
    try:
        # Get raw body for debugging
        body = await request.body()
        logging.info(f"Raw webhook payload: {body.decode('utf-8')[:500]}...")  # Log first 500 chars
        
        # Parse JSON payload
        payload = await request.json()
        logging.info(f"Parsed webhook payload: {payload}")
        
        # Extract event details with fallbacks
        event_type = payload.get("event") or payload.get("type") or payload.get("event_type")
        call_id = payload.get("call_id") or payload.get("callId") or payload.get("id")
        print(f"Webhook event: {event_type}, call_id: {call_id}")
        # Handle different payload structures from Bland AI
        if not event_type:
            # Try to infer event type from payload structure
            if payload.get("status") == "completed":
                event_type = "call_ended"
            elif payload.get("status") == "in-progress":
                event_type = "call_started"
            elif payload.get("transcript"):
                event_type = "transcript_updated"
            else:
                logging.error(f"Could not determine event type from payload: {payload}")
                return {
                    "status": "error",
                    "message": "Could not determine event type",
                    "received_payload": payload
                }
        print(f"Determined event_type: {event_type}")
        if not call_id:
            logging.error(f"Missing call_id in webhook payload: {payload}")
            return {
                "status": "error", 
                "message": "Missing call_id",
                "received_payload": payload
            }
        
        logging.info(f"🎯 Webhook received: {event_type} for call {call_id}")
        
        # Route to event handlers with enhanced error handling
        try:
            if event_type in ["call_started", "call-started"]:
                await handle_call_started(call_id, payload)
            elif event_type in ["call_ended", "call-ended", "call_completed"]:
                print(f"Handling call ended for call_id: {call_id}")
                await handle_call_ended(call_id, payload)
            elif event_type in ["call_failed", "call-failed"]:
                await handle_call_failed(call_id, payload)
            elif event_type in ["transcript_updated", "transcript-updated", "transcript"]:
                await handle_transcript_updated(call_id, payload)
            elif event_type in ["interruption"]:
                await handle_interruption(call_id, payload)
            else:
                logging.warning(f"Unknown webhook event: {event_type}")
                # Still return success to avoid retries
                
        except Exception as handler_error:
            logging.error(f"Error in webhook handler for {event_type}: {handler_error}")
            # Don't raise - return success to prevent Bland AI retries
        
        return {
            "status": "success", 
            "event": event_type,
            "call_id": call_id,
            "processed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in webhook: {e}")
        logging.error(f"Raw body was: {body.decode('utf-8') if 'body' in locals() else 'Could not get body'}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logging.error(f"Simple webhook error: {e}")
        logging.error(f"Request headers: {dict(request.headers)}")
        raise HTTPException(status_code=500, detail=str(e))
# WEBHOOK EVENT HANDLERS (SIMPLIFIED)

async def handle_call_started(call_id: str, payload: dict):
    """Handle call started event"""
    logging.info(f"📞 Call started: {call_id}")
    
    # Update metadata
    if call_id in call_metadata:
        call_metadata[call_id].update({
            "status": "in_progress",
            "actual_start_time": payload.get("timestamp"),
            "answered_by": payload.get("answered_by")
        })
    
    # Send to WebSocket clients
    await connection_manager.send_to_call({
        "event": "call_started",
        "call_id": call_id,
        "status": "Call started successfully!",
        "timestamp": payload.get("timestamp"),
        "answered_by": payload.get("answered_by", "unknown")
    }, call_id)

async def handle_call_ended(call_id: str, payload: dict):
    """Handle call ended event"""
    logging.info(f"📞 Call ended: {call_id}")
    
    # Update metadata
    if call_id in call_metadata:
        call_metadata[call_id].update({
            "status": "completed",
            "end_time": payload.get("timestamp"),
            "duration": payload.get("duration"),
            "end_reason": payload.get("end_reason")
        })
    
    # Get final transcript
    final_transcript = payload.get("transcripts", "")
    # Send to WebSocket clients
    await connection_manager.send_to_call({
        "event": "call_ended",
        "call_id": call_id,
        "status": "Call completed",
        "final_transcript": final_transcript,
        "duration": payload.get("duration"),
        "end_reason": payload.get("end_reason"),
        "summary": payload.get("summary", ""),
        "timestamp": payload.get("timestamp")
    }, call_id)

async def handle_call_failed(call_id: str, payload: dict):
    """Handle call failed event"""
    logging.error(f"❌ Call failed: {call_id}")
    
    # Update metadata
    if call_id in call_metadata:
        call_metadata[call_id].update({
            "status": "failed",
            "failure_reason": payload.get("failure_reason"),
            "error_code": payload.get("error_code")
        })
    
    # Send to WebSocket clients
    await connection_manager.send_to_call({
        "event": "call_failed",
        "call_id": call_id,
        "status": "Call failed",
        "failure_reason": payload.get("failure_reason"),
        "error_code": payload.get("error_code"),
        "timestamp": payload.get("timestamp")
    }, call_id)

async def handle_transcript_updated(call_id: str, payload: dict):
    """Handle real-time transcript updates - MAIN EVENT!"""
    logging.info(f"📝 Transcript updated for call: {call_id}")
    
    transcript = payload.get("transcript", "")
    
    # Send live transcript to WebSocket clients
    await connection_manager.send_to_call({
        "event": "live_transcript",
        "call_id": call_id,
        "transcript": transcript,
        "speaker": payload.get("speaker", "unknown"),
        "timestamp": payload.get("timestamp"),
        "is_partial": payload.get("is_partial", False)
    }, call_id)

async def handle_interruption(call_id: str, payload: dict):
    """Handle interruption events"""
    logging.info(f"⚠️ Interruption in call: {call_id}")
    
    await connection_manager.send_to_call({
        "event": "interruption",
        "call_id": call_id,
        "interruption_type": payload.get("interruption_type"),
        "timestamp": payload.get("timestamp")
    }, call_id)

# EXISTING ENDPOINTS (Keep as they are)

@router.get("/call-status/{call_id}")
async def call_status_route(call_id: str):
    try:
        result = get_call_status(call_id)
        return {
            "call_id": call_id,
            "status": result.get("status", "unknown"),
            "data": result,
            "metadata": call_metadata.get(call_id, {})
        }
    except Exception as error:
        logging.error(f"Error in call_status_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get call status: {str(error)}"
        )

@router.post("/end-call/{call_id}")
async def end_call_route(call_id: str):
    try:
        result = end_call(call_id)
        
        # Update metadata
        if call_id in call_metadata:
            call_metadata[call_id]["status"] = "ended_manually"
            call_metadata[call_id]["ended_at"] = datetime.utcnow().isoformat()
        
        # Notify WebSocket connections
        await connection_manager.send_to_call({
            "event": "call_ended_manually",
            "call_id": call_id,
            "status": "Call ended by user",
            "timestamp": datetime.utcnow().isoformat()
        }, call_id)
        
        return {
            "call_id": call_id,
            "status": "ended",
            "message": "Call ended successfully"
        }
    except Exception as error:
        logging.error(f"Error in end_call_route: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end call: {str(error)}"
        )

# WEBSOCKET ENDPOINT (Simplified)
@router.websocket("/ws/live-transcript")
async def websocket_live_transcript(websocket: WebSocket):
    """WebSocket for receiving webhook-driven updates"""
    call_id = None
    is_accepted = False
    
    try:
        # Accept connection only once
        if not is_accepted:
            await websocket.accept()
            is_accepted = True
            logging.info("WebSocket connection accepted")
        
        # Wait for connection message
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
            
            # Check if connection already exists for this call
            if call_id in connection_manager.active_connections:
                # Close existing connections for this call to prevent duplicates
                existing_connections = list(connection_manager.active_connections[call_id])
                for existing_ws in existing_connections:
                    try:
                        await existing_ws.close(code=1000, reason="New connection established")
                    except:
                        pass
                connection_manager.active_connections[call_id].clear()
            
            # Connect to manager
            await connection_manager.connect(websocket, call_id)
            
            # Send confirmation
            await websocket.send_text(json.dumps({
                "event": "connected",
                "call_id": call_id,
                "message": "Connected to webhook updates",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Keep connection alive
            try:
                while True:
                    # Wait for messages or send periodic pings
                    try:
                        # Set a timeout for receiving messages
                        message = await asyncio.wait_for(
                            websocket.receive_text(), 
                            timeout=30.0
                        )
                        # Process any incoming messages from client
                        data = json.loads(message)
                        if data.get("event") == "ping":
                            await websocket.send_text(json.dumps({
                                "event": "pong",
                                "timestamp": datetime.utcnow().isoformat()
                            }))
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await websocket.send_text(json.dumps({
                            "event": "ping",
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    except WebSocketDisconnect:
                        break
                        
            except WebSocketDisconnect:
                logging.info(f"WebSocket client disconnected for call_id: {call_id}")
                
        else:
            await websocket.send_text(json.dumps({
                "event": "error",
                "message": "Expected 'start' event with call_sid"
            }))
            
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for call_id: {call_id}")
    except Exception as error:
        logging.error(f"Error in websocket_live_transcript: {error}")
        try:
            if is_accepted:
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "message": str(error)
                }))
        except:
            pass
    finally:
        if call_id:
            connection_manager.disconnect(websocket, call_id)


# UTILITY ENDPOINTS

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "webhook_type": "simple (no secret)",
        "active_connections": len(connection_manager.active_connections),
        "active_calls": len(call_metadata)
    }