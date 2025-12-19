from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.deps import get_vector_store_collection, get_embedding_model
from app.core.security import get_current_user
from app.schemas.users import UserOut

router = APIRouter()

@router.get("/vector-store/inspect")
async def inspect_vector_store(
    source: Optional[str] = Query(None, description="Filter by source (e.g., 'qa/question/2' or 'Project-Titles.pdf')"),
    limit: int = Query(10, ge=1, le=100),
    current_user: UserOut = Depends(get_current_user),
    collection = Depends(get_vector_store_collection),
):
    """
    Inspect what's actually stored in the vector store.
    Useful for debugging indexing issues.
    """
    try:
        # Get all documents or filter by source
        if source:
            results = collection.get(
                where={"source": source},
                limit=limit,
                include=["documents", "metadatas"]
            )
        else:
            results = collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
        
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        ids = results.get("ids") or []
        
        # Handle nested structure
        if documents and isinstance(documents[0], list):
            documents = [doc for sublist in documents for doc in sublist]
        if metadatas and isinstance(metadatas[0], list):
            metadatas = [md for sublist in metadatas for md in sublist]
        if ids and isinstance(ids[0], list):
            ids = [id for sublist in ids for id in sublist]
        
        items = []
        for idx, (doc_id, doc_content, metadata) in enumerate(zip(ids, documents, metadatas)):
            items.append({
                "id": doc_id,
                "content_preview": doc_content[:200] + "..." if len(doc_content) > 200 else doc_content,
                "content_length": len(doc_content),
                "metadata": metadata or {},
            })
        
        return {
            "total_found": len(items),
            "items": items,
        }
    except Exception as e:
        return {"error": str(e), "items": []}


@router.get("/vector-store/test-query")
async def test_query(
    query: str = Query(..., description="Test query to see what gets retrieved"),
    top_k: int = Query(3, ge=1, le=10),
    current_user: UserOut = Depends(get_current_user),
    collection = Depends(get_vector_store_collection),
    embedding_model = Depends(get_embedding_model),
):
    """
    Test a query and see what documents are retrieved from the vector store.
    Useful for debugging why certain content isn't being found.
    """
    from app.infra.vector_store import search_similar_documents
    
    try:
        results = search_similar_documents(query, collection, embedding_model, top_k)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content_preview": result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"],
                "content_length": len(result["content"]),
                "metadata": result.get("metadata", {}),
                "id": result.get("id"),
            })
        
        return {
            "query": query,
            "top_k": top_k,
            "results_count": len(formatted_results),
            "results": formatted_results,
        }
    except Exception as e:
        return {"error": str(e), "results": []}


@router.get("/vector-store/stats")
async def vector_store_stats(
    current_user: UserOut = Depends(get_current_user),
    collection = Depends(get_vector_store_collection),
):
    """
    Get statistics about what's in the vector store.
    """
    try:
        # Get all documents
        all_results = collection.get(include=["metadatas"])
        all_metadatas = all_results.get("metadatas") or []
        all_ids = all_results.get("ids") or []
        
        # Handle nested structure
        if all_metadatas and isinstance(all_metadatas[0], list):
            all_metadatas = [md for sublist in all_metadatas for md in sublist]
        if all_ids and isinstance(all_ids[0], list):
            all_ids = [id for sublist in all_ids for id in sublist]
        
        # Count by source
        source_counts = {}
        type_counts = {}
        
        for metadata in all_metadatas:
            if isinstance(metadata, dict):
                source = metadata.get("source", "unknown")
                doc_type = metadata.get("type", "document")
                
                source_counts[source] = source_counts.get(source, 0) + 1
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        return {
            "total_chunks": len(all_ids),
            "unique_sources": len(source_counts),
            "sources": source_counts,
            "types": type_counts,
        }
    except Exception as e:
        return {"error": str(e)}