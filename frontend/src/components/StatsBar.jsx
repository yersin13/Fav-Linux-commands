const HAT_DESC = { black: 'offensive', red: 'pentesting', blue: 'defensive', gray: 'utility' }

export default function StatsBar({ counts, total, progress, learned }) {
  return (
    <div className="stats-bar">
      {Object.entries(counts).map(([h, n]) => {
        const prog = progress?.[h]
        const pct = prog && prog.total > 0 ? Math.round((prog.done / prog.total) * 100) : 0
        return (
          <div key={h} className={`stat-pill hat-bg-${h}`}>
            <span className="stat-count">{n}</span>
            <span className="stat-label">{HAT_DESC[h]}</span>
            {prog && <div className="stat-progress-bar"><div className="stat-progress-fill" style={{ width: `${pct}%` }} /></div>}
          </div>
        )
      })}
      <div className="stat-pill stat-total">
        <span className="stat-count">{total}</span>
        <span className="stat-label">tools</span>
        {learned != null && <span className="stat-learned">{learned} learned</span>}
      </div>
    </div>
  )
}
