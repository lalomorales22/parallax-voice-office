#!/usr/bin/env python3
"""
Parallax Voice Office - Distributed AI Voice Assistant
Single file with web interface for local network access
Run: python obp-GUI.py
Access: http://your-ip:5001
"""

import json
import yaml
import time
import logging
import os
import re
import requests
import sqlite3
import threading
import subprocess
import socket
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import traceback

# Parallax SDK imports
try:
    import grpc
    from parallax import Client as ParallaxClient
    PARALLAX_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Parallax SDK not available: {e}")
    logger.warning("Falling back to Ollama compatibility mode")
    PARALLAX_AVAILABLE = False

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("python-dotenv not installed, environment variables from .env file won't be loaded")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums
class TaskType(Enum):
    SEARCH = "search"
    PROCESS = "process"
    CREATE = "create"
    CHAIN = "chain"
    CODE = "code"
    CUSTOM = "custom"

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

# Data classes
@dataclass
class Task:
    id: str
    type: TaskType
    content: str
    config_name: str = None
    status: TaskStatus = TaskStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    processing_time: float = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parallax Voice Office - AI Voice Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --background: #0a0a0a;
            --foreground: #fafafa;
            --muted: #171717;
            --muted-foreground: #a3a3a3;
            --border: #262626;
            --input: #171717;
            --primary: #3b82f6;
            --primary-foreground: #ffffff;
            --secondary: #1f1f1f;
            --secondary-foreground: #e5e5e5;
            --accent: #262626;
            --accent-foreground: #fafafa;
            --destructive: #dc2626;
            --destructive-foreground: #ffffff;
            --ring: #3b82f6;
            --radius: 0.75rem;
            --glow: rgba(59, 130, 246, 0.5);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--background);
            background-image: 
                radial-gradient(ellipse at top, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at bottom, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
            color: var(--foreground);
            line-height: 1.5;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            border-bottom: 1px solid var(--border);
            padding-bottom: 2rem;
            margin-bottom: 2rem;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: var(--muted-foreground);
            font-size: 0.875rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
        }
        
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Custom Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(23, 23, 23, 0.5);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 5px;
            border: 2px solid rgba(23, 23, 23, 0.5);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        }
        
        /* Firefox scrollbar */
        * {
            scrollbar-width: thin;
            scrollbar-color: #3b82f6 rgba(23, 23, 23, 0.5);
        }
        
        .card {
            background: rgba(23, 23, 23, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            animation: fadeIn 0.3s ease-out;
        }
        
        .card-header {
            margin-bottom: 1rem;
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .card-description {
            color: var(--muted-foreground);
            font-size: 0.875rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border);
            border-radius: calc(var(--radius) - 2px);
            font-size: 0.875rem;
            transition: border-color 0.15s;
            background: var(--input);
            color: var(--foreground);
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--ring);
            box-shadow: 0 0 0 3px var(--glow);
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
            font-family: inherit;
        }
        
        .button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            border-radius: calc(var(--radius) - 2px);
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.15s;
            text-decoration: none;
        }
        
        .button-primary {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: var(--primary-foreground);
            border: none;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }
        
        .button-primary:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 0 25px rgba(59, 130, 246, 0.5);
            transform: translateY(-1px);
        }
        
        .button-secondary {
            background: var(--secondary);
            color: var(--secondary-foreground);
            border-color: var(--border);
        }
        
        .button-secondary:hover {
            background: var(--accent);
        }
        
        .button-destructive {
            background: var(--destructive);
            color: var(--destructive-foreground);
        }
        
        .button-destructive:hover {
            opacity: 0.9;
        }
        
        .button-ghost {
            background: transparent;
            color: var(--foreground);
        }
        
        .button-ghost:hover {
            background: var(--accent);
        }
        
        .button-group {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .task-type-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .task-type-btn {
            padding: 0.75rem;
            text-align: center;
            border: 2px solid var(--border);
            background: var(--background);
            border-radius: calc(var(--radius) - 2px);
            cursor: pointer;
            transition: all 0.15s;
            font-weight: 500;
        }
        
        .task-type-btn:hover {
            background: var(--secondary);
        }
        
        .task-type-btn.active {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border-color: #3b82f6;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(31, 31, 31, 0.8) 0%, rgba(38, 38, 38, 0.6) 100%);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-radius: calc(var(--radius) - 2px);
            text-align: center;
            border: 1px solid var(--border);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: var(--muted-foreground);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .task-list {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            background: rgba(23, 23, 23, 0.3);
            backdrop-filter: blur(5px);
        }
        
        .task-item {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.15s;
        }
        
        .task-item:last-child {
            border-bottom: none;
        }
        
        .task-item:hover {
            background: var(--secondary);
        }
        
        .task-info {
            flex: 1;
        }
        
        .task-id {
            font-size: 0.75rem;
            color: var(--muted-foreground);
            font-family: monospace;
        }
        
        .task-content {
            margin: 0.25rem 0;
            font-size: 0.875rem;
        }
        
        .task-meta {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            font-weight: 500;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .badge-default {
            background: var(--secondary);
            color: var(--secondary-foreground);
        }
        
        .badge-pending {
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.3);
        }
        
        .badge-processing {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            animation: pulse 2s infinite;
        }
        
        .badge-completed {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .badge-failed {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--muted-foreground);
        }
        
        .metadata-inputs {
            display: grid;
            gap: 0.5rem;
        }
        
        .metadata-row {
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 0.5rem;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .icon-button {
            width: 2rem;
            height: 2rem;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: calc(var(--radius) - 2px);
        }
        
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: rgba(31, 31, 31, 0.95);
            color: var(--foreground);
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s;
            z-index: 1000;
            max-width: 400px;
            backdrop-filter: blur(10px);
        }
        
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .toast.error {
            background: var(--destructive);
            color: var(--destructive-foreground);
        }
        
        .tabs {
            border-bottom: 1px solid var(--border);
            margin-bottom: 1.5rem;
        }
        
        .tab-list {
            display: flex;
            gap: 2rem;
        }
        
        .tab-trigger {
            padding: 0.5rem 0;
            border-bottom: 2px solid transparent;
            background: none;
            border-top: none;
            border-left: none;
            border-right: none;
            cursor: pointer;
            font-weight: 500;
            color: var(--muted-foreground);
            transition: all 0.15s;
        }
        
        .tab-trigger:hover {
            color: var(--foreground);
        }
        
        .tab-trigger.active {
            color: #3b82f6;
            border-bottom-color: #3b82f6;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .server-info {
            background: linear-gradient(135deg, rgba(31, 31, 31, 0.8) 0%, rgba(38, 38, 38, 0.6) 100%);
            padding: 1rem;
            border-radius: var(--radius);
            margin-bottom: 2rem;
            font-family: monospace;
            font-size: 0.875rem;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }
        
        .loader {
            width: 1rem;
            height: 1rem;
            border: 2px solid rgba(59, 130, 246, 0.2);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            display: inline-block;
            margin-left: 0.5rem;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .result-viewer {
            background: var(--secondary);
            padding: 1rem;
            border-radius: calc(var(--radius) - 2px);
            font-family: monospace;
            font-size: 0.75rem;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 300px;
            overflow-y: auto;
        }

        /* Voice Interface Styles */
        .voice-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 1rem;
        }

        .mic-button {
            width: 4rem;
            height: 4rem;
            border-radius: 50%;
            border: 3px solid var(--primary);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .mic-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        }

        .mic-button.listening {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            border-color: #ef4444;
            animation: pulse-glow 1.5s infinite;
        }

        .mic-button.processing {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            border-color: #f59e0b;
        }

        @keyframes pulse-glow {
            0%, 100% {
                box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
            }
            50% {
                box-shadow: 0 0 40px rgba(239, 68, 68, 0.8);
            }
        }

        .voice-status {
            flex: 1;
            padding: 1rem;
            background: rgba(23, 23, 23, 0.5);
            border-radius: calc(var(--radius) - 2px);
            border: 1px solid var(--border);
        }

        .voice-status-text {
            font-size: 0.875rem;
            color: var(--muted-foreground);
            margin-bottom: 0.5rem;
        }

        .voice-transcript {
            font-size: 0.875rem;
            color: var(--foreground);
            min-height: 1.5rem;
        }

        .voice-settings-panel {
            background: rgba(23, 23, 23, 0.7);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .voice-setting-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        .voice-setting-row:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }

        .voice-setting-label {
            font-size: 0.875rem;
            font-weight: 500;
        }

        .voice-setting-description {
            font-size: 0.75rem;
            color: var(--muted-foreground);
            margin-top: 0.25rem;
        }

        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 3rem;
            height: 1.5rem;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--secondary);
            transition: 0.3s;
            border-radius: 1.5rem;
            border: 1px solid var(--border);
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 1rem;
            width: 1rem;
            left: 0.25rem;
            bottom: 0.2rem;
            background-color: var(--muted-foreground);
            transition: 0.3s;
            border-radius: 50%;
        }

        .toggle-switch input:checked + .toggle-slider {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-color: #3b82f6;
        }

        .toggle-switch input:checked + .toggle-slider:before {
            transform: translateX(1.5rem);
            background-color: white;
        }

        .permission-alert {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #ef4444;
            padding: 1rem;
            border-radius: calc(var(--radius) - 2px);
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }

        .compatibility-alert {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.3);
            color: #fbbf24;
            padding: 1rem;
            border-radius: calc(var(--radius) - 2px);
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎙️ Parallax Voice Office</h1>
            <p class="subtitle">Your voice-enabled AI assistant powered by distributed computing • Accessible at {{ server_info }}</p>
        </header>
        
        <div class="server-info">
            <strong>Server Status:</strong> Running<br>
            <strong>Model:</strong> {{ model }}<br>
            <strong>Access URL:</strong> http://{{ server_info }}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-pending">0</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-processing">0</div>
                <div class="stat-label">Processing</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-completed">0</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-failed">0</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Add New Task</h2>
                    <p class="card-description">Speak or type your task</p>
                </div>

                <!-- Voice Controls -->
                <div id="voice-compatibility-alert" class="compatibility-alert" style="display: none;">
                    ⚠️ Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.
                </div>

                <div id="voice-permission-alert" class="permission-alert" style="display: none;">
                    🎤 Microphone access denied. Please allow microphone permissions to use voice input.
                </div>

                <div class="voice-controls">
                    <button class="mic-button" id="mic-button" onclick="toggleVoiceRecording()" title="Click to speak">
                        <span id="mic-icon">🎤</span>
                    </button>
                    <div class="voice-status">
                        <div class="voice-status-text" id="voice-status-text">Click the microphone to speak your task</div>
                        <div class="voice-transcript" id="voice-transcript"></div>
                    </div>
                </div>

                <form id="task-form">
                    <div class="form-group">
                        <label for="command">Describe Your Task (Type or Speak)</label>
                        <textarea id="command" name="command" placeholder="Example: Research the latest AI developments and create a comprehensive report..." style="min-height: 120px;" required></textarea>
                    </div>

                    <div class="button-group">
                        <button type="button" class="button button-primary" onclick="interpretTask()">Interpret Task</button>
                        <button type="button" class="button button-secondary" onclick="clearAll()">Clear</button>
                        <button type="button" class="button button-ghost" onclick="toggleVoiceSettings()">⚙️ Voice Settings</button>
                    </div>
                </form>

                <!-- Voice Settings Panel -->
                <div id="voice-settings-panel" class="voice-settings-panel" style="display: none; margin-top: 1rem;">
                    <h3 style="margin-bottom: 1rem;">Voice Settings</h3>

                    <div class="voice-setting-row">
                        <div>
                            <div class="voice-setting-label">Voice Feedback</div>
                            <div class="voice-setting-description">Hear spoken confirmations and responses</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="voice-feedback-toggle" onchange="saveVoiceSettings()">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="voice-setting-row">
                        <div>
                            <div class="voice-setting-label">Auto-detect Task Type</div>
                            <div class="voice-setting-description">Automatically determine task type from speech</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="auto-detect-toggle" checked onchange="saveVoiceSettings()">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="voice-setting-row">
                        <div>
                            <div class="voice-setting-label">Continuous Listening</div>
                            <div class="voice-setting-description">Keep listening until you click stop</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="continuous-mode-toggle" onchange="saveVoiceSettings()">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="voice-setting-row">
                        <div>
                            <div class="voice-setting-label">Language</div>
                            <div class="voice-setting-description">Select your preferred language</div>
                        </div>
                        <select id="voice-language-select" onchange="saveVoiceSettings()" style="width: 200px; padding: 0.5rem; border-radius: 0.25rem; background: var(--input); color: var(--foreground); border: 1px solid var(--border);">
                            <option value="en-US">English (US)</option>
                            <option value="en-GB">English (UK)</option>
                            <option value="es-ES">Spanish (Spain)</option>
                            <option value="es-MX">Spanish (Mexico)</option>
                            <option value="fr-FR">French</option>
                            <option value="de-DE">German</option>
                            <option value="it-IT">Italian</option>
                            <option value="pt-BR">Portuguese (Brazil)</option>
                            <option value="ja-JP">Japanese</option>
                            <option value="zh-CN">Chinese (Simplified)</option>
                            <option value="ko-KR">Korean</option>
                        </select>
                    </div>
                </div>
                
                <div id="confirmation-area" style="display: none; margin-top: 2rem; padding: 1.5rem; background: var(--secondary); border-radius: var(--radius);">
                    <h3 style="margin-bottom: 1rem;">Task Interpretation</h3>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Type:</strong>
                        <span id="interpreted-type" class="badge badge-default" style="margin-left: 0.5rem;"></span>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Content:</strong>
                        <div id="interpreted-content" style="margin-top: 0.5rem; padding: 0.75rem; background: var(--background); border-radius: calc(var(--radius) - 2px); font-size: 0.875rem;"></div>
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <strong>Metadata:</strong>
                        <div id="interpreted-metadata" style="margin-top: 0.5rem; padding: 0.75rem; background: var(--background); border-radius: calc(var(--radius) - 2px); font-family: monospace; font-size: 0.75rem;"></div>
                    </div>
                    
                    <div class="button-group">
                        <button class="button button-primary" onclick="confirmAndQueue()">Add to Queue</button>
                        <button class="button button-secondary" onclick="clearConfirmation()">Clear</button>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Processing Controls</h2>
                    <p class="card-description">Manage task processing</p>
                </div>
                
                <div class="button-group">
                    <button id="process-btn" class="button button-primary" onclick="startProcessing()">
                        Start Processing
                    </button>
                    <button class="button button-destructive" onclick="stopProcessing()">Stop</button>
                    <button class="button button-secondary" onclick="clearCompleted()">Clear Completed</button>
                    <button class="button button-secondary" onclick="resetFailed()">Reset Failed</button>
                </div>
                
                <div style="margin-top: 1rem;">
                    <label for="auto-refresh">
                        <input type="checkbox" id="auto-refresh" checked> Auto-refresh (5s)
                    </label>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="tabs">
                <div class="tab-list">
                    <button class="tab-trigger active" onclick="switchTab('queue')">Task Queue</button>
                    <button class="tab-trigger" onclick="switchTab('results')">Results</button>
                    <button class="tab-trigger" onclick="switchTab('cluster')">🖥️  Cluster</button>
                    <button class="tab-trigger" onclick="switchTab('logs')">Logs</button>
                    <button class="tab-trigger" onclick="switchTab('files')">Files 📁</button>
                    <a href="/gallery" target="_blank" class="tab-trigger" style="text-decoration: none;">Gallery View 🎨</a>
                </div>
            </div>
            
            <div class="tab-content active" id="tab-queue">
                <div id="task-list">
                    <div class="empty-state">No tasks in queue</div>
                </div>
            </div>
            
            <div class="tab-content" id="tab-results">
                <div id="results-list">
                    <div class="empty-state">No completed tasks</div>
                </div>
            </div>
            
            <div class="tab-content" id="tab-cluster">
                <div style="margin-bottom: 1rem;">
                    <button onclick="refreshClusterStatus()" class="button button-primary">🔄 Refresh Cluster Status</button>
                </div>
                <div id="cluster-info" class="result-viewer">
                    <div class="cluster-status-card">
                        <h3>Parallax Cluster Status</h3>
                        <div id="cluster-status-content">
                            <p>Loading cluster information...</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="tab-content" id="tab-logs">
                <div class="result-viewer" id="logs-viewer">
                    Logs will appear here...
                </div>
            </div>

            <div class="tab-content" id="tab-files">
                <div style="margin-bottom: 1rem;">
                    <button onclick="refreshFiles()" class="btn">🔄 Refresh Files</button>
                    <button onclick="downloadWorkspace()" class="btn">📦 Download Workspace</button>
                </div>
                <div id="files-list">
                    <div class="empty-state">Click refresh to load workspace files</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="toast" id="toast"></div>
    
    <script>
        let processingInterval = null;
        let refreshInterval = null;
        let interpretedTask = null;

        // Voice Recognition Variables
        let recognition = null;
        let isListening = false;
        let voiceSettings = {
            voiceFeedback: false,
            autoDetect: true,
            continuousMode: false,
            language: 'en-US'
        };
        let speechSynthesis = window.speechSynthesis;
        let voiceTimeout = null;

        // Initialize Voice Recognition
        function initVoiceRecognition() {
            // Check browser compatibility
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                document.getElementById('voice-compatibility-alert').style.display = 'block';
                document.getElementById('mic-button').disabled = true;
                document.getElementById('mic-button').style.opacity = '0.5';
                document.getElementById('mic-button').style.cursor = 'not-allowed';
                return false;
            }

            recognition = new SpeechRecognition();
            recognition.continuous = voiceSettings.continuousMode;
            recognition.interimResults = true;
            recognition.lang = voiceSettings.language;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {
                isListening = true;
                updateVoiceUI('listening');
                document.getElementById('voice-status-text').textContent = 'Listening... Speak now';

                // Set timeout for auto-stop (30 seconds)
                voiceTimeout = setTimeout(() => {
                    if (isListening) {
                        stopVoiceRecording();
                        speakFeedback('Voice input timed out');
                    }
                }, 30000);
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }

                // Update live transcript display
                document.getElementById('voice-transcript').innerHTML =
                    '<span style="color: #10b981;">' + finalTranscript + '</span>' +
                    '<span style="color: #6b7280;">' + interimTranscript + '</span>';

                // Update the textarea with final transcript
                if (finalTranscript) {
                    const currentText = document.getElementById('command').value;
                    document.getElementById('command').value = currentText + finalTranscript;
                }
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);

                if (event.error === 'not-allowed' || event.error === 'permission-denied') {
                    document.getElementById('voice-permission-alert').style.display = 'block';
                    speakFeedback('Microphone permission denied');
                } else if (event.error === 'no-speech') {
                    speakFeedback('No speech detected. Please try again.');
                } else if (event.error === 'network') {
                    speakFeedback('Network error. Please check your connection.');
                } else {
                    speakFeedback('Voice recognition error: ' + event.error);
                }

                stopVoiceRecording();
            };

            recognition.onend = function() {
                if (voiceSettings.continuousMode && isListening) {
                    // Restart if in continuous mode
                    try {
                        recognition.start();
                    } catch (e) {
                        console.error('Failed to restart recognition:', e);
                        stopVoiceRecording();
                    }
                } else {
                    stopVoiceRecording();
                }
            };

            return true;
        }

        function toggleVoiceRecording() {
            if (isListening) {
                stopVoiceRecording();
            } else {
                startVoiceRecording();
            }
        }

        function startVoiceRecording() {
            if (!recognition) {
                if (!initVoiceRecognition()) {
                    return;
                }
            }

            try {
                recognition.lang = voiceSettings.language;
                recognition.continuous = voiceSettings.continuousMode;
                recognition.start();
                speakFeedback('Listening');
            } catch (e) {
                console.error('Failed to start recognition:', e);
                speakFeedback('Failed to start voice recognition');
            }
        }

        function stopVoiceRecording() {
            if (recognition && isListening) {
                recognition.stop();
            }

            isListening = false;
            updateVoiceUI('idle');
            document.getElementById('voice-status-text').textContent = 'Click the microphone to speak your task';

            if (voiceTimeout) {
                clearTimeout(voiceTimeout);
                voiceTimeout = null;
            }

            // If there's text, offer to interpret it
            const commandText = document.getElementById('command').value.trim();
            if (commandText && voiceSettings.autoDetect) {
                setTimeout(() => {
                    speakFeedback('Task captured. Click interpret to process.');
                }, 500);
            }
        }

        function updateVoiceUI(state) {
            const micButton = document.getElementById('mic-button');
            const micIcon = document.getElementById('mic-icon');

            micButton.classList.remove('listening', 'processing');

            if (state === 'listening') {
                micButton.classList.add('listening');
                micIcon.textContent = '⏸️';
            } else if (state === 'processing') {
                micButton.classList.add('processing');
                micIcon.textContent = '⏳';
            } else {
                micIcon.textContent = '🎤';
            }
        }

        function speakFeedback(text) {
            if (!voiceSettings.voiceFeedback || !speechSynthesis) {
                return;
            }

            // Cancel any ongoing speech
            speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;

            // Try to use a voice matching the selected language
            const voices = speechSynthesis.getVoices();
            const langPrefix = voiceSettings.language.substring(0, 2);
            const matchingVoice = voices.find(voice => voice.lang.startsWith(langPrefix));
            if (matchingVoice) {
                utterance.voice = matchingVoice;
            }

            speechSynthesis.speak(utterance);
        }

        function toggleVoiceSettings() {
            const panel = document.getElementById('voice-settings-panel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }

        function saveVoiceSettings() {
            voiceSettings.voiceFeedback = document.getElementById('voice-feedback-toggle').checked;
            voiceSettings.autoDetect = document.getElementById('auto-detect-toggle').checked;
            voiceSettings.continuousMode = document.getElementById('continuous-mode-toggle').checked;
            voiceSettings.language = document.getElementById('voice-language-select').value;

            // Save to localStorage
            localStorage.setItem('voiceSettings', JSON.stringify(voiceSettings));

            // Update recognition if active
            if (recognition) {
                recognition.lang = voiceSettings.language;
                recognition.continuous = voiceSettings.continuousMode;
            }

            speakFeedback('Settings saved');
        }

        function loadVoiceSettings() {
            const saved = localStorage.getItem('voiceSettings');
            if (saved) {
                voiceSettings = JSON.parse(saved);

                document.getElementById('voice-feedback-toggle').checked = voiceSettings.voiceFeedback;
                document.getElementById('auto-detect-toggle').checked = voiceSettings.autoDetect;
                document.getElementById('continuous-mode-toggle').checked = voiceSettings.continuousMode;
                document.getElementById('voice-language-select').value = voiceSettings.language;
            }
        }

        // Load voices when available
        if (speechSynthesis) {
            speechSynthesis.onvoiceschanged = function() {
                speechSynthesis.getVoices();
            };
        }

        
        async function interpretTask() {
            const command = document.getElementById('command').value.trim();
            if (!command) {
                showToast('Please enter a task description', 'error');
                speakFeedback('Please enter a task description');
                return;
            }

            // Update voice UI to show processing
            updateVoiceUI('processing');
            speakFeedback('Interpreting your task');

            // Show loading state
            const button = event.target;
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = 'Interpreting...';

            try {
                const response = await fetch('/api/interpret_task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: command, voice_input: true})
                });

                if (response.ok) {
                    interpretedTask = await response.json();
                    displayInterpretation(interpretedTask);
                    speakFeedback('Task interpreted as ' + interpretedTask.type);
                } else {
                    const error = await response.json();
                    showToast('Failed to interpret task: ' + (error.error || 'Unknown error'), 'error');
                    speakFeedback('Failed to interpret task');
                }
            } catch (error) {
                showToast('Error: ' + error.message, 'error');
                speakFeedback('Error interpreting task');
            } finally {
                button.disabled = false;
                button.textContent = originalText;
                updateVoiceUI('idle');
            }
        }
        
        function displayInterpretation(task) {
            // Show the confirmation area
            document.getElementById('confirmation-area').style.display = 'block';
            
            // Display task type
            const typeSpan = document.getElementById('interpreted-type');
            typeSpan.textContent = task.type.toUpperCase();
            typeSpan.className = 'badge badge-default';
            
            // Display content
            document.getElementById('interpreted-content').textContent = task.content;
            
            // Display metadata
            const metadataDiv = document.getElementById('interpreted-metadata');
            if (task.metadata && Object.keys(task.metadata).length > 0) {
                metadataDiv.textContent = JSON.stringify(task.metadata, null, 2);
            } else {
                metadataDiv.textContent = 'No metadata specified';
            }
            
            // Scroll to confirmation area
            document.getElementById('confirmation-area').scrollIntoView({ behavior: 'smooth' });
        }
        
        async function confirmAndQueue() {
            if (!interpretedTask) {
                showToast('No task to queue', 'error');
                speakFeedback('No task to queue');
                return;
            }

            try {
                const response = await fetch('/api/add_task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(interpretedTask)
                });

                if (response.ok) {
                    const result = await response.json();
                    showToast(`Task queued: ${result.task_id}`);
                    speakFeedback('Task queued successfully');
                    clearAll();
                    updateStatus();
                    loadTasks();
                } else {
                    showToast('Failed to queue task', 'error');
                    speakFeedback('Failed to queue task');
                }
            } catch (error) {
                showToast('Error: ' + error.message, 'error');
                speakFeedback('Error queuing task');
            }
        }
        
        function clearConfirmation() {
            document.getElementById('confirmation-area').style.display = 'none';
            interpretedTask = null;
        }
        
        function clearAll() {
            document.getElementById('command').value = '';
            clearConfirmation();
        }
        
        function clearForm() {
            clearAll();
        }
        
        // Keep for backward compatibility but won't be used with new flow
        async function submitTask(event) {
            event.preventDefault();
            // This form submission is now handled through the interpret flow
            interpretTask();
        }
        
        async function startProcessing() {
            const processBtn = document.getElementById('process-btn');
            processBtn.disabled = true;
            processBtn.innerHTML = 'Processing... <span class="loader" style="display: inline-block;"></span>';

            try {
                const response = await fetch('/api/start_processing', {method: 'POST'});
                if (response.ok) {
                    showToast('Processing started');
                    speakFeedback('Processing started');
                    processingInterval = setInterval(updateStatus, 2000);
                    processBtn.classList.add('processing');
                }
            } catch (error) {
                showToast('Error starting processing', 'error');
                speakFeedback('Error starting processing');
                processBtn.innerHTML = 'Start Processing';
                processBtn.disabled = false;
            }
        }
        
        async function stopProcessing() {
            const processBtn = document.getElementById('process-btn');
            
            try {
                const response = await fetch('/api/stop_processing', {method: 'POST'});
                if (response.ok) {
                    showToast('Processing stopped');
                    if (processingInterval) {
                        clearInterval(processingInterval);
                        processingInterval = null;
                    }
                    processBtn.innerHTML = 'Start Processing';
                    processBtn.classList.remove('processing');
                    processBtn.disabled = false;
                }
            } catch (error) {
                showToast('Error stopping processing', 'error');
            }
        }
        
        async function clearCompleted() {
            try {
                const response = await fetch('/api/clear_completed', {method: 'POST'});
                if (response.ok) {
                    showToast('Completed tasks cleared');
                    updateStatus();
                    loadTasks();
                }
            } catch (error) {
                showToast('Error clearing tasks', 'error');
            }
        }
        
        async function resetFailed() {
            try {
                const response = await fetch('/api/reset_failed', {method: 'POST'});
                if (response.ok) {
                    showToast('Failed tasks reset');
                    updateStatus();
                    loadTasks();
                }
            } catch (error) {
                showToast('Error resetting tasks', 'error');
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    const stats = await response.json();
                    document.getElementById('stat-total').textContent = stats.total || 0;
                    document.getElementById('stat-pending').textContent = stats.pending || 0;
                    document.getElementById('stat-processing').textContent = stats.processing || 0;
                    document.getElementById('stat-completed').textContent = stats.completed || 0;
                    document.getElementById('stat-failed').textContent = stats.failed || 0;
                    
                    // Update button state based on actual processing status
                    const processBtn = document.getElementById('process-btn');
                    const isProcessing = stats.processing === true;
                    
                    if (isProcessing) {
                        processBtn.innerHTML = 'Processing... <span class="loader" style="display: inline-block;"></span>';
                        processBtn.classList.add('processing');
                        processBtn.disabled = true;
                    } else {
                        processBtn.innerHTML = 'Start Processing';
                        processBtn.classList.remove('processing');
                        processBtn.disabled = false;
                        
                        // Clear processing interval when processing stops
                        if (processingInterval) {
                            clearInterval(processingInterval);
                            processingInterval = null;
                        }
                    }
                }
            } catch (error) {
                console.error('Status update error:', error);
            }
        }
        
        
        function renderTasks(tasks) {
            const container = document.getElementById('task-list');
            
            if (tasks.length === 0) {
                container.innerHTML = '<div class="empty-state">No tasks in queue</div>';
                return;
            }
            
            container.innerHTML = '<div class="task-list">' + 
                tasks.map(task => `
                    <div class="task-item">
                        <div class="task-info">
                            <div class="task-id">${task.id}</div>
                            <div class="task-content">${task.content.substring(0, 100)}${task.content.length > 100 ? '...' : ''}</div>
                            <div class="task-meta">
                                <span class="badge badge-default">${task.type}</span>
                                <span class="badge badge-${task.status}">${task.status}</span>
                                ${task.processing_time ? `<span class="badge badge-default">${task.processing_time.toFixed(1)}s</span>` : ''}
                            </div>
                        </div>
                        <div class="task-actions" style="display: flex; gap: 0.5rem;">
                            ${task.status === 'completed' ? 
                                `<button class="button button-ghost" onclick="viewResults('${task.id}')">View</button>` : 
                                ''}
                            ${task.status === 'pending' ? 
                                `<button class="button button-ghost" onclick="editTask('${task.id}')">Edit</button>` : 
                                ''}
                            <button class="button button-ghost" onclick="deleteTask('${task.id}')" style="color: #ef4444;">Delete</button>
                        </div>
                    </div>
                `).join('') + '</div>';
        }
        
        async function viewResults(taskId) {
            try {
                const response = await fetch(`/api/task/${taskId}`);
                if (response.ok) {
                    const task = await response.json();
                    switchTab('results');
                    document.getElementById('results-list').innerHTML = 
                        `<div class="result-viewer">${JSON.stringify(task.results, null, 2)}</div>`;
                }
            } catch (error) {
                showToast('Error loading results', 'error');
            }
        }
        
        function switchTab(tabName) {
            // Update current tab tracker
            currentTab = tabName;
            
            // Update tab buttons
            document.querySelectorAll('.tab-trigger').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Find the clicked button and activate it
            const clickedButton = Array.from(document.querySelectorAll('.tab-trigger'))
                .find(btn => btn.textContent.toLowerCase().includes(tabName) || btn.onclick?.toString().includes(tabName));
            if (clickedButton) {
                clickedButton.classList.add('active');
            }
            
            // Show the correct tab content
            const tabContent = document.getElementById(`tab-${tabName}`);
            if (tabContent) {
                tabContent.classList.add('active');

                // Load content based on tab
                if (tabName === 'files') {
                    refreshFiles();
                } else if (tabName === 'results') {
                    loadCompletedTasks();
                } else if (tabName === 'cluster') {
                    onClusterTabOpen();
                }
            }
        }
        
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show' + (type === 'error' ? ' error' : '');
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
        
        // Auto-refresh
        document.getElementById('auto-refresh').addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(() => {
                    updateStatus();
                    loadTasks();
                    if (currentTab === 'files') refreshFiles();
                }, 5000);
            } else {
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                    refreshInterval = null;
                }
            }
        });
        
        // File management functions
        async function refreshFiles() {
            try {
                const response = await fetch('/api/files');
                if (response.ok) {
                    const files = await response.json();
                    displayFiles(files);
                } else {
                    showToast('Error loading files', 'error');
                }
            } catch (error) {
                console.error('Error loading files:', error);
                showToast('Error loading files', 'error');
            }
        }
        
        function displayFiles(files) {
            const filesList = document.getElementById('files-list');
            
            if (files.length === 0) {
                filesList.innerHTML = '<div class="empty-state">No files in workspace</div>';
                return;
            }
            
            filesList.innerHTML = files.map(file => `
                <div class="task-card" style="cursor: pointer; margin-bottom: 0.5rem;" onclick="downloadFile('${file.name}')">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${file.name}</strong>
                            <div style="font-size: 0.75rem; color: #666;">
                                ${formatFileSize(file.size)} • ${new Date(file.modified).toLocaleDateString()}
                            </div>
                        </div>
                        <button class="btn" onclick="event.stopPropagation(); downloadFile('${file.name}')" style="font-size: 0.75rem;">📥 Download</button>
                    </div>
                </div>
            `).join('');
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        }
        
        async function downloadFile(filename) {
            try {
                const response = await fetch(`/api/download/${encodeURIComponent(filename)}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    showToast('File downloaded: ' + filename, 'success');
                } else {
                    showToast('Error downloading file', 'error');
                }
            } catch (error) {
                showToast('Download failed: ' + error.message, 'error');
            }
        }
        
        async function downloadWorkspace() {
            try {
                const response = await fetch('/api/download/workspace.zip');
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'workspace.zip';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    showToast('Workspace downloaded', 'success');
                } else {
                    showToast('Error downloading workspace', 'error');
                }
            } catch (error) {
                showToast('Download failed: ' + error.message, 'error');
            }
        }

        // Cluster Status Functions
        async function refreshClusterStatus() {
            try {
                const response = await fetch('/api/cluster/status');
                if (response.ok) {
                    const status = await response.json();
                    displayClusterStatus(status);
                    showToast('Cluster status updated', 'success');
                } else {
                    showToast('Error loading cluster status', 'error');
                }
            } catch (error) {
                console.error('Error loading cluster status:', error);
                showToast('Error loading cluster status', 'error');
            }
        }

        function displayClusterStatus(status) {
            const content = document.getElementById('cluster-status-content');

            const statusIcon = status.connected ? '✅' : '❌';
            const statusText = status.connected ? 'Connected' : 'Disconnected';
            const statusColor = status.connected ? '#10b981' : '#ef4444';

            const html = `
                <div style="padding: 1rem;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                        <div style="padding: 1rem; background: var(--muted); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.25rem;">Status</div>
                            <div style="font-size: 1.25rem; font-weight: bold; color: ${statusColor};">
                                ${statusIcon} ${statusText}
                            </div>
                        </div>
                        <div style="padding: 1rem; background: var(--muted); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.25rem;">Model</div>
                            <div style="font-size: 1.25rem; font-weight: bold;">${status.model || 'N/A'}</div>
                        </div>
                        <div style="padding: 1rem; background: var(--muted); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.25rem;">Active Nodes</div>
                            <div style="font-size: 1.25rem; font-weight: bold;">${status.nodes || 0}</div>
                        </div>
                        <div style="padding: 1rem; background: var(--muted); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.25rem;">Cluster Host</div>
                            <div style="font-size: 1rem; font-weight: bold;">${status.host || 'N/A'}:${status.port || 'N/A'}</div>
                        </div>
                    </div>
                    <div style="padding: 1rem; background: var(--muted); border-radius: 0.5rem;">
                        <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.5rem;">Parallax SDK Status</div>
                        <div style="font-size: 0.875rem;">
                            ${status.parallax_available ? '✅ Parallax SDK Available' : '⚠️  Parallax SDK Not Available (Using Ollama fallback)'}
                        </div>
                        ${status.last_check ? `
                        <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-top: 0.5rem;">
                            Last checked: ${new Date(status.last_check).toLocaleString()}
                        </div>
                        ` : ''}
                    </div>
                    ${!status.connected && status.parallax_available ? `
                    <div style="margin-top: 1rem; padding: 1rem; background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 0.5rem; color: #92400e;">
                        <strong>⚠️  Connection Issue</strong>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem;">
                            Make sure Parallax is running: <code style="background: #fff; padding: 0.125rem 0.25rem; border-radius: 0.25rem;">parallax serve</code>
                        </p>
                    </div>
                    ` : ''}
                </div>
            `;

            content.innerHTML = html;
        }

        // Auto-refresh cluster status when tab is opened
        function onClusterTabOpen() {
            refreshClusterStatus();
        }

        // Enhanced task display with progress
        function displayEnhancedTask(task) {
            const results = typeof task.results === 'string' ? JSON.parse(task.results || '{}') : (task.results || {});
            const steps = Object.keys(results);
            
            let progressHtml = '';
            if (task.status === 'processing' && steps.length > 0) {
                progressHtml = `
                    <div style="margin: 0.5rem 0; font-size: 0.75rem;">
                        <strong>Progress:</strong> ${steps.map(step => 
                            `<span style="background: #10b981; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; margin: 0 0.25rem;">${step}</span>`
                        ).join('')}
                        <span style="background: #f59e0b; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem;">Processing...</span>
                    </div>
                `;
            }
            
            // Show web search indicator
            let searchIndicator = '';
            if (results.web_search || results.search_docs || results.research) {
                searchIndicator = '<span style="background: #3b82f6; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">🔍 Web Search</span>';
            }
            
            return progressHtml + searchIndicator;
        }
        
        // Track current tab for refresh
        let currentTab = 'queue';
        
        // Load completed tasks for results tab
        async function loadCompletedTasks() {
            try {
                const response = await fetch('/api/tasks');
                if (response.ok) {
                    const data = await response.json();
                    const tasks = data.tasks || data;
                    const completedTasks = tasks.filter(t => t.status === 'completed');
                    
                    const resultsDiv = document.getElementById('results-list');
                    if (completedTasks.length === 0) {
                        resultsDiv.innerHTML = '<div class="empty-state">No completed tasks</div>';
                        return;
                    }
                    
                    resultsDiv.innerHTML = completedTasks.map(task => `
                        <div class="task-item" style="margin-bottom: 1rem; padding: 1rem; border: 1px solid #ddd; border-radius: 0.5rem;">
                            <div style="display: flex; justify-content: between; margin-bottom: 0.5rem;">
                                <strong>${task.type}</strong>
                                <small>${new Date(task.created_at).toLocaleString()}</small>
                            </div>
                            <div style="margin-bottom: 0.5rem; font-size: 0.875rem;">
                                ${task.content.substring(0, 150)}...
                            </div>
                            <button onclick="viewTaskResults('${task.id}')" class="btn" style="font-size: 0.75rem;">View Results</button>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading completed tasks:', error);
            }
        }
        
        // Delete a task
        async function deleteTask(taskId) {
            if (!confirm('Are you sure you want to delete this task?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/delete_task/${taskId}`, {method: 'DELETE'});
                if (response.ok) {
                    showToast('Task deleted successfully');
                    updateStatus();
                    loadTasks();
                } else {
                    const error = await response.json();
                    showToast(error.error || 'Failed to delete task', 'error');
                }
            } catch (error) {
                showToast('Error deleting task', 'error');
            }
        }
        
        // Edit a task
        async function editTask(taskId) {
            const task = allTasks ? allTasks.find(t => t.id === taskId) : null;
            if (!task) {
                showToast('Task not found', 'error');
                return;
            }
            
            if (task.status !== 'pending') {
                showToast('Can only edit pending tasks', 'error');
                return;
            }
            
            // Create a modal for editing
            const modal = document.getElementById('task-modal');
            const modalTitle = document.getElementById('modal-title');
            const modalBody = document.getElementById('modal-body');
            
            modalTitle.textContent = `Edit Task ${task.id}`;
            
            modalBody.innerHTML = `
                <div class="form-group">
                    <label for="edit-content">Task Content:</label>
                    <textarea id="edit-content" style="width: 100%; min-height: 100px;">${task.content}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Metadata (Optional):</label>
                    <div id="edit-metadata-container"></div>
                    <button type="button" class="button button-secondary" onclick="addEditMetadataRow()">+ Add Metadata</button>
                </div>
                
                <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                    <button class="button button-primary" onclick="saveTaskEdit('${task.id}')">Save Changes</button>
                    <button class="button button-secondary" onclick="closeModal()">Cancel</button>
                </div>
            `;
            
            // Populate existing metadata
            const metadataContainer = document.getElementById('edit-metadata-container');
            if (task.metadata && Object.keys(task.metadata).length > 0) {
                Object.entries(task.metadata).forEach(([key, value]) => {
                    const row = document.createElement('div');
                    row.className = 'metadata-row';
                    row.innerHTML = `
                        <input type="text" placeholder="Key" class="meta-key" value="${key}">
                        <input type="text" placeholder="Value" class="meta-value" value="${value}">
                        <button type="button" class="button button-ghost icon-button" onclick="removeMetadataRow(this)">×</button>
                    `;
                    metadataContainer.appendChild(row);
                });
            } else {
                addEditMetadataRow();
            }
            
            modal.classList.add('active');
        }
        
        function addEditMetadataRow() {
            const container = document.getElementById('edit-metadata-container');
            const row = document.createElement('div');
            row.className = 'metadata-row';
            row.innerHTML = `
                <input type="text" placeholder="Key" class="meta-key">
                <input type="text" placeholder="Value" class="meta-value">
                <button type="button" class="button button-ghost icon-button" onclick="removeMetadataRow(this)">×</button>
            `;
            container.appendChild(row);
        }
        
        async function saveTaskEdit(taskId) {
            const content = document.getElementById('edit-content').value.trim();
            if (!content) {
                showToast('Task content cannot be empty', 'error');
                return;
            }
            
            const metadata = {};
            document.querySelectorAll('#edit-metadata-container .metadata-row').forEach(row => {
                const key = row.querySelector('.meta-key').value.trim();
                const value = row.querySelector('.meta-value').value.trim();
                if (key && value) {
                    metadata[key] = value;
                }
            });
            
            try {
                const response = await fetch(`/api/update_task/${taskId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({content, metadata})
                });
                
                if (response.ok) {
                    showToast('Task updated successfully');
                    closeModal();
                    updateStatus();
                    loadTasks();
                } else {
                    const error = await response.json();
                    showToast(error.error || 'Failed to update task', 'error');
                }
            } catch (error) {
                showToast('Error updating task', 'error');
            }
        }
        
        // Store tasks globally for edit/delete operations  
        let allTasks = [];
        
        // Update loadTasks to store tasks globally
        async function loadTasks() {
            try {
                const response = await fetch('/api/tasks');
                if (response.ok) {
                    const data = await response.json();
                    allTasks = data.tasks || data; // Store globally and handle both formats
                    renderTasks(allTasks);
                }
            } catch (error) {
                console.error('Error loading tasks:', error);
            }
        }

        // View individual task results
        async function viewTaskResults(taskId) {
            try {
                const response = await fetch(`/api/task/${taskId}`);
                if (response.ok) {
                    const task = await response.json();
                    const resultsDiv = document.getElementById('results-list');
                    
                    let resultsHtml = '<div class="result-viewer">';
                    resultsHtml += `<h3>Task: ${task.type}</h3>`;
                    resultsHtml += `<p><strong>Content:</strong> ${task.content}</p>`;
                    resultsHtml += `<p><strong>Processing Time:</strong> ${task.processing_time}s</p>`;
                    resultsHtml += '<h4>Results:</h4>';
                    
                    if (task.results && typeof task.results === 'object') {
                        Object.entries(task.results).forEach(([key, value]) => {
                            resultsHtml += `<div style="margin-bottom: 1rem;">`;
                            resultsHtml += `<h5>${key.replace(/_/g, ' ').toUpperCase()}</h5>`;
                            resultsHtml += `<pre style="background: #f5f5f5; padding: 1rem; border-radius: 0.25rem; white-space: pre-wrap; font-size: 0.875rem;">${typeof value === 'string' ? value : JSON.stringify(value, null, 2)}</pre>`;
                            resultsHtml += `</div>`;
                        });
                    }
                    
                    resultsHtml += `<button onclick="loadCompletedTasks()" class="btn" style="margin-top: 1rem;">← Back to Results</button>`;
                    resultsHtml += '</div>';
                    
                    resultsDiv.innerHTML = resultsHtml;
                }
            } catch (error) {
                console.error('Error loading task results:', error);
            }
        }
        
        
        // Form submission
        document.getElementById('task-form').addEventListener('submit', submitTask);

        // Initial load
        updateStatus();
        loadTasks();

        // Initialize voice recognition
        loadVoiceSettings();
        initVoiceRecognition();

        // Start auto-refresh
        refreshInterval = setInterval(() => {
            updateStatus();
            loadTasks();
        }, 5000);
    </script>
</body>
</html>
'''

def create_ai_router_prompt():
    """Create a system prompt for the AI to interpret user commands into task JSON"""
    return """You are a Task Interpreter for Parallax Voice Office, a voice-first AI assistant. Your role is to analyze user commands (spoken or typed) and convert them into structured task JSON objects.

Based on the user's input, determine the appropriate task type and extract relevant metadata from natural language.

Task Types:
- search: For research, web searches, information gathering, finding information
- process: For text processing, formatting, improving, summarizing, or transforming existing content
- create: For generating new content from scratch (articles, documents, creative writing)
- code: For programming, script generation, code analysis, debugging
- chain: For multi-step complex tasks with dependencies

Voice Command Detection Patterns:
- "search for...", "research...", "find information about..." → search
- "create...", "write...", "generate...", "compose..." → create
- "process...", "improve...", "summarize...", "rephrase...", "make it more..." → process
- "write code...", "create a script...", "debug...", "implement..." → code

Metadata Extraction from Natural Language:

For SEARCH tasks:
- search_query: The main search topic
- comparison: true if comparing multiple things (e.g., "compare X and Y")
- filename: Extract from "save to X.md" or "output as X" (default: research_report.md)

For PROCESS tasks:
- format: Detect format requests (bullet_points, markdown, json, csv, table)
- improve_clarity: true if "clearer", "more clear", "easier to understand"
- simplify: true if "simpler", "simplify", "make it simple"
- tone: Extract tone words (professional, casual, friendly, formal, technical)

For CREATE tasks:
- tone: Detect tone (professional, casual, conversational, friendly, formal, technical)
- audience: Extract audience (executives, developers, beginners, experts, general public, students)
- format: Detect format (essay, bullet_points, article, blog_post, report, email, letter)
- filename: Extract from "save to X" or "output as X" or "call it X"

For CODE tasks:
- language: Detect programming language (python, javascript, java, c++, rust, go, typescript, etc.)
- filename: Extract from "save to X.py" or use language extension
- include_docs: true if "with documentation", "include comments", "add docstrings"
- include_tests: true if "with tests", "include test cases", "add unit tests"

For CHAIN tasks:
- steps: Try to identify distinct steps if mentioned
- Include relevant metadata for the overall workflow

Filename Detection Examples:
- "save to report.md" → filename: "report.md"
- "call it analysis.py" → filename: "analysis.py"
- "output as summary.txt" → filename: "summary.txt"
- No filename mentioned → Use appropriate default

Tone Detection Keywords:
- professional, formal, business → "professional"
- casual, friendly, relaxed → "casual"
- conversational, chatty → "conversational"
- technical, detailed → "technical"

IMPORTANT: Return ONLY a clean JSON object with this structure:
{
  "type": "task_type_here",
  "content": "the user's request clearly stated",
  "metadata": {
    "key": "value"
  }
}

Examples:

User: "Search for the latest AI safety research and save to ai_safety.md"
{
  "type": "search",
  "content": "Search for the latest AI safety research",
  "metadata": {
    "search_query": "AI safety research",
    "filename": "ai_safety.md"
  }
}

User: "Create a professional email to executives about the project deadline"
{
  "type": "create",
  "content": "Create a professional email to executives about the project deadline",
  "metadata": {
    "tone": "professional",
    "audience": "executives",
    "format": "email"
  }
}

User: "Write a Python script to analyze CSV files with documentation and tests"
{
  "type": "code",
  "content": "Write a Python script to analyze CSV files",
  "metadata": {
    "language": "python",
    "include_docs": true,
    "include_tests": true,
    "filename": "analyzer.py"
  }
}

Do not include any explanation, markdown formatting, or additional text. Only return the JSON object."""

# Processor class (simplified for single file)
class TaskProcessor:
    def __init__(self):
        # Use data directory for database in Docker, current dir otherwise
        data_dir = Path("data")
        if data_dir.exists():
            self.db_path = data_dir / "task_processor.db"
        else:
            self.db_path = Path("task_processor.db")
        self.queue_file = Path("task_queue.json")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Load configuration from YAML file
        self.load_config()

        self.queue = []
        self.processing = False
        self.processing_thread = None

        # Initialize Parallax client
        self.parallax_client = None
        self.cluster_nodes = []
        self.cluster_health = {
            'connected': False,
            'nodes': [],
            'last_check': None
        }
        self.init_parallax()

        self.init_database()
        self.load_queue()

    def load_config(self):
        """Load configuration from processor_config.yaml"""
        config_file = Path("processor_config.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                yaml_config = yaml.safe_load(f)

            # Extract Parallax configuration
            parallax_config = yaml_config.get('parallax', {})
            self.config = {
                'model': yaml_config.get('model', 'qwen3:1b'),
                'temperature': yaml_config.get('temperature', 0.8),
                'max_retries': yaml_config.get('max_retries', 3),
                'parallax_host': os.getenv('PARALLAX_HOST', parallax_config.get('host', 'localhost')),
                'parallax_port': int(os.getenv('PARALLAX_PORT', parallax_config.get('port', 50051))),
                'parallax_timeout': parallax_config.get('timeout', 600),
                'parallax_max_workers': parallax_config.get('max_workers', 4),
                'top_p': yaml_config.get('top_p', 0.9),
                'max_tokens': yaml_config.get('max_tokens', -1),
                'cluster_config': yaml_config.get('cluster', {})
            }

            # Fallback to Ollama for backward compatibility
            if not PARALLAX_AVAILABLE:
                self.config['ollama_host'] = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        else:
            # Default configuration
            self.config = {
                'model': 'qwen3:1b',
                'parallax_host': os.getenv('PARALLAX_HOST', 'localhost'),
                'parallax_port': int(os.getenv('PARALLAX_PORT', 50051)),
                'parallax_timeout': 600,
                'parallax_max_workers': 4,
                'temperature': 0.8,
                'max_retries': 3,
                'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            }

    def init_parallax(self):
        """Initialize Parallax client and check connection"""
        if not PARALLAX_AVAILABLE:
            logger.warning("Parallax SDK not available, using fallback mode")
            return

        try:
            # Create Parallax client
            host = self.config['parallax_host']
            port = self.config['parallax_port']

            logger.info(f"Connecting to Parallax at {host}:{port}")
            self.parallax_client = ParallaxClient(host=host, port=port)

            # Test connection by checking cluster status
            self.check_cluster_health()

            if self.cluster_health['connected']:
                logger.info("✅ Successfully connected to Parallax cluster")
                logger.info(f"Active nodes: {len(self.cluster_health['nodes'])}")
            else:
                logger.warning("⚠️  Connected to Parallax but no cluster information available")

        except Exception as e:
            logger.error(f"Failed to initialize Parallax client: {e}")
            logger.warning("Falling back to Ollama compatibility mode")
            self.parallax_client = None

    def check_cluster_health(self):
        """Check the health and status of the Parallax cluster"""
        if not self.parallax_client:
            self.cluster_health['connected'] = False
            return

        try:
            # Try to get cluster status
            # Note: The actual API might differ based on Parallax SDK version
            # This is a placeholder for the actual cluster status check
            self.cluster_health['connected'] = True
            self.cluster_health['last_check'] = datetime.now().isoformat()

            # In a real implementation, we would query the cluster for node information
            # For now, we'll mark it as connected
            logger.info("Cluster health check completed")

        except Exception as e:
            logger.error(f"Cluster health check failed: {e}")
            self.cluster_health['connected'] = False

    def get_cluster_status(self):
        """Get current cluster status for API endpoint"""
        self.check_cluster_health()
        return {
            'connected': self.cluster_health['connected'],
            'nodes': len(self.cluster_health['nodes']),
            'last_check': self.cluster_health['last_check'],
            'parallax_available': PARALLAX_AVAILABLE,
            'host': self.config.get('parallax_host'),
            'port': self.config.get('parallax_port'),
            'model': self.config.get('model')
        }
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                results TEXT,
                metadata TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def load_queue(self):
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.queue = []
                    for item in data:
                        if 'type' in item and isinstance(item['type'], str):
                            item['type'] = TaskType(item['type'])
                        if 'status' in item and isinstance(item['status'], str):
                            item['status'] = TaskStatus(item['status'])
                        self.queue.append(Task(**item))
            except:
                self.queue = []
    
    def save_queue(self):
        queue_data = []
        for task in self.queue:
            task_dict = asdict(task)
            task_dict['type'] = task.type.value
            task_dict['status'] = task.status.value
            queue_data.append(task_dict)
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    def add_task(self, task_type: str, content: str, metadata: dict = None) -> str:
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:17]}"
        task = Task(
            id=task_id,
            type=TaskType(task_type),
            content=content,
            metadata=metadata or {}
        )
        self.queue.append(task)
        self.save_queue()
        self.save_to_db(task)
        return task_id
    
    def save_to_db(self, task: Task):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, type, content, status, results, metadata, error, retry_count, updated_at, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id,
            task.type.value,
            task.content,
            task.status.value,
            json.dumps(task.results),
            json.dumps(task.metadata),
            task.error,
            task.retry_count,
            datetime.now().isoformat(),
            task.processing_time
        ))
        conn.commit()
        conn.close()
    
    def process_with_parallax(self, prompt: str) -> str:
        """Process a prompt using Parallax distributed computing"""
        if self.parallax_client and PARALLAX_AVAILABLE:
            try:
                logger.info("Processing with Parallax cluster")

                # Generate with Parallax
                response = self.parallax_client.generate(
                    model=self.config['model'],
                    prompt=prompt,
                    temperature=self.config.get('temperature', 0.8),
                    top_p=self.config.get('top_p', 0.9),
                    max_tokens=self.config.get('max_tokens', -1) if self.config.get('max_tokens', -1) > 0 else None
                )

                # Extract the response text
                if hasattr(response, 'text'):
                    return response.text
                elif isinstance(response, dict):
                    return response.get('response', response.get('text', str(response)))
                else:
                    return str(response)

            except Exception as e:
                logger.error(f"Parallax error: {e}")
                logger.warning("Falling back to Ollama")
                return self.process_with_ollama_fallback(prompt)
        else:
            # Fallback to Ollama if Parallax not available
            return self.process_with_ollama_fallback(prompt)

    def process_with_ollama_fallback(self, prompt: str) -> str:
        """Fallback to Ollama API for backward compatibility"""
        try:
            if 'ollama_host' not in self.config:
                return "Error: Neither Parallax nor Ollama is configured"

            logger.info("Processing with Ollama (fallback mode)")
            payload = {
                'model': self.config['model'],
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': self.config.get('temperature', 0.7),
                }
            }

            response = requests.post(
                f"{self.config['ollama_host']}/api/generate",
                json=payload,
                timeout=None
            )

            if response.status_code == 200:
                return response.json().get('response', '')
            return "Error: Failed to get response from Ollama"
        except Exception as e:
            logger.error(f"Ollama fallback error: {e}")
            return f"Error: {str(e)}"

    # Alias for backward compatibility
    def process_with_ollama(self, prompt: str) -> str:
        """Backward compatibility alias - redirects to process_with_parallax"""
        return self.process_with_parallax(prompt)
    
    def process_task(self, task: Task):
        task.status = TaskStatus.PROCESSING
        task.updated_at = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            # Simple processing based on task type
            if task.type == TaskType.SEARCH:
                # Simulate web search
                task.results['search'] = f"Search results for: {task.content[:50]}"
                prompt = f"Summarize this search query and create a report: {task.content}"
                task.results['report'] = self.process_with_ollama(prompt)
                
            elif task.type == TaskType.PROCESS:
                prompt = f"Process and improve this content: {task.content}"
                task.results['processed'] = self.process_with_ollama(prompt)
                
            elif task.type == TaskType.CREATE:
                prompt = f"Create content based on: {task.content}"
                task.results['created'] = self.process_with_ollama(prompt)
                
            elif task.type == TaskType.CODE:
                prompt = f"Write code for: {task.content}"
                task.results['code'] = self.process_with_ollama(prompt)
                
            elif task.type == TaskType.CHAIN:
                # Multi-step processing
                steps = ["analyze", "expand", "finalize"]
                for step in steps:
                    prompt = f"{step.capitalize()} this: {task.content}"
                    task.results[step] = self.process_with_ollama(prompt)
            
            # Save content to file if filename is specified in metadata
            self._save_results_to_file(task)
            
            task.status = TaskStatus.COMPLETED
            task.processing_time = time.time() - start_time
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.retry_count += 1
        
        task.updated_at = datetime.now().isoformat()
        self.save_to_db(task)
        self.save_queue()
    
    def start_processing(self):
        if not self.processing:
            self.processing = True
            self.processing_thread = threading.Thread(target=self._process_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
    
    def stop_processing(self):
        self.processing = False
    
    def _process_loop(self):
        while self.processing:
            pending_tasks = [t for t in self.queue if t.status == TaskStatus.PENDING]
            if pending_tasks:
                task = pending_tasks[0]
                self.process_task(task)
                time.sleep(2)  # Delay between tasks
            else:
                # No more pending tasks, stop processing
                logger.info("No more pending tasks, stopping processing")
                self.processing = False
                break
    
    def get_stats(self):
        return {
            'total': len(self.queue),
            'pending': sum(1 for t in self.queue if t.status == TaskStatus.PENDING),
            'processing': sum(1 for t in self.queue if t.status == TaskStatus.PROCESSING),
            'completed': sum(1 for t in self.queue if t.status == TaskStatus.COMPLETED),
            'failed': sum(1 for t in self.queue if t.status == TaskStatus.FAILED),
        }
    
    def clear_completed(self):
        self.queue = [t for t in self.queue if t.status != TaskStatus.COMPLETED]
        self.save_queue()
    
    def reset_failed(self):
        for task in self.queue:
            if task.status == TaskStatus.FAILED:
                task.status = TaskStatus.PENDING
                task.retry_count = 0
                task.error = None
        self.save_queue()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the queue"""
        initial_len = len(self.queue)
        self.queue = [t for t in self.queue if t.id != task_id]
        if len(self.queue) < initial_len:
            self.save_queue()
            return True
        return False
    
    def update_task(self, task_id: str, content: str = None, metadata: dict = None) -> bool:
        """Update a task's content and/or metadata (only if pending)"""
        task = next((t for t in self.queue if t.id == task_id), None)
        if task and task.status == TaskStatus.PENDING:
            if content is not None:
                task.content = content
            if metadata is not None:
                task.metadata = metadata
            task.updated_at = datetime.now().isoformat()
            self.save_queue()
            self.save_to_db(task)
            return True
        return False
    
    def _save_results_to_file(self, task: Task):
        """Save task results to a file in the workspace directory"""
        try:
            # Create workspace directory if it doesn't exist
            workspace_dir = Path("workspace")
            workspace_dir.mkdir(exist_ok=True)
            
            # Determine filename from metadata or use default
            filename = task.metadata.get('filename', f"{task.id}.txt")
            
            # If no extension, add .txt
            if '.' not in filename:
                filename += '.txt'
            
            # Combine all results into one content string
            content_parts = []
            
            # Add task description
            content_parts.append(f"Task: {task.content}\n")
            content_parts.append(f"Type: {task.type.value}\n")
            content_parts.append(f"Generated: {task.updated_at}\n")
            content_parts.append("=" * 50 + "\n")
            
            # Add all result sections
            for key, value in task.results.items():
                if isinstance(value, str) and value.strip():
                    content_parts.append(f"\n## {key.upper().replace('_', ' ')}\n")
                    content_parts.append(f"{value}\n")
                elif isinstance(value, dict):
                    # For nested dict results (like web search), extract meaningful content
                    if key == 'research' and 'organic' in value:
                        content_parts.append(f"\n## WEB SEARCH RESULTS\n")
                        for result in value['organic'][:3]:  # Top 3 results
                            content_parts.append(f"- {result.get('title', 'No title')}\n")
                            content_parts.append(f"  {result.get('snippet', 'No description')}\n")
                            content_parts.append(f"  Link: {result.get('link', 'No link')}\n\n")
                    else:
                        content_parts.append(f"\n## {key.upper().replace('_', ' ')}\n")
                        content_parts.append(f"{json.dumps(value, indent=2)}\n")
            
            # Write to file
            file_path = workspace_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(content_parts)
            
            # Update results with file save confirmation
            task.results['save_document'] = f"Content saved to: {filename}"
            logger.info(f"Saved task results to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save results to file: {e}")
            task.results['save_document'] = f"Error saving file: {str(e)}"

# Flask application
app = Flask(__name__)
CORS(app)

# Initialize processor
processor = TaskProcessor()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def get_all_network_interfaces():
    """Get all available network interfaces and their IPs"""
    interfaces = []
    try:
        import subprocess
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        current_interface = None
        for line in lines:
            if line and not line.startswith('\t') and not line.startswith(' '):
                current_interface = line.split(':')[0]
            elif 'inet ' in line and '127.0.0.1' not in line and 'inet 169.254' not in line:
                ip = line.split('inet ')[1].split(' ')[0]
                if current_interface:
                    interfaces.append((current_interface, ip))
    except:
        pass
    return interfaces

def test_network_connectivity():
    """Test if the server is accessible from different interfaces"""
    print("🔍 NETWORK DIAGNOSTICS:")
    local_ip = get_local_ip()
    interfaces = get_all_network_interfaces()
    
    print(f"Primary IP detected: {local_ip}")
    if interfaces:
        print("Available network interfaces:")
        for interface, ip in interfaces:
            print(f"  {interface}: {ip}")
    
    # Test if we can bind to the port
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('0.0.0.0', 5001))
        test_socket.close()
        print("✅ Port 5001 is available")
    except OSError:
        print("❌ Port 5001 is already in use")
    
    return local_ip, interfaces

def generate_qr_code_ascii(url):
    """Generate a simple ASCII QR-like code for the URL"""
    try:
        # Try to use qrcode library if available
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=1, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Generate ASCII art
        matrix = qr.modules
        if matrix:
            print(f"\n📱 SCAN QR CODE WITH PHONE:")
            print("█" * (len(matrix[0]) + 2))
            for row in matrix:
                line = "█"
                for cell in row:
                    line += "██" if cell else "  "
                line += "█"
                print(line)
            print("█" * (len(matrix[0]) + 2))
            return True
    except ImportError:
        pass
    return False

@app.route('/')
def index():
    server_info = f"{get_local_ip()}:5001"
    return render_template_string(HTML_TEMPLATE, 
                                 server_info=server_info,
                                 model=processor.config['model'])

@app.route('/api/interpret_task', methods=['POST'])
def interpret_task():
    """Interpret user's natural language command into structured task JSON"""
    try:
        data = request.json
        user_command = data.get('command', '').strip()
        
        if not user_command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Create the prompt for the AI
        system_prompt = create_ai_router_prompt()
        
        # Combine system prompt with user command
        full_prompt = f"{system_prompt}\n\nUser Command: {user_command}\n\nTask JSON:"
        
        # Process with Ollama to get interpretation
        interpretation = processor.process_with_ollama(full_prompt)
        
        # Try to parse the response as JSON
        try:
            # Clean the response - remove any markdown formatting
            cleaned = interpretation.strip()
            if cleaned.startswith('```'):
                # Remove markdown code blocks
                cleaned = cleaned.split('```')[1]
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
            
            task_json = json.loads(cleaned)
            
            # Validate the structure
            if 'type' not in task_json or 'content' not in task_json:
                raise ValueError("Missing required fields")
            
            # Ensure metadata exists
            if 'metadata' not in task_json:
                task_json['metadata'] = {}
            
            return jsonify(task_json)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI interpretation: {e}")
            # Fallback: try to extract meaningful parts
            return jsonify({
                'type': 'process',
                'content': user_command,
                'metadata': {},
                'error': 'Could not fully interpret command, using defaults'
            })
            
    except Exception as e:
        logger.error(f"Error in interpret_task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_id = processor.add_task(
        task_type=data.get('type', 'process'),
        content=data.get('content', ''),
        metadata=data.get('metadata', {})
    )
    return jsonify({'task_id': task_id, 'status': 'queued'})

@app.route('/api/status')
def status():
    stats = processor.get_stats()
    stats['processing'] = processor.processing
    return jsonify(stats)

@app.route('/api/tasks')
def get_tasks():
    tasks_data = []
    for task in processor.queue:
        task_dict = asdict(task)
        task_dict['type'] = task.type.value
        task_dict['status'] = task.status.value
        tasks_data.append(task_dict)
    return jsonify({'tasks': tasks_data})

@app.route('/api/task/<task_id>')
def get_task(task_id):
    task = next((t for t in processor.queue if t.id == task_id), None)
    if task:
        task_dict = asdict(task)
        task_dict['type'] = task.type.value
        task_dict['status'] = task.status.value
        return jsonify(task_dict)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/start_processing', methods=['POST'])
def start_processing():
    processor.start_processing()
    return jsonify({'status': 'started'})

@app.route('/api/stop_processing', methods=['POST'])
def stop_processing():
    processor.stop_processing()
    return jsonify({'status': 'stopped'})

@app.route('/api/clear_completed', methods=['POST'])
def clear_completed():
    processor.clear_completed()
    return jsonify({'status': 'cleared'})

@app.route('/api/reset_failed', methods=['POST'])
def reset_failed():
    processor.reset_failed()
    return jsonify({'status': 'reset'})

@app.route('/api/cluster/status')
def cluster_status():
    """Get Parallax cluster status and health information"""
    status = processor.get_cluster_status()
    return jsonify(status)

@app.route('/api/cluster/refresh', methods=['POST'])
def refresh_cluster():
    """Force refresh cluster health check"""
    processor.check_cluster_health()
    status = processor.get_cluster_status()
    return jsonify(status)

@app.route('/api/delete_task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a specific task"""
    success = processor.delete_task(task_id)
    if success:
        return jsonify({'status': 'deleted', 'task_id': task_id})
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/api/update_task/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task's content and metadata (only if pending)"""
    data = request.json
    content = data.get('content')
    metadata = data.get('metadata')
    
    success = processor.update_task(task_id, content, metadata)
    if success:
        return jsonify({'status': 'updated', 'task_id': task_id})
    else:
        return jsonify({'error': 'Task not found or not editable (must be pending)'}), 400

@app.route('/gallery')
def gallery():
    """Serve the gallery view"""
    gallery_file = Path('gallery_template.html')
    if gallery_file.exists():
        return send_file(str(gallery_file))
    else:
        return "Gallery template not found", 404

@app.route('/api/export/<task_id>')
def export_task(task_id):
    """Export a single task result"""
    task = processor.get_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/files')
def list_files():
    """List files in workspace"""
    workspace_dir = Path('workspace')
    if not workspace_dir.exists():
        return jsonify([])
    
    files = []
    for file_path in workspace_dir.rglob('*'):
        if file_path.is_file():
            try:
                stat = file_path.stat()
                files.append({
                    'name': str(file_path.relative_to(workspace_dir)),
                    'size': stat.st_size,
                    'modified': stat.st_mtime * 1000  # JavaScript timestamp
                })
            except:
                pass
    
    return jsonify(files)

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download a file from workspace"""
    workspace_dir = Path('workspace')
    file_path = workspace_dir / filename
    
    # Security check - ensure file is within workspace
    try:
        file_path.resolve().relative_to(workspace_dir.resolve())
    except ValueError:
        return jsonify({'error': 'Access denied'}), 403
    
    if file_path.exists() and file_path.is_file():
        return send_file(str(file_path), as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """Upload a file to workspace"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    workspace_dir = Path('workspace')
    workspace_dir.mkdir(exist_ok=True)
    
    file_path = workspace_dir / file.filename
    file.save(str(file_path))
    
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename})

@app.route('/api/cli_tasks')
def get_cli_tasks():
    """Get tasks from CLI database (universal_processor.db)"""
    try:
        # Use data directory for database in Docker, current dir otherwise
        data_dir = Path("data")
        if data_dir.exists():
            cli_db_path = data_dir / "universal_processor.db"
        else:
            cli_db_path = Path("universal_processor.db")
        
        if not cli_db_path.exists():
            return jsonify({'tasks': []})
        
        conn = sqlite3.connect(cli_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, type, content, config_name, status, results, metadata, error, 
                   retry_count, created_at, updated_at, processing_time
            FROM tasks
            ORDER BY created_at DESC
        ''')
        
        tasks_data = []
        for row in cursor.fetchall():
            task = {
                'id': row[0],
                'type': row[1],
                'content': row[2],
                'config_name': row[3],
                'status': row[4],
                'results': json.loads(row[5]) if row[5] else {},
                'metadata': json.loads(row[6]) if row[6] else {},
                'error': row[7],
                'retry_count': row[8],
                'created_at': row[9],
                'updated_at': row[10],
                'processing_time': row[11]
            }
            tasks_data.append(task)
        
        conn.close()
        return jsonify({'tasks': tasks_data})
        
    except Exception as e:
        logger.error(f"Error loading CLI tasks: {e}")
        return jsonify({'tasks': [], 'error': str(e)})

@app.route('/api/cli_task/<task_id>')
def get_cli_task(task_id):
    """Get single CLI task with steps"""
    try:
        # Use data directory for database in Docker, current dir otherwise
        data_dir = Path("data")
        if data_dir.exists():
            cli_db_path = data_dir / "universal_processor.db"
        else:
            cli_db_path = Path("universal_processor.db")
        
        if not cli_db_path.exists():
            return jsonify({'error': 'CLI database not found'}), 404
        
        conn = sqlite3.connect(cli_db_path)
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute('''
            SELECT id, type, content, config_name, status, results, metadata, error, 
                   retry_count, created_at, updated_at, processing_time
            FROM tasks WHERE id = ?
        ''', (task_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Task not found'}), 404
        
        task = {
            'id': row[0],
            'type': row[1],
            'content': row[2],
            'config_name': row[3],
            'status': row[4],
            'results': json.loads(row[5]) if row[5] else {},
            'metadata': json.loads(row[6]) if row[6] else {},
            'error': row[7],
            'retry_count': row[8],
            'created_at': row[9],
            'updated_at': row[10],
            'processing_time': row[11]
        }
        
        # Get task steps
        cursor.execute('''
            SELECT step_name, result, created_at
            FROM task_steps WHERE task_id = ?
            ORDER BY created_at
        ''', (task_id,))
        
        task['steps'] = []
        for step_row in cursor.fetchall():
            step = {
                'step_name': step_row[0],
                'result': step_row[1],
                'created_at': step_row[2]
            }
            task['steps'].append(step)
        
        conn.close()
        return jsonify(task)
        
    except Exception as e:
        logger.error(f"Error loading CLI task {task_id}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run network diagnostics first
    local_ip, interfaces = test_network_connectivity()
    
    print("\n" + "="*70)
    print("🚀 TASK PROCESSOR GUI STARTED")
    print("="*70)
    print(f"📱 Local Access:    http://localhost:5001")
    print(f"🌐 Network Access:  http://{local_ip}:5001")
    print(f"📲 Phone Access:    http://{local_ip}:5001")
    print(f"🎨 Gallery View:    http://{local_ip}:5001/gallery")
    print("="*70)
    if PARALLAX_AVAILABLE and processor.parallax_client:
        print("✅ Parallax cluster connected")
        print(f"📊 Model: {processor.config['model']}")
        print(f"🖥️  Cluster: {processor.config['parallax_host']}:{processor.config['parallax_port']}")
    elif PARALLAX_AVAILABLE:
        print("⚠️  Parallax SDK available but not connected")
        print("🤖 Make sure Parallax is running: parallax serve")
    else:
        print("⚠️  Parallax SDK not available - using Ollama fallback")
        print("🤖 Make sure Ollama is running: ollama serve")
    print("="*70)
    
    # Show alternative IPs if available
    if interfaces and len(interfaces) > 1:
        print("\n🔄 ALTERNATIVE NETWORK ADDRESSES:")
        for interface, ip in interfaces:
            if ip != local_ip:
                print(f"   {interface}: http://{ip}:5001")
        print("="*70)
    
    print("\n📱 PHONE/TABLET ACCESS TROUBLESHOOTING:")
    print(f"1. Ensure your device is on the same WiFi network")
    print(f"2. Try: http://{local_ip}:5001")
    print(f"3. If blocked, check macOS Firewall:")
    print(f"   System Preferences → Security & Privacy → Firewall")
    print(f"   Allow 'Python' or add port 5001")
    print(f"4. Test connectivity from phone: ping {local_ip}")
    print(f"5. Try alternative addresses listed above")
    print("="*70)
    
    # Try to generate QR code for easy mobile access
    main_url = f"http://{local_ip}:5001"
    if not generate_qr_code_ascii(main_url):
        print(f"\n📱 QUICK PHONE ACCESS:")
        print(f"   Bookmark this: {main_url}")
        print(f"   Or install 'qrcode' for QR codes: pip install qrcode[pil]")
    
    print("="*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ ERROR: Port 5001 is already in use!")
            print("💡 SOLUTION: Run this command to free the port:")
            print("   lsof -ti:5001 | xargs kill -9")
            print("   Then restart the server.")
        else:
            print(f"❌ ERROR: {e}")
        exit(1)