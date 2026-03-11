import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.ingest import load_documents
from pipeline.chunking import chunk_documents
from pipeline.embeddings import load_embedding_model
from pipeline.vector_store import store_vectors

def run_pipeline():

    print("Loading documents...")
    docs = load_documents()
    print(f"Loaded {len(docs)} pages")

    print("Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print("Loading embedding model...")
    embeddings = load_embedding_model()

    print("Storing vectors (this may take a while)...")
    store_vectors(chunks, embeddings)

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()