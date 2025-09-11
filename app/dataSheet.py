from PySide6.QtWidgets import QDockWidget, QTableView, QVBoxLayout, QWidget
from PySide6.QtCore import Qt



#Data Sheet Dock
#CSV file for data


def create_data_sheet_dock(parent):
    dock = QDockWidget("Data Sheet", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)




    #Main widget
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
   
    
    
    return dock