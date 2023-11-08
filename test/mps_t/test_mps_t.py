import qailo as q


def test_mps_t():
    v = q.mps_t.zero(3)

    print("input:")
    print("state vector:", q.vector(v))
    print("probabitily:", q.probability(v))

    v = q.apply(v, q.op.h(), [0])
    v = q.apply(v, q.op.h(), [2])
    v = q.apply(v, q.op.cx(), [0, 1])
    v = q.apply(v, q.op.cz(), [1, 2])
    v = q.apply(v, q.op.h(), [2])

    print("output:")
    print("state vector:", q.vector(v))
    print("probabitily:", q.probability(v))

    print("# tensor pool")
    for id, tp in enumerate(v.tpool):
        print(f"{id} {tp[0].shape} {tp[1]} {tp[2]}")
    assert len(v.tpool) == 25

    print("# generator pool")
    for id, gp in enumerate(v.gpool):
        print(f"{id} {gp[0].shape} {gp[1]} {gp[2].shape} {gp[3].shape}")
    assert len(v.gpool) == 2

    prefix = "test_mps_t"
    v._dump(prefix)


if __name__ == "__main__":
    test_mps_t()
