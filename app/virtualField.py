from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

def create_virtual_field_dock(parent):
    dock = QDockWidget("Virtual Field", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    
    # Main widget
    main_widget = QWidget()
    layout = QVBoxLayout()
    
    # Placeholder label
    label = QLabel("Virtual Field View - Coming Soon")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    main_widget.setLayout(layout)
    dock.setWidget(main_widget)
    
    return dock