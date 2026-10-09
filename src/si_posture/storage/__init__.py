"""Settings and calibration storage."""

import json
import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Application data directory
APP_DATA_DIR = Path(__file__).parent.parent / ".si_posture"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


class SettingsManager:
    """Manages application settings."""
    
    SETTINGS_FILE = APP_DATA_DIR / "settings.json"
    
    DEFAULT_SETTINGS = {
        "camera_index": 0,
        "api_base_url": "",
        "api_key": "",
        "model": "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M",
        "timeout": 30.0,
        "capture_interval": 15,
        "consecutive_window": 4,
        "alert_threshold": 3,
        "min_abnormal_duration": 45,
        "alert_cooldown": 15,
        "windows_notifications": True,
        "telegram_notifications": False,
        "start_minimized": True,
        "start_with_windows": False,
        "debug_mode": False
    }
    
    def __init__(self):
        self._settings: Dict[str, Any] = self.DEFAULT_SETTINGS.copy()
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from file."""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self._settings.update(loaded)
            except Exception:
                pass
    
    def _save_settings(self):
        """Save settings to file."""
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(self._settings, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value."""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value."""
        self._settings[key] = value
        self._save_settings()
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()


class CalibrationManager:
    """Manages posture calibration data."""
    
    CALIBRATION_DIR = APP_DATA_DIR / "calibration"
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    
    def __init__(self):
        self._db_path = APP_DATA_DIR / "history.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calibration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                camera_index INTEGER NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posture_status TEXT NOT NULL,
                detected_change TEXT,
                alert_triggered BOOLEAN DEFAULT 0,
                inference_duration_ms REAL,
                error_state TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_calibration(self, image_data: bytes, camera_index: int):
        """Save calibration image."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO calibration (image_data, camera_index) VALUES (?, ?)',
            (image_data, camera_index)
        )
        
        conn.commit()
        conn.close()
    
    def get_calibration(self) -> Optional[bytes]:
        """Get stored calibration image."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT image_data FROM calibration ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0]
        return None
    
    def delete_calibration(self):
        """Delete calibration data."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM calibration')
        
        conn.commit()
        conn.close()
    
    def add_history_entry(
        self,
        posture_status: str,
        detected_change: Optional[str] = None,
        alert_triggered: bool = False,
        inference_duration_ms: Optional[float] = None,
        error_state: Optional[str] = None
    ):
        """Add entry to history."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO history 
            (posture_status, detected_change, alert_triggered, inference_duration_ms, error_state)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            posture_status,
            detected_change,
            1 if alert_triggered else 0,
            inference_duration_ms,
            error_state
        ))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 100) -> list:
        """Get recent history entries."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,))
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'posture_status': row[2],
                'detected_change': row[3],
                'alert_triggered': bool(row[4]),
                'inference_duration_ms': row[5],
                'error_state': row[6]
            })
        
        conn.close()
        return results
    
    def clear_history(self):
        """Clear all history."""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM history')
        
        conn.commit()
        conn.close()
