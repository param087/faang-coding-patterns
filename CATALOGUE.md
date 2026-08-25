# CATALOGUE

The hand-curated half of the index. Auto-classification from LeetCode tags is
good enough for the long tail, but it cannot know that Basic Calculator is
String Parsing rather than Stack, or that Word Break is 1-D DP rather than
Tries. Everything this site actually *recommends* is assigned here, and the
catalogue always beats the classifier.

Parsed by `scripts/catalogue.ts`. One `##` section per pattern id, three lists:

- `core` — the must-do set, in teaching order (easiest first, ≥ 8 per pattern)
- `stretch` — worth doing once core is solid
- `anchors` — the problems that get a full live-solve walkthrough on the pattern
  page (≥ 2, must be drawn from core or stretch)

Slugs are LeetCode `titleSlug` values. `npm run data:build` fails if a slug
here does not exist upstream, so typos cannot reach the site.

---

## arrays-hashing
- core: two-sum, contains-duplicate, valid-anagram, group-anagrams, top-k-frequent-elements, product-of-array-except-self, valid-sudoku, longest-consecutive-sequence, subarray-sum-equals-k, majority-element
- stretch: encode-and-decode-strings, first-missing-positive, insert-delete-getrandom-o1, 4sum-ii, find-all-anagrams-in-a-string, isomorphic-strings, word-pattern, longest-palindrome
- anchors: two-sum, longest-consecutive-sequence, product-of-array-except-self

## prefix-sums
- core: running-sum-of-1d-array, find-pivot-index, range-sum-query-immutable, subarray-sum-equals-k, contiguous-array, continuous-subarray-sum, subarray-sums-divisible-by-k, range-sum-query-2d-immutable, corporate-flight-bookings
- stretch: maximum-size-subarray-sum-equals-k, number-of-submatrices-that-sum-to-target, matrix-block-sum, car-pooling, product-of-array-except-self, count-number-of-nice-subarrays, path-sum-iii
- anchors: subarray-sum-equals-k, contiguous-array, range-sum-query-2d-immutable

## two-pointers
- core: valid-palindrome, two-sum-ii-input-array-is-sorted, 3sum, container-with-most-water, remove-duplicates-from-sorted-array, move-zeroes, sort-colors, trapping-rain-water, merge-sorted-array
- stretch: 4sum, boats-to-save-people, next-permutation, is-subsequence, squares-of-a-sorted-array, partition-labels, shortest-unsorted-continuous-subarray, valid-palindrome-ii
- anchors: 3sum, container-with-most-water, sort-colors

## sliding-window
- core: best-time-to-buy-and-sell-stock, longest-substring-without-repeating-characters, longest-repeating-character-replacement, permutation-in-string, max-consecutive-ones-iii, minimum-size-subarray-sum, fruit-into-baskets, minimum-window-substring, substring-with-concatenation-of-all-words
- stretch: sliding-window-maximum, longest-subarray-of-1s-after-deleting-one-element, subarrays-with-k-different-integers, maximum-points-you-can-obtain-from-cards, count-number-of-nice-subarrays, minimum-number-of-k-consecutive-bit-flips, longest-substring-with-at-most-k-distinct-characters
- anchors: longest-substring-without-repeating-characters, minimum-window-substring, subarrays-with-k-different-integers

## sorting
- core: merge-sorted-array, sort-colors, largest-number, meeting-rooms-ii, h-index, sort-characters-by-frequency, custom-sort-string, relative-sort-array, sort-array-by-parity, wiggle-sort-ii
- stretch: sort-an-array, maximum-gap, pancake-sorting, kth-largest-element-in-an-array, top-k-frequent-words, reorganize-string, queue-reconstruction-by-height
- anchors: largest-number, sort-array-by-parity, wiggle-sort-ii

## intervals
- core: merge-intervals, insert-interval, non-overlapping-intervals, meeting-rooms, meeting-rooms-ii, interval-list-intersections, my-calendar-i, minimum-number-of-arrows-to-burst-balloons, car-pooling
- stretch: employee-free-time, my-calendar-ii, my-calendar-iii, the-skyline-problem, remove-covered-intervals, data-stream-as-disjoint-intervals, range-module
- anchors: merge-intervals, meeting-rooms-ii, the-skyline-problem

## matrix
- core: rotate-image, spiral-matrix, set-matrix-zeroes, transpose-matrix, valid-sudoku, game-of-life, diagonal-traverse, search-a-2d-matrix, toeplitz-matrix
- stretch: spiral-matrix-ii, rotating-the-box, image-overlap, matrix-diagonal-sum, shift-2d-grid, robot-room-cleaner, design-tic-tac-toe
- anchors: rotate-image, spiral-matrix, set-matrix-zeroes

## string-manipulation
- core: valid-palindrome, longest-common-prefix, string-to-integer-atoi, add-strings, multiply-strings, basic-calculator-ii, decode-string, valid-parenthesis-string, text-justification, string-compression
- stretch: basic-calculator, basic-calculator-iii, integer-to-roman, roman-to-integer, zigzag-conversion, reorganize-string, simplify-path, valid-number, expression-add-operators
- anchors: basic-calculator-ii, decode-string, text-justification

## string-algorithms
- core: find-the-index-of-the-first-occurrence-in-a-string, repeated-substring-pattern, longest-palindromic-substring, palindromic-substrings, shortest-palindrome, longest-happy-prefix, rotate-string, longest-common-prefix, implement-magic-dictionary
- stretch: distinct-echo-substrings, longest-duplicate-substring, string-matching-in-an-array, sum-of-scores-of-built-strings, find-all-anagrams-in-a-string, shortest-palindrome
- anchors: longest-palindromic-substring, shortest-palindrome, longest-happy-prefix

## stack
- core: valid-parentheses, min-stack, evaluate-reverse-polish-notation, baseball-game, remove-all-adjacent-duplicates-in-string, implement-queue-using-stacks, implement-stack-using-queues, simplify-path, asteroid-collision, backspace-string-compare
- stretch: exclusive-time-of-functions, flatten-nested-list-iterator, remove-k-digits, longest-valid-parentheses, decode-string, maximum-frequency-stack, ternary-expression-parser
- anchors: min-stack, evaluate-reverse-polish-notation, asteroid-collision

## monotonic-stack
- core: next-greater-element-i, next-greater-element-ii, daily-temperatures, online-stock-span, remove-k-digits, largest-rectangle-in-histogram, trapping-rain-water, sum-of-subarray-minimums, sliding-window-maximum
- stretch: maximal-rectangle, shortest-unsorted-continuous-subarray, remove-duplicate-letters, 132-pattern, maximum-width-ramp, jump-game-vi, constrained-subsequence-sum, number-of-visible-people-in-a-queue
- anchors: daily-temperatures, largest-rectangle-in-histogram, sliding-window-maximum

## binary-search
- core: binary-search, search-insert-position, first-bad-version, find-first-and-last-position-of-element-in-sorted-array, search-in-rotated-sorted-array, find-minimum-in-rotated-sorted-array, search-a-2d-matrix, find-peak-element, sqrtx
- stretch: search-in-rotated-sorted-array-ii, median-of-two-sorted-arrays, find-k-closest-elements, single-element-in-a-sorted-array, kth-smallest-element-in-a-sorted-matrix, random-pick-with-weight, time-based-key-value-store
- anchors: search-in-rotated-sorted-array, find-first-and-last-position-of-element-in-sorted-array, median-of-two-sorted-arrays

## binary-search-answer
- core: koko-eating-bananas, capacity-to-ship-packages-within-d-days, split-array-largest-sum, minimum-number-of-days-to-make-m-bouquets, magnetic-force-between-two-balls, find-the-smallest-divisor-given-a-threshold, minimize-max-distance-to-gas-station, maximum-value-at-a-given-index-in-a-bounded-array, kth-smallest-number-in-multiplication-table
- stretch: minimum-time-to-complete-trips, divide-chocolate, minimum-speed-to-arrive-on-time, path-with-minimum-effort, swim-in-rising-water, nth-magical-number, minimize-deviation-in-array
- anchors: koko-eating-bananas, split-array-largest-sum, path-with-minimum-effort

## linked-lists
- core: reverse-linked-list, merge-two-sorted-lists, linked-list-cycle, middle-of-the-linked-list, remove-nth-node-from-end-of-list, palindrome-linked-list, reorder-list, add-two-numbers, odd-even-linked-list, intersection-of-two-linked-lists
- stretch: reverse-nodes-in-k-group, copy-list-with-random-pointer, sort-list, merge-k-sorted-lists, rotate-list, swap-nodes-in-pairs, flatten-a-multilevel-doubly-linked-list, linked-list-cycle-ii, partition-list
- anchors: reverse-linked-list, reorder-list, reverse-nodes-in-k-group

## binary-trees
- core: maximum-depth-of-binary-tree, invert-binary-tree, same-tree, subtree-of-another-tree, balanced-binary-tree, diameter-of-binary-tree, binary-tree-level-order-traversal, path-sum, lowest-common-ancestor-of-a-binary-tree, binary-tree-right-side-view
- stretch: binary-tree-maximum-path-sum, serialize-and-deserialize-binary-tree, construct-binary-tree-from-preorder-and-inorder-traversal, path-sum-ii, flatten-binary-tree-to-linked-list, binary-tree-zigzag-level-order-traversal, count-good-nodes-in-binary-tree, all-nodes-distance-k-in-binary-tree, vertical-order-traversal-of-a-binary-tree
- anchors: diameter-of-binary-tree, lowest-common-ancestor-of-a-binary-tree, binary-tree-maximum-path-sum

## binary-search-trees
- core: search-in-a-binary-search-tree, insert-into-a-binary-search-tree, delete-node-in-a-bst, validate-binary-search-tree, kth-smallest-element-in-a-bst, lowest-common-ancestor-of-a-binary-search-tree, binary-search-tree-iterator, convert-sorted-array-to-binary-search-tree, minimum-absolute-difference-in-bst
- stretch: recover-binary-search-tree, inorder-successor-in-bst, range-sum-of-bst, trim-a-binary-search-tree, closest-binary-search-tree-value, unique-binary-search-trees, serialize-and-deserialize-bst
- anchors: validate-binary-search-tree, kth-smallest-element-in-a-bst, binary-search-tree-iterator

## tries
- core: implement-trie-prefix-tree, design-add-and-search-words-data-structure, word-search-ii, replace-words, longest-word-in-dictionary, map-sum-pairs, search-suggestions-system, index-pairs-of-a-string
- stretch: maximum-xor-of-two-numbers-in-an-array, design-search-autocomplete-system, stream-of-characters, palindrome-pairs, word-break-ii, concatenated-words, prefix-and-suffix-search
- anchors: implement-trie-prefix-tree, word-search-ii, maximum-xor-of-two-numbers-in-an-array

## heaps
- core: kth-largest-element-in-an-array, kth-largest-element-in-a-stream, last-stone-weight, k-closest-points-to-origin, top-k-frequent-elements, merge-k-sorted-lists, task-scheduler, find-median-from-data-stream, meeting-rooms-ii
- stretch: sliding-window-median, ipo, reorganize-string, minimum-cost-to-connect-sticks, find-k-pairs-with-smallest-sums, the-skyline-problem, smallest-range-covering-elements-from-k-lists, design-twitter, single-threaded-cpu
- anchors: k-closest-points-to-origin, find-median-from-data-stream, task-scheduler

## graph-traversal
- core: number-of-islands, flood-fill, max-area-of-island, clone-graph, rotting-oranges, pacific-atlantic-water-flow, surrounded-regions, walls-and-gates, 01-matrix, word-search
- stretch: word-ladder, shortest-bridge, number-of-distinct-islands, open-the-lock, minimum-knight-moves, is-graph-bipartite, jump-game-iii, shortest-path-in-binary-matrix, sliding-puzzle, snakes-and-ladders
- anchors: number-of-islands, rotting-oranges, word-ladder

## topological-sort
- core: course-schedule, course-schedule-ii, find-eventual-safe-states, minimum-height-trees, sequence-reconstruction, all-ancestors-of-a-node-in-a-directed-acyclic-graph, find-all-possible-recipes-from-given-supplies, build-a-matrix-with-conditions
- stretch: alien-dictionary, parallel-courses, parallel-courses-iii, sort-items-by-groups-respecting-dependencies, longest-increasing-path-in-a-matrix, course-schedule-iv
- anchors: course-schedule-ii, alien-dictionary, minimum-height-trees

## union-find
- core: number-of-provinces, redundant-connection, number-of-connected-components-in-an-undirected-graph, graph-valid-tree, accounts-merge, most-stones-removed-with-same-row-or-column, satisfiability-of-equality-equations, longest-consecutive-sequence, number-of-operations-to-make-network-connected
- stretch: swim-in-rising-water, evaluate-division, smallest-string-with-swaps, redundant-connection-ii, number-of-islands-ii, regions-cut-by-slashes, checking-existence-of-edge-length-limited-paths
- anchors: redundant-connection, accounts-merge, number-of-operations-to-make-network-connected

## shortest-paths
- core: network-delay-time, cheapest-flights-within-k-stops, path-with-maximum-probability, path-with-minimum-effort, swim-in-rising-water, the-maze-ii, find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance, minimum-cost-to-make-at-least-one-valid-path-in-a-grid
- stretch: number-of-ways-to-arrive-at-destination, minimum-weighted-subgraph-with-the-required-paths, second-minimum-time-to-reach-destination, reachable-nodes-in-subdivided-graph, bus-routes, shortest-path-visiting-all-nodes
- anchors: network-delay-time, cheapest-flights-within-k-stops, path-with-minimum-effort

## minimum-spanning-tree
- core: min-cost-to-connect-all-points, connecting-cities-with-minimum-cost, optimize-water-distribution-in-a-village, find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree, minimum-cost-to-connect-sticks, path-with-minimum-effort, swim-in-rising-water, number-of-operations-to-make-network-connected
- stretch: checking-existence-of-edge-length-limited-paths, remove-max-number-of-edges-to-keep-graph-fully-traversable, find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree
- anchors: min-cost-to-connect-all-points, find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree

## advanced-graphs
- core: is-graph-bipartite, possible-bipartition, critical-connections-in-a-network, reconstruct-itinerary, evaluate-division, longest-cycle-in-a-graph, find-the-celebrity, minimum-number-of-vertices-to-reach-all-nodes
- stretch: valid-arrangement-of-pairs, maximum-employees-to-be-invited-to-a-meeting, number-of-good-paths, maximum-number-of-accepted-invitations, strange-printer-ii, course-schedule-iv
- anchors: reconstruct-itinerary, critical-connections-in-a-network, is-graph-bipartite

## divide-and-conquer
- core: merge-sorted-array, sort-an-array, kth-largest-element-in-an-array, majority-element, maximum-subarray, convert-sorted-array-to-binary-search-tree, search-a-2d-matrix-ii, k-closest-points-to-origin, construct-binary-tree-from-preorder-and-inorder-traversal
- stretch: median-of-two-sorted-arrays, count-of-smaller-numbers-after-self, reverse-pairs, different-ways-to-add-parentheses, beautiful-array, the-skyline-problem, longest-substring-with-at-least-k-repeating-characters
- anchors: kth-largest-element-in-an-array, count-of-smaller-numbers-after-self, maximum-subarray

## backtracking
- core: subsets, subsets-ii, permutations, permutations-ii, combination-sum, combination-sum-ii, letter-combinations-of-a-phone-number, generate-parentheses, palindrome-partitioning, word-search
- stretch: n-queens, sudoku-solver, restore-ip-addresses, combination-sum-iii, word-break-ii, matchsticks-to-square, partition-to-k-equal-sum-subsets, beautiful-arrangement, expression-add-operators, split-array-into-fibonacci-sequence
- anchors: subsets, combination-sum, n-queens

## greedy
- core: best-time-to-buy-and-sell-stock-ii, jump-game, jump-game-ii, gas-station, assign-cookies, partition-labels, task-scheduler, non-overlapping-intervals, candy, hand-of-straights
- stretch: minimum-number-of-arrows-to-burst-balloons, boats-to-save-people, queue-reconstruction-by-height, reorganize-string, remove-k-digits, wiggle-subsequence, maximum-swap, two-city-scheduling, minimum-deletions-to-make-character-frequencies-unique
- anchors: jump-game-ii, gas-station, candy

## dp-1d
- core: climbing-stairs, min-cost-climbing-stairs, house-robber, house-robber-ii, fibonacci-number, maximum-subarray, word-break, coin-change, longest-increasing-subsequence, decode-ways
- stretch: partition-equal-subset-sum, combination-sum-iv, delete-and-earn, number-of-longest-increasing-subsequence, best-time-to-buy-and-sell-stock-with-cooldown, jump-game-vi, maximum-product-subarray, perfect-squares, russian-doll-envelopes
- anchors: house-robber, coin-change, longest-increasing-subsequence

## dp-grid-knapsack
- core: unique-paths, unique-paths-ii, minimum-path-sum, triangle, maximal-square, partition-equal-subset-sum, target-sum, coin-change-ii, ones-and-zeroes, dungeon-game
- stretch: cherry-pickup, cherry-pickup-ii, minimum-falling-path-sum, number-of-dice-rolls-with-target-sum, last-stone-weight-ii, profitable-schemes, paint-house, knight-probability-in-chessboard, out-of-boundary-paths
- anchors: unique-paths, coin-change-ii, maximal-square

## dp-strings
- core: longest-common-subsequence, edit-distance, longest-palindromic-subsequence, palindromic-substrings, longest-palindromic-substring, delete-operation-for-two-strings, distinct-subsequences, is-subsequence, longest-repeating-substring
- stretch: regular-expression-matching, wildcard-matching, interleaving-string, shortest-common-supersequence, minimum-insertion-steps-to-make-a-string-palindrome, count-different-palindromic-subsequences, scramble-string
- anchors: edit-distance, longest-common-subsequence, regular-expression-matching

## dp-advanced
- core: best-time-to-buy-and-sell-stock-with-cooldown, best-time-to-buy-and-sell-stock-iii, best-time-to-buy-and-sell-stock-iv, burst-balloons, partition-to-k-equal-sum-subsets, stone-game, predict-the-winner, house-robber-iii, minimum-cost-for-tickets
- stretch: find-the-shortest-superstring, shortest-path-visiting-all-nodes, number-of-ways-to-wear-different-hats-to-each-other, count-vowels-permutation, numbers-with-repeated-digits, stone-game-ii, binary-tree-cameras, maximum-profit-in-job-scheduling, palindrome-partitioning-ii
- anchors: best-time-to-buy-and-sell-stock-with-cooldown, burst-balloons, house-robber-iii

## math-geometry
- core: palindrome-number, reverse-integer, plus-one, powx-n, sqrtx, happy-number, excel-sheet-column-number, roman-to-integer, count-primes, rectangle-overlap
- stretch: multiply-strings, fraction-to-recurring-decimal, max-points-on-a-line, k-closest-points-to-origin, integer-to-english-words, basic-calculator, angle-between-hands-of-a-clock, valid-square, the-k-th-lexicographical-string-of-all-happy-strings-of-length-n
- anchors: powx-n, count-primes, max-points-on-a-line

## bit-manipulation
- core: single-number, number-of-1-bits, counting-bits, reverse-bits, missing-number, single-number-ii, single-number-iii, sum-of-two-integers, power-of-two, hamming-distance
- stretch: subsets, maximum-xor-of-two-numbers-in-an-array, bitwise-and-of-numbers-range, total-hamming-distance, divide-two-integers, utf-8-validation, minimum-flips-to-make-a-or-b-equal-to-c, count-triplets-that-can-form-two-arrays-of-equal-xor
- anchors: counting-bits, single-number-ii, sum-of-two-integers

## randomized
- core: shuffle-an-array, random-pick-index, random-pick-with-weight, linked-list-random-node, insert-delete-getrandom-o1, insert-delete-getrandom-o1-duplicates-allowed, implement-rand10-using-rand7, random-point-in-non-overlapping-rectangles, kth-largest-element-in-an-array
- stretch: generate-random-point-in-a-circle, random-flip-matrix, random-pick-with-blacklist, guess-the-word
- anchors: random-pick-with-weight, linked-list-random-node, insert-delete-getrandom-o1

## design
- core: min-stack, lru-cache, implement-queue-using-stacks, design-hashmap, design-hashset, time-based-key-value-store, design-underground-system, logger-rate-limiter, moving-average-from-data-stream, design-browser-history
- stretch: lfu-cache, all-oone-data-structure, design-twitter, design-in-memory-file-system, design-a-leaderboard, snapshot-array, design-circular-queue, design-hit-counter, max-stack, stock-price-fluctuation, design-authentication-manager
- anchors: lru-cache, time-based-key-value-store, lfu-cache

## ood
- core: design-parking-system, design-tic-tac-toe, design-underground-system, design-a-food-rating-system, design-browser-history, design-an-ordered-stream, design-snake-game, design-a-file-sharing-system, design-movie-rental-system
- stretch: design-in-memory-file-system, design-search-autocomplete-system, design-a-text-editor, design-excel-sum-formula, design-log-storage-system, design-a-leaderboard
- anchors: design-parking-system, design-snake-game, design-underground-system

## concurrency
- core: print-in-order, print-foobar-alternately, print-zero-even-odd, building-h2o, fizz-buzz-multithreaded, the-dining-philosophers, web-crawler-multithreaded, design-bounded-blocking-queue, traffic-light-controlled-intersection
- stretch:
- anchors: print-in-order, design-bounded-blocking-queue, the-dining-philosophers

## segment-tree
- core: range-sum-query-mutable, range-sum-query-2d-mutable, count-of-smaller-numbers-after-self, reverse-pairs, my-calendar-iii, longest-increasing-subsequence, falling-squares, range-module, the-skyline-problem
- stretch: count-of-range-sum, number-of-longest-increasing-subsequence, rectangle-area-ii, queries-on-number-of-points-inside-a-circle, maximum-sum-queries, handling-sum-queries-after-update
- anchors: range-sum-query-mutable, count-of-smaller-numbers-after-self, falling-squares

## ordered-set
- core: my-calendar-i, my-calendar-ii, time-based-key-value-store, contains-duplicate-iii, find-k-closest-elements, data-stream-as-disjoint-intervals, sliding-window-median, exam-room, longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit
- stretch: count-of-smaller-numbers-after-self, stock-price-fluctuation, maximum-number-of-events-that-can-be-attended, sequentially-ordinal-rank-tracker, snapshot-array, number-of-visible-people-in-a-queue
- anchors: my-calendar-i, contains-duplicate-iii, sliding-window-median
