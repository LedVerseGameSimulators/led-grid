"""
API Configuration - Game and Database Settings
"""
import os
import sys
from pathlib import Path

from .runtime_paths import games_root, install_root

# GAMES_ROOT: path to the games directory (data + engine packages in dev).
# Default via runtime_paths (repo games/ in dev; install_root()/games when frozen).
# Override with GAMES_ROOT env var if running from a different location.
_REPO_ROOT = install_root()
GAMES_ROOT = games_root()

# Game Configuration
GAME_NAME = "grid"
GAME_DIR = GAMES_ROOT
GAME_SOURCE_DIR = GAME_DIR / "game_play"
GAME_LEVEL_DIR = GAME_DIR / "source"
# Group-mode playlist root (same dash-folder layout as 1P tiers under source/).
# Override with GAMES_GROUP_LEVEL_DIR if needed.
GAME_GROUP_LEVEL_DIR = Path(
    os.getenv("GAMES_GROUP_LEVEL_DIR", str(GAME_DIR / "source_group"))
)
GAME_SETTING_DIR = GAME_DIR / "setting"

# Add game source to path for imports
if str(GAME_SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_SOURCE_DIR))

if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "ledplaydb")

# API Configuration
API_HOST = "0.0.0.0"
# Must match frontend/src/config.js (source of truth) and START_GAME.bat.
API_PORT = int(os.getenv("API_PORT", 8003))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Game Configuration
MAX_CONCURRENT_GAMES = 10
GAME_TIMEOUT_SECONDS = 600  # 10 minutes
GAME_STATE_UPDATE_INTERVAL = 0.016  # ~60fps

# Session Configuration
SESSION_DURATION_SECONDS = 3600  # 60 minutes
