import { RFID_API_URL } from './config'

/** Best-effort /validate (used at login and again at save). */
export async function validateRfidCard(cardId, timeoutMs = 2000) {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const res = await fetch(
      `${RFID_API_URL}/validate?card_id=${encodeURIComponent(cardId)}`,
      { signal: ctrl.signal }
    )
    return await res.json()
  } finally {
    clearTimeout(timer)
  }
}

export function playModeToRfidPlayMode(playMode) {
  if (playMode === 'multi') return 'team_battle'
  if (playMode === 'group') return 'tournament'
  return 'quick_play'
}

/** Map RFID /validate payload → save-score stamp fields (nulls when invalid). */
export function stampFieldsFromValidate(data) {
  if (!data || data.valid !== true) {
    return {
      session_id: null,
      group_id: null,
      roster_size_at_play: null,
      roster_player_ids: null,
    }
  }
  let rosterIds = data.roster_player_ids
  if (!Array.isArray(rosterIds) && Array.isArray(data.members)) {
    rosterIds = data.members
      .map((m) => (typeof m === 'object' && m != null ? (m.id ?? m.player_id) : null))
      .filter((id) => id != null)
  }
  const rosterSize =
    data.roster_size != null
      ? data.roster_size
      : Array.isArray(rosterIds)
        ? rosterIds.length
        : Array.isArray(data.members)
          ? data.members.length
          : null
  return {
    session_id: data.session_id ?? null,
    group_id: data.group_id ?? null,
    roster_size_at_play: rosterSize,
    roster_player_ids: Array.isArray(rosterIds) ? rosterIds : null,
  }
}

/** Re-validate at save; fall back to login-time payload; never throws. */
export async function resolveStampAtSave(cardId, loginValidate) {
  if (!cardId || !String(cardId).trim()) {
    return stampFieldsFromValidate(null)
  }
  let fresh = null
  try {
    fresh = await validateRfidCard(String(cardId).trim(), 2000)
  } catch {
    /* use loginValidate */
  }
  return stampFieldsFromValidate(fresh?.valid === true ? fresh : loginValidate)
}
