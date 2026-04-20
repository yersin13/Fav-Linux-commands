import { useState } from 'react'

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
    <button className={`copy-btn${copied ? ' copied' : ''}`} onClick={handle} title="Copy to clipboard">
      {copied ? 'copied' : 'copy'}
    </button>
  )
}

export default function SecurityCard({ video }) {
  const [open, setOpen] = useState(false)
  const [transcriptOpen, setTranscriptOpen] = useState(false)

  return (
    <div className={`sec-card hat-border-${video.hat}${open ? ' open' : ''}`}>
      <div className="sec-header" onClick={() => setOpen(!open)}>
        <div className="sec-header-left">
          <span className={`hat-badge hat-badge-${video.hat}`}>{HAT_LABELS[video.hat]}</span>
          <span className="sec-command">$ {video.command}</span>
          {video.threat_level >= 4 && (
            <span className="threat-dot" title={`Threat: ${THREAT_LABELS[video.threat_level]}`} />
          )}
        </div>
        <div className="sec-header-right">
          <span className="sec-title-short">{video.title}</span>
          <span className="expand-caret">{open ? '▾' : '▸'}</span>
        </div>
      </div>

      {open && (
        <div className="sec-body">
          <p className="sec-intent">{video.security_intent}</p>

          <div className="sec-cols">
            {video.attack_vectors?.length > 0 && (
              <div className="sec-col">
                <h4 className="col-label">// attack vectors</h4>
                <ul className="vector-list">
                  {video.attack_vectors.map((v, i) => (
                    <li key={i} className="vector-item">
                      <span className="vector-bullet">›</span> {v}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {video.defense_use && (
              <div className="sec-col">
                <h4 className="col-label">// defense use</h4>
                <p className="defense-text">{video.defense_use}</p>
              </div>
            )}
          </div>

          {video.mitre_tags?.length > 0 && (
            <div className="sec-row">
              <h4 className="col-label">// mitre att&amp;ck</h4>
              <div className="tag-row">
                {video.mitre_tags.map((t) => (
                  <span key={t} className="mitre-tag">{t}</span>
                ))}
                <span className={`threat-badge threat-${THREAT_LABELS[video.threat_level]}`}>
                  {THREAT_LABELS[video.threat_level]}
                </span>
              </div>
            </div>
          )}

          {video.related_commands?.length > 0 && (
            <div className="sec-row">
              <h4 className="col-label">// related commands</h4>
              <div className="tag-row">
                {video.related_commands.map((c) => (
                  <span key={c} className="cmd-tag">$ {c}</span>
                ))}
              </div>
            </div>
          )}

          {video.quick_use?.length > 0 && (
            <div className="sec-row toolbook-section">
              <h4 className="col-label toolbook-label">// quick use</h4>
              <div className="quick-use-list">
                {video.quick_use.map((line, i) => (
                  <div key={i} className="quick-use-item">
                    <pre className="quick-use-code">{line}</pre>
                    <CopyButton text={line} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {video.combinations?.length > 0 && (
            <div className="sec-row toolbook-section">
              <h4 className="col-label toolbook-label">// combinations</h4>
              <div className="combinations-list">
                {video.combinations.map((combo, i) => (
                  <div key={i} className="combo-item">
                    <div className="combo-header">
                      <span className="combo-with">+ {combo.with}</span>
                      {combo.note && <span className="combo-note">{combo.note}</span>}
                    </div>
                    <div className="combo-example-wrap">
                      <pre className="combo-example">{combo.example}</pre>
                      <CopyButton text={combo.example} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="sec-footer">
            <a href={video.video_url} target="_blank" rel="noopener noreferrer" className="yt-link">
              [▶] Watch on YouTube
            </a>
            {video.transcript && (
              <button className="transcript-btn" onClick={() => setTranscriptOpen(!transcriptOpen)}>
                {transcriptOpen ? '[▾] hide transcript' : '[▸] full transcript'}
              </button>
            )}
          </div>

          {transcriptOpen && video.transcript && (
            <div className="transcript-box">{video.transcript}</div>
          )}
        </div>
      )}
    </div>
  )
}
