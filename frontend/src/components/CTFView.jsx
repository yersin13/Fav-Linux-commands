import { useState } from 'react'

const CATEGORIES = [
  { id: 'all',       label: 'All',         icon: '◈' },
  { id: 'pwn',       label: 'Pwn',         icon: '⚡' },
  { id: 'web',       label: 'Web',         icon: '⛓' },
  { id: 'crypto',    label: 'Crypto',      icon: '🔑' },
  { id: 'forensics', label: 'Forensics',   icon: '🔬' },
  { id: 'reversing', label: 'Reversing',   icon: '⟲' },
  { id: 'network',   label: 'Network',     icon: '⌁' },
  { id: 'linux',     label: 'Linux',       icon: '❯' },
  { id: 'recon',     label: 'Recon',       icon: '◎' },
  { id: 'scripting', label: 'Scripting',   icon: '⌘' },
]

const HAT_LABELS = { black: 'Black Hat', red: 'Red Hat', blue: 'Blue Hat', gray: 'Utility' }
const THREAT_LABELS = ['', 'info', 'low', 'medium', 'high', 'critical']

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handle = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    })
  }
  return (
    <button className={`copy-btn${copied ? ' copied' : ''}`} onClick={handle}>
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

function CTFCard({ video, onOpen }) {
  return (
    <div
      className={`ctf-card hat-border-${video.hat}`}
      onClick={() => onOpen(video)}
    >
      <div className="ctf-card-header">
        <span className={`hat-badge hat-badge-${video.hat}`}>{HAT_LABELS[video.hat]}</span>
        <span className="sec-command">$ {video.command}</span>
        {video.threat_level >= 4 && (
          <span className={`threat-badge threat-${THREAT_LABELS[video.threat_level]}`}>
            {THREAT_LABELS[video.threat_level]}
          </span>
        )}
      </div>
      <p className="ctf-intent">{video.security_intent}</p>
      <div className="ctf-cats">
        {video.ctf_categories?.map((c) => (
          <span key={c} className="ctf-tag">{c}</span>
        ))}
      </div>
      {video.quick_use?.length > 0 && (
        <div className="ctf-quickuse">
          <div className="quick-use-item" onClick={(e) => e.stopPropagation()}>
            <pre className="quick-use-code">{video.quick_use[0]}</pre>
            <CopyButton text={video.quick_use[0]} />
          </div>
        </div>
      )}
    </div>
  )
}

export default function CTFView({ videos, onOpenModal }) {
  const [cat, setCat] = useState('all')
  const [search, setSearch] = useState('')

  const withCTF = videos.filter((v) => v.ctf_categories?.length > 0)

  const filtered = withCTF.filter((v) => {
    if (cat !== 'all' && !v.ctf_categories.includes(cat)) return false
    if (search.trim()) {
      const q = search.toLowerCase()
      return (
        v.command.toLowerCase().includes(q) ||
        v.security_intent.toLowerCase().includes(q) ||
        v.ctf_categories.some((c) => c.includes(q))
      )
    }
    return true
  })

  const catCounts = {}
  withCTF.forEach((v) => {
    v.ctf_categories.forEach((c) => { catCounts[c] = (catCounts[c] || 0) + 1 })
  })

  return (
    <div className="ctf-view">
      <div className="chains-header">
        <div className="chains-title-row">
          <h2 className="chains-title">// ctf toolkit</h2>
          <span className="chains-count">{filtered.length} tools</span>
        </div>
        <p className="chains-sub">
          Commands grouped by CTF category. Click any card to open the full toolbook entry.
        </p>

        <div className="ctf-cat-filters">
          {CATEGORIES.map(({ id, label, icon }) => (
            <button
              key={id}
              className={`ctf-cat-btn${cat === id ? ' active' : ''}`}
              onClick={() => setCat(id)}
            >
              <span>{icon}</span>
              <span>{label}</span>
              {id !== 'all' && catCounts[id] && (
                <span className="ctf-cat-count">{catCounts[id]}</span>
              )}
            </button>
          ))}
        </div>

        <div className="chain-search" style={{ marginTop: '12px' }}>
          <span className="search-icon">/</span>
          <input
            className="search-input"
            placeholder="search ctf tools..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && <button className="search-clear" onClick={() => setSearch('')}>x</button>}
        </div>
      </div>

      <div className="ctf-grid">
        {filtered.map((v) => (
          <CTFCard key={v.id} video={v} onOpen={onOpenModal} />
        ))}
      </div>
    </div>
  )
}
