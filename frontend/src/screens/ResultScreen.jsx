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
        <h1>🏁 Game Over</h1>
        <p style={{ textAlign: 'center', color: '#888', marginTop: '-10px' }}>{reason}</p>

        {/* Final score panel */}
        <div style={{
          marginTop: '25px',
          padding: '30px',
          background: '#06060c',
          borderRadius: '10px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '8px' }}>
            {multiplayer ? 'P1 SCORE' : 'FINAL SCORE'}
          </div>
          <div style={{ fontSize: '3.5rem', fontWeight: 'bold', color: '#c8b4fa', lineHeight: 1 }}>
            {score}
          </div>
          {multiplayer && (
            <div style={{ marginTop: '12px' }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '4px' }}>P2 SCORE</div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#ffaa44', lineHeight: 1 }}>
                {score2}
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
          <div style={{ flex: 1, padding: '15px', background: '#06060c', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', color: '#fff' }}>{time.toFixed(1)}s</div>
            <div style={{ fontSize: '0.75rem', color: '#888' }}>Time Played</div>
          </div>
          <div style={{ flex: 1, padding: '15px', background: '#06060c', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', color: '#fff' }}>{config.level}</div>
            <div style={{ fontSize: '0.75rem', color: '#888' }}>Level</div>
          </div>
          <div style={{ flex: 1, padding: '15px', background: '#06060c', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', color: life > 0 ? '#51cf66' : '#ff6b6b' }}>{life}</div>
            <div style={{ fontSize: '0.75rem', color: '#888' }}>Life Left</div>
          </div>
          <div style={{ flex: 1, padding: '15px', background: '#06060c', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', color: '#fff' }}>{config.difficulty?.toUpperCase()}</div>
            <div style={{ fontSize: '0.75rem', color: '#888' }}>Difficulty</div>
          </div>
        </div>

        {/* Leaderboard for this level */}
        {board.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '8px' }}>
              Top Scores — Level {config.level}
            </div>
            <div style={{ background: '#06060c', borderRadius: '8px', overflow: 'hidden' }}>
              {board.map((e, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between',
                  padding: '8px 14px',
                  borderBottom: i < board.length - 1 ? '1px solid #14141f' : 'none',
                  color: e.card_id === config.cardId ? '#c8b4fa' : '#ccc',
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
        <button onClick={onLogout} style={{ background: '#333', marginTop: '10px' }}>Logout</button>
      </div>
    </div>
  )
}
