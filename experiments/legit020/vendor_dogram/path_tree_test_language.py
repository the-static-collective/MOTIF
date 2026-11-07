from itertools import product


def adjacency_matrix(vertex_count, edges):
    matrix = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]
    for left, right in edges:
        if left == right:
            raise ValueError("loops are outside this specimen")
        if matrix[left][right] or matrix[right][left]:
            raise ValueError("duplicate edges are outside this specimen")
        matrix[left][right] = 1
        matrix[right][left] = 1
    return matrix


def matvec(matrix, vector):
    return [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]


def degrees(matrix):
    return [sum(row) for row in matrix]


def total_walk_counts(adjacency, max_length):
    if max_length < 0:
        raise ValueError("max_length must be nonnegative")
    vector = [1] * len(adjacency)
    counts = []
    for _ in range(max_length + 1):
        counts.append(sum(vector))
        vector = matvec(adjacency, vector)
    return counts


def path_recurrence_certificate(adjacency, eigenvalue):
    """Certify an all-length path-count recurrence for the frozen shape.

    For a simple graph adjacency matrix A, hom(P_{t+1}, G) is the total
    number of length-t walks, 1^T A^t 1. If d=A1 and A d=lambda d, then
    A^t 1=lambda^(t-1)d for every t>=1. The returned receipt records only
    that exact algebraic condition; it does not interpret the collision.
    """
    ones = [1] * len(adjacency)
    degree = matvec(adjacency, ones)
    transported_degree = matvec(adjacency, degree)
    expected = [eigenvalue * value for value in degree]
    return {
        "valid": transported_degree == expected,
        "vertex_count": len(adjacency),
        "first_walk_count": sum(degree),
        "eigenvalue": eigenvalue,
        "degree_vector": degree,
    }


def branching_star_hom_count(adjacency, leaf_count):
    """Count hom(K_1,leaf_count, G) exactly from target degrees."""
    if leaf_count < 1:
        raise ValueError("leaf_count must be positive")
    return sum(degree ** leaf_count for degree in degrees(adjacency))


def homomorphism_count(source_adjacency, target_adjacency):
    """Brute-force finite graph homomorphism count for bounded fixtures."""
    source_size = len(source_adjacency)
    target_size = len(target_adjacency)
    source_edges = [
        (left, right)
        for left in range(source_size)
        for right in range(left + 1, source_size)
        if source_adjacency[left][right]
    ]
    count = 0
    for assignment in product(range(target_size), repeat=source_size):
        if all(target_adjacency[assignment[left]][assignment[right]] for left, right in source_edges):
            count += 1
    return count
