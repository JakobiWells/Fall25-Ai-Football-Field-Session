from PySide6.QtWidgets import QDockWidget
from PySide6.QtCore import Qt

#Virtual Field Dock
#Draws the virtual field and the players on the field



def create_virtual_field_dock(parent):
    dock = QDockWidget("Virtual Field", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    
    return dock