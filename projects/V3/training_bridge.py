"""Chapter 12's two-coordinate loss-to-update example; no encoder dependency."""
import math


def softmax(logits):
    if not logits or not all(math.isfinite(x) for x in logits):
        raise ValueError("Finite nonempty logits required")
    maximum = max(logits)
    weights = [math.exp(x - maximum) for x in logits]
    total = math.fsum(weights)
    return [x / total for x in weights]


def matvec(matrix, vector):
    """A row's dot product produces one output coordinate."""
    if not matrix or any(len(row) != len(vector) for row in matrix):
        raise ValueError("Matrix columns must match input coordinates")
    return [math.fsum(a * b for a, b in zip(row, vector)) for row in matrix]


def loss_and_gradient(matrix, query=(1., 2.), passages=((1., 0.), (0., 1.)),
                      positive=0, temperature=1., normalize=False):
    """Gradient of one row-softmax loss with respect to W.

    The optional normalization path exposes the Jacobian used by the actual
    adapter, while the manuscript's hand example uses unnormalized dot scores.
    """
    if temperature <= 0 or not math.isfinite(temperature):
        raise ValueError("Positive finite temperature required")
    z = matvec(matrix, query)
    norm = math.sqrt(math.fsum(x*x for x in z))
    if normalize and norm == 0:
        raise ValueError("Cannot normalize a zero projected query")
    represented = [x/norm for x in z] if normalize else z
    scores = [math.fsum(a*b for a, b in zip(represented, p)) for p in passages]
    logits = [s / temperature for s in scores]
    probabilities = softmax(logits)
    maximum = max(logits)
    loss = maximum - logits[positive] + math.log(
        math.fsum(math.exp(x-maximum) for x in logits))
    # dL/ds_j = (P_j - 1[j is positive])/temperature.
    upstream = [math.fsum((probabilities[j] - (j == positive)) * p[i]
                         for j, p in enumerate(passages)) / temperature
                for i in range(len(z))]
    if normalize:
        # d(z/||z||)/dz = (I - z_hat z_hat^T)/||z||.
        parallel = math.fsum(a*b for a, b in zip(represented, upstream))
        upstream = [(g - x*parallel)/norm
                    for x, g in zip(represented, upstream)]
    gradient = [[g*x for x in query] for g in upstream]
    return {"z": z, "scores": scores, "probabilities": probabilities,
            "loss": loss, "gradient": gradient}


def finite_difference(matrix, epsilon=1e-6, **kwargs):
    """Central differences perturb each scalar independently."""
    result = []
    for i, row in enumerate(matrix):
        values = []
        for j, _ in enumerate(row):
            plus, minus = [list(r) for r in matrix], [list(r) for r in matrix]
            plus[i][j] += epsilon
            minus[i][j] -= epsilon
            values.append((loss_and_gradient(plus, **kwargs)["loss"] -
                           loss_and_gradient(minus, **kwargs)["loss"]) / (2*epsilon))
        result.append(values)
    return result


def example():
    matrix = [[1., 0.], [0., 1.]]
    before = loss_and_gradient(matrix)
    updated = [[w - .1*g for w, g in zip(row, grad)]
               for row, grad in zip(matrix, before["gradient"])]
    after = loss_and_gradient(updated)
    numeric = finite_difference(matrix)
    error = max(abs(a-b) for row, check in zip(before["gradient"], numeric)
                for a, b in zip(row, check))
    return {"before": before, "updated_matrix": updated, "after": after,
            "finite_difference_max_error": error,
            "stability": softmax([1004., 1003., 1001.])}


if __name__ == "__main__":
    import json
    print(json.dumps(example(), indent=2))
