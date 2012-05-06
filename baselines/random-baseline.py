# random baseline - computes expected value of picking the right guy (or None)

def random_baseline_test_predictionerror(data):
  sumacc = 0.0
  for cs in data:
    noptions = 1 + len(cs.get_surferlist())
    sumacc += 1 / float(noptions)
  accuracy = sumacc / len(data)
  return accuracy


def random_baseline_test_meannormalizedwinnerrank():
  return 0.5 # Tim thinks it works out like this mathematically
