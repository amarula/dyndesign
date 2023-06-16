import pytest

from dyndesign import mergeclasses
from .testing_results import ClassResults as cr
from .samples.sample_classes import *


def test_simple_merge():
    """Base class `A` is merged with extension class `B`: the attributes and methods of the latter overload the
    attributes and methods of the former, whereas the constructors are invoked following the order `A.__init__`,
    `B.__init__`. It is noted that `B.__init__` invokes method `m2` which is defined only in `A`, not in `B` itself.
    """
    merged_class = mergeclasses(A, B)
    merged_instance = merged_class()
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_A__M2, "Error initializing attribute `a3`"
    assert merged_instance.m1() == cr.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == cr.CLASS_A__M2, "Error calling method `m2`"


def test_merge_imported():
    """Simple test similar to `test_simple_merge`, but with classes `A` and `B` imported dynamically.
    """
    merged_class = mergeclasses("tests.samples.sample_classes_imported.A", "tests.samples.sample_classes_imported.B")
    merged_instance = merged_class()
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.m1() == cr.CLASS_B__M1, "Error overloading method `m1`"


def test_multi_merge():
    """Base class `A` is merged with two extension classes `B_child` and `C_child`, which inherits from classes `B` and
    `C` respectively. As expected, merged class extends the attributes and methods of the base class with the ones of
    the extension classes in the order in which they are passed to `merge`, while respecting the inheritance rules
    between `B` and `B_child` and between `C` and `C_child`. The constructors are invoked following the order
    `A.__init__`, `B.__init__`, `C_child.__init__`, `C.__init__`.
    """
    merged_class = mergeclasses(A, B_child, C_child)
    merged_instance = merged_class()
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_C_CHILD__A2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_B_CHILD__M3, "Error initializing attribute `a3`"
    assert merged_instance.m1() == cr.CLASS_C__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == cr.CLASS_C_CHILD__M2, "Error calling method `m2`"


def test_merge_lambda_methods():
    """This test case shows that class merging works also with methods assigned or created dynamically. In class `D`,
    method `m3` is defined as an alias of `m1`, and `m2` is defined as lambda function.
    """
    merged_class = mergeclasses(D, C_child, B)
    merged_instance = merged_class()
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_C_CHILD__A2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_D__M2, "Error initializing attribute `a3`"
    assert merged_instance.m1() == cr.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == cr.CLASS_D__M2, "Error calling method `m2`"


def test_merge_with_multi_init_args_1():
    """This test case shows how the initializing arguments are passed to the constructors of the component classes. In
    this case, both the initializing arguments are passed to constructor of class `E`, while constructor of class `B`
    is initialized with no arguments, according to its signature.
    """
    merged_class = mergeclasses(E, B)
    merged_instance = merged_class(cr.CLASS_E__P1, cr.CLASS_E__P2)
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_E__P2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_E__P1, "Error initializing attribute `a3`"
    assert merged_instance.m1() == cr.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == cr.CLASS_E__P1, "Error calling method `m2`"


def test_merge_with_multi_init_args_2():
    """Constructor of class `E` accepts both the initializing arguments, while constructor of class `F` accepts the
    first argument only, according to its signature."""
    merged_class = mergeclasses(E, F)
    merged_instance = merged_class(cr.CLASS_F__P1, cr.CLASS_E__P2)
    assert merged_instance.a1 == cr.CLASS_F__P1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_F__P1, "Error initializing attribute `a2`"
    assert merged_instance.m2() == cr.CLASS_F__M2, "Error calling method `m2`"


def test_merge_with_kw_only_args():
    """Constructor of class `E` accepts the arguments `param_1` and `param_2` as regular arguments, while constructor
    of class `G` accepts `param_1` as positional-only argument, `option` as regular argument and `kwonly` as
    keyword-only argument.
    """
    merged_class = mergeclasses(E, G)
    merged_instance = merged_class(
        param_1=cr.CLASS_E__P1,
        param_2=cr.CLASS_E__P2,
        option=cr.CLASS_G__O1,
        kwonly=cr.CLASS_G__K1
    )
    assert merged_instance.a1 == cr.CLASS_G__O1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_E__P1, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_G__K1, "Error initializing attribute `a3`"
    assert merged_instance.m2() == cr.CLASS_E__P1, "Error calling method `m2`"


def test_merge_with_no_init_args():
    """In this test case `strict_merged_args` is set to False in `mergeclasses` and no initializing argument is
    passed to initialize the merged class. As a result, the constructor of class `F`, which requires 2 positional
    parameters, is skipped. On the other hand, the constructor of class `B` is initialized with no arguments according
    to its signature.
    """
    merged_class = mergeclasses(F, B, strict_merged_args=False)
    merged_instance = merged_class()
    assert merged_instance.a1 == cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a3 == cr.CLASS_F__M2, "Error initializing attribute `a3`"
    assert merged_instance.m1() == cr.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == cr.CLASS_F__M2, "Error calling method `m2`"


def test_merge_with_missing_args_exception():
    """This test case is similar to the previous one, but with the difference that the parameter `strict_merged_args`
    of `merged_class` is not set (i.e., it is True by default). As a result, a `TypeError` exception is raised.
    """
    merged_class = mergeclasses(F, B)
    assert pytest.raises(TypeError, merged_class), "Exception `TypeError` not raised"


def test_merge_with_type_error_unrelated_exception():
    """This test case shows that a `TypeError` exception that does not arise from missing positional parameters of a
    constructor is correctly raised when `strict_merged_args` is set to False.
    """
    merged_class = mergeclasses(F, B_exception, strict_merged_args=False)
    assert pytest.raises(TypeError, merged_class), "Exception `TypeError` not raised"


def test_merge_merged_class():
    """This test case shows how merged classes can be merged in turn with other classes. In this case, merged class
    `merged_class` of test case `test_merge_with_kw_only_args` is merged with class `H`. Constructor of class `H`
    accepts `param_2` as positional-only argument, `option_2` as regular argument and `kwonly_2` as keyword-only
    argument.
    """
    merged_class = mergeclasses(E, G)
    merged_class_2 = mergeclasses(merged_class, H)
    merged_instance = merged_class_2(
        param_1=cr.CLASS_E__P1,
        param_2=cr.CLASS_E__P2,
        option=cr.CLASS_G__O1,
        kwonly=cr.CLASS_G__K1,
        option_2=cr.CLASS_H__O2,
        kwonly_2=cr.CLASS_H__K2
    )
    assert merged_instance.a1 == cr.CLASS_H__O2, "Error initializing attribute `a1`"
    assert merged_instance.a2 == cr.CLASS_E__P2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == cr.CLASS_H__K2, "Error initializing attribute `a3`"
    assert merged_instance.m2() == cr.CLASS_H__M2, "Error calling method `m2`"


def test_merge_singleton_class():
    """Singleton classes can be merged too, and the merged class inherits the singleton properties. In this case, class
    `F` is merged with dynamically-loaded singleton class `A` and then the merged class is instantiated two times: both
    the times the same instance of the merged class is returned.
    """
    merged_class = mergeclasses(F, "tests.samples.sample_singletons.A")
    merged_class(cr.CLASS_F_SING__P1)
    merged_instance = merged_class()
    assert merged_instance.a2 == cr.CLASS_F_SING__P1, "Error initializing attribute `a2`"
    assert merged_instance.m2() == cr.CLASS_F__M2, "Error calling method `m2`"


def test_merge_singleton_class_destroy():
    """Class `I` is merged with dynamically-loaded singleton class `A`, and the merged class is correctly destroyed."""
    merged_class = mergeclasses(I, "tests.samples.sample_singletons.A")
    merged_class(cr.CLASS_F_SING__P1)
    merged_class().destroy_singleton()
    merged_instance = merged_class()
    assert 'param1' not in dir(merged_instance), "Error destroying singleton `A`"
    assert merged_instance.m1() == cr.CLASS_I__M1, "Error calling method `m1`"


def test_merge_invoke_all():
    """Class `J` is merged with class `K`, and method `m1` is called for both the classes rather than being overloaded.
    """
    merged_class = mergeclasses(J, K, invoke_all=["m1"])
    merged_instance = merged_class()
    merged_instance.m1()
    assert merged_instance.a1 == cr.CLASS_J__A1, "Error calling method `J.m1`"
    assert merged_instance.a2 == cr.CLASS_K__A2, "Error calling method `K.m1`"


def test_merge_invoke_all_decorators():
    """Class `L` is merged with classes `M` and `N`, and decorators `d1` of method `N.m1` are called from both the
    classes `L` and `M` rather than being overloaded. Nevertheless, a double invocation to the decorated method `N.m1`
    (from the two instances of decorators) is prevented.
    """
    merged_class = mergeclasses(L, M, N, invoke_all=["d1"])
    merged_instance = merged_class()
    assert merged_instance.m1() == [cr.CLASS_N__ITEM_1, cr.CLASS_N__ITEM_1], ("Error: decorated method `m1` executed"
        " more than once.")
    assert merged_instance.a1 == cr.CLASS_L__A1, "Error calling decorator `L.d1`"
    assert merged_instance.a2 == cr.CLASS_M__A2, "Error calling decorator `M.d1`"


def test_merge_invoke_all_decorators_in_chain():
    """Class `L` is merged with classes `M` and `O`, and decorators `d2` of method `O.m1` are called from all the
    classes `L`, `M` and `O` following the order in which the classes are merged.
    """
    merged_class = mergeclasses(L, M, O, invoke_all=["d2"])
    merged_instance = merged_class()
    assert merged_instance.m1([]) == [
        cr.CLASS_L__ITEM_1,
        cr.CLASS_M__ITEM_1,
        cr.CLASS_O__ITEM_1,
        cr.CLASS_O__ITEM_2,
        cr.CLASS_O__ITEM_3,
        cr.CLASS_M__ITEM_2,
        cr.CLASS_L__ITEM_2,
    ], ("Error calling decorator chain.")


def test_merge_invoke_all_decorators_with_different_args():
    """Class `P` is merged with class `L`, and decorators `d2` of method `P.m1` are called from both the classes `P`
    and `L`. Decorator arguments are adapted to each signature of decorator instance, as decorator `P.d2` accepts the
    arguments `param_1, param_2` while decorator `L.d2` accepts `param_1` only.
    """
    merged_class = mergeclasses(P, L, invoke_all=["d2"])
    merged_instance = merged_class()
    assert merged_instance.m1([], cr.CLASS_P__P2) == [
        cr.CLASS_P__P2,
        cr.CLASS_L__ITEM_1,
        cr.CLASS_P__ITEM_1,
        cr.CLASS_L__ITEM_2,
    ], ("Error calling decorator chain.")
