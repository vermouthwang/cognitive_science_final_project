from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict
import os
from dotenv import load_dotenv
from app.routers import consultant, logo_routes, evaluator, collaborator_chat
import asyncio
import threading
from app.utils.logo_monitor import start_logo_monitoring


# Load environment variables
load_dotenv()

app = FastAPI(title="Logo Design Lab API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(consultant.router, prefix="/consultant", tags=["consultant AI"])
app.include_router(logo_routes.router, prefix="/logo-generator", tags=["logo-generator"])
app.include_router(evaluator.router, prefix="/evaluator", tags=["Mystery Evaluator"])
app.include_router(collaborator_chat.router, prefix="/collaborator", tags=["Collaborator"])
# Session storage (in-memory for demo)
class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

session_store = SessionStore()

@app.get("/")
async def read_root():
    return {"status": "Logo Design Lab API is running"}

# def run_logo_monitor():
#     fakedata_path = os.path.join(os.path.dirname(__file__), "app", "fakedata")
#     os.makedirs(fakedata_path, exist_ok=True)
#     asyncio.run(start_logo_monitoring(fakedata_path))

# @app.on_event("startup")
# async def startup_event():
#     # Start logo monitor in a separate thread
#     monitor_thread = threading.Thread(target=run_logo_monitor, daemon=True)
#     monitor_thread.start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 

