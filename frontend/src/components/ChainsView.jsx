import { useState } from 'react'

const HAT_LABELS = { black: 'Black Hat', red: 'Red Hat', blue: 'Blue Hat', gray: 'Utility' }

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handle = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    })
  }
  return (
    <button className={`copy-btn${copied ? ' copied' : ''}`} onClick={handle} title="Copy to clipboard">
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

function ChainSimulator({ chain, onExit }) {
  const [step, setStep] = useState(0)
  const total = chain.steps.length
  const current = chain.steps[step]

  return (
    <div className="simulator-overlay">
      <div className="simulator-panel">
        <div className="simulator-header">
          <span className={`hat-badge hat-badge-${chain.hat}`}>{HAT_LABELS[chain.hat]}</span>
          <span className="simulator-title">{chain.name}</span>
          <span className="simulator-progress">{step + 1} / {total}</span>
          <button className="modal-close" onClick={onExit}>✕</button>
        </div>

        <div className="simulator-track">
          {chain.steps.map((_, i) => (
            <button
              key={i}
              className={`sim-node${i === step ? ' active' : i < step ? ' done' : ''}`}
              onClick={() => setStep(i)}
            >
              {String(i + 1).padStart(2, '0')}
            </button>
          ))}
          <div className="sim-track-line" style={{ width: `${(step / (total - 1)) * 100}%` }} />
        </div>

        <div className="simulator-step">
          <div className="step-number">{String(step + 1).padStart(2, '0')}</div>
          <div className="step-body">
            <div className="step-head">
              <span className="step-name">$ {current.step}</span>
              <span className="step-action">{current.action}</span>
            </div>
            <div className="step-example-wrap">
              <pre className="step-example">{current.example}</pre>
              <CopyButton text={current.example} />
            </div>
            {current.note && (
              <p className="step-note"><span className="note-prefix">// </span>{current.note}</p>
            )}
          </div>
        </div>

        <div className="simulator-nav">
          <button className="sim-btn" onClick={() => setStep(0)} disabled={step === 0}>⟪ start</button>
          <button className="sim-btn" onClick={() => setStep((s) => s - 1)} disabled={step === 0}>◀ prev</button>
          <button className="sim-btn primary" onClick={() => setStep((s) => s + 1)} disabled={step === total - 1}>next ▶</button>
          <button className="sim-btn" onClick={() => setStep(total - 1)} disabled={step === total - 1}>end ⟫</button>
        </div>

        {step === total - 1 && (
          <div className="simulator-done">
            <span className="done-icon">✓</span> Chain complete — {total} steps executed
          </div>
        )}
      </div>
    </div>
  )
}

function ChainCard({ chain, videosByCommand, onSimulate }) {
  const [open, setOpen] = useState(false)

  return (
    <div className={`chain-card hat-border-${chain.hat}${open ? ' open' : ''}`}>
      <div className="chain-header" onClick={() => setOpen(!open)}>
        <div className="chain-header-top">
          <span className={`hat-badge hat-badge-${chain.hat}`}>{HAT_LABELS[chain.hat]}</span>
          <h3 className="chain-name">{chain.name}</h3>
          <span className="chain-caret">{open ? '▾' : '▸'}</span>
        </div>
        <p className="chain-scenario">{chain.scenario}</p>
        <div className="chain-cmd-pills">
          {chain.commands.map((cmd) => {
            const v = videosByCommand[cmd.toLowerCase()]
            return v ? (
              <a
                key={cmd}
                href={v.video_url || '#'}
                target={v.video_url ? '_blank' : undefined}
                rel="noopener noreferrer"
                className={`chain-pill linked hat-cmd-${v.hat}`}
                onClick={(e) => e.stopPropagation()}
              >
                $ {cmd}
              </a>
            ) : (
              <span key={cmd} className="chain-pill external">$ {cmd}</span>
            )
          })}
        </div>
      </div>

      {open && (
        <div className="chain-steps">
          <div className="chain-steps-actions">
            <button
              className="simulate-btn"
              onClick={(e) => { e.stopPropagation(); onSimulate(chain) }}
            >
              [▶] simulate step-by-step
            </button>
          </div>
          {chain.steps.map((step, i) => (
            <div key={i} className="chain-step">
              <div className="step-number">{String(i + 1).padStart(2, '0')}</div>
              <div className="step-body">
                <div className="step-head">
                  <span className="step-name">$ {step.step}</span>
                  <span className="step-action">{step.action}</span>
                </div>
                <div className="step-example-wrap">
                  <pre className="step-example">{step.example}</pre>
                  <CopyButton text={step.example} />
                </div>
                {step.note && (
                  <p className="step-note">
                    <span className="note-prefix">// </span>{step.note}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ChainsView({ chains, videos }) {
  const [hatFilter, setHatFilter] = useState('all')
  const [search, setSearch]       = useState('')
  const [simChain, setSimChain]   = useState(null)

  const videosByCommand = {}
  videos.forEach((v) => { videosByCommand[v.command.toLowerCase()] = v })

  const filtered = chains.filter((c) => {
    if (hatFilter !== 'all' && c.hat !== hatFilter) return false
    if (search.trim()) {
      const q = search.toLowerCase()
      return (
        c.name.toLowerCase().includes(q) ||
        c.scenario.toLowerCase().includes(q) ||
        c.commands.some((cmd) => cmd.toLowerCase().includes(q)) ||
        c.steps?.some(
          (s) =>
            s.step.toLowerCase().includes(q) ||
            s.action.toLowerCase().includes(q) ||
            s.example.toLowerCase().includes(q)
        )
      )
    }
    return true
  })

  return (
    <div className="chains-view">
      {simChain && <ChainSimulator chain={simChain} onExit={() => setSimChain(null)} />}

      <div className="chains-header">
        <div className="chains-title-row">
          <h2 className="chains-title">// attack &amp; defense chains</h2>
          <span className="chains-count">{filtered.length} chains</span>
        </div>
        <p className="chains-sub">
          Real-world multi-step scenarios. Click [▶] simulate to step through any chain interactively.
          Commands with videos are linked. All examples are VM-ready.
        </p>
        <div className="chains-controls">
          <div className="chain-hat-filters">
            {['all','black','red','blue'].map((h) => (
              <button
                key={h}
                className={`chain-hat-btn hat-btn-${h}${hatFilter === h ? ' active' : ''}`}
                onClick={() => setHatFilter(h)}
              >
                {h === 'all' ? 'All' : HAT_LABELS[h]}
              </button>
            ))}
          </div>
          <div className="chain-search">
            <span className="search-icon">/</span>
            <input
              className="search-input"
              placeholder="search chains, commands, techniques..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && <button className="search-clear" onClick={() => setSearch('')}>x</button>}
          </div>
        </div>
      </div>

      <div className="chains-list">
        {filtered.map((chain, i) => (
          <ChainCard key={i} chain={chain} videosByCommand={videosByCommand} onSimulate={setSimChain} />
        ))}
      </div>
    </div>
  )
}
