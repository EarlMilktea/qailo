import numpy as np

from ..operator import type as op
from ..operator.swap import swap
from .svd import svd_left, svd_right, svd_two


class MPS:
    """
    MPS representation of quantum pure state

    shape of tensors: [du, dp, dl]
        du: dimension of left leg (1 for left-edge tensor)
        dp: dimension of physical leg (typically 2)
        dl: dimension of right leg (1 for right-edge tensor)

    canonical position: cp in range(n)
        0 <= cp(0) <= cp(1) < n
        tensors [0...cp(0)-1]: left canonical
        tensors [cp(1)+1...n-1]: right canonical
    """

    def __init__(self, tensors, q2t=None, t2q=None, cp=None, normalize=False):
        self.tensors = tensors
        n = len(self.tensors)
        self.q2t = [p for p in range(n)] if q2t is None else q2t
        if t2q is not None:
            self.t2q = t2q
        else:
            self.t2q = [0 for _ in range(n)]
            for p in range(n):
                self.t2q[self.q2t[p]] = p
        assert len(self.q2t) == n and len(self.t2q) == n
        self.cp = [0, n - 1] if cp is None else cp
        if normalize:
            self.normalize()

    def num_qubits(self):
        return len(self.tensors)

    def norm(self):
        A = np.identity(2)
        for t in range(self.num_qubits()):
            A = np.einsum("ij,jkl->ikl", A, self.tensors[t])
            A = np.einsum("ijk,ijl->kl", A, self.tensors[t].conj())
        return np.sqrt(np.trace(A))

    def normalize(self):
        self.canonicalize(0)
        self.tensors[0] /= self.norm()

    def canonicalize(self, p):
        n = len(self.tensors)
        assert 0 <= p and p < n
        if self.cp[0] < p:
            for t in range(self.cp[0], p):
                L, R = svd_left(self.tensors[t])
                self.tensors[t] = L
                self.tensors[t + 1] = np.einsum("il,ljk->ijk", R, self.tensors[t + 1])
        self.cp[0] = p
        self.cp[1] = max(p, self.cp[1])
        if self.cp[1] > p:
            for t in range(self.cp[1], p, -1):
                L, R = svd_right(self.tensors[t])
                self.tensors[t - 1] = np.einsum("ijl,lk->ijk", self.tensors[t - 1], L)
                self.tensors[t] = R
        self.cp[1] = p

    def _apply_one(self, p, s):
        assert op.num_qubits(p) == 1
        self.tensors[s] = np.einsum("abc,db->adc", self.tensors[s], p)
        self.cp[0] = min(self.cp[0], s)
        self.cp[1] = max(self.cp[1], s)

    def _apply_two(self, p, s, maxdim=None, reverse=False):
        """
        apply 2-qubit operator on neighboring tensors, s and s+1
        """
        assert op.num_qubits(p) == 2
        self.canonicalize(s + 1)
        t0 = self.tensors[s]
        t1 = self.tensors[s + 1]
        if not reverse:
            t = np.einsum("abc,cde,fgbd->afge", t0, t1, p)
        else:
            t = np.einsum("abc,cde,fgdb->agfe", t0, t1, p)
        L, R = svd_two(t, nkeep=maxdim, canonical="left")
        # print("apply:", self.tensors[s].shape,self.tensors[s + 1].shape, L.shape, R.shape)
        self.tensors[s] = L
        self.tensors[s + 1] = R

    def _swap_tensors(self, s, maxdim=None):
        """
        swap neighboring two tensors at s and s+1
        """
        assert s in range(0, self.num_qubits() - 1)
        self._apply_two(swap(), s, maxdim=maxdim)
        p0, p1 = self.t2q[s], self.t2q[s + 1]
        self.q2t[p0], self.q2t[p1] = s + 1, s
        self.t2q[s], self.t2q[s + 1] = p1, p0

    def _move_qubit(self, p, s, maxdim=None):
        if self.q2t[p] != s:
            # print(f"moving qubit {p} at {self.q2t[p]} to {s}")
            for u in range(self.q2t[p], s):
                # print(f"swap tensors {u} and {u+1}")
                self._swap_tensors(u, maxdim=maxdim)
            for u in range(self.q2t[p], s, -1):
                # print(f"swap tensors {u-1} and {u}")
                self._swap_tensors(u - 1, maxdim=maxdim)

    def apply(self, p, qpos, maxdim=None):
        assert op.is_operator(p) and len(qpos) == op.num_qubits(p)
        if op.num_qubits(p) == 1:
            self._apply_one(p, self.q2t[qpos[0]])
        elif op.num_qubits(p) == 2:
            tpos = [self.q2t[qpos[0]], self.q2t[qpos[1]]]
            assert tpos[0] != tpos[1]
            if tpos[0] < tpos[1]:
                self._move_qubit(qpos[1], tpos[0] + 1)
                self._apply_two(p, tpos[0], maxdim=maxdim)
            else:
                self._move_qubit(qpos[0], tpos[1] + 1)
                self._apply_two(p, tpos[1], maxdim=maxdim, reverse=True)
        else:
            raise ValueError


def check(mps):
    """
    Check the shape of mps
    """
    n = mps.num_qubits()

    # tensor shape
    dims = []
    assert mps.tensors[0].shape[0] == 1
    dims.append(mps.tensors[0].shape[0])
    for t in range(1, n - 1):
        dims.append(mps.tensors[t].shape[0])
        assert mps.tensors[t].shape[0] == mps.tensors[t - 1].shape[2]
        assert mps.tensors[t].shape[2] == mps.tensors[t + 1].shape[0]
    assert mps.tensors[n - 1].shape[2] == 1
    dims.append(mps.tensors[n - 1].shape[0])
    dims.append(mps.tensors[n - 1].shape[2])
    # print(dims)

    # qubit <-> tensor mapping
    for q in range(n):
        assert mps.t2q[mps.q2t[q]] == q
    for t in range(n):
        assert mps.q2t[mps.t2q[t]] == t

    # canonical position
    assert mps.cp[0] in range(n)
    assert mps.cp[1] in range(n)

    return True


def product_state(n, c=0):
    assert n > 0
    tensors = []
    for t in range(n):
        tensor = np.zeros((1, 2, 1))
        tensor[0, (c >> (n - t - 1)) & 1, 0] = 1
        tensors.append(tensor)
    return MPS(tensors)


def norm(mps):
    return mps.norm()
