const ADJECTIVES = [
  'Swift', 'Bright', 'Neon', 'Pulse', 'Nova', 'Echo', 'Blitz', 'Apex',
  'Orbit', 'Spark', 'Frost', 'Solar', 'Pixel', 'Turbo', 'Vortex',
]

const NOUNS = [
  'Fox', 'Hawk', 'Wolf', 'Lynx', 'Bolt', 'Wave', 'Core', 'Hex',
  'Grid', 'Arc', 'Dash', 'Beam', 'Spark', 'Rune', 'Knight',
]

function pick(list) {
  return list[Math.floor(Math.random() * list.length)]
}

/** Random guest display name for no-RFID play (no typing). */
export function randomGuestName(playerIndex = 1) {
  const n = Math.floor(100 + Math.random() * 900)
  return `${pick(ADJECTIVES)}${pick(NOUNS)}${n}`
}

export function randomGuestNames(playerCount = 1) {
  const p1 = randomGuestName(1)
  if (playerCount < 2) return { playerName: p1, playerName2: '' }
  let p2 = randomGuestName(2)
  // Avoid identical pair in the rare collision
  if (p2 === p1) p2 = randomGuestName(2)
  return { playerName: p1, playerName2: p2 }
}
