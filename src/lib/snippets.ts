/**
 * Read Python source off disk at build time.
 *
 * Code is never pasted into MDX. Every snippet on the site is sliced out of a
 * module in `code/` or `solutions/` that pytest actually runs, so a page
 * cannot drift away from working code — if the module breaks, the gate fails
 * before the page ships.
 */
import { readFileSync } from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(process.cwd())

export interface SnippetOptions {
  /** Repo-relative path, e.g. `code/monotonic_stack.py`. */
  file: string
  /** Top-level `def` or `class` to extract. Omit for the whole file. */
  symbol?: string
  /** Drop the module docstring — pages usually supply their own prose. */
  stripDocstring?: boolean
}

/**
 * Slice one top-level definition, including any decorators above it and the
 * blank lines inside it, stopping at the next top-level statement.
 */
function extractSymbol(source: string, symbol: string, file: string): string {
  const lines = source.split('\n')
  const header = new RegExp(`^(def|class|async def)\\s+${symbol}\\b`)

  let start = lines.findIndex((line) => header.test(line))
  if (start === -1) throw new Error(`Snippet: no top-level "${symbol}" in ${file}`)

  // Walk back over decorators attached to the definition.
  while (start > 0 && (lines[start - 1] ?? '').startsWith('@')) start--

  let end = lines.length
  for (let i = start + 1; i < lines.length; i++) {
    const line = lines[i] ?? ''
    // A non-blank line at column zero ends the definition.
    if (line.trim() !== '' && !/^\s/.test(line)) {
      end = i
      break
    }
  }

  // Trim trailing blank lines the lookahead swept up.
  while (end > start && (lines[end - 1] ?? '').trim() === '') end--
  return lines.slice(start, end).join('\n')
}

/** Remove a leading module docstring and the blank lines after it. */
function stripModuleDocstring(source: string): string {
  const match = /^(?:from __future__[^\n]*\n+)?("""|''')/.exec(source)
  if (!match) return source
  const quote = match[1] as string
  const open = source.indexOf(quote)
  const close = source.indexOf(quote, open + quote.length)
  if (close === -1) return source
  return source.slice(close + quote.length).replace(/^\n+/, '')
}

export function snippet({ file, symbol, stripDocstring = false }: SnippetOptions): string {
  const source = readFileSync(path.join(ROOT, file), 'utf8')
  if (symbol) return extractSymbol(source, symbol, file)
  const body = stripDocstring ? stripModuleDocstring(source) : source
  // Test scaffolding belongs in the repo, not on the page.
  return body.split(/\n(?=CASES = |def check\(\) -> None:)/)[0]?.trimEnd() ?? body.trimEnd()
}
