/** Full-bleed looping background video for kiosk screens. */
export default function VideoBackground({
  src = '/media/background.mp4',
  poster = '/media/background.jpg',
  title = 'Mega Grid',
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
      {title ? (
        <div className="video-bg-brand">
          <p className="video-bg-brand-title">{title}</p>
        </div>
      ) : null}
    </div>
  )
}
