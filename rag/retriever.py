import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.vectorstores import Chroma
from pipeline.embeddings import load_embedding_model

def get_retriever():

    embeddings = load_embedding_model()

    vectordb = Chroma(
        persist_directory=str(PROJECT_ROOT / "vector_db"),
        embedding_function=embeddings
    )

    return vectordb.as_retriever(search_kwargs={"k": 5})