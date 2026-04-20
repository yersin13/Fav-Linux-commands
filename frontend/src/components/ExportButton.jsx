import { useState } from 'react'

const THREAT_LABELS = ['', 'info', 'low', 'medium', 'high', 'critical']

export default function ExportButton({ videos, hat, search }) {
  const [open, setOpen] = useState(false)
  const [done, setDone] = useState(false)

  const doExport = (format) => {
    const subset = videos // already filtered by caller
    let content = ''
    const title = `Linux Security Toolbook${hat !== 'all' ? ` — ${hat} hat` : ''}${search ? ` — "${search}"` : ''}`

    if (format === 'md') {
      const lines = [
        `# ${title}`,
        `> Generated ${new Date().toISOString().slice(0, 10)} | ${subset.length} commands`,
        '',
      ]
      subset.forEach((v) => {
        lines.push(`## \$ ${v.command}`)
        lines.push(`**Hat:** ${v.hat} | **Threat:** ${THREAT_LABELS[v.threat_level] || '-'}`)
        lines.push('')
        lines.push(v.security_intent)
        lines.push('')
        if (v.attack_vectors?.length) {
          lines.push('**Attack Vectors:**')
          v.attack_vectors.forEach((a) => lines.push(`- ${a}`))
          lines.push('')
        }
        if (v.defense_use) {
          lines.push(`**Defense:** ${v.defense_use}`)
          lines.push('')
        }
        if (v.mitre_tags?.length) {
          lines.push(`**MITRE:** ${v.mitre_tags.join(', ')}`)
          lines.push('')
        }
        if (v.cve_refs?.length) {
          lines.push('**CVEs:**')
          v.cve_refs.forEach((c) => lines.push(`- ${c}`))
          lines.push('')
        }
        if (v.quick_use?.length) {
          lines.push('**Quick Use:**')
          lines.push('```bash')
          v.quick_use.forEach((l) => lines.push(l))
          lines.push('```')
          lines.push('')
        }
        if (v.combinations?.length) {
          lines.push('**Combinations:**')
          v.combinations.forEach((c) => {
            lines.push(`- **+ ${c.with}** — ${c.note || ''}`)
            lines.push('  ```bash')
            lines.push(`  ${c.example}`)
            lines.push('  ```')
          })
          lines.push('')
        }
        if (v.root_vs_user?.root) {
          lines.push(`**Root:** ${v.root_vs_user.root}`)
          lines.push(`**User:** ${v.root_vs_user.user}`)
          lines.push('')
        }
        lines.push('---')
        lines.push('')
      })
      content = lines.join('\n')
    } else {
      // plain text cheat sheet
      const lines = [
        title.toUpperCase(),
        '='.repeat(title.length),
        `${subset.length} commands | ${new Date().toISOString().slice(0, 10)}`,
        '',
      ]
      subset.forEach((v) => {
        lines.push(`$ ${v.command.toUpperCase()} [${v.hat}] [${THREAT_LABELS[v.threat_level]}]`)
        lines.push(v.security_intent)
        if (v.quick_use?.length) {
          lines.push('')
          v.quick_use.slice(0, 2).forEach((l) => lines.push(`  ${l}`))
        }
        lines.push('')
      })
      content = lines.join('\n')
    }

    const ext = format === 'md' ? 'md' : 'txt'
    const filename = `toolbook_${(hat !== 'all' ? hat : 'all')}_${new Date().toISOString().slice(0, 10)}.${ext}`
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = filename; a.click()
    URL.revokeObjectURL(url)
    setOpen(false)
    setDone(true)
    setTimeout(() => setDone(false), 2000)
  }

  return (
    <div className="export-wrapper">
      <button
        className={`export-trigger${done ? ' exported' : ''}`}
        onClick={() => setOpen((o) => !o)}
      >
        {done ? '✓ saved' : '↓ export'}
      </button>
      {open && (
        <div className="export-dropdown">
          <button className="export-opt" onClick={() => doExport('md')}>Markdown (.md)</button>
          <button className="export-opt" onClick={() => doExport('txt')}>Cheat Sheet (.txt)</button>
        </div>
      )}
    </div>
  )
}
