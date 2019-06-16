import numpy as np


# overlay a small matrix on top of a big one, at (row,col)
def overlay(big, row, col, small):
  big[row:row+small.shape[0], col:col+small.shape[1]] = small
  return big


# use a bfs way to fill hole at [i,j]
def fill_hole(b, row, col):
  q = [(row,col)]
  while len(q) > 0:
    # dequeue and fill
    (i, j) = q[0]
    q = q[1:]
    b[i,j] = 1

    # add other parts
    if b[i-1,j] == 0:
      q += [(i-1, j)]
    if b[i+1,j] == 0:
      q += [(i+1, j)]
    if b[i,j-1] == 0:
      q += [(i, j-1)]
    if b[i,j+1] == 0:
      q += [(i, j+1)]

# return the number of "holes" in the code
def num_holes(board):
  clipped = board.clip(0,1)
  r = board.shape[0]
  c = board.shape[1]

  b = overlay(np.array([[1]*(c+2)]*(r+2)), 1, 1, clipped)
  print(b)
  rows = b.shape[0]
  cols = b.shape[1]
  holes = 0
  while (True):
    found = False
    for i in range(1, rows-1):
      for j in range(1, cols-1):
        if b[i,j] == 0:
          print("found hole in (%d,%d)" % (i,j))
          found = True
          fill_hole(b, i, j)
          holes += 1
    if not found:
      break
  return holes


a = np.array([
  [1, 1, 0, 0],
  [0, 0, 0, 1],
  [1, 1, 0, 0],
  [1, 1, 1, 1]
])

print("num holes in a = %d" % num_holes(a))

print(a)
