/**
 * Resolve a brand mark for every company and vendor it into the repo.
 *
 *   npx tsx scripts/fetch-logos.ts [--refresh]
 *
 * Emits `src/data/generated/logos.json`: company id -> { hex, path } where
 * `path` is the single SVG path string of the mark, or nothing when we fall
 * back to a monogram. Paths are inlined rather than written as files so a
 * chip costs no extra request and can be recoloured with `fill`.
 *
 * Resolution order, strictest first — a monogram is always better than a
 * confidently wrong logo, so we never guess:
 *   1. BRANDS[id].icon        explicit, hand-checked
 *   2. slug guess == id       exact match only ("zoho" -> siZoho)
 *   3. monogram               initials on a deterministic hue
 */

import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { BRANDS, SIMPLE_ICONS_VERSIONS } from './logo-map.ts'

const ROOT = path.resolve(import.meta.dirname, '..')
const GEN = path.join(ROOT, 'src', 'data', 'generated')
const CACHE = path.join(ROOT, 'data', 'raw', 'icons')
const REFRESH = process.argv.includes('--refresh')

export interface LogoRecord {
  /** Brand hex without `#`. Always present — monograms use it too. */
  hex: string
  /**
   * Substitute hex for the dark theme, present only when the brand mark is
   * near-black (Apple, Uber, Bloomberg…) and would otherwise disappear
   * against the ink canvas. These brands render their mark in white on dark
   * backgrounds anyway, so this matches real usage rather than fighting it.
   */
  hexDark?: string
  /** SVG path data for a 24x24 viewBox. Absent ⇒ render a monogram. */
  path?: string
}

/** WCAG relative luminance, used only to decide "is this mark too dark to see". */
function luminance(hex: string): number {
  const channel = (i: number) => {
    const v = Number.parseInt(hex.slice(i, i + 2), 16) / 255
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * channel(0) + 0.7152 * channel(2) + 0.0722 * channel(4)
}

/** Near-white; what these brands use on a dark background themselves. */
const DARK_THEME_SUBSTITUTE = 'E8E9ED'

/** Stable hue from a name, so monogram companies keep the same colour forever. */
function monogramHex(id: string): string {
  let h = 0
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0
  const hue = h % 360
  // Fixed S/L keeps every monogram at comparable weight against the dark canvas.
  const [r, g, b] = hslToRgb(hue / 360, 0.55, 0.55)
  return [r, g, b]
    .map((v) => v.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase()
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const k = (n: number) => (n + h * 12) % 12
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => Math.round(255 * (l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1))))
  return [f(0), f(8), f(4)]
}

/** Pull one icon's SVG, walking the version ladder for marks 16.x dropped. */
async function fetchIcon(slug: string): Promise<string | null> {
  const cached = path.join(CACHE, `${slug}.svg`)
  if (existsSync(cached) && !REFRESH) return readFile(cached, 'utf8')

  for (const version of SIMPLE_ICONS_VERSIONS) {
    const url = `https://cdn.jsdelivr.net/npm/simple-icons@${version}/icons/${slug}.svg`
    const res = await fetch(url).catch(() => null)
    if (!res?.ok) continue
    const svg = await res.text()
    if (!svg.startsWith('<svg')) continue
    await writeFile(cached, svg)
    return svg
  }
  return null
}

/** simple-icons SVGs are exactly one `<path d="…">`; that string is all we need. */
function extractPath(svg: string): string | null {
  return /\sd="([^"]+)"/.exec(svg)?.[1] ?? null
}

async function main() {
  await mkdir(CACHE, { recursive: true })
  await mkdir(GEN, { recursive: true })

  const directory = JSON.parse(await readFile(path.join(GEN, 'companies.json'), 'utf8')) as {
    id: string
    name: string
  }[]

  // The current package is the source of truth for hexes it still carries.
  const si = (await import('simple-icons')) as unknown as Record<
    string,
    { title: string; hex: string; path: string } | undefined
  >
  const exportName = (slug: string) =>
    `si${slug
      .split('-')
      .map((w) => (w[0] ?? '').toUpperCase() + w.slice(1))
      .join('')}`

  const logos: Record<string, LogoRecord> = {}
  let withMark = 0

  for (const { id } of directory) {
    const brand = BRANDS[id]
    // Only an explicit entry or an exact slug match — never a fuzzy guess.
    const slug = brand?.icon ?? (si[exportName(id)] ? id : null)
    const pkg = slug ? si[exportName(slug)] : undefined
    const hex = brand?.hex ?? pkg?.hex ?? monogramHex(id)

    let d: string | null = pkg?.path ?? null
    if (!d && slug) d = await fetchIcon(slug).then((svg) => (svg ? extractPath(svg) : null))

    const record: LogoRecord = { hex }
    if (luminance(hex) < 0.06) record.hexDark = DARK_THEME_SUBSTITUTE
    if (d) {
      record.path = d
      withMark++
    }
    logos[id] = record
  }

  await writeFile(path.join(GEN, 'logos.json'), JSON.stringify(logos))
  console.log(`logos     ${directory.length} companies`)
  console.log(`  mark    ${withMark}`)
  console.log(`  monogram ${directory.length - withMark}`)

  const missingCore = ['google', 'meta', 'amazon', 'microsoft', 'apple', 'netflix'].filter(
    (id) => !logos[id]?.path
  )
  if (missingCore.length) {
    console.error(`FAIL: core companies without a mark: ${missingCore.join(', ')}`)
    process.exit(1)
  }
}

await main()
