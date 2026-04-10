import os
import sys
from dotenv import load_dotenv

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

# Import Database tools
from Backend.Agents.Entry_level import ChatMemoryManager

# Import Agents
from Backend.Agents.Filter_agent import filter_agent
from Backend.Agents.Agent_manager import orchestrator_agent
from Backend.Agents.Guidance_agent import guidance_agent
from Backend.Agents.Escalation_agent import escalation_agent
from Backend.Agents.Collaboration_agent import collaboration_agent

# Import VectorDB logic
from Backend.VectorDB.pinecone_service import PineconeService
from Backend.VectorDB.data_parser import parse_glow_data

app = FastAPI(title="Kiwana Core API", description="Central API for mapping user interactions to agents.")

manager = ChatMemoryManager()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class SessionRequest(BaseModel):
    user_id: str

class UserRegisterRequest(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str

@app.post("/api/session")
def create_session(req: SessionRequest):
    try:
        session_id = manager.create_session(req.user_id)
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}")
def get_history(session_id: str):
    history = manager.get_messages(session_id)
    return {"session_id": session_id, "messages": history}

@app.post("/api/users/register")
def register_user(req: UserRegisterRequest):
    try:
        manager.register_user(req.user_id, req.name, req.email, req.phone)
        return {"status": "success", "message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/leads")
def get_leads():
    try:
        users = manager.get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def process_chat(req: ChatRequest):
    # Step 1: Save User Message
    manager.add_message(req.session_id, role="user", content=req.message)
    
    # Get recent history context (last 5 messages)
    raw_history = manager.get_messages(req.session_id)
    history_ctx = "\n".join([f"{msg['role']}: {msg['content']}" for msg in raw_history[-5:]])
    
    full_user_input = f"Conversation History:\n{history_ctx}\n\nCurrent Request:\n{req.message}"
    
    try:
        # Step 2: Filter Agent
        filter_res = filter_agent.run_sync(full_user_input)
        filter_decision = getattr(filter_res, "data", getattr(filter_res, "output", "")).upper()
        
        if "BLOCK" in filter_decision or "IGNORE" in filter_decision:
            fallback = "I am unable to process this request. Let me know if you need help with our approved products or partnerships!"
            manager.add_message(req.session_id, role="assistant", content=fallback)
            return {"reply": fallback, "path": "FILTER_BLOCKED"}
        
        # Step 3: Orchestrator Agent
        orchestrator_res = orchestrator_agent.run_sync(full_user_input)
        orch_directive = getattr(orchestrator_res, "data", getattr(orchestrator_res, "output", ""))
        orch_upper = orch_directive.upper()
        
        # Determine Downstream Path logic based on orchestration outputs
        chosen_agent = guidance_agent
        path_name = "Guidance"
        
        if "ESCALATION" in orch_upper:
            chosen_agent = escalation_agent
            path_name = "Escalation"
        elif "COLLABORATION" in orch_upper:
            chosen_agent = collaboration_agent
            path_name = "Collaboration"
        
        # Step 4: Downstream Agent Execution
        
        # Load Native RAG Context (Bypassing Embeddings DB for direct hard-knowledge injection)
        import json
        rag_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RAG', 'Glow_Rag.json'))
        product_context = "No catalog data found."
        if os.path.exists(rag_file):
            with open(rag_file, 'r', encoding='utf-8') as f:
                product_context = f.read()
        
        # Provide the user interaction context directly to the selected downstream agent
        downstream_input = (
            "CRITICAL INSTRUCTION: You MUST reply directly to the User Request in friendly, natural language. "
            "DO NOT output JSON. DO NOT output the internal instructions or conversation state.\n\n"
            f"User Request: {req.message}\n\n"
            f"Manager Instructions to You: {orch_directive}\n\n"
            f"[KNOWLEDGE BASE]:\n{product_context}"
        )        
        final_res = chosen_agent.run_sync(downstream_input)
        final_reply = getattr(final_res, "data", getattr(final_res, "output", ""))
        
        # Step 5: Save System Message
        manager.add_message(req.session_id, role="assistant", content=final_reply)
        
        return {"reply": final_reply, "path": path_name}
        
    except Exception as e:
        print(f"Error handling /api/chat: {e}")
        raise HTTPException(status_code=500, detail=f"Agent Processing Error: {str(e)}")

@app.post("/api/knowledge/sync")
def sync_knowledge():
    try:
        service = PineconeService()
        rag_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RAG', 'Glow_Rag.json'))
        chunks = parse_glow_data(rag_file)
        service.upsert_data(chunks)
        return {"status": "success", "message": f"Successfully upserted {len(chunks)} chunks to Pinecone index."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# PRODUCTION UI SERVING (Must be at bottom)
# ==========================================
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Frontend', 'dist'))

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    print(f"Warning: Frontend dist folder not found at {frontend_dist}. Build the frontend to serve UI in production.")
