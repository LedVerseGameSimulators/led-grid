import { useEffect, useState, useRef } from 'react'

import { API_URL, WS_BRIDGE_URL } from '../config'

export default function SimulatorScreen({ config, onGameEnd }) {
  const [gameState, setGameState] = useState(null)
  const [gameId, setGameId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stopping, setStopping] = useState(false)
  const iframeRef = useRef(null)
  const gameIdRef = useRef(null)
  const endedRef = useRef(false)
  const stateRef = useRef(null)
  const startedRef = useRef(false)  // guards against StrictMode's dev-mode double-mount
  // Audio: synth beeps via Web Audio (no asset files needed)
  const audioCtxRef = useRef(null)
  const prevScoreRef = useRef(0)
  const prevLifeRef = useRef(null)

  const beep = (freq, durMs, type = 'sine', gain = 0.15) => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }
      const ctx = audioCtxRef.current
      const osc = ctx.createOscillator()
      const g = ctx.createGain()
      osc.type = type
      osc.frequency.value = freq
      g.gain.value = gain
      osc.connect(g); g.connect(ctx.destination)
      osc.start()
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + durMs / 1000)
      osc.stop(ctx.currentTime + durMs / 1000)
    } catch (e) { /* audio not available */ }
  }
  const playScore = () => beep(880, 120, 'triangle', 0.18)   // bright ding
  const playHurt = () => beep(140, 220, 'sawtooth', 0.22)    // low buzz

  // Start game on mount (or resume an already-running game after reload)
  useEffect(() => {
    // Resuming: backend game already exists, don't start a new one.
    if (config.resumeGameId) {
      setGameId(config.resumeGameId)
      gameIdRef.current = config.resumeGameId
      setLoading(false)
      return
    }
    // React.StrictMode intentionally mounts/unmounts/remounts once in dev,
    // which would otherwise fire this effect (and POST /start-game) twice
    // in quick succession, racing two game instances against each other.
    if (startedRef.current) return
    startedRef.current = true
    const startGame = async () => {
      try {
        const response = await fetch(`${API_URL}/start-game`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            card_id: config.cardId,
            level: config.level || '001',
            difficulty: config.difficulty || 'normal'
          })
        })
        const data = await response.json()
        if (data.success) {
          setGameId(data.game_id)
          gameIdRef.current = data.game_id
          setLoading(false)
        } else {
          setError(data.error || 'Failed to start game')
        }
      } catch (err) {
        setError(err.message)
      }
    }
    startGame()
  }, [config])

  // End the game: stop on backend, record, route to result panel
  const endGame = async (reason) => {
    if (endedRef.current) return
    endedRef.current = true
    setStopping(true)
    const id = gameIdRef.current
    const st = stateRef.current || {}
    const finalScore = st.score || 0
    const finalScore2 = st.score2 || 0
    const finalMultiplayer = st.multiplayer || false
    const finalTime = st.time_elapsed || 0
    const finalLife = st.life ?? 0
    // out_of_life beats the passed reason (game ended because HP hit 0)
    const finalReason = st.game_over_reason === 'out_of_life'
      ? 'out_of_life' : (reason || 'stopped')
    try {
      // Persist score to leaderboard
      await fetch(`${API_URL}/save-score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          card_id: config.cardId,
          card_id2: config.cardId2 || null,
          level: config.level,                       // starting level picked
          end_level: st.current_level ?? config.level, // level ended on
          score: finalScore,                         // raw P1 (on-screen)
          score2: finalScore2,                       // raw P2 (on-screen)
          final_score: st.final_score ?? finalScore,   // normalized P1
          final_score2: st.final_score2 ?? finalScore2,// normalized P2
          multiplayer: finalMultiplayer,
          life: finalLife,
          lives_start: st.max_life ?? 0,
          result: st.result ?? null,
          time_used: finalTime,                      // full session duration
          levels_cleared: st.levels_cleared ?? 0,
          difficulty: config.difficulty ?? '',
          started_at: st.started_at ?? ''
        })
      })
      await fetch(`${API_URL}/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ card_id: config.cardId, game_id: id })
      })
    } catch (err) {
      console.error('Stop/save error:', err)
    }
    onGameEnd({
      score: finalScore,
      score2: finalScore2,
      multiplayer: finalMultiplayer,
      time_elapsed: finalTime,
      life: finalLife,
      level: config.level,
      game: config.game,
      difficulty: config.difficulty,
      reason: finalReason
    })
  }

  // Poll game state; auto-end on timeout/game_over
  useEffect(() => {
    if (!gameId) return
    const pollState = async () => {
      try {
        // Poll THIS game specifically (avoid stale "first active" game)
        const response = await fetch(`${API_URL}/game-state/${gameId}`)
        const data = await response.json()
        if (data.success) {
          const st = data.state
          // Sound cues on score gain / life loss
          if (st.score > prevScoreRef.current) playScore()
          if (prevLifeRef.current !== null && st.life < prevLifeRef.current) playHurt()
          prevScoreRef.current = st.score
          prevLifeRef.current = st.life

          setGameState(st)
          stateRef.current = st
          if (st.game_over && !endedRef.current) {
            endGame('timeout')
          }
        }
      } catch (err) {
        console.error('Poll error:', err)
      }
    }
    const interval = setInterval(pollState, 16)
    return () => clearInterval(interval)
  }, [gameId])

  if (loading) {
    return (
      <div className="screen">
        <div className="card">
          <h2>Starting Game...</h2>
          <p style={{ textAlign: 'center', marginTop: '20px' }}>
            {config.game.toUpperCase()} - Level {config.level} ({config.difficulty})
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="screen">
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: '#ff6b6b', marginTop: '20px' }}>{error}</p>
        </div>
      </div>
    )
  }

  const timeLeft = gameState?.time_left != null ? gameState.time_left : 300
  // Hearts: 5 shown (each absorbs a share of mistakes scaled to this game's own
  // max_life). Backend sends display_lives/display_max; fall back to raw HP.
  const life = gameState?.display_lives ?? gameState?.life ?? gameState?.max_life ?? 0
  const maxLife = gameState?.display_max ?? gameState?.max_life ?? 5
  const isOver = gameState?.game_over

  return (
    <div className="simulator-container">
      <div className="simulator-header">
        <div>
          <h2 style={{ margin: 0 }}>
            {config.game.toUpperCase()} - Level {gameState?.current_level ?? config.level}
          </h2>
          <span style={{ fontSize: '0.8rem', color: '#888' }}>
            {config.difficulty?.toUpperCase()}
          </span>
        </div>

        {/* Live score panel */}
        <div className="game-info">
          <div className="game-info-item">
            <span className="game-info-value">{gameState?.score ?? 0}</span>
            <span>{gameState?.multiplayer ? 'P1 Score' : 'Score'}</span>
          </div>
          {gameState?.multiplayer && (
            <div className="game-info-item">
              <span className="game-info-value" style={{ color: '#ffaa44' }}>
                {gameState?.score2 ?? 0}
              </span>
              <span>P2 Score</span>
            </div>
          )}
          <div className="game-info-item">
            <span className="game-info-value" style={{ color: timeLeft < 30 ? '#ff6b6b' : '#fff' }}>
              {Math.max(0, timeLeft).toFixed(0)}s
            </span>
            <span>Time Left</span>
          </div>
          <div className="game-info-item">
            <span className="game-info-value" style={{ color: life <= maxLife * 0.3 ? '#ff6b6b' : '#51cf66' }}>
              {life}/{maxLife}
            </span>
            <span>Life</span>
          </div>
          <div className="game-info-item">
            <span style={{ color: isOver ? '#ff6b6b' : '#51cf66' }}>
              {isOver ? '● ENDED' : '● PLAYING'}
            </span>
            <span>Status</span>
          </div>
          {/* Stop panel */}
          <button
            onClick={() => endGame('stopped')}
            disabled={stopping}
            style={{
              background: '#ff6b6b',
              padding: '10px 20px',
              fontSize: '0.9rem',
              width: 'auto',
              margin: 0
            }}
          >
            {stopping ? 'Stopping...' : '■ Stop Game'}
          </button>
        </div>
      </div>

      <div className="simulator-content">
        {gameId && (
          <iframe
            ref={iframeRef}
            src={`${WS_BRIDGE_URL}?game_id=${gameId}`}
            style={{ width: '100%', height: '100%', border: 'none' }}
            title="Game Simulator"
          />
        )}
      </div>

      <div style={{
        padding: '10px 20px',
        fontSize: '0.75rem',
        color: '#666',
        borderTop: '1px solid #1e1e2e',
        background: '#06060c'
      }}>
        Game ID: {gameId} | P1: {config.cardId}{config.cardId2 ? ` | P2: ${config.cardId2}` : ''}
      </div>
    </div>
  )
}
