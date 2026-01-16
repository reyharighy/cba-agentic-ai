"""
Docstring for cache.context
"""
# internal
from context.database import DatabaseManager
from util import st_cache

@st_cache("Loading database manager", "resource")
def load_database_manager() -> DatabaseManager:
    """
    Docstring for load_database_manager
    
    :return: Description
    :rtype: DatabaseManager
    """
    return DatabaseManager()
