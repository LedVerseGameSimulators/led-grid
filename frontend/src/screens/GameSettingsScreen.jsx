import { useState, useEffect } from 'react'

import { API_URL } from '../config'

const CAT_LABEL = {
  'easy':    { label: 'Easy',     desc: '001-010 (1P)' },
  'medium':  { label: 'Medium',   desc: '11 levels (1P)' },
  'hard':    { label: 'Hard',     desc: '001-014 HARD (1P)' },
  '2player': { label: '2-Player', desc: '01-13 (2P)' },
}

const DIFFICULTIES = ['easy', 'normal', 'hard']

export default function GameSettingsScreen({ game, onConfirm, onBack }) {
  const [categories, setCategories] = useState({})
  const [playerCount, setPlayerCount] = useState(1)
  const [category, setCategory]       = useState('easy')
  const [level, setLevel]             = useState('')
  const [difficulty, setDifficulty]   = useState('normal')
  const [loading, setLoading]         = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/levels`)
      .then(r => r.json())
      .then(d => {
        if (d.success) {
          setCategories(d.categories || {})
          // default: a-series → first level
          const first = (d.categories?.['easy'] || [])[0]
          if (first) setLevel(first.id)
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  // When category changes, reset level to first in new category
  const handleCategory = (cat) => {
    setCategory(cat)
    const lvls = filteredLevels(cat)
    if (lvls.length) setLevel(lvls[0].id)
  }

  // When player count changes, switch to dk-series (2P) or a-series (1P)
  const handlePlayerCount = (n) => {
    setPlayerCount(n)
    const defaultCat = n === 2 ? '2player' : 'easy'
    setCategory(defaultCat)
    const lvls = filteredLevels(defaultCat, n)
    if (lvls.length) setLevel(lvls[0].id)
  }

  const filteredLevels = (cat = category, players = playerCount) => {
    const all = categories[cat] || []
    if (players === 2) return all.filter(l => l.multiplayer)
    return all.filter(l => !l.multiplayer)
  }

  const availableCats = Object.keys(categories).filter(cat => {
    const lvls = categories[cat] || []
    return playerCount === 2
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
      playerCount,
      difficulty,
    })
  }

  if (loading) return (
    <div className="screen">
      <div className="card"><p style={{ textAlign: 'center', color: '#888' }}>Loading levels…</p></div>
    </div>
  )

  return (
    <div className="screen">
      <div className="card">
        <h1>⛰️ Climb</h1>
        <p style={{ color: '#888', textAlign: 'center', marginTop: '-10px' }}>
          Game Settings
        </p>

        {/* Players */}
        <h2 style={{ fontSize: '0.9rem', color: '#aaa', marginTop: '20px' }}>PLAYERS</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          {[1, 2].map(n => (
            <button
              key={n}
              className={`option-btn ${playerCount === n ? 'selected' : ''}`}
              style={{ flex: 1 }}
              onClick={() => handlePlayerCount(n)}
            >
              {n === 1 ? '1 Player' : '2 Players'}
            </button>
          ))}
        </div>

        {/* Category */}
        <h2 style={{ fontSize: '0.9rem', color: '#aaa', marginTop: '20px' }}>CATEGORY</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          {availableCats.map(cat => (
            <button
              key={cat}
              className={`option-btn ${category === cat ? 'selected' : ''}`}
              style={{ padding: '10px 8px' }}
              onClick={() => handleCategory(cat)}
            >
              <div style={{ fontWeight: 'bold' }}>{CAT_LABEL[cat]?.label || cat}</div>
              <div style={{ fontSize: '0.7rem', color: '#888', marginTop: '3px' }}>
                {CAT_LABEL[cat]?.desc}
              </div>
            </button>
          ))}
        </div>

        {/* Level */}
        <h2 style={{ fontSize: '0.9rem', color: '#aaa', marginTop: '20px' }}>
          LEVEL <span style={{ color: '#555' }}>({levelList.length} available)</span>
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '6px',
          maxHeight: '180px',
          overflowY: 'auto',
        }}>
          {levelList.map(lv => (
            <button
              key={lv.id}
              className={`option-btn ${level === lv.id ? 'selected' : ''}`}
              style={{ padding: '8px 4px', fontSize: '0.8rem' }}
              onClick={() => setLevel(lv.id)}
            >
              {lv.name}
            </button>
          ))}
        </div>

        {/* Difficulty */}
        <h2 style={{ fontSize: '0.9rem', color: '#aaa', marginTop: '20px' }}>DIFFICULTY</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          {DIFFICULTIES.map(d => (
            <button
              key={d}
              className={`option-btn ${difficulty === d ? 'selected' : ''}`}
              style={{ flex: 1 }}
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
        <button onClick={onBack} style={{ background: '#333', marginTop: '10px' }}>
          Back
        </button>
      </div>
    </div>
  )
}
