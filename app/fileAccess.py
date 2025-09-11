from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTreeView,
    QFileSystemModel, QMenu
)
from PySide6.QtCore import Qt, QDir, QFileInfo
import os
import pandas as pd

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
    
    # Single click loads the folder content but doesn't change tree view
    parent.tree_view.clicked.connect(lambda index: on_tree_clicked(parent, index))
    
    # Double click expands/collapses folders in the tree view
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
    parent.load_folder = lambda folder_path: load_folder(parent, folder_path, change_view=True)
    parent.open_video_file = lambda video_path: open_video_file(parent, video_path)

    return dock

def on_tree_clicked(parent, index):
    """Handle single click on tree view items - load folder content but don't change tree view"""
    if parent.tree_model.isDir(index):
        path = parent.tree_model.filePath(index)
        load_folder(parent, path, change_view=False)
        # Don't change the tree view expansion state

def on_tree_double_clicked(parent, index):
    """Handle double click on tree view items - expand/collapse folders only"""
    if parent.tree_model.isDir(index):
        # Toggle expansion state (expand if collapsed, collapse if expanded)
        if parent.tree_view.isExpanded(index):
            parent.tree_view.collapse(index)
        else:
            parent.tree_view.expand(index)
    else:
        # Handle file double-click (for videos and CSVs)
        file_path = parent.tree_model.filePath(index)
        file_info = QFileInfo(file_path)
        
        if file_info.isFile():
            file_ext = file_info.suffix().lower()
            
            if file_ext in ['mp4', 'avi', 'mov', 'mkv', 'wmv']:
                open_video_file(parent, file_path)
            elif file_ext == 'csv':
                # Load CSV into data sheet
                if hasattr(parent, 'load_csv_file'):
                    parent.load_csv_file(file_path)

def load_folder(parent, folder_path, change_view=False):
    parent.current_folder = folder_path
    
    # Change the tree view only if explicitly requested (from Open Folder button)
    if change_view:
        tree_index = parent.tree_model.index(folder_path)
        parent.tree_view.setRootIndex(tree_index)
    
    # Auto-load first CSV and first video in the folder
    auto_load_folder_content(parent, folder_path)

def auto_load_folder_content(parent, folder_path):
    """Automatically load first CSV and first video from the folder"""
    try:
        # Find all CSV files
        csv_files = [f for f in os.listdir(folder_path) 
                    if f.lower().endswith('.csv') and os.path.isfile(os.path.join(folder_path, f))]
        
        # Find all video files
        video_files = [f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')) 
                      and os.path.isfile(os.path.join(folder_path, f))]
        
        # Create CSV with video titles if none exists and videos are present
        if not csv_files and video_files:
            csv_path = create_video_based_csv(folder_path, video_files)
            if csv_path:
                csv_files = [os.path.basename(csv_path)]
                print(f"Created new CSV with video titles: {csv_path}")
        
        # Load first CSV if available
        if csv_files and hasattr(parent, 'load_csv_file'):
            first_csv = os.path.join(folder_path, csv_files[0])
            parent.load_csv_file(first_csv)
            print(f"Loaded CSV: {csv_files[0]}")
        else:
            print("No CSV files available")
        
        # Load and play first video if available
        if video_files and hasattr(parent, 'open_video_file'):
            first_video = os.path.join(folder_path, video_files[0])
            parent.open_video_file(first_video)
            print(f"Playing video: {video_files[0]}")
        else:
            print("No video files found in folder")
            
    except Exception as e:
        print(f"Error auto-loading folder content: {e}")

def create_video_based_csv(folder_path, video_files):
    """Create a CSV file with video clip names as the first column"""
    try:
        # Get folder name for CSV filename
        folder_name = os.path.basename(folder_path.rstrip('/\\'))
        csv_filename = f"{folder_name}_data.csv"
        csv_path = os.path.join(folder_path, csv_filename)
        
        # Check if CSV already exists (shouldn't, but just in case)
        if os.path.exists(csv_path):
            return csv_path
        
        # Create CSV with video clip names as the first column
        video_names = [os.path.splitext(video)[0] for video in video_files]  # Remove extensions
        
        # Create default data structure with video names as the first column
        default_data = {
            'Clip Name': video_names,
            'Video File': video_files,  # Actual filenames with extensions
            'Timestamp': ['00:00:00'] * len(video_files),
            'Player': [''] * len(video_files),
            'Action': [''] * len(video_files),
            'Score': [0] * len(video_files),
            'Team': [''] * len(video_files),
            'Quarter': [1] * len(video_files),
            'Game Time': ['00:00'] * len(video_files),
            'X Position': [0] * len(video_files),
            'Y Position': [0] * len(video_files)
        }
        
        # Create DataFrame and save as CSV
        df = pd.DataFrame(default_data)
        df.to_csv(csv_path, index=False)
        
        print(f"Created CSV with {len(video_files)} video entries")
        return csv_path
        
    except Exception as e:
        print(f"Error creating video-based CSV: {e}")
        return None

def open_video_file(parent, video_path):
    """Open and play a video file"""
    from PySide6.QtCore import QUrl
    parent.player.setSource(QUrl.fromLocalFile(video_path))
    parent.play_button.setText("Pause")
    parent.time_label.setText("00:00 / 00:00")
    parent.progress_slider.setValue(0)
    parent.player.play()

def show_context_menu(parent, position):
    index = parent.tree_view.indexAt(position)
    if not index.isValid():
        return

    menu = QMenu()
    
    if parent.tree_model.isDir(index):
        open_action = menu.addAction("Open (Change View)")
        open_action.triggered.connect(lambda: load_folder(parent, parent.tree_model.filePath(index), change_view=True))
        
        open_no_view_action = menu.addAction("Open (Keep View)")
        open_no_view_action.triggered.connect(lambda: load_folder(parent, parent.tree_model.filePath(index), change_view=False))
        
        # Add option to create new CSV
        create_csv_action = menu.addAction("Create Data Sheet")
        create_csv_action.triggered.connect(
            lambda: create_video_based_csv_from_folder(parent, parent.tree_model.filePath(index))
        )
    else:
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: on_tree_double_clicked(parent, index))
    
    menu.exec(parent.tree_view.viewport().mapToGlobal(position))

def create_video_based_csv_from_folder(parent, folder_path):
    """Create CSV from folder for context menu"""
    try:
        video_files = [f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')) 
                      and os.path.isfile(os.path.join(folder_path, f))]
        
        if video_files:
            csv_path = create_video_based_csv(folder_path, video_files)
            if csv_path and hasattr(parent, 'load_csv_file'):
                parent.load_csv_file(csv_path)
        else:
            print("No video files found to create data sheet")
    except Exception as e:
        print(f"Error creating data sheet from context menu: {e}")