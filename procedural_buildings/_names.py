from enum import StrEnum


class OpName(StrEnum):
    SPLIT = "split"
    REPEAT = "repeat"
    REPEATN = "repeatN"
    COMP = "comp"
    COLOUR = "colour"
    NIL = "nil"
    I = "I"  # noqa: E741
    S = "S"
    T = "T"
    R = "R"
    SCALE = "scale"
    INSET = "inset"
    OPENING = "opening"
    DO = "do"
    FLIP = "flip"
    MATERIAL = "material"


class Axis(StrEnum):
    X = "x"
    Y = "y"
    Z = "z"


class Face(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
