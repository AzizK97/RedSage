import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agent.supervisor import supervisor

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "test_thread"  # Default for testing

class ChatResponse(BaseModel):
    response: str
    interrupts: Dict[str, Any] = {}  
    requires_human: bool = False

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        # Invoke supervisor
        result = supervisor.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config,
        )
        
        # Check HITL interrupt (write tool POST)
        if hasattr(result, 'interrupts') and result.interrupts:
            pending = result.interrupts[0].value
            first_action = pending['action_requests'][0]
            
            return ChatResponse(
                response="Paused for approval",
                interrupts=pending,
                requires_human=True
            )
        
        # Normal response
        response_msg = result["messages"][-1].content
        return ChatResponse(response=response_msg)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve/{thread_id}")
async def approve(thread_id: str, decision_type: str = "approve"):
    """
    Resume after HITL approval.
    POST /approve/test_thread?decision_type=approve
    Or POST /approve/test_thread?decision_type=reject&message="Too risky"
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Build decision (approve/edit/reject)
    decision = {"type": decision_type}
    if decision_type == "reject":
        decision["message"] = "Request denied"  # Optional feedback
    
    # Resume execution
    final_result = supervisor.invoke(
        Command(resume={"decisions": [decision]}),
        config,
    )
    
    response_msg = final_result["messages"][-1].content
    return {"status": "approved", "final_response": response_msg}

# Test endpoints
@app.get("/test")
async def test_chat():
    """Test full flow: chat → HITL → approve"""
    config = {"configurable": {"thread_id": "test1"}}
    
    # Step 1: Trigger write (should interrupt)
    result1 = supervisor.invoke(
        {"messages": [HumanMessage(content="Planning: create new sprint 'Sprint 42' in project 1")]},
        config,
    )
    
    if result1.interrupts:
        print("✅ HITL triggered:", result1.interrupts[0].value["action_requests"])
        
        # Step 2: Simulate approve
        result2 = supervisor.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config,
        )
        print("✅ Approved:", result2["messages"][-1].content)
        return {"success": True, "response": result2["messages"][-1].content}
    
    return {"message": "No interrupt (no write tool called)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)