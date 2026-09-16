/** Full-bleed looping background video for kiosk screens. */
export default function VideoBackground({
  src = '/media/background.mp4',
  poster = '/media/background.jpg',
}) {
  return (
    <div className="video-bg" aria-hidden="true">
      <video
        className="video-bg-el"
        autoPlay
        muted
        loop
        playsInline
        poster={poster}
        src={src}
      />
      <div className="video-bg-dim" />
    </div>
  )
}
