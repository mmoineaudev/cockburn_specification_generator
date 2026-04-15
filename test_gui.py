#!/usr/bin/env python3
"""
Simple test to verify PyQt6 imports work
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

def test_gui():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Test GUI")
    window.setGeometry(100, 100, 400, 300)
    
    # Create central widget and layout
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Add a label
    label = QLabel("PyQt6 GUI Test Working")
    layout.addWidget(label)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    test_gui()