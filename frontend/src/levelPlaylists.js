/**
 * Placeholder playlists for Grid (Floor Is Lava) FE redesign.
 * Real 20-level lists will replace these when the team delivers them.
 * Backend still receives real file ids (stems); UI may show 1..N.
 */

/**
 * Quick Play (1P) — prefer clean numeric stems from source/- + --.
 * Only ~13 unique clean ids exist; pad with ---- 01–07 as placeholders.
 */
export const QUICK_PLAY_LEVELS = [
  '001', '002', '003', '004', '005', '006', '007', '008', '009', '010',
  '011', '012', '013', '01', '02', '03', '04', '05', '06', '07',
]

/** Team Battle (2P) — ---- 01–12 + pad with remaining 08–12 / casual. */
export const TEAM_BATTLE_LEVELS = [
  '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
  '11', '12', '001', '002', '003', '004', '005', '006', '007', '008',
]

/**
 * Tournament playlist order (source_group/-- numeric stems).
 */
export const TOURNAMENT_LEVEL_ORDER = [
  '002', '003', '004', '005', '006', '007', '008', '009', '010', '011',
]

export const HOW_TO = {
  single:
    'Step on glowing tiles that match the goal colour. Avoid red hazards. Clear each wave to advance.',
  multi:
    'Each player scores their own colour. Watch the floor — red hurts both. Clear your targets to progress.',
  group:
    'A fixed set of levels runs in order. No level pick — just play through 1, 2, 3… as a group session.',
}

/** Bullet copy for Setup screen (mock-style how-to). */
export const HOW_TO_BULLETS = {
  single: [
    'Watch the goal colour on the HUD.',
    'Step on matching glowing floor tiles as fast as you can.',
    'Avoid lava / red hazards — clear each wave to advance.',
  ],
  multi: [
    'Each player scores their own colour on the floor.',
    'Red hurts both — stay sharp together.',
    'Clear your targets to progress through levels.',
  ],
  group: [
    'A fixed tournament set runs in order — no level pick.',
    'Play through levels 1, 2, 3… as a group session.',
    'Clear each stage to keep moving.',
  ],
}

export function playlistForMode(playMode) {
  if (playMode === 'multi') return TEAM_BATTLE_LEVELS
  if (playMode === 'group') return TOURNAMENT_LEVEL_ORDER
  return QUICK_PLAY_LEVELS
}

/** Map backend level stem → UI number (1-based) within the active playlist. */
export function displayLevelNumber(playMode, levelId) {
  const stem = String(levelId ?? '')
    .replace(/\.(led|ledb)$/i, '')
    .trim()
  if (!stem || stem === 'auto') return null
  const list = playlistForMode(playMode)
  const idx = list.findIndex(
    (id) => id === stem || stem.startsWith(id) || id.startsWith(stem)
  )
  if (idx >= 0) return idx + 1
  // Fallback: numeric stems display as themselves when in tournament-style lists
  if (/^\d+$/.test(stem)) return Number(stem)
  return null
}

export function formatLevelLabel(playMode, levelId) {
  const n = displayLevelNumber(playMode, levelId)
  if (n != null) return String(n)
  return String(levelId ?? '—')
}
