from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

def store_vectors(chunks: list[Document], embeddings: Embeddings) -> Chroma:

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vector_db"
    )

    vectordb.persist()

    return vectordb