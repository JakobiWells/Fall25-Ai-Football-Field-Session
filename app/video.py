from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QSlider, QLabel, QSizePolicy)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QTime

def create_video_title_bar(dock):
    """Create a custom title bar for the video dock widget"""
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
    from PySide6.QtGui import QFont
    
    title_bar = QWidget()
    title_bar.setFixedHeight(30)
    title_bar.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            border-bottom: 1px solid #555555;
        }
        QLabel {
            color: white;
            font-weight: bold;
        }
        QPushButton {
            background-color: transparent;
            border: none;
            color: white;
            padding: 4px;
            border-radius: 3px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #404040;
        }
        QPushButton:pressed {
            background-color: #505050;
        }
    """)
    
    layout = QHBoxLayout()
    layout.setContentsMargins(8, 4, 8, 4)
    layout.setSpacing(8)
    
    # Left spacer to center the title
    left_spacer = QWidget()
    left_spacer.setFixedWidth(20)  # Space for close button on the right
    layout.addWidget(left_spacer)
    
    # Title label (centered)
    title_label = QLabel("Video")
    title_label.setFont(QFont("Arial", 10, QFont.Bold))
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)
    
    # Right spacer to balance the left spacer
    right_spacer = QWidget()
    right_spacer.setFixedWidth(20)  # Space for buttons on the right
    layout.addWidget(right_spacer)
    
    # Bounding boxes checkbox
    bbox_checkbox = QPushButton("📦")
    bbox_checkbox.setFixedSize(20, 20)
    bbox_checkbox.setCheckable(True)
    bbox_checkbox.setChecked(True)  # Bounding boxes visible by default
    bbox_checkbox.setToolTip("Toggle Bounding Boxes")
    bbox_checkbox.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: none;
            color: white;
            padding: 4px;
            border-radius: 3px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #404040;
        }
        QPushButton:pressed {
            background-color: #505050;
        }
        QPushButton:checked {
            background-color: #0078d4;
        }
    """)
    layout.addWidget(bbox_checkbox)
    
    # Close button (X)
    close_btn = QPushButton("✕")
    close_btn.setFixedSize(20, 20)
    close_btn.setToolTip("Close")
    close_btn.clicked.connect(dock.close)
    layout.addWidget(close_btn)
    
    title_bar.setLayout(layout)
    return title_bar

def create_video_dock(parent):
    dock = QDockWidget("Video", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    
    # Set custom title bar
    dock.setTitleBarWidget(create_video_title_bar(dock))
    
    # Main container widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # Video Widget
    video_widget = QVideoWidget()
    video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    main_layout.addWidget(video_widget, 4)

    # Controls container
    controls_widget = QWidget()
    controls_widget.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            border-top: 1px solid #555555;
        }
    """)
    controls_layout = QHBoxLayout()
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_layout.setSpacing(15)

    # Play/Pause button
    parent.play_button = QPushButton("▶")
    parent.play_button.setFixedSize(40, 30)
    parent.play_button.setStyleSheet("""
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            color: white;
            padding: 6px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #606060;
        }
    """)
    parent.play_button.clicked.connect(lambda: toggle_playback(parent))
    controls_layout.addWidget(parent.play_button)

    # Time label
    parent.time_label = QLabel("00:00 / 00:00")
    parent.time_label.setFixedWidth(100)
    parent.time_label.setStyleSheet("""
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
    """)
    controls_layout.addWidget(parent.time_label)

    # Progress slider
    parent.progress_slider = QSlider(Qt.Horizontal)
    parent.progress_slider.setRange(0, 0)
    parent.progress_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 6px;
            background: #404040;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #606060;
            border: 1px solid #555555;
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #707070;
        }
        QSlider::handle:horizontal:pressed {
            background: #808080;
        }
        QSlider::sub-page:horizontal {
            background: #606060;
            border-radius: 3px;
        }
    """)
    parent.progress_slider.sliderMoved.connect(lambda position: set_position(parent, position))
    parent.progress_slider.sliderPressed.connect(lambda: pause_for_drag(parent))
    parent.progress_slider.sliderReleased.connect(lambda: resume_after_drag(parent))
    controls_layout.addWidget(parent.progress_slider, 1)

    # Volume label
    volume_label = QLabel("●")
    volume_label.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            font-weight: bold;
        }
    """)
    controls_layout.addWidget(volume_label)

    # Volume slider
    parent.volume_slider = QSlider(Qt.Horizontal)
    parent.volume_slider.setRange(0, 100)
    parent.volume_slider.setValue(50)
    parent.volume_slider.setFixedWidth(80)
    parent.volume_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 4px;
            background: #404040;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #606060;
            border: 1px solid #555555;
            width: 12px;
            margin: -5px 0;
            border-radius: 6px;
        }
        QSlider::handle:horizontal:hover {
            background: #707070;
        }
        QSlider::handle:horizontal:pressed {
            background: #808080;
        }
        QSlider::sub-page:horizontal {
            background: #606060;
            border-radius: 2px;
        }
    """)
    parent.volume_slider.valueChanged.connect(lambda volume: set_volume(parent, volume))
    controls_layout.addWidget(parent.volume_slider)

    controls_widget.setLayout(controls_layout)
    main_layout.addWidget(controls_widget, 1)

    main_widget.setLayout(main_layout)
    dock.setWidget(main_widget)

    # Media player setup
    parent.player = QMediaPlayer()
    parent.audio_output = QAudioOutput()
    parent.player.setAudioOutput(parent.audio_output)
    parent.player.setVideoOutput(video_widget)
    
    # Set initial volume
    parent.audio_output.setVolume(0.5)

    # Connect player signals
    parent.player.positionChanged.connect(lambda position: update_position(parent, position))
    parent.player.durationChanged.connect(lambda duration: update_duration(parent, duration))
    parent.player.playbackStateChanged.connect(lambda state: update_play_button(parent, state))

    return dock

def toggle_playback(parent):
    if parent.player.playbackState() == QMediaPlayer.PlayingState:
        parent.player.pause()
    else:
        parent.player.play()

def set_position(parent, position):
    parent.player.setPosition(position)

def set_volume(parent, volume):
    parent.audio_output.setVolume(volume / 100.0)

def update_position(parent, position):
    if not parent.progress_slider.isSliderDown():
        parent.progress_slider.setValue(position)
    
    # Update time label
    current_time = QTime(0, 0, 0, 0).addMSecs(position)
    duration = parent.player.duration()
    total_time = QTime(0, 0, 0, 0).addMSecs(duration) if duration > 0 else QTime(0, 0, 0, 0)
    
    current_format = "mm:ss" if duration < 3600000 else "hh:mm:ss"
    total_format = "mm:ss" if duration < 3600000 else "hh:mm:ss"
    
    parent.time_label.setText(f"{current_time.toString(current_format)} / {total_time.toString(total_format)}")

def update_duration(parent, duration):
    parent.progress_slider.setRange(0, duration)

def update_play_button(parent, state):
    if state == QMediaPlayer.PlayingState:
        parent.play_button.setText("⏸")
    else:
        parent.play_button.setText("▶")

def pause_for_drag(parent):
    """Pause video and remember if it was playing before drag"""
    parent.was_playing_before_drag = (parent.player.playbackState() == QMediaPlayer.PlayingState)
    parent.player.pause()

def resume_after_drag(parent):
    """Resume playback only if it was playing before drag started"""
    if hasattr(parent, 'was_playing_before_drag') and parent.was_playing_before_drag:
        parent.player.play()
    parent.was_playing_before_drag = False