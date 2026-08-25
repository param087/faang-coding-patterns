/**
 * The problem explorer — the page you actually live in.
 *
 * Everything the site knows, filterable: 3,700 problems across 39 patterns and
 * 659 companies. The core six ship inside `problems.json`; the other 653 load
 * their frequency map on demand, which keeps first paint small without giving
 * up the long tail.
 *
 * Filter state lives in the URL so a view is shareable, and mirrors to
 * localStorage so reopening the tab lands you where you left off.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import { PATTERNS } from '../data/taxonomy.ts'
import {
  type Company,
  type Difficulty,
  type ExplorerProblem,
  type Logo,
  WINDOW_LABELS,
} from '../lib/problems.ts'
import { readProgress, toggle } from '../lib/progress.ts'

interface Props {
  problems: ExplorerProblem[]
  companies: Company[]
  logos: Record<string, Logo>
  /** `import.meta.env.BASE_URL`, passed in because islands don't inherit it. */
  base: string
}

const DIFFICULTIES: Difficulty[] = ['Easy', 'Medium', 'Hard']
const PATTERN_NAME = new Map(PATTERNS.map((p) => [p.id, p.name]))
const PAGE_SIZE = 100

interface Filters {
  q: string
  difficulty: Difficulty[]
  pattern: string
  company: string
  window: number
  minFrequency: number
  hidePremium: boolean
  list: '' | 'blind75' | 'nc150' | 'curated'
  hideDone: boolean
}

const DEFAULTS: Filters = {
  q: '',
  difficulty: [],
  pattern: '',
  company: '',
  window: 2,
  minFrequency: 0,
  hidePremium: false,
  list: '',
  hideDone: false,
}

function readUrl(): Filters {
  if (typeof location === 'undefined') return DEFAULTS
  const p = new URLSearchParams(location.search)
  const stored = (() => {
    try {
      return JSON.parse(localStorage.getItem('explorer:v1') ?? 'null') as Filters | null
    } catch {
      return null
    }
  })()
  // An explicit URL always wins; storage only fills a bare visit.
  const base = p.toString() ? DEFAULTS : { ...DEFAULTS, ...stored }
  return {
    ...base,
    ...(p.has('q') ? { q: p.get('q') ?? '' } : {}),
    ...(p.has('d')
      ? { difficulty: (p.get('d') ?? '').split(',').filter(Boolean) as Difficulty[] }
      : {}),
    ...(p.has('p') ? { pattern: p.get('p') ?? '' } : {}),
    ...(p.has('c') ? { company: p.get('c') ?? '' } : {}),
    ...(p.has('w') ? { window: Number(p.get('w')) } : {}),
    ...(p.has('f') ? { minFrequency: Number(p.get('f')) } : {}),
    ...(p.has('list') ? { list: (p.get('list') ?? '') as Filters['list'] } : {}),
  }
}

function writeUrl(f: Filters): void {
  const p = new URLSearchParams()
  if (f.q) p.set('q', f.q)
  if (f.difficulty.length) p.set('d', f.difficulty.join(','))
  if (f.pattern) p.set('p', f.pattern)
  if (f.company) p.set('c', f.company)
  if (f.window !== 2) p.set('w', String(f.window))
  if (f.minFrequency) p.set('f', String(f.minFrequency))
  if (f.list) p.set('list', f.list)
  const query = p.toString()
  history.replaceState(null, '', query ? `?${query}` : location.pathname)
  try {
    localStorage.setItem('explorer:v1', JSON.stringify(f))
  } catch {
    /* storage is optional */
  }
}

function Mark({ logo, name, size = 14 }: { logo: Logo; name: string; size?: number }) {
  const initials = name
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
  const text = (
    initials.length > 1 ? (initials[0]?.[0] ?? '') + (initials[1]?.[0] ?? '') : name.slice(0, 2)
  ).toUpperCase()
  return (
    <span
      className="logo-chip !border-0 !bg-transparent !p-0"
      style={{
        ['--logo' as string]: `#${logo.hex}`,
        ...(logo.hexDark ? { ['--logo-dark' as string]: `#${logo.hexDark}` } : {}),
      }}
    >
      {logo.path ? (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          aria-hidden="true"
          className="logo-mark shrink-0"
        >
          <path d={logo.path} />
        </svg>
      ) : (
        <span
          className="logo-monogram tabular grid shrink-0 place-items-center rounded-[3px] font-semibold"
          style={{ width: size, height: size, fontSize: size * 0.5 }}
          aria-hidden="true"
        >
          {text}
        </span>
      )}
    </span>
  )
}

export default function Explorer({ problems, companies, logos, base }: Props) {
  const [f, setF] = useState<Filters>(DEFAULTS)
  const [ready, setReady] = useState(false)
  const [done, setDone] = useState<Set<string>>(new Set())
  const [limit, setLimit] = useState(PAGE_SIZE)
  /** Lazily-fetched frequency maps for non-core companies. */
  const [extra, setExtra] = useState<Record<string, Record<string, (number | null)[]>>>({})
  const [loading, setLoading] = useState(false)
  const [companyQuery, setCompanyQuery] = useState('')
  const [companyOpen, setCompanyOpen] = useState(false)

  // URL/storage is only readable on the client, so hydrate after mount.
  useEffect(() => {
    setF(readUrl())
    setDone(readProgress())
    setReady(true)
  }, [])
  useEffect(() => {
    if (ready) writeUrl(f)
    setLimit(PAGE_SIZE)
  }, [f, ready])

  const coreIds = useMemo(
    () => new Set(companies.filter((c) => c.core).map((c) => c.id)),
    [companies]
  )
  const companyById = useMemo(() => new Map(companies.map((c) => [c.id, c])), [companies])

  // Pull the selected company's map if it isn't one of the six we ship inline.
  useEffect(() => {
    const id = f.company
    if (!id || coreIds.has(id) || extra[id]) return
    setLoading(true)
    fetch(`${base}/data/companies/${id}.json`)
      .then((r) => (r.ok ? r.json() : {}))
      .then((data) => setExtra((prev) => ({ ...prev, [id]: data })))
      .catch(() => setExtra((prev) => ({ ...prev, [id]: {} })))
      .finally(() => setLoading(false))
  }, [f.company, coreIds, extra, base])

  /** Frequency of `problem` at the selected company in the selected window. */
  const frequencyOf = useCallback(
    (p: ExplorerProblem): number | null => {
      if (!f.company) return null
      if (coreIds.has(f.company)) return p.companies[f.company]?.[f.window] ?? null
      return extra[f.company]?.[p.slug]?.[f.window] ?? null
    },
    [f.company, f.window, coreIds, extra]
  )

  const rows = useMemo(() => {
    const q = f.q.trim().toLowerCase()
    const out: { p: ExplorerProblem; frequency: number | null }[] = []
    for (const p of problems) {
      if (q && !p.title.toLowerCase().includes(q) && !p.slug.includes(q) && String(p.id) !== q)
        continue
      if (f.difficulty.length && !f.difficulty.includes(p.difficulty)) continue
      if (f.pattern && p.pattern !== f.pattern) continue
      if (f.hidePremium && p.premium) continue
      if (f.hideDone && done.has(p.slug)) continue
      if (f.list === 'blind75' && !p.blind75) continue
      if (f.list === 'nc150' && !p.nc150) continue
      if (f.list === 'curated' && !p.curated) continue

      const frequency = frequencyOf(p)
      if (f.company && frequency === null) continue
      if (f.minFrequency && (frequency ?? p.heat) < f.minFrequency) continue
      out.push({ p, frequency })
    }
    out.sort((a, b) => (b.frequency ?? b.p.heat) - (a.frequency ?? a.p.heat) || a.p.id - b.p.id)
    return out
  }, [problems, f, frequencyOf, done])

  const companyOptions = useMemo(() => {
    const q = companyQuery.trim().toLowerCase()
    return companies.filter((c) => !q || c.name.toLowerCase().includes(q)).slice(0, 60)
  }, [companies, companyQuery])

  const set = <K extends keyof Filters>(key: K, value: Filters[K]) =>
    setF((prev) => ({ ...prev, [key]: value }))

  const selected = f.company ? companyById.get(f.company) : null

  return (
    <div className="grid gap-8 py-8 lg:grid-cols-[16rem_minmax(0,1fr)]">
      {/* ---------------------------------------------------------- filters */}
      <aside className="lg:sticky lg:top-20 lg:self-start">
        <h2 className="sr-only">Filters</h2>
        <div className="space-y-5">
          <div>
            <label
              htmlFor="q"
              className="text-ink-faint mb-1.5 block text-[11px] tracking-[0.14em] uppercase"
            >
              Search
            </label>
            <input
              id="q"
              type="search"
              value={f.q}
              onChange={(e) => set('q', e.target.value)}
              placeholder="Title, slug or number"
              className="border-line bg-bg-raised placeholder:text-ink-faint w-full rounded-chip border px-3 py-2 text-[13px]"
            />
          </div>

          <fieldset>
            <legend className="text-ink-faint mb-1.5 text-[11px] tracking-[0.14em] uppercase">
              Difficulty
            </legend>
            <div className="flex gap-1.5">
              {DIFFICULTIES.map((d) => {
                const on = f.difficulty.includes(d)
                return (
                  <button
                    key={d}
                    type="button"
                    aria-pressed={on}
                    onClick={() =>
                      set(
                        'difficulty',
                        on ? f.difficulty.filter((x) => x !== d) : [...f.difficulty, d]
                      )
                    }
                    className={`rounded-chip border px-2.5 py-1.5 text-[12px] transition-colors ${
                      on ? 'border-ink bg-ink text-bg' : 'border-line text-ink-muted hover:text-ink'
                    }`}
                  >
                    {d}
                  </button>
                )
              })}
            </div>
          </fieldset>

          <div>
            <label
              htmlFor="pattern"
              className="text-ink-faint mb-1.5 block text-[11px] tracking-[0.14em] uppercase"
            >
              Pattern
            </label>
            <select
              id="pattern"
              value={f.pattern}
              onChange={(e) => set('pattern', e.target.value)}
              className="border-line bg-bg-raised w-full rounded-chip border px-3 py-2 text-[13px]"
            >
              <option value="">All patterns</option>
              {PATTERNS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Combobox over all 659 — a native select with 659 options is unusable. */}
          <div className="relative">
            <label
              htmlFor="company"
              className="text-ink-faint mb-1.5 block text-[11px] tracking-[0.14em] uppercase"
            >
              Company
            </label>
            {selected ? (
              <div className="border-line bg-bg-raised flex items-center gap-2 rounded-chip border px-3 py-2">
                <Mark logo={logos[selected.id] ?? { hex: '888' }} name={selected.name} />
                <span className="flex-1 truncate text-[13px]">{selected.name}</span>
                <button
                  type="button"
                  onClick={() => {
                    set('company', '')
                    setCompanyQuery('')
                  }}
                  className="text-ink-faint hover:text-ink text-[16px] leading-none"
                  aria-label="Clear company filter"
                >
                  ×
                </button>
              </div>
            ) : (
              <input
                id="company"
                type="text"
                role="combobox"
                aria-expanded={companyOpen}
                aria-controls="company-list"
                autoComplete="off"
                value={companyQuery}
                onChange={(e) => {
                  setCompanyQuery(e.target.value)
                  setCompanyOpen(true)
                }}
                onFocus={() => setCompanyOpen(true)}
                onBlur={() => setTimeout(() => setCompanyOpen(false), 150)}
                placeholder={`Any of ${companies.length}`}
                className="border-line bg-bg-raised placeholder:text-ink-faint w-full rounded-chip border px-3 py-2 text-[13px]"
              />
            )}
            {/* A listbox must not be a <ul>: the list semantics fight the
                option semantics, and screen readers announce the wrong count. */}
            {companyOpen && !selected && (
              <div
                id="company-list"
                role="listbox"
                aria-label="Companies"
                className="border-line bg-bg-raised absolute z-20 mt-1 max-h-72 w-full overflow-auto rounded-chip border py-1 shadow-xl"
              >
                {companyOptions.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    role="option"
                    aria-selected={false}
                    onMouseDown={() => {
                      set('company', c.id)
                      setCompanyOpen(false)
                    }}
                    className="hover:bg-bg-sunken flex w-full items-center gap-2 px-3 py-1.5 text-left text-[13px]"
                  >
                    <Mark logo={logos[c.id] ?? { hex: '888' }} name={c.name} />
                    <span className="flex-1 truncate">{c.name}</span>
                    <span className="tabular text-ink-faint text-[11px]">{c.recent}</span>
                  </button>
                ))}
                {!companyOptions.length && (
                  <p className="text-ink-faint px-3 py-2 text-[12px]">No company matches.</p>
                )}
              </div>
            )}
          </div>

          <div>
            <label
              htmlFor="window"
              className="text-ink-faint mb-1.5 block text-[11px] tracking-[0.14em] uppercase"
            >
              Window
            </label>
            <select
              id="window"
              value={f.window}
              onChange={(e) => set('window', Number(e.target.value))}
              className="border-line bg-bg-raised w-full rounded-chip border px-3 py-2 text-[13px]"
            >
              {WINDOW_LABELS.map((label, i) => (
                <option key={label} value={i}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="freq"
              className="text-ink-faint mb-1.5 flex justify-between text-[11px] tracking-[0.14em] uppercase"
            >
              <span>Min frequency</span>
              <span className="tabular">{f.minFrequency}%</span>
            </label>
            <input
              id="freq"
              type="range"
              min={0}
              max={100}
              step={5}
              value={f.minFrequency}
              onChange={(e) => set('minFrequency', Number(e.target.value))}
              className="accent-onlogn w-full"
            />
          </div>

          <div>
            <label
              htmlFor="list"
              className="text-ink-faint mb-1.5 block text-[11px] tracking-[0.14em] uppercase"
            >
              List
            </label>
            <select
              id="list"
              value={f.list}
              onChange={(e) => set('list', e.target.value as Filters['list'])}
              className="border-line bg-bg-raised w-full rounded-chip border px-3 py-2 text-[13px]"
            >
              <option value="">Everything</option>
              <option value="curated">In the catalogue</option>
              <option value="blind75">Blind 75</option>
              <option value="nc150">NeetCode 150</option>
            </select>
          </div>

          <div className="space-y-2 text-[13px]">
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="checkbox"
                checked={f.hidePremium}
                onChange={(e) => set('hidePremium', e.target.checked)}
                className="accent-onlogn h-3.5 w-3.5"
              />
              <span className="text-ink-muted">Hide premium-only</span>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="checkbox"
                checked={f.hideDone}
                onChange={(e) => set('hideDone', e.target.checked)}
                className="accent-onlogn h-3.5 w-3.5"
              />
              <span className="text-ink-muted">Hide what I've done</span>
            </label>
          </div>

          <button
            type="button"
            onClick={() => {
              setF(DEFAULTS)
              setCompanyQuery('')
            }}
            className="border-line text-ink-muted hover:text-ink w-full rounded-chip border px-3 py-2 text-[12px] transition-colors"
          >
            Reset filters
          </button>
        </div>
      </aside>

      {/* ------------------------------------------------------------ table */}
      <div className="min-w-0">
        <p className="text-ink-muted mb-3 text-[13px]" aria-live="polite">
          <span className="tabular text-ink font-semibold">{rows.length.toLocaleString()}</span>{' '}
          {rows.length === 1 ? 'problem' : 'problems'}
          {selected && <> asked at {selected.name}</>}
          {loading && <span className="text-ink-faint"> · loading…</span>}
        </p>

        <div className="border-line-soft rounded-card overflow-x-auto border">
          <table className="w-full border-collapse text-left text-[13px]">
            <caption className="sr-only">Filtered problems</caption>
            {/* Not sticky: the scroll container clips it, which parks the header
                on top of the first row instead of above it. */}
            <thead className="bg-bg-raised text-ink-faint text-[11px] tracking-wide uppercase">
              <tr className="border-line-soft border-b">
                <th scope="col" className="w-9 py-2 pl-4">
                  <span className="sr-only">Done</span>
                </th>
                <th scope="col" className="py-2">
                  Problem
                </th>
                <th scope="col" className="w-20 py-2">
                  Difficulty
                </th>
                <th scope="col" className="py-2">
                  Pattern
                </th>
                <th scope="col" className="w-20 py-2 text-right">
                  {selected ? 'Freq' : 'Peak'}
                </th>
                <th scope="col" className="w-16 py-2 pr-4 text-right">
                  Link
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, limit).map(({ p, frequency }) => (
                <tr
                  key={p.slug}
                  className="border-line-soft hover:bg-bg-raised/60 border-b transition-colors last:border-b-0"
                >
                  <td className="py-2 pl-4">
                    <input
                      type="checkbox"
                      checked={done.has(p.slug)}
                      onChange={(e) => setDone(new Set(toggle(p.slug, e.target.checked)))}
                      className="accent-onlogn h-3.5 w-3.5 cursor-pointer"
                      aria-label={`Mark ${p.title} as done`}
                    />
                  </td>
                  <td className="py-2 pr-3">
                    <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
                      <span className="tabular text-ink-faint text-[11px]">{p.id}</span>
                      <a
                        href={`https://leetcode.com/problems/${p.slug}/`}
                        rel="noopener"
                        className="hover:text-onlogn text-ink-muted"
                      >
                        {p.title}
                      </a>
                      {p.blind75 && (
                        <span className="border-line text-ink-faint rounded-[3px] border px-1 text-[10px]">
                          B75
                        </span>
                      )}
                      {p.nc150 && (
                        <span className="border-line text-ink-faint rounded-[3px] border px-1 text-[10px]">
                          NC150
                        </span>
                      )}
                      {p.premium && (
                        <span className="border-on2/40 text-on2 rounded-[3px] border px-1 text-[10px]">
                          Premium
                        </span>
                      )}
                    </span>
                  </td>
                  <td className="py-2">
                    {/* The meter is decorative; the difficulty is announced by
                        the visually-hidden text so it reads once, not twice. */}
                    <span
                      className="flex items-end gap-[2px]"
                      title={p.difficulty}
                      aria-hidden="true"
                    >
                      {[1, 2, 3].map((step) => (
                        <span
                          key={step}
                          className={`w-[3px] rounded-[1px] ${step <= { Easy: 1, Medium: 2, Hard: 3 }[p.difficulty] ? 'bg-ink' : 'bg-line'}`}
                          style={{ height: 4 + step * 3 }}
                        />
                      ))}
                    </span>
                    <span className="sr-only">{p.difficulty}</span>
                  </td>
                  <td className="text-ink-faint py-2 text-[12px]">
                    {p.pattern ? (
                      <a href={`${base}/patterns/${p.pattern}/`} className="hover:text-ink">
                        {PATTERN_NAME.get(p.pattern) ?? p.pattern}
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="tabular text-ink-muted py-2 text-right text-[12px]">
                    {(frequency ?? p.heat) ? `${Math.round(frequency ?? p.heat)}%` : '—'}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    <a
                      href={`https://leetcode.com/problems/${p.slug}/`}
                      rel="noopener"
                      className="text-ink-faint hover:text-ink text-[11px]"
                    >
                      LC
                    </a>
                  </td>
                </tr>
              ))}
              {!rows.length && (
                <tr>
                  <td colSpan={6} className="text-ink-faint px-4 py-10 text-center text-[13px]">
                    Nothing matches. Widen the window, drop the frequency floor, or reset.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {limit < rows.length && (
          <button
            type="button"
            onClick={() => setLimit((n) => n + PAGE_SIZE * 4)}
            className="border-line text-ink-muted hover:text-ink mt-4 w-full rounded-chip border py-2.5 text-[13px] transition-colors"
          >
            Show more — {(rows.length - limit).toLocaleString()} remaining
          </button>
        )}
      </div>
    </div>
  )
}
