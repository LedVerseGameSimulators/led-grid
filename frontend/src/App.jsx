import { useState, useEffect } from 'react'
import LoginScreen         from './screens/LoginScreen'
import GameSelectionScreen from './screens/GameSelectionScreen'
import GameSettingsScreen  from './screens/GameSettingsScreen'
import SimulatorScreen     from './screens/SimulatorScreen'
import ResultScreen        from './screens/ResultScreen'

import { API_URL } from './config'

const S = {
  GAME_SELECT: 'game_select',  // pick play mode (single / multi / group)
  SETTINGS:    'settings',     // pick category + level + difficulty
  LOGIN:       'login',        // enter 1 or 2 card IDs
  SIMULATOR:   'simulator',
  RESULT:      'result',
}

const DEFAULT_CONFIG = {
  game: 'grid',
  playMode: 'single',
  level: '001',
  playerCount: 1,
  difficulty: 'normal',
  cardId: '',
  cardId2: '',
  playerName: '',
  playerName2: '',
  minutesRemaining: null,
  minutesRemaining2: null,
}

export default function App() {
  const [screen, setScreen] = useState(S.GAME_SELECT)
  const [gameConfig, setGameConfig] = useState(DEFAULT_CONFIG)
  const [result, setResult] = useState(null)
  const [booting, setBooting] = useState(true)

  // Resume running game on reload
  useEffect(() => {
    fetch(`${API_URL}/active-game`)
      .then(r => r.json())
      .then(d => {
        if (d.success) {
          setGameConfig(prev => ({
            ...prev,
            cardId: d.card_id,
            level: d.level,
            difficulty: d.difficulty,
            resumeGameId: d.game_id,
          }))
          setScreen(S.SIMULATOR)
        }
      })
      .catch(() => {})
      .finally(() => setBooting(false))
  }, [])

  // Step 1: play mode selected (single | multi | group)
  const handleModeSelect = (mode) => {
    if (mode === 'group') {
      // Group skips settings; backend builds playlist from games/source_group/
      setGameConfig(prev => ({
        ...prev,
        game: 'grid',
        playMode: 'group',
        playerCount: 1,
        level: 'auto',
        difficulty: 'normal',
        resumeGameId: undefined,
      }))
      setScreen(S.LOGIN)
      return
    }

    if (mode === 'multi') {
      setGameConfig(prev => ({
        ...prev,
        game: 'grid',
        playMode: 'multi',
        playerCount: 2,
      }))
      setScreen(S.SETTINGS)
      return
    }

    setGameConfig(prev => ({
      ...prev,
      game: 'grid',
      playMode: 'single',
      playerCount: 1,
    }))
    setScreen(S.SETTINGS)
  }

  // Step 2: settings confirmed — clear resumeGameId so simulator starts fresh
  const handleSettings = ({ game, level, playerCount, difficulty }) => {
    setGameConfig(prev => ({
      ...prev, game, level, playerCount, difficulty,
      resumeGameId: undefined   // don't resume old game
    }))
    setScreen(S.LOGIN)
  }

  // Step 3: login (1 or 2 cards)
  const handleLogin = (cardId, cardId2, playerName = '', playerName2 = '',
                       minutesRemaining = null, minutesRemaining2 = null) => {
    setGameConfig(prev => ({
      ...prev,
      cardId: cardId || '',
      cardId2: cardId2 || '',
      playerName: playerName || '',
      playerName2: playerName2 || '',
      minutesRemaining,
      minutesRemaining2,
    }))
    setScreen(S.SIMULATOR)
  }

  const handleGameEnd = (finalResult) => {
    setResult(finalResult)
    setScreen(S.RESULT)
  }

  const handlePlayAgain = () => {
    setResult(null)
    // Group returns to landing; single/multi return to level settings
    setScreen(gameConfig.playMode === 'group' ? S.GAME_SELECT : S.SETTINGS)
  }

  const handleLogout = () => {
    setResult(null)
    setGameConfig({ ...DEFAULT_CONFIG })
    setScreen(S.GAME_SELECT)
  }

  if (booting) return (
    <div className="screen">
      <div className="card"><h2 style={{ textAlign: 'center' }}>Loading…</h2></div>
    </div>
  )

  return (
    <>
      {screen === S.GAME_SELECT && (
        <GameSelectionScreen
          onSelect={handleModeSelect}
        />
      )}
      {screen === S.SETTINGS && (
        <GameSettingsScreen
          game={gameConfig.game}
          playerCount={gameConfig.playerCount}
          onConfirm={handleSettings}
          onBack={() => setScreen(S.GAME_SELECT)}
        />
      )}
      {screen === S.LOGIN && (
        <LoginScreen
          gameTitle="Floor Is Lava"
          playerCount={gameConfig.playerCount}
          onLogin={handleLogin}
          onBack={() => setScreen(
            gameConfig.playMode === 'group' ? S.GAME_SELECT : S.SETTINGS
          )}
        />
      )}
      {screen === S.SIMULATOR && (
        <SimulatorScreen config={gameConfig} onGameEnd={handleGameEnd} />
      )}
      {screen === S.RESULT && (
        <ResultScreen
          result={result}
          config={gameConfig}
          onPlayAgain={handlePlayAgain}
          onLogout={handleLogout}
        />
      )}
    </>
  )
}
