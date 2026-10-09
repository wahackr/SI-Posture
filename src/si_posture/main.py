"""SI-Posture - Windows AI Posture Monitoring Application."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from si_posture.storage import SettingsManager, CalibrationManager
from si_posture.ai import AIClient
from si_posture.monitoring import MonitoringState, PostureEvaluator
from si_posture.notifications import NotificationManager
from si_posture.ui import SetupWizard, MainWindow


def run_setup_wizard():
    """Run first-launch setup wizard."""
    app = QApplication.instance() or QApplication([])
    
    wizard = SetupWizard()
    if wizard.exec() == QDialog.Accepted:
        settings = wizard.get_settings()
        settings_manager = SettingsManager()
        settings_manager._settings.update(settings)
        settings_manager._save_settings()
        
        # Save calibration if done
        calibration_manager = CalibrationManager()
        if hasattr(wizard, 'get_calibration'):
            calibration_data = wizard.get_calibration()
            if calibration_data:
                calibration_manager.save_calibration(calibration_data, settings['camera_index'])
        
        return settings
    return None


def create_ai_client(settings: dict):
    """Create AI client with settings."""
    return AIClient(
        base_url=settings['api_base_url'],
        api_key=settings.get('api_key'),
        timeout=settings.get('timeout', 30.0),
        model=settings.get('model')
    )


def create_monitoring_state(settings: dict, evaluator: PostureEvaluator):
    """Create monitoring state with settings."""
    return MonitoringState(
        capture_interval_seconds=settings.get('capture_interval', 15),
        evaluator=evaluator
    )


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("SI-Posture")
    app.setOrganizationName("SI-Posture")
    
    # Check if first launch
    settings_manager = SettingsManager()
    is_first_launch = not settings_manager.SETTINGS_FILE.exists()
    
    if is_first_launch:
        print("Running first-launch setup wizard...")
        run_setup_wizard()
        print("Setup complete!")
    else:
        # Load existing settings
        settings = settings_manager.get_settings()
    
    # Validate required settings
    if not settings.get('api_base_url'):
        print("Error: AI server URL not configured")
        sys.exit(1)
    
    if not CalibrationManager().get_calibration():
        print("Error: No calibration data found. Please recalibrate.")
        sys.exit(1)
    
    # Create evaluator with settings
    evaluator = PostureEvaluator(
        consecutive_window=settings.get('consecutive_window', 4),
        alert_threshold=settings.get('alert_threshold', 3),
        min_abnormal_duration_seconds=settings.get('min_abnormal_duration', 45),
        alert_cooldown_minutes=settings.get('alert_cooldown', 15)
    )
    
    # Create monitoring state
    monitoring_state = create_monitoring_state(settings, evaluator)
    
    # Create AI client
    ai_client = create_ai_client(settings)
    
    # Create notification manager
    notification_manager = NotificationManager()
    notification_manager.set_windows_enabled(settings.get('windows_notifications', True))
    if settings.get('telegram_notifications'):
        notification_manager.set_telegram_config(
            settings.get('telegram_token', ''),
            settings.get('telegram_chat_id', '')
        )
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Connect signals
    window.status_changed.connect(lambda status: window.update_status(status))
    
    # Start monitoring if not minimized
    if not settings.get('start_minimized', True):
        monitoring_state.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
