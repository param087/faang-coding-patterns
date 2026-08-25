/**
 * The constraint instrument — the site's signature.
 *
 * The move that separates an SDE-2 from a candidate who has memorised a list
 * is reading the constraint block *first*: `n <= 20` means find the bitmask,
 * `n <= 10^5` means stop hunting for a clever quadratic. This is that reflex
 * as an instrument. Pick a bound, see which complexity classes still fit in
 * the ~10^8-operation budget, and which of the 39 patterns live there.
 *
 * It is also the navigation: selecting a class filters the pattern grid below.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  COMPLEXITY_CLASSES,
  CONSTRAINT_STOPS,
  type ComplexityId,
  isFeasible,
  OPS_BUDGET,
} from '../lib/complexity.ts'

interface Props {
  /** Pattern names per complexity class, so the instrument can name the payoff. */
  patternsByComplexity: Record<string, string[]>
}

/** `1.3e+7` is unreadable at a glance; `13M` is not. */
function formatOps(value: number): string {
  if (value >= 1e15) return '10¹⁵+'
  if (value >= 1e12) return `${(value / 1e12).toFixed(value < 1e13 ? 1 : 0)}T`
  if (value >= 1e9) return `${(value / 1e9).toFixed(value < 1e10 ? 1 : 0)}B`
  if (value >= 1e6) return `${(value / 1e6).toFixed(value < 1e7 ? 1 : 0)}M`
  if (value >= 1e3) return `${(value / 1e3).toFixed(value < 1e4 ? 1 : 0)}K`
  return String(Math.max(1, Math.round(value)))
}

export default function ConstraintInstrument({ patternsByComplexity }: Props) {
  // Default to n ≤ 10^5: by a wide margin the most common bound in the set.
  const [stopIndex, setStopIndex] = useState(5)
  const stop = CONSTRAINT_STOPS[stopIndex] ?? CONSTRAINT_STOPS[5]
  const n = stop?.n ?? 100000

  const rows = useMemo(
    () =>
      COMPLEXITY_CLASSES.map((cls) => ({
        cls,
        ops: cls.ops(n),
        fits: isFeasible(cls, n),
        patterns: patternsByComplexity[cls.id] ?? [],
      })),
    [n, patternsByComplexity]
  )
  const target = [...rows].reverse().find((r) => r.fits)

  /** Broadcast to the pattern grid, which filters itself without a framework. */
  const emit = useCallback((id: ComplexityId | null) => {
    document.dispatchEvent(new CustomEvent('complexity:select', { detail: id }))
  }, [])

  useEffect(() => () => emit(null), [emit])

  return (
    <div className="border-line bg-bg-raised/70 rounded-card overflow-hidden border backdrop-blur">
      <div className="border-line-soft flex items-baseline justify-between gap-4 border-b px-5 py-3">
        <label
          htmlFor="constraint"
          className="text-ink-muted text-[11px] tracking-[0.14em] uppercase"
        >
          Constraint
        </label>
        <output className="tabular text-ink text-lg font-semibold" htmlFor="constraint">
          {stop?.written}
        </output>
      </div>

      <div className="px-5 pt-4">
        <input
          id="constraint"
          type="range"
          min={0}
          max={CONSTRAINT_STOPS.length - 1}
          step={1}
          value={stopIndex}
          onChange={(e) => setStopIndex(Number(e.target.value))}
          aria-valuetext={`${stop?.written}. ${stop?.tell}`}
          className="accent-onlogn w-full cursor-pointer"
        />
        <p className="text-ink-muted mt-3 min-h-[2.5rem] text-[13px] leading-relaxed">
          {stop?.tell}
        </p>
      </div>

      <table className="w-full border-collapse text-left">
        <caption className="sr-only">
          Which complexity classes fit within {formatOps(OPS_BUDGET)} operations at {stop?.written}
        </caption>
        <thead className="sr-only">
          <tr>
            <th scope="col">Complexity</th>
            <th scope="col">Operations</th>
            <th scope="col">Verdict</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ cls, ops, fits, patterns }) => (
            <tr
              key={cls.id}
              className="border-line-soft hover:bg-bg-sunken/60 group cursor-pointer border-t transition-colors"
              onMouseEnter={() => fits && emit(cls.id)}
              onMouseLeave={() => emit(null)}
              onFocus={() => fits && emit(cls.id)}
              onBlur={() => emit(null)}
              tabIndex={0}
            >
              <th
                scope="row"
                className="tabular w-[7.5rem] py-2.5 pl-5 text-[13px] font-medium"
                style={{ color: fits ? `var(--color-${cls.id})` : 'var(--color-ink-faint)' }}
              >
                {cls.label}
              </th>
              <td className="tabular text-ink-faint py-2.5 text-[12px]">{formatOps(ops)} ops</td>
              <td className="py-2.5 pr-5 text-right text-[12px]">
                {fits ? (
                  <span className="text-ink-muted">
                    {patterns.length} {patterns.length === 1 ? 'pattern' : 'patterns'}
                  </span>
                ) : (
                  <span className="text-ink-faint">too slow</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="border-line-soft text-ink-faint border-t px-5 py-3 text-[12px] leading-relaxed">
        Aim for{' '}
        <span className="tabular font-medium" style={{ color: `var(--color-${target?.cls.id})` }}>
          {target?.cls.label}
        </span>{' '}
        or better. Budget is {formatOps(OPS_BUDGET)} operations — roughly one second.
      </p>
    </div>
  )
}
