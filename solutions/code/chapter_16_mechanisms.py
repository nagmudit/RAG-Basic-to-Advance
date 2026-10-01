"""Separate worked answer: attempt the learner task first. Standard library only."""

import math


def squared_distance(a, b):
    if not a or len(a) != len(b) or not all(math.isfinite(x) for x in (*a, *b)):
        raise ValueError("Mismatched or nonfinite vectors")
    return sum((x-y)**2 for x,y in zip(a,b))


def nearest_centroid(vector, centroids):
    if not centroids:
        raise ValueError("Empty codebook")
    return min(range(len(centroids)), key=lambda i: (squared_distance(vector, centroids[i]), i))


def encode_subvectors(vector, codebooks):
    width = len(codebooks[0][0])
    if len(vector) != width*len(codebooks):
        raise ValueError("Subspaces must partition vector")
    return tuple(nearest_centroid(vector[m*width:(m+1)*width], book)
                 for m, book in enumerate(codebooks))


def adc_distance(query, code, codebooks):
    width = len(codebooks[0][0])
    if len(query) != width*len(codebooks) or len(code) != len(codebooks):
        raise ValueError("Invalid partition or code")
    return sum(squared_distance(query[m*width:(m+1)*width], book[code[m]])
               for m, book in enumerate(codebooks))
