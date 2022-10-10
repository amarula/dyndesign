from dyndee.class_merger import ClassMerger
from .sample_classes import Results, A, B, B_child, C_child, D, E


def test_simple_merge():
    """Base class `A` is merged with extension class `B`: the attributes and methods of the latter overload the
    attributes and methods of the former, whereas the constructors are invoked following the order `A.__init__`,
    `B.__init__`. It is noted that `B.__init__` invokes method `m2` which is defined only in `A`, not in `B` itself.
    """
    merged_class = ClassMerger.merge(A, B)
    merged_object = merged_class()
    assert merged_object.a1 == Results.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_object.a2 == Results.CLASS_A__A2, "Error initializing attribute `a2`"
    assert merged_object.a3 == Results.CLASS_A__M2, "Error initializing attribute `a3`"
    assert merged_object.m1() == Results.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_object.m2() == Results.CLASS_A__M2, "Error calling method `m2`"


def test_multi_merge():
    """Base class `A` is merged with two extension classes `B_child` and `C_child`, which inherits from classes `B` and
    `C` respectively. As expected, merged class extends the attributes and methods of the base class with the ones of
    the extension classes in the order in which they are passed to `merge`, while respecting the inheritance rules
    between `B` and `B_child` and between `C` and `C_child`. The constructors are invoked following the order
    `A.__init__`, `B.__init__`, `C_child.__init__`, `C.__init__`.
    """
    merged_class = ClassMerger.merge(A, B_child, C_child)
    merged_object = merged_class()
    assert merged_object.a1 == Results.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_object.a2 == Results.CLASS_C_CHILD__A2, "Error initializing attribute `a2`"
    assert merged_object.a3 == Results.CLASS_B_CHILD__M3, "Error initializing attribute `a3`"
    assert merged_object.m1() == Results.CLASS_C__M1, "Error overloading method `m1`"
    assert merged_object.m2() == Results.CLASS_C_CHILD__M2, "Error calling method `m2`"


def test_merge_lambda_methods():
    """Class merging works also with method assigned or created dynamically. In class `D`, method `m3` is defined as an
    alias of `m1`, and `m2` is defined as lambda function.
    """
    merged_class = ClassMerger.merge(D, C_child, B)
    merged_object = merged_class()
    assert merged_object.a1 == Results.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_object.a2 == Results.CLASS_C_CHILD__A2, "Error initializing attribute `a2`"
    assert merged_object.a3 == Results.CLASS_D__M2, "Error initializing attribute `a3`"
    assert merged_object.m1() == Results.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_object.m2() == Results.CLASS_D__M2, "Error calling method `m2`"


def test_merge_with_init_params():
    """Two initializing parameters are passed to constructor of class `E`.
    """
    merged_class = ClassMerger.merge(E, B)
    merged_object = merged_class(Results.CLASS_E__P1, Results.CLASS_E__P2)
    assert merged_object.a1 == Results.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_object.a2 == Results.CLASS_E__P2, "Error initializing attribute `a2`"
    assert merged_object.a3 == Results.CLASS_E__P1, "Error initializing attribute `a3`"
    assert merged_object.m1() == Results.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_object.m2() == Results.CLASS_E__P1, "Error calling method `m2`"
