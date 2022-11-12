from enum import Enum
class VarianceType(Enum):
    DELETION = 0
    INSERTION_BIGGER = 1
    INSERTION_SMALLER = 2
    TANDEM = 3
    INVERSION = 4
    TRANSLOCATION = 5