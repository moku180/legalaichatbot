import sys
import os
import asyncio
import logging
import shutil
from pathlib import Path

# Add backend to sys.path
backend_path = Path("c:/Users/moksh/OneDrive/Desktop/legalchatbot/backend")
sys.path.append(str(backend_path))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from app.services.embedding_service import embedding_service
from app.rag.vector_store import vector_store
from app.rag.chunker import legal_chunker
from app.services.s3_service import s3_service
from app.core.config import settings

async def verify_flow():
    print("=== Starting RAG Flow Verification ===")
    
    # 1. Disable S3 for this test
    s3_service.enabled = False
    print("S3 disabled for testing.")

    # 2. Use a test organization ID
    test_org_id = 99999
    
    # 3. Create dummy text
    dummy_text = """
    This is a test document for the Legal AI Chatbot.
    The Supreme Court in the case of Smith v. Jones ruled that AI agents are liable for their actions.
    Section 45 of the Robotics Act 2025 states that robots must not harm humans.
    """
    print(f"Dummy text created ({len(dummy_text)} chars).")

    # 4. Chunk the document
    print("Chunking document...")
    chunks = legal_chunker.chunk_document(
        text=dummy_text,
        metadata={
            "document_id": 12345,
            "organization_id": test_org_id,
            "title": "Test Legal Document",
            "jurisdiction": "US",
            "court_level": "supreme_court",
            "year": 2025,
            "document_type": "case_law"
        }
    )
    print(f"Created {len(chunks)} chunks.")
    
    # Add text to metadata as expected by vector_store
    for chunk in chunks:
        chunk["metadata"]["text"] = chunk["text"]

    # 5. Add to Vector Store (Embedding Generation)
    print("\nGenerating embeddings and adding to vector store...")
    try:
        success = await vector_store.add_documents(test_org_id, chunks)
        if success:
            print("Successfully added documents to vector store.")
        else:
            print("Failed to add documents (returned False).")
            return
    except Exception as e:
        print(f"Error adding documents: {e}")
        import traceback
        traceback.print_exc()
        return

    # 6. Search (Retrieval)
    print("\nSearching vector store...")
    queries = [
        "What did Smith v. Jones rule?",
        "What does the Robotics Act say?"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        start_time = asyncio.get_event_loop().time()
        results = await vector_store.search(test_org_id, query, top_k=3)
        elapsed = asyncio.get_event_loop().time() - start_time
        
        print(f"Found {len(results)} results in {elapsed:.2f}s:")
        for res in results:
            score = res['score']
            text = res['metadata'].get('text', 'No text found')
            print(f"  - Score: {score:.4f} | Text: {text[:100]}...")
            
    # Cleanup
    print("\nCleaning up...")
    index_path = vector_store._get_index_path(test_org_id)
    meta_path = vector_store._get_metadata_path(test_org_id)
    if index_path.exists():
        os.remove(index_path)
    if meta_path.exists():
        os.remove(meta_path)
    print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(verify_flow())
