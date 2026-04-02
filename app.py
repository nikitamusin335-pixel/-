from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMIddleware
from fastapi.responses import StreamingResponse
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMIddleware,
    allow_orgins=["*"],
    allow_credentials=True,
    allown_methods=["*"],
    allown_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name = "static")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "GEMMA3:4b"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    history = data.get("history", [])

    message = history + [{"role": "user", "content: user_message"}]

    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                OLLMA_URL,
                json={"model": MODEL_NAME, "message": messages, "stream":True},
                timeout = 60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield line + "\n"

    return StreamingResponse(generate(), media_type = "test/event-stream")

