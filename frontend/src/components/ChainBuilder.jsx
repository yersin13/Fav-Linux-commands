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
    <button className={`copy-btn${copied ? ' copied' : ''}`} onClick={handle}>
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

export default function ChainBuilder({ videos }) {
  const [steps, setSteps] = useState([])
  const [search, setSearch] = useState('')
  const [chainName, setChainName] = useState('')
  const [dragIdx, setDragIdx] = useState(null)
  const [exported, setExported] = useState(false)

  const filtered = videos.filter((v) => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      v.command.toLowerCase().includes(q) ||
      v.hat.toLowerCase().includes(q) ||
      v.security_intent.toLowerCase().includes(q)
    )
  }).slice(0, 30)

  const addStep = (video) => {
    const example = video.quick_use?.[0] || `${video.command} [options]`
    setSteps((prev) => [...prev, {
      id: Date.now(),
      command: video.command,
      hat: video.hat,
      action: video.attack_vectors?.[0] || 'execute',
      example,
      note: '',
    }])
  }

  const removeStep = (id) => setSteps((prev) => prev.filter((s) => s.id !== id))

  const updateStep = (id, field, value) => {
    setSteps((prev) => prev.map((s) => s.id === id ? { ...s, [field]: value } : s))
  }

  const moveStep = (from, to) => {
    if (to < 0 || to >= steps.length) return
    const next = [...steps]
    const [item] = next.splice(from, 1)
    next.splice(to, 0, item)
    setSteps(next)
  }

  const exportMarkdown = () => {
    const lines = [
      `# ${chainName || 'My Chain'}`,
      '',
      '## Steps',
      '',
      ...steps.map((s, i) => [
        `### ${String(i + 1).padStart(2, '0')}. ${s.command} — ${s.action}`,
        '',
        '```bash',
        s.example,
        '```',
        s.note ? `> ${s.note}` : '',
        '',
      ].filter((l) => l !== null).join('\n')),
    ]
    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(chainName || 'chain').replace(/\s+/g, '_').toLowerCase()}.md`
    a.click()
    URL.revokeObjectURL(url)
    setExported(true)
    setTimeout(() => setExported(false), 2000)
  }

  const clearAll = () => { setSteps([]); setChainName('') }

  return (
    <div className="builder-view">
      <div className="builder-header">
        <h2 className="chains-title">// chain builder</h2>
        <p className="chains-sub">Click commands to add them as steps. Reorder, annotate, then export as Markdown.</p>
      </div>

      <div className="builder-layout">
        {/* Left: command picker */}
        <div className="builder-picker">
          <p className="filter-label">// pick commands</p>
          <div className="chain-search" style={{ marginBottom: '12px' }}>
            <span className="search-icon">/</span>
            <input
              className="search-input"
              placeholder="filter commands..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && <button className="search-clear" onClick={() => setSearch('')}>x</button>}
          </div>
          <div className="picker-list">
            {filtered.map((v) => (
              <button
                key={v.id}
                className={`picker-item hat-border-${v.hat}`}
                onClick={() => addStep(v)}
                title={v.security_intent}
              >
                <span className={`hat-badge hat-badge-${v.hat}`}>{v.hat}</span>
                <span className="picker-cmd">$ {v.command}</span>
                <span className="picker-add">+</span>
              </button>
            ))}
          </div>
        </div>

        {/* Right: chain canvas */}
        <div className="builder-canvas">
          <div className="builder-canvas-header">
            <input
              className="chain-name-input"
              placeholder="chain name..."
              value={chainName}
              onChange={(e) => setChainName(e.target.value)}
            />
            <div className="builder-actions">
              {steps.length > 0 && (
                <>
                  <button
                    className={`export-btn${exported ? ' exported' : ''}`}
                    onClick={exportMarkdown}
                  >
                    {exported ? '✓ exported' : '↓ export .md'}
                  </button>
                  <button className="clear-btn" onClick={clearAll}>✕ clear</button>
                </>
              )}
            </div>
          </div>

          {steps.length === 0 ? (
            <div className="builder-empty">
              <span className="empty-prompt">$</span>
              <span>add commands from the left to build your chain</span>
            </div>
          ) : (
            <div className="builder-steps">
              {steps.map((s, i) => (
                <div
                  key={s.id}
                  className={`builder-step hat-border-${s.hat}${dragIdx === i ? ' dragging' : ''}`}
                  draggable
                  onDragStart={() => setDragIdx(i)}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={() => { moveStep(dragIdx, i); setDragIdx(null) }}
                  onDragEnd={() => setDragIdx(null)}
                >
                  <div className="builder-step-left">
                    <span className="step-number">{String(i + 1).padStart(2, '0')}</span>
                    <span className="drag-handle">⠿</span>
                  </div>
                  <div className="builder-step-body">
                    <div className="builder-step-top">
                      <span className={`hat-badge hat-badge-${s.hat}`}>{HAT_LABELS[s.hat]}</span>
                      <span className="builder-cmd">$ {s.command}</span>
                      <input
                        className="builder-action-input"
                        value={s.action}
                        onChange={(e) => updateStep(s.id, 'action', e.target.value)}
                        placeholder="action description..."
                      />
                      <button className="remove-step-btn" onClick={() => removeStep(s.id)}>✕</button>
                    </div>
                    <div className="step-example-wrap">
                      <textarea
                        className="builder-example-input"
                        value={s.example}
                        onChange={(e) => updateStep(s.id, 'example', e.target.value)}
                        rows={2}
                      />
                      <CopyButton text={s.example} />
                    </div>
                    <input
                      className="builder-note-input"
                      value={s.note}
                      onChange={(e) => updateStep(s.id, 'note', e.target.value)}
                      placeholder="// add a note..."
                    />
                  </div>
                  <div className="builder-step-right">
                    <button className="step-move-btn" onClick={() => moveStep(i, i - 1)} disabled={i === 0}>▲</button>
                    <button className="step-move-btn" onClick={() => moveStep(i, i + 1)} disabled={i === steps.length - 1}>▼</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
