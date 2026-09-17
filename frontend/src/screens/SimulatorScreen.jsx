import { useEffect, useState, useRef } from 'react'

import { API_URL, WS_BRIDGE_URL } from '../config'
import { formatLevelLabel, TOURNAMENT_LEVEL_ORDER } from '../levelPlaylists'

function countdownDisplay(state) {
  if (!state || state.phase !== 'countdown') return null
  // Hex: phase_step / countdown_step; Grid backend still publishes countdown_digit
  const step = state.phase_step ?? state.countdown_step ?? state.countdown_digit
  if (step == null) return ''
  return String(step)
}

function isInputBlocked(state) {
  if (!state) return true
  if (state.accepting_input === false) return true
  return state.phase && state.phase !== 'playing'
}

function showPhaseOverlay(state) {
  return ['countdown', 'level_clear', 'level_fail'].includes(state?.phase)
}

function HeartRow({ life, maxLife }) {
  // Cap visual hearts (backend display_max is typically 5)
  const total = Math.max(1, Math.min(10, Math.round(maxLife) || 5))
  const filled = Math.max(0, Math.min(total, Math.round(life)))
  return (
    <div className="hud-hearts" aria-label={`${filled} of ${total} lives`}>
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={`hud-heart ${i < filled ? 'filled' : 'empty'}`}>♥</span>
      ))}
    </div>
  )
}

/** CSS color from backend goal_color [r,g,b] or goal_color_hex. */
function goalSwatchCss(rgb, hex) {
  if (typeof hex === 'string' && hex) return hex
  if (Array.isArray(rgb) && rgb.length >= 3) {
    return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`
  }
  return null
}

export default function SimulatorScreen({ config, onGameEnd }) {
  const [gameState, setGameState] = useState(null)
  const [gameId, setGameId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stopping, setStopping] = useState(false)
  const [showSim, setShowSim] = useState(false)
  const iframeRef = useRef(null)
  const gameIdRef = useRef(null)
  const endedRef = useRef(false)
  const stateRef = useRef(null)
  // Audio: synth beeps via Web Audio (no asset files needed)
  const audioCtxRef = useRef(null)
  const prevScoreRef = useRef(0)
  const prevLifeRef = useRef(null)
  const startedRef = useRef(false)

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
    if (startedRef.current) return
    startedRef.current = true
    // Resuming: backend game already exists, don't start a new one.
    if (config.resumeGameId) {
      setGameId(config.resumeGameId)
      gameIdRef.current = config.resumeGameId
      setLoading(false)
      return
    }
    const startGame = async () => {
      try {
        const response = await fetch(`${API_URL}/start-game`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            card_id: config.cardId,
            level: config.playMode === 'group' ? (config.level || 'auto') : (config.level || '001'),
            difficulty: config.difficulty || 'normal',
            ...(config.playMode === 'group' ? { mode: 'group' } : {}),
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

    // Player-facing level names (1, 2, 3…) for scores / RFID / leaderboards.
    // Real file stems are only used to load levels via start-game (config.level).
    const startStem =
      config.playMode === 'group' && (!config.level || config.level === 'auto')
        ? TOURNAMENT_LEVEL_ORDER[0]
        : (config.level || '')
    const endStem = st.current_level ?? startStem
    const levelLabel = formatLevelLabel(config.playMode, startStem)
    const endLevelLabel = formatLevelLabel(config.playMode, endStem)
    // Guests (no RFID): skip save-score only. Always stop the backend game
    // so BGM / session teardown still run.
    const hasRfidCard = Boolean(config.cardId && String(config.cardId).trim())

    try {
      if (hasRfidCard) {
        await fetch(`${API_URL}/save-score`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            card_id: config.cardId,
            card_id2: config.cardId2 || null,
            level: levelLabel,
            end_level: endLevelLabel,
            level_file: startStem,
            end_level_file: endStem,
            score: finalScore,
            score2: finalScore2,
            final_score: st.final_score ?? finalScore,
            final_score2: st.final_score2 ?? finalScore2,
            multiplayer: finalMultiplayer,
            life: finalLife,
            lives_start: st.max_life ?? 0,
            result: st.result ?? null,
            time_used: finalTime,
            levels_cleared: st.levels_cleared ?? 0,
            difficulty: config.difficulty ?? '',
            started_at: st.started_at ?? '',
            player_name: config.playerName || '',
            player_name2: config.playerName2 || '',
          })
        })
      }
      // Always stop game (BGM + floor blank) — guests too
      if (id) {
        await fetch(`${API_URL}/logout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ card_id: config.cardId || '', game_id: id })
        })
      }
    } catch (err) {
      console.error('Stop/save error:', err)
    }
    onGameEnd({
      score: finalScore,
      score2: finalScore2,
      multiplayer: finalMultiplayer,
      time_elapsed: finalTime,
      life: finalLife,
      level: levelLabel,
      end_level: endLevelLabel,
      level_file: startStem,
      end_level_file: endStem,
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
          const backendAudio =
            st.backend_audio_active === true || st.audio_active === true
          const inputLive = st.accepting_input === true && st.phase === 'playing'
          // Sound cues on score gain / life loss (mute when backend audio owns SFX)
          if (!backendAudio && inputLive && st.score > prevScoreRef.current) playScore()
          if (!backendAudio && inputLive && prevLifeRef.current !== null && st.life < prevLifeRef.current) playHurt()
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
    const interval = setInterval(pollState, 100)
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
          <p style={{ color: 'var(--color-error)', marginTop: '20px' }}>{error}</p>
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
  const phase = gameState?.phase || (isOver ? 'session_end' : 'playing')
  const inputLocked = isInputBlocked(gameState)
  const countdownLabel = countdownDisplay(gameState)
  const phaseOverlay = showPhaseOverlay(gameState) && !isOver
  const isMulti = !!(gameState?.multiplayer || config.playerCount === 2)
  const p1Name = config.playerName || 'Player 1'
  const p2Name = config.playerName2 || 'Player 2'
  const currentLevelRaw = gameState?.current_level ?? config.level
  const currentLevelLabel = formatLevelLabel(config.playMode, currentLevelRaw)
  // Goal swatches: only when backend says Team Battle multiplayer (not FE playerCount alone)
  const showGoalSwatches = gameState?.multiplayer === true
  const p1SwatchCss = showGoalSwatches
    ? goalSwatchCss(gameState.goal_color, gameState.goal_color_hex)
    : null
  const p2SwatchCss = showGoalSwatches
    ? goalSwatchCss(gameState.goal2_color, gameState.goal2_color_hex)
    : null

  return (
    <div className="simulator-container">
      <div className="simulator-header">
        <div>
          <h2 style={{ margin: 0 }}>
            Mega Grid — Level {currentLevelLabel}
          </h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {config.playMode === 'group'
              ? 'Tournament'
              : config.playMode === 'multi'
                ? 'Team Battle'
                : 'Quick Play'}
          </span>
        </div>

        <div className="game-info">
          <button
            type="button"
            className="view-toggle-btn"
            onClick={() => setShowSim(v => !v)}
          >
            {showSim ? 'Show game board' : 'Show simulator'}
          </button>
          <button
            type="button"
            className="stop-game-btn"
            onClick={() => endGame('stopped')}
            disabled={stopping}
          >
            {stopping ? 'Stopping...' : '■ Stop Game'}
          </button>
        </div>
      </div>

      {/* Stable stage: iframe always full-size; HUD overlays on top */}
      <div className="simulator-stage">
        <iframe
          ref={iframeRef}
          className={`simulator-iframe ${showSim ? '' : 'simulator-iframe--hidden'}`}
          src={gameId ? `${WS_BRIDGE_URL}?game_id=${gameId}` : WS_BRIDGE_URL}
          title="Game Simulator"
        />

        {phaseOverlay && gameState?.phase === 'countdown' && (
          <div
            className={`phase-countdown-overlay step-${countdownLabel || 'pending'}`}
            aria-live="polite"
          >
            <div className="phase-countdown-digit">{countdownLabel || '…'}</div>
            <div className="phase-countdown-level">Level {currentLevelLabel}</div>
          </div>
        )}

        {phaseOverlay && gameState?.phase === 'level_clear' && (
          <div className="phase-transition-overlay level-clear-overlay" aria-live="polite">
            Level clear!
          </div>
        )}

        {phaseOverlay && gameState?.phase === 'level_fail' && (
          <div className="phase-transition-overlay level-fail-overlay" aria-live="polite">
            Try again!
          </div>
        )}

        {!showSim && (
          <div className={`play-hud ${inputLocked ? 'play-hud--locked' : ''}`}>
            <div className="hud-board">
              <div className="hud-meta">
                <span className="hud-level">Level {currentLevelLabel}</span>
                <span className="hud-diff">MEDIUM</span>
                <span className={`hud-status ${isOver ? 'ended' : phase === 'playing' ? 'playing' : 'transition'}`}>
                  {isOver ? '● ENDED' : phase === 'playing' ? '● PLAYING' : `● ${String(phase).toUpperCase()}`}
                </span>
              </div>

              <div className={`hud-players ${isMulti ? 'multi' : 'solo'}`}>
                <div className="hud-player">
                  <div className="hud-player-name">{p1Name}</div>
                  {config.minutesRemaining != null && (
                    <div className="hud-session-mins">
                      {Math.round(config.minutesRemaining)} min left
                    </div>
                  )}
                  <div className="hud-score">{gameState?.score ?? 0}</div>
                  <div className="hud-score-label">{isMulti ? 'P1 Score' : 'Score'}</div>
                  {p1SwatchCss && (
                    <div
                      className="hud-goal-swatch"
                      style={{ backgroundColor: p1SwatchCss }}
                      title="P1 target color"
                      aria-label="P1 target color"
                    />
                  )}
                </div>
                {isMulti && (
                  <div className="hud-player hud-player--p2">
                    <div className="hud-player-name">{p2Name}</div>
                    {config.minutesRemaining2 != null && (
                      <div className="hud-session-mins">
                        {Math.round(config.minutesRemaining2)} min left
                      </div>
                    )}
                    <div className="hud-score">{gameState?.score2 ?? 0}</div>
                    <div className="hud-score-label">P2 Score</div>
                    {p2SwatchCss && (
                      <div
                        className="hud-goal-swatch"
                        style={{ backgroundColor: p2SwatchCss }}
                        title="P2 target color"
                        aria-label="P2 target color"
                      />
                    )}
                  </div>
                )}
              </div>

              <div className="hud-stats">
                <div className="hud-stat">
                  <span
                    className="hud-stat-value"
                    style={{ color: timeLeft < 30 ? 'var(--color-error)' : 'var(--text-primary)' }}
                  >
                    {Math.max(0, timeLeft).toFixed(0)}s
                  </span>
                  <span className="hud-stat-label">Time Left</span>
                </div>
                <div className="hud-stat">
                  <HeartRow life={life} maxLife={maxLife} />
                  <span className="hud-stat-label">Lives {life}/{maxLife}</span>
                </div>
              </div>

              <button
                type="button"
                className="stop-game-btn stop-game-btn--lg"
                onClick={() => endGame('stopped')}
                disabled={stopping}
              >
                {stopping ? 'Stopping...' : '■ Stop Game'}
              </button>
            </div>
          </div>
        )}
      </div>

      {(config.playerName || config.playerName2) && (
        <div className="sim-player-bar">
          {config.playerName && (
            <span>
              {config.playerName}
              {config.minutesRemaining != null
                ? ` — ${Math.round(config.minutesRemaining)} min left`
                : ''}
            </span>
          )}
          {config.playerName2 && (
            <span className="sim-player-bar-p2">
              {config.playerName2}
              {config.minutesRemaining2 != null
                ? ` — ${Math.round(config.minutesRemaining2)} min left`
                : ''}
            </span>
          )}
        </div>
      )}

      {showSim && inputLocked && !isOver && (
        <div className="sim-input-lock" aria-hidden="true">
          Input paused ({phase})
        </div>
      )}

      {showSim && (
        <div className="sim-debug-footer">
          Game ID: {gameId} | P1: {config.cardId}
          {config.cardId2 ? ` | P2: ${config.cardId2}` : ''}
        </div>
      )}
    </div>
  )
}
