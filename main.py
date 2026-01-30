# internal
from application import UserInterface
from application.cache import cold_start, load_memory_manager


def main() -> None:
    """
    Docstring for main
    """
    cold_start()
    app: UserInterface = UserInterface(memory_manager=load_memory_manager())
    app.run()


if __name__ == "__main__":
    main()
