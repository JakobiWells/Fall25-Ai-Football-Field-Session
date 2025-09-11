from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, 
    QDockWidget, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import sys
from video import create_video_dock
from fileAccess import create_file_dock
from dataSheet import create_data_sheet_dock
from virtualField import create_virtual_field_dock

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hudl AI Analysis")
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.resize(1200, 800)
        
        # Store current folder path
        self.current_folder = ""

        # --- Menu Bar ---
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        # Add Open Video action
        open_video_action = QAction("Open Video", self)
        open_video_action.triggered.connect(self.open_video)
        file_menu.addAction(open_video_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # Window Menu
        window_menu = menu_bar.addMenu("Window")

        # --- Dock Widgets ---
        self.video_dock = create_video_dock(self)
        self.file_dock = create_file_dock(self)
        self.data_dock = create_data_sheet_dock(self)
        self.virtual_dock = create_virtual_field_dock(self)

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

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            # Call the file access method to load the folder
            if hasattr(self, 'load_folder'):
                self.load_folder(folder)

    def open_video(self):
        video_file, _ = QFileDialog.getOpenFileName(
            self, "Open Video", self.current_folder or "", "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)"
        )
        if video_file:
            # Call the video method to open the file
            if hasattr(self, 'open_video_file'):
                self.open_video_file(video_file)

    def export_data(self):
        print("Exporting data... (stub)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())