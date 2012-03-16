from biz.business_logic import BusinessLogic as bl
from math import sqrt


def update_user_bias(u, e_ui):
    b_u = bl.get_user_bias(u)
    lrn_rate = bl.get_learning_rate()
    new_b_u = b_u + lrn_rate * ( e_ui - bl.get_lambda(4) * b_u)
    bl.set_user_bias(u, new_b_u)


def update_item_bias(i, e_ui):
    b_i = bl.get_item_bias(i)
    lrn_rate = bl.get_learning_rate()
    new_b_i = b_i + lrn_rate * ( e_ui - bl.get_lambda(4) * b_i)
    bl.set_item_bias(i, new_b_i)


def update_weights(u, i, e_ui):
    knn = bl.get_rated_knn(u, i)
    normalization = 1.0/sqrt(len(knn))
    g_avg = bl.get_global_avg()
    lrn_rate = bl.get_learning_rate()
    lambda4 = bl.get_lambda(4)
    b_u = bl.get_user_bias(u)
    for j in knn:
        weight = bl.get_weight(i, j)
        r_uj = bl.get_rating(u,j)
        b_j = bl.get_item_bias(j)
        b_uj = g_avg + b_u + b_j
        new_weight = weight + lrn_rate * \
            (normalization * e_ui * (r_uj - b_uj) - lambda4 * weight)
        bl.set_weight(i, j, new_weight)
