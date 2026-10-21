import { useState, useEffect } from 'react'
import SetupScreen     from './screens/SetupScreen'
import LoginScreen     from './screens/LoginScreen'
import CountdownScreen from './screens/CountdownScreen'
import SimulatorScreen from './screens/SimulatorScreen'
import ResultScreen    from './screens/ResultScreen'

import { API_URL } from './config'
import { loadGameResumeContext } from './gameResumeContext'
import VideoBackground from './components/VideoBackground'

const S = {
  SETUP:     'setup',      // Mode + Level (one screen)
  LOGIN:     'login',
  COUNTDOWN: 'countdown',
  SIMULATOR: 'simulator',
  RESULT:    'result',
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
  rfidValidate1: null,
  rfidValidate2: null,
}

export default function App() {
  const [screen, setScreen] = useState(S.SETUP)
  const [gameConfig, setGameConfig] = useState(DEFAULT_CONFIG)
  const [result, setResult] = useState(null)
  const [booting, setBooting] = useState(true)
  const [playlists, setPlaylists] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/playlists`)
      .then((r) => r.json())
      .then((data) => {
        if (data && (data.single || data.multi || data.group)) {
          setPlaylists(data)
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    fetch(`${API_URL}/active-game`)
      .then((r) => r.json())
      .then((d) => {
        if (d.success) {
          const saved = loadGameResumeContext(d.game_id)
          const mergeResume =
            saved && saved.game_id === d.game_id
              ? {
                  playMode: saved.playMode ?? undefined,
                  playerCount: saved.playerCount ?? undefined,
                  cardId: saved.cardId ?? d.card_id,
                  cardId2: saved.cardId2 ?? undefined,
                  rfidValidate1: saved.rfidValidate1 ?? undefined,
                  rfidValidate2: saved.rfidValidate2 ?? undefined,
                  playerName: saved.playerName ?? undefined,
                  playerName2: saved.playerName2 ?? undefined,
                  minutesRemaining: saved.minutesRemaining ?? undefined,
                  minutesRemaining2: saved.minutesRemaining2 ?? undefined,
                }
              : {}
          setGameConfig((prev) => ({
            ...prev,
            cardId: mergeResume.cardId ?? d.card_id,
            level: d.level,
            difficulty: d.difficulty,
            resumeGameId: d.game_id,
            ...mergeResume,
          }))
          setScreen(S.SIMULATOR)
        }
      })
      .catch(() => {})
      .finally(() => setBooting(false))
  }, [])

  // Setup confirmed (mode + level together)
  const handleSetup = ({ game, level, playerCount, difficulty, playMode }) => {
    setGameConfig((prev) => ({
      ...prev,
      game,
      level,
      playerCount,
      difficulty,
      playMode: playMode || prev.playMode,
      playlists: playlists ?? prev.playlists,
      resumeGameId: undefined,
    }))
    setScreen(S.LOGIN)
  }

  const handleLogin = (
    cardId,
    cardId2,
    playerName = '',
    playerName2 = '',
    minutesRemaining = null,
    minutesRemaining2 = null,
    rfidValidate1 = null,
    rfidValidate2 = null
  ) => {
    setGameConfig((prev) => ({
      ...prev,
      cardId: cardId || '',
      cardId2: cardId2 || '',
      playerName: playerName || '',
      playerName2: playerName2 || '',
      minutesRemaining,
      minutesRemaining2,
      rfidValidate1: rfidValidate1 || null,
      rfidValidate2: rfidValidate2 || null,
    }))
    setScreen(S.COUNTDOWN)
  }

  const handleCountdownDone = () => setScreen(S.SIMULATOR)

  const handleGameEnd = (finalResult) => {
    setResult(finalResult)
    setScreen(S.RESULT)
  }

  const handlePlayAgain = () => {
    setResult(null)
    setScreen(S.SETUP)
  }

  const handleLogout = () => {
    setResult(null)
    setGameConfig({ ...DEFAULT_CONFIG })
    setScreen(S.SETUP)
  }

  if (booting) {
    return (
      <div className="screen screen-with-video">
        <VideoBackground />
        <div className="card">
          <h2 style={{ textAlign: 'center' }}>Loading…</h2>
        </div>
      </div>
    )
  }

  return (
    <>
      {screen === S.SETUP && (
        <SetupScreen
          game={gameConfig.game}
          playlists={playlists}
          onConfirm={handleSetup}
        />
      )}
      {screen === S.LOGIN && (
        <LoginScreen
          gameTitle="Mega Grid"
          playerCount={gameConfig.playerCount}
          onLogin={handleLogin}
          onBack={() => setScreen(S.SETUP)}
        />
      )}
      {screen === S.COUNTDOWN && (
        <CountdownScreen onDone={handleCountdownDone} />
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
