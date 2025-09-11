from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, 
    QDockWidget, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QAbstractTableModel
import sys
from video import create_video_dock
from fileAccess import create_file_dock
from dataSheet import create_data_sheet_dock

class DataModel(QAbstractTableModel):
    """Simple data model for the table view"""
    def __init__(self, data=None):
        super().__init__()
        self.data = data or []
        self.headers = ["Frame", "Player", "X", "Y", "Confidence"]
    
    def rowCount(self, parent=None):
        return len(self.data)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            if row < len(self.data) and col < len(self.data[row]):
                return str(self.data[row][col])
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hudl AI Analysis")
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.resize(1200, 800)
        
        # Initialize data model
        self.data_model = DataModel()

        # --- Menu Bar ---
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        # Window Menu
        window_menu = menu_bar.addMenu("Window")

        # --- Dock Widgets ---
        self.video_dock = create_video_dock(self)
        self.file_dock = create_file_dock(self)
        self.data_dock = create_data_sheet_dock(self)
        self.virtual_dock = self.create_dock("Virtual Field")

        # Add docks in desired layout
        self.addDockWidget(Qt.TopDockWidgetArea, self.video_dock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.file_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.data_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.virtual_dock)

        # Place side-by-side
        self.splitDockWidget(self.video_dock, self.file_dock, Qt.Horizontal)
        self.splitDockWidget(self.data_dock, self.virtual_dock, Qt.Horizontal)

        # Add dock visibility toggles to Window menu
        window_menu.addAction(self.video_dock.toggleViewAction())
        window_menu.addAction(self.file_dock.toggleViewAction())
        window_menu.addAction(self.data_dock.toggleViewAction())
        window_menu.addAction(self.virtual_dock.toggleViewAction())

    def create_dock(self, title):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        dock.setTitleBarWidget(QWidget())

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{title} content here"))
        widget.setLayout(layout)

        widget.setStyleSheet("""
            QWidget {
                border: 2px solid #888;
            }
        """)

        dock.setWidget(widget)
        return dock

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            # Call the file access method to load the folder
            if hasattr(self, 'load_folder'):
                self.load_folder(folder)

    def export_data(self):
        print("Exporting data... (stub)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())