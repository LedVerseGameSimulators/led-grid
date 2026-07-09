import { useState } from 'react'

export default function SettingsScreen({ onSubmit, onBack }) {
  const [difficulty, setDifficulty] = useState('normal')

  const DIFFICULTIES = [
    { id: 'easy', label: 'Easy', color: '#51cf66' },
    { id: 'normal', label: 'Normal', color: '#6c3ef5' },
    { id: 'hard', label: 'Hard', color: '#ff6b6b' }
  ]

  return (
    <div className="screen">
      <div className="card">
        <h1>Game Difficulty</h1>

        <div className="input-group">
          <label>Difficulty</label>
          <div className="grid">
            {DIFFICULTIES.map(diff => (
              <button
                key={diff.id}
                className={`option-btn ${difficulty === diff.id ? 'selected' : ''}`}
                onClick={() => setDifficulty(diff.id)}
              >
                {diff.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginTop: '30px', padding: '15px', background: '#06060c', borderRadius: '6px' }}>
          <p style={{ fontSize: '0.85rem', color: '#888', marginBottom: '8px' }}>Summary:</p>
          <p style={{ color: '#c8b4fa' }}>
            <strong>{difficulty.toUpperCase()}</strong> difficulty
          </p>
        </div>

        <button onClick={() => onSubmit(difficulty)}>Start Game</button>
        <button style={{ background: '#333', marginTop: '10px' }} onClick={onBack}>Back</button>
      </div>
    </div>
  )
}
