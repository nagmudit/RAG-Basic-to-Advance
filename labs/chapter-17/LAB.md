# Chapter 17 lab — Build the frontier, then judge the graph

Read [Chapter 17](../../chapters/chapter-17-proximity-graphs-nsw-and-hnsw.md) Sections 1–7 first. Chapters 10, 13, 15 and 16 supply the metric, materialized exact oracle, eligibility and approximation contracts. Keep final reference code and solutions closed until your first construction attempt. Preserve every negative observation.

## A0. Construct the bounded mechanisms

Implement `search_layer` and `select_neighbors` in [implement.py](implement.py). This task builds a **single-layer mechanism**, not the whole HNSW engine. Use finite equal-dimensional coordinates, squared L2, lexicographic ID ties and a valid graph. Define the visited set, nearest-first frontier and retained pool before coding. The pool contains at most `ef` neighbors. Each encountered vertex is scored once per search. Admission, eviction and the stopping condition must follow the chapter; cycles must terminate.

Return the ordered `(ID,d²)` ranking, actual scored IDs and post-expansion frontier/retained snapshots using the starter's schema. Implement diversity selection independently: visit candidates in distance/ID order; accept c only when every previously selected s has `d²(c,s)≥d²(c,center)`. Do not refill rejected candidates.

1. Draw your own four-vertex graph with a greedy local minimum. Predict the result at widths one and two, with all queue states.
2. Implement both functions. You may use two heaps or a sorted bounded retained list; explain the resulting update cost.
3. Run the checker on its fresh visible fixtures:

```powershell
python -X utf8 labs/chapter-17/check_implementation.py
```

The untouched starter intentionally raises `NotImplementedError`. Feedback includes a local-minimum failure, recovery through a retained bridge, a cycle, equal distances, disconnection and redundant neighbor selection. A search that visits exactly `ef` vertices fails the intended contract. Submit your code, predictions, feedback and one repaired bug or explanation of why your first attempt was already correct. Only then consult the [independent answer](../../solutions/code/chapter_17_mechanisms.py) and complete engine.

## A. Paper hierarchy and insertion

4. Reproduce `ch17-frontier-fixture-v1` by hand. At `ef=1`, identify the first decision that prevents D's discovery. At `ef=2`, show all admission/eviction decisions and final top one. Remove C→D and explain why width 100 cannot help.
5. For `M=4`, calculate `P(L≥0)`, `P(L≥1)`, `P(L≥2)`, expected upper memberships and expected layer populations at `N=1,024`. Calculate levels for `U=.8,.2,.01`; state why the random level says nothing about a document's authority.
6. Read [the hierarchy coordinates and actual graph](../../visuals/chapter-17/hierarchy-example.json). Trace query `(6.7,.2)` from A through each layer. Compute the squared distances to F,G,H,E. Explain why the base expands E after H while returning H,G.
7. Hand-insert I `(6.5,0)` at **level zero** into that eight-vertex graph with `M=2,efConstruction=12`. Identify upper entry search, the base candidate pool, diversity-selected links and reciprocal lists. Compare your prediction with `add(..., level=0)`. Record an old list if pruning changes it. A prescribed level is for arithmetic, not the experiment's random construction.
8. Compute the P,Q,R neighbor-selection example. Show each distance comparison. Change the rule to nearest-only and explain the potential navigation cost; do not assert a measured recall gain without running a compatible experiment.

## B. Reproduce a declared experiment

After A0, run from the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V4 -p test_ch17.py -v
python -X utf8 projects/V4/experiment_ch17.py --output projects/V4/chapter-17-experiment-local.json
python -X utf8 visuals/chapter-17/plot-17-01-03-graph-mechanics.py
python -X utf8 visuals/chapter-17/plot-17-04-quality-cost.py
```

The standard-library index needs no ANN package. The judged experiment loads the cached pinned Chapter 11 encoder; follow [V3 setup](../../projects/V3/README.md) if absent, and use `--allow-download` only for that exact public revision. Plots require matplotlib. The measured plot reads the checked observation, not your local replay. Save local results separately. UUIDs, timestamps and latencies change; frozen vectors, graph identities, IDs, work and quality should reproduce under compatible inputs.

9. On `ch16-synthetic-n1024-d32-v1`, tabulate exact-neighbor Recall@2, distinct vectors scored, p50 and p95 for all three query widths at each `M`. Hold each graph fixed within the width comparison. Explain why the `M` comparison also changes random levels.
10. At `M=4,e=24`, compare construction widths 8 and 32: build time, level populations, adjacency entries and geometric recall. Explain why the build distance counter is incomplete. Repeat under a second seed in a **new registered workload/experiment record** if you change the corpus/questions; if only the graph seed changes, keep the workload ID and give the graph a new identity. Never overwrite the checked record.
11. Use actual entries to compute vector, adjacency and level payload lower bounds at `M=2,4,8`. List five excluded resident/storage costs. Explain why this graph is not a compressed-only PQ index.
12. Compare fresh exact/IVF-Flat controls with HNSW at identical cutoff and questions. Explain why the new coarse training is not the Chapter 16 index. Historical timings and current traced timings must not be joined into a longitudinal speed claim.

## C. Trace a miss; separate quality layers

13. On `ch16-synthetic-n1024-d32-v1`, find `synth-07` at `m8_c32_e24`. Join the case's request ID to its sample. List oracle, raw scored, base-retained and final IDs; reconstruct frontier mutations until stopping. Is `s00352` undiscovered, scored-and-rejected, evicted, or excluded only by final cutoff? Use the record, not guesses from the result.
14. On `ch13-stress-probes-v1`, repeat for `code-sev` at `m2_c32_e2` and `m4_c32_e24`. Inspect outgoing reachability from the saved entry at `M=2`. Why does increasing width to 24 leave aggregate recall unchanged? Distinguish a missing path from an insufficient frontier.
15. Inspect `code-segment` and `acronym-sla` under exact search. Identify the relevant/direct qrels the geometric oracle omits. Explain why index parity cannot repair those failures. Compare context IDs with candidates without claiming answer correctness.
16. For both no-positive questions, state the candidate-return rate, undefined recall convention, D10 exclusion and unmeasured abstention. Why is graph search completion status not retrieval confidence? What held-out calibration data would a similarity threshold need?

## D. Operation and project decision

17. Delete a bridge in a tiny graph and then its entry. Show what disappears from raw scored candidates, what remains physically stored, and what happens to reachability. Reload a checksummed snapshot; try a wrong source version or altered vector. State the trusted digest boundary and why restored snapshots are query-only.
18. Design a trusted scope change: no forbidden vertex may be scored or appear in the trace. Specify graph rebuild/routing, eligibility-version cache invalidation, matched exact oracle and the quality test. Caller-provided strings and final postfilters do not satisfy authentication.
19. Write a one-page V4 decision card with workload IDs, frozen inputs, geometric and judged metrics, per-stage timing boundaries, memory limits, two request IDs and failures. State whether to keep exact, adopt the graph, or gather more evidence. Include null generation outcomes and a representative independent judged/service gate. A negative deployment decision is fully creditworthy.

## Recall and rubric

Without opening code, draw `C/W/visited`, the hierarchy, index-time insertion and query-time search. Explain why width is not a visit budget and why deletion can lower recall. Teach one example back the next day; compare with your original trace and correct any missing state. This is chapter practice; the cumulative Part IV assessment comes at its later boundary.

Suggested rubric: independent mechanisms and invariants **30%**; hand arithmetic/hierarchy/insertion **20%**; registered, controlled measurements **20%**; actual trace-led failure diagnosis **20%**; scope/lifecycle and justified project decision **10%**. Running the reference alone earns no construction credit. See [separate reasoned solutions](../../solutions/chapter-17-solutions.md) after attempting each task.
