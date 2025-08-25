#!/usr/bin/env python3
"""
FastAPI server to integrate NPCI Grievance Bot with OpenWebUI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import uvicorn
import json
from datetime import datetime
from finance_bot import NPCIGrievanceBot

app = FastAPI(title="NPCI Grievance Bot API", version="1.0.0")

# Add CORS middleware for OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NPCI Grievance Bot
npci_bot = NPCIGrievanceBot()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]

@app.get("/v1/models")
async def list_models():
    """List available models for OpenWebUI"""
    return {
        "object": "list",
        "data": [
            {
                "id": "npci-grievance-bot",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "npci-nemo-guardrails",
                "permission": [],
                "root": "npci-grievance-bot",
                "parent": None,
            },
            {
                "id": "upi-support-bot",
                "object": "model", 
                "created": int(datetime.now().timestamp()),
                "owned_by": "npci-nemo-guardrails",
                "permission": [],
                "root": "upi-support-bot",
                "parent": None,
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Handle chat completions from OpenWebUI with context retention and streaming support"""
    try:
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_user_message = user_messages[-1].content
        
        # Build conversation history for context
        conversation_history = []
        for msg in request.messages[:-1]:  # All messages except the last one
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Check if streaming is requested
        if request.stream:
            return await handle_streaming_request(request, last_user_message, conversation_history)
        else:
            return await handle_non_streaming_request(request, last_user_message, conversation_history)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_streaming_request(request: ChatRequest, last_user_message: str, conversation_history: List[Dict]):
    """Handle streaming chat completions"""
    
    async def generate_stream():
        try:
            # Stream through NPCI Grievance Bot
            async for chunk in npci_bot.stream_message(
                user_message=last_user_message,
                user_id="webui_user", 
                conversation_history=conversation_history
            ):
                # Format chunk according to OpenAI streaming format
                chunk_data = {
                    "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                    "object": "chat.completion.chunk",
                    "created": int(datetime.now().timestamp()),
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": chunk
                            },
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # Send final chunk with finish_reason
            final_chunk = {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion.chunk", 
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # Send error in streaming format
            error_chunk = {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion.chunk",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": f"Error: {str(e)}"
                        },
                        "finish_reason": "stop"
                    }
                ]
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

async def handle_non_streaming_request(request: ChatRequest, last_user_message: str, conversation_history: List[Dict]):
    """Handle non-streaming chat completions (original behavior)"""
    
    # Process through NPCI Grievance Bot with context
    response = await npci_bot.process_message(
        user_message=last_user_message, 
        user_id="webui_user",
        conversation_history=conversation_history
    )
    
    if not response.get("success"):
        raise HTTPException(status_code=500, detail=response.get("error", "Unknown error"))
    
    bot_response = response.get("response", "I'm sorry, I couldn't generate a response.")
    
    # Add context information to metadata
    metadata = response.get("metadata", {})
    context_messages = metadata.get('context_messages', 1)
    has_context = metadata.get('has_conversation_history', False)
    
    # Add subtle context indicator to response if there's conversation history
    if has_context and context_messages > 1:
        # Don't modify the actual response, just log it
        print(f"🧠 Processing with {context_messages} messages of context")
    
    # Format response for OpenWebUI
    return ChatResponse(
        id=f"chatcmpl-{int(datetime.now().timestamp())}",
        created=int(datetime.now().timestamp()),
        model=request.model,
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": bot_response
                },
                "finish_reason": "stop"
            }
        ]
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test bot initialization
        test_response = await npci_bot.process_message("health check", "health_user")
        return {
            "status": "healthy", 
            "service": "NPCI Grievance Bot API",
            "bot_status": "operational" if test_response.get("success") else "degraded"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "NPCI Grievance Bot API", 
            "error": str(e)
        }

@app.get("/npci/services")
async def list_npci_services():
    """List supported NPCI services"""
    return {
        "services": [
            {
                "name": "UPI",
                "description": "Unified Payments Interface - Instant payment system",
                "issues": ["Transaction failures", "Money debited but payment failed", "UPI ID issues", "Transaction limits"]
            },
            {
                "name": "RuPay", 
                "description": "India's domestic payment network for cards",
                "issues": ["Card not working", "Transaction declined", "International usage", "Reward points"]
            },
            {
                "name": "NACH",
                "description": "National Automated Clearing House for bulk payments", 
                "issues": ["Mandate failures", "Payment bounces", "Auto-debit issues", "Mandate cancellation"]
            },
            {
                "name": "IMPS",
                "description": "Immediate Payment Service for instant money transfer",
                "issues": ["Transfer failed", "Beneficiary issues", "Transaction limits", "Service unavailable"]
            },
            {
                "name": "NETC/FASTag",
                "description": "National Electronic Toll Collection",
                "issues": ["FASTag not working", "Double deduction", "Balance issues", "Blacklist issues"]
            },
            {
                "name": "BBPS",
                "description": "Bharat Bill Payment System", 
                "issues": ["Bill payment failed", "Duplicate payments", "Biller not available", "Receipt issues"]
            }
        ]
    }

@app.post("/npci/grievance")
async def create_npci_grievance(
    user_id: str,
    category: str,
    description: str,
    priority: str = "medium",
    service_type: str = "general"
):
    """Create a new NPCI grievance directly"""
    try:
        result = await npci_bot.create_grievance(
            user_id=user_id,
            category=category,
            description=description,
            priority=priority
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/npci/faq/{query_type}")
async def get_npci_faq(query_type: str):
    """Get NPCI FAQ information"""
    try:
        result = await npci_bot.get_npci_faq(query_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "NPCI Grievance Bot API",
        "version": "1.0.0",
        "description": "NeMoGuardrails NPCI Grievance Bot integration for OpenWebUI",
        "bot_type": "NPCI Service Assistant",
        "supported_services": ["UPI", "RuPay", "NACH", "IMPS", "NETC/FASTag", "BBPS"],
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions", 
            "health": "/health",
            "services": "/npci/services",
            "grievance": "/npci/grievance",
            "faq": "/npci/faq/{query_type}"
        },
        "integration": {
            "openwebui_url": "http://host.docker.internal:8087/v1",
            "local_url": "http://localhost:8087"
        }
    }

if __name__ == "__main__":
    print("🏛️ Starting NPCI Grievance Bot API server...")
    print("📊 This will integrate your NeMoGuardrails NPCI Bot with OpenWebUI")
    print("🔗 API will be available at: http://localhost:8087")
    print("📋 OpenWebUI can connect to: http://host.docker.internal:8087/v1")
    print()
    print("🎯 Supported NPCI Services:")
    print("   • UPI - Payment issues and transaction failures")
    print("   • RuPay - Card-related problems")
    print("   • NACH - Mandate and auto-debit issues") 
    print("   • IMPS - Instant transfer problems")
    print("   • NETC/FASTag - Toll payment issues")
    print("   • BBPS - Bill payment problems")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8087,
        log_level="info"
    )