import pytest

from dyndesign import mergeclasses
from .testing_results import DynamicMethodsResults as DmR
from .samples.sample_imported_methods import *


def test_simple_decoration():
    """Basic test showing that dynamic decorators can emulate the behavior of built-in static decorators. In this test,
    method `m1` is decorated with method `m2` of the same class `A`.
    """
    instance_A = A()
    assert instance_A.m1() == (DmR.CLASS_A__M1, DmR.CLASS_A__M2), "Error calling method `m1`"


def test_decoration_with_class_dynamically_imported():
    """Class `B` is merged with class `DmB` (dynamically imported). Method `m1` of class `B` is dynamically decorated
    with method `d1` of class `DmB`. It is noted that built-in static decorators do not allow to decorate a method
    unless it is in the current class scope.
    """
    merged_class = mergeclasses(B, "tests.samples.sample_classes_imported.DmB")
    merged_instance = merged_class()
    assert merged_instance.m1() == (DmR.CLASS_B__M1, DmR.CLASS_DM_B__D1), "Error calling method `m1`"


def test_decorator_not_loaded():
    """If a dynamic decorator method is not found, it is simply ignored and code execution proceeds normally."""
    instance_B = B()
    assert instance_B.m1() == DmR.CLASS_B__M1, "Error calling method `m1`"


def test_dynamic_context_manager_with_class_dynamically_imported():
    """Class `C` is merged with class `DmC` (dynamically imported), and method `m1` of class `C` invokes method `d2`
    of class `DmC` from the context manager `safezone`.
    """
    merged_class = mergeclasses(C, "tests.samples.sample_classes_imported.DmC")
    merged_instance = merged_class(DmR.CLASS_C__M1)
    assert merged_instance.m1() == (DmR.CLASS_C__M1, DmR.CLASS_DM_C__D2), "Error calling method `m1`"


def test_context_manager_suppress_exceptions_when_method_not_loaded():
    """Class `C` is instantiated without merging with class `DmC`, and method `m1` returns `None` since method `d2`
    (invoked from a safe zone context manager of method `m1`) is not found.
    """
    instance_C = C(DmR.CLASS_DM_C__M1)
    assert instance_C.m1() is None, "Error calling method `m1`"


def test_context_manager_suppress_exceptions_when_function_not_found(capsys):
    """A non-existent function `does_not_exist` is invoked from a safe zone context manager, and the fallback function
    is correctly executed.
    """
    def fallback():
        print(int(DmR.MISSING_FUNCTION_RES))
    with safezone(fallback=fallback):
        does_not_exist()  # type: ignore
    captured = capsys.readouterr()
    assert captured.out == f"{DmR.MISSING_FUNCTION_RES}\n", "Error with safe zone fallback function"


def test_context_manager_suppress_exceptions_for_specific_methods():
    """Class `C` is instantiated without merging with class `DmC`, and the safe zone in method `m2` suppresses
    exception `AttributeError` only if it is raised by invoking method `d2`. Thus, an exception `AttributeError` when
    method `does_not_exist` is invoked.
    """
    instance_C = C(DmR.CLASS_DM_C__M1)
    with pytest.raises(AttributeError):
        instance_C.m2()


def test_invocation_with_class_dynamically_imported():
    """Class `D` is merged with class `DmD` (dynamically imported), and method `m1` of class `C` invokes method `d3`
    of class `DmC` through `safeinvoke`.
    """
    merged_class = mergeclasses(D, "tests.samples.sample_classes_imported.DmD")
    merged_instance = merged_class()
    assert merged_instance.m1() == DmR.CLASS_DM_D__D3, "Error calling method `m1`"


def test_invocation_method_not_loaded():
    """Class `D` is instantiated without merging with class `DmD`, thus method `d3` is not found and method `m1`
    returns `None`.
    """
    instance_D = D()
    assert instance_D.m1() is None, "Error calling method `m1`"


def test_decorator_with_fallback():
    """Method `m1` of class `E` is dynamically decorated with non-existent method `d4` while passing method `c1` as
    decorator fallback.
    """
    instance_E = E()
    assert instance_E.m1() == DmR.CLASS_E__M1, "Error calling method `m1`"
    assert instance_E.param1 == DmR.CLASS_E__C1, "Error executing decorator-not-found callback"


def test_method_invocation_with_fallback():
    """Method `m1` of class `F` attempts to invoke non-existent method `d5` while passing method `c2` as method
    fallback.
    """
    instance_F = F()
    assert instance_F.m1() == DmR.CLASS_F__M1, "Error calling method `m1`"
    assert instance_F.param1 == DmR.CLASS_F__C2, "Error executing method-not-found callback"


def test_decorator_with_method_of_parent():
    """Method `m1` of class `H` is decorated with method `d6` of the parent class."""
    instance_H = H()
    assert instance_H.m1() == (DmR.CLASS_H__M1, DmR.CLASS_DM_G__D6), "Error calling method `m1`"


def test_decorator_with_method_of_component_class():
    """Method `m1` of class `I` is decorated with method `d7` of the component class `DmI` (dynamically imported)."""
    instance_I = I()
    assert instance_I.m1() == (DmR.CLASS_I__M1, DmR.CLASS_I__A1), "Error calling method `m1`"


def test_decorator_with_multiple_methods_of_component_class():
    """Method `m1` of class `J` is decorated with methods `d8` and `d9` of the component class `DmJ` by passing the
    name of the component class instance as argument `method_sub_instance` to `decoratewith`.
    """
    instance_J = J()
    assert instance_J.m1() == (
        DmR.CLASS_DM_J__D8,
        DmR.CLASS_DM_J__D9,
        DmR.CLASS_J__M1
    ), "Error calling method `m1`"


def test_decorator_disabled_with_disable_property():
    """Method `m1` of class `K` is decorated with method `d10` of class `L` and property name "apply_decorator" is
    passed as `disable_property`.
    """
    merged_class = mergeclasses(K, L)
    instance_K_deco = merged_class(False)
    instance_K_no_deco = merged_class(True)
    assert instance_K_deco.m1() == (DmR.CLASS_L__D10, DmR.CLASS_K__M1), "Error calling method `m1` with decorator"
    assert instance_K_no_deco.m1() == DmR.CLASS_K__M1, "Error calling method `m1` without decorator"
