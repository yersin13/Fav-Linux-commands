const HATS = [
  { id: 'all',   label: 'All',       icon: '◈' },
  { id: 'black', label: 'Black Hat', icon: '▓' },
  { id: 'red',   label: 'Red Hat',   icon: '▒' },
  { id: 'blue',  label: 'Blue Hat',  icon: '░' },
  { id: 'gray',  label: 'Utility',   icon: '·' },
]

export default function HatFilter({ active, onChange, counts }) {
  return (
    <div className="hat-filter">
      <p className="filter-label">// filter by hat</p>
      {HATS.map(({ id, label, icon }) => (
        <button
          key={id}
          className={`hat-btn hat-btn-${id}${active === id ? ' active' : ''}`}
          onClick={() => onChange(id)}
        >
          <span className="hat-btn-icon">{icon}</span>
          <span className="hat-btn-label">{label}</span>
          {id !== 'all' && counts[id] != null && (
            <span className="hat-btn-count">{counts[id]}</span>
          )}
        </button>
      ))}

      <div className="hat-legend">
        <p className="filter-label" style={{ marginTop: '24px' }}>// legend</p>
        <p className="legend-item"><span className="hat-dot black" />offensive techniques</p>
        <p className="legend-item"><span className="hat-dot red" />recon &amp; pentesting</p>
        <p className="legend-item"><span className="hat-dot blue" />defense &amp; hardening</p>
        <p className="legend-item"><span className="hat-dot gray" />general utility</p>
      </div>
    </div>
  )
}
