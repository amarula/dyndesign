from enum import IntEnum, auto


class ClassMergeResults(IntEnum):
    CLASS_A__A1 = auto()
    CLASS_A__A2 = auto()
    CLASS_A__M1 = auto()
    CLASS_A__M2 = auto()
    CLASS_B__A1 = auto()
    CLASS_B__M1 = auto()
    CLASS_B_CHILD__M1 = auto()
    CLASS_B_CHILD__M3 = auto()
    CLASS_C_CHILD__A2 = auto()
    CLASS_C__M1 = auto()
    CLASS_C_CHILD__A1 = auto()
    CLASS_C_CHILD__M2 = auto()
    CLASS_D__M2 = auto()
    CLASS_E__P1 = auto()
    CLASS_E__P2 = auto()
    CLASS_F__P1 = auto()
    CLASS_F__M2 = auto()
