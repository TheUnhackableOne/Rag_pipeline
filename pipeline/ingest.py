from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import os

def load_documents(folder: str = "data/documents") -> list[Document]:
    documents: list[Document] = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder, file))
            docs = loader.load()
            documents.extend(docs)

    return documents