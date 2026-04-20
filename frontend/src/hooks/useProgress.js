import { useState, useEffect } from 'react'

export function useProgress() {
  const [learned, setLearned] = useState(() => {
    try { return JSON.parse(localStorage.getItem('lnotes_learned') || '[]') }
    catch { return [] }
  })

  useEffect(() => {
    localStorage.setItem('lnotes_learned', JSON.stringify(learned))
  }, [learned])

  const toggleLearned = (command) => {
    setLearned((prev) =>
      prev.includes(command) ? prev.filter((c) => c !== command) : [...prev, command]
    )
  }

  const isLearned = (command) => learned.includes(command)

  const progressByHat = (videos) => {
    const hats = { black: { total: 0, done: 0 }, red: { total: 0, done: 0 }, blue: { total: 0, done: 0 }, gray: { total: 0, done: 0 } }
    videos.forEach((v) => {
      if (!hats[v.hat]) return
      hats[v.hat].total++
      if (learned.includes(v.command)) hats[v.hat].done++
    })
    return hats
  }

  return { learned, toggleLearned, isLearned, progressByHat }
}
