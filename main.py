"""
Application entry point.
"""
# internal
from application import UserInterface
from memory.database import MemoryManager
from cache import cold_start, load_memory_manager

def main() -> None:
    """
    Initialize and run the application.

    This function coordinates early system setup, resolves required
    dependencies, and starts the primary user interface loop.
    """
    cold_start()
    memory_manager: MemoryManager = load_memory_manager()
    app: UserInterface = UserInterface(memory_manager)
    app.run()

if __name__ == "__main__":
    main()
