import qailo as q


def test_pure_state():
    n = 2
    sv = q.sv.zeros(n)
    dm = q.op.pure_state(sv)
    print(q.op.matrix(dm))
    assert q.op.is_density_matrix(dm)

    for i in range(n):
        sv = q.sv.apply(q.op.h(), sv, [i])
    print(q.sv.vector(sv))
    dm = q.op.pure_state(sv)
    print(q.op.matrix(dm))
    assert q.op.is_density_matrix(dm)
