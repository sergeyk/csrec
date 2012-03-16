from scipy import stats
import heapq
from biz.business_logic import BusinessLogic as bl


def compute_and_set_items_knn(similarity_fn, k):
    """Computes and stores the k nearest neighbors for each item."""
    for item_id in bl.get_all_item_ids():
        bl.set_item_knn(item_id, find_knn_for_item(item_id, similarity_fn, k))


def find_knn_for_item(item_id, similarity_fn, k):
    knn = []
    for item2_id in bl.get_all_item_ids():
        if not item_id == item2_id:
            similarity_score = int(round(100*similarity_fn(item_id, item2_id)))
            if len(knn) < k:
                heapq.heappush(knn, (similarity_score, item2_id))
            else:
                worst_score_so_far = knn[0][0]
                if similarity_score > worst_score_so_far:
                    l = heapq.heappop(knn)
                    heapq.heappush(knn, (similarity_score, item2_id))
    return knn


def shrunk_pearson_correlation(item1_id, item2_id):
    common_raters = set(bl.get_common_raters(item1_id, item2_id))
    num_in_common = len(common_raters)
    item1_ratings = bl.get_ratings_for_item(item1_id, 
                                            common_raters)
    item2_ratings = bl.get_ratings_for_item(item2_id,
                                            common_raters)
    pearson = stats.pearsonr(item1_ratings, item2_ratings)[0]
    lambda2 = bl.get_lambda(2)
    out = num_in_common/(num_in_common + lambda2) * pearson
    return out
