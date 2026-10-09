"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QScrollArea, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap


class MainWindow(QMainWindow):
    """Main application window."""
    
    status_changed = pyqtSignal(object)
    inference_completed = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SI-Posture")
        self.setGeometry(100, 100, 1200, 800)
        
        self._init_ui()
        self._init_status()
    
    def _init_ui(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Camera preview group
        camera_group = QGroupBox("Live Camera Preview")
        camera_layout = QVBoxLayout()
        
        self.camera_label = QLabel("No camera connected")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #1a1a2e; color: white;")
        
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setMaximumSize(640, 480)
        
        camera_layout.addWidget(self.camera_label)
        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)
        
        # Status group
        status_group = QGroupBox("Monitoring Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: UNKNOWN")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        self.last_inference_label = QLabel("Last inference: Never")
        status_layout.addWidget(self.last_inference_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        
        self.start_pause_button = QPushButton("Start Monitoring")
        self.start_pause_button.clicked.connect(self.toggle_monitoring)
        controls_layout.addWidget(self.start_pause_button)
        
        self.recalibrate_button = QPushButton("Recalibrate")
        self.recalibrate_button.clicked.connect(self.trigger_recalibration)
        controls_layout.addWidget(self.recalibrate_button)
        
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # Settings summary group
        settings_group = QGroupBox("Settings Summary")
        settings_layout = QVBoxLayout()
        
        self.settings_label = QLabel("Configure in Settings menu")
        settings_layout.addWidget(self.settings_label)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # History group
        history_group = QGroupBox("Recent History")
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        history_content = QWidget()
        history_layout = QVBoxLayout(history_content)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        history_scroll.setWidget(history_content)
        history_group.setLayout(history_scroll)
        main_layout.addWidget(history_group)
    
    def _init_status(self):
        """Initialize status indicators."""
        self.status_colors = {
            "GOOD": "#4caf50",
            "HEAD_FORWARD": "#f44336",
            "TORSO_FORWARD": "#ff9800",
            "UNKNOWN": "#9e9e9e",
            "PAUSED": "#2196f3",
            "SERVER_OFFLINE": "#f44336",
            "CAMERA_ERROR": "#f44336",
            "INSUFFICIENT_VISIBILITY": "#ff9800"
        }
    
    def update_status(self, status: object):
        """Update status display."""
        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"color: {self.status_colors.get(str(status), '#9e9e9e')}")
        self.status_changed.emit(status)
    
    def update_camera(self, frame):
        """Update camera preview."""
        if frame is not None:
            pixmap = QPixmap.fromImage(frame)
            scaled_pixmap = pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
        else:
            self.camera_label.setText("No camera connected")
            self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
