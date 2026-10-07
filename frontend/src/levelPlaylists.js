/**
 * Mode playlist helpers for Grid. Ordered lists come from GET /playlists at runtime.
 */

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

/** @param {object|null} playlists from GET /playlists */
export function playlistForMode(playMode, playlists) {
  if (!playlists) return []
  if (playMode === 'multi') return playlists.multi || []
  if (playMode === 'group') return playlists.group || []
  return playlists.single || []
}

export function playlistEntryId(entry) {
  if (!entry) return ''
  if (typeof entry === 'string') return entry
  return String(entry.id ?? '')
}

export function tournamentFirstId(playlists) {
  const list = playlistForMode('group', playlists)
  return list.length ? playlistEntryId(list[0]) : null
}

/** Map backend level stem → UI number (1-based) within the full mode playlist. */
export function displayLevelNumber(playMode, levelId, playlists) {
  const stem = String(levelId ?? '')
    .replace(/\.(led|ledb)$/i, '')
    .trim()
  if (!stem || stem === 'auto') return null
  const list = playlistForMode(playMode, playlists)
  const idx = list.findIndex((entry) => playlistEntryId(entry) === stem)
  if (idx >= 0) return idx + 1
  return null
}

export function formatLevelLabel(playMode, levelId, playlists) {
  const n = displayLevelNumber(playMode, levelId, playlists)
  if (n != null) return String(n)
  return String(levelId ?? '—')
}
