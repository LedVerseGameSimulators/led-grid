const GAMES = [
  { id: 'grid', name: 'Floor Is Lava', emoji: '🌋' },
]

export default function GameSelectionScreen({ onSelect }) {
  return (
    <div className="screen">
      <div className="card">
        <h1>🌋 Floor Is Lava</h1>
        <p style={{ textAlign: 'center', color: '#888', marginTop: '-10px' }}>
          Select game to play
        </p>
        <div className="grid" style={{ gridTemplateColumns: '1fr', marginTop: '20px' }}>
          {GAMES.map(g => (
            <button
              key={g.id}
              type="button"
              className="option-btn"
              onClick={() => onSelect(g.id)}
            >
              <div style={{ fontSize: '2rem', marginBottom: '8px' }}>{g.emoji}</div>
              <div>{g.name}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
