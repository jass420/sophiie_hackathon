import asyncio
import io
import json
import os
import uuid
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Roomie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy load agent to avoid import issues at startup
_agent = None
_agent_lock = asyncio.Lock()


async def get_agent():
    global _agent
    if _agent is not None:
        return _agent
    async with _agent_lock:
        if _agent is None:  # double-check after acquiring lock
            from backend.agent.graph import create_agent
            _agent = await create_agent()
            print(f"[GET_AGENT] Created agent id={id(_agent)}")
    return _agent


class ChatMessage(BaseModel):
    role: str
    content: str
    image: str | None = None  # base64 encoded image


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    thread_id: str | None = None


class ResumeRequest(BaseModel):
    thread_id: str
    action: str  # "approve_all", "approve_selected", "reject"
    selected_ids: list[str] | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


def _extract_response(result):
    """Extract content, tool_calls, and products from an agent result."""
    # Walk backwards to find the last AIMessage with real content
    # (skip ToolMessages which contain raw JSON that shouldn't be displayed)
    content = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            text = msg.content if isinstance(msg.content, str) else str(msg.content)
            # Skip AI messages that are just tool call placeholders (empty or whitespace)
            if text.strip():
                content = text
                break
    # Fallback to last message if no AI content found
    if not content:
        content = result["messages"][-1].content

    tool_results = []
    products = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_results.append({
                    "tool": tc["name"],
                    "args": tc["args"],
                })
        if msg.type == "tool" and msg.content:
            try:
                tool_data = json.loads(msg.content)
                if "products" in tool_data:
                    products.extend(tool_data["products"])
            except (json.JSONDecodeError, TypeError):
                pass

    return content, tool_results, products


@app.post("/api/chat")
async def chat(request: ChatRequest):
    agent = await get_agent()

    thread_id = request.thread_id or str(uuid.uuid4())
    print(f"[CHAT] thread_id={thread_id}, incoming_thread_id={request.thread_id}, message_count={len(request.messages)}")

    # Convert messages to LangChain format
    lc_messages = []
    for msg in request.messages:
        if msg.role == "user":
            if msg.image:
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

    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 100,
    }

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
                config=config,
            )

            content, tool_results, products = _extract_response(result)
            print(f"[CHAT] ainvoke returned. Message count in result: {len(result.get('messages', []))}")
            print(f"[CHAT] agent id={id(agent)}, checkpointer id={id(agent.checkpointer) if hasattr(agent, 'checkpointer') else 'N/A'}")

            # Check if the graph hit an interrupt
            state = await agent.aget_state(config)
            print(f"[CHAT] Post-ainvoke state.next={state.next}, tasks={[t.name if hasattr(t, 'name') else str(t) for t in (state.tasks or [])]}")
            if hasattr(agent, 'checkpointer') and hasattr(agent.checkpointer, 'storage'):
                print(f"[CHAT] Checkpointer storage keys: {list(agent.checkpointer.storage.keys())[:5]}")
            if state.next:  # graph is paused at a node
                # Find the interrupt data from the state's tasks
                interrupt_data = None
                if state.tasks:
                    for task in state.tasks:
                        if hasattr(task, "interrupts") and task.interrupts:
                            interrupt_data = task.interrupts[0].value
                            break

                response_data = {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_results,
                    "products": products,
                    "thread_id": thread_id,
                    "interrupt": interrupt_data,
                }
            else:
                response_data = {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_results,
                    "products": products,
                    "thread_id": thread_id,
                }

            yield f"data: {json.dumps(response_data)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_data = {
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}. Please try again.",
                "thread_id": thread_id,
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/chat/resume")
async def chat_resume(request: ResumeRequest):
    """Resume the graph after a human approval interrupt."""
    agent = await get_agent()

    config = {
        "configurable": {"thread_id": request.thread_id},
        "recursion_limit": 100,
    }

    # Build the resume value matching what human_approval expects
    if request.action == "approve_all":
        resume_value = {"action": "approve_all"}
    elif request.action == "approve_selected":
        resume_value = {"action": "approve_selected", "selected_ids": request.selected_ids or []}
    else:
        resume_value = {"action": "reject"}

    async def event_stream():
        try:
            # Debug: check state before resume
            print(f"[RESUME] agent id={id(agent)}, checkpointer id={id(agent.checkpointer) if hasattr(agent, 'checkpointer') else 'N/A'}")
            if hasattr(agent, 'checkpointer') and hasattr(agent.checkpointer, 'storage'):
                print(f"[RESUME] Checkpointer storage keys: {list(agent.checkpointer.storage.keys())[:5]}")
            pre_state = await agent.aget_state(config)
            print(f"[RESUME] thread_id={request.thread_id}, action={request.action}")
            print(f"[RESUME] Pre-resume state.next={pre_state.next}")
            print(f"[RESUME] Pre-resume tasks={[t.name if hasattr(t, 'name') else str(t) for t in (pre_state.tasks or [])]}")
            if pre_state.values.get("messages"):
                print(f"[RESUME] Pre-resume message count={len(pre_state.values['messages'])}")
            else:
                print(f"[RESUME] Pre-resume messages=EMPTY")

            result = await agent.ainvoke(
                Command(resume=resume_value),
                config=config,
            )

            content, tool_results, products = _extract_response(result)

            # Check for another interrupt (e.g. contact_sellers after shortlist approval)
            state = await agent.aget_state(config)
            interrupt_data = None
            if state.next and state.tasks:
                for task in state.tasks:
                    if hasattr(task, "interrupts") and task.interrupts:
                        interrupt_data = task.interrupts[0].value
                        break

            response_data = {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_results,
                "products": products,
                "thread_id": request.thread_id,
            }
            if interrupt_data:
                response_data["interrupt"] = interrupt_data

            yield f"data: {json.dumps(response_data)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_data = {
                "role": "assistant",
                "content": f"I encountered an error while processing your decision: {str(e)}",
                "thread_id": request.thread_id,
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/browser/screenshot")
async def browser_screenshot():
    """Return the current browser screenshot from Worker A."""
    await get_agent()  # ensure MCP tools are loaded
    from backend.browser.mcp_client import take_screenshot
    result = await take_screenshot()
    if result is None:
        return JSONResponse({"screenshot": None, "status": "no_browser"})
    return JSONResponse({"screenshot": result, "status": "ok"})


@app.get("/api/browser/screenshot-b")
async def browser_screenshot_b():
    """Return the current browser screenshot from Worker B."""
    await get_agent()  # ensure MCP tools are loaded
    from backend.browser.mcp_client import take_screenshot_b
    result = await take_screenshot_b()
    if result is None:
        return JSONResponse({"screenshot": None, "status": "no_browser"})
    return JSONResponse({"screenshot": result, "status": "ok"})


class TTSRequest(BaseModel):
    text: str


@app.post("/api/voice/transcribe")
async def voice_transcribe(file: UploadFile = File(...)):
    """Transcribe audio to text using OpenAI Whisper."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_APIKEY"))
    audio_bytes = await file.read()
    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.webm", audio_bytes, file.content_type or "audio/webm"),
    )
    return {"text": transcript.text}


@app.post("/api/voice/tts")
async def voice_tts(req: TTSRequest):
    """Convert text to speech using OpenAI TTS with streaming."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_APIKEY"))

    async def stream_audio():
        async with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="nova",
            input=req.text,
        ) as response:
            async for chunk in response.iter_bytes(1024):
                yield chunk

    return StreamingResponse(
        stream_audio(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
