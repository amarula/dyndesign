from typing import Optional, Type
from types import SimpleNamespace

from dyndesign import dynconfig, safesuper, safeinvoke, safezone, ClassConfig, LocalClassConfig
from .sample_builder_components import *
from ..testing_results import ClassResults as Cr, MiscParams as Mp


@dynconfig({
    "option1": ClassConfig(inherit_from=A),
    "option2": ClassConfig(inherit_from=B),
})
class BaseInheritance:
    INTEGRITY_CHECK = Cr.INTEGRITY_CHECK_1

    def __init__(self, param_1):
        super().__init__()
        self.a2 = param_1

    def m4(self):
        return safeinvoke("m1", safesuper(A, self))


@dynconfig(
    {
        "option1": ClassConfig(inherit_from=A),
        "option2": ClassConfig(inherit_from=B),
    },
    option_order=("option2", "option1")
)
class BaseInheritanceReverseOrder:
    def __init__(self, param_1):
        super().__init__()
        self.a2 = param_1

    def m4(self):
        return safeinvoke("m1", safesuper(A, self))


@dynconfig({
    "option1": ClassConfig(inherit_from=(A, B), default_class=C),
})
class BaseInheritanceMultipleClasses:
    def __init__(self, param_1):
        super().__init__()
        self.a2 = param_1


@dynconfig({
    "option1": ClassConfig(inherit_from=A),
})
class BaseInheritanceAlreadyInheriting(B):
    def __init__(self, param_1):
        super().__init__()
        self.a2 = param_1


@dynconfig({
    "selector": {
        Mp.OPTION_1: ClassConfig(inherit_from=A),
        Mp.OPTION_2: ClassConfig(inherit_from=B),
        dynconfig.SWITCH_DEFAULT: ClassConfig(inherit_from=C)
    }
})
class BaseInheritanceSwitch:
    ...


@dynconfig({
    "option1": ClassConfig(inherit_from=C),
})
class BaseInheritanceInheritFromC:
    a3: Optional[int] = None

    def __init__(self):
        super().__init__()
        self.a1 = self.a3


@dynconfig({
    "option1": ClassConfig(inherit_from=BaseInheritance),
})
class BaseInheritanceRecursive:
    def __init__(self, param_1):
        super().__init__(param_1)
        safesuper(A, self).__init__()


@dynconfig({
    "option1": ClassConfig(inherit_from=BaseInheritanceInheritFromC),
})
class BaseInheritanceRecursiveStatic(BaseInheritance):
    def __init__(self, param_1):
        super().__init__(param_1)
        safesuper(A, self).__init__()


@dynconfig({
    "option1": ClassConfig(component_attr="comp", component_class=A),
    "option2": ClassConfig(component_attr="comp", component_class=B),
})
class BaseComposition:
    INTEGRITY_CHECK = Cr.INTEGRITY_CHECK_1

    def __init__(self, param_1):
        self.a2 = param_1


@dynconfig(
    {
        "option1": ClassConfig(component_attr="comp", component_class=A),
        "option2": ClassConfig(component_attr="comp", component_class=B),
    },
    option_order=("option2", "option1")
)
class BaseCompositionReverseOrder:
    def __init__(self, param_1):
        self.a2 = param_1


@dynconfig({
    "option1": ClassConfig(component_attr="comp", component_class=A),
    "option2": ClassConfig(component_attr="comp2", component_class=B),
})
class BaseCompositionNoInit:
    ...


@dynconfig({
    "option1": (
            ClassConfig(component_attr="comp", component_class=A),
            ClassConfig(component_attr="comp2", component_class=B),
    )
})
class BaseCompositionMultipleComponentsPerOption:
    ...


@dynconfig({
    "option1": ClassConfig(component_attr="comp", component_class=A, default_class=B)
})
class BaseCompositionUseComponent:
    def __init__(self, param_1):
        self.comp: Type
        with safezone('comp'):
            self.comp.a2 = param_1


class BaseCompositionComponentListConfigClass:
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(
        component_attr="comp_list",
        structured_component_type=list
    )
    option1 = ClassConfig(component_class=A)
    option2 = ClassConfig(component_class=B)


@dynconfig(BaseCompositionComponentListConfigClass)
class BaseCompositionComponentList:
    ...


@dynconfig(
    {
        "option1": ClassConfig(component_class=A, structured_component_key="a"),
        "option2": ClassConfig(component_class=B, structured_component_key="b"),
    },
    component_attr="comp_dict",
    structured_component_type=dict
)
class BaseCompositionComponentDict:
    ...


@dynconfig(
    {
        "option1": ClassConfig(component_class=A, structured_component_key="a"),
        "option2": ClassConfig(component_class=B, structured_component_key="b"),
    },
    component_attr="comp_obj",
    structured_component_type=SimpleNamespace
)
class BaseCompositionComponentSimpleNamespace:
    ...


@dynconfig(
    {
        "option1": ClassConfig(component_attr="comp", component_class=A)
    },
    injection_method='m1',
    add_components_after_method=True
)
class BaseCompositionCustomAddingMethod:
    def m1(self):
        return hasattr(self, 'comp')


@dynconfig({
    "option1": ClassConfig(component_attr="comp", component_class=G)
})
class BaseCompositionInjectInTheMiddle:
    def __init__(self, param_1, kwonly=None):
        self.a1 = hasattr(self, 'comp')
        dynconfig.inject_components(param_1, kwonly=kwonly)
        self.a2 = hasattr(self, 'comp')


@dynconfig(
    {
        "option1": (
                ClassConfig(component_attr="comp", component_class=A),
                ClassConfig(component_attr="comp", component_class=B, injection_method='m2'),
        )
    },
    add_components_after_method=True
)
class BaseCompositionCustomAddingMethodMulti:
    def __init__(self):
        self.comp: Type
        self.a1 = hasattr(self, 'comp')

    def m1(self):
        return self.comp.m1()

    def m2(self):
        return self.comp.m2()

    def m3(self):
        return self.comp.m3()


@dynconfig()
class BaseCompositionCustomInlineMethods:
    @dynconfig({"option1": ClassConfig(component_attr="comp", component_class=A)})
    def __init__(self):
        self.comp: Type
        self.a1 = hasattr(self, 'comp')

    def m1(self):
        return self.comp.m1()

    def m2(self):
        return self.comp.m2()

    @dynconfig({"option1": ClassConfig(component_attr="comp", component_class=B)})
    def m3(self):
        return self.comp.m3()


@dynconfig(add_components_after_method=True)
class BaseCompositionCustomInlineMethodsAdvancedLoadAllAfter:
    @dynconfig({"option1": ClassConfig(component_attr="comp", component_class=A)})
    def __init__(self):
        self.comp: Type
        self.a1 = hasattr(self, 'comp')

    @dynconfig({
        "option2": (
                ClassConfig(component_attr="comp", component_class=B),
                ClassConfig(component_attr="comp2", component_class=A),
        )
    })
    def m1(self):
        return self.comp.m1()

    @dynconfig({
        lambda option1, option2: option1 and not option2:
            ClassConfig(component_attr="comp", component_class=C)
    })
    def m2(self):
        return safeinvoke("m3", self.comp)

    def m3(self):
        return self.comp.m3()


@dynconfig({
    "selector1": {
        Mp.OPTION_1: ClassConfig(component_class=A),
        Mp.OPTION_2: ClassConfig(component_class=B),
    },
    "DYNDESIGN_LOCAL_CONFIG": LocalClassConfig(component_attr="comp")
})
class BaseCompositionFakeSelectorSwitch:
    ...

@dynconfig()
class BaseCompositionCustomInlineMethodsSwitch:
    @dynconfig({
        "selector": {
            Mp.OPTION_1: ClassConfig(component_attr="comp", component_class=A),
            Mp.OPTION_2: ClassConfig(component_attr="comp", component_class=B)
        }
    })
    def __init__(self):
        self.a1 = hasattr(self, 'comp')


@dynconfig({
    "option2": ClassConfig(inherit_from=G),
})
class BaseInheritanceCompositionCustomInlineMethodsAdvanced:
    @dynconfig({"option1": ClassConfig(component_attr="comp", component_class=A, add_components_after_method=True)})
    def __init__(self, *args, **kwargs):
        self.comp: Type
        self.a1 = hasattr(self, 'comp')
        super().__init__(*args, **kwargs)

    def m1(self):
        return self.comp.m1()

    @dynconfig({"option2": (
            ClassConfig(component_attr="comp", component_class=B),
            ClassConfig(component_attr="comp2", component_class=A),
    )})
    def m2(self):
        return safeinvoke("m3", self.comp)

    @dynconfig({
        lambda option1, option2: option1 and not option2:
            ClassConfig(component_attr="comp", component_class=C)
    })
    def m3(self):
        return self.comp.m3()


@dynconfig({
    "option1": (
            ClassConfig(component_attr="comp_A", component_class=A),
            ClassConfig(component_attr="comp_G", component_class=G),
            ClassConfig(component_attr="comp_H", component_class=H),
    )
})
class BaseCompositionAdaptArguments:
    def __init__(self):
        self.a1 = Cr.BASE_PARAM_1


@dynconfig(
    {
        "option1": (
                ClassConfig(component_attr="comp_A", component_class=A),
                ClassConfig(component_attr="comp_G", component_class=G),
                ClassConfig(component_attr="comp_H", component_class=H),
        )
    },
    strict_missing_args=False
)
class BaseCompositionAdaptArgumentsNoStrictMissingArgs:
    ...


@dynconfig(
    {
        "option1": (
                ClassConfig(component_attr="comp_G", component_class=G),
                ClassConfig(
                    component_attr="comp_H",
                    component_class=H,
                    init_args_from_self="a1",
                    init_kwargs_from_self={"kwonly_2": "kw_H"}
                ),
        )
    },
    add_components_after_method=True
)
class BaseCompositionAdaptArgumentsFromSelf:
    def __init__(self):
        self.a1 = Cr.BASE_PARAM_2_ALT
        self.kw_H = Cr.CLASS_H__K2


@dynconfig(
    {
        "option1": ClassConfig(
            component_attr="comp",
            component_class=H,
            init_args_keep_first=1,
            init_args_from_self="a2_alt"
        ),
        "DYNDESIGN_LOCAL_CONFIG": LocalClassConfig(add_components_after_method=True)
    }
)
class BaseCompositionAdaptArgumentsFilter:
    def __init__(self, param1, param2):
        self.a1 = param1
        self.a2 = param2
        self.a2_alt = Cr.BASE_PARAM_2_ALT


@dynconfig({
    "option1": ClassConfig(
        component_attr="comp",
        component_class=H,
        init_args_from_option=True
    )
})
class BaseCompositionAdaptArgumentsFromOption:
    ...


@dynconfig({
    "option1": ClassConfig(component_attr="comp_base", component_class=BaseComposition),
})
class BaseCompositionRecursive:
    ...


@dynconfig({
    "option1": ClassConfig(component_attr="comp", component_class=B),
})
class BaseCompositionRecursiveStatic:
    def __init__(self, param1):
        self.comp_base = dynconfig.buildcomponent(BaseComposition)(param1)


@dynconfig(
    {
        "option1": ClassConfig(component_attr="comp", component_class=BaseComposition),
    },
    build_recursively=False
)
class BaseCompositionDisableRecursion:
    def __init__(self):
        self.a1 = Cr.BASE_PARAM_1


@dynconfig({
    lambda option1, option2, option3: option1 and option2 or option3:
        ClassConfig(component_attr="comp", component_class=A)
})
class BaseCompositionConditionalOptions:
    ...


@dynconfig({
    lambda value: value >= Mp.THRESHOLD_VALUE:
        ClassConfig(component_attr="comp", component_class=A)
})
class BaseCompositionThresholdOption:
    ...


@dynconfig({
    lambda value, THRESHOLD: value >= THRESHOLD:
        ClassConfig(component_attr="comp", component_class=A)
})
class BaseCompositionThresholdOptionWithClassAttr:
    THRESHOLD = Mp.THRESHOLD_VALUE


@dynconfig({
    "option1": (
            ClassConfig(inherit_from=A),
            ClassConfig(component_attr="comp", component_class=B)
    ),
})
class BaseInheritanceCompositionWithNoInit:
    ...


@dynconfig(
    {
        "option1": (
                ClassConfig(inherit_from="additional_test_class_builder.A"),
                ClassConfig(component_attr="comp", component_class="additional_test_class_builder.B")
        ),
    },
    class_builder_base_dir="tests.test_nested1.test_nested2"
)
class BaseInheritanceCompositionImport:
    def __init__(self):
        super().__init__()
        self.a1 = Cr.BASE_PARAM_1


class BaseInheritanceCompositionConfigClass:
    option1 = (
        ClassConfig(inherit_from=A),
        ClassConfig(component_attr="comp", component_class=B)
    )


@dynconfig(BaseInheritanceCompositionConfigClass)
class BaseInheritanceCompositionClassConfigured:
    ...


class BaseCompositionConfigClass:
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(component_attr="comp")

    option1 = ClassConfig(component_class=A)
    option2 = ClassConfig(component_class=B)


@dynconfig(BaseCompositionConfigClass)
class BaseCompositionClassConfiguredWithComponentAttr:
    ...


class BaseCompositionConfigClassWithConditions:
    @staticmethod
    def condition(option1, option2):
        return option1 and option2

    dynconfig.set_configuration(condition, ClassConfig(component_class=A, component_attr="comp"))


@dynconfig(BaseCompositionConfigClassWithConditions)
class BaseCompositionClassConfiguredWithConditions:
    ...


class BaseCompositionConfigClassWithLambdaConditions:
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(default_class=B)

    dynconfig.set_configuration(
        lambda option1, option2: option1 and option2,
        ClassConfig(component_class=A, component_attr="comp")
    )


@dynconfig(BaseCompositionConfigClassWithLambdaConditions)
class BaseCompositionClassConfiguredWithLambdaConditions:
    ...


@dynconfig("tests.test_nested1.test_nested2.additional_class_builder_configurator.BICConfigClass")
class BaseInheritanceCompositionClassConfigurationImported:
    def m1(self):
        return hasattr(self, 'comp')


@dynconfig(BaseCompositionConfigClass, BaseCompositionComponentListConfigClass)
class BaseCompositionMultipleConfigurators:
    ...


@dynconfig(
    BaseCompositionConfigClassWithLambdaConditions,
    {"option1": ClassConfig(component_class=A)},
    component_attr="comp2",
)
class BaseCompositionMultipleMixedConfiguration:
    ...


dynconfig.set_global(add_components_after_method=True)


@dynconfig(
    {
        "option1": ClassConfig(component_attr="comp", component_class=A)
    },
    injection_method='m1'
)
class BaseCompositionCustomGlobalConfig:
    def m1(self):
        return hasattr(self, 'comp')
