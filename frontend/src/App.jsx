import { useState, useEffect, useRef } from 'react'
import LoginScreen         from './screens/LoginScreen'
import GameSelectionScreen from './screens/GameSelectionScreen'
import GameSettingsScreen  from './screens/GameSettingsScreen'
import CountdownScreen     from './screens/CountdownScreen'
import SimulatorScreen     from './screens/SimulatorScreen'
import ResultScreen        from './screens/ResultScreen'

import { API_URL } from './config'

const S = {
  GAME_SELECT: 'game_select',  // pick play mode (single / multi / group)
  SETTINGS:    'settings',     // pick category + level + difficulty
  LOGIN:       'login',        // enter 1 or 2 card IDs
  COUNTDOWN:   'countdown',
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
  const [groupLoading, setGroupLoading] = useState(false)
  const groupRequestIdRef = useRef(0)
  const groupLoadingRef = useRef(false)

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

  // Pick first 1P level from first 1P-capable category (prefer 'easy', then Object.keys order)
  const pickFirst1PLevel = (categories) => {
    const cats = categories || {}
    const keys = Object.keys(cats)
    const ordered = keys.includes('easy')
      ? ['easy', ...keys.filter(k => k !== 'easy')]
      : keys
    for (const cat of ordered) {
      const oneP = (cats[cat] || []).find(l => !l.multiplayer)
      if (oneP) return oneP.id
    }
    return null
  }

  const clearGroupLoading = () => {
    groupLoadingRef.current = false
    setGroupLoading(false)
  }

  const applyGroupConfig = (levelId) => {
    setGameConfig(prev => ({
      ...prev,
      game: 'grid',
      playMode: 'group',
      playerCount: 1,
      level: levelId,
      difficulty: 'normal',
      resumeGameId: undefined,
    }))
    clearGroupLoading()
    setScreen(S.LOGIN)
  }

  // Step 1: play mode selected (single | multi | group)
  const handleModeSelect = (mode) => {
    // Sync guard: block double-tap before React re-renders disabled cards
    if (groupLoadingRef.current) return

    if (mode === 'group') {
      groupLoadingRef.current = true
      setGroupLoading(true)
      const requestId = ++groupRequestIdRef.current
      // Group skips settings: auto-pick first 1P level → LOGIN
      fetch(`${API_URL}/levels`)
        .then(r => r.json())
        .then(d => {
          if (requestId !== groupRequestIdRef.current) return
          const levelId = d.success
            ? pickFirst1PLevel(d.categories) || DEFAULT_CONFIG.level
            : DEFAULT_CONFIG.level
          applyGroupConfig(levelId)
        })
        .catch(() => {
          if (requestId !== groupRequestIdRef.current) return
          applyGroupConfig(DEFAULT_CONFIG.level)
        })
      return
    }

    // Invalidate any in-flight group /levels fetch
    groupRequestIdRef.current += 1
    clearGroupLoading()

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
    setScreen(S.COUNTDOWN)
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
          loading={groupLoading}
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
