import { useState, useEffect } from 'react'

import { API_URL } from '../config'

const CAT_LABEL = {
  easy:     { label: 'Easy',     desc: '001-010 (1P)' },
  medium:   { label: 'Medium',   desc: '1P' },
  hard:     { label: 'Hard',     desc: '1P' },
  '2player': { label: '2-Player', desc: '2P' },
}

const DIFFICULTIES = ['easy', 'normal', 'hard']


function firstMatchingCategory(cats, players) {
  const keys = Object.keys(cats || {})
  for (const cat of keys) {
    const lvls = cats[cat] || []
    const ok = players === 2
      ? lvls.some(l => l.multiplayer)
      : lvls.some(l => !l.multiplayer)
    if (ok) return cat
  }
  return keys[0] || ''
}

function firstMatchingLevel(pool, players) {
  if (!pool?.length) return null
  if (players === 2) return pool.find(l => l.multiplayer) || pool[0]
  return pool.find(l => !l.multiplayer) || pool[0]
}

export default function GameSettingsScreen({ game, playerCount, onConfirm, onBack }) {
  const players = playerCount ?? 1
  const [categories, setCategories] = useState({})
  const [category, setCategory]     = useState(players === 2 ? '2player' : 'easy')
  const [level, setLevel]           = useState('')
  const [difficulty, setDifficulty] = useState('normal')
  const [loading, setLoading]       = useState(true)
  const [loadError, setLoadError]   = useState('')

  useEffect(() => {
    const preferred = players === 2 ? '2player' : 'easy'
    setLoading(true)
    setLoadError('')
    fetch(`${API_URL}/levels`)
      .then(r => {
        if (!r.ok) throw new Error(`Levels API HTTP ${r.status}`)
        return r.json()
      })
      .then(d => {
        if (!d.success) throw new Error(d.error || 'Levels API returned success=false')
        const cats = d.categories || {}
        setCategories(cats)
        const defaultCat = (cats[preferred] && (
          players === 2
            ? (cats[preferred] || []).some(l => l.multiplayer)
            : (cats[preferred] || []).some(l => !l.multiplayer)
        )) ? preferred : firstMatchingCategory(cats, players)
        setCategory(defaultCat || preferred)
        const pool = cats[defaultCat] || []
        const first = firstMatchingLevel(pool, players)
        if (first) setLevel(first.id)
        else setLevel('001')
        if (!defaultCat) {
          setLoadError(players === 2
            ? 'No multiplayer levels available for this game.'
            : 'No single-player levels found.')
        }
      })
      .catch(err => {
        console.error(err)
        setLoadError(`Could not load levels from ${API_URL}/levels — is the game API running?`)
        setCategories({})
      })
      .finally(() => setLoading(false))
  }, [players])

  const filteredLevels = (cat = category) => {
    const all = categories[cat] || []
    if (players === 2) return all.filter(l => l.multiplayer)
    return all.filter(l => !l.multiplayer)
  }

  const handleCategory = (cat) => {
    setCategory(cat)
    const lvls = filteredLevels(cat)
    const first = firstMatchingLevel(lvls, players)
    if (first) setLevel(first.id)
  }

  const availableCats = Object.keys(categories).filter(cat => {
    const lvls = categories[cat] || []
    return players === 2
      ? lvls.some(l => l.multiplayer)
      : lvls.some(l => !l.multiplayer)
  })

  const levelList = filteredLevels()
  const selectedLevel = levelList.find(l => l.id === level) || levelList[0]

  const handleConfirm = () => {
    if (!selectedLevel) return
    onConfirm({
      game,
      level: selectedLevel.id,
      levelData: selectedLevel,
      playerCount: players,
      difficulty,
    })
  }

  if (loading) return (
    <div className="screen">
      <div className="card settings-card">
        <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading levels…</p>
      </div>
    </div>
  )

  return (
    <div className="screen">
      <div className="card settings-card">
        <h1>Floor Is Lava</h1>
        <p className="settings-subtitle">
          Game Settings · {players === 2 ? '2 Players' : '1 Player'}
        </p>

        {loadError && (
          <div className="error" style={{ marginTop: 16 }}>{loadError}</div>
        )}

        {/* Category rail */}
        <h2 className="settings-section-label">CATEGORY</h2>
        <div className="cat-rail" role="listbox" aria-label="Categories">
          {availableCats.map(cat => (
            <button
              key={cat}
              type="button"
              role="option"
              aria-selected={category === cat}
              className={`cat-chip ${category === cat ? 'selected' : ''}`}
              onClick={() => handleCategory(cat)}
            >
              <span className="cat-chip-label">{CAT_LABEL[cat]?.label || cat}</span>
              <span className="cat-chip-desc">{CAT_LABEL[cat]?.desc}</span>
            </button>
          ))}
        </div>

        {/* Level rail */}
        <h2 className="settings-section-label">
          LEVEL <span className="settings-count">({levelList.length} available)</span>
        </h2>
        <div className="level-rail" role="listbox" aria-label="Levels">
          {levelList.map(lv => (
            <button
              key={lv.id}
              type="button"
              role="option"
              aria-selected={level === lv.id}
              className={`level-chip ${level === lv.id ? 'selected' : ''}`}
              onClick={() => setLevel(lv.id)}
            >
              {lv.name}
            </button>
          ))}
          {levelList.length === 0 && (
            <p className="rail-empty">No levels for this mode</p>
          )}
        </div>

        {/* Difficulty */}
        <h2 className="settings-section-label">DIFFICULTY</h2>
        <div className="diff-row">
          {DIFFICULTIES.map(d => (
            <button
              key={d}
              type="button"
              className={`option-btn ${difficulty === d ? 'selected' : ''}`}
              style={{ flex: 1, margin: 0 }}
              onClick={() => setDifficulty(d)}
            >
              {d.charAt(0).toUpperCase() + d.slice(1)}
            </button>
          ))}
        </div>

        <button onClick={handleConfirm} style={{ marginTop: '24px' }}
                disabled={!selectedLevel}>
          Next → Login
        </button>
        <button onClick={onBack} className="btn-secondary" style={{ marginTop: '10px' }}>
          Back
        </button>
      </div>
    </div>
  )
}
