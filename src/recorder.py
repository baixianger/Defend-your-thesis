import os
import sys
from langchain.indexes import SQLRecordManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.utils import get_record_db_url



def get_record_manager(
    collection_name: str,
):
    """Get the record manager."""
    namespace = f"{collection_name}"
    return SQLRecordManager(
        namespace=namespace,
        db_url=get_record_db_url(),
    )