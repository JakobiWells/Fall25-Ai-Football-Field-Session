from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QSlider, QLabel, QSizePolicy)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QTime

def create_video_dock(parent):
    dock = QDockWidget("Video w/ Bounding Boxes", parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
    
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
    controls_layout = QHBoxLayout()
    controls_layout.setContentsMargins(5, 5, 5, 5)

    # Play/Pause button
    parent.play_button = QPushButton("Play")
    parent.play_button.setFixedSize(60, 30)
    parent.play_button.clicked.connect(lambda: toggle_playback(parent))
    controls_layout.addWidget(parent.play_button)

    # Time label
    parent.time_label = QLabel("00:00 / 00:00")
    parent.time_label.setFixedWidth(100)
    controls_layout.addWidget(parent.time_label)

    # Progress slider
    parent.progress_slider = QSlider(Qt.Horizontal)
    parent.progress_slider.setRange(0, 0)
    parent.progress_slider.sliderMoved.connect(lambda position: set_position(parent, position))
    parent.progress_slider.sliderPressed.connect(lambda: parent.player.pause())
    parent.progress_slider.sliderReleased.connect(lambda: parent.player.play())
    controls_layout.addWidget(parent.progress_slider, 1)

    # Volume slider
    controls_layout.addWidget(QLabel("Volume:"))
    parent.volume_slider = QSlider(Qt.Horizontal)
    parent.volume_slider.setRange(0, 100)
    parent.volume_slider.setValue(50)
    parent.volume_slider.setFixedWidth(80)
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
        parent.play_button.setText("Pause")
    else:
        parent.play_button.setText("Play")