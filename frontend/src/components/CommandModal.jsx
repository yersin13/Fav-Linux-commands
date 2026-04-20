import { useState, useEffect } from 'react'

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

export default function CommandModal({ video, allVideos, allChains, onClose, onNavigate }) {
  const [transcriptOpen, setTranscriptOpen] = useState(false)

  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const relatedInKB = (video.related_commands || [])
    .map((cmd) => allVideos.find((v) => v.command.toLowerCase() === cmd.toLowerCase()))
    .filter(Boolean)

  const appearsInChains = allChains.filter((c) =>
    c.commands.some((cmd) => cmd.toLowerCase() === video.command.toLowerCase())
  )

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-topbar">
          <div className="modal-title-row">
            <span className={`hat-badge hat-badge-${video.hat}`}>{HAT_LABELS[video.hat]}</span>
            <h2 className="modal-command">$ {video.command}</h2>
            {video.extra && <span className="extra-badge">extended</span>}
            {video.threat_level >= 1 && (
              <span className={`threat-badge threat-${THREAT_LABELS[video.threat_level]}`}>
                {THREAT_LABELS[video.threat_level]}
              </span>
            )}
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Intent */}
          <section className="modal-section">
            <h4 className="modal-section-label">// security intent</h4>
            <p className="modal-intent">{video.security_intent}</p>
          </section>

          {/* Attack + Defense */}
          <div className="modal-two-col">
            {video.attack_vectors?.length > 0 && (
              <section className="modal-section">
                <h4 className="modal-section-label">// attack vectors</h4>
                <ul className="vector-list">
                  {video.attack_vectors.map((v, i) => (
                    <li key={i} className="vector-item"><span className="vector-bullet">›</span> {v}</li>
                  ))}
                </ul>
              </section>
            )}
            {video.defense_use && (
              <section className="modal-section">
                <h4 className="modal-section-label">// defense use</h4>
                <p className="defense-text">{video.defense_use}</p>
              </section>
            )}
          </div>

          {/* MITRE + CVEs */}
          <div className="modal-two-col">
            {video.mitre_tags?.length > 0 && (
              <section className="modal-section">
                <h4 className="modal-section-label">// mitre att&amp;ck</h4>
                <div className="tag-row">
                  {video.mitre_tags.map((t) => (
                    <span key={t} className="mitre-tag">{t}</span>
                  ))}
                </div>
              </section>
            )}
            {video.cve_refs?.length > 0 && (
              <section className="modal-section">
                <h4 className="modal-section-label">// cve references</h4>
                <ul className="cve-list">
                  {video.cve_refs.map((c, i) => (
                    <li key={i} className="cve-item">
                      <span className="cve-bullet">⚠</span> {c}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>

          {/* Root vs User diff */}
          {video.root_vs_user && Object.keys(video.root_vs_user).length > 0 && (
            <section className="modal-section">
              <h4 className="modal-section-label">// root vs user</h4>
              <div className="rvu-grid">
                <div className="rvu-card rvu-root">
                  <span className="rvu-label">root</span>
                  <p>{video.root_vs_user.root}</p>
                </div>
                <div className="rvu-card rvu-user">
                  <span className="rvu-label">user</span>
                  <p>{video.root_vs_user.user}</p>
                </div>
              </div>
            </section>
          )}

          {/* CTF categories */}
          {video.ctf_categories?.length > 0 && (
            <section className="modal-section">
              <h4 className="modal-section-label">// ctf categories</h4>
              <div className="tag-row">
                {video.ctf_categories.map((c) => (
                  <span key={c} className="ctf-tag">{c}</span>
                ))}
              </div>
            </section>
          )}

          {/* Quick use */}
          {video.quick_use?.length > 0 && (
            <section className="modal-section toolbook-section">
              <h4 className="modal-section-label toolbook-label">// quick use</h4>
              <div className="quick-use-list">
                {video.quick_use.map((line, i) => (
                  <div key={i} className="quick-use-item">
                    <pre className="quick-use-code">{line}</pre>
                    <CopyButton text={line} />
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Combinations */}
          {video.combinations?.length > 0 && (
            <section className="modal-section toolbook-section">
              <h4 className="modal-section-label toolbook-label">// combinations</h4>
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
            </section>
          )}

          {/* Appears in chains */}
          {appearsInChains.length > 0 && (
            <section className="modal-section">
              <h4 className="modal-section-label">// appears in chains</h4>
              <div className="modal-chains-list">
                {appearsInChains.map((chain, i) => (
                  <div key={i} className={`modal-chain-pill hat-border-${chain.hat}`}>
                    <span className={`hat-badge hat-badge-${chain.hat}`}>{HAT_LABELS[chain.hat]}</span>
                    <span className="modal-chain-name">{chain.name}</span>
                    <span className="modal-chain-scenario">{chain.scenario}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Related commands — clickable */}
          {relatedInKB.length > 0 && (
            <section className="modal-section">
              <h4 className="modal-section-label">// related commands</h4>
              <div className="tag-row">
                {relatedInKB.map((v) => (
                  <button
                    key={v.command}
                    className={`cmd-tag cmd-tag-link hat-cmd-${v.hat}`}
                    onClick={() => onNavigate(v)}
                  >
                    $ {v.command}
                  </button>
                ))}
                {(video.related_commands || [])
                  .filter((cmd) => !allVideos.find((v) => v.command.toLowerCase() === cmd.toLowerCase()))
                  .map((cmd) => (
                    <span key={cmd} className="cmd-tag external">$ {cmd}</span>
                  ))}
              </div>
            </section>
          )}

          {/* YouTube link + transcript */}
          {video.video_url && (
            <section className="modal-section">
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
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
