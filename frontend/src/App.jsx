import { useState, useEffect } from 'react'
import LoginScreen        from './screens/LoginScreen'
import GameSelectionScreen from './screens/GameSelectionScreen'
import GameSettingsScreen  from './screens/GameSettingsScreen'
import CountdownScreen     from './screens/CountdownScreen'
import SimulatorScreen     from './screens/SimulatorScreen'
import ResultScreen        from './screens/ResultScreen'

import { API_URL } from './config'

const S = {
  GAME_SELECT: 'game_select',  // pick game type (LED Hex, Hoops…)
  SETTINGS:    'settings',     // pick players + category + level + difficulty
  LOGIN:       'login',        // enter 1 or 2 card IDs
  COUNTDOWN:   'countdown',
  SIMULATOR:   'simulator',
  RESULT:      'result',
}

export default function App() {
  const [screen, setScreen] = useState(S.GAME_SELECT)
  const [gameConfig, setGameConfig] = useState({
    game: 'grid',
    level: '001',
    playerCount: 1,
    difficulty: 'normal',
    cardId: '',
    cardId2: '',
    playerName: '',
    playerName2: '',
  })
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

  // Step 1: game type selected
  const handleGameSelect = (game) => {
    setGameConfig(prev => ({ ...prev, game }))
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

  // Step 3: login (1 or 2 cards, or guest name for anonymous)
  const handleLogin = (cardId, cardId2, playerName = '', playerName2 = '') => {
    setGameConfig(prev => ({
      ...prev,
      cardId: cardId || '',
      cardId2: cardId2 || '',
      playerName: playerName || '',
      playerName2: playerName2 || '',
    }))
    setScreen(S.COUNTDOWN)
  }

  const handleGameEnd = (finalResult) => {
    setResult(finalResult)
    setScreen(S.RESULT)
  }

  const handlePlayAgain = () => {
    setResult(null)
    setScreen(S.SETTINGS)
  }

  const handleLogout = () => {
    setResult(null)
    setGameConfig({ game: 'grid', level: '001', playerCount: 1,
                   difficulty: 'normal', cardId: '', cardId2: '' })
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
        <GameSelectionScreen onSelect={handleGameSelect} />
      )}
      {screen === S.SETTINGS && (
        <GameSettingsScreen
          game={gameConfig.game}
          onConfirm={handleSettings}
          onBack={() => setScreen(S.GAME_SELECT)}
        />
      )}
      {screen === S.LOGIN && (
        <LoginScreen
          gameTitle="⛰️ Climb"
          playerCount={gameConfig.playerCount}
          onLogin={handleLogin}
          onBack={() => setScreen(S.SETTINGS)}
        />
      )}
      {screen === S.COUNTDOWN && (
        <CountdownScreen
          config={gameConfig}
          onDone={() => setScreen(S.SIMULATOR)}
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
