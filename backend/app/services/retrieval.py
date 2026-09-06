import os
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from typing import List, Dict, Any
from app.core.config import settings
from app.schemas.query import SourceCitation
from app.utils.logging_config import logger

class FastEmbedEF(EmbeddingFunction):
    """Custom Chroma DB Embedding Function matching the thenlper/gte-large 1024-dim index."""
    def __init__(self, model_name: str = "thenlper/gte-large"):
        try:
            from fastembed import TextEmbedding
            self.model = TextEmbedding(model_name=model_name, threads=2)
        except Exception as e:
            logger.warning(f"FastEmbed init error: {e}. Falling back to sentence-transformers.")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("thenlper/gte-large")

    def __call__(self, input: Documents) -> Embeddings:
        if hasattr(self.model, "embed"):
            return [list(vec) for vec in self.model.embed(input)]
        else:
            return self.model.encode(input).tolist()

    def embed_query(self, input: Documents) -> Embeddings:
        return self(input)

    def embed_documents(self, input: Documents) -> Embeddings:
        return self(input)

    def name(self) -> str:
        return "FastEmbedEF"

class VectorStoreService:
    def __init__(self, vector_store_path: str = None, collection_name: str = None):
        self.vector_store_path = vector_store_path or settings.VECTOR_STORE_PATH
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.client = None
        self.collection = None
        self.ef = None

    def initialize(self):
        logger.info(f"Initializing ChromaDB PersistentClient from: {self.vector_store_path}")
        if not os.path.exists(self.vector_store_path):
            os.makedirs(self.vector_store_path, exist_ok=True)
            
        self.client = chromadb.PersistentClient(path=self.vector_store_path)
        
        try:
            self.ef = FastEmbedEF(model_name="thenlper/gte-large")
        except Exception as e:
            logger.warning(f"Failed to load FastEmbedEF: {e}")
            self.ef = None

        try:
            if self.ef:
                self.collection = self.client.get_collection(name=self.collection_name, embedding_function=self.ef)
            else:
                self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection '{self.collection_name}' with {self.collection.count()} items.")
        except Exception as e:
            logger.warning(f"Collection '{self.collection_name}' not found: {e}. Getting or creating collection.")
            self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def retrieve(self, query: str, top_k: int = 4) -> List[SourceCitation]:
        if not self.collection:
            self.initialize()
            
        count = self.collection.count()
        if count == 0:
            logger.warning("Vector store collection is empty.")
            return []
            
        actual_k = min(top_k, count)
        # Retrieve more candidates for re-ranking
        retrieval_k = min(actual_k * 3, count)

        # Primary: Vector similarity search (semantic understanding)
        try:
            results = self.collection.query(query_texts=[query], n_results=retrieval_k)
            if results and 'documents' in results and results['documents']:
                docs = results['documents'][0]
                metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(docs)
                ids = results['ids'][0] if 'ids' in results and results['ids'] else [f"chunk_{i}" for i in range(len(docs))]
                distances = results.get('distances', [[]])[0] if 'distances' in results else [0.0] * len(docs)
                
                # Re-rank with keyword boost on top of vector results
                keywords = [w.lower() for w in query.split() if len(w) > 3]
                scored_results = []
                for i, (doc_id, doc_text, meta, dist) in enumerate(zip(ids, docs, metas, distances)):
                    meta_dict = meta if isinstance(meta, dict) else {}
                    # Base score from vector distance (lower distance = better, so invert)
                    vector_score = 1.0 / (1.0 + dist)
                    # Keyword boost
                    keyword_score = sum(0.05 for kw in keywords if kw in doc_text.lower())
                    topic = str(meta_dict.get("topic_key", "")).lower()
                    if any(kw in topic for kw in keywords):
                        keyword_score += 0.1
                    combined_score = vector_score + keyword_score
                    scored_results.append((combined_score, doc_id, doc_text, meta_dict))
                
                # Sort by combined score (highest first) and take top_k
                scored_results.sort(key=lambda x: x[0], reverse=True)
                top_results = scored_results[:actual_k]
                
                citations = []
                for score, doc_id, doc_text, meta_dict in top_results:
                    citations.append(
                        SourceCitation(
                            id=str(doc_id),
                            source=str(meta_dict.get("source", "pdfs/it_support_knowledge_base_1000pages.pdf")),
                            page=int(meta_dict.get("page", 1)),
                            content_snippet=str(doc_text),
                            metadata=meta_dict
                        )
                    )
                if citations:
                    logger.info(f"Vector search returned {len(citations)} results for query: '{query[:80]}...'")
                    return citations
        except Exception as e:
            logger.error(f"Vector search error: {e}")

        # Fallback: Keyword-based retrieval if vector search fails
        try:
            logger.warning("Falling back to keyword-based retrieval.")
            raw = self.collection.get(limit=300)
            all_docs = raw.get("documents", [])
            all_metas = raw.get("metadatas", [])
            all_ids = raw.get("ids", [])
            
            keywords = [w.lower() for w in query.split() if len(w) > 3]
            scored = []
            for doc_id, doc_text, meta in zip(all_ids, all_docs, all_metas):
                score = sum(2 if kw in doc_text.lower() else 0 for kw in keywords)
                if meta and isinstance(meta, dict):
                    topic = str(meta.get("topic_key", "")).lower()
                    if any(kw in topic for kw in keywords):
                        score += 5
                scored.append((score, doc_id, doc_text, meta))
                
            scored.sort(key=lambda x: x[0], reverse=True)
            top_matches = scored[:actual_k]
            
            citations = []
            for score, doc_id, doc_text, meta in top_matches:
                meta_dict = meta if isinstance(meta, dict) else {}
                citations.append(
                    SourceCitation(
                        id=str(doc_id),
                        source=str(meta_dict.get("source", "pdfs/it_support_knowledge_base_1000pages.pdf")),
                        page=int(meta_dict.get("page", 1)),
                        content_snippet=str(doc_text),
                        metadata=meta_dict
                    )
                )
            if citations:
                return citations
        except Exception as err:
            logger.error(f"Keyword retrieval error: {err}")
            
        return []

    def get_count(self) -> int:
        if self.collection:
            return self.collection.count()
        return 0

vector_store_service = VectorStoreService()
