from collections import defaultdict
from random import random

from sympy.core.expr import Expr
from sympy.core.numbers import Integer
from sympy.core.relational import Relational
from sympy.logic.boolalg import BooleanAtom

from .parsing.Rule import Size
from .RandRange import RandRange


class Args:
    def __init__(self, args, perChildArgs):
        self.args = args
        self.perChildArgs = perChildArgs
        if len(perChildArgs) > 0:
            self.allArgs = (*self.args, self.perChildArgs)
        else:
            self.allArgs = self.args

    # evaluate arg values
    def evaluate(self, env):
        evaledArgs = tuple(self.evalArg(arg, env) for arg in self.allArgs)
        return evaledArgs

    def evaluateSeparate(self, env):
        evaledArgs = tuple(self.evalArg(arg, env) for arg in self.args)
        evaledChildArgs = tuple(self.evalArg(arg, env) for arg in self.perChildArgs)
        return evaledArgs, evaledChildArgs

    def evalArg(self, arg, env):
        t = type(arg)
        if t is tuple:
            return tuple(self.evalArg(a, env) for a in arg)
        elif t is Size:
            return Size(self.evalArg(arg.size, env), arg.isRelative)
        elif t in (int, str, float):
            return arg
        elif issubclass(t, RandRange):
            return arg.evaluate()
        elif issubclass(t, Expr) or issubclass(t, Relational):
            evaled = arg.subs(env)
            if len(evaled.free_symbols) > 0:
                return str(evaled)
            elif issubclass(type(evaled), BooleanAtom):
                return bool(evaled)
            elif issubclass(type(evaled), Integer):
                return int(evaled)
            else:
                return float(evaled)
        else:
            return arg

    def combineWith(self, other):
        newArgs = self.combineArgs(self.args, other.args)
        if newArgs is None:
            return None
        newPerChildArgs = self.combineArgs(self.perChildArgs, other.perChildArgs)
        if newPerChildArgs is None:
            return None
        else:
            return Args(newArgs, perChildArgs=newPerChildArgs)

    def combineArgs(self, arg1, arg2):
        if arg1 == arg2:
            return arg1
        t1 = type(arg1)
        t2 = type(arg2)
        if t1 in (list, tuple):
            if t2 is t1 and len(arg1) == len(arg2):
                newListArg = []
                for a1, a2 in zip(arg1, arg2, strict=True):
                    newArg = self.combineArgs(a1, a2)
                    if newArg is None:
                        return None
                    newListArg.append(newArg)
                return newListArg if t1 is list else tuple(newListArg)
            return None
        elif t2 is list:
            return None

        elif t1 is Size:
            if t2 is Size and arg1.isRelative == arg2.isRelative:
                newSizeVal = self.combineArgs(arg1.size, arg2.size)
                return Size(newSizeVal, arg1.isRelative)
            return None
        elif t2 is Size:
            return None
        elif t1 is str:
            if t2 is str and arg1 == arg2:
                return arg1
            return None
        elif t2 is str:
            return None
        else:
            if not issubclass(t1, RandRange):
                arg1 = RandRange(arg1, arg1)
            if not issubclass(t2, RandRange):
                arg2 = RandRange(arg2, arg2)
            return arg1.union(arg2)

    def __getitem__(self, key):
        return self.allArgs[key]

    def __str__(self):
        return self.allArgs.__str__()

    def formatForGrammar(self):
        if len(self.args) == 0:
            return ""
        else:
            return f"({', '.join(map(str, self.args))})"


class Op:
    def __init__(self, *args, **kwargs):
        perChildArgs = kwargs.get("perChildArgs", ())
        self.args = Args(args, perChildArgs)
        self.childOps = kwargs.get("childOps")
        self.ruleLabel = None

    def addParams(self, paramNames):
        self.paramNames = paramNames

    def __repr__(self):
        return f"{self.__class__.__name__}@{hex(id(self))}"

    def __str__(self):
        return self.toString(0)

    def toString(self, indent):
        spaces = "  " * indent
        s = f"{spaces}{self.__class__.__name__}{self.args.allArgs}"

        if self.childOps and len(self.childOps) > 0:
            s += "\n"
            if indent > 50:
                s += "...\n"
            newIndent = indent + 1
            s += "\n".join([c.toString(newIndent) if not isinstance(c, str) else c for c in self.childOps])
        return s

    def toStringWithIDs(self):
        return self._toStringWithIDs(0)

    def _toStringWithIDs(self, indent):
        spaces = "  " * indent
        s = f"{spaces}{self.__class__.__name__}{self.args.allArgs}({hex(id(self))})"
        if self.childOps and len(self.childOps) > 0:
            s += "\n"
            newIndent = indent + 1
            s += "\n".join([c._toStringWithIDs(newIndent) if not isinstance(c, str) else c for c in self.childOps])
        return s

    def run(self, context, scope, env):
        raise NotImplementedError

    def simplify(self, seenOps, combArgs=False):
        # Two ops that can definitely be merged should have the same hash

        ident = self.argsToHash() if combArgs else [self.__class__.__name__, *self.args.allArgs]
        if self.childOps:
            for i in range(len(self.childOps)):
                child = self.childOps[i].simplify(seenOps, combArgs)
                self.childOps[i] = child
                ident.append(child.hash)
        myHash = hash(tuple(ident))

        if myHash in seenOps:
            comboOp = seenOps[myHash]
            if combArgs:
                comboOp.augmentArgs(self)
            return comboOp
        else:
            seenOps[myHash] = self
            self.hash = myHash
            return self

    def combineWith(self, other):
        return OpChooseRuleWithPriority(perChildArgs=((0.5, 0.5), (True, True)), childOps=[self, other]).simplify({})

    def augmentArgs(self, other):
        comboArgs = self.args.combineWith(other.args)
        if comboArgs is None:
            raise RuntimeError(f"Failed to combine op:\n{self}\nwith op:\n{other}")
        else:
            self.args = comboArgs

    def argsToHash(self):
        return [self.__class__.__name__]

    # Return a fully-deterministic op that could be generated by this op
    def exampleTree(self, env):
        cs = [c.exampleTree(env) for c in self.childOps] if self.childOps else None
        newArgs, newPerChildArgs = self.args.evaluateSeparate(env)
        return type(self)(*newArgs, perChildArgs=newPerChildArgs, childOps=cs)

    # Return n fully-deterministic ops that could be generated by this op
    def examples(self, n):
        return [self.exampleTree({}) for i in range(n)]

    # First generate n fully-deterministic ops that could be generated by this op
    # Then combine these examples to try and calculate the original op (self)
    def regenOpFromExamples(self, n):
        if n <= 0:
            return None
        examples = self.examples(n)
        return self.combineMany(examples)

    @staticmethod
    def combineMany(ops):
        n = len(ops)
        return OpChooseRuleWithPriority(perChildArgs=((1 / n,) * n, (True,) * n), childOps=ops).simplify({}, True)

    def toGrammarText(self):
        MAX_RULES = 10000
        ruleNum = iter(range(MAX_RULES))
        _, grammarText = self._toGrammarText(ruleNum)
        return grammarText

    def _toGrammarText(self, ruleNum):
        # If we have already seen this operation and included it in the grammar
        # then just return the rule name and an empty string
        # since we don't want the rule to appear in the grammar more than once
        if self.ruleLabel:
            return self.ruleLabel, ""
        label = "rule" + str(next(ruleNum))
        self.ruleLabel = label
        # If this op has no children then we just return a one line rule
        # We add child args to this if needed
        ruleText = f"{label} --> {self.opName}{self.args.formatForGrammar()}"
        childText = ""
        if self.childOps is not None:
            childArgs = []
            if len(self.args.perChildArgs) == 0:
                for c in self.childOps:
                    childLabel, cText = c._toGrammarText(ruleNum)
                    childArgs.append(childLabel)
                    childText += cText
            else:
                for arg, c in zip(self.args.perChildArgs, self.childOps, strict=True):
                    childLabel, cText = c._toGrammarText(ruleNum)
                    childArgs.append(f"{arg} : {childLabel}")
                    childText += cText
            ruleText += "{" + " | ".join(childArgs) + "}"

        return label, ruleText + "\n" + childText


# Split context in given direction into given size sections
class OpSplit(Op):
    opName = "split"

    def run(self, context, scope, env):
        axis, sizes = self.args.evaluate(env)
        childScopes = scope.split(axis, sizes)
        for childOp, childScope in zip(self.childOps, childScopes, strict=True):
            childOp.run(context, childScope, env)

    def simplify(self, seenOps, combArgs=False):
        newMe = Op.simplify(self, seenOps, combArgs)
        sizes = newMe.args[1]
        newChildOps = []
        newSizes = []
        for i, child in enumerate(newMe.childOps):
            if type(child) is OpSplit and child.args[0] == newMe.args[0]:
                # Can flatten this child
                newChildOps.extend(child.childOps)
                sumChildSizes = sum([s.size for s in child.args[1] if s.isRelative])
                mult = sizes[i]
                newSizes.extend([Size(s.size * mult / sumChildSizes, True) if s.isRelative else s for s in child.sizes])
            else:
                newChildOps.append(child)
                newSizes.append(sizes[i])
        newNewMe = OpSplit(self.args[0], perChildArgs=tuple(newSizes), childOps=newChildOps)
        return Op.simplify(newNewMe, seenOps, combArgs)

    # Also include the axis and number of children in the hash
    # because we can't combine operators with these values differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0], len(self.args[1])]


# Split the scope into uniform scopes and repeat an operation on each new scope
class OpRepeat(Op):
    opName = "repeat"

    def run(self, context, scope, env):
        axis, _sizes = self.args.evaluate(env)
        size = _sizes[0]
        # There is really just one child op
        childOp = self.childOps[0]
        childScopes = scope.repeat(axis, size)

        for childScope in childScopes:
            childOp.run(context, childScope, env)

    # Also include the axis in the hash
    # because we can't combine operators with this value differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]


# Split the scope into uniform scopes and repeat an operation on each new scope
class OpRepeatN(Op):
    opName = "repeatN"

    def run(self, context, scope, env):
        axis, n = self.args.evaluate(env)
        # There is really just one child op
        childOp = self.childOps[0]
        childScopes = scope.repeatN(axis, n)

        for childScope in childScopes:
            childOp.run(context, childScope, env)

    # Also include the axis in the hash
    # because we can't combine operators with this value differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]


# Split the scope into components (e.g. faces) and apply rules to each
class OpComp(Op):
    opName = "comp"

    def run(self, context, scope, env):
        faces = self.args[0]
        childScopes = [scope.comp(face) for face in faces]
        for childOp, childScope in zip(self.childOps, childScopes, strict=True):
            childOp.run(context, childScope, env)


# Colour current context
class OpColour(Op):

    opName = "colour"

    def run(self, context, scope, env):
        col = self.args.evaluate(env)
        context.colour(col, scope)
        if self.childOps:
            self.childOps[0].run(context, scope, env)


# Given a list of rules, choose one at random according to their priorirties
class OpChooseRuleWithPriority(Op):
    def chooseChild(self, env):
        priorities, conditions = self.args.evaluate(env)[0]
        # remove children whose conditions fail
        # remember the index of the valid children in the original list though
        filteredPriorities = [(i, p) for i, p in enumerate(priorities) if conditions[i]]
        # Pick a random number less than the max cumulative priority
        rand = random() * sum(x[1] for x in filteredPriorities)
        i = 0
        cumulativePriority = filteredPriorities[0][1]
        while cumulativePriority < rand:
            i += 1
            cumulativePriority += filteredPriorities[i][1]
        return self.childOps[filteredPriorities[i][0]]

    def run(self, context, scope, env):
        scope_env = {
            **env,
            "width": scope.size[0],
            "depth": scope.size[1],
            "height": scope.size[2],
        }
        child = self.chooseChild(scope_env)
        child.run(context, scope, env)

    def exampleTree(self, env):
        return self.chooseChild(env).exampleTree(env)

    def simplify(self, seenOps, combArgs=False):
        priorities, conditions = self.args[0]
        seenChildren = defaultdict(float)
        seenConditions = {}
        for i in range(len(self.childOps)):
            child = self.childOps[i].simplify(seenOps, combArgs)
            if type(child) is OpChooseRuleWithPriority:
                for j in range(len(child.childOps)):
                    c = child.childOps[j]
                    weight = child.args[0][i] * priorities[i]
                    seenChildren[c.hash] += weight
                    childCond = child.args[0][1][j]
                    if c.hash in seenConditions:
                        seenConditions[c.hash] = (
                            seenConditions[c.hash] & childCond if childCond is not True else seenConditions[c.hash]
                        )
                    else:
                        seenConditions[c.hash] = childCond
            else:
                seenChildren[child.hash] += priorities[i]
                if child.hash in seenConditions:
                    seenConditions[child.hash] = (
                        seenConditions[child.hash] & conditions[i]
                        if conditions[i] is not True
                        else seenConditions[child.hash]
                    )
                else:
                    seenConditions[child.hash] = conditions[i]

        newChildOps = []
        newPriorities = []
        newConditions = []
        childHashes = []
        for opHash, priority in seenChildren.items():
            newChildOps.append(seenOps[opHash])
            newPriorities.append(priority)
            newConditions.append(seenConditions[opHash])
            childHashes.append(opHash)

        if len(newChildOps) == 1:
            return newChildOps[0]
        newPriorities = tuple(newPriorities)
        newConditions = tuple(newConditions)
        newOp = OpChooseRuleWithPriority(perChildArgs=(newPriorities, newConditions), childOps=newChildOps)
        if combArgs:
            ident = ("OpChooseRuleWithPriority", *childHashes)
        else:
            ident = ("OpChooseRuleWithPriority", newPriorities, *childHashes)
        myHash = hash(ident)

        if myHash in seenOps:
            comboOp = seenOps[myHash]
            if combArgs:
                comboOp.augmentArgs(newOp)
            comboOp.hash = myHash
            return comboOp
        else:
            seenOps[myHash] = newOp
            newOp.hash = myHash
            return newOp

    def _toGrammarText(self, ruleNum):
        if self.ruleLabel:
            return self.ruleLabel, ""
        label = "rule" + str(next(ruleNum))
        self.ruleLabel = label
        childText = ""
        text = ""
        for c, p in zip(self.childOps, self.args[0][0], strict=True):
            childLabel, cText = c._toGrammarText(ruleNum)
            text += f"{label} --> {childLabel} : %.5f\n" % p
            childText += cText
        return label, text + childText


# Scale the current scope
class OpResizeScope(Op):
    opName = "S"

    def run(self, context, scope, env):
        v = self.args.evaluate(env)
        self.childOps[0].run(context, scope.resize(v), env)


# Scale the current scope by factor(s)
class OpScale(Op):
    opName = "scale"

    def run(self, context, scope, env):
        v = self.args.evaluate(env)
        self.childOps[0].run(context, scope.scale(v), env)


# Translate the current object
class OpTranslate(Op):
    opName = "T"

    def run(self, context, scope, env):
        v = self.args.evaluate(env)
        self.childOps[0].run(context, scope.translate(v), env)


# Rotate the current object
class OpRotate(Op):
    opName = "R"

    def run(self, context, scope, env):
        axis, angle = self.args.evaluate(env)
        self.childOps[0].run(context, scope.rotate(axis, angle), env)


# Put a primitive in the current scope
class OpPrimitive(Op):
    opName = "I"

    def run(self, context, scope, env):
        prim = self.args[0]
        context.addPrim(prim, scope)

    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]

    def _toGrammarText(self, ruleNum):
        return f"I({self.args[0]})", ""


# Very simple parent op that just runs its child
class OpDo(Op):
    def run(self, context, scope, env):
        self.childOps[0].run(context, scope, env)

    def _toGrammarText(self, ruleNum):
        return self.childOps[0]._toGrammarText(ruleNum)


# Nil op does nothing
class OpNil(Op):
    opName = "nil"

    # Run on a scope, just leave that scope blank and do nothing
    def run(self, context, scope, env):
        pass

    def _toGrammarText(self, ruleNum):
        return "nil", ""


# Create an inset (recessed panel with frame) in the current scope
class OpInset(Op):
    opName = "inset"

    def run(self, context, scope, env):
        (amount,) = self.args.evaluate(env)
        frameOp = self.childOps[0]
        innerOp = self.childOps[1]
        frameScopes, innerScope = scope.inset(amount)
        for frameScope in frameScopes:
            frameOp.run(context, frameScope, env)
        innerOp.run(context, innerScope, env)

    def simplify(self, seenOps, combArgs=False):
        childOps = [c.simplify(seenOps, combArgs) for c in self.childOps]
        ident = ("OpInset", self.args[0])
        myHash = hash(ident)
        if myHash in seenOps:
            return seenOps[myHash]
        newOp = OpInset(self.args[0], childOps=childOps)
        seenOps[myHash] = newOp
        newOp.hash = myHash
        return newOp

    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]


# Sets the values of parameters in the environment
class OpSetParams(Op):
    def exampleTree(self, env):
        paramVals = self.args.evaluate(env)
        child = self.childOps[0]
        envNew = env.copy()
        envNew.update(zip(child.paramNames, paramVals, strict=True))
        return OpSetParams(paramVals, childOps=[child.exampleTree(envNew)])

    def run(self, context, scope, env):
        # Evaluate the param values in the current environment
        paramVals = self.args.evaluate(env)
        # The child operation is the operation that uses the params
        # set by this operation
        child = self.childOps[0]
        # Update the environment with the param values
        envNew = env.copy()
        envNew.update(zip(child.paramNames, paramVals, strict=True))
        child.run(context, scope, envNew)
