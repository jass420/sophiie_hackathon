import json
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Roomie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy load agent to avoid import issues at startup
_agent = None


async def get_agent():
    global _agent
    if _agent is None:
        from backend.agent.graph import create_agent
        _agent = await create_agent()
    return _agent


class ChatMessage(BaseModel):
    role: str
    content: str
    image: str | None = None  # base64 encoded image


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    agent = await get_agent()

    # Convert messages to LangChain format
    lc_messages = []
    for msg in request.messages:
        if msg.role == "user":
            if msg.image:
                # Multi-modal message with image (OpenAI format)
                content = [
                    {"type": "text", "text": msg.content or "Please analyze this room."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{msg.image}",
                        },
                    },
                ]
                lc_messages.append(HumanMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))

    async def event_stream():
        try:
            result = await agent.ainvoke(
                {
                    "messages": lc_messages,
                    "room_analysis": None,
                    "shopping_list": [],
                    "search_results": [],
                    "pending_proposal": None,
                    "approved_items": [],
                    "search_tasks": [],
                    "current_task_index": 0,
                    "worker_results": [],
                    "_tasks_a": [],
                    "_tasks_b": [],
                    "_messaging_tasks": [],
                    "_messaging_results": [],
                },
                config={"recursion_limit": 100},
            )

            # Get the last AI message
            last_message = result["messages"][-1]
            content = last_message.content

            # Extract tool calls and their results
            tool_results = []
            products = []
            for msg in result["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_results.append({
                            "tool": tc["name"],
                            "args": tc["args"],
                        })
                # ToolMessage contains the results
                if msg.type == "tool" and msg.content:
                    try:
                        tool_data = json.loads(msg.content)
                        if "products" in tool_data:
                            products.extend(tool_data["products"])
                    except (json.JSONDecodeError, TypeError):
                        pass

            response_data = {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_results,
                "products": products,
            }

            yield f"data: {json.dumps(response_data)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = {"role": "assistant", "content": f"I encountered an error: {str(e)}. Please try again."}
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/browser/screenshot")
async def browser_screenshot():
    """Return the current browser screenshot as base64."""
    await get_agent()  # ensure MCP tools are loaded
    from backend.browser.mcp_client import take_screenshot
    result = await take_screenshot()
    if result is None:
        return JSONResponse({"screenshot": None, "status": "no_browser"})
    return JSONResponse({"screenshot": result, "status": "ok"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
