import pytest

from dyndesign import importclass, mergeclasses
from dyndesign.exceptions import ErrorClassNotFoundInModules
from .test_nested1.test_nested2.additional_test_dyn_inheritance import AdditionalDynInheritanceTests
from .samples.sample_classes_inheritance import *
from .testing_results import ClassResults as Cr


def test_add_parents():
    """Test of the basic `dynparents_add` functions: by inheriting from `DynInheritance` special class, class `B` is
    enabled to dynamically change its superclass set. In this test, parent class `A` is dynamically added to class `B`.
    After the test, the initial parents of class `B` are restored.
    """
    B.dynparents_add(A)
    inheriting_instance = B()
    assert inheriting_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_B__M1, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"

    B.dynparents_restore()


def test_add_parents_live_instances():
    """Similar to "test_add_parents", this test demonstrates the functionality of live-updating instances of a class
    with a new set of superclasses. In this test, the `inheriting_instance` is created prior to invoking the
    `dynparents_add` API: as a result of this difference, the constructor of B is not called and `a2` and `a3`
    are unset. Anyway, it is tested that `A` is correctly added to `B`'s parents from `inheriting_instance`, as method
    `m2()` correctly returns `CLASS_A__M2`.
    """
    inheriting_instance = B()
    B.dynparents_add(A)
    assert inheriting_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert not hasattr(inheriting_instance, 'a2'), "Error initializing attribute `a2`"
    assert not hasattr(inheriting_instance, 'a3'), "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"

    B.dynparents_restore()


def test_add_parents_locked_instances():
    """By inheriting from `DynInheritanceLockedInstances` special class instead of from `DynInheritance`, class
    `BLocked` is enabled to dynamically modify its superclass set while keeping locked the class in the existing class
    instances. In greater details, `BLocked` is instantiated in `original_instance` first, then class `A` is appended
    to its superclass set, and finally `BLocked` is instantiated again in `inheriting_instance`. This test shows that
    `original_instance` is still an instance of the initial class `BLocked`, before that parent `A` is appended.
    """
    original_instance = BLocked()

    BLocked.dynparents_add(A)
    inheriting_instance = BLocked()
    assert inheriting_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_B__M1, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"

    assert original_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert not hasattr(original_instance, 'a2'), "Error initializing attribute `a2`"
    assert not hasattr(original_instance, 'a3'), "Error initializing attribute `a3`"
    assert original_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert not hasattr(original_instance, 'm2'), "Error calling method `m2`"

    BLocked.dynparents_restore()


def test_add_parents_rename_locked_instances():
    """Test similar to "test_add_parents_live_instances", but in this case the initial class `BLocked` is kept
    separate from the patched class that is renamed to `NewB`. By this way, the initial class `BLocked` is
    instantiated as the instance `original_instance` after the call to `dynparents_add`.
    """
    BLocked.dynparents_add(A, rename_to="NewB")
    inheriting_instance = NewB()
    assert inheriting_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_B__M1, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"

    original_instance = BLocked()
    assert original_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert not hasattr(original_instance, 'a2'), "Error initializing attribute `a2`"
    assert not hasattr(original_instance, 'a3'), "Error initializing attribute `a3`"
    assert original_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert not hasattr(original_instance, 'm2'), "Error calling method `m2`"

    BLocked.dynparents_restore()


def test_add_parents_keep_docstring():
    """This test verifies that the renamed class `NewB` retains the same docstring as the original class `BLocked`.
    """
    BLocked.dynparents_add(A, rename_to="NewB")
    assert NewB.__doc__ == "BLocked docstring"


def test_restore_parents():
    """This test examines the functionality of `dynparents_restore` to restore the initial superclasses of one class
    and in all its class instances. The method `safesuper`, which ensures the safe retrieval of parent class `C` when
    it is dynamically added, is also tested in the constructor of class `D`.
    """
    D.dynparents_add(C)
    inheriting_instance = D()
    assert inheriting_instance.a1 == Cr.CLASS_C__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"
    assert inheriting_instance.m3() == Cr.CLASS_C__M3, "Error calling method `m3`"

    D.dynparents_restore()
    assert inheriting_instance.a1 == Cr.CLASS_C__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"
    assert not hasattr(inheriting_instance, 'm3'), "Error overloading method `m3`"


def test_restore_parents_locked_instances():
    """Test of `dynparents_restore` with locked instances. In this case, `inheriting_instance` still inherits from `A`
    and `D` after invoking `dynparents_restore`. In contrast, `original_instance` inherits from `A` only, for being
    instantiated after the call to `dynparents_restore`.
    """
    DLocked.dynparents_add(C)
    inheriting_instance = DLocked()

    DLocked.dynparents_restore()
    original_instance = DLocked()

    assert inheriting_instance.a1 == Cr.CLASS_C__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"
    assert inheriting_instance.m3() == Cr.CLASS_C__M3, "Error calling method `m3`"

    assert original_instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert original_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert original_instance.a3 == Cr.CLASS_A__M1, "Error initializing attribute `a3`"
    assert original_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert original_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"
    assert not hasattr(original_instance, 'm3'), "Error overloading method `m3`"


def test_replace_parents():
    """Test of `dynparents_replace`. The superclasses of `D` are replaced with a set of new ones passed to the API
    `dynparents_replace`.
    """
    D.dynparents_replace(C)
    inheriting_instance = D()
    assert inheriting_instance.a1 == Cr.CLASS_C__A1, "Error initializing attribute `a1`"
    assert not hasattr(inheriting_instance, 'a2'), "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert not hasattr(inheriting_instance, 'm1'), "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"
    assert inheriting_instance.m3() == Cr.CLASS_C__M3, "Error calling method `m3`"

    D.dynparents_restore()


def test_remove_parents():
    """Test of `dynparents_remove`. The superclasses of `D` that are provided to the API `dynparents_remove` are
    removed.
    """
    D.dynparents_remove(A)
    inheriting_instance = D()
    assert not hasattr(inheriting_instance, 'a1'), "Error initializing attribute `a1`"
    assert not hasattr(inheriting_instance, 'a2'), "Error initializing attribute `a2`"
    assert not hasattr(inheriting_instance, 'a3'), "Error initializing attribute `a3`"
    assert not hasattr(inheriting_instance, 'm1'), "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_D__M2, "Error calling method `m2`"

    D.dynparents_restore()


def test_add_parents_dynamic_import():
    """In this test, it is demonstrated that both the base class and superclass set can be dynamically imported when
    the class instances are live-updated.
    """
    E = importclass('tests.samples.sample_classes_imported.E')
    E.dynparents_add('tests.samples.sample_classes_imported.A')
    inheriting_instance = E()
    assert inheriting_instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_E__M2, "Error overloading method `m2`"

    E.dynparents_restore()


def test_add_parents_dynamic_import_locked_instances_fails():
    """In case of dynamic inheritance with locked instances, dynamically importing the base class results in an error.
    """
    ELocked = importclass('tests.samples.sample_classes_imported.ELocked')
    with pytest.raises(ErrorClassNotFoundInModules):
        ELocked.dynparents_add('tests.samples.sample_classes_imported.A')


def test_dynamic_import_of_added_parents_locked_instances():
    """Dynamic inheritance with locked instances allows to dynamically import the superclass set, as shown in this
    test.
    """
    FLocked.dynparents_add('tests.samples.sample_classes_imported.A')
    inheriting_instance = FLocked()
    assert inheriting_instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_F__M2, "Error overloading method `m2`"

    FLocked.dynparents_restore()


def test_add_parents_nested_dir_locked_instances():
    """Class `BLocked`, which is loaded from the loader class `AdditionalDynInheritanceTests` of module
    `additional_test_dyn_inheritance`, undergoes an update to its superclass set with locked instances.
    """
    BLocked = AdditionalDynInheritanceTests.get_BLocked()
    inheriting_instance = BLocked()
    assert inheriting_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert inheriting_instance.a3 == Cr.CLASS_B__M1, "Error initializing attribute `a3`"
    assert inheriting_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"

    BLocked.dynparents_restore()


def test_auto_add_parents_and_mocked_methods():
    """Superclass set of class `G` is self-updated from an instance of the class itself. Additionally, method `m1` is
    passed as `mocked_methods` argument of `safesuper` method from method instance `G.m1`. The method's call can
    therefore be safely chained to the `safesuper` call, even when `G` does not inherit from `A`.
    """
    inheriting_instance = G()
    assert inheriting_instance.a1 == Cr.CLASS_G__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.m1() == Cr.CLASS_G__M1, "Error overloading method `m1`"

    inheriting_instance.self_add_A()
    assert inheriting_instance.a1 == Cr.CLASS_G__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert inheriting_instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m1`"

    G.dynparents_restore()


def test_mocked_attrs():
    """Class attribute `a1` is passed as `mocked_attrs` argument of `safesuper` from method `I.m1`. The attribute can
    therefore be safely accessed to after the `safesuper` call, even when `I` does not inherit from `H`.
    """
    original_instance = I()
    assert original_instance.m1() == Cr.CLASS_I__M1, "Error overloading method `m1`"

    I.dynparents_add(H)
    inheriting_instance = I()
    assert inheriting_instance.a1 == Cr.CLASS_H__A1, "Error initializing attribute `a1`"
    assert inheriting_instance.m1() == Cr.CLASS_H__A1, "Error overloading method `m1`"

    I.dynparents_restore()


def test_replace_parents_merge_classes():
    """This test involves modifying the superclass set of class `B` and subsequently merging the same class with class
    `A` using the `merge_classes` API.
    """
    B.dynparents_replace(C)
    merged_class = mergeclasses(A, B)
    merged_instance = merged_class()
    assert merged_instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert merged_instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert merged_instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert merged_instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert merged_instance.m2() == Cr.CLASS_A__M2, "Error calling method `m2`"
    assert merged_instance.m3() == Cr.CLASS_C__M3, "Error calling method `m3`"

    B.dynparents_restore()


def test_add_parents_dyn_decorators():
    """This test examines the dynamic decoration of method `m1` with decorator `d1` from class `M`, which is
    dynamically added to the superclass set of class `N`.
    """
    inheriting_instance = N()
    assert inheriting_instance.m1() == [Cr.CLASS_N__ITEM_1], "Error calling method `m1`"

    N.dynparents_add(M)
    assert inheriting_instance.m1() == [Cr.CLASS_N__ITEM_1, Cr.CLASS_M__ITEM_1, Cr.CLASS_N__ITEM_1], \
        "Error calling method `m1`"

    N.dynparents_restore()


def test_cannot_remove_dyn_inherit_class():
    """This test demonstrates that the special class `DynInheritance` cannot be dynamically removed from the superclass
    set.
    """
    assert D.dynparents_get() == (A,), "Error calling dynparents_get"
    D.dynparents_remove(DynInheritance)
    assert D.dynparents_get() == (A,), "Error base classes removed"
    assert D._dyn_class == DynInheritance, "Error DynInheritance removed"

    D.dynparents_restore()
