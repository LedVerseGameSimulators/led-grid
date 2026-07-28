"""
API Request/Response Models (Pydantic)
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

# ============= LOGIN =============
class LoginRequest(BaseModel):
    card_id: str

class PlayerInfo(BaseModel):
    custom_id: int
    name: str
    phone: str
    time_left: float  # seconds
    card_id: str

class LoginResponse(BaseModel):
    success: bool
    player: Optional[PlayerInfo] = None
    error: Optional[str] = None

# ============= GAME START =============
class StartGameRequest(BaseModel):
    card_id: str
    level: Optional[Union[int, str]] = None  # omitted/auto for group mode
    difficulty: str = "normal"  # "easy", "normal", "hard"
    mode: Optional[str] = None  # "group" → marathon from games/source_group/

class StartGameResponse(BaseModel):
    success: bool
    game_id: Optional[str] = None
    ws_url: Optional[str] = None
    error: Optional[str] = None

# ============= GAME STATE (WebSocket) =============
class GameState(BaseModel):
    type: str = "game_state"
    data: Dict[str, Any] = {
        "score": 0,
        "time_elapsed": 0.0,
        "time_left": 0.0,
        "player_pos": [0, 0],
        "led_display": [],
        "game_over": False,
        "game_over_reason": ""
    }

class GameInput(BaseModel):
    type: str = "input"
    data: Dict[str, Any] = {
        "button": "left",  # "left" | "right" | "jump"
        "timestamp": 0.0
    }

# ============= GAME RESULT =============
class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    score: int
    timestamp: str

class GameResult(BaseModel):
    success: bool
    score: Optional[int] = None
    player_name: Optional[str] = None
    time_used: Optional[float] = None
    difficulty: Optional[str] = None
    leaderboard: Optional[List[LeaderboardEntry]] = None
    error: Optional[str] = None

# ============= LOGOUT =============
class LogoutRequest(BaseModel):
    card_id: str
    game_id: str

class LogoutResponse(BaseModel):
    success: bool
    error: Optional[str] = None
