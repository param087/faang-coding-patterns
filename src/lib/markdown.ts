/**
 * A very small markdown renderer for solution prose.
 *
 * Solution text lives inside Python docstrings, not MDX, so it never reaches
 * Astro's markdown pipeline. It only needs the handful of constructs the
 * prose actually uses — paragraphs, lists, bold, italic, inline code and
 * fenced blocks — so a targeted renderer beats pulling in a parser.
 *
 * Input is authored by us, never user-supplied, but HTML is still escaped
 * first so a `<` in a complexity bound cannot break the page.
 */

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/**
 * Inline: `code`, **bold**, *italic*.
 *
 * Code spans are lifted out first and replaced with a sentinel, so their
 * contents are never treated as emphasis — otherwise `a*b` inside backticks
 * would become italics. The sentinel uses private-use-area characters, which
 * cannot occur in the prose.
 */
const OPEN = '\uE000'
const CLOSE = '\uE001'

function inline(text: string): string {
  const codes: string[] = []
  let out = text.replace(/`([^`]+)`/g, (_, code: string) => {
    codes.push(code)
    return `${OPEN}${codes.length - 1}${CLOSE}`
  })

  out = escapeHtml(out)
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  out = out.replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')

  return out.replace(new RegExp(`${OPEN}(\\d+)${CLOSE}`, 'g'), (_, index: string) => {
    const code = codes[Number(index)] ?? ''
    return `<code>${escapeHtml(code)}</code>`
  })
}

export function markdownToHtml(markdown: string): string {
  const lines = markdown.split('\n')
  const html: string[] = []
  let paragraph: string[] = []
  let list: string[] = []
  let fence: string[] | null = null

  const flushParagraph = () => {
    if (paragraph.length) {
      html.push(`<p>${inline(paragraph.join(' '))}</p>`)
      paragraph = []
    }
  }
  const flushList = () => {
    if (list.length) {
      html.push(`<ul>${list.map((item) => `<li>${inline(item)}</li>`).join('')}</ul>`)
      list = []
    }
  }

  for (const raw of lines) {
    const line = raw.trimEnd()

    if (line.trimStart().startsWith('```')) {
      if (fence === null) {
        flushParagraph()
        flushList()
        fence = []
      } else {
        html.push(`<pre><code>${escapeHtml(fence.join('\n'))}</code></pre>`)
        fence = null
      }
      continue
    }
    if (fence !== null) {
      fence.push(raw)
      continue
    }

    if (!line.trim()) {
      flushParagraph()
      flushList()
      continue
    }

    const bullet = /^\s*[-*]\s+(.*)$/.exec(line)
    if (bullet?.[1]) {
      flushParagraph()
      list.push(bullet[1])
      continue
    }

    // A non-bullet line while a list is open is a *continuation* of the last
    // item — the prose is hard-wrapped, so bullets routinely span several
    // lines. Closing the list here would push the tail out as its own
    // paragraph, unindented and visually detached from its bullet.
    if (list.length && !paragraph.length) {
      list[list.length - 1] = `${list[list.length - 1]} ${line.trim()}`
      continue
    }

    flushList()
    paragraph.push(line.trim())
  }

  flushParagraph()
  flushList()
  if (fence !== null) html.push(`<pre><code>${escapeHtml(fence.join('\n'))}</code></pre>`)

  return html.join('\n')
}
