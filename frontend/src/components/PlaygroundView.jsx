import { useState, useEffect, useRef, useMemo, useCallback } from 'react'

const HAT_LABELS  = { black: 'Black Hat', red: 'Red Hat', blue: 'Blue Hat', gray: 'Utility' }
const THREAT_LABELS = ['', 'info', 'low', 'medium', 'high', 'critical']

// ─── shared helpers ──────────────────────────────────────────────────────────

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function pick(arr, n) {
  return shuffle(arr).slice(0, n)
}

function useCardScores() {
  const [scores, setScores] = useState(() => {
    try { return JSON.parse(localStorage.getItem('pg_scores') || '{}') }
    catch { return {} }
  })
  useEffect(() => {
    localStorage.setItem('pg_scores', JSON.stringify(scores))
  }, [scores])

  const record = (cmd, correct) => {
    setScores((prev) => {
      const entry = prev[cmd] || { correct: 0, again: 0 }
      return { ...prev, [cmd]: { ...entry, [correct ? 'correct' : 'again']: entry[correct ? 'correct' : 'again'] + 1 } }
    })
  }
  return { scores, record }
}

// ─── FLASHCARD MODE ───────────────────────────────────────────────────────────

function Flashcards({ videos }) {
  const [hatFilter, setHatFilter]   = useState('all')
  const [weakOnly, setWeakOnly]     = useState(false)
  const [deck, setDeck]             = useState([])
  const [idx, setIdx]               = useState(0)
  const [flipped, setFlipped]       = useState(false)
  const [sessionStats, setSession]  = useState({ correct: 0, again: 0 })
  const { scores, record }          = useCardScores()

  const buildDeck = useCallback(() => {
    let pool = videos.filter((v) => hatFilter === 'all' || v.hat === hatFilter)
    if (weakOnly) pool = pool.filter((v) => {
      const s = scores[v.command]
      return !s || s.again > s.correct
    })
    if (pool.length === 0) pool = videos
    setDeck(shuffle(pool))
    setIdx(0)
    setFlipped(false)
    setSession({ correct: 0, again: 0 })
  }, [videos, hatFilter, weakOnly, scores])

  useEffect(() => { buildDeck() }, [hatFilter, weakOnly])

  const card = deck[idx]
  const total = deck.length
  const pct   = total > 0 ? Math.round(((sessionStats.correct + sessionStats.again) / total) * 100) : 0

  const answer = (correct) => {
    record(card.command, correct)
    setSession((s) => ({ ...s, [correct ? 'correct' : 'again']: s[correct ? 'correct' : 'again'] + 1 }))
    if (idx + 1 < total) { setIdx((i) => i + 1); setFlipped(false) }
    else setIdx(total) // deck done
  }

  if (!card && deck.length > 0) return (
    <div className="pg-done">
      <div className="pg-done-icon">✓</div>
      <h3>Deck complete</h3>
      <p>{sessionStats.correct} correct · {sessionStats.again} to review</p>
      <button className="pg-restart-btn" onClick={buildDeck}>Restart deck</button>
    </div>
  )

  if (!card) return <div className="pg-done"><p>No cards in this filter.</p></div>

  const cardScore = scores[card.command]

  return (
    <div className="fc-wrapper">
      <div className="fc-controls">
        <div className="fc-hat-pills">
          {['all','black','red','blue','gray'].map((h) => (
            <button
              key={h}
              className={`chain-hat-btn hat-btn-${h}${hatFilter === h ? ' active' : ''}`}
              onClick={() => setHatFilter(h)}
            >
              {h === 'all' ? 'All' : HAT_LABELS[h]}
            </button>
          ))}
        </div>
        <label className="fc-weak-toggle">
          <input type="checkbox" checked={weakOnly} onChange={(e) => setWeakOnly(e.target.checked)} />
          weak cards only
        </label>
        <button className="fc-shuffle-btn" onClick={buildDeck}>⟳ shuffle</button>
      </div>

      <div className="fc-progress-row">
        <span className="fc-counter">{Math.min(idx + 1, total)} / {total}</span>
        <div className="fc-progress-track">
          <div className="fc-progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <span className="fc-session-score">
          <span className="fc-correct">{sessionStats.correct}✓</span>
          <span className="fc-again"> {sessionStats.again}↺</span>
        </span>
      </div>

      <div className={`fc-card${flipped ? ' flipped' : ''}`} onClick={() => setFlipped((f) => !f)}>
        <div className="fc-card-inner">
          {/* FRONT */}
          <div className="fc-front">
            <span className={`hat-badge hat-badge-${card.hat}`}>{HAT_LABELS[card.hat]}</span>
            <div className="fc-command">$ {card.command}</div>
            {card.ctf_categories?.length > 0 && (
              <div className="fc-ctf-row">
                {card.ctf_categories.map((c) => <span key={c} className="ctf-tag">{c}</span>)}
              </div>
            )}
            <div className="fc-flip-hint">tap to reveal →</div>
          </div>

          {/* BACK */}
          <div className="fc-back">
            <div className="fc-back-header">
              <span className={`hat-badge hat-badge-${card.hat}`}>{HAT_LABELS[card.hat]}</span>
              <span className="fc-command-small">$ {card.command}</span>
              <span className={`threat-badge threat-${THREAT_LABELS[card.threat_level]}`}>
                {THREAT_LABELS[card.threat_level]}
              </span>
            </div>
            <p className="fc-intent">{card.security_intent}</p>
            {card.attack_vectors?.length > 0 && (
              <div className="fc-vectors">
                {card.attack_vectors.slice(0, 3).map((v, i) => (
                  <span key={i} className="fc-vector-pill">› {v}</span>
                ))}
              </div>
            )}
            {card.quick_use?.length > 0 && (
              <pre className="fc-example">{card.quick_use[0]}</pre>
            )}
            {card.mitre_tags?.length > 0 && (
              <div className="tag-row" style={{ marginTop: 4 }}>
                {card.mitre_tags.slice(0, 2).map((t) => <span key={t} className="mitre-tag">{t}</span>)}
              </div>
            )}
            {cardScore && (
              <div className="fc-history">
                past: <span className="fc-correct">{cardScore.correct}✓</span>
                <span className="fc-again"> {cardScore.again}↺</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {flipped && (
        <div className="fc-answer-row">
          <button className="fc-again-btn" onClick={() => answer(false)}>↺ Again</button>
          <button className="fc-got-btn"   onClick={() => answer(true)}>✓ Got it</button>
        </div>
      )}
    </div>
  )
}

// ─── QUIZ MODE ────────────────────────────────────────────────────────────────

function generateQuestion(videos, used) {
  const pool   = videos.filter((v) => v.attack_vectors?.length > 0 && v.security_intent)
  const rest   = pool.filter((v) => !used.has(v.command))
  const src    = rest.length > 3 ? rest : pool
  const target = src[Math.floor(Math.random() * src.length)]
  const wrong3 = pick(pool.filter((v) => v.command !== target.command), 3)

  // Alternate between two types: identify the function, identify the command
  const type = Math.random() < 0.5 ? 0 : 1

  if (type === 0) {
    // Given command → pick correct description
    const opts = shuffle([target, ...wrong3])
    return {
      type: 0,
      question: `What does  $ ${target.command}  do?`,
      options: opts.map((v) => ({ label: v.security_intent.slice(0, 90) + (v.security_intent.length > 90 ? '…' : ''), value: v.command })),
      answer: target.command,
      command: target.command,
    }
  } else {
    // Given use case / attack vector → pick command
    const snippet = target.attack_vectors[Math.floor(Math.random() * target.attack_vectors.length)]
    const opts = shuffle([target, ...wrong3])
    return {
      type: 1,
      question: `Which command is used for:  "${snippet}"?`,
      options: opts.map((v) => ({ label: `$ ${v.command}`, value: v.command })),
      answer: target.command,
      command: target.command,
    }
  }
}

function Quiz({ videos }) {
  const [q, setQ]           = useState(null)
  const [selected, setSelected] = useState(null)
  const [streak, setStreak] = useState(0)
  const [total, setTotal]   = useState(0)
  const [correct, setCorrect] = useState(0)
  const used = useRef(new Set())

  useEffect(() => { nextQ() }, [])

  const nextQ = () => {
    setQ(generateQuestion(videos, used.current))
    setSelected(null)
  }

  const choose = (val) => {
    if (selected !== null) return
    setSelected(val)
    const right = val === q.answer
    setTotal((t) => t + 1)
    if (right) {
      setCorrect((c) => c + 1)
      setStreak((s) => s + 1)
      used.current.add(q.command)
    } else {
      setStreak(0)
    }
  }

  if (!q) return null

  const answered = selected !== null
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0

  return (
    <div className="quiz-wrapper">
      <div className="quiz-stats">
        <span className="quiz-stat"><span className="qs-val">{streak}</span> streak</span>
        <span className="quiz-stat"><span className="qs-val">{correct}/{total}</span> correct</span>
        <span className="quiz-stat"><span className="qs-val">{accuracy}%</span> accuracy</span>
      </div>

      <div className="quiz-card">
        <div className="quiz-type-label">
          {['identify the function', 'identify the command'][q.type]}
        </div>
        <p className="quiz-question">{q.question}</p>
      </div>

      <div className="quiz-options">
        {q.options.map((opt) => {
          let cls = 'quiz-opt'
          if (answered) {
            if (opt.value === q.answer) cls += ' correct'
            else if (opt.value === selected) cls += ' wrong'
            else cls += ' dim'
          }
          return (
            <button key={opt.value} className={cls} onClick={() => choose(opt.value)}>
              {opt.label}
            </button>
          )
        })}
      </div>

      {answered && (
        <div className={`quiz-feedback${selected === q.answer ? ' right' : ' wrong-fb'}`}>
          {selected === q.answer ? (
            <span>✓ Correct{streak > 2 ? ` — ${streak} streak!` : ''}</span>
          ) : (
            <span>✗ Correct answer: <strong>{q.answer}</strong></span>
          )}
          <button className="quiz-next-btn" onClick={nextQ}>Next →</button>
        </div>
      )}
    </div>
  )
}

// ─── TERMINAL MODE ────────────────────────────────────────────────────────────

const TERM_HELP = `Available commands:
  <command>        look up any command (e.g. nc, dd, find)
  help             show this message
  list             list all available commands
  list <hat>       filter by hat (black / red / blue / gray)
  clear            clear terminal
  random           show a random command entry`

function TermEntry({ video }) {
  return (
    <div className="term-entry">
      <div className="term-entry-header">
        <span className={`hat-badge hat-badge-${video.hat}`}>{HAT_LABELS[video.hat]}</span>
        <span className="term-cmd">$ {video.command}</span>
        <span className={`threat-badge threat-${THREAT_LABELS[video.threat_level]}`}>
          {THREAT_LABELS[video.threat_level]}
        </span>
        {video.mitre_tags?.slice(0, 2).map((t) => <span key={t} className="mitre-tag">{t}</span>)}
      </div>
      <p className="term-intent">{video.security_intent}</p>
      {video.attack_vectors?.length > 0 && (
        <div className="term-section">
          <span className="term-label">attack vectors: </span>
          {video.attack_vectors.map((v, i) => (
            <span key={i} className="term-vector">{v}{i < video.attack_vectors.length - 1 ? ' · ' : ''}</span>
          ))}
        </div>
      )}
      {video.quick_use?.length > 0 && (
        <div className="term-section">
          <span className="term-label">quick use:</span>
          {video.quick_use.slice(0, 2).map((l, i) => (
            <pre key={i} className="term-code">{l}</pre>
          ))}
        </div>
      )}
      {video.root_vs_user?.root && (
        <div className="term-section">
          <span className="term-label">root: </span>
          <span className="term-root">{video.root_vs_user.root.slice(0, 120)}{video.root_vs_user.root.length > 120 ? '…' : ''}</span>
        </div>
      )}
    </div>
  )
}

function Terminal({ videos }) {
  const [input, setInput]     = useState('')
  const [history, setHistory] = useState([{ type: 'system', text: 'shellhats terminal — type a command name or "help"' }])
  const [cmdHistory, setCmdHistory] = useState([])
  const [cmdIdx, setCmdIdx]   = useState(-1)
  const inputRef = useRef(null)
  const bottomRef = useRef(null)
  const byCommand = useMemo(() => {
    const m = {}
    videos.forEach((v) => { m[v.command.toLowerCase()] = v })
    return m
  }, [videos])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  const run = (raw) => {
    const cmd = raw.trim().toLowerCase()
    if (!cmd) return
    setCmdHistory((h) => [raw, ...h].slice(0, 50))
    setCmdIdx(-1)
    setHistory((h) => [...h, { type: 'input', text: raw }])

    if (cmd === 'clear') { setHistory([]); return }
    if (cmd === 'help') { setHistory((h) => [...h, { type: 'system', text: TERM_HELP }]); return }
    if (cmd === 'random') {
      const v = videos[Math.floor(Math.random() * videos.length)]
      setHistory((h) => [...h, { type: 'entry', video: v }])
      return
    }
    if (cmd.startsWith('list')) {
      const parts = cmd.split(' ')
      const hat   = parts[1]
      const pool  = hat ? videos.filter((v) => v.hat === hat) : videos
      if (pool.length === 0) {
        setHistory((h) => [...h, { type: 'error', text: `No commands found for hat: ${hat}` }])
      } else {
        const lines = pool.map((v) => `  ${v.hat.padEnd(6)} $ ${v.command}`).join('\n')
        setHistory((h) => [...h, { type: 'system', text: `${pool.length} commands:\n${lines}` }])
      }
      return
    }
    const found = byCommand[cmd]
    if (found) {
      setHistory((h) => [...h, { type: 'entry', video: found }])
    } else {
      setHistory((h) => [...h, { type: 'error', text: `command not found: ${cmd}  (try "list" to see all)` }])
    }
  }

  const onKey = (e) => {
    if (e.key === 'Enter') { run(input); setInput(''); return }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      const next = Math.min(cmdIdx + 1, cmdHistory.length - 1)
      setCmdIdx(next)
      setInput(cmdHistory[next] || '')
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      const next = Math.max(cmdIdx - 1, -1)
      setCmdIdx(next)
      setInput(next === -1 ? '' : cmdHistory[next])
    }
  }

  return (
    <div className="term-shell" onClick={() => inputRef.current?.focus()}>
      <div className="term-output">
        {history.map((item, i) => (
          <div key={i} className={`term-line term-${item.type}`}>
            {item.type === 'input'  && <span><span className="term-prompt">shellhats $ </span>{item.text}</span>}
            {item.type === 'system' && <pre className="term-sys">{item.text}</pre>}
            {item.type === 'error'  && <span className="term-err">✗ {item.text}</span>}
            {item.type === 'entry'  && <TermEntry video={item.video} />}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="term-input-row">
        <span className="term-prompt">shellhats $ </span>
        <input
          ref={inputRef}
          className="term-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          autoComplete="off"
          autoCapitalize="off"
          spellCheck={false}
          placeholder="type a command..."
        />
      </div>
    </div>
  )
}

// ─── PLAYGROUND ROOT ─────────────────────────────────────────────────────────

const MODES = [
  { id: 'flashcard', label: 'Flashcards', icon: '⟳', desc: 'Flip cards — front shows command, back reveals intel. Track what you know.' },
  { id: 'quiz',      label: 'Quiz',       icon: '?',  desc: 'Multiple-choice questions across all commands. Builds recognition speed.' },
  { id: 'terminal',  label: 'Terminal',   icon: '>_', desc: 'Type any command name and get its full intel inline. Builds muscle memory.' },
]

export default function PlaygroundView({ videos }) {
  const [mode, setMode] = useState('flashcard')

  return (
    <div className="pg-view">
      <div className="pg-header">
        <h2 className="chains-title">// playground</h2>
        <p className="chains-sub">Learn by doing. Three modes to take you from recognition to recall to reflex.</p>
      </div>

      <div className="pg-mode-tabs">
        {MODES.map(({ id, label, icon, desc }) => (
          <button
            key={id}
            className={`pg-mode-tab${mode === id ? ' active' : ''}`}
            onClick={() => setMode(id)}
          >
            <span className="pg-mode-icon">{icon}</span>
            <span className="pg-mode-label">{label}</span>
            <span className="pg-mode-desc">{desc}</span>
          </button>
        ))}
      </div>

      <div className="pg-content">
        {mode === 'flashcard' && <Flashcards videos={videos} />}
        {mode === 'quiz'      && <Quiz       videos={videos} />}
        {mode === 'terminal'  && <Terminal   videos={videos} />}
      </div>
    </div>
  )
}
