/** Client-side play/RFID context for reload resume (Step 0 Round 2). */
const STORAGE_PREFIX = 'grid_game_resume_'

export function persistGameResumeContext(gameId, config) {
  if (!gameId || typeof sessionStorage === 'undefined') return
  const payload = {
    game_id: gameId,
    playMode: config.playMode,
    playerCount: config.playerCount,
    cardId: config.cardId,
    cardId2: config.cardId2,
    rfidValidate1: config.rfidValidate1,
    rfidValidate2: config.rfidValidate2,
    playerName: config.playerName,
    playerName2: config.playerName2,
    minutesRemaining: config.minutesRemaining,
    minutesRemaining2: config.minutesRemaining2,
  }
  try {
    sessionStorage.setItem(STORAGE_PREFIX + gameId, JSON.stringify(payload))
  } catch {
    /* quota / private mode */
  }
}

export function loadGameResumeContext(gameId) {
  if (!gameId || typeof sessionStorage === 'undefined') return null
  try {
    const raw = sessionStorage.getItem(STORAGE_PREFIX + gameId)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (data?.game_id !== gameId) return null
    return data
  } catch {
    return null
  }
}

export function clearGameResumeContext(gameId) {
  if (!gameId || typeof sessionStorage === 'undefined') return
  try {
    sessionStorage.removeItem(STORAGE_PREFIX + gameId)
  } catch {
    /* ignore */
  }
}
