/**
 * Progress tracking, in localStorage.
 *
 * No account, no sync, no backend — this is a reference you keep open in a
 * tab for eight weeks, and a checkbox that survives a reload is the whole
 * requirement. Every table and the explorer share one store, so ticking a
 * problem off on a pattern page shows up everywhere else.
 */
const KEY = 'progress:v1'

export type ProgressSet = Set<string>

export function readProgress(): ProgressSet {
  if (typeof localStorage === 'undefined') return new Set()
  try {
    const raw = localStorage.getItem(KEY)
    return new Set(raw ? (JSON.parse(raw) as string[]) : [])
  } catch {
    // Corrupt or unavailable storage should never break the page.
    return new Set()
  }
}

export function writeProgress(set: ProgressSet): void {
  try {
    localStorage.setItem(KEY, JSON.stringify([...set]))
  } catch {
    /* private mode / quota — progress is a convenience, not a requirement */
  }
}

export function toggle(slug: string, done: boolean): ProgressSet {
  const set = readProgress()
  if (done) set.add(slug)
  else set.delete(slug)
  writeProgress(set)
  document.dispatchEvent(new CustomEvent('progress:change', { detail: { slug, done } }))
  return set
}

/** Wire every `.progress-box` on the page to the store. */
export function hydrateCheckboxes(root: ParentNode = document): void {
  const done = readProgress()
  for (const box of root.querySelectorAll<HTMLInputElement>('.progress-box')) {
    const slug = box.dataset.slug
    if (!slug) continue
    box.checked = done.has(slug)
    box.addEventListener('change', () => toggle(slug, box.checked))
  }
}
