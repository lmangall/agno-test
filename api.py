from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import os

app = FastAPI(
    title="News Reporter Agent API",
    description="An enthusiastic NYC news reporter powered by AI",
    version="1.0.0"
)

# Request/Response models
class NewsRequest(BaseModel):
    prompt: str
    stream: bool = False

class NewsResponse(BaseModel):
    response: str

# Initialize the agent
def get_agent():
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=dedent("""\
            You are an enthusiastic news reporter with a flair for storytelling! 🗽
            Think of yourself as a mix between a witty comedian and a sharp journalist.

            Your style guide:
            - Start with an attention-grabbing headline using emoji
            - Share news with enthusiasm and NYC attitude
            - Keep your responses concise but entertaining
            - Throw in local references and NYC slang when appropriate
            - End with a catchy sign-off like 'Back to you in the studio!' or 'Reporting live from the Big Apple!'

            Remember to verify all facts while keeping that NYC energy high!\
        """),
        markdown=True,
    )

@app.get("/")
async def root():
    return {
        "message": "News Reporter Agent API",
        "endpoints": {
            "/report": "POST - Get a news report",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/report", response_model=NewsResponse)
async def get_report(request: NewsRequest):
    try:
        agent = get_agent()
        response = agent.run(request.prompt, stream=request.stream)
        
        # Extract the content from the response
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
            
        return NewsResponse(response=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
