const MODES = [
  {
    id: 'single',
    title: 'Single Player',
    desc: 'One player challenge',
    icon: '1',
  },
  {
    id: 'multi',
    title: 'Multiplayer',
    desc: 'Two players head-to-head',
    icon: '2',
  },
  {
    id: 'group',
    title: 'Group',
    desc: 'Team play mode',
    icon: 'G',
  },
]

export default function GameSelectionScreen({ onSelect, loading = false }) {
  return (
    <div className="screen">
      <div className="landing">
        <header className="landing-hero">
          <h1 className="landing-brand">ACTIVERSE</h1>
          <p className="landing-product">Floor Is Lava</p>
          <p className="landing-tagline">
            {loading ? 'Loading group level…' : 'Choose how you want to play'}
          </p>
        </header>

        <div className="mode-grid" aria-busy={loading || undefined}>
          {MODES.map((mode) => (
            <button
              key={mode.id}
              type="button"
              className="mode-card"
              disabled={loading}
              onClick={() => onSelect(mode.id)}
            >
              <span className="mode-card-icon" aria-hidden="true">{mode.icon}</span>
              <span className="mode-card-text">
                <span className="mode-card-title">{mode.title}</span>
                <span className="mode-card-desc">{mode.desc}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
