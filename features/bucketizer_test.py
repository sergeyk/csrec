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
        print out.nonzero()[0]
        (vec, out) = consume(vec, 
                             bucketizer_fn.pre_cross_dim(field_name))
        assert(len(out) == bucketizer_fn.pre_cross_dim(field_name))
        print out.nonzero()[0], bucketizer_fn.pre_cross_dim(field_name)
        (vec, out) = consume(vec, 
                             bucketizer_fn.pre_cross_dim(field_name))
        assert(len(out) == bucketizer_fn.pre_cross_dim(field_name))
        print out.nonzero()[0], bucketizer_fn.pre_cross_dim(field_name)
        print '--'
