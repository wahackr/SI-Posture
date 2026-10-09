"""Setup wizard for first-launch configuration."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox, QFileDialog, QProgressBar,
    QMessageBox, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..camera import CameraEnumerator, Camera
from ..storage import SettingsManager, CalibrationManager


class SetupWizard(QDialog):
    """First-launch setup wizard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup Wizard")
        self.setModal(True)
        self.setMinimumSize(800, 700)
        
        self._steps = [
            "Camera Setup",
            "AI Server Configuration", 
            "Posture Calibration",
            "Monitoring Preferences"
        ]
        self._current_step = 0
        
        self.calibration_images = []
        self.capture_count = 0
    
    def next_step(self):
        """Move to next step."""
        self._current_step += 1
        self._update_ui()
    
    def previous_step(self):
        """Move to previous step."""
        self._current_step -= 1
        self._update_ui()
    
    def _update_ui(self):
        """Update UI based on current step."""
        self.setWindowTitle(f"Setup Wizard - Step {self._current_step + 1}/{len(self._steps)}")
        
        # Progress bar
        progress = self._current_step + 1
        self.progress_bar.setValue(progress * 25)
        self.progress_bar.setMaximum(len(self._steps) * 25)
        
        # Step title
        self.step_label.setText(self._steps[self._current_step])
        
        # Clear previous content
        for widget in self.central_widget.layout().widget():
            self.central_widget.layout().removeWidget(widget)
        
        self._setup_step_ui()
    
    def _setup_step_ui(self):
        """Setup UI for current step."""
        layout = QVBoxLayout()
        
        if self._current_step == 0:
            self._setup_camera_step(layout)
        elif self._current_step == 1:
            self._setup_ai_step(layout)
        elif self._current_step == 2:
            self._setup_calibration_step(layout)
        elif self._current_step == 3:
            self._setup_preferences_step(layout)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        if self._current_step == 0:
            nav_layout.addStretch()
        else:
            prev_btn = QPushButton("Previous")
            prev_btn.clicked.connect(self.previous_step)
            nav_layout.addWidget(prev_btn)
        
        nav_layout.addStretch()
        
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(next_btn)
        
        if self._current_step == len(self._steps) - 1:
            finish_btn = QPushButton("Finish Setup")
            finish_btn.clicked.connect(self.finish)
            nav_layout.addWidget(finish_btn)
        
        layout.addLayout(nav_layout)
        self.central_widget.setLayout(layout)
    
    def _setup_camera_step(self, layout):
        """Setup camera selection step."""
        group = QGroupBox("Select Camera")
        form = QFormLayout()
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["No cameras found"])
        
        cameras = CameraEnumerator.enumerate_cameras()
        for idx, (index, name) in enumerate(cameras):
            self.camera_combo.addItem(f"Camera {index}: {name}", index)
        
        form.addRow("Camera:", self.camera_combo)
        
        # Live preview
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout()
        
        self.camera_preview = QLabel()
        self.camera_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_preview.setMinimumSize(640, 480)
        
        self.preview_status = QLabel("Starting camera...")
        preview_layout.addWidget(self.preview_status)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addWidget(group)
    
    def _setup_ai_step(self, layout):
        """Setup AI server configuration step."""
        group = QGroupBox("AI Server Configuration")
        form = QFormLayout()
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("http://192.168.1.100:8083/v1")
        form.addRow("API Base URL:", self.api_url_input)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key (optional)")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("API Key:", self.api_key_input)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Select Model..."])
        form.addRow("Model:", self.model_combo)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 120)
        self.timeout_spin.setValue(30)
        form.addRow("Timeout (seconds):", self.timeout_spin)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.refresh_models_btn = QPushButton("Refresh Models")
        self.refresh_models_btn.clicked.connect(self.refresh_models)
        btn_layout.addWidget(self.refresh_models_btn)
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_connection_btn)
        
        form.addRow("", btn_layout)
        
        group.setLayout(form)
        layout.addWidget(group)
    
    def _setup_calibration_step(self, layout):
        """Setup posture calibration step."""
        instruction = QLabel("Sit in a comfortable, upright working position with your head balanced over your shoulders. Keep your shoulders relaxed and look at your normal screen position.")
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(instruction)
        
        # Countdown
        countdown_group = QGroupBox("Countdown")
        countdown_layout = QVBoxLayout()
        
        self.countdown_label = QLabel("Ready...")
        self.countdown_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        countdown_layout.addWidget(self.countdown_label)
        
        self.countdown_progress = QProgressBar()
        self.countdown_progress.setVisible(True)
        countdown_layout.addWidget(self.countdown_progress)
        
        countdown_group.setLayout(countdown_layout)
        layout.addWidget(countdown_group)
        
        # Capture controls
        capture_group = QGroupBox("Capture Images")
        capture_layout = QVBoxLayout()
        
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.clicked.connect(self.capture_image)
        capture_layout.addWidget(self.capture_button)
        
        self.capture_count_label = QLabel("Captured: 0/3")
        capture_layout.addWidget(self.capture_count_label)
        
        capture_group.setLayout(capture_group)
        layout.addWidget(capture_group)
        
        # Image review
        review_group = QGroupBox("Review Captured Images")
        review_layout = QVBoxLayout()
        
        self.image_list = QListWidget()
        review_layout.addWidget(self.image_list)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
    
    def _setup_preferences_step(self, layout):
        """Setup monitoring preferences step."""
        group = QGroupBox("Monitoring Preferences")
        form = QFormLayout()
        
        self.capture_interval_spin = QSpinBox()
        self.capture_interval_spin.setRange(5, 120)
        self.capture_interval_spin.setValue(15)
        form.addRow("Capture interval (seconds):", self.capture_interval_spin)
        
        self.window_spin = QSpinBox()
        self.window_spin.setRange(2, 10)
        self.window_spin.setValue(4)
        form.addRow("Consecutive evaluation window:", self.window_spin)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 10)
        self.threshold_spin.setValue(3)
        form.addRow("Alert threshold:", self.threshold_spin)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 300)
        self.duration_spin.setValue(45)
        form.addRow("Minimum abnormal duration (seconds):", self.duration_spin)
        
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setRange(1, 120)
        self.cooldown_spin.setValue(15)
        form.addRow("Alert cooldown (minutes):", self.cooldown_spin)
        
        form.addRow("", QHBoxLayout())
        
        self.windows_notifications_cb = QCheckBox("Windows notifications")
        self.windows_notifications_cb.setChecked(True)
        form.addRow("Windows notifications:", self.windows_notifications_cb)
        
        self.telegram_notifications_cb = QCheckBox("Telegram notifications")
        self.telegram_notifications_cb.setChecked(False)
        form.addRow("Telegram notifications:", self.telegram_notifications_cb)
        
        self.start_minimized_cb = QCheckBox("Start minimized to tray")
        self.start_minimized_cb.setChecked(True)
        form.addRow("Start minimized to tray:", self.start_minimized_cb)
        
        group.setLayout(form)
        layout.addWidget(group)
    
    def finish(self):
        """Finish setup and accept."""
        self.accept()
    
    def get_settings(self) -> dict:
        """Collect settings from wizard."""
        settings = {
            "camera_index": self.camera_combo.currentData(),
            "api_base_url": self.api_url_input.text(),
            "api_key": self.api_key_input.text(),
            "model": self.model_combo.currentData(),
            "timeout": self.timeout_spin.value(),
            "capture_interval": self.capture_interval_spin.value(),
            "consecutive_window": self.window_spin.value(),
            "alert_threshold": self.threshold_spin.value(),
            "min_abnormal_duration": self.duration_spin.value(),
            "alert_cooldown": self.cooldown_spin.value(),
            "windows_notifications": self.windows_notifications_cb.isChecked(),
            "telegram_notifications": self.telegram_notifications_cb.isChecked(),
            "start_minimized": self.start_minimized_cb.isChecked()
        }
        return settings
    
    def start_calibration(self):
        """Start calibration countdown."""
        # Capture 3 images over 5 seconds
        for i in range(3):
            self.capture_image()
            import time
            time.sleep(1.5)
        
        # Show images for review
        self.show_images_for_review()
    
    def capture_image(self):
        """Capture single image."""
        # Get camera and capture
        try:
            camera = Camera(int(self.camera_combo.currentData()))
            camera.open()
            
            frame = camera.get_frame_encoded()
            if frame:
                self.image_list.addItem(f"Image {self.capture_count + 1}")
                self.capture_count += 1
                
                # Save temporarily for review
                self.calibration_images.append(frame)
            
            camera.close()
        except Exception:
            pass
    
    def show_images_for_review(self):
        """Show captured images for selection."""
        # Display images in list
        for i, img_data in enumerate(self.calibration_images):
            self.image_list.addItem(f"Image {i + 1}")
        
        # Allow user to select one
        selected = self.image_list.currentRow()
        if selected >= 0 and len(self.calibration_images) > 0:
            self.save_calibration(self.calibration_images[selected])
    
    def save_calibration(self, image_data: bytes):
        """Save calibration image."""
        camera_idx = int(self.camera_combo.currentData())
        calibration_manager = CalibrationManager()
        calibration_manager.save_calibration(image_data, camera_idx)
        
        QMessageBox.information(self, "Success", "Calibration saved successfully!")
        self.accept()


# Fix missing import
from PyQt6.QtWidgets import QLineEdit
