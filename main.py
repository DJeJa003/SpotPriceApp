"""
Main entry point for the Electricity Spot Price Monitor application.
This module initializes the PyQt6 application and creates the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from presentation.main_window import MainWindow

def main():
    """
    Initialize and run the main application window.
    Creates a QApplication instance and shows the main window.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 