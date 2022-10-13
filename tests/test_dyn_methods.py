from dyndesign.classmerger import mergeclasses
from .testing_results import DynamicMethodsResults as cdr
from .sample_imported_methods import *


def test_simple_decoration():
    """Basic test showing that dynamic decorators can emulate the behavior of built-in static decorators. In this test,
    method `m1` is decorated with method `m2` of the same class `A`.
    """
    instance_A = A()
    assert instance_A.m1() == (cdr.CLASS_A__M1, cdr.CLASS_A__M2), "Error calling method `m1`"


def test_decoration_with_class_dynamically_imported():
    """Class `B` is merged with class `DM_B` (dynamically imported). Method `m1` of class `B` is dynamically decorated
    with method `d1` of class `DM_B`. It is noted that built-in static decorators do not allow to decorate a method
    unless it is in the current class scope.
    """
    merged_class = mergeclasses(B, "tests.sample_classes_imported.DM_B")
    merged_instance = merged_class()
    assert merged_instance.m1() == (cdr.CLASS_B__M1, cdr.CLASS_DM_B__D1), "Error calling method `m1`"


def test_decorator_not_loaded_and_still_works():
    """If a dynamic decorator method is not found, it is simply ignored and code execution proceeds normally."""
    instance_B = B()
    assert instance_B.m1() == cdr.CLASS_B__M1, "Error calling method `m1`"


def test_dynamic_context_manager_with_class_dynamically_imported():
    """Class `C` is merged with class `DM_C` (dynamically imported), and method `m1` of class `C` invokes method `d2`
    of class `DM_C` from the context manager `safezone`.
    """
    merged_class = mergeclasses(C, "tests.sample_classes_imported.DM_C")
    merged_instance = merged_class(cdr.CLASS_C__M1)
    assert merged_instance.m1() == (cdr.CLASS_C__M1, cdr.CLASS_DM_C__M1), "Error calling method `m1`"


def test_context_manager_suppress_exception_when_method_not_loaded():
    """Class `C` is instantiated without merging with class `DM_C`, thus method `d2` is not found and method `m1`
    returns `None`.
    """
    instance_C = C(cdr.CLASS_DM_C__M1)
    assert instance_C.m1() == None, "Error calling method `m1`"


def test_invocation_with_class_dynamically_imported():
    """Class `D` is merged with class `DM_D` (dynamically imported), and method `m1` of class `C` invokes method `d3`
    of class `DM_C` through the function `invoke`.
    """
    merged_class = mergeclasses(D, "tests.sample_classes_imported.DM_D")
    merged_instance = merged_class()
    assert merged_instance.m1() == cdr.CLASS_DM_D__M1, "Error calling method `m1`"


def test_invocation_method_not_loaded_and_still_works():
    """Class `D` is instantiated without merging with class `DM_D`, thus method `d3` is not found and method `m1`
    returns `None`.
    """
    instance_D = D()
    assert instance_D.m1() == None, "Error calling method `m1`"
