from . import mps
from . import operator as op
from . import state_vector as sv


def apply(v, p, pos=None, maxdim=None):
    if sv.is_state_vector(v):
        v = sv.apply(v, p, pos)
    elif mps.is_mps(v):
        v = mps.apply(v, p, pos, maxdim)
    else:
        assert False
    return v


def apply_seq(v, seq, maxdim=None):
    if sv.is_state_vector(v):
        v = sv.apply_seq(v, seq)
    elif mps.is_mps(v):
        v = mps.apply_seq(v, seq, maxdim)
    else:
        assert False
    return v


def num_qubits(v):
    if sv.is_state_vector(v):
        return sv.num_qubits(v)
    elif op.is_operator(v):
        return op.num_qubits(v)
    elif mps.is_mps(v):
        return mps.num_qubits(v)
    assert False


def probability(v, pos=None):
    if sv.is_state_vector(v):
        return sv.probability(v, pos)
    elif mps.is_mps(v):
        return sv.probability(mps.state_vector(v), pos)
    assert False


def vector(v, c=None):
    if sv.is_state_vector(v):
        return sv.vector(v, c)
    elif mps.is_mps(v):
        return sv.vector(mps.state_vector(v), c)
    assert False
