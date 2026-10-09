"""Windows and Telegram notifications."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from PyQt6.QtGui import QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False


class NotificationError(Exception):
    """Notification delivery error."""
    pass


class WindowsNotification:
    """Windows notification handler."""
    
    @staticmethod
    def show_notification(title: str, message: str, is_critical: bool = False):
        """Show Windows notification using Qt."""
        if not HAS_QT:
            raise NotificationError("Qt not available for Windows notifications")
        
        app = QApplication.instance() or QApplication([])
        
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import Qt
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setInformativeText("")
        msg_box.setIcon(QMessageBox.Icon.Information if not is_critical else QMessageBox.Icon.Critical)
        msg_box.exec()
    
    @staticmethod
    def show_tray_notification(title: str, message: str, icon: str = "information"):
        """Show notification in system tray."""
        if not HAS_QT:
            raise NotificationError("Qt not available for system tray")
        
        app = QApplication.instance() or QApplication([])
        
        from PyQt6.QtWidgets import QSystemTrayIcon
        from PyQt6.QtCore import Qt
        
        tray_icon = QSystemTrayIcon(app)
        tray_icon.showMessage(title, message, QSystemTrayIcon.Icon.Information, 5000)
        tray_icon.closeMessage()


class TelegramNotification:
    """Telegram bot notification handler."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def _build_message(self, timestamp: str, issue: str, explanation: str, duration: str) -> str:
        """Build Telegram message."""
        return f"""🔔 *Posture Alert*

🕐 Time: {timestamp}

⚠️ Issue: {issue}

📝 {explanation}

⏱️ Duration: {duration}

---
*SI-Posture Reminder*"""
    
    def send(self, timestamp: str, issue: str, explanation: str, duration: str):
        """Send notification to Telegram."""
        import requests
        
        message = self._build_message(timestamp, issue, explanation, duration)
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise NotificationError(f"Telegram send failed: {str(e)}")


class NotificationManager:
    """Unified notification manager."""
    
    def __init__(self):
        self.windows_enabled = True
        self.telegram_enabled = False
        self.telegram_bot_token: Optional[str] = None
        self.telegram_chat_id: Optional[str] = None
    
    def set_windows_enabled(self, enabled: bool):
        """Enable/disable Windows notifications."""
        self.windows_enabled = enabled
    
    def set_telegram_config(self, token: str, chat_id: str):
        """Configure Telegram notifications."""
        self.telegram_enabled = True
        self.telegram_bot_token = token
        self.telegram_chat_id = chat_id
    
    def show_alert(self, title: str, message: str, is_critical: bool = False):
        """Show alert notification."""
        if self.windows_enabled:
            try:
                WindowsNotification.show_notification(title, message, is_critical)
            except NotificationError:
                pass
    
    def show_posture_reminder(self, issue: str, explanation: str):
        """Show gentle posture reminder."""
        title = "Posture Reminder"
        message = f"{issue}: {explanation}"
        self.show_alert(title, message, is_critical=False)
    
    def send_telegram_alert(self, timestamp: str, issue: str, explanation: str, duration: str):
        """Send Telegram alert."""
        if not self.telegram_enabled:
            return
        
        try:
            telegram = TelegramNotification(self.telegram_bot_token, self.telegram_chat_id)
            telegram.send(timestamp, issue, explanation, duration)
        except NotificationError:
            pass  # Don't interrupt monitoring
