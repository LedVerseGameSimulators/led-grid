import { useState } from 'react'
import { RFID_API_URL } from '../config'

function validationError(data) {
  if (data.reason === 'insufficient_time') {
    return `Not enough time (${data.minutes_remaining} min left). Need at least 5 min.`
  }
  if (data.reason === 'expired') return 'Session expired. Visit reception.'
  if (data.reason === 'no_active_session') return 'No active session. Visit reception.'
  return 'Card not recognized.'
}

async function validateRfidCard(cardId) {
  const res = await fetch(
    `${RFID_API_URL}/validate?card_id=${encodeURIComponent(cardId.trim())}`
  )
  return res.json()
}

function PlayerBadge({ info, label }) {
  if (!info?.valid) return null
  return (
    <div style={{ background: '#1a3a1a', padding: '10px', borderRadius: 8, marginTop: 8 }}>
      ✓ {label}: {info.player_name} — {info.minutes_remaining} min remaining
    </div>
  )
}

// Mode 1: guest names (anonymous). Mode 2: RFID scan → /validate per card.
export default function LoginScreen({ gameTitle = 'Game', onLogin, playerCount = 1, onBack }) {
  const [card1, setCard1] = useState('')
  const [card2, setCard2] = useState('')
  const [p1Info, setP1Info] = useState(null)
  const [p2Info, setP2Info] = useState(null)
  const [guestName1, setGuestName1] = useState('')
  const [guestName2, setGuestName2] = useState('')
  const [mode, setMode] = useState('rfid') // rfid | guest
  const [error, setError] = useState('')
  const [validating, setValidating] = useState(false)

  const runValidate = async (cardId, setInfo) => {
    if (!cardId.trim()) return null
    setValidating(true)
    setError('')
    try {
      const data = await validateRfidCard(cardId)
      setInfo(data.valid ? data : null)
      if (!data.valid) setError(validationError(data))
      return data
    } catch {
      setError('Could not reach RFID server.')
      return null
    } finally {
      setValidating(false)
    }
  }

  const handleCard1KeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      runValidate(card1, setP1Info)
    }
  }

  const handleCard2KeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      runValidate(card2, setP2Info)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (mode === 'guest') {
      if (!guestName1.trim()) { setError('Enter Player 1 name'); return }
      if (playerCount === 2 && !guestName2.trim()) { setError('Enter Player 2 name'); return }
      onLogin('', playerCount === 2 ? '' : null, guestName1.trim(), guestName2.trim(), null, null)
      return
    }

    if (!card1.trim()) { setError('Scan Player 1 card'); return }
    if (playerCount === 2 && !card2.trim()) { setError('Scan Player 2 card'); return }
    if (playerCount === 2 && card1.trim() === card2.trim()) {
      setError('Each player needs a different card')
      return
    }

    setValidating(true)
    try {
      const d1 = p1Info?.valid ? p1Info : await validateRfidCard(card1)
      if (!d1.valid) {
        setP1Info(null)
        setError(`Player 1: ${validationError(d1)}`)
        return
      }
      setP1Info(d1)

      let d2 = null
      if (playerCount === 2) {
        d2 = p2Info?.valid ? p2Info : await validateRfidCard(card2)
        if (!d2.valid) {
          setP2Info(null)
          setError(`Player 2: ${validationError(d2)}`)
          return
        }
        setP2Info(d2)
      }

      onLogin(
        card1.trim(),
        playerCount === 2 ? card2.trim() : null,
        d1.player_name || '',
        d2?.player_name || '',
        d1.minutes_remaining ?? null,
        d2?.minutes_remaining ?? null
      )
    } catch {
      setError('Could not reach RFID server.')
    } finally {
      setValidating(false)
    }
  }

  return (
    <div className="screen">
      <div className="card">
        <h1>{gameTitle}</h1>
        <p style={{ textAlign: 'center', color: '#888', marginTop: '-10px' }}>
          {playerCount === 2 ? '2-Player Login' : '1-Player Login'}
        </p>

        {mode === 'rfid' && (
          <form onSubmit={handleSubmit}>
            <div className="input-group" style={{ marginTop: '20px' }}>
              <label>Player 1 — Scan RFID Card</label>
              <input
                type="text"
                placeholder="Scan card + Enter"
                value={card1}
                onChange={e => { setCard1(e.target.value); setP1Info(null); setError('') }}
                onKeyDown={handleCard1KeyDown}
                autoFocus
              />
            </div>
            <PlayerBadge info={p1Info} label="P1" />

            {playerCount === 2 && (
              <>
                <div className="input-group" style={{ marginTop: '14px' }}>
                  <label>Player 2 — Scan RFID Card</label>
                  <input
                    type="text"
                    placeholder="Scan card + Enter"
                    value={card2}
                    onChange={e => { setCard2(e.target.value); setP2Info(null); setError('') }}
                    onKeyDown={handleCard2KeyDown}
                  />
                </div>
                <PlayerBadge info={p2Info} label="P2" />
              </>
            )}

            {validating && <p style={{ color: '#888', fontSize: '0.85rem', marginTop: 8 }}>Validating…</p>}
            {error && <div className="error">{error}</div>}
            <button type="submit" style={{ marginTop: '20px' }} disabled={validating}>
              Start Game
            </button>
            <button type="button" onClick={() => { setMode('guest'); setError('') }}
                    style={{ background: '#333', marginTop: '10px', width: '100%' }}>
              Skip — Play as Guest
            </button>
            {onBack && (
              <button type="button" onClick={onBack}
                      style={{ background: '#333', marginTop: '10px', width: '100%' }}>
                Back
              </button>
            )}
          </form>
        )}

        {mode === 'guest' && (
          <form onSubmit={handleSubmit}>
            <div className="input-group" style={{ marginTop: '20px' }}>
              <label>Player 1 — Name (anonymous)</label>
              <input
                type="text"
                placeholder="Enter name"
                value={guestName1}
                onChange={e => { setGuestName1(e.target.value); setError('') }}
                autoFocus
              />
            </div>
            {playerCount === 2 && (
              <div className="input-group" style={{ marginTop: '14px' }}>
                <label>Player 2 — Name (anonymous)</label>
                <input
                  type="text"
                  placeholder="Enter name"
                  value={guestName2}
                  onChange={e => { setGuestName2(e.target.value); setError('') }}
                />
              </div>
            )}
            {error && <div className="error">{error}</div>}
            <button type="submit" style={{ marginTop: '20px' }}>Start as Guest</button>
            <button type="button" onClick={() => { setMode('rfid'); setError('') }}
                    style={{ background: '#333', marginTop: '10px', width: '100%' }}>
              Back to RFID Scan
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
