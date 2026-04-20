import { useState } from 'react'
import { GLOSSARY, CATEGORIES } from '../data/glossary'

function GlossaryCard({ entry, onCommandClick, allVideos }) {
  const [expanded, setExpanded] = useState(false)

  const linkedCommands = (entry.related_commands || [])
    .map((cmd) => allVideos.find((v) => v.command.toLowerCase() === cmd.toLowerCase()))
    .filter(Boolean)

  return (
    <div className={`gl-card${expanded ? ' open' : ''}`} onClick={() => setExpanded((e) => !e)}>
      <div className="gl-card-header">
        <div className="gl-term-row">
          <span className="gl-term">{entry.term}</span>
          <span className={`gl-cat-pill gl-cat-${entry.category}`}>{entry.category}</span>
        </div>
        <p className="gl-short">{entry.short}</p>
        <span className="gl-caret">{expanded ? '▾' : '▸'}</span>
      </div>

      {expanded && (
        <div className="gl-body" onClick={(e) => e.stopPropagation()}>
          <p className="gl-full">{entry.full}</p>
          {linkedCommands.length > 0 && (
            <div className="gl-commands">
              <span className="gl-cmd-label">// relevant commands</span>
              <div className="tag-row">
                {linkedCommands.map((v) => (
                  <button
                    key={v.command}
                    className={`cmd-tag cmd-tag-link hat-cmd-${v.hat}`}
                    onClick={() => onCommandClick(v)}
                  >
                    $ {v.command}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function GlossaryView({ allVideos, onCommandClick }) {
  const [cat, setCat]     = useState('all')
  const [search, setSearch] = useState('')

  const filtered = GLOSSARY.filter((e) => {
    if (cat !== 'all' && e.category !== cat) return false
    if (search.trim()) {
      const q = search.toLowerCase()
      return e.term.toLowerCase().includes(q) || e.short.toLowerCase().includes(q) || e.full.toLowerCase().includes(q)
    }
    return true
  })

  return (
    <div className="gl-view">
      <div className="chains-header">
        <div className="chains-title-row">
          <h2 className="chains-title">// concept glossary</h2>
          <span className="chains-count">{filtered.length} terms</span>
        </div>
        <p className="chains-sub">
          Plain-english definitions of the security concepts used throughout this app.
          Click any term to expand. Click a command pill to open its full entry.
        </p>

        <div className="gl-cat-filters">
          {CATEGORIES.map(({ id, label }) => (
            <button
              key={id}
              className={`gl-cat-btn${cat === id ? ' active' : ''}`}
              onClick={() => setCat(id)}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="chain-search" style={{ marginTop: '12px' }}>
          <span className="search-icon">/</span>
          <input
            className="search-input"
            placeholder="search concepts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && <button className="search-clear" onClick={() => setSearch('')}>x</button>}
        </div>
      </div>

      <div className="gl-list">
        {filtered.map((entry) => (
          <GlossaryCard
            key={entry.term}
            entry={entry}
            allVideos={allVideos}
            onCommandClick={onCommandClick}
          />
        ))}
      </div>
    </div>
  )
}
