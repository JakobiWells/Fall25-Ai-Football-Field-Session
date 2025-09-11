from PySide6.QtWidgets import QDockWidget, QTableView, QVBoxLayout, QWidget, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
import os

class CSVTableModel(QAbstractTableModel):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data if data is not None else pd.DataFrame()
        self.video_clip_column = None
        self.video_time_column = None
        self.empty_message = "No data available. Double-click to add rows."

    def rowCount(self, parent=QModelIndex()):
        if self._data.empty:
            return 1  # Show one row for empty message
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if self._data.empty:
            return 1  # Show one column for empty message
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            if self._data.empty:
                # Show empty message in first cell
                if index.row() == 0 and index.column() == 0:
                    return self.empty_message
                return None
            return str(self._data.iloc[index.row(), index.column()])
        
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self._data.empty:
                return "Data" if section == 0 else None
            return str(self._data.columns[section])
        return None

    def load_csv(self, csv_path):
        try:
            self.beginResetModel()
            self._data = pd.read_csv(csv_path)
            
            # Try to auto-detect video clip and time columns
            for col in self._data.columns:
                col_lower = col.lower()
                if 'clip' in col_lower or 'video' in col_lower:
                    self.video_clip_column = col
                if 'time' in col_lower or 'timestamp' in col_lower:
                    self.video_time_column = col
            
            self.endResetModel()
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False

    def get_video_info(self, row):
        """Get video file path and timestamp for the given row"""
        if self._data.empty or row >= len(self._data):
            return None, None
        
        video_file = None
        timestamp = None
        
        # Get video file from detected column or first column that looks like a file path
        if self.video_clip_column:
            video_file = self._data.iloc[row][self.video_clip_column]
        else:
            for col in self._data.columns:
                value = str(self._data.iloc[row][col])
                if any(ext in value.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']):
                    video_file = value
                    break
        
        # Get timestamp if available
        if self.video_time_column:
            timestamp = self._data.iloc[row][self.video_time_column]
        
        return video_file, timestamp

def create_data_sheet_dock(parent):
    dock = QDockWidget("Data Sheet", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)

    # Main widget
    main_widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    # Create table view
    parent.tableView = QTableView()
    parent.csv_model = CSVTableModel()
    parent.tableView.setModel(parent.csv_model)
    
    # Configure table view
    parent.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
    parent.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
    parent.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    parent.tableView.setAlternatingRowColors(True)
    
    # Connect selection change to play corresponding video
    parent.tableView.selectionModel().selectionChanged.connect(
        lambda: on_row_selected(parent)
    )
    
    layout.addWidget(parent.tableView)
    main_widget.setLayout(layout)
    dock.setWidget(main_widget)
    
    # Add method to parent
    parent.load_csv_file = lambda csv_path: load_csv_file(parent, csv_path)
    
    return dock

def load_csv_file(parent, csv_path):
    """Load a CSV file into the data sheet"""
    if parent.csv_model.load_csv(csv_path):
        parent.tableView.resizeColumnsToContents()
        print(f"Loaded CSV: {csv_path}")
        return True
    return False

def on_row_selected(parent):
    """Handle row selection to play corresponding video clip"""
    selected_indexes = parent.tableView.selectionModel().selectedRows()
    if not selected_indexes:
        return
    
    row = selected_indexes[0].row()
    video_file, timestamp = parent.csv_model.get_video_info(row)
    
    if video_file:
        # Construct full path if the video file is relative
        if not os.path.isabs(video_file) and hasattr(parent, 'current_folder'):
            video_file = os.path.join(parent.current_folder, video_file)
        
        if os.path.exists(video_file):
            play_video_clip(parent, video_file, timestamp)
        else:
            print(f"Video file not found: {video_file}")

def play_video_clip(parent, video_path, timestamp=None):
    """Play video at specific timestamp if available"""
    from PySide6.QtCore import QUrl
    
    parent.player.setSource(QUrl.fromLocalFile(video_path))
    
    # Seek to timestamp if provided
    if timestamp:
        try:
            # Handle different timestamp formats
            if isinstance(timestamp, (int, float)):
                # Assume milliseconds or seconds
                position = int(timestamp * 1000) if timestamp < 1000 else int(timestamp)
            elif isinstance(timestamp, str):
                # Handle time strings like "00:01:30" or "1m30s"
                if ':' in timestamp:
                    parts = timestamp.split(':')
                    if len(parts) == 3:  # HH:MM:SS
                        hours, minutes, seconds = map(float, parts)
                        position = int((hours * 3600 + minutes * 60 + seconds) * 1000)
                    elif len(parts) == 2:  # MM:SS
                        minutes, seconds = map(float, parts)
                        position = int((minutes * 60 + seconds) * 1000)
                else:
                    position = 0
            else:
                position = 0
                
            parent.player.setPosition(position)
        except (ValueError, TypeError):
            position = 0
    
    parent.play_button.setText("Pause")
    parent.time_label.setText("00:00 / 00:00")
    parent.player.play()