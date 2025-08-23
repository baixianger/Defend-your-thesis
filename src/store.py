import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import chromadb
from chromadb.api import ClientAPI
from langchain.indexes import index
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from src.embeddings import get_embeddings_model
from src.utils import get_vector_db_dir
from src.recorder import get_record_manager

def get_document(thesis_path: str = "data/BACHELOR_Andreas.pdf"):
    loader = PyMuPDF4LLMLoader(file_path=thesis_path, mode="single")
    full_doc = loader.load()[0]
    full_doc.metadata["collection_name"] = thesis_path
    return full_doc

def get_store(doc):
    chunk_size = 4000
    chunk_overlap = 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Split
    splits = text_splitter.split_documents(doc)

    path = get_vector_db_dir()
    model = "openai/text-embedding-3-small"
    embedding = get_embeddings_model(model)
    client: ClientAPI = chromadb.PersistentClient(path=path)
    store = Chroma(
            client=client,
            collection_name=doc.metadata["collection_name"],
            embedding_function=embedding,
        )
    record_manager = get_record_manager(
        collection_name=doc.metadata["collection_name"],
    )

    indexing_stats = index(
        splits,
        record_manager,
        store,
        cleanup="full",  # 旧的有的，新的没有的，会删除
        source_id_key="source",
        force_update=(os.environ.get("FORCE_UPDATE") or "false").lower() == "true",
    )

    return store