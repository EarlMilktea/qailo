from __future__ import annotations

import numpy as np
import numpy.typing as npt

from .hconj import hconj
from .identity import identity
from .matrix import matrix
from .multiply import multiply
from .type import is_operator, num_qubits


def is_close(p0: npt.NDArray, p1: npt.NDArray) -> bool:
    return p0.shape == p1.shape and np.allclose(p0, p1)


def is_hermitian(op: npt.NDArray) -> bool:
    return np.allclose(op, hconj(op))


def is_identity(op: npt.NDArray) -> bool:
    assert is_operator(op)
    n = num_qubits(op)
    return np.allclose(op, identity(n))


def is_semi_positive(op: npt.NDArray) -> bool:
    if not is_hermitian(op):
        return False
    evs = np.linalg.eigvalsh(matrix(op))
    for ev in evs:
        if ev < -1e-15:
            return False
    return True


def is_unitary(op: npt.NDArray) -> bool:
    assert is_operator(op)
    n = num_qubits(op)
    return is_identity(multiply(hconj(op), op, range(n))) and is_identity(
        multiply(op, hconj(op), range(n))
    )
