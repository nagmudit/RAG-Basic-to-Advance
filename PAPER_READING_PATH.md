# Research-paper reading path: 15 tracks

This is a curriculum, not an instruction to read every paper. **CORE** papers anchor a mechanism; **IMPORTANT** papers deepen it; **OPTIONAL** papers broaden comparison; **FRONTIER** papers require fresh verification and may change status. Enter a track only after the listed chapters. For each reading, record authors/year/version, question, architecture, training and retrieval timing, corpus/labels/metric, strongest relevant baseline, reported result, ablation, limitation, influence, and one reproducible test on the running project. Primary papers and official benchmark sources were checked on **2026-09-29**. Reported gains remain specific to their datasets and setups.

## Track A — Classical IR (after Chapters 05–09)

| Tier | Paper/source | Mechanism and reading question |
|---|---|---|
| CORE | [A Vector Space Model for Automatic Indexing](https://doi.org/10.1145/361219.361220), Salton, Wong & Yang, 1975 | Weighted term vectors: what information is retained or lost by bag-of-words indexing? Reconstruct a small TF-IDF vector before reading variants. |
| CORE | [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf), Robertson & Zaragoza, 2009 | Probabilistic term evidence, saturation and length normalization: derive `k1` and `b` behavior; identify assumptions that fail on short fields. Chapter 7 supplies the worked BM25 prerequisite. |
| IMPORTANT | [Efficient Query Evaluation Using a Two-Level Retrieval Process](https://research.ibm.com/publications/efficient-query-evaluation-using-a-two-level-retrieval-process), Broder et al., 2003 | Use Chapter 08's cursor trace to reconstruct a WAND pivot and identify when its efficiency/effectiveness setting preserves exact top-k. |
| IMPORTANT | [Faster Top-k Document Retrieval Using Block-Max Indexes](https://research.engineering.nyu.edu/~suel/papers/bmw.pdf), Ding & Suel, 2011 | Safe block upper bounds and early termination: how can the same top-k be returned after scoring fewer documents? Compare with Chapter 08's toy pruner. |
| IMPORTANT | [TREC: An Overview](https://www.nist.gov/publications/trec-overview), NIST / Voorhees, 2006 | Test collections and relevance judgments: why do pooling and task definitions affect claims of retrieval quality? |

## Track B — Dense retrieval and retriever training (core papers after Chapter 11; mining papers after Chapters 12–13)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [Sentence-BERT](https://arxiv.org/abs/1908.10084), Reimers & Gurevych, 2019 | Independent sentence encoding; compare cached vectors with cross-encoding on cost and lost interactions. |
| CORE | [Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906), Karpukhin et al., 2020 | Dual encoders and positive/negative training pairs; reproduce its BM25 comparison on a new domain before generalizing. |
| IMPORTANT | [ANCE](https://arxiv.org/abs/2007.00808), Xiong et al., 2020 | ANN-mined negatives during retriever learning; inspect distribution mismatch, stale indexes and false negatives. |
| IMPORTANT | [RocketQA](https://arxiv.org/abs/2010.08191), Qu et al., 2020 | Cross-batch negatives, denoising and augmentation; test whether more difficult negatives help without contaminating labels. |
| OPTIONAL | [Optimizing Dense Retrieval Model Training with Hard Negatives](https://arxiv.org/abs/2104.08051), Zhan et al., 2021 | Static vs dynamic hard-negative mining; trace the stability/quality trade-off. |
| IMPORTANT | [Generative Pseudo Labeling](https://arxiv.org/abs/2112.07577), Wang et al., 2021 | Synthetic domain questions and cross-encoder pseudo-labels; separate teacher error from tested relevance and read after Chapter 12. |

## Track C — Retrieval benchmarks (after Chapters 12 and 33)

| Tier | Paper/source | Mechanism and reading question |
|---|---|---|
| CORE | [MS MARCO](https://arxiv.org/abs/1611.09268), Bajaj et al. (current arXiv author list; first submitted 2016) | Web-derived questions and passage/answer tasks; inspect label coverage and what an MRR gain actually means. |
| IMPORTANT | [Natural Questions](https://aclanthology.org/Q19-1026/), Kwiatkowski et al., 2019 | Real search queries with answer spans; distinguish reader evaluation from corpus-level retrieval evaluation. |
| CORE | [BEIR](https://arxiv.org/abs/2104.08663), Thakur et al., 2021 | Heterogeneous zero-shot retrieval; compare lexical, dense and reranking baselines across tasks, not only their average. |
| IMPORTANT | [MTEB](https://arxiv.org/abs/2210.07316), Muennighoff et al., 2022 | Multiple embedding tasks and languages; distinguish retrieval from classification and semantic similarity. |
| IMPORTANT | [MIRACL](https://arxiv.org/abs/2210.09984), Zhang et al., 2022 | Native-language queries and corpora across languages; distinguish monolingual multilingual evaluation from cross-lingual retrieval. |
| OPTIONAL | [BRIGHT](https://arxiv.org/abs/2407.12883), Su et al., 2024 | Reasoning-intensive retrieval; ask which query types defeat surface lexical or semantic matching. |

## Track D — Sparse neural and late interaction (after Chapter 14)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [SPLADE](https://arxiv.org/abs/2107.05720), Formal, Piwowarski & Clinchant, 2021 | Learned vocabulary weights and expansion executed in an inverted index; quantify sparsity/index cost. |
| CORE | [ColBERT](https://arxiv.org/abs/2004.12832), Khattab & Zaharia, 2020 | Separate token encoders and MaxSim; calculate one score matrix and compare with a single-vector dot product. |
| OPTIONAL | [ColBERTv2](https://arxiv.org/abs/2112.01488), Santhanam et al., 2021 | Compression and denoised supervision in late interaction; compare storage with the original design. |

ColBERTv2 also introduces the **LoTTE** evaluation setting. Read its dataset construction separately from the model results: long-tail query distribution, topic splits, qrels, and metric choice may matter more to transfer than a single average score.

## Track E — ANN and vector indexing (after Chapters 15–18)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [Product Quantization for Nearest Neighbor Search](https://doi.org/10.1109/TPAMI.2010.57), Jégou, Douze & Schmid, 2011 | Subvector codebooks and approximate distance tables; separate compression error from coarse pruning. |
| CORE | [HNSW](https://arxiv.org/abs/1603.09320), Malkov & Yashunin, 2016 preprint | Layered navigable graphs; trace insertion, `M`, `efConstruction`, `efSearch`, recall and memory. |
| IMPORTANT | [DiskANN](https://proceedings.neurips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html), Subramanya et al., 2019 | SSD-resident graph and memory/disk co-design; test hardware and filtered-query assumptions before copying results. |
| OPTIONAL | [Accelerating Large-Scale Inference with Anisotropic Vector Quantization](https://arxiv.org/abs/1908.10396), Guo et al., 2019 | ScaNN-related asymmetric quantization; identify which approximation targets the chosen similarity objective. |

## Track F — Learning to rank and reranking (after Chapters 26–27)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [Learning to Rank Using an Ensemble of Lambda-Gradient Models](https://proceedings.mlr.press/v14/burges11a.html), Burges et al., 2011 | Lambda-gradient tree ensembles; connect pair swaps to ranking metric change without treating LambdaMART as magic. |
| CORE | [Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085), Nogueira & Cho, 2019 | Cross-encoder query–passage scoring; compare quality with the candidate depth and inference budget. |
| OPTIONAL | [Shallow Cross-Encoders for Low-Latency Retrieval](https://arxiv.org/abs/2403.20222), Petrov, MacAvaney & Macdonald, 2024 | Under a latency budget, a smaller reranker may score more candidates; test the complete funnel, not model quality alone. |

## Track G — Retrieval-augmented language models (after Chapters 29 and 55)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [REALM](https://arxiv.org/abs/2002.08909), Guu et al., 2020 | Learned latent retrieval during pretraining; where does the training signal for the retriever originate? |
| CORE | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), Lewis et al., 2020 | RAG-Sequence vs RAG-Token; distinguish this trained model family from modern application-level RAG. |
| IMPORTANT | [Fusion-in-Decoder](https://arxiv.org/abs/2007.01282), Izacard & Grave, 2020 | Encode passages separately and fuse in the decoder; ask how passage count changes cost and evidence use. |
| IMPORTANT | [RETRO](https://arxiv.org/abs/2112.04426), Borgeaud et al., 2021 | Chunk retrieval and cross-attention during language-model training/inference; separate frozen retriever from trained model components. |
| OPTIONAL | [Atlas](https://arxiv.org/abs/2208.03299), Izacard et al., 2022 | Retrieval-augmented few-shot learning and index updates; distinguish retrieval timing and joint training choices. |

## Track H — Query transformation and multi-hop (after Chapters 24 and 35)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| IMPORTANT | [HyDE](https://arxiv.org/abs/2212.10496), Gao et al., 2022 | Hypothetical document as query representation; never treat the generated hypothetical text as evidence. |
| CORE | [IRCoT](https://arxiv.org/abs/2212.10509), Trivedi et al., 2022 | Interleave reasoning and retrieval; compare hop-level evidence recall with final answer accuracy. |
| IMPORTANT | [HotpotQA](https://arxiv.org/abs/1809.09600), Yang et al., 2018 | Supporting-fact supervision; inspect whether a system truly uses both hops. |
| OPTIONAL | [MuSiQue](https://arxiv.org/abs/2108.00573), Trivedi et al., 2021 | Composed multi-hop questions designed to reduce shortcut solutions; test decomposition assumptions. |

## Track I — Adaptive, active and corrective retrieval (after Chapter 36)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [Active Retrieval Augmented Generation / FLARE](https://arxiv.org/abs/2305.06983), Jiang et al., 2023 | Retrieve during generation using forward-looking text and low-confidence signals; measure unnecessary vs missed triggers. |
| CORE | [Self-RAG](https://arxiv.org/abs/2310.11511), Asai et al., 2023 | Trained reflection tokens for retrieval and critique; a generic self-check prompt is not the same architecture. |
| IMPORTANT | [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884), Yan et al., 2024 | Grade initial evidence, correct or escalate; quantify extra search cost and bad correction decisions. |

## Track J — Hierarchical and long-document retrieval (after Chapters 20 and 28)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| IMPORTANT | [RAPTOR](https://arxiv.org/abs/2401.18059), Sarthi et al., 2024 | Recursive clustering/summarization tree; trace summary error to final evidence. |
| IMPORTANT | [Late Chunking](https://arxiv.org/abs/2409.04701), Günther et al., 2024 | Encode long context before pooling chunk vectors; compare with independently embedded chunks. |
| CORE | [Lost in the Middle](https://arxiv.org/abs/2307.03172), Liu et al., 2023 | Context position experiments; re-test on the book's current model rather than assuming the effect is fixed. |

## Track K — Graph retrieval (after Chapters 38–39)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130), Edge et al., 2024 preprint, revised 2025 | Entity graph, communities and summaries for global questions; compare local relationship and global-theme workloads separately. |
| OPTIONAL | [G-Retriever](https://arxiv.org/abs/2402.07630), He et al., 2024 | Graph-text retrieval for graph QA; distinguish graph-native data from a graph extracted from document text. |

## Track L — Multimodal retrieval (after Chapters 42–43)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [ColPali: Efficient Document Retrieval with Vision Language Models](https://arxiv.org/abs/2407.01449), Faysse et al., 2024 | Page images, multi-vector late interaction and ViDoRe; compare OCR-first and OCR-free retrieval by document type. |
| FRONTIER | Additional visual, audio and video retrieval work is tracked in [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md) | Promote to core only after stable comparisons, provenance support and reproducible gains. |

## Track M — RAG evaluation (after Chapters 30–33 and 48)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| IMPORTANT | [RAGAS](https://arxiv.org/abs/2309.15217), Es et al., 2023 | Reference-free component metrics; compare judge outputs with human labels and inspect bias. |
| IMPORTANT | [RAGChecker](https://arxiv.org/abs/2408.08067), Ru et al., 2024 | Fine-grained retrieval/generation diagnosis; ask whether claim-level labels localize failure better than one score. |
| OPTIONAL | [TREC 2024 RAG Track baseline framework](https://arxiv.org/abs/2406.16828), Pradeep et al., 2024 | System-level RAG evaluation; inspect track version, collection, topics, support labels and public baselines before comparing runs. |
| OPTIONAL | [Official TREC 2024 RAG track overview](https://pages.nist.gov/trec-browser/trec33/rag/overview/), NIST, 2024 | Read the actual retrieval, augmented-generation and generation task definitions before interpreting a paper's TREC score. |

## Track N — Security and robustness (after Chapter 49)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| CORE | [Not what you've signed up for: Indirect Prompt Injection](https://arxiv.org/abs/2302.12173), Greshake et al., 2023 | Malicious instructions in retrieved data cross a trust boundary; identify which controls must exist outside the prompt. |
| IMPORTANT | [PoisonedRAG](https://arxiv.org/abs/2402.07867), Zou et al., 2024 | Knowledge-base poisoning; test source validation, provenance and evidence conflict, not only instruction filtering. |

## Track O — Agentic and reasoning RAG (after Chapters 35–37)

| Tier | Paper | Mechanism and reading question |
|---|---|---|
| IMPORTANT | [ReAct](https://arxiv.org/abs/2210.03629), Yao et al., 2022 | Interleaved reasoning and tool actions; trace state, observation and stop conditions, and distinguish it from a fixed tool chain. |
| FRONTIER | New reasoning-aware retrieval and learned policies live in [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md) | Terms and baselines are evolving; require measured gains over bounded deterministic and adaptive policies. |

## Benchmark reading card (Chapter 33)

For each benchmark, record **task, corpus, query distribution, label unit/completeness, metric, what it rewards, what it misses, licensing/version, and resemblance to the target production workload**. The examples below are starting questions, not final dataset claims; inspect the current dataset card and split before using any benchmark.

| Benchmark | Primary question for the learner |
|---|---|
| MS MARCO | Does web-query passage ranking match your private-document questions and judgment density? |
| Natural Questions | Are you evaluating retrieval, short-answer QA, or both, and against which corpus snapshot? |
| BEIR | Which constituent tasks resemble your domain, and does its average hide a weak slice? |
| MTEB | Is a reported score for retrieval or a different embedding task? Which language/task subset? |
| MIRACL | Does same-language retrieval reflect your cross-lingual users? |
| LoTTE | Does long-tail query wording and corpus setup match your specialized corpus? |
| HotpotQA / MuSiQue | Are intermediate supporting facts retrieved, or is final-answer accuracy using shortcuts? |
| TREC RAG | Which track year, collection, support/citation protocol and judge are used? |
| BRIGHT | Does reasoning-intensive retrieval describe your query distribution? |
| ViDoRe | Are page-image relevance labels sufficient for region-level answer grounding? |

## Reading worksheet and promotion rule

For each paper, write a one-page card: **problem → architecture → training data/objective → retrieval timing → benchmark/metric → reported result → strongest baseline → limitations → influence → a falsifiable experiment**. Include reported latency, memory, indexing and cost measurements when present; mark them **not reported** when absent. Compare claims with the frozen local corpus using the [experiment contract](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md), and identify which stage trace would expose the claimed mechanism. Promote a FRONTIER method to core only when its mechanism differs meaningfully from existing material, primary evidence is credible across relevant settings, and the teaching prerequisites are stable. The living candidates and review dates are in [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md).
