"""Chapter 11: transparent pooling and in-batch contrastive arithmetic.

This explains a training signal. It does not train or fine-tune a model;
Chapter 12 handles retriever training and domain adaptation.
"""

import math


def masked_mean_pool(token_vectors, attention_mask):
    """Average only nonpadding token vectors, returning a fixed-size vector."""
    if not token_vectors or len(token_vectors) != len(attention_mask):
        raise ValueError("Token vectors and mask must have equal nonzero length")
    dimension = len(token_vectors[0])
    if not dimension or any(len(row) != dimension for row in token_vectors):
        raise ValueError("Token vectors must share a positive dimension")
    if any(mask not in (0, 1) for mask in attention_mask):
        raise ValueError("Mask entries must be zero or one")
    count = sum(attention_mask)
    if count == 0:
        raise ValueError("At least one token must be unmasked")
    if any(not math.isfinite(float(value)) for row in token_vectors for value in row):
        raise ValueError("Token coordinates must be finite")
    return tuple(math.fsum(row[i] for row, mask in zip(token_vectors, attention_mask)
                           if mask) / count for i in range(dimension))


def in_batch_loss(scores, temperature=1.0):
    """One positive per row on the diagonal; other columns act as negatives.

    Returns mean cross-entropy and per-row positive probabilities. A different
    valid positive in another column is a *false negative* under this contract.
    """
    n = len(scores)
    if not n or any(len(row) != n for row in scores):
        raise ValueError("Scores must be a nonempty square matrix")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Temperature must be positive and finite")
    if any(not math.isfinite(float(value)) for row in scores for value in row):
        raise ValueError("Scores must be finite")
    losses = []
    positive_probabilities = []
    for i, row in enumerate(scores):
        logits = [value / temperature for value in row]
        if not all(math.isfinite(value) for value in logits):
            raise ValueError("Scaled score overflow; use a stable score scale")
        maximum = max(logits)
        log_denominator = maximum + math.log(math.fsum(
            math.exp(value - maximum) for value in logits))
        log_probability = logits[i] - log_denominator
        losses.append(-log_probability)
        positive_probabilities.append(math.exp(log_probability))
    return math.fsum(losses) / n, tuple(positive_probabilities)


if __name__ == "__main__":
    for matrix in (((3.0, 1.0), (0.0, 2.0)),
                   ((1.0, 1.0), (1.0, 1.0))):
        loss, probabilities = in_batch_loss(matrix)
        print({"scores": matrix, "loss": round(loss, 6),
               "diagonal_probabilities": tuple(round(x, 6) for x in probabilities)})
