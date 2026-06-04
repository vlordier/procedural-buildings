from math import ceil
from random import randint, random

from ._constants import LEAF_PROBABILITY, MAX_RELATIVE_SIZE, MIN_RELATIVE_SIZE, NUM_AXES
from .Ops import OpNil, OpPrimitive, OpSplit
from .parsing.Rule import Size


# Generate a random operation graph with the given parameters
def genRandOpGraph(maxDepth, maxBranch, numPrims):
    if numPrims > maxBranch**maxDepth:
        raise RuntimeError("Can't fit this many prims in tree with these params")
    return randSplit(0, maxDepth, maxBranch, numPrims)


# Create a random split operation with the given parameters
def randSplit(depth, maxDepth, maxBranch, numPrims):
    if numPrims == 0:
        return OpNil()
    if depth == maxDepth:
        return OpPrimitive("rect")
    if numPrims == 1 and random() < LEAF_PROBABILITY:
        return OpPrimitive("rect")
    dDiff = maxDepth - depth
    minBranch = ceil(numPrims / (maxBranch ** (dDiff - 1)))
    numChildren = randint(minBranch, maxBranch)

    childPrims = calcPrimsInChildren(numChildren, maxBranch ** (dDiff - 1), numPrims, numChildren)

    sizes = tuple(Size(randint(MIN_RELATIVE_SIZE, MAX_RELATIVE_SIZE), True) for i in range(numChildren))
    childOps = [randSplit(depth + 1, maxDepth, maxBranch, n) for n in childPrims]
    return OpSplit(randint(0, NUM_AXES - 1), perChildArgs=sizes, childOps=childOps)


# The following function splits some number of operations 'randomly' between a set of operations
# The problem is essentially:
# Given N children and M primitives,
# Assign some number of primitives to each child such that the total number of
# assigned primitives is M and each child has no more than P primitives assigned.
# To generate a truly random assignment is complicated
# see https://stackoverflow.com/questions/8064629/random-numbers-that-add-to-100-matlab/8068956#8068956
# for a discussion.
# So we use a non-uniform verison that just generates the number of primitives assigned to each child on
# the fly.


def calcPrimsInChildren(numChildren, maxPerChild, numPrims, totChildren):
    if numChildren == 1:
        return [numPrims]
    myMin = max(numPrims - maxPerChild * (numChildren - 1), 0)
    myMax = min(numPrims, maxPerChild)
    inThisChild = randint(myMin, myMax)
    return [inThisChild, *calcPrimsInChildren(numChildren - 1, maxPerChild, numPrims - inThisChild, totChildren)]
