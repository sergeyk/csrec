import numpy as np
import scipy.stats as st

def importance_sample(dist, num_points, kde=None):
  """
  dist is a list of numbers drawn from some distribution.
  If kde is given, uses it, otherwise computes own.
  Return num_points points to sample this dist at, spaced such that
  approximately the same area is between each pair of sample points.
  """
  if not kde:
    kde = st.gaussian_kde(dist.T)
  x = np.linspace(np.min(dist),np.max(dist))
  y = kde.evaluate(x)
  ycum = np.cumsum(y)
  points = np.interp(np.linspace(np.min(ycum),np.max(ycum),num_points),xp=ycum,fp=x)
  return points