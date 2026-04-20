import { useState, useEffect, useMemo } from 'react'
import SearchBar from './components/SearchBar'
import SecurityCard from './components/SecurityCard'
import HatFilter from './components/HatFilter'
import ChainsView from './components/ChainsView'
import StatsBar from './components/StatsBar'

export default function App() {
  const [knowledge, setKnowledge] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hat, setHat] = useState('all')
  const [search, setSearch] = useState('')
  const [view, setView] = useState('notes') // notes | chains

  useEffect(() => {
    fetch('/knowledge.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => { setKnowledge(data); setLoading(false) })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [])

  const filtered = useMemo(() => {
    if (!knowledge) return []
    let videos = knowledge.videos
    if (hat !== 'all') videos = videos.filter((v) => v.hat === hat)
    if (search.trim()) {
      const q = search.toLowerCase()
      videos = videos.filter(
        (v) =>
          v.command.toLowerCase().includes(q) ||
          v.security_intent.toLowerCase().includes(q) ||
          v.attack_vectors.some((a) => a.toLowerCase().includes(q)) ||
          v.mitre_tags.some((t) => t.toLowerCase().includes(q)) ||
          v.transcript.toLowerCase().includes(q)
      )
    }
    return videos
  }, [knowledge, hat, search])

  if (loading) return (
    <div className="splash">
      <span className="splash-prompt">$</span>
      <span className="splash-text">loading knowledge base<span className="blink">_</span></span>
    </div>
  )

  if (error) return (
    <div className="splash error">
      <span className="splash-prompt">!</span>
      <span>Failed to load knowledge.json — run <code>python build_knowledge.py</code> first</span>
    </div>
  )

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-prompt">$</span>
            <span className="logo-text">linux-notes</span>
            <span className="logo-sub">// security intelligence layer</span>
          </div>
          <StatsBar counts={knowledge.hat_counts} total={knowledge.total_videos} />
        </div>
        <nav className="header-nav">
          <button className={`nav-btn${view === 'notes' ? ' active' : ''}`} onClick={() => setView('notes')}>
            Intelligence
          </button>
          <button className={`nav-btn${view === 'chains' ? ' active' : ''}`} onClick={() => setView('chains')}>
            Attack Chains ({knowledge.attack_chains.length})
          </button>
        </nav>
      </header>

      <div className="app-body">
        {view === 'notes' && (
          <>
            <aside className="sidebar">
              <HatFilter active={hat} onChange={setHat} counts={knowledge.hat_counts} />
            </aside>
            <main className="main-content">
              <SearchBar value={search} onChange={setSearch} />
              <p className="results-label">
                {filtered.length} command{filtered.length !== 1 ? 's' : ''}
                {hat !== 'all' && <span className={`hat-inline hat-${hat}`}> [{hat} hat]</span>}
                {search && <span> matching "{search}"</span>}
              </p>
              <div className="cards-grid">
                {filtered.map((v) => <SecurityCard key={v.id} video={v} />)}
              </div>
            </main>
          </>
        )}
        {view === 'chains' && (
          <main className="main-content full">
            <ChainsView chains={knowledge.attack_chains} videos={knowledge.videos} />
          </main>
        )}
      </div>
    </div>
  )
}
