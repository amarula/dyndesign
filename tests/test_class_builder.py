import pytest
from types import SimpleNamespace

from dyndesign import buildclass
import dyndesign.exceptions as exc
from .samples.sample_builder_base_classes import *


def test_builder_base_class():
    """The `BaseInheritance` class is directly instantiated.
    """
    base_class = BaseInheritance(Cr.BASE_PARAM_1)
    assert base_class.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert base_class.m4() is None, "Error calling method `m4`"


def test_builder_inheritance():
    """The built class is initialized with 'option1' to True, which causes it to inherit from the `A` class.
    """
    BuiltClass = buildclass(BaseInheritance, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m4() is None, "Error calling method `m4`"


def test_builder_inheritance_empty():
    """This test is similar to the preceding test, but the option set is empty.
    """
    BuiltClass = buildclass(BaseInheritance, {})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m4() is None, "Error calling method `m4`"


def test_builder_inheritance_multiple():
    """The built class is initialized with 'option1' and 'option2' to True, which causes it to inherit from both the `A`
    and `B` classes.
    """
    BuiltClass = buildclass(BaseInheritance, {"option1": True, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"
    assert instance.m4() == Cr.CLASS_B__M1, "Error calling method `m4`"


def test_builder_inheritance_multiple_reverse():
    """The `BaseInheritanceReverseOrder` class is the same as the `BaseInheritance` class, except that the options
    `option1` and `option2` are applied in reverse order from the `@dynconfig` configuration. This affects the method
    resolution order (MRO) of parent classes `B` and `A` when the class is built with `option1` and `option2`.
    """
    BuiltClass = buildclass(BaseInheritanceReverseOrder, {"option1": True, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"
    assert instance.m4() is None, "Error calling method `m4`"


def test_builder_inheritance_multiple_at_once():
    """The built class inherits from both `A` and `B` classes when 'option1' is set to True.
    """
    BuiltClass = buildclass(BaseInheritanceMultipleClasses, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_inheritance_default_class():
    """The built class is initialized with 'option1' to False, which causes it to inherit from the default class `C`.
    """
    BuiltClass = buildclass(BaseInheritanceMultipleClasses, {"option1": False})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert not hasattr(instance, 'a1'), "Attribute `a1` should not be here"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert instance.m2() == Cr.CLASS_C__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_C__M3, "Error overloading method `m3`"


def test_builder_inheritance_already_inheriting():
    """The `BaseInheritanceAlreadyInheriting` class inherits statically from the `B` class. When the built class is
    initialized with the `option1` set to True, it also inherits dynamically from the `A` class.
    """
    BuiltClass = buildclass(BaseInheritanceAlreadyInheriting, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_inheritance_switch_option_1():
    """The built class is initialized with 'selector' switch to `OPTION_1`, which causes it to inherit from the `A`
    class.
    """
    BuiltClass = buildclass(BaseInheritanceSwitch, {"selector": Mp.OPTION_1})
    instance = BuiltClass()
    assert instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"


def test_builder_inheritance_switch_option_2():
    """The built class is initialized with 'selector' switch to `OPTION_2`, which causes it to inherit from the `B`
    class.
    """
    BuiltClass = buildclass(BaseInheritanceSwitch, {"selector": Mp.OPTION_2})
    instance = BuiltClass()
    assert instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert instance.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_inheritance_switch_default_option_with_empty_set():
    """The built class is initialized with an empty option set, which causes it to inherit from the default class `C`,
    as determined by the 'selector' switch configuration.
    """
    BuiltClass = buildclass(BaseInheritanceSwitch)
    instance = BuiltClass()
    assert instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert instance.m2() == Cr.CLASS_C__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_C__M3, "Error overloading method `m3`"


def test_builder_inheritance_switch_default_option_with_option_outside():
    """The built class is initialized with a 'selector' switch to `OPTION_3`, which is not among the available switch
    case options. This causes the built class to inherit from the default class `C`, as determined by the 'selector'
    switch configuration.
    """
    BuiltClass = buildclass(BaseInheritanceSwitch, selector=Mp.OPTION_3)
    instance = BuiltClass()
    assert instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert instance.m2() == Cr.CLASS_C__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_C__M3, "Error overloading method `m3`"


def test_builder_inheritance_recursive():
    """The built class is initialized with 'option1' to True, which causes it to inherit from the `BaseInheritance`
    class. The `BaseInheritance` class is recursively built with the same 'option1' to True, which causes it to
    inherit from the `A` class.
    """
    BuiltClass = buildclass(BaseInheritanceRecursive, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert not hasattr(instance, 'm3'), "Method `m3` should not be here"


def test_builder_inheritance_recursive_2():
    """The built class is initialized with 'option1' and 'option2' to True, which causes it to inherit from the
    `BaseInheritance` class. The `BaseInheritance` class is recursively built with same option set, which
    causes it to inherit from both the `A` and `B` classes.
    """
    BuiltClass = buildclass(BaseInheritanceRecursive, {"option1": True, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_inheritance_recursive_static():
    """The `BaseInheritanceRecursiveStatic` class inherits statically from the `BaseInheritance` class. When the
    built class is initialized with the `option1` set to True, it also inherits dynamically from the
    `BaseInheritanceInheritFromC` class. The `BaseInheritance` and `BaseInheritanceInheritFromC` classes are
    recursively built with the same 'option1' to True, which causes them to inherit from the `A` class and the `C`
    class, respectively.
    """
    BuiltClass = buildclass(BaseInheritanceRecursiveStatic, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a1 == Cr.CLASS_C__A3, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.a3 == Cr.CLASS_C__A3, "Error initializing attribute `a3`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.m3() == Cr.CLASS_C__M3, "Error overloading method `m3`"
    assert instance.m4() is None, "Error calling method `m4`"


def test_builder_composition():
    """The built class is initialized with 'option1' to True, which causes the `A` class to be instantiated as the
    component 'comp' before the `__init__` method is called.
    """
    BuiltClass = buildclass(BaseComposition, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"


def test_builder_composition_false_option():
    """The built class is initialized with 'option1' to False and 'option2' to True, which causes the `B` class to be
    instantiated as the component 'comp' before the `__init__` method is called.
    """
    BuiltClass = buildclass(BaseComposition, {"option1": False, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"


def test_builder_composition_non_matching_options():
    """The built class is initialized with `option3` set to False, which causes no class to be instantiated as the
    component `comp`.
    """
    BuiltClass = buildclass(BaseComposition, {"option3": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert not hasattr(instance, 'comp'), "Attribute `comp` should not be here"


def test_builder_composition_multiple():
    """The built class is initialized with 'option1' and 'option2' to True, which causes only the `B` class to be
    instantiated as the component 'comp' before the `__init__` method is called. The options are passed as
    `SimpleNamespace` object.
    """
    BuiltClass = buildclass(BaseComposition, SimpleNamespace(option1=True, option2=True))
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert not hasattr(instance.comp, 'a2'), "Attribute `a2` should not be here"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert not hasattr(instance.comp, 'm2'), "Method `m2` should not be here"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_composition_multiple_reverse():
    """The `BaseCompositionReverseOrder` class is the same as the `BaseComposition` class, except that the options
    `option1` and `option2` are applied in reverse order from the `@dynconfig` configuration. This affects the order in
    which the classes are instantiated as the component 'comp' and, consequently, leads to the instantiation of the `A`
    class instead of the `B` class.
    """
    BuiltClass = buildclass(BaseCompositionReverseOrder, {"option1": True, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert not hasattr(instance.comp, 'm3'), "Method `m3` should not be here"


def test_builder_composition_multiple_distinct_components_no_init():
    """The built class is initialized with 'option1' and 'option2' to True, which causes the `A` class to be
    instantiated as the component 'comp' and the `B` class to be instantiated as the component 'comp2'. The
    instantiation of the component classes occurs even when the constructor `__init__` is not present.
    """
    BuiltClass = buildclass(BaseCompositionNoInit, option1=True, option2=True)
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"
    assert instance.comp2.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp2.a1`"
    assert instance.comp2.m1() == Cr.CLASS_B__M1, "Error overloading method `comp2.m1`"
    assert instance.comp2.m3() == Cr.CLASS_B__M3, "Error overloading method `comp2.m3`"


def test_builder_composition_multiple_components_per_option():
    """The built class is initialized with 'option1' to True. This results in the instantiation of both the `A` class
    as the 'comp' component and the `B` class as the 'comp2' component.
    """
    BuiltClass = buildclass(BaseCompositionMultipleComponentsPerOption, {"option1": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"
    assert instance.comp2.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp2.a1`"
    assert instance.comp2.m1() == Cr.CLASS_B__M1, "Error overloading method `comp2.m1`"
    assert instance.comp2.m3() == Cr.CLASS_B__M3, "Error overloading method `comp2.m3`"


def test_builder_composition_adding_after_custom_method():
    """The built class is initialized with 'option1' to True, which causes the `A` class to be instantiated as the
    component 'comp' after the `m1` method is called.
    """
    BuiltClass = buildclass(BaseCompositionCustomAddingMethod, {"option1": True})
    instance = BuiltClass()
    assert not instance.m1(), "Error adding class components after method `m1`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"


def test_builder_check_component_injected_only_once():
    """Similar to the preceding test, this test is designed to ensure that the component is injected into the 'comp'
    attribute only the first time it is invoked, and not on subsequent invocations.
    """
    BuiltClass = buildclass(BaseCompositionCustomAddingMethod, {"option1": True})
    instance = BuiltClass()
    assert not instance.m1(), "Error adding class components after method `m1`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    instance.comp.a1 = Cr.BASE_PARAM_1
    assert instance.m1(), "Error invoking method `m1`"
    assert instance.comp.a1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp.a1`"


def test_builder_composition_inject_in_the_middle():
    """The built class is initialized with 'option1' to True, which causes the `A` class to be instantiated as the
    component 'comp' within the `__init__` method, precisely during the execution of the `inject_components`
    function. This approach ensures that the `A` component class is initialized with custom positional and keyword
    arguments.
    """
    BuiltClass = buildclass(BaseCompositionInjectInTheMiddle, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1, kwonly=Cr.CLASS_G__K1)
    assert not instance.a1, "Component `comp` erroneously injected before `inject_components`"
    assert instance.a2, "Component `comp` erroneously injected"
    assert instance.comp.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp.param_1`"
    assert hasattr(instance.comp, "optional"), "Attribute `optional` should not be here"
    assert instance.comp.kwonly == Cr.CLASS_G__K1, "Error initializing attribute `comp.kwonly`"


def test_builder_composition_custom_adding_method_multi():
    """The built class is initialized with 'option1' to True, which causes:
    1- the `A` class to be instantiated as the component 'comp' after the `__init__` method;
    2- the component 'comp' to be overwritten by a new instance of `B` class after the `m2` method.
    """
    BuiltClass = buildclass(BaseCompositionCustomAddingMethodMulti, {"option1": True})
    instance = BuiltClass()
    assert not instance.a1, "Error adding class components after method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    # Class B Loaded before `m2`
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error re-initializing attribute `comp.a1`"
    assert instance.m1() == Cr.CLASS_B__M1, "Error re-overloading method `comp.m1`"
    assert instance.m3() == Cr.CLASS_B__M3, "Error re-overloading method `comp.m3`"


def test_builder_composition_custom_adding_method_inline():
    """Similar to the preceding test, in this test the components are injected using `@dynconfig` as decorator of each
    injection method, as opposed to applying it as a class decorator.
    """
    BuiltClass = buildclass(BaseCompositionCustomInlineMethods, {"option1": True})
    instance = BuiltClass()
    assert instance.a1, "Error adding class components before method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"
    # Class B Loaded before `m3`
    assert instance.m3() == Cr.CLASS_B__M3, "Error re-overloading method `comp.m3`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error re-initializing attribute `comp.a1`"
    assert instance.m1() == Cr.CLASS_B__M1, "Error re-overloading method `comp.m1`"


def test_builder_composition_custom_adding_method_inline2():
    """The built class is initialized with 'option1' to True, which causes:
    1- the `A` class to be instantiated as the component 'comp' after the `__init__` method;
    2- the component 'comp' to be overwritten by a new instance of `C` class after the `m3` method. This replacement is
    contingent upon the conditions that 'option1' is True and 'option2' is not.
    """
    BuiltClass = buildclass(BaseInheritanceCompositionCustomInlineMethodsAdvanced, {"option1": True})
    instance = BuiltClass()
    assert not instance.a1, "Error adding class components before method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Attribute `comp.a1` erroneously changed"
    assert not instance.m2(), "Error overloading method `comp.m2`"
    # Class C Loaded before `m3`
    assert instance.m3() == Cr.CLASS_C__M3, "Error re-overloading method `comp.m3`"
    assert not hasattr(instance.comp, 'a1'), "Attribute `a1` should not be here"
    assert instance.comp.a3 == Cr.CLASS_C__A3, "Error re-initializing attribute `comp.a3`"


def test_builder_composition_custom_adding_method_inline_and_inherited():
    """The built class is initialized with 'option1' and 'option2' to True, which causes:
    1- the `A` class to be instantiated as the component 'comp' after the `__init__` method;
    2- the built class to inherit from the `G` class;
    3- the component 'comp' to be overwritten by a new instance of `B` class before the `m2` method;
    4- a new instance of `A` class to be assigned to 'comp2' before `m2` method;
    """
    BuiltClass = buildclass(BaseInheritanceCompositionCustomInlineMethodsAdvanced, {"option1": True, "option2": True})
    instance = BuiltClass(Cr.BASE_PARAM_1, optional=Cr.CLASS_G__O1, kwonly=Cr.CLASS_G__K1)
    assert instance.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_G.param_1`"
    assert instance.optional == Cr.CLASS_G__O1, "Error initializing attribute `comp_G.optional`"
    assert instance.kwonly == Cr.CLASS_G__K1, "Error initializing attribute `comp_G.kwonly`"
    assert not instance.a1, "Error adding class components before method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    # Class B and comp2.A Loaded before `m2`
    assert instance.m2() == Cr.CLASS_B__M3, "Error overloading method `comp.m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert not hasattr(instance.comp, 'a2'), "Attribute `a2` should not be here"
    assert instance.comp2.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp2.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    # Class C NOT Loaded before `m3`
    assert instance.m3() == Cr.CLASS_B__M3, "Error re-overloading method `comp.m3`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Attribute `comp.a1` erroneously changed"


def test_builder_composition_custom_adding_method_inline_load_all_after():
    """Similar to the preceding test, in this test the components are injected using the configuration setting
    `add_components_after_method=True` from the `@dynconfig` class decorator.
    """
    BuiltClass = buildclass(BaseCompositionCustomInlineMethodsAdvancedLoadAllAfter, {"option1": True, "option2": True})
    instance = BuiltClass()
    assert not instance.a1, "Error adding class components before method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    # Class B and comp2.A Loaded after `m1`
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert not hasattr(instance.comp, 'a2'), "Attribute `a2` should not be here"
    assert instance.comp2.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp2.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.m2() == Cr.CLASS_B__M3, "Error overloading method `comp.m2`"
    # Class C NOT Loaded after `m3`
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Attribute `comp.a1` erroneously changed"
    assert instance.m3() == Cr.CLASS_B__M3, "Error re-overloading method `comp.m3`"


def test_builder_composition_custom_adding_method_inline_switch():
    """The built class is initialized with 'selector' switch to `OPTION_1`, which causes the `A` class to be
    instantiated as the component 'comp' before the `__init__` method;
    """
    BuiltClass = buildclass(BaseCompositionCustomInlineMethodsSwitch, {"selector": Mp.OPTION_1})
    instance = BuiltClass()
    assert instance.a1, "Error adding class components before method `__init__`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"


def test_builder_composition_base_class():
    """The `BaseCompositionUseComponent` class is directly instantiated.
    """
    base_class = BaseCompositionUseComponent(Cr.BASE_PARAM_1)
    assert not hasattr(base_class, 'comp')


def test_builder_composition_default_class():
    """The built class is initialized with an empty option set, which causes the default `B` class to be
    instantiated as the component 'comp' before the `__init__` method is called.
    """
    BuiltClass = buildclass(BaseCompositionUseComponent, {})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `comp.a2`"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `comp.m3`"


def test_builder_composition_adapt_arguments():
    """The built class is initialized with 'option1' to True, which causes the `A`, `G`, and `H` classes to be
    instantiated before the `__init__` method as the components 'comp_A', 'comp_G', and 'comp_H', respectively. The
    arguments used to instantiate each component are adapted from the ones used to instantiate the built class.
    """
    BuiltClass = buildclass(BaseCompositionAdaptArguments, {"option1": True})
    instance = BuiltClass(
        Cr.BASE_PARAM_1,
        Cr.BASE_PARAM_2,
        optional=Cr.CLASS_G__O1,
        optional_2=Cr.CLASS_H__O2,
        kwonly=Cr.CLASS_G__K1,
        kwonly_2=Cr.CLASS_H__K2
    )
    assert instance.a1 == Cr.BASE_PARAM_1, "Error initializing attribute `a1`"
    assert instance.comp_A.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp_A.a1`"
    assert instance.comp_A.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp_A.a2`"
    assert instance.comp_A.m1() == Cr.CLASS_A__M1, "Error overloading method `comp_A.m1`"
    assert instance.comp_A.m2() == Cr.CLASS_A__M2, "Error overloading method `comp_A.m2`"
    assert instance.comp_G.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_G.param_1`"
    assert instance.comp_G.optional == Cr.CLASS_G__O1, "Error initializing attribute `comp_G.optional`"
    assert instance.comp_G.kwonly == Cr.CLASS_G__K1, "Error initializing attribute `comp_G.kwonly`"
    assert instance.comp_H.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_H.param_1`"
    assert instance.comp_H.param_2 == Cr.BASE_PARAM_2, "Error initializing attribute `comp_H.param_2`"
    assert instance.comp_H.optional_2 == Cr.CLASS_H__O2, "Error initializing attribute `comp_H.optional_2`"
    assert instance.comp_H.kwonly_2 == Cr.CLASS_H__K2, "Error initializing attribute `comp_H.kwonly_2`"


def test_builder_composition_adapt_arguments_not_enough_init_args():
    """This test shows that if a class built as in the preceding test is instantiated with fewer positional arguments
    than the ones required by at least one component, a `TypeError` exception is raised.
    """
    BuiltClass = buildclass(BaseCompositionAdaptArguments, {"option1": True})
    with pytest.raises(TypeError):
        BuiltClass(Cr.BASE_PARAM_1)


def test_builder_composition_adapt_arguments_no_strict_missing_args():
    """This test demonstrates that if a class, constructed similarly to the previous test except for the
    `strict_missing_args` option being set to False, is instantiated with fewer positional arguments, no `TypeError`
    exception is raised. Instead, the corresponding components (i.e., 'comp_H') are simply not instantiated.
    """
    BuiltClass = buildclass(BaseCompositionAdaptArgumentsNoStrictMissingArgs, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1, optional=Cr.CLASS_G__O1, kwonly=Cr.CLASS_G__K1)
    assert instance.comp_A.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp_A.a1`"
    assert instance.comp_A.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp_A.a2`"
    assert instance.comp_A.m1() == Cr.CLASS_A__M1, "Error overloading method `comp_A.m1`"
    assert instance.comp_A.m2() == Cr.CLASS_A__M2, "Error overloading method `comp_A.m2`"
    assert instance.comp_G.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_G.param_1`"
    assert instance.comp_G.optional == Cr.CLASS_G__O1, "Error initializing attribute `comp_G.optional`"
    assert instance.comp_G.kwonly == Cr.CLASS_G__K1, "Error initializing attribute `comp_G.kwonly`"
    assert not hasattr(instance, "comp_H"), "Attribute `comp_H` erroneously initialized"


def test_builder_composition_adapt_arguments_from_self():
    """The built class is initialized with 'option1' to True, which causes the `G` and `H` classes to be instantiated
    after the `__init__` method as the components 'comp_G' and 'comp_H', respectively. The class `H` is instantiated
    with additional positional and keyword parameters derived from the `self` attributes.
    """
    BuiltClass = buildclass(BaseCompositionAdaptArgumentsFromSelf, {"option1": True})
    instance = BuiltClass(
        Cr.BASE_PARAM_1,
        optional=Cr.CLASS_G__O1,
        optional_2=Cr.CLASS_H__O2,
        kwonly=Cr.CLASS_G__K1
    )
    assert instance.a1 == Cr.BASE_PARAM_2_ALT, "Error initializing attribute `a1`"
    assert instance.comp_G.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_G.param_1`"
    assert instance.comp_G.optional == Cr.CLASS_G__O1, "Error initializing attribute `comp_G.optional`"
    assert instance.comp_G.kwonly == Cr.CLASS_G__K1, "Error initializing attribute `comp_G.kwonly`"
    assert instance.comp_H.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_H.param_1`"
    assert instance.comp_H.param_2 == Cr.BASE_PARAM_2_ALT, "Error initializing attribute `comp_H.param_2`"
    assert instance.comp_H.optional_2 == Cr.CLASS_H__O2, "Error initializing attribute `comp_H.optional_2`"
    assert instance.comp_H.kwonly_2 == Cr.CLASS_H__K2, "Error initializing attribute `comp_H.kwonly_2`"


def test_builder_composition_adapt_arguments_filter():
    """The built class is initialized with 'option1' to True, which causes the `H` class to be instantiated after the
    `__init__` method as the components 'comp'. The class `H` is instantiated by excluding positional arguments
    beyond the initial one, and subsequently adding an extra positional parameter derived from the attributes of `self`.
    """
    BuiltClass = buildclass(BaseCompositionAdaptArgumentsFilter, {"option1": True})
    instance = BuiltClass(
        Cr.BASE_PARAM_1,
        Cr.BASE_PARAM_2,
        optional_2=Cr.CLASS_H__O2,
        kwonly_2=Cr.CLASS_H__K2
    )
    assert instance.a1 == Cr.BASE_PARAM_1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.BASE_PARAM_2, "Error initializing attribute `a2`"
    assert instance.comp.param_1 == Cr.BASE_PARAM_1, "Error initializing attribute `comp_H.param_1`"
    assert instance.comp.param_2 == Cr.BASE_PARAM_2_ALT, "Error initializing attribute `comp_H.param_2`"
    assert instance.comp.optional_2 == Cr.CLASS_H__O2, "Error initializing attribute `comp_H.optional_2`"
    assert instance.comp.kwonly_2 == Cr.CLASS_H__K2, "Error initializing attribute `comp_H.kwonly_2`"


def test_builder_composition_recursive():
    """The built class is initialized with 'option1' to True, which causes the `BaseComposition` class to be
    instantiated as the component 'comp_base' before the `__init__` method is called. The `BaseComposition` class is
    recursively built with the same 'option1' to True, which causes the `A` class to be instantiated as the component
    'comp_base.comp'.
    """
    BuiltClass = buildclass(BaseCompositionRecursive, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.comp_base.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.comp_base.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp_base.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp_base.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp.a2`"
    assert instance.comp_base.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp.m1`"
    assert instance.comp_base.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp.m2`"


def test_builder_composition_recursive_static_base():
    """The `BaseCompositionRecursiveStatic` class is directly instantiated to test that the static component `comp_base`
    is instantiated with the `BaseComposition` class, which is not built.
    """
    instance = BaseCompositionRecursiveStatic(Cr.BASE_PARAM_1)
    assert instance.comp_base.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.comp_base.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert not hasattr(instance.comp_base, "comp"), "Class `BaseComposition` erroneously configured"


def test_builder_composition_recursive_static():
    """The `BaseCompositionRecursiveStatic` class incorporates a static component named `BaseComposition`. Upon
    initializing it with the `option1` configured as True, an additional dynamic component `B` is instantiated. The
    `BaseComposition` class is recursively built with the same 'option1' to True through an explicit call to
    `buildclass`, which causes the `A` class to be instantiated as the component 'comp_base.comp'.
    """
    BuiltClass = buildclass(BaseCompositionRecursiveStatic, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_1)
    assert instance.comp_base.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.comp_base.a2 == Cr.BASE_PARAM_1, "Error initializing attribute `a2`"
    assert instance.comp_base.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp_base.a1`"
    assert instance.comp_base.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `comp_base.a2`"
    assert instance.comp_base.comp.m1() == Cr.CLASS_A__M1, "Error overloading method `comp_base.m1`"
    assert instance.comp_base.comp.m2() == Cr.CLASS_A__M2, "Error overloading method `comp_base.m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `comp.m3`"


def test_builder_composition_disable_recursion():
    """The built class is initialized with 'option1' to True, which causes the `BaseComposition` class to be
    instantiated as the component 'comp'. However, the `build_recursively` setting to False prevents the class
    `BaseComposition` to be recursively built.
    """
    BuiltClass = buildclass(BaseCompositionDisableRecursion, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_2)
    assert instance.a1 == Cr.BASE_PARAM_1, "Error initializing attribute `a1`"
    assert instance.comp.INTEGRITY_CHECK == Cr.INTEGRITY_CHECK_1, "Base class has changed after building"
    assert instance.comp.a2 == Cr.BASE_PARAM_2, "Error initializing attribute `comp.a2`"
    assert not hasattr(instance.comp, "comp"), "Class `BaseComposition` erroneously configured"


def test_builder_composition_conditional_options():
    """The built class is initialized with three combinations of 'option1', 'option2', and 'option3' to test the
    conditional option `option1 and option2 or option3`.
    """
    BuiltClass = buildclass(BaseCompositionConditionalOptions, {"option1": True})
    instance = BuiltClass()
    assert not hasattr(instance, "comp"), "Class `BaseCompositionConditionalOptions` erroneously configured"

    BuiltClass = buildclass(BaseCompositionConditionalOptions, {"option1": True, "option2": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"

    BuiltClass = buildclass(BaseCompositionConditionalOptions, {"option3": True})
    instance = BuiltClass()
    assert instance.comp.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"


def test_builder_composition_threshold_option():
    """The built class is initialized with values both below and above a specific threshold. In the latter scenario,
    the `A` class is instantiated as the 'comp' component.
    """
    BuiltClass = buildclass(BaseCompositionThresholdOption, {"value": Mp.LT_THRESHOLD_VALUE})
    instance = BuiltClass()
    assert not hasattr(instance, "comp"), "Class `BaseCompositionConditionalOptions` erroneously configured"

    BuiltClass = buildclass(BaseCompositionThresholdOption, {"value": Mp.GT_THRESHOLD_VALUE})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"


def test_builder_composition_threshold_option_with_class_attributes():
    """This test is similar to the preceding test, but the threshold value is derived from the self attribute rather
    than being hardcoded in the condition.
    """
    BuiltClass = buildclass(BaseCompositionThresholdOptionWithClassAttr, {"value": Mp.LT_THRESHOLD_VALUE})
    instance = BuiltClass()
    assert not hasattr(instance, "comp"), "Class `BaseCompositionConditionalOptions` erroneously configured"

    BuiltClass = buildclass(BaseCompositionThresholdOptionWithClassAttr, {"value": Mp.GT_THRESHOLD_VALUE})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"


def test_builder_inheritance_composition_with_no_init():
    """The built class is initialized with 'option1' to True, which causes:
    1- the built class to inherit from the `A` class
    1- the `B` class to be instantiated as the component 'comp', even if the constructor `__init__` is not present.
    """
    BuiltClass = buildclass(BaseInheritanceCompositionWithNoInit, {"option1": True})
    instance = BuiltClass()
    assert instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `comp.m3`"


def test_builder_inheritance_composition_import():
    """Similar to the preceding test, in this test the dependent classes are dynamically imported from the
    corresponding packages in a directory specified in the `class_builder_base_dir` global parameter.
    """
    BuiltClass = buildclass(BaseInheritanceCompositionImport, {"option1": True})
    instance = BuiltClass(Cr.BASE_PARAM_2)
    assert instance.a1 == Cr.BASE_PARAM_1, "Error initializing attribute `a1`"
    assert instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `comp.m1`"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `comp.m3`"


def test_builder_inheritance_composition_config_class():
    """Similar to the preceding two tests, in this test the configuration is passed to `@dynconfig` as a separated
    configuration class rather than as decorator parameters.
    """
    BuiltClass = buildclass(BaseInheritanceCompositionClassConfigured, {"option1": True})
    instance = BuiltClass()
    assert instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert instance.m1() == Cr.CLASS_A__M1, "Error overloading method `m1`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `comp.m1`"


def test_builder_inheritance_composition_configuration_imported():
    """Similar to the preceding test, in this test the configuration is passed to `@dynconfig` as a separated
    configuration class dynamically imported.
    """
    BuiltClass = buildclass(BaseInheritanceCompositionClassConfigurationImported, {"option1": True})
    instance = BuiltClass()
    assert instance.a2 == Cr.CLASS_A__A2, "Error initializing attribute `a2`"
    assert not instance.m1(), "Component `comp` erroneously injected before method `m1`"
    assert instance.m2() == Cr.CLASS_A__M2, "Error overloading method `m2`"
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `comp.a1`"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `comp.m3`"


def test_builder_composition_config_class_with_attrs():
    """Similar to the 'test_builder_composition_multiple' test, in this test the configuration is passed to
    `@dynconfig` as a separated configuration class and the `component_attr` is set to 'comp' as global class setting
    from the same configuration class.
    """
    BuiltClass = buildclass(BaseCompositionClassConfiguredWithComponentAttr, {"option1": True, "option2": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"
    assert not hasattr(instance.comp, 'a2'), "Attribute `a2` should not be here"
    assert instance.comp.m1() == Cr.CLASS_B__M1, "Error overloading method `m1`"
    assert not hasattr(instance.comp, 'm2'), "Method `m2` should not be here"
    assert instance.comp.m3() == Cr.CLASS_B__M3, "Error overloading method `m3`"


def test_builder_composition_config_class_with_conditions():
    """Similar to the 'test_builder_composition_conditional_options' test, in this test the configuration is passed to
    `@dynconfig` as a separated configuration class where the conditional option `option1 and option2` is configured
    using `dynconfig.set_configuration`.
    """
    BuiltClass = buildclass(BaseCompositionClassConfiguredWithConditions, {"option1": True})
    instance = BuiltClass()
    assert not hasattr(instance, "comp"), "Class `BaseCompositionConditionalOptions` erroneously configured"

    BuiltClass = buildclass(BaseCompositionClassConfiguredWithConditions, {"option1": True, "option2": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"


def test_builder_composition_config_class_with_lambda_conditions():
    """Similar to the preceding test, in this test the conditional option is passed as a lambda function. Additionally,
    the default class is set globally.
    """
    BuiltClass = buildclass(BaseCompositionClassConfiguredWithLambdaConditions, {"option1": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_B__A1, "Error initializing attribute `a1`"

    BuiltClass = buildclass(BaseCompositionClassConfiguredWithLambdaConditions, {"option1": True, "option2": True})
    instance = BuiltClass()
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `a1`"


def test_builder_global_config():
    """Test for the global configuration of `dynconfig` using `set_global`. After that `add_components_after_method` is
    globally set to True, the built class is initialized with 'option1' to True. This causes the `A` class to be
    instantiated as the component 'comp' after the method `m1`.
    """
    BuiltClass = buildclass(BaseCompositionCustomGlobalConfig, {"option1": True})
    instance = BuiltClass()
    assert not instance.m1(), "Error adding class components after method `m1`"
    assert instance.comp.a1 == Cr.CLASS_A__A1, "Error initializing attribute `comp.a1`"


def test_builder_exception_missing_dependency():
    """A `ClassConfigMissingDependency` exception is raised if a `ClassConfig` node lacks either a `component_class` or
    an `inherit_from` field.
    """
    with pytest.raises(exc.ClassConfigMissingDependency):
        @dynconfig({"option1": ClassConfig()})
        class BaseExceptionMissingDependency:
            ...


def test_builder_exception_dependency_overflow():
    """A `ClassConfigDependencyOverflow` exception is raised if a `ClassConfig` node includes both the
    `component_class` and `inherit_from` fields.
    """
    with pytest.raises(exc.ClassConfigDependencyOverflow):
        @dynconfig({"option1": ClassConfig(inherit_from=A, component_class=B)})
        class BaseExceptionDependencyOverflow:
            ...


def test_builder_exception_missing_component_attr():
    """A `ClassConfigMissingComponentAttr` exception is raised if a `ClassConfig` node of a component class lacks the
    `component_attr` field.
    """
    with pytest.raises(exc.ClassConfigMissingComponentAttr):
        @dynconfig({"option1": ClassConfig(component_class=A)})
        class BaseExceptionMissingComponentAttr:
            ...

        buildclass(BaseExceptionMissingComponentAttr, {"option1": True})


def test_builder_exception_missing_component_injection_method():
    """A `ClassConfigMissingComponentInjectionMethod` exception is raised if a `ClassConfig` node of a component
    class lacks the method specified in the `injection_method` field.
    """
    with pytest.raises(exc.ClassConfigMissingComponentInjectionMethod):
        @dynconfig({
            "option1": ClassConfig(component_class=A, component_attr="comp", injection_method="non_existent")
        })
        class BaseExceptionMissingComponentInjectionMethod:
            ...

        buildclass(BaseExceptionMissingComponentInjectionMethod, {"option1": True})
