import numpy as np

from ..operator import type as op
from ..util.letters import letters
from ..util.replace import replace
from . import type as sv


def apply(p, v, pos=None):
    assert op.is_operator(p) and sv.is_state_vector(v)
    n = sv.num_qubits(v)
    m = op.num_qubits(p)
    if pos is None:
        assert m == n
        pos = range(n)
    assert len(pos) == m

    ss_op = letters()[: 2 * m]
    ss_v = ss_to = letters()[2 * m : 2 * m + n + 1]
    for i in range(m):
        ss_v = replace(ss_v, pos[i], ss_op[m + i])
        ss_to = replace(ss_to, pos[i], ss_op[i])
    return np.einsum("{},{}->{}".format(ss_v, ss_op, ss_to), v, p)
