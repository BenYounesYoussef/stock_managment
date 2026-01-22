
import pytest
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manager import StockManager
from gui import MainWindow

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def test_manager(tmp_path):
    # Create temp files
    p_file = tmp_path / "test_products.json"
    o_file = tmp_path / "test_orders.json"
    
    # Initialize with temp files
    manager = StockManager(products_file=str(p_file), orders_file=str(o_file))
    
    # Add some initial data
    manager.add_product("Test Product 1", "Desc 1", 10, 100.0)
    manager.add_product("Test Product 2", "Desc 2", 5, 200.0)
    
    return manager

@pytest.fixture
def main_window(qapp, test_manager, qtbot):
    # Patch the global manager or inject it if possible
    # In gui.py, MainWindow creates its own StockManager instance.
    # We might need to monkeypatch MainWindow's manager creation or attribute.
    
    window = MainWindow()
    window.manager = test_manager
    # Re-initialize tabs with the new manager because they were already created in __init__
    # This relies on knowing internal structure of MainWindow
    # gui.py: 
    # self.tab_welcome = WelcomeTab(self.manager, ...
    # self.tab_product = ProductTab(self.manager, ...
    # self.tab_order = OrderTab(self.manager, ...
    
    # So we need to update those references too
    window.tab_welcome.manager = test_manager
    window.tab_product.manager = test_manager
    window.tab_order.manager = test_manager
    
    # Reload data to reflect test_manager's data
    window.refresh_app_data()
    
    qtbot.addWidget(window)
    return window
