from PyQt6.QtWidgets import QApplication
from gui import MainWindow
import sys

if __name__ == "__main__":
    if "--cli" in sys.argv:
        from interface import ConsoleInterface
        cli = ConsoleInterface()
        cli.main_menu()
    else:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
