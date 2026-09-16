import VideoBackground from '../components/VideoBackground'

const MODES = [
  {
    id: 'single',
    title: 'Quick Play',
    sub: 'Solo · Basic',
    badge: '1',
    className: 'mode-btn-single',
  },
  {
    id: 'multi',
    title: 'Team Battle',
    sub: 'Co-op · 2 players',
    badge: '2',
    className: 'mode-btn-multi',
  },
  {
    id: 'group',
    title: 'Tournament',
    sub: 'Co-op · Bracket',
    badge: 'T',
    className: 'mode-btn-group',
  },
]

export default function GameSelectionScreen({ onSelect, loading = false }) {
  return (
    <div className="screen screen-with-video">
      <VideoBackground />
      <div className="mode-shell">
        <p className="mode-shell-title">Choose Mode</p>
        <div className="mode-list" aria-busy={loading || undefined}>
          {MODES.map((mode) => (
            <button
              key={mode.id}
              type="button"
              className={`mode-btn ${mode.className}`}
              disabled={loading}
              onClick={() => onSelect(mode.id)}
            >
              <span className="mode-badge" aria-hidden="true">{mode.badge}</span>
              <span className="mode-copy">
                <span className="mode-title">{mode.title}</span>
                <span className="mode-sub">{mode.sub}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
