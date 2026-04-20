import { useState, useRef } from 'react'
import { GLOSSARY_INDEX } from '../data/glossary'

// Wraps a known term with a hover tooltip showing its plain-english definition.
// Usage: <Term>reverse shell</Term>  or  <Term name="SUID">SUID bit</Term>
export function Term({ children, name }) {
  const [visible, setVisible] = useState(false)
  const [pos, setPos] = useState({ top: true })
  const ref = useRef(null)

  const key = (name || children || '').toString().toLowerCase()
  const entry = GLOSSARY_INDEX[key]
  if (!entry) return <span>{children}</span>

  const show = (e) => {
    const rect = ref.current?.getBoundingClientRect()
    setPos({ top: rect && rect.top > 180 })
    setVisible(true)
  }

  return (
    <span className="term-wrap" ref={ref} onMouseEnter={show} onMouseLeave={() => setVisible(false)}>
      <span className="term-highlight">{children}</span>
      {visible && (
        <span className={`term-tooltip${pos.top ? '' : ' tooltip-below'}`}>
          <span className="tt-term">{entry.term}</span>
          <span className="tt-def">{entry.short}</span>
        </span>
      )}
    </span>
  )
}

// Renders a block of text and auto-links any known glossary terms found in it.
// Used on SecurityCard intent paragraphs when tooltips are enabled.
export function AnnotatedText({ text, enabled }) {
  if (!enabled || !text) return <span>{text}</span>

  const terms = Object.keys(GLOSSARY_INDEX).sort((a, b) => b.length - a.length)
  const parts = []
  let remaining = text
  let key = 0

  while (remaining.length > 0) {
    let earliest = null
    let earliestIdx = Infinity

    for (const term of terms) {
      const idx = remaining.toLowerCase().indexOf(term)
      if (idx !== -1 && idx < earliestIdx) {
        earliestIdx = idx
        earliest = term
      }
    }

    if (!earliest || earliestIdx === Infinity) {
      parts.push(<span key={key++}>{remaining}</span>)
      break
    }

    if (earliestIdx > 0) {
      parts.push(<span key={key++}>{remaining.slice(0, earliestIdx)}</span>)
    }
    const matchedText = remaining.slice(earliestIdx, earliestIdx + earliest.length)
    parts.push(<Term key={key++} name={earliest}>{matchedText}</Term>)
    remaining = remaining.slice(earliestIdx + earliest.length)
  }

  return <>{parts}</>
}
