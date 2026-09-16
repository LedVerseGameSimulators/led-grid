import { useMemo, useState } from 'react'

import VideoBackground from '../components/VideoBackground'
import {
  HOW_TO_BULLETS,
  QUICK_PLAY_LEVELS,
  TEAM_BATTLE_LEVELS,
} from '../levelPlaylists'

export default function GameSettingsScreen({
  game,
  playerCount,
  playMode = 'single',
  onConfirm,
  onBack,
}) {
  const players = playerCount ?? 1
  const ids = players === 2 ? TEAM_BATTLE_LEVELS : QUICK_PLAY_LEVELS
  const [selectedIndex, setSelectedIndex] = useState(0)
  const modeName = players === 2 ? 'Team Battle' : 'Quick Play'

  const bullets = useMemo(
    () => (players === 2 ? HOW_TO_BULLETS.multi : HOW_TO_BULLETS.single),
    [players]
  )

  const selectedId = ids[selectedIndex] || ids[0]

  const handleConfirm = () => {
    if (!selectedId) return
    onConfirm({
      game,
      level: selectedId,
      levelData: { id: selectedId, name: String(selectedIndex + 1) },
      playerCount: players,
      difficulty: 'normal',
      playMode,
    })
  }

  return (
    <div className="screen screen-with-video">
      <VideoBackground />
      {onBack && (
        <button type="button" className="btn-back" onClick={onBack}>
          Back
        </button>
      )}
      <div className="setup-shell">
        <div className="setup-head">
          <p className="setup-kicker">Select Level</p>
          <p className="setup-mode-name">{modeName} · {ids.length} available</p>
        </div>

        <div>
          <p className="setup-label">Levels</p>
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
        </div>

        <div className="howto">
          <p className="howto-title">How to play — {modeName}</p>
          <ul className="howto-list">
            {bullets.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>

        <button type="button" className="btn-primary" onClick={handleConfirm}>
          I&apos;m Ready
        </button>
      </div>
    </div>
  )
}
