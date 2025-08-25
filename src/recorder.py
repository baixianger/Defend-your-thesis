import os
import sys
from langchain.indexes import SQLRecordManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.utils import get_record_db_url



def get_record_manager(
    store_id: str,
):
    """Get the record manager."""
    return SQLRecordManager(
        namespace=store_id,
        db_url=get_record_db_url(),
    )