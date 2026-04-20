import { useState, useEffect } from 'react'

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState(() => {
    try { return JSON.parse(localStorage.getItem('lnotes_bookmarks') || '[]') }
    catch { return [] }
  })

  useEffect(() => {
    localStorage.setItem('lnotes_bookmarks', JSON.stringify(bookmarks))
  }, [bookmarks])

  const toggle = (command) => {
    setBookmarks((prev) =>
      prev.includes(command) ? prev.filter((c) => c !== command) : [...prev, command]
    )
  }

  const isBookmarked = (command) => bookmarks.includes(command)

  return { bookmarks, toggle, isBookmarked }
}
