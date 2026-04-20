const HAT_LABELS = { black: 'Black Hat', red: 'Red Hat', blue: 'Blue Hat', gray: 'Gray' }
const HAT_DESC  = { black: 'offensive', red: 'pentesting', blue: 'defensive', gray: 'utility' }

export default function StatsBar({ counts, total }) {
  return (
    <div className="stats-bar">
      {Object.entries(counts).map(([h, n]) => (
        <div key={h} className={`stat-pill hat-bg-${h}`}>
          <span className="stat-count">{n}</span>
          <span className="stat-label">{HAT_DESC[h]}</span>
        </div>
      ))}
      <div className="stat-pill stat-total">
        <span className="stat-count">{total}</span>
        <span className="stat-label">total</span>
      </div>
    </div>
  )
}
