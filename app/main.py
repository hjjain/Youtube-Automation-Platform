"""
Main FastAPI Application
Automated Video Creation Platform for Hindi Historical Reels
"""
import os
from pathlib import Path
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.api.routes import router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Reel Creator API",
    description="Automated Video Creation Platform for Hindi Historical Reels",
    version="1.0.0"
)

# CORS Configuration
# In production, replace with your actual frontend domains
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",           # Local Next.js dev
    "http://localhost:8000",           # Local FastAPI
    "https://*.vercel.app",            # Vercel deployments
    # Add your production domain here:
    # "https://your-app.vercel.app",
]

# For development, allow all origins
# In production, set CORS_ORIGINS env variable
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time pipeline updates
class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket connected for project {project_id}")
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket disconnected for project {project_id}")
    
    async def send_progress(self, project_id: str, data: dict):
        """Send progress update to all connected clients"""
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(data)
                except Exception:
                    pass

# Global connection manager
ws_manager = ConnectionManager()

# Include API routes
app.include_router(router, prefix="/api", tags=["videos"])

# Serve output files statically
if settings.OUTPUT_DIR.exists():
    app.mount("/output", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="output")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🎬 Reel Creator API Starting...")
    logger.info(f"Output directory: {settings.OUTPUT_DIR}")
    logger.info(f"Music directory: {settings.MUSIC_DIR}")
    logger.info(f"Temp directory: {settings.TEMP_DIR}")
    
    # Create required directories
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("✅ Application initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Reel Creator API Shutting down...")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Reel Creator API",
        "version": "1.0.0",
        "description": "Automated Video Creation Platform for Hindi Historical Reels",
        "docs_url": "/docs",
        "endpoints": {
            "create_video": "POST /api/videos/create",
            "create_video_auto": "POST /api/videos/create/auto",
            "video_status": "GET /api/videos/{project_id}/status",
            "get_videos": "GET /api/videos",
            "get_trends": "GET /api/trends",
            "get_stats": "GET /api/stats",
            "upload_youtube": "POST /api/videos/{project_id}/upload",
            "websocket": "WS /ws/pipeline/{project_id}",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "reel-creator-api",
        "version": "1.0.0"
    }


@app.websocket("/ws/pipeline/{project_id}")
async def websocket_pipeline(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time pipeline progress updates
    
    Sends JSON messages with format:
    {
        "step": "generating_images",
        "progress": 45,
        "message": "Generating image 4 of 8...",
        "completed_steps": ["trends", "script", "voiceover"],
        "current_step": "images"
    }
    """
    await ws_manager.connect(websocket, project_id)
    try:
        while True:
            # Keep connection alive, wait for disconnect
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, project_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

