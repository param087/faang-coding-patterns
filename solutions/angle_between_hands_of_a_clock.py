"""Angle Between Hands of a Clock — LeetCode 1344."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "The hour hand moves continuously at 0.5° per minute; forgetting that, or forgetting the reflex angle, is the whole problem.",
    "time": "O(1)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Given an hour (1–12) and a minute (0–59), return the **smaller** angle between
the two hands, in degrees.

Two things to pin down before writing anything: the answer is accepted within
1e-5, so a float is fine; and "smaller angle" means you always return something
in `[0, 180]`, never the reflex side.

This turns up as a warm-up or a phone-screen filler. It is thirty seconds of
work and there are exactly two ways to get it wrong, so the value is in naming
both before the interviewer finds them.
""",
        ),
        (
            "The insight",
            """
Convert both hands to an absolute angle from 12 o'clock and subtract.

- **Minute hand**: a full 360° in 60 minutes → `6 · minutes`.
- **Hour hand**: 360° in 12 hours → 30° per hour, *plus* 30/60 = **0.5° per
  minute**, because the hour hand does not jump between hours. At 3:30 it sits
  at 105°, not 90°.

That trailing `0.5 · minutes` is the entire question. Drop it and 3:30 reports
90 instead of 75 — and that is LeetCode's own first example, chosen precisely
to catch it.

The other half is the wrap: `abs(hour_angle - minute_angle)` can exceed 180
(at 1:57 it is 283.5°), so return `min(diff, 360 - diff)`.
""",
        ),
        (
            "Edge cases",
            """
- **Hour 12.** The input uses 12, not 0, so `hour % 12` before multiplying by
  30. Without it, 12:00 gives 360° and — after the reflex fix — still returns
  0, which hides the bug; but 12:30 gives `360 + 15 = 375` against a minute
  hand at 180, `diff = 195`, `min(195, 165) = 165`. It happens to survive
  because the reflex correction is modular. Write `% 12` anyway: relying on two
  bugs cancelling is not an answer you want to defend.
- **6:00** is the maximum, 180°, and `min(180, 180)` is the boundary of the
  reflex rule.
- **Floating point.** Every quantity here is a multiple of 0.5, which is exact
  in binary floating point, so `==` comparisons in tests are safe and no
  epsilon is needed. If you would rather not argue that, work in half-degrees
  as integers (`12 · minutes` vs `60 · hour + minutes`) and halve at the end.
- **Ranges.** Nothing to validate — the constraints guarantee 1 ≤ hour ≤ 12 and
  0 ≤ minutes ≤ 59. Say so rather than writing dead guard clauses.
""",
        ),
    ],
}


def angle_clock(hour: int, minutes: int) -> float:
    minute_angle = 6.0 * minutes  # 360 / 60
    hour_angle = (hour % 12) * 30.0 + 0.5 * minutes  # 360 / 12, plus the drift

    difference = abs(hour_angle - minute_angle)
    return min(difference, 360.0 - difference)  # never the reflex angle


CASES = [
    ((12, 30), 165.0),
    ((3, 30), 75.0),  # 90 if you forget the hour hand drifts
    ((3, 15), 7.5),
    ((4, 50), 155.0),
    ((12, 0), 0.0),
    ((6, 0), 180.0),  # the maximum
    ((1, 57), 76.5),  # raw difference is 283.5 — needs the reflex fix
    ((9, 0), 90.0),
]


def solve(hour: int, minutes: int) -> float:
    return angle_clock(hour, minutes)
