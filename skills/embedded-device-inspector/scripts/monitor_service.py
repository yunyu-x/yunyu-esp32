#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills/embedded-device-inspector/scripts/monitor_service.py
-----------------------------------------------------------
Embedded Diagnostic Monitor Service for M5Stack StickS3 (ESP32-S3).
Forwarding wrapper to scripts/embedded_monitor_service.py.
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from embedded_monitor_service import EmbeddedMonitor, main

if __name__ == "__main__":
    monitor = EmbeddedMonitor()
    monitor.run()
