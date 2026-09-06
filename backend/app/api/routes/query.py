from fastapi import APIRouter, HTTPException, status
from app.schemas.query import QueryRequest, QueryResponse, HealthResponse
from app.services.retrieval import vector_store_service
from app.services.generation import generation_service
from app.core.config import settings
from app.utils.logging_config import logger

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    try:
        count = vector_store_service.get_count()
        return HealthResponse(
            status="ok",
            vector_store_status="connected",
            collection_count=count,
            ollama_model=settings.OLLAMA_MODEL
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="degraded",
            vector_store_status=f"error: {str(e)}",
            collection_count=0,
            ollama_model=settings.OLLAMA_MODEL
        )

@router.post("/query", response_model=QueryResponse, tags=["RAG Pipeline"])
def query_rag_assistant(request: QueryRequest):
    logger.info(f"Received query request: '{request.question}' (top_k={request.top_k})")
    
    # Optional image data support (Extended track visual context fusion)
    effective_question = request.question
    if request.image_data:
        effective_question = f"[Visual Log Attachment Included]\n{request.question}"
        
    try:
        # Step 1: Vector retrieval
        citations = vector_store_service.retrieve(
            query=effective_question,
            top_k=request.top_k or settings.TOP_K_RESULTS
        )
        
        # Step 2: Grounded LLM answer generation
        answer = generation_service.generate_grounded_answer(
            question=effective_question,
            sources=citations
        )
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=citations,
            retrieved_count=len(citations),
            model_used=settings.OLLAMA_MODEL
        )
    except Exception as e:
        logger.error(f"Error processing query endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process RAG query: {str(e)}"
        )
