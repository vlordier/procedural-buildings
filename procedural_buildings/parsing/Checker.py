from ..Ops import Op, OpChooseRuleWithPriority


class Checker:
    def __init__(self):
        self.opFromLabel = {}

    def check(self, ruleFromLabel):
        self.ruleFromLabel = ruleFromLabel
        for label in ruleFromLabel:
            self.processLabel(label)
        return self.opFromLabel

    def createPriorityRule(self, rules):
        childOps = [r.op for r in rules]
        priorities = tuple(1 if r.priority is None else r.priority for r in rules)
        conditions = tuple(r.condition for r in rules)
        newOp = OpChooseRuleWithPriority(perChildArgs=(priorities, conditions), childOps=childOps)
        if hasattr(childOps[0], "paramNames"):
            newOp.addParams(childOps[0].paramNames)
        return newOp

    def processLabel(self, label):
        if label not in self.ruleFromLabel:
            raise RuntimeError(f"Rule with label {label} does not exist")

        rules = self.ruleFromLabel[label]
        if label not in self.opFromLabel:
            op = rules[0].op if len(rules) == 1 else self.createPriorityRule(rules)
            self.opFromLabel[label] = op
            self.processOp(op)

        return self.opFromLabel[label]

    def processOp(self, op):
        if op.childOps is not None:
            for i in range(len(op.childOps)):
                child = op.childOps[i]
                if isinstance(child, str):
                    op.childOps[i] = self.processLabel(child)
                elif isinstance(child, Op):
                    self.processOp(child)
                else:
                    raise RuntimeError(f"Op has a child of invalid type {type(child)}.")
