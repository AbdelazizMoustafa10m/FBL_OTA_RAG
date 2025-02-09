from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from agent_setup import setup_agent

# Create API router
from fastapi import APIRouter

app = APIRouter(
    prefix="/api/v1",
    tags=["query"]
)

# Initialize the agent
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        try:
            _agent = setup_agent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    return _agent

class Query(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class Response(BaseModel):
    answer: str
    conversation_id: Optional[str]
    error: Optional[str] = None

@app.post("/query", response_model=Response)
async def query_documents(query: Query):
    try:
        # Get agent instance
        agent = get_agent()
        # Get response from agent
        response = agent.query(query.question)
        
        # Format the response
        formatted_response = format_response(response)
        
        return Response(
            answer=formatted_response,
            conversation_id=query.conversation_id,
            error=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

def format_response(response):
    """Format the response from the agent"""
    if not response:
        return "No relevant information found. Please try rephrasing your question."
    
    # Remove markdown-style formatting and clean up the text
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', str(response))
    
    # Format numbered points if they exist
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if re.match(r'^\d+\.', line):
            parts = line.split(': ', 1)
            if len(parts) > 1:
                number, content = parts
                formatted_lines.append(f"{number} {content}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)