import { useState, useRef, useEffect } from 'react'

import VideoBackground from '../components/VideoBackground'
import { randomGuestNames } from '../guestNames'
import { validateRfidCard } from '../rfidPlayFacts'

function normalizeCardId(raw) {
  return String(raw ?? '').replace(/[\r\n]/g, '').trim()
}

function canonicalCardId(scanned, validateData) {
  const fromApi =
    validateData?.card_id != null ? normalizeCardId(validateData.card_id) : ''
  return fromApi || normalizeCardId(scanned)
}

function cardsEqualCaseInsensitive(a, b) {
  const na = normalizeCardId(a).toLowerCase()
  const nb = normalizeCardId(b).toLowerCase()
  return Boolean(na && nb && na === nb)
}

function teamBattleSameGroup(p1Validate, p2Validate) {
  const g1 = p1Validate?.group_id
  const g2 = p2Validate?.group_id
  if (g1 == null || g2 == null) return false
  return g1 === g2
}

function validationError(data) {
  if (data.reason === 'insufficient_time') {
    return `Not enough time (${data.minutes_remaining} min left). Need at least 5 min.`
  }
  if (data.reason === 'expired') return 'Session expired. Visit reception.'
  if (data.reason === 'no_active_session') return 'No active session. Visit reception.'
  return 'Card not recognized.'
}

export default function LoginScreen({ gameTitle = 'Mega Grid', onLogin, playerCount = 1, onBack }) {
  const [card1, setCard1] = useState('')
  const [card2, setCard2] = useState('')
  const [p1Info, setP1Info] = useState(null)
  const [p2Info, setP2Info] = useState(null)
  const [validatedCard1, setValidatedCard1] = useState('')
  const [validatedCard2, setValidatedCard2] = useState('')
  const [error, setError] = useState('')
  const [validating, setValidating] = useState(false)
  const [activeScan, setActiveScan] = useState(1)

  const card1Ref = useRef(null)
  const card2Ref = useRef(null)

  const p1Valid = Boolean(p1Info?.valid)
  const p2Valid = Boolean(p2Info?.valid)
  const canStart = p1Valid && (playerCount === 1 || p2Valid)

  const displayName = p1Info?.player_name
    || (Array.isArray(p1Info?.members) && p1Info.members[0]
      ? (typeof p1Info.members[0] === 'string' ? p1Info.members[0] : p1Info.members[0]?.name)
      : '')
  const displayName2 = p2Info?.player_name || ''

  useEffect(() => {
    if (!p1Valid) {
      setActiveScan(1)
      card1Ref.current?.focus()
      return
    }
    if (playerCount === 2 && !p2Valid) {
      setActiveScan(2)
      card2Ref.current?.focus()
    }
  }, [p1Valid, p2Valid, playerCount])

  const runValidate = async (which, rawOverride) => {
    const inputEl = which === 1 ? card1Ref.current : card2Ref.current
    const fallback = which === 1 ? card1 : card2
    const cardId = normalizeCardId(
      rawOverride !== undefined ? rawOverride : (inputEl?.value ?? fallback)
    )

    if (!cardId) {
      setError(which === 1 ? 'Scan Player 1 card' : 'Scan Player 2 card')
      return
    }

    if (which === 1) setCard1(cardId)
    else setCard2(cardId)

    if (playerCount === 2) {
      const otherRaw = which === 1
        ? (validatedCard2 || card2Ref.current?.value || card2)
        : (validatedCard1 || card1Ref.current?.value || card1)
      if (cardsEqualCaseInsensitive(cardId, otherRaw)) {
        setError('Each player needs a different card')
        if (which === 1) {
          setP1Info(null)
          setValidatedCard1('')
        } else {
          setP2Info(null)
          setValidatedCard2('')
        }
        return
      }
    }

    setValidating(true)
    setError('')
    let ok = false
    try {
      const data = await validateRfidCard(cardId)
      if (data.valid) {
        const canonical = canonicalCardId(cardId, data)
        if (which === 2 && playerCount === 2 && p1Info?.valid) {
          if (cardsEqualCaseInsensitive(canonical, validatedCard1 || p1Info.card_id)) {
            setP2Info(null)
            setValidatedCard2('')
            setError('Each player needs a different card')
            return
          }
          if (teamBattleSameGroup(p1Info, data)) {
            setP2Info(null)
            setValidatedCard2('')
            setError('Team Battle needs two different groups — scan the other team’s leader card')
            return
          }
        }
        ok = true
        if (which === 1) {
          setP1Info(data)
          setValidatedCard1(canonical)
          setCard1(canonical)
        } else {
          setP2Info(data)
          setValidatedCard2(canonical)
          setCard2(canonical)
        }
      } else {
        if (which === 1) {
          setP1Info(null)
          setValidatedCard1('')
        } else {
          setP2Info(null)
          setValidatedCard2('')
        }
        setError(validationError(data))
      }
    } catch {
      setError('Could not reach RFID server')
    } finally {
      setValidating(false)
      requestAnimationFrame(() => {
        if (which === 1 && ok && playerCount === 2) card2Ref.current?.focus()
        else if (which === 1) card1Ref.current?.focus()
        else card2Ref.current?.focus()
      })
    }
  }

  const handleCardKeyDown = (which) => (e) => {
    if (e.key !== 'Enter') return
    e.preventDefault()
    e.stopPropagation()
    runValidate(which, e.currentTarget.value)
  }

  const handleCardChange = (which) => (e) => {
    const value = e.target.value
    if (which === 1) {
      setCard1(value)
      setP1Info(null)
      setValidatedCard1('')
    } else {
      setCard2(value)
      setP2Info(null)
      setValidatedCard2('')
    }
    setError('')
  }

  const handleStartGame = () => {
    if (!canStart || validating) return
    if (playerCount === 2 && cardsEqualCaseInsensitive(validatedCard1, validatedCard2)) {
      setError('Each player needs a different card')
      return
    }
    if (playerCount === 2 && teamBattleSameGroup(p1Info, p2Info)) {
      setError('Team Battle needs two different groups — scan the other team’s leader card')
      return
    }
    onLogin(
      validatedCard1,
      playerCount === 2 ? validatedCard2 : null,
      p1Info.player_name || '',
      p2Info?.player_name || '',
      p1Info.minutes_remaining ?? null,
      p2Info?.minutes_remaining ?? null,
      p1Info,
      playerCount === 2 ? p2Info : null
    )
  }

  const handleScanAgain = () => {
    setCard1('')
    setCard2('')
    setP1Info(null)
    setP2Info(null)
    setValidatedCard1('')
    setValidatedCard2('')
    setError('')
    setActiveScan(1)
    requestAnimationFrame(() => card1Ref.current?.focus())
  }

  const handlePlayWithoutRfid = () => {
    const { playerName, playerName2 } = randomGuestNames(playerCount)
    onLogin('', playerCount === 2 ? '' : null, playerName, playerName2, null, null)
  }

  const statusReady = canStart
  const welcome = !p1Valid
    ? (playerCount === 2 ? 'Scan Player 1 card to continue' : 'Scan your card to continue')
    : playerCount === 2 && !p2Valid
      ? `Welcome, ${displayName || 'Player 1'} — scan Player 2`
      : playerCount === 2
        ? `Welcome, ${displayName || 'Player 1'} & ${displayName2 || 'Player 2'}`
        : `Welcome back, ${displayName || 'Player'}`

  return (
    <div className="screen screen-with-video">
      <VideoBackground />
      {onBack && (
        <button type="button" className="btn-back" onClick={onBack}>
          Back
        </button>
      )}

      <div className="login-card">
        <div className={`login-status-row${statusReady ? '' : ' idle'}`}>
          <span className={`login-status-dot${statusReady ? '' : ' idle'}`} />
          {statusReady ? 'Card scanned — Ready' : validating ? 'Validating…' : 'Waiting for card'}
        </div>

        <p className="login-welcome">
          {gameTitle}
          <br />
          <strong>{welcome}</strong>
        </p>

        {/* Hidden wedge fields — RFID scanners type into focused input */}
        <input
          ref={card1Ref}
          className="login-scan-input"
          type="text"
          value={card1}
          onChange={handleCardChange(1)}
          onKeyDown={handleCardKeyDown(1)}
          onFocus={() => setActiveScan(1)}
          autoFocus
          autoComplete="off"
          spellCheck={false}
          aria-label="Player 1 RFID"
        />
        {playerCount === 2 && (
          <input
            ref={card2Ref}
            className="login-scan-input"
            type="text"
            value={card2}
            onChange={handleCardChange(2)}
            onKeyDown={handleCardKeyDown(2)}
            onFocus={() => setActiveScan(2)}
            autoComplete="off"
            spellCheck={false}
            aria-label="Player 2 RFID"
          />
        )}

        {!statusReady && (
          <p className="login-waiting">
            {activeScan === 2 ? 'Ready to scan Player 2' : 'Ready to scan'}
          </p>
        )}

        {error && <p className="login-error">{error}</p>}

        <button
          type="button"
          className="btn-primary"
          disabled={!canStart || validating}
          onClick={handleStartGame}
        >
          Tap to Play
        </button>

        <div className="login-footer-links">
          <button type="button" onClick={handleScanAgain}>Not you? Scan again</button>
          <span aria-hidden="true">·</span>
          <button type="button" onClick={handlePlayWithoutRfid}>Skip as Guest</button>
        </div>
      </div>
    </div>
  )
}
