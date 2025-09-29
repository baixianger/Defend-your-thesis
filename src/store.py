import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import chromadb
from chromadb.api import ClientAPI

from langchain_chroma import Chroma

from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from src.embeddings import get_embeddings_model
from src.utils import get_vector_db_dir





def get_document(thesis_path: str = "data/Master_Zhang.pdf"):
    loader = PyMuPDF4LLMLoader(file_path=thesis_path, mode="single")
    full_doc = loader.load()[0]
    full_doc.metadata["source"] = thesis_path
    return full_doc


def get_store(store_id: str):
    path = get_vector_db_dir()
    model = "openai/text-embedding-3-small"
    embedding = get_embeddings_model(model)
    client: ClientAPI = chromadb.PersistentClient(path=path)
    store = Chroma(
            client=client,
            collection_name=store_id,
            embedding_function=embedding,
        )
    return store
    