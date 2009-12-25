EXCLUDE_SCORE = -1e10
INSTITUTION_SCORE = 1
HISTORY_SCORE = 1e2

def dp(data):
    N = len(data) + 1
    state = [0] * (N + 1)
    action = [0] * (N + 1)

    for i in range(2, N+1):
        if (state[i-2] + data[i-2]) > state[i-1]:
            action[i] = 1
            state[i] = state[i-2] + data[i-2]
        else:
            action[i] = 0
            state[i] = state[i-1]
    j = N
    L = []
    #while j >= 0:
    #    L.insert(0, j) 
    #    j -= (action[j] + 1)
    #return state[N], L
    while j >= 0:
        j -= (action[j] + 1)
        if action[j]:
            L.insert(0, j-2) # insert index corresponding to start of swap
    return state[N], L

def run():
    data = [3, 5, 3, 5, 3]
    print dp(data)

def score_swap((a1, n1), (a2, n2)):
    inst = (a1.institution == n1.institution,
            a2.institution == n2.institution)
    hist = (a1.seen(n1), a2.seen(n2))

    if not (inst[0] or inst[1]) and sum(hist) == 0:
        return EXCLUDE_SCORE

    inst_swap = (a1.institution == n2.institution,
                 a2.institution == n1.institution)
    hist_swap = (a1.seen(n2), a2.seen(n1))

    if sum(hist_swap) > sum(hist):
        return EXCLUDE_SCORE

    def badness(i, h):
        return i.count(True) * INSTITUTION_SCORE + sum(h) * HISTORY_SCORE

    return badness(inst, hist) - badness(inst_swap, hist_swap)

class Team(object):
    def __init__(self, id, inst, hist):
        self.id = id
        self.institution = inst
        self.hist = hist 

    def seen(self, other):
        return self.hist.count(other.id)

def swap(draw, i):
    m1 = (draw[i][0], draw[i+1][1])
    m2 = (draw[i+1][0], draw[i][1])
    draw[i] = m1
    draw[i+1] = m2

def one_up_down(draw):
    score, swaps = dp([(score_swap(draw[i], draw[i+1])) for i in range(len(draw) - 1)])
    for s in swaps:
        swap(draw, s)
    return draw

from unittest import TestCase

class TestDraw(TestCase):
    def failUnlessEqual(self, a, b):
        return

    def testNoSwap(self):
        data = (((1, 'A', ()), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = ((1, 5), (2, 6), (3, 7), (4, 8))
        self.failUnlessEqual(result, self.draw(data))
        return self.draw(data)

    def testSwapInst(self):
        data = (((1, 'A', ()), (5, 'A', ())),
                ((2, 'C', ()), (6, 'B', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = ((1, 6), (2, 5), (3, 7), (4, 8))
        self.failUnlessEqual(result, self.draw(data))
        return self.draw(data)

    def testSwapHist(self):
        data = (((1, 'A', (5,)), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = ((1, 6), (2, 5), (3, 7), (4, 8))
        self.failUnlessEqual(result, self.draw(data))
        return self.draw(data)

    def draw(self, data):
        d = []
        for ((p1, in1, hist1), (p2, in2, hist2)) in data:
            d.append((Team(p1, in1, hist1), Team(p2, in2, hist2)))
        r = one_up_down(d)
        return [(a.id, b.id) for (a, b) in r]


if __name__ == '__main__':
    run()
    d = Tests()
    d.testNoSwap()
    
