import { useState, useEffect, useMemo } from 'react'
import SearchBar from './components/SearchBar'
import SecurityCard from './components/SecurityCard'
import HatFilter from './components/HatFilter'
import ChainsView from './components/ChainsView'
import StatsBar from './components/StatsBar'
import CommandModal from './components/CommandModal'
import ChainBuilder from './components/ChainBuilder'
import CTFView from './components/CTFView'
import ExportButton from './components/ExportButton'
import { useBookmarks } from './hooks/useBookmarks'
import { useProgress } from './hooks/useProgress'

export default function App() {
  const [knowledge, setKnowledge] = useState(null)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)
  const [hat, setHat]             = useState('all')
  const [search, setSearch]       = useState('')
  const [view, setView]           = useState('notes') // notes | chains | builder | ctf
  const [modal, setModal]         = useState(null)    // video object or null
  const [bookmarksOnly, setBookmarksOnly] = useState(false)

  const { bookmarks, toggle: toggleBookmark, isBookmarked } = useBookmarks()
  const { learned, toggleLearned, isLearned, progressByHat } = useProgress()

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
    if (bookmarksOnly) videos = videos.filter((v) => isBookmarked(v.command))
    if (search.trim()) {
      const q = search.toLowerCase()
      videos = videos.filter(
        (v) =>
          v.command.toLowerCase().includes(q) ||
          v.security_intent.toLowerCase().includes(q) ||
          v.attack_vectors.some((a) => a.toLowerCase().includes(q)) ||
          v.mitre_tags.some((t) => t.toLowerCase().includes(q)) ||
          v.ctf_categories?.some((c) => c.toLowerCase().includes(q)) ||
          v.cve_refs?.some((c) => c.toLowerCase().includes(q)) ||
          v.transcript.toLowerCase().includes(q)
      )
    }
    return videos
  }, [knowledge, hat, search, bookmarksOnly, bookmarks])

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

  const progress = progressByHat(knowledge.videos)

  return (
    <div className="app">
      {modal && (
        <CommandModal
          video={modal}
          allVideos={knowledge.videos}
          allChains={knowledge.attack_chains}
          onClose={() => setModal(null)}
          onNavigate={(v) => setModal(v)}
        />
      )}

      <nav className="bottom-nav">
        {[
          { id: 'notes',   icon: '◈', label: 'Intel' },
          { id: 'chains',  icon: '⛓', label: 'Chains' },
          { id: 'ctf',     icon: '⚡', label: 'CTF' },
          { id: 'builder', icon: '⌘', label: 'Build' },
        ].map(({ id, icon, label }) => (
          <button
            key={id}
            className={`bottom-nav-btn${view === id ? ' active' : ''}`}
            onClick={() => setView(id)}
          >
            <span className="bn-icon">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-prompt">$</span>
            <span className="logo-text">linux-notes</span>
            <span className="logo-sub">// security toolbook</span>
          </div>
          <StatsBar
            counts={knowledge.hat_counts}
            total={knowledge.total_tools || knowledge.total_videos}
            progress={progress}
            learned={learned.length}
          />
        </div>
        <nav className="header-nav">
          {[
            { id: 'notes',   label: 'Intelligence' },
            { id: 'chains',  label: `Chains (${knowledge.attack_chains.length})` },
            { id: 'ctf',     label: 'CTF Toolkit' },
            { id: 'builder', label: 'Chain Builder' },
          ].map(({ id, label }) => (
            <button
              key={id}
              className={`nav-btn${view === id ? ' active' : ''}`}
              onClick={() => setView(id)}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      <div className="app-body">
        {view === 'notes' && (
          <>
            <aside className="sidebar">
              <HatFilter
                active={hat}
                onChange={setHat}
                counts={knowledge.hat_counts}
                progress={progress}
              />
              <div className="sidebar-section">
                <p className="filter-label" style={{ marginTop: '20px' }}>// bookmarks</p>
                <button
                  className={`sidebar-toggle${bookmarksOnly ? ' active' : ''}`}
                  onClick={() => setBookmarksOnly((b) => !b)}
                >
                  {bookmarksOnly ? '★ showing bookmarks' : `☆ bookmarks (${bookmarks.length})`}
                </button>
              </div>
            </aside>

            <main className="main-content">
              <div className="main-toolbar">
                <SearchBar value={search} onChange={setSearch} />
                <ExportButton videos={filtered} hat={hat} search={search} />
              </div>
              <p className="results-label">
                {filtered.length} command{filtered.length !== 1 ? 's' : ''}
                {hat !== 'all' && <span className={`hat-inline hat-${hat}`}> [{hat} hat]</span>}
                {search && <span> matching "{search}"</span>}
                {bookmarksOnly && <span> ★ bookmarked</span>}
                <span className="results-learned"> — {learned.length} learned</span>
              </p>
              <div className="cards-grid">
                {filtered.map((v) => (
                  <SecurityCard
                    key={v.id}
                    video={v}
                    bookmarked={isBookmarked(v.command)}
                    learned={isLearned(v.command)}
                    onBookmark={() => toggleBookmark(v.command)}
                    onLearn={() => toggleLearned(v.command)}
                    onOpenModal={() => setModal(v)}
                  />
                ))}
              </div>
            </main>
          </>
        )}

        {view === 'chains' && (
          <main className="main-content full">
            <ChainsView chains={knowledge.attack_chains} videos={knowledge.videos} />
          </main>
        )}

        {view === 'ctf' && (
          <main className="main-content full">
            <CTFView videos={knowledge.videos} onOpenModal={setModal} />
          </main>
        )}

        {view === 'builder' && (
          <main className="main-content full">
            <ChainBuilder videos={knowledge.videos} />
          </main>
        )}
      </div>
    </div>
  )
}
