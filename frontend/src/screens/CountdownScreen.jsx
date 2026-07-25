import { useEffect, useState, useRef } from 'react'

// Pre-game 3-2-1-GO countdown (mirrors the real game's countdown video).
export default function CountdownScreen({ config, onDone }) {
  const [n, setN] = useState(3)
  const audioCtxRef = useRef(null)

  const beep = (freq, dur = 150) => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      }
      const ctx = audioCtxRef.current
      const osc = ctx.createOscillator()
      const g = ctx.createGain()
      osc.frequency.value = freq
      g.gain.value = 0.18
      osc.connect(g); g.connect(ctx.destination)
      osc.start()
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur / 1000)
      osc.stop(ctx.currentTime + dur / 1000)
    } catch (e) { /* no audio */ }
  }

  useEffect(() => {
    beep(523, 180)
    const id = setInterval(() => {
      setN(prev => {
        const next = prev - 1
        if (next <= 0) {
          clearInterval(id)
          beep(880, 350)              // GO!
          setTimeout(onDone, 600)
          return 0
        }
        beep(523, 180)
        return next
      })
    }, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="screen">
      <div className="card" style={{ textAlign: 'center' }}>
        <p className="countdown-meta">
          {config.game?.toUpperCase()} · Level {config.level} · {config.difficulty?.toUpperCase()}
        </p>
        <div className={`countdown-num${n === 0 ? ' go' : ''}`}>
          {n === 0 ? 'GO!' : n}
        </div>
        <p className="countdown-hint">Get ready…</p>
      </div>
    </div>
  )
}
