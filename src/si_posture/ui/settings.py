"""Settings dialog for application configuration."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox, QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt
from ..storage import SettingsManager


class SettingsDialog(QDialog):
    """Application settings dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        self.settings = SettingsManager()
        self._load_settings()
        self._setup_ui()
    
    def _load_settings(self):
        """Load current settings."""
        settings = self.settings.get_settings()
        
        self.camera_index_combo.setCurrentData(settings.get("camera_index", 0))
        self.api_url_input.setText(settings.get("api_base_url", ""))
        self.api_key_input.setText(settings.get("api_key", ""))
        self.model_combo.setCurrentData(settings.get("model", "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M"))
        self.timeout_spin.setValue(settings.get("timeout", 30.0))
        self.capture_interval_spin.setValue(settings.get("capture_interval", 15))
        self.window_spin.setValue(settings.get("consecutive_window", 4))
        self.threshold_spin.setValue(settings.get("alert_threshold", 3))
        self.duration_spin.setValue(settings.get("min_abnormal_duration", 45))
        self.cooldown_spin.setValue(settings.get("alert_cooldown", 15))
        self.windows_notifications_cb.setChecked(settings.get("windows_notifications", True))
        self.telegram_notifications_cb.setChecked(settings.get("telegram_notifications", False))
        self.start_minimized_cb.setChecked(settings.get("start_minimized", True))
        self.debug_mode_cb.setChecked(settings.get("debug_mode", False))
    
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout()
        
        # Camera settings
        camera_group = QGroupBox("Camera Settings")
        camera_form = QFormLayout()
        
        camera_form.addRow("Camera:", self.camera_index_combo)
        camera_group.setLayout(camera_form)
        layout.addWidget(camera_group)
        
        # AI settings
        ai_group = QGroupBox("AI Server Settings")
        ai_form = QFormLayout()
        
        ai_form.addRow("API Base URL:", self.api_url_input)
        api_key_group = QGroupBox("API Key")
        api_key_layout = QVBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addStretch()
        api_key_group.setLayout(api_key_layout)
        ai_form.addRow("API Key:", api_key_group)
        
        ai_form.addRow("Model:", self.model_combo)
        ai_form.addRow("Timeout (seconds):", self.timeout_spin)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.test_connection_btn)
        ai_form.addRow("", btn_layout)
        
        ai_group.setLayout(ai_form)
        layout.addWidget(ai_group)
        
        # Monitoring settings
        monitoring_group = QGroupBox("Monitoring Settings")
        monitoring_form = QFormLayout()
        
        monitoring_form.addRow("Capture interval (seconds):", self.capture_interval_spin)
        monitoring_form.addRow("Consecutive window:", self.window_spin)
        monitoring_form.addRow("Alert threshold:", self.threshold_spin)
        monitoring_form.addRow("Min abnormal duration (seconds):", self.duration_spin)
        monitoring_form.addRow("Alert cooldown (minutes):", self.cooldown_spin)
        
        monitoring_group.setLayout(monitoring_form)
        layout.addWidget(monitoring_group)
        
        # Notification settings
        notification_group = QGroupBox("Notification Settings")
        notification_form = QFormLayout()
        
        notification_form.addRow("Windows notifications:", self.windows_notifications_cb)
        self.telegram_notifications_cb = QCheckBox("Telegram notifications")
        notification_form.addRow("Telegram notifications:", self.telegram_notifications_cb)
        
        telegram_group = QGroupBox("Telegram Configuration")
        telegram_form = QFormLayout()
        
        self.telegram_token_input = QLineEdit()
        self.telegram_token_input.setPlaceholderText("Bot Token")
        telegram_form.addRow("Bot Token:", self.telegram_token_input)
        
        self.telegram_chat_input = QLineEdit()
        self.telegram_chat_input.setPlaceholderText("Chat ID")
        telegram_form.addRow("Chat ID:", self.telegram_chat_input)
        
        telegram_group.setLayout(telegram_form)
        notification_group.setLayout(notification_form)
        layout.addWidget(notification_group)
        
        layout.addWidget(telegram_group)
        
        # Other settings
        other_group = QGroupBox("Other Settings")
        other_form = QFormLayout()
        
        other_form.addRow("Start minimized to tray:", self.start_minimized_cb)
        self.debug_mode_cb = QCheckBox("Debug mode")
        other_form.addRow("Debug mode:", self.debug_mode_cb)
        
        other_group.setLayout(other_form)
        layout.addWidget(other_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        btn_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_defaults)
        btn_layout.addWidget(self.reset_button)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save(self):
        """Save settings."""
        self.settings.set("camera_index", self.camera_index_combo.currentData())
        self.settings.set("api_base_url", self.api_url_input.text())
        self.settings.set("api_key", self.api_key_input.text())
        self.settings.set("model", self.model_combo.currentData())
        self.settings.set("timeout", self.timeout_spin.value())
        self.settings.set("capture_interval", self.capture_interval_spin.value())
        self.settings.set("consecutive_window", self.window_spin.value())
        self.settings.set("alert_threshold", self.threshold_spin.value())
        self.settings.set("min_abnormal_duration", self.duration_spin.value())
        self.settings.set("alert_cooldown", self.cooldown_spin.value())
        self.settings.set("windows_notifications", self.windows_notifications_cb.isChecked())
        self.settings.set("telegram_notifications", self.telegram_notifications_cb.isChecked())
        self.settings.set("start_minimized", self.start_minimized_cb.isChecked())
        self.settings.set("debug_mode", self.debug_mode_cb.isChecked())
        
        if self.telegram_notifications_cb.isChecked():
            self.settings.set("telegram_token", self.telegram_token_input.text())
            self.settings.set("telegram_chat_id", self.telegram_chat_input.text())
        
        self.accept()
    
    def reset_defaults(self):
        """Reset to default settings."""
        self.settings.reset_to_defaults()
        self._load_settings()
        QMessageBox.information(self, "Success", "Settings reset to defaults!")
