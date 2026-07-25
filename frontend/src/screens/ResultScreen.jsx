import { useEffect, useState } from 'react'

import { API_URL } from '../config'

export default function ResultScreen({ result, config, onPlayAgain, onLogout }) {
  const score = result?.score ?? 0
  const score2 = result?.score2 ?? 0
  const multiplayer = result?.multiplayer ?? false
  const time = result?.time_elapsed ?? 0
  const life = result?.life ?? 0
  const REASONS = {
    timeout: 'Time Up!',
    out_of_life: 'Out of Life!',
    stopped: 'Game Stopped'
  }
  const reason = REASONS[result?.reason] || 'Game Over'

  const [board, setBoard] = useState([])
  useEffect(() => {
    // Saved score is written before this screen; fetch the level leaderboard.
    const t = setTimeout(async () => {
      try {
        const res = await fetch(`${API_URL}/leaderboard/${config.level}?limit=5`)
        const data = await res.json()
        if (data.success) setBoard(data.entries || [])
      } catch (err) {
        console.error('leaderboard fetch:', err)
      }
    }, 300)
    return () => clearTimeout(t)
  }, [config.level])

  return (
    <div className="screen">
      <div className="card">
        <h1>Game Over</h1>
        <p className="result-reason">{reason}</p>

        {/* Final score panel */}
        <div className="result-score-panel">
          <div className="result-score-label">
            {multiplayer ? 'P1 SCORE' : 'FINAL SCORE'}
          </div>
          <div className="result-score-value">{score}</div>
          {multiplayer && (
            <div style={{ marginTop: '12px' }}>
              <div className="result-score-label">P2 SCORE</div>
              <div className="result-score-value-p2">{score2}</div>
            </div>
          )}
        </div>

        <div className="result-stats">
          <div className="result-stat">
            <div className="result-stat-value">{time.toFixed(1)}s</div>
            <div className="result-stat-label">Time Played</div>
          </div>
          <div className="result-stat">
            <div className="result-stat-value">{config.level}</div>
            <div className="result-stat-label">Level</div>
          </div>
          <div className="result-stat">
            <div
              className="result-stat-value"
              style={{ color: life > 0 ? 'var(--color-success)' : 'var(--color-error)' }}
            >
              {life}
            </div>
            <div className="result-stat-label">Life Left</div>
          </div>
          <div className="result-stat">
            <div className="result-stat-value">{config.difficulty?.toUpperCase()}</div>
            <div className="result-stat-label">Difficulty</div>
          </div>
        </div>

        {/* Leaderboard for this level */}
        {board.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Top Scores — Level {config.level}
            </div>
            <div style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              overflow: 'hidden',
            }}>
              {board.map((e, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between',
                  padding: '8px 14px',
                  borderBottom: i < board.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                  color: e.card_id === config.cardId ? 'var(--brand-orange)' : 'var(--text-secondary)',
                  fontWeight: e.card_id === config.cardId ? 'bold' : 'normal'
                }}>
                  <span>#{i + 1} &nbsp; {e.card_id || '—'}</span>
                  <span>{e.score} pts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <button onClick={onPlayAgain} style={{ marginTop: '25px' }}>Play Again</button>
        <button onClick={onLogout} className="btn-secondary" style={{ marginTop: '10px' }}>
          Logout
        </button>
      </div>
    </div>
  )
}
