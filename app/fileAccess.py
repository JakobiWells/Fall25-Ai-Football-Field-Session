from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTreeView,
    QFileSystemModel, QMenu
)
from PySide6.QtCore import Qt, QDir, QFileInfo
import os

def create_file_dock(parent):
    dock = QDockWidget("File Access", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    
    # Main widget
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Tree view for navigation
    parent.tree_model = QFileSystemModel()
    parent.tree_model.setRootPath("")
    parent.tree_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
    
    parent.tree_view = QTreeView()
    parent.tree_view.setModel(parent.tree_model)
    parent.tree_view.setRootIndex(parent.tree_model.index(""))
    parent.tree_view.setHeaderHidden(True)
    parent.tree_view.doubleClicked.connect(lambda index: on_tree_double_clicked(parent, index))
    parent.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
    parent.tree_view.customContextMenuRequested.connect(lambda pos: show_context_menu(parent, pos))
    
    # Hide all columns except Name
    parent.tree_view.setColumnHidden(1, True)
    parent.tree_view.setColumnHidden(2, True)
    parent.tree_view.setColumnHidden(3, True)
    
    layout.addWidget(parent.tree_view)
    main_widget.setLayout(layout)
    dock.setWidget(main_widget)

    # Add methods to parent
    parent.load_folder = lambda folder_path: load_folder(parent, folder_path)
    parent.open_video_file = lambda video_path: open_video_file(parent, video_path)

    return dock

def load_folder(parent, folder_path):
    parent.current_folder = folder_path
    
    # Set model to the selected folder
    tree_index = parent.tree_model.index(folder_path)
    parent.tree_view.setRootIndex(tree_index)

def on_tree_double_clicked(parent, index):
    if parent.tree_model.isDir(index):
        path = parent.tree_model.filePath(index)
        load_folder(parent, path)
    else:
        # Handle file double-click (for videos)
        file_path = parent.tree_model.filePath(index)
        file_info = QFileInfo(file_path)
        
        if file_info.isFile() and file_info.suffix().lower() in ['mp4', 'avi', 'mov', 'mkv', 'wmv']:
            open_video_file(parent, file_path)

def open_video_file(parent, video_path):
    """Open and play a video file"""
    from PySide6.QtCore import QUrl
    parent.player.setSource(QUrl.fromLocalFile(video_path))
    parent.play_button.setText("Play")
    parent.time_label.setText("00:00 / 00:00")
    parent.progress_slider.setValue(0)
    parent.player.play()

def show_context_menu(parent, position):
    index = parent.tree_view.indexAt(position)
    if not index.isValid():
        return

    menu = QMenu()
    
    if parent.tree_model.isDir(index):
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: load_folder(parent, parent.tree_model.filePath(index)))
    else:
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: on_tree_double_clicked(parent, index))
    
    menu.exec(parent.tree_view.viewport().mapToGlobal(position))