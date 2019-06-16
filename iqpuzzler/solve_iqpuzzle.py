import numpy as np
import itertools
import random

# the class for a single piece, its name and shape
class Piece:
  def __init__(self, id, legend, shortname, data):
    self.id = id
    self.legend = legend
    self.shortname = shortname
    self.data = data

  def size():
    return shape.sum()


p_pinkZ =    Piece(11, "P", "Pink",  np.array([[1,1,1,0],[0,0,1,1]]))
p_mblueL =   Piece(22, "<", "MBlu",  np.array([[1,1,1],[0,0,1],[0,0,1]]))
p_lblueL =   Piece(33, ">", "LBlu",  np.array([[1,0],[1,1]]))
p_dblueL =   Piece(44, "X", "DBlu",  np.array([[1,1],[0,1],[0,1]]))
p_lgreenb =  Piece(55, "g", "LGrn",  np.array([[1,1],[1,1],[0,1]]))
p_dgreenT =  Piece(66, "G", "DGrn",  np.array([[0,1,0],[1,1,1]]))
p_lredL =    Piece(77, "r", "LRed",  np.array([[1,1],[0,1],[0,1],[0,1]]))
p_dredZ =    Piece(88, "R", "DRed",  np.array([[0,1,1],[1,1,0]]))
p_yellowT =  Piece(911, "Y", "Yelw", np.array([[1,1,1,1],[0,1,0,0]]))
p_orange =   Piece(922, "O", "Orng", np.array([[0,0,1],[1,1,1],[0,1,0]]))
p_purpleW =  Piece(933, "#", "Purp", np.array([[1,1,0],[0,1,1],[0,0,1]]))
p_oliveC =   Piece(944, "%", "Oliv", np.array([[1,0,1],[1,1,1]]))

all_pieces = [
  p_pinkZ,
  p_yellowT,
  p_orange,
  p_purpleW,
  p_oliveC,
  p_mblueL,
  p_lblueL,
  p_dblueL,
  p_lgreenb,
  p_dgreenT,
  p_lredL,
  p_dredZ
]

name_map = dict((p.id, p.legend) for p in all_pieces)
name_map[1] = "."

steps = 0


# overlay a small matrix on top of a big one, at (row,col)
def overlay(big, row, col, small):
  big[row:row+small.shape[0], col:col+small.shape[1]] = small
  return big


# use a bfs way to fill hole at [i,j]
def fill_hole(b, row, col):
  fillings = 0
  q = [(row,col)]
  while len(q) > 0:
    # dequeue and fill
    (i, j) = q[0]
    q = q[1:]
    b[i,j] = 1
    fillings += 1

    # add other parts
    if b[i-1,j] == 0:
      q += [(i-1, j)]
    if b[i+1,j] == 0:
      q += [(i+1, j)]
    if b[i,j-1] == 0:
      q += [(i, j-1)]
    if b[i,j+1] == 0:
      q += [(i, j+1)]

  return fillings


# return the number of "holes" in the code
def num_holes(board):
  if board is None:
    return 0

  clipped = board.clip(0,1)
  r = board.shape[0]
  c = board.shape[1]

  b = overlay(np.array([[1]*(c+2)]*(r+2)), 1, 1, clipped)
  rows = b.shape[0]
  cols = b.shape[1]
  holes = 0
  while (True):
    found = False
    for i in range(1, rows-1):
      for j in range(1, cols-1):
        if b[i,j] == 0:
          #print("found hole in (%d,%d)" % (i,j))
          found = True
          fillings = fill_hole(b, i, j)
          if fillings <= 2:
            # very small hole found, consider this bad
            # return a very large hole count immediately to fail it
            return 99999
          holes += 1
    if not found:
      break
  return holes


tried_combo = {""}

# add a piece at row/col, 0-based
# returns a new version of board (could be None) and descriptor string
def add_piece(stack_profile, board, piece, row, col, transpose = False, fliplr = False, flipud = False):
  # make into right form
  p = piece.data.transpose() if transpose else piece.data
  p = np.fliplr(p) if fliplr else p  
  p = np.flipud(p) if flipud else p  

  desc = str([list(i) for i in list(p)])
  global tried_combo
  if (stack_profile, piece.id, row, col, desc) in tried_combo:
    return None  # already tried this before
  else:
    tried_combo.add((stack_profile, piece.id, row, col, desc))

  # check if the piece will go out of board boundary
  if ((row + p.shape[0] > board.shape[0]) or (col + p.shape[1] > board.shape[1])):
    return None

  # embed this piece into an empty board
  piece_big = np.zeros((5,11), dtype=np.int)
  piece_big[row:row+p.shape[0], col:col+p.shape[1]] = p * piece.id  # store id in pic

  # check for overlap
  if (board * piece_big).sum() > 0:
    return None

  # valid position, add this piece to the board and return
  return board + piece_big


def pretty_print(board):
  for i in range(5):
    print(" ".join("%4s" % name_map[x] for x in list(board[i])))
  print()


def pretty_stack(stack):
  results = []
  for i in range(len(stack)):
    (b, pos) = stack[i]
    p = pieces[i]
    results += ["%5s-%-3d" % (p.shortname, pos)]
  print(" ".join(results))



# search for solutions in DFS manner
def search_for_solutions(start_board, pieces):
  #random.shuffle(pieces)

  s = start_board.sum() + sum([p.data.sum() for p in pieces])
  if not s == 11*5:
    print("CANNOT SOLVE, invalid start, sum = %d (should be 55)" % s)
    exit()

  # generate all positions and orientations each piece can be tried with
  tf = [False, True]
  all_args = list(itertools.product(tf, tf, tf))
  all_pos = list(itertools.product(all_args, list(range(5)), list(range(11))))

  print("Total positions to explore for each piece: %d" % len(all_pos))
  print("Total pieces remaining: %d" % len(pieces))

  status_stack = []
  cur_board = start_board
  cur_pos_index = 0
  p = pieces[0]

  global steps

  while(True): 

    #print("-- dealing with %5s, start pos_index = %d" % (p.shortname, cur_pos_index))

    while cur_pos_index < len(all_pos):
      ((trans, fliplr, flipud), row, col) = all_pos[cur_pos_index] 
      # get a descriptor of the stack itself
      stack_profile = ".".join([str(pos) for (b, pos) in status_stack])
      board = add_piece(stack_profile, cur_board, p, row, col, trans, fliplr, flipud)
    
      # quick invalidation for some obviously issues, like more holes
      # than left over pieces
      holes = num_holes(board)
      if holes > len(pieces) - len(status_stack) - 1:
        board = None
        #print("early termination: holes = %d, left pieces = %d" % (holes, len(pieces) - len(status_stack)))

      # --- check for success ---
      if board is not None:
        if board.min() > 0:
          print("Found solution after %d steps" % steps)
          pretty_print(board)
          exit()
        else:
          # -------- still more space to fill --------
          '''
          print("PUSH: %5s at (%d, %d) %s%s%s   (pos_index = %d)  stack len afterwards = %d" %
           (p.shortname, row, col,
            "T " if trans else "- ",
            "LR " if fliplr else "-  ",
            "UD " if flipud else "-  ",
            cur_pos_index,
            len(status_stack) + 1))
          '''
   
          status_stack += [(cur_board, cur_pos_index)]  # old board in it
          #if len(pieces) - len(status_stack) <= 2:
          #  print("...almost...")
          #  pretty_print(board)

          steps += 1
          if steps % 100 == 0:
            print("steps = %d" % steps)
            pretty_stack(status_stack)


          # start the placement for a new piece
          cur_board = board
          cur_pos_index = 0
          p = pieces[len(status_stack)]

      else:
        # the piece cannot be added with this position config
        cur_pos_index += 1
    # end of inner while

    # keep popping until we have some pos available to try
    #print("  -- running out of pos for %s, current stack len = %d" % (p.shortname, len(status_stack)))

    while(cur_pos_index == len(all_pos)):
      p = pieces[len(status_stack) - 1]  # record last one for display purpose

      #print("POP : %5s" % (p.shortname))
      (cur_board, cur_pos_index) = status_stack[-1]
      status_stack = status_stack[:-1]   # actually pop
      cur_pos_index += 1

      global tried_combo
      tried_combo.clear()  # this can be cleared as the stack has changed

  # end of outer while
    
    
if __name__ == "__main__":

  # ---- set the value of start and pieces to a game ----

  # problem 22 of IQ Puzzler Pro
  start = np.array([
    [1,1,1,1,1,1,1,1,0,0,0],
    [1,1,1,1,1,0,0,1,0,0,0],
    [1,1,1,1,1,0,0,0,0,0,0],
    [1,1,1,1,0,0,0,0,0,0,0],
    [1,1,1,1,0,0,0,0,0,0,0]
  ])

  # 12 in total, comment out the ones already used
  pieces = [
    p_pinkZ,
    p_yellowT,
    p_orange,
    # p_purpleW,
    # p_oliveC,
    p_mblueL,
    # p_lblueL,
    p_dblueL,
    # p_lgreenb,
    p_dgreenT
    # p_lredL,
    # p_dredZ
  ]

  '''
  # problem 40 of IQ Puzzler Pro
  start = np.array([
    [1,0,0,0,0,0,0,0,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0]
  ])

  # 12 in total, comment out the ones already used
  pieces = [
    p_pinkZ,
    # p_yellowT,
    p_orange,
    p_purpleW,
    p_oliveC,
    p_mblueL,
    p_lblueL,
    p_dblueL,
    # p_lgreenb,
    p_dgreenT,
    p_lredL,
    p_dredZ
  ]
  '''
  '''
  # problem 34 of IQ Puzzler Pro
  start = np.array([
    [1,1,1,1,1,1,1,0,0,0,0],
    [0,0,1,0,0,1,1,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0]
  ])

  # 12 in total, comment out the ones already used
  pieces = [
    p_pinkZ,
    p_yellowT,
    p_orange,
    p_purpleW,
    p_oliveC,
    p_mblueL,
    p_lblueL,
    # p_dblueL,
    # p_lgreenb,
    p_dgreenT,
    # p_lredL,
    p_dredZ
  ]
  '''

  search_for_solutions(start, pieces)


