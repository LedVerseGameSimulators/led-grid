import { useEffect, useState } from 'react'

import { API_URL } from '../config'
import { formatLevelLabel } from '../levelPlaylists'
import VideoBackground from '../components/VideoBackground'

export default function ResultScreen({ result, config, onPlayAgain, onLogout }) {
  const score = result?.score ?? 0
  const score2 = result?.score2 ?? 0
  const multiplayer = result?.multiplayer ?? false
  const time = result?.time_elapsed ?? 0
  const life = result?.life ?? 0
  const REASONS = {
    timeout: 'Time Up!',
    out_of_life: 'Out of Life!',
    stopped: 'Game Stopped',
  }
  const reason = REASONS[result?.reason] || 'Game Over'
  const levelLabel = result?.end_level ?? result?.level
    ?? formatLevelLabel(config.playMode, result?.end_level ?? config.level)
  const leaderboardKey = result?.level
    ?? formatLevelLabel(config.playMode, config.level)

  const [board, setBoard] = useState([])
  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_URL}/leaderboard/${encodeURIComponent(leaderboardKey)}?limit=5`
        )
        const data = await res.json()
        if (data.success) setBoard(data.entries || [])
      } catch (err) {
        console.error('leaderboard fetch:', err)
      }
    }, 300)
    return () => clearTimeout(t)
  }, [leaderboardKey])

  return (
    <div className="screen screen-with-video">
      <VideoBackground />
      <div className="card">
        <h1>Game Over</h1>
        <p className="result-reason">{reason}</p>

        <div className="result-score-panel">
          <div className="result-score-label">
            {multiplayer ? 'P1 Score' : 'Final Score'}
          </div>
          <div className="result-score-value">{score}</div>
          {multiplayer && (
            <div style={{ marginTop: 12 }}>
              <div className="result-score-label">P2 Score</div>
              <div className="result-score-value-p2">{score2}</div>
            </div>
          )}
        </div>

        <div className="result-stats">
          <div className="result-stat">
            <div className="result-stat-value">{time.toFixed(1)}s</div>
            <div className="result-stat-label">Time</div>
          </div>
          <div className="result-stat">
            <div className="result-stat-value">{levelLabel}</div>
            <div className="result-stat-label">Level</div>
          </div>
          <div className="result-stat">
            <div
              className="result-stat-value"
              style={{ color: life > 0 ? 'var(--color-success)' : 'var(--color-error)' }}
            >
              {life}
            </div>
            <div className="result-stat-label">Life</div>
          </div>
          <div className="result-stat">
            <div className="result-stat-value">Medium</div>
            <div className="result-stat-label">Difficulty</div>
          </div>
        </div>

        {board.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <div className="setup-label">Top scores — Level {levelLabel}</div>
            {board.map((e, i) => (
              <div
                key={`${e.card_id}-${i}`}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '10px 0',
                  borderBottom: '1px solid rgba(255,255,255,0.08)',
                  color: e.card_id === config.cardId ? 'var(--accent)' : 'var(--text-muted)',
                  fontWeight: e.card_id === config.cardId ? 700 : 400,
                }}
              >
                <span>#{i + 1} {e.card_id || '—'}</span>
                <span>{e.score} pts</span>
              </div>
            ))}
          </div>
        )}

        <button type="button" className="btn-primary" onClick={onPlayAgain} style={{ marginTop: 20 }}>
          Play Again
        </button>
        <button type="button" className="btn-secondary" onClick={onLogout}>
          Logout
        </button>
      </div>
    </div>
  )
}
