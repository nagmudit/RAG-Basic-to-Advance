# Chapter 16 lab — worked solutions

Use these after the [lab](../labs/chapter-16/LAB.md). IDs and quality values come from the [checked V4 record](../projects/V4/chapter-16-experiment.json); local timing replay can differ.

## A. Coarse cells

1. Figure 16.01 has exact IDs `01,02`; one probe returns `01,00`, so `02` is unavailable until the next centroid list is opened. Coarse k-means trains centroids, `_assign` stores each passage under one nearest centroid at index time, and query search chooses its closest `nprobe` centroids. Assignment to the nearest center does not guarantee both nearest *points* share a cell near a boundary.
2. The query compares against all `nlist` centroids even if only one list is opened. `_assign` uses squared L2 with a stable center tie; `lists` stores IDs; `search` gates scope/deletes before scoring. All-list IVF-Flat scores every eligible original unit vector under L2, whose order equals exact cosine. Stale rows, different normalization/metric or tie rules, incomplete probe caps, wrong scopes and deletes could break apparent parity.

| `N=1024,d=32` nprobe | Oracle-list coverage | IVF-Flat Recall@2 | Mean eligible scored | Flat search p50 ms |
|---:|---:|---:|---:|---:|
| 1 | .3125 | .3125 | 64.94 | .355 |
| 2 | .4688 | .4688 | 129.38 | .685 |
| 4 | .6563 | .6563 | 257.88 | 1.280 |
| 16 | 1.000 | 1.000 | 1024 | 4.834 |

Every probed global top-two member remains in the probed subset's top two under the identical exact metric, so Flat recall equals list coverage. The list population is uneven; `nprobe/nlist` does not determine the mean rows scored. These are short warmed in-process Python samples.

## B. Residual PQ

4. `r=(.4,1.7)`. The nearest subspace codeword choices are `.5` and `2.0`, so the stored code indices `(1,1)` take one bit each. `x̂=(1.5,2.0)`, `||x−x̂||²=.01+.09=.10`. For `q=(1.2,1.8)`, exact `||q−x||²=.04+.01=.05`; ADC reconstruction gives `||q−x̂||²=.09+.04=.13`. A competitor with true distance between `.05` and `.13` may reverse the order. This is unnormalized toy L2; the V0 original vectors are unit normalized, and PQ reconstructions are not generally unit length.
5. `M·b=8×2=16` bits = **2 packed bytes/vector**, thus `2,048` bytes of codes for 1,024 rows. Numeric IDs cost `8,192` bytes; 16 centroids ×32 floats ×4 bytes cost `2,048`; PQ codebooks cost `8×4×4×4=512` bytes. IVF-Flat's raw vectors, IDs and centroids total `131,072+8,192+2,048=141,312` bytes = **138.0 KiB**. Compressed PQ without originals totals `2,048+8,192+2,048+512=12,800` bytes = **12.5 KiB**. PQ with raw originals for refinement totals `143,872` bytes = **140.5 KiB**. These are payload lower bounds; Python objects, list offsets, scope/versions, tombstones, replicas, caches and source text are excluded.
6. At all sixteen lists, Flat exact-neighbor Recall@2 is `1.000` at `4.834 ms`; ADC is `.125` at `1.920 ms`; top-eight refinement is `.375` at `1.842 ms`. The exact IDs are present, but many rank below ADC position eight and cannot be fetched for exact refinement. The record contains per-query `candidate_ids`, negative approximate squared distances, probed lists and `eligible_scored` so one can name the missed ID rather than assume a model failure.
7. At four lists, Flat `.656`, ADC `.125`, refinement `.375`; at sixteen, Flat `1.000`, ADC `.125`, refinement `.375`. ADC did not improve here. At `nprobe=2`, ADC recall is `.156`, then falls to `.125` at four lists: more lists introduce falsely high-ranked compressed competitors. The coarse coverage rises monotonically, but approximate top-two ranking need not.

## C. V0 diagnosis and decision

8. `spanish-fee` exact IDs are `D6:row-2:0,D1:§8:0`. One-probe Flat has `D4:step-4:0,D4:step-4:2`, coverage `0` and judged Recall@2 `0`: both oracle lists are missed. All-probe Flat restores both and judged recall `1`. All-probe ADC returns `D4:step-4:0,D7:timeline:0`, coverage `1` but judged recall `0`: compression misorders present candidates. Top-four refinement restores both IDs and judged recall `1`; both survived its ADC shortlist. In each path these candidate IDs also enter the chapter's simple two-row context. For `code-segment`, all-probe Flat matches geometric exact top two `D4:step-4:1,D4:step-4:2`, but judged Recall@2 stays `0` because the direct literal metadata ID `D6:row-2:0` is absent from the embedded title/body route. ADC and top-four refinement do not fix that source/representation failure.
9. V0 exact geometric Recall@2 is `1` by definition; exact macro judged Recall@2 is `.792`. One-probe Flat geometric `.857`, judged `.708`; all-probe ADC geometric `.500`, judged `.792`; all-probe top-four refinement geometric `.714`, judged `.875`. The `.875` is on fourteen previously inspected author-written questions with only twelve vectors used to train both centroids and codebooks; it can arise from lucky reorderings, not a held-out gain. This run's query encoder median is `10.141 ms` and exact search p50 `.405 ms`. Even all-probe Flat/ADC search medians are higher than the exact scan here. Do not select PQ on aggregate inspected qrels.
10. `add` assigns a new versionless ID with existing centroids/codebooks; `delete` immediately excludes that ID from search but leaves it in its list and `rows` map. Durable replacement needs versioned source and index updates, physical compaction, raw-vector/candidate cache deletion, retraining when distribution drifts, and atomic visibility/migration. Build an eligible roster under a trusted policy, issue a different-scope query, and assert the restricted ID is absent from both candidate and context IDs. A free-form string supplied by a caller is merely a teaching fixture.

**Interview answer.** All-list IVF-Flat is exact under the frozen contract; all-list ADC is only `.500` geometric Recall@2 on V0. A two-byte PQ code is one component of storage: numeric IDs, centroids, codebooks and retained originals for refinement count too. On the 1,024-by-32 example, the compressed-only lower bound is 12.5 KiB, while retaining raw vectors raises it to 140.5 KiB. `spanish-fee` loses judged evidence under all-list ADC. A replacement requires independent qrels, stable policy and source versions, measured resident storage/build/update cost, stage and end-to-end latency, per-slice exact-neighbor and judged recall, and a predeclared acceptance/rollback gate.
