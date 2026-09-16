import { useMemo, useState } from 'react'

import VideoBackground from '../components/VideoBackground'
import {
  HOW_TO_BULLETS,
  QUICK_PLAY_LEVELS,
  TEAM_BATTLE_LEVELS,
} from '../levelPlaylists'

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
    sub: 'Co-op · 2 teams',
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

/**
 * Setup = Mode + Level on one screen (mock Screen 2 / our first screen).
 * Tournament: no level pick — playlist is fixed.
 */
export default function SetupScreen({ game = 'grid', onConfirm }) {
  const [mode, setMode] = useState('single')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const isTournament = mode === 'group'
  const isTeam = mode === 'multi'
  const ids = isTeam ? TEAM_BATTLE_LEVELS : QUICK_PLAY_LEVELS
  const modeMeta = MODES.find((m) => m.id === mode) || MODES[0]

  const bullets = useMemo(() => {
    if (mode === 'multi') return HOW_TO_BULLETS.multi
    if (mode === 'group') return HOW_TO_BULLETS.group
    return HOW_TO_BULLETS.single
  }, [mode])

  const selectedId = ids[selectedIndex] || ids[0]

  const handleReady = () => {
    if (isTournament) {
      onConfirm({
        game,
        playMode: 'group',
        playerCount: 1,
        level: 'auto',
        difficulty: 'normal',
      })
      return
    }
    if (!selectedId) return
    onConfirm({
      game,
      playMode: mode,
      playerCount: isTeam ? 2 : 1,
      level: selectedId,
      levelData: { id: selectedId, name: String(selectedIndex + 1) },
      difficulty: 'normal',
    })
  }

  return (
    <div className="screen screen-with-video">
      <VideoBackground />
      <div className="setup-layout">
        {/* Left — CHOOSE MODE */}
        <section className="setup-modes" aria-label="Choose mode">
          <p className="setup-col-label">Choose Mode</p>
          <div className="mode-list">
            {MODES.map((m) => {
              const selected = mode === m.id
              return (
                <button
                  key={m.id}
                  type="button"
                  className={`mode-btn ${m.className}${selected ? ' is-selected' : ''}`}
                  onClick={() => {
                    setMode(m.id)
                    setSelectedIndex(0)
                  }}
                >
                  {selected && m.id === 'single' && (
                    <span className="mode-selected-tag">Selected</span>
                  )}
                  {selected && m.id !== 'single' && (
                    <span className="mode-selected-tag">Selected</span>
                  )}
                  <span className="mode-badge" aria-hidden="true">{m.badge}</span>
                  <span className="mode-copy">
                    <span className="mode-title">{m.title}</span>
                    <span className="mode-sub">{m.sub}</span>
                  </span>
                </button>
              )
            })}
          </div>
        </section>

        {/* Right — SELECT LEVEL + HOW TO */}
        <section className="setup-panel" aria-label="Level and how to play">
          {!isTournament ? (
            <>
              <div className="setup-head">
                <p className="setup-kicker">Select Level</p>
                <p className="setup-mode-name">{ids.length} available</p>
              </div>
              <div className="level-grid" role="listbox" aria-label="Levels">
                {ids.map((id, i) => (
                  <button
                    key={id}
                    type="button"
                    role="option"
                    aria-selected={selectedIndex === i}
                    className={`level-chip ${selectedIndex === i ? 'is-selected' : ''}`}
                    onClick={() => setSelectedIndex(i)}
                    title={id}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div className="setup-head">
              <p className="setup-kicker">Tournament</p>
              <p className="setup-mode-name">Fixed level set · no pick</p>
            </div>
          )}

          <div className="howto">
            <p className="howto-title">How to play — {modeMeta.title}</p>
            <ul className="howto-list">
              {bullets.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        </section>

        <button type="button" className="btn-primary setup-ready" onClick={handleReady}>
          I&apos;m Ready
        </button>
      </div>
    </div>
  )
}
