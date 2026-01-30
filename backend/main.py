import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from database import init_db, engine, SessionLocal
from routes import auth, users, commandes, livraisons, itineraires, reports, clients
from dotenv import load_dotenv
from scheduler import optimization_scheduler

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and scheduler
    logger.info("Starting application...")
    init_db()
    optimization_scheduler.start()
    logger.info("Route optimization scheduler initialized")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    optimization_scheduler.stop()

# Initialize FastAPI app
app = FastAPI(
    title="Route Optimization System",
    description="Logistics and delivery route optimization platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(commandes.router, prefix="/api/commandes", tags=["Commandes"])
app.include_router(livraisons.router, prefix="/api/livraisons", tags=["Livraisons"])
app.include_router(itineraires.router, prefix="/api/itineraires", tags=["Itineraires"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
