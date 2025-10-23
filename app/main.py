import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .router import router as cab_router
from .agent import handle_chat

app = FastAPI(title="Cab Roster Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cab_router)


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    if not message:
        return {"status": "error", "message": "Missing 'message' in request body"}
    return await handle_chat(message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
