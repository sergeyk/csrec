import numpy as np
import bucketizer

def consume(vec, size):
    output = vec[:size]
    vec = vec[size:]
    return (vec, output)

def test(vec, u1_dct, u2_dct, r_dct, dim, field_names):
    for field_name in field_names:
        bucketizer_fn = bucketizer.get_bucketizer_fn(field_name)
        (vec, out) = consume(vec, 
                             bucketizer_fn.post_cross_dim(field_name))
        assert(len(out) == bucketizer_fn.post_cross_dim(field_name))
        active_crossed = list(out.nonzero()[0])
        size_crossed = bucketizer_fn.post_cross_dim(field_name)
        (vec, out) = consume(vec, 
                             bucketizer_fn.pre_cross_dim(field_name))
        assert(len(out) == bucketizer_fn.pre_cross_dim(field_name))
        active_pre1 = list(out.nonzero()[0])
        size_pre1 = bucketizer_fn.pre_cross_dim(field_name)
        (vec, out) = consume(vec, 
                             bucketizer_fn.pre_cross_dim(field_name))
        assert(len(out) == bucketizer_fn.pre_cross_dim(field_name))
        active_pre2 = list(out.nonzero()[0])
        size_pre2 = bucketizer_fn.pre_cross_dim(field_name)
        copy_of_active_crossed = []
        for ac in active_crossed:
            copy_of_active_crossed.append(ac)
        for a1 in active_pre1:
            for a2 in active_pre2:
                copy_of_active_crossed.remove((a1*size_pre1+a2))
        assert(len(copy_of_active_crossed)==0)
    assert(len(vec) == 0)
