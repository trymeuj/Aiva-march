# app.py
import os
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Import our custom components
from api_knowledge_base import APIKnowledgeBase
from ai_agent import AIAgent

# Initialize FastAPI app
app = FastAPI(title="AI API Assistant")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API knowledge base
api_knowledge_base = APIKnowledgeBase()

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)

# Store agent instances per session
agent_instances = {}

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    print("No static directory found. Skipping static files serving.")

@app.get("/")
async def get_home():
    """Serve the home page"""
    try:
        return FileResponse("static/index.html")
    except:
        return {"message": "Welcome to AI API Assistant. Connect via WebSocket to /ws/{session_id}"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Handle WebSocket connections for chat sessions"""
    await websocket.accept()
    
    # Create or get an agent instance for this session
    if session_id not in agent_instances:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a new agent instance
        agent_instances[session_id] = AIAgent(
            api_knowledge_base=api_knowledge_base,
            model=model
        )
    
    agent = agent_instances[session_id]
    
    try:
        # Send welcome message
        await websocket.send_json({
            "text": "Hello! How can I help you today?",
            "state": "idle"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                user_text = message.get("text", "")
            except json.JSONDecodeError:
                # If not JSON, treat the entire text as user input
                user_text = data
            
            # Process user input
            try:
                response = await agent.process_user_input(user_text)
                
                # Send response back to client
                await websocket.send_json({
                    "text": response,
                    "state": agent.current_state,
                    # Include additional context for frontend if needed
                    "context": {
                        "intent": agent.current_intent,
                        "execution_plan": agent.execution_plan,
                        "parameters": agent.collected_parameters
                    } if agent.current_state == "confirming_execution" else {}
                })
            except Exception as e:
                # Handle errors during processing
                error_message = f"Sorry, I encountered an error: {str(e)}"
                await websocket.send_json({
                    "text": error_message,
                    "state": "error"
                })
                # Reset agent state
                agent.current_state = "idle"
                
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")

@app.get("/api/knowledge")
async def get_api_knowledge():
    """Endpoint to retrieve API knowledge base summary for the frontend"""
    return {
        "apis": api_knowledge_base.get_endpoint_summaries(),
        "capabilities": api_knowledge_base.get_capability_summary()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "AI API Assistant"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)