import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import logging
from langchain.indexes import index
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.recorder import get_record_manager
from src.store import get_store, get_document

def ingest(thesis_path: str = "data/Master_Zhang.pdf", store_id: str = "Zhang"):
    chunk_size = 1000
    chunk_overlap = 100
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Split
    splits = text_splitter.split_documents([get_document(thesis_path)])

    store = get_store(store_id)
    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger(__name__)
    # logger.info("Split thesis into %d chunks", len(splits))
    # record_manager = get_record_manager(
    #     store_id=store_id,
    # )

    # indexing_stats = index(
    #     splits,
    #     record_manager,
    #     store,
    #     cleanup="full",  # 旧的有的，新的没有的，会删除
    #     source_id_key="source",
    #     force_update=(os.environ.get("FORCE_UPDATE") or "false").lower() == "true",
    # )
    # logger.info("Indexing stats: %s", indexing_stats)
    
    store.add_documents(splits)
