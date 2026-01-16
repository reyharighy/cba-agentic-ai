"""
Docstring for main
"""
# internal
from application import UserInterface
from context.database import DatabaseManager
from cache import cold_start, load_database_manager

def main() -> None:
    """
    Docstring for main
    """
    cold_start()
    database_manager: DatabaseManager = load_database_manager()
    app: UserInterface = UserInterface(database_manager)
    app.run()

if __name__ == "__main__":
    main()
