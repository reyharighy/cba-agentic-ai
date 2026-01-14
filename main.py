"""
Docstring for main
"""
# internal
from application import UserInterface
from cache import cold_start

def main() -> None:
    """
    Docstring for main
    """
    cold_start()
    app: UserInterface = UserInterface()
    app.run()

if __name__ == "__main__":
    main()
