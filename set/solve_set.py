properties = [
  ["1", "2", "3"], # count
  ["h", "z", "l"], # color
  ["s", "x", "k"], # filling
  ["y", "l", "w"]  # shape
]

cards = [
  "3zsw",
  "3zxw",
  "2hkw",
  "2zkl",
  "2zxy",
  "3lsl",
  "2lky",
  "2lxl",
  "3hsw",
  "2lsl",
  "3zky",
  "2hsy",
]


def solve_card(card1, card2):
  return "".join([ solve_property(card1[i], card2[i], properties[i]) for i in range(4) ])


def solve_property(p1, p2, all_values):
  if p1 == p2:
    return p1
  else:
    return [x for x in all_values if x not in [p1, p2]][0]

solutions = []

for i in range(len(cards) - 1):
  for j in range(i+1, len(cards)):
    solution = solve_card(cards[i], cards[j])
    exists = solution in cards
    sindex = cards.index(solution) if exists else -1
    if exists:
      sol = [i, j, sindex]
      sol.sort()
      if sol not in solutions:
        print("--- found solution: %s" % [x+1 for x in sol])  # 1-based
        solutions += [sol]   
