# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

block_cipher = None

spec = {
    'name': 'SI-Posture',
    'version': '0.1.0',
    'windowed': True,
    'noconsole': True,
    'hidden': True,
    'datas': [
        ('src/si_posture', '.')
    ]
}
