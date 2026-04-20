import { useState } from 'react'

export default function NoteCard({ note }) {
  const [expanded, setExpanded] = useState(false)
  const [transcriptOpen, setTranscriptOpen] = useState(false)

  return (
    <div className={`note-card${expanded ? ' expanded' : ''}`}>
      <div className="note-header" onClick={() => setExpanded(!expanded)}>
        <div className="note-title-row">
          <span className="command-badge">$ {note.command}</span>
          <span className="note-title">{note.title}</span>
        </div>
        <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div className="note-body">
          {note.error ? (
            <div className="note-error">Error: {note.error}</div>
          ) : (
            <>
              {note.all_commands?.length > 0 && (
                <div className="note-section">
                  <h4 className="section-label">Commands found</h4>
                  <div className="tag-list">
                    {note.all_commands.map((cmd) => (
                      <span key={cmd} className="tag command-tag">
                        {cmd}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {note.flags?.length > 0 && (
                <div className="note-section">
                  <h4 className="section-label">Flags &amp; Options</h4>
                  <div className="tag-list">
                    {note.flags.map((flag, i) => (
                      <span key={i} className="tag flag-tag">
                        {flag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="note-section">
                <a
                  href={note.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="video-link"
                  onClick={(e) => e.stopPropagation()}
                >
                  [&gt;] Watch on YouTube
                </a>
              </div>

              <div className="note-section">
                <button
                  className="transcript-toggle"
                  onClick={() => setTranscriptOpen(!transcriptOpen)}
                >
                  {transcriptOpen ? '▼' : '▶'} Full Transcript
                </button>
                {transcriptOpen && (
                  <div className="transcript-text">{note.transcript}</div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
