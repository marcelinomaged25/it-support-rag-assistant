from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import query
from app.services.retrieval import vector_store_service
from app.utils.logging_config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup loading: Load vector store index and setup services ONCE at startup
    logger.info("--- Starting FastAPI Server Startup Lifespan ---")
    try:
        vector_store_service.initialize()
        count = vector_store_service.get_count()
        logger.info(f"Vector Store initialized successfully at startup. Total vectors: {count}")
    except Exception as e:
        logger.error(f"Error initializing vector store during lifespan startup: {e}")
        
    yield
    
    logger.info("--- Shutting Down FastAPI Server ---")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise IT Support RAG-Powered Document Assistant Backend API",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(query.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
