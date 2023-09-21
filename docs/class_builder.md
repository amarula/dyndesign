# Class Builder

Class Builder is an impressive module that allows Python developers to **build
classes by simply specifying a configuration**.

The primary objective of Class Builder is to completely **separate** the code
responsible for **class configuration** from **the core logic** of the classes.
Thanks to a set of ad hoc tools, developers can now define a set of possible
configurations for a Base class in terms of **Parent** and **Component** Class
Dependencies. They can then build new classes based on the Base class by selecting
one or more Building Options.

The first step involves associating a comprehensive set of potential class
configurations with a Base class. This can be achieved by employing the
`dynconfig` decorator, which allows for three distinct levels of separation
between class configuration and core logic:

1. the class configuration can be encapsulated within Configurator classes that
   can be associated with the Base class using `dynconfig` as a class decorator,
1. the class configuration can be directly passed to `dynconfig` class decorator
   as argument, or
1. `dynconfig` can also function as method decorator to configure inline component
   injections within specific methods.

The second and final step involves building a class with selected Class
Dependencies using the `buildclass` function.

## Getting Started

A Configurator class is linked to a Base class through the `dynconfig` decorator.
Once the Base class is configured, a new class can be built by passing the Base
class one or more Building Options as `buildclass` arguments.

``` py
@dynconfig(Configurator)
class Base:
    pass

BuiltClass = buildclass(Base, bool_option=True, switch="switch_option1")
```

Each Building Option determines which Class Dependencies are added to the newly
built class.

The Configurator class defines the class configurations for a set of potential
values of the Building Options. Each potential Option, referred to as a
"Configuration Option" in the context of class configuration, is used as a class
attribute to which a corresponding Class Dependency is assigned as value. Class
Dependencies, defined as `ClassConfig` instances, specify Class Dependencies of
either **Parent** or **Component** type.

``` py
class Configurator:
    bool_option = ClassConfig(component_attr="comp", component_class=Component)

    switch = {
        'switch_option1': ClassConfig(inherit_from=ParentA),
        'switch_option2': ClassConfig(inherit_from=ParentB),
    }
```
In the provided example, if the "bool_option" is set to True a Component class is
injected into the built class. Furthermore, if the "switch" selector is set to
"switch_option1" the built class inherits from a ParentA class. Conversely, if
"switch" is set to "switch_option2" the built class inherits from a ParentB class.

Considering the Building Options passed to `buildclass` in the first code snippet,
the resulting BuiltClass incorporates the Component class in the "comp" attribute
and inherits from the ParentA class.

## Syntax

### buildclass and @dynconfig

The syntax of the `buildclass` function is defined as following.

``` py
BuiltClass = buildclass(
    BaseClass,
    {"option1": val1, "option2": val2, ...} | building_option_object,
    option3=val3, option4=val4, ...
)
```

**Arguments:**

- **BaseClass**: Type  
    The Base class upon which to build the new class.<br/><br/>

- **Building Options**: Dict *or* Object *and/or* Keyword Arguments *(Optional)*  
    The Building Options can be provided as a dictionary or as any other object
    with a `__dict__` attribute. This broadens the scope to include various types
    of objects, including the return value of the `parse_args` method from the
    `argparse` package, as shown in the [Integration with
    argparse](#integration-with-argparse) section. Alternatively/additionally,
    Building Options can be provided directly as keyword arguments.<br/><br/>

- **return**: Type  
    The new class built based on the Building Options.<br/><br/>

The Base class is decorated with `@dynconfig` to specify all the potential class
configurations.

``` py
@dynconfig(
    ConfiguratorClass1 | 'path.to.ConfiguratorClass1' | {<configuration_dict_1>},
    ConfiguratorClass2 | 'path.to.ConfiguratorClass2' | {<configuration_dict_2>},
    ...
    local_base_setting1 = value1,
    local_base_setting2 = value2,
    ...
)
class Base:
    ...
```

**Arguments of dynconfig Class Decorator:**

- **Configuration Units**: Type *or* str *or* Dict (*Optional*)  
    One or more sets of Configuration Options associated with corresponding Class
    Dependencies, passed to `dynconfig` as positional arguments. Each
    Configuration Unit can be either a Configurator class, a string with a
    dot-notation path to a Configurator class, or a configuration dictionary. The
    syntax for the path in dot-notation is described in the
    [importclass](../misc_utilities#importclass) utility documentation.<br/><br/>

- **Local Base Settings**: Keyword Arguments (*Optional*)  
    Described in the [Global and Local
    Configuration](#global-and-local-configuration) section.<br/><br/>

The `dynconfig` decorator does not have any required arguments, meaning it can
also be called with no arguments. This feature is valuable when using `dynconfig`
as a method decorator to inject specific components into the decorated method.

``` py
@dynconfig()
class Base:
    ...

    @dynconfig({<configuration_dict_1>})
    def injection_method_1(...):
        ...

    @dynconfig({<configuration_dict_2>})
    def injection_method_2(...):
        ...

    ...
```

**Arguments of dynconfig Method Decorator:**

- **Configuration Dictionary**: Dict  
    A configuration dictionary to configure the Class Dependencies for the
    decorated method. <br/><br/>


### Using a Configurator Class

As mentioned previously, a Configurator class can be associated with a Base class
using the `dynconfig` class decorator.

``` py
@dynconfig(ConfiguratorClass)
class Base:
    ...
```

Below is the complete syntax for the Configurator classes.

``` py
class ConfiguratorClass:
    # Class Dependency Configuration
    bool_option1 = ClassConfig(...)
    bool_option2 = (
        ClassConfig(...),
        ClassConfig(...),
        ...
    ),
    ...

    dynconfig.set_configuration(
        lambda opt1, opt2, ...: <condition-on-opts>,
        ClassConfig(...)
    )
    def method_with_condition(self, opt1, opt2, ...):
        return <condition-on-opts>

    dynconfig.set_configuration(method_with_condition, ClassConfig(...))
    ...

    switch_selector1 = {
        'switch_option1': ClassConfig(...),
        'switch_option2': ClassConfig(...),
        ...
        dynconfig.SWITCH_DEFAULT: ClassConfig(...)
    }
    ...

    # Local Unit Configuration
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(
        # Unscoped Settings
        build_recursively = True | False
        class_builder_base_dir = 'path.to.BaseDir'
        option_order = (option1, option2, ...)
        # Dependency Settings
        default_class = DefaultClass | 'path.to.DefaultClass'
        force_add = True | False
        component_attr = 'component_attribure'
        injection_method = 'injection_method'
        add_components_after_method = True | False
        strict_missing_args = True | False
        structured_component_type = list | dict | ...
    )
```
The Configurator is made up of two parts: the Class Dependency Configuration and
the Local Unit Configuration.

The Class Dependency Configuration associates all potential Class Dependencies
that can be integrated into the Base class with their respective Configuration
Options. To this end, each potential Configuration Option is associated with a
`ClassConfig` instance or with a tuple of `ClassConfig` instances, where the
`ClassConfig` instance serves as a foundational configuration element that allows
the addition of either a Parent or a Component Dependency.

Configuration Options can be of different types:

- **Boolean Options** that enable the addition of Class Dependencies based on the
  values of Building Options interpreted as boolean,
- **Conditional Options** that specify conditions that must be met in order for
  the Class Dependencies to be added, and
- **Switch Options** that allow the addition of Class Dependencies based on the
  selection of single options from a range of options.

NOTE: *In Configurator classes, configurations with Conditional Options are set up
via `dynconfig.set_configuration`, which can be also employed to programmatically
set configurations of any type. Conditional Options can be provided through the
first argument of `set_configuration` in the form of any callable object,
including lambdas and methods*.

The Local Unit Configuration, defined through a `LocalClassConfig` instance
assigned to the `DYNDESIGN_LOCAL_CONFIG` attribute, establishes Local Settings
that are applied when building the classes defined within that Configurator, as
described in the [Global and Local Configuration](#global-and-local-configuration)
section.

### ClassConfig Syntax for Parent Dependencies

For the Parent Dependency Configuration, `ClassConfig` has the following syntax:

``` py
ClassConfig(
    inherit_from = ParentClass | 'path.to.Parent' | (Parent1, Parent2, ...)
    default_class = DefaultParentClass | 'path.to.DefaultParentClass'
)
```

**Arguments for Parent Dependency Configuration:**

- **inherit_from**: Type, str *or* Tuple[Type *or* str]  
    The class(es) that the Base class will inherit from if the corresponding
    Building Option is selected.<br/><br/>

- **default_class**: Type *or* str (*Optional*)  
    The class that the Base class will inherit from if the corresponding Building
    Option is **not selected**.<br/>

NOTE: *Either parent or component classes can be provided either directly or as
strings with a dot-notation path to the classes, as described in
[importclass](../misc_utilities#importclass).*

### ClassConfig Syntax for Component Dependencies

The syntax for the Component Dependency Configuration is as following:

``` py
ClassConfig(
    component_class = ComponentClass | 'path.to.ComponentClass'
    component_attr = 'component_attribure'
    default_class = DefaultComponentClass | 'path.to.DefaultComponentClass'
    force_add = True | False
    add_components_after_method = True | False
    injection_method = 'injection_method'
    init_args_from_option = True | False
    init_args_keep_first = 0 | 1 | 2 | ...
    init_args_from_self = 'attr' | ('attr1', 'attr2', ...)
    init_kwargs_from_self = {'key1': 'attr1', 'key2': 'attr2', ...}
    strict_missing_args = True | False
    structured_component_type = list | dict | ...
    structured_component_key = 'component_key'
)
```

**Arguments for Component Dependency Configuration:**

- **component_class**: Type *or* str  
    The class to be instantiated as component and injected into the built class
    if the corresponding Building Option is selected.<br/><br/>

- **component_attr**: str (*Optional*)  
    The class or instance attribute to be initialized with the component class.

    NOTE: *`component_attr` must be provided in any case within at least one of
    the four settings' scopes outlined in the [Global and Local
    Configuration](#global-and-local-configuration) section.*<br/><br/>

- **default_class**: Type *or* str (*Optional*)  
    The class to be instantiated as component and injected into the built class
    if the corresponding Building Option is **not selected**.<br/><br/>

- **force_add**: bool (*Optional*)  
    When this flag is set, the related component is always added to the built
    class regardless of the value of the associated Building Option. <br/><br/>

- **add_components_after_method**: bool (*Optional*)  
    Whether to add the component before or after the execution of the injection
    method. The default value is False, which means that the component are
    injected by default **before** executing the injection method. <br/><br/>

- **injection_method**: str (*Optional*)  
    The method into which the component is to be injected. By default, components
    are injected into the constructor **\_\_init\_\_**. <br/><br/>

- **init_args_keep_first**: int (*Optional*)  
    By default, arguments to be passed to the component constructor are adapted
    from the arguments passed to the injection method, as described in the
    [Argument Adaptation](#argument-adaptation) section. If certain or all of the
    positional arguments from the injection method need to be excluded from those
    passed to the constructor of the component, this parameter can be utilized to
    specify how many positional parameters passed to the injection method are to
    be retained. If no positional parameter of the injection method is needed to
    initialize the component, `init_args_keep_first` must be set to zero.
    <br/><br/>

- **init_args_from_option**: bool (*Optional*)  
    If this flag is set, the value of the related Building Option is passed as
    first positional argument when initializing the component's constructor,
    before any positional arguments from the injection method. <br/><br/>

- **init_args_from_self**: str *or* Tuple[str] (*Optional*)  
    In addition to the arguments adapted from the ones of the injection method,
    one or more positional arguments can be passed to the constructor of the
    component from the `self` properties by passing the property names through
    this parameter. <br/><br/>

- **init_kwargs_from_self**: dict[str: str] (*Optional*)  
    Similarly to the `init_args_from_self` parameter, one or more keyword
    arguments can be passed to the constructor by setting this parameter to a
    dictionary. In this dictionary, the keys must match the keyword arguments'
    names, and the values must correspond to the `self` property names whose
    values are to be passed to the constructor. <br/><br/>

- **strict_missing_args**: bool (*Optional*)  
    This parameter controls how missing positional parameters are handled when
    initializing a component. When this parameter is **True** (*Default* value),
    if any required positional parameter is missing when initializing the
    component, an exception will be raised, following the default Python behavior.
    When this parameter is False, any component with missing required parameters
    will simply not be initialized, and the execution will continue normally.
    <br/><br/>

- **structured_component_type**: Type (*Optional*)  
    To aggregate components in a data structure assigned to a class or instance
    attribute, the data type can be specified using this parameter, as described
    in the [Injecting Components in Data
    Structures](#injecting-components-in-data-structures) section. <br/><br/>

- **structured_component_key**: str (*Optional*)  
    If the data type specified in `structured_component_type` is a dictionary type
    or requires an assignment key in any way, that key can be defined using this
    parameter. <br/><br/>

### Configuration Passed as dynconfig Arguments

In alternative to using a Configurator class, the pairs of Configuration Options
and Class Dependencies can be directly passed to `dynconfig` within a
configuration dictionary.

``` py
@dynconfig(
    # Class Dependency Configuration
    {
        'bool_option1': ClassConfig(...),
        'bool_option2': ClassConfig(...),
        'bool_option3': (
            ClassConfig(...),
            ClassConfig(...),
            ...
        ),
        ...
        lambda opt1, opt2, ...: <condition-on-opts>:
            ClassConfig(...),
        conditional_callable: ClassConfig(...),
        ...
        'switch_selector': {
            'switch_option1': ClassConfig(...),
            'switch_option2': ClassConfig(...),
            ...
            dynconfig.SWITCH_DEFAULT: ClassConfig(...)
        },
        ...

        # Local Unit Configuration
        "DYNDESIGN_LOCAL_CONFIG": LocalClassConfig(...)
    },

    # Local Base Configuration
    local_base_setting1 = value1,
    local_base_setting2 = value2,
    ...
)
class Base:
    ...
```

The syntax closely resembles that of the Configurators with one notable
distinction: conditions can be directly defined as dictionary keys in the form of
lambda functions or any other callable object, eliminating the need for
`dynconfig.set_configuration`.

## Global and Local Configuration

The configuration settings can be specified within four different scopes:

- **Global**: Global Settings can be defined using `dynconfig.set_global`, and
  these settings will be applied to all classes configured using dynconfig after
  their definition.
- **Local to a Base class**: If a setting is passed as a keyword argument of
  `dynconfig` class decorator, it will only apply to the Base class that is being
  configured.
- **Local to a Configuration Unit**: If a setting is defined through the
  `DYNDESIGN_LOCAL_CONFIG` attribute of a Configurator class (or, equivalently,
  through the "DYNDESIGN_LOCAL_CONFIG" key of a configuration dictionary) that
  setting will only apply to the Class Dependencies of that Configurator (or
  dictionary).
- **Local to a ClassConfig instance**: If a setting is defined as a field of a
  `ClassConfig` instance, the setting will only apply to the Class Dependency that
  is added using that `ClassConfig` object.

Here is an example of how Global settings work:

``` py
@dynconfig(...)
class NotAffectedClass:
    ...

dynconfig.set_global(build_recursively=False, add_components_after_method=True)

@dynconfig(...)
class AffectedClass:
    ...
```

The Global and Local Configuration Settings can fall into two categories:
**Unscoped settings**, which encompass configurations that affect the way a class
is built, and **Dependency settings**, which include configurations that
specifically govern the addition of Class Dependencies.

NOTE: *Settings that are scoped to a `ClassConfig` instance can only be of the
Dependency Configuration category.*

### Unscoped Settings

The following Unscoped settings affect the general behavior of Class Builder.

- **build_recursively**: bool  
    Whether the classes dependent to the Base class have to be built recursively
    or not. When set to **True** (the Default setting), both statically defined
    Class Dependencies and those added dynamically are built recursively in
    accordance with the table below.

    |                       | Parent Dependencies |      Component Dependencies       |
    |-----------------------|:-------------------:|:---------------------------------:|
    | **Static**            |    Automatically    | Manually (via **buildcomponent**) |
    | **Added Dynamically** |    Automatically    |           Automatically           |

    If a dependency added dynamically by Class Builder is also dynamically
    configurable (i.e., it is decorated with `@dynconfig`), it will be
    automatically built with the same Building Options as the Base class. This
    rule also applies to static parent classes of base classes. However, if a
    **static component** class requires to be recursively built, it needs to be
    explicitly instantiated using `buildcomponent`, as explained in details in the
    [Building of Static Component
    Dependencies](#building-of-static-component-dependencies) section.<br/><br/>

- **class_builder_base_dir**: str  
    The base directory from which the Configurator classes and dependent classes
    in dot notation are dynamically imported. <br/><br/>

- **option_order**: Type *or* str  
    The order in which the Building Options must be assessed for applying the
    corresponding `ConfigClass` instances. If multiple Options are enabled, this
    setting could impact the Method Resolution Order (MRO) of dynamically
    inherited classes or the instantiation of components within class/instance
    attributes, as shown in the [Customizing MRO](#customizing-mro) section.<br/>

### Dependency Settings

Described in details in the [ClassConfig Syntax for Parent
Dependencies](#classconfig-syntax-for-parent-dependencies) and [ClassConfig Syntax
for Component Dependencies](#classconfig-syntax-for-component-dependencies)
sections.

## Basic Examples

### Component Class

The following is a basic example of a Boolean Option that can be used to control
the instantiation of the component class "A" and to assign it to the "self.comp"
attribute.

``` py
from dyndesign import buildclass, dynconfig, ClassConfig

class A:
    def whoami(self):
        print("I am component `A`")


class Configurator:
    optionA = ClassConfig(component_class=A, component_attr="comp")


@dynconfig(Configurator)
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True)
BuiltClass().comp.whoami()
# I am component `A`

BuiltClass = buildclass(Base, optionA=False)
assert not hasattr(BuiltClass(), 'comp')
```

If the Base class is built with "optionA" set to True, the "A" instance is
assigned to "self.comp", otherwise the "comp" attribute remains unassigned.

### Parent Classes

The following is a basic example of configurable inheritance.

``` py
from dyndesign import buildclass, dynconfig, ClassConfig

class P1:
    def __init__(self):
        print("I am the constructor of `P1`")

class P2:
    def __init__(self):
        print("I am the constructor of `P2`")


@dynconfig({
    "optionA": ClassConfig(inherit_from=P1),
    "optionB": ClassConfig(inherit_from=P2),
})
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True)
BuiltClass()
# I am the constructor of `P1`

BuiltClass = buildclass(Base, optionB=True)
BuiltClass()
# I am the constructor of `P2`

BuiltClass = buildclass(Base, optionA=True, optionB=True)
BuiltClass()
# I am the constructor of `P1`
```

The following scenarios occur:

- When BuiltClass is built with "optionA" set to True, the Base class inherits
  from the P1 class.
- When "optionB" is set to True, the Base class inherits from P2.
- When both "optionA" and "optionB" are set to True, the Base class inherits from
  both P1 and P2. However, only the constructor of P1 is called due to the MRO.
  The MRO can be modified by changing the order in which the Options are applied,
  as shown in the [Customizing MRO](#customizing-mro) section.

NOTE: *The bodies of component classes such as "A", "B", "C", ..., and Default,
along with those of parent classes P1, P2, ..., and "PDefault", will be assumed to
have the same form as in the previous examples and will therefore be omitted from
the following code snippets unless otherwise specified. Import statements of
`buildclass`, `dynconfig`, `ClassConfig`, and `LocalClassConfig` will be implied
as well.*

## Switches

Switch is a powerful construct for managing Options that take on values other than
True or False.

``` py
class Configurator:
    switch = {
        "optionA": ClassConfig(component_class=A),
        "optionB": ClassConfig(component_class=B),
        dynconfig.SWITCH_DEFAULT: ClassConfig(component_class=Default)
    }
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(component_attr="comp")


@dynconfig(Configurator)
class Base:
    def __init__(self):
        self.comp.whoami()


buildclass(Base, switch="optionA")()
# I am component `A`

buildclass(Base, switch="optionB")()
# I am component `B`

buildclass(Base)()
# I am component `Default`
```
In the code above, if the "switch" parameter is set to either "optionA" or
"optionB" the corresponding component classes are injected in the "self.comp"
attribute. Otherwise, the Default class, set up through the
`dynconfig.SWITCH_DEFAULT` fixed key, is injected by default.

The code also shows how to set a Local Unit Configuration setting through the
`DYNDESIGN_LOCAL_CONFIG` fixed attribute. In this case, the "comp" setting is
locally assigned to `component_attr`: this means that all `ClassConfig` instances
of Configurator will use "comp" as attribute to instantiate the components, unless
it is overridden in a specific `ClassConfig` instance.

## Multiple Dependencies per Option

In the code below, some modifications are applied to the previous example to show
how to assign multiple Class Dependencies to one Option and, more generally, how
complex functionalities can be easily implemented using Class Builder.

``` py
class Configurator:
    switch = {
        "optionA": ClassConfig(component_class=A),
        "optionB": (
            ClassConfig(component_class=B),
            ClassConfig(component_class=C, component_attr="comp2"),
        ),
        dynconfig.SWITCH_DEFAULT: ClassConfig(component_class=Default)
    }
    bool_option = ClassConfig(component_class=D)

    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(component_attr="comp")


@dynconfig(Configurator)
class Base:
    def __init__(self):
        self.comp.whoami()


buildclass(Base, switch="optionA")()
# I am component `A`

built_class = buildclass(Base, switch="optionB")()
# I am component `B`

built_class.comp2.whoami()
# I am component `C`

buildclass(Base, bool_option=True)()
# I am component `D`

buildclass(Base)()
# I am component `Default`
```

To elaborate, the Configurator has been altered to make "optionB" result in the
composition of two classes, namely "B" and "C", instead of just the "B" class as
seen in the previous example. Furthermore, an additional Boolean Option,
"bool_option", has been introduced to illustrate the handling of Configuration
Options with varying types. In other words, components "A", "B", "D", and Default
are instantiated by default in the "comp" attribute, thanks to the Unit Local
Setting `component_attr="comp"`, while "C" is instantiated in "comp2", since the
`component_attr` Local setting of the corresponding `ClassConfig` overrides the
Unit Local Setting.

As results:

- When a class is built with the "switch" Option set to "optionA", class "A" is
  instantiated in "comp".
- When "switch" is set to "optionB", "B" is instantiated in "comp" and "C" is
  instantiated in "comp2".
- When "bool_option" is set to True, "D" is instantiated in "comp".
- When a class is built with no Option, the Default class is instantiated in
  "comp".

## Multiple Configuration Units

In some cases, splitting Class Dependencies into separate Configuration Units can
be useful. For example, this could be done to use different Local Configuration
Settings for each Unit, or to modularize the Units so that they can be reused when
building further classes.

To support this capability, starting from DynDesign version 1.1, the `dynconfig`
class decorator accepts multiple Configuration Units as positional arguments.

``` py
class Configurator1:
    switch_a_b = {
        "optionA": ClassConfig(component_class=A),
        "optionB": ClassConfig(component_class=B),
        dynconfig.SWITCH_DEFAULT: ClassConfig(component_class=DefaultAB)
    }
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(component_attr="comp")


class Configurator2:
    switch_c_d = {
        "optionC": ClassConfig(component_class=C),
        "optionD": ClassConfig(component_class=D),
        dynconfig.SWITCH_DEFAULT: ClassConfig(component_class=DefaultCD)
    }
    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(component_attr="comp2")


@dynconfig(Configurator1, Configurator2)
class Base:
    def __init__(self):
        self.comp.whoami()
        self.comp2.whoami()


buildclass(Base, switch_a_b="optionA")()
# I am component `A`
# I am component `DefaultCD`

buildclass(Base, switch_a_b="optionB", switch_c_d="optionD")()
# I am component `B`
# I am component `D`
```

In the above code, the two switches "switch_a_b" and "switch_c_d" have two
different component attributes. Instead of repeating the `component_attr`
assignment in each individual `ClassConfig` instance, it appears only once per
Configuration Unit. The Base class is subsequently associated with both
Configuration Units.

The ability to use multiple Configuration Units is especially useful when
[Injecting Components in Data
Structures](#injecting-components-in-data-structures).

## Conditional Options

To allow for enhanced flexibility, conditional functions are also permitted as
Configuration Options.

### Functions Using Other Configuration Options

In the code snippet below, a lambda function is employed as a Configuration Option
from a dictionary provided as the first argument to the `dynconfig` class
decorator.

``` py
@dynconfig({
    lambda optionA, optionB: optionA and not optionB:
        ClassConfig(component_class=A, component_attr="comp")
})
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True)
BuiltClass().comp.whoami()
# I am component `A`

BuiltClass = buildclass(Base, optionA=True, optionB=True)
assert not hasattr(BuiltClass(), 'comp')
```
The lambda function checks if the "optionA" Option is set to True and "optionB" is
set to False or not set. If both of these conditions are met, the "A" component is
added as a dependency.

NOTE: *The arguments' names in the conditional function signatures must match the
names of the Building Options passed to `buildclass`.*

### Functions Using Class Parameters

In the example below, the conditional function compares the integer Option "value"
with the value of a THRESHOLD class attribute extracted from the Base class.

``` py
class Configurator:
    @staticmethod
    def threshold_condition(value, THRESHOLD):
        return value >= THRESHOLD

    dynconfig.set_configuration(
        threshold_condition,
        ClassConfig(inherit_from=P1)
    )


@dynconfig(Configurator)
class Base:
    THRESHOLD = 100

    def __init__(self):
        print("Initializing class `Base`")
        super().__init__()


BuiltClass = buildclass(Base, value=99)
BuiltClass()
# Initializing class `Base`

BuiltClass = buildclass(Base, value=101)
BuiltClass()
# Initializing class `Base`
# I am the Constructor of `P1`
```

If the BuiltClass is built with the "value" Option less than THRESHOLD (set at
100), then no dependency is added. As opposite, for values greater than or equal
to THRESHOLD, the built class inherits from P1.

NOTES:

- *Any callable object, including lambda functions as well as static, class, and
  instance methods, can be used as conditional function.*
- *Any class and instance attribute of the Base class (such as THRESHOLD) can be
  provided as well to the conditional function using the name matching rule with
  the Base attributes.*
- *When using class Configurators, the Conditional Options must be defined using
  `dynconfig.set_configuration`.*

## Safe Communication with Dependent Classes

### Safely Calling Methods from Components

If the Base classes of the preceding composition examples were instantiated as
standalone classes, without being built, an error would occur when the
corresponding "self.comp" attributes are invoked. To silently ignore the error,
the [safeinvoke](../extended_class_communication#safeinvoke) or the
[safezone](../extended_class_communication#safezone-context-manager) functions can
be used.

``` py
from dyndesign import ..., safeinvoke

@dynconfig(Configurator)
class Base:
    def __init__(self):
        print("Initializing class `Base`")
        safeinvoke('comp.whoami', self)

Base()
# Initializing class `Base`
```

### Safely Initializing Specific Parent Classes

It is possible to modify the example in the [Parent Classes](#parent-classes)
section so that both constructors of the parent classes are called when both
Options "optionA" and "optionB" are set to True. To achieve this, both dynamically
added superclasses need to be accessed from within the Base's constructor when
both Options are True.

``` py
from dyndesign import ..., safesuper
...

@dynconfig({
    "optionA": ClassConfig(inherit_from=P1),
    "optionB": ClassConfig(inherit_from=P2),
})
class Base:
    def __init__(self):
        print("Initializing Class `Base`")
        super().__init__()
        safesuper(P1, self).__init__()


BuiltClass = buildclass(Base, optionA=True)
BuiltClass()
# Initializing Class `Base`
# I am the constructor of `P1`

BuiltClass = buildclass(Base, optionB=True)
BuiltClass()
# Initializing Class `Base`
# I am the constructor of `P2`

BuiltClass = buildclass(Base, optionA=True, optionB=True)
BuiltClass()
# Initializing Class `Base`
# I am the constructor of `P1`
# I am the constructor of `P2`

Base()
# Initializing Class `Base`
```

To invoke the constructor of the second parent class (P2) when both Options are
True, it is necessary to pass the first parent class (P1) as initial parameter of
the `super` function. However, employing `super(P1, self)` directly would lead to
a `TypeError` whenever the class is built without P1. To seamlessly bypass the
error, the [safesuper
function](../extended_class_communication#safesuper-function) is utilized instead.

It is worth noting that the above implementation raises no exception even if the
Base class is directly instantiated without being built first.

### Safely Using Methods from Dependent Classes as Decorators

Class Builder's capabilities shine when combined with the
[decoratewith](../extended_class_communication#decoratewith) meta decorator.
Through this combined usage, both dynamically added Parent and Component
Dependencies can be seamlessly utilized to decorate methods of the base classes.
Even if any or all of the parent or component classes are not (yet) added, the
execution continues without errors.

``` py
from dyndesign import ..., decoratewith

class A:
    def component_decorator(self, func, decorated_self):
        print("Beginning of `A` decoration.")
        func(decorated_self)
        print("End of `A` decoration.")

class P1:
    def inherited_decorator(self, func):
        print("Beginning of `P1` decoration.")
        func(self)
        print("End of `P1` decoration.")


@dynconfig({
    "optionA": ClassConfig(component_attr="comp", component_class=A),
    "optionP1": ClassConfig(inherit_from=P1),
})
class Base:
    @decoratewith('inherited_decorator', 'comp.component_decorator')
    def decorated_method(self):
        print("I am the decorated method")


BuiltClass = buildclass(Base, optionA=True, optionP1=True)
BuiltClass().decorated_method()
# Beginning of `P1` decoration.
# Beginning of `A` decoration.
# I am the decorated method
# End of `A` decoration.
# End of `P1` decoration.

BuiltClass = buildclass(Base, optionA=True)
BuiltClass().decorated_method()
# Beginning of `A` decoration.
# I am the decorated method
# End of `A` decoration.

Base().decorated_method()
# I am the decorated method
```

The following scenarios occur:

- When BuiltClass is built with both Options "optionA" and "optionP1" set to True,
  the P1 parent class and the "A" component class are both added to the Base
  class. In this case, "decorated_method" is decorated with the methods from both
  classes.
- If only one Option is set to True, the decorator of the corresponding class is
  applied.
- If no Option is added or the Base class is directly instantiated, no decoration
  is applied.

## Advanced Component Configuration

### Components Added by Default

In the example below, if the Base class is built with "optionA" set to True, an
instance of "A" is injected in "self.comp", otherwise an instance of the Default
class is injected.

``` py
class Configurator:
    optionA = ClassConfig(
        component_class=A,
        component_attr="comp",
        default_class=Default
    )

@dynconfig(Configurator)
class Base:
    def __init__(self):
        self.comp.whoami()


BuiltClass = buildclass(Base, optionA=True)
BuiltClass()
# I am component `A`

BuiltClass = buildclass(Base, optionA=False)
BuiltClass()
# I am component `Default`

BuiltClass = buildclass(Base)
BuiltClass()
# I am component `Default`
```

### Custom Injection Methods

By default, components are injected into the `__init__` constructor. To inject the
components into a different method, the `injection_method` setting can be used.

``` py
class Configurator:
    optionA = ClassConfig(
        component_class=A,
        component_attr="comp",
        injection_method="injection_method"
    )

@dynconfig(Configurator)
class Base:
    def __init__(self):
        assert not hasattr(self, 'comp')

    def injection_method(self):
        self.comp.whoami()


BuiltClass = buildclass(Base, optionA=True)
BuiltClass().injection_method()
# I am component `A`
```

As confirmed by the `assert` statement in `__init__`, component "A" has not been
instantiated yet in "comp" when the constructor of the Base class is executed.

### Using dynconfig as Method Decorator

For convenience, `dynconfig` can be directly used as a method decorator to
configure component injection into specific methods, without having to set
`injection_method`.

``` py
@dynconfig()
class Base:
    @dynconfig({"optionA": ClassConfig(component_class=A, component_attr="comp")})
    def __init__(self):
        self.comp.whoami()
        assert not hasattr(self, 'comp2')

    @dynconfig({"optionA": ClassConfig(component_class=B, component_attr="comp2")})
    def injection_method(self):
        self.comp2.whoami()


BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass()
# I am component `A`

built_class.injection_method()
# I am component `B`
```

### Custom Injection Position

By default, components are injected **before** the method is executed. This
behavior can be changed to inject the components **after** or in the **middle** of
the method's execution.

``` py
@dynconfig()
class Base:
    @dynconfig({"optionA": ClassConfig(
            component_class=A,
            component_attr="comp",
            add_components_after_method=True
    )})
    def __init__(self):
        assert not hasattr(self, 'comp')
        assert not hasattr(self, 'comp2')
        print("Initializing class `Base`")

    @dynconfig({"optionB": ClassConfig(
            component_class=B,
            component_attr="comp2"
    )})
    def injection_method(self):
        assert not hasattr(self, 'comp2')
        dynconfig.inject_components()
        self.comp2.whoami()


BuiltClass = buildclass(Base, optionA=True, optionB=True)
built_class = BuiltClass()
# Initializing class `Base`

built_class.comp.whoami()
# I am component `A`

built_class.injection_method()
# I am component `B`
```

In the example provided, the "A" component is injected after executing the
constructor `__init__`, while the "B" component is injected within the execution
of "injection_method" through the `dynconfig.inject_components` fixed method.

### Passing the Option Value as Argument

The value of the Building Option used to select a certain component can also be
passed to the component constructor as the first positional argument, by setting
the `init_args_from_option` flag. This is especially useful when the option has a
non-boolean value that needs to be used to initialize the component.

``` py
class A:
    def __init__(self, param1, param2):
        print(f"Component `A` prints {param1=} and {param2=}")


@dynconfig({"optionA": ClassConfig(
    component_attr="comp",
    component_class=A,
    init_args_from_option=True
)})
class Base:
    pass


BuiltClass = buildclass(Base, optionA="VALUE #1")
built_class = BuiltClass("VALUE #2")
# Component `A` prints param1='VALUE #1' and param2='VALUE #2'
```

### Argument Adaptation

To initialize a component, specific arguments from those passed to the injection
method may be required. By default, these arguments are **adapted** to match the
parameters of the component constructor, in a manner similar to that described for
[mergeclass constructors](../dynamic_class_design#constructors).

Specifically, any excessive positional arguments passed are filtered out before
being forwarded to the component constructor, and non-positional arguments are
passed to the component constructor by matching their names.

``` py
class A:
    def __init__(self, a, kw1=None):
        print(f"Initializing `A` with {a=} and {kw1=}")

class B:
    def __init__(self, kw2=None):
        print(f"Initializing `B` with {kw2=}")


class Configurator:
    optionA = (
        ClassConfig(component_class=A, component_attr="comp"),
        ClassConfig(component_class=B, component_attr="comp2")
    )

@dynconfig(Configurator)
class Base:
    def __init__(self, a, b, kw1=None, kw2=None):
        print(f"Initializing `Base` with {a=}, {b=}, {kw1=} and {kw2=}")


BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass('x', 'y', kw1='z', kw2='w')
# Initializing `A` with a='x' and kw1='z'
# Initializing `B` with kw2='w'
# Initializing `Base` with a='x', b='y', kw1='z' and kw2='w'
```

In the above example:

- the first positional argument "a" of `__init__` is passed to the constructor of
  component "A" and is filtered out when component "B" is initialized, since it is
  required only by "A";
- the second positional argument "b" of `__init__` is filtered out when
  initializing both components "A" and "B", since neither "A" nor "B" require it;
- the keyword argument "kw1" is used to initialize "A", based on the name
  matching; and
- the keyword argument "kw2" is used to initialize "B".

Similarly, the arguments that are passed to the injection method must also be
adapted to the signature of the injection method itself. This is because the
component constructor may require more positional arguments or different keyword
arguments than the injection method. For example, the code above can be modified
so that no argument is accepted by the Base constructor (which serves as the
injection method):

``` py
...

@dynconfig(Configurator)
class Base:
    def __init__(self):
        print(f"Initializing `Base` with no arguments")


BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass('x', 'y', kw1='z', kw2='w')
# Initializing `A` with a='x' and kw1='z'
# Initializing `B` with kw2='w'
# Initializing `Base` with no arguments
```

In this example, both components are initialized exactly as in the previous code,
but `__init__` does not receive any positional or keyword arguments.

### Altering Behavior with Missing Required Arguments

As previously mentioned, excessive positional arguments are filtered out before
being transferred to the component constructors. However, what occurs when the
component constructors lack the required positional arguments? By default, a
`TypeError` exception is raised, as shown in the modified code below.

``` py
...

BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass(kw2='w')
# ...
# TypeError: __init__() missing 1 required positional argument: 'a'
```
The `TypeError` exception occurs when an attempt is made to invoke the constructor
of "A" without providing the necessary first positional argument "a".

Nevertheless, this behavior can be overridden by utilizing the
`strict_missing_args` setting.

``` py
...

@dynconfig(Configurator, strict_missing_args=False)
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass(kw2='w')
# Initializing `B` with kw2='w'
```

In the code above, the "A" component class cannot be instantiated because the
first positional argument of its constructor is missing. However, this does not
raise any exception and the execution proceeds to add the "B" component.

### Component Initialization Parameters

The arguments that are passed to component constructors can be customized with a
high degree of flexibility. This can be accomplished through two distinct
approaches:

1. By partially or entirely replacing the arguments passed to the injection method
   and/or adding new ones. This can be achieved using the argument filtering
   settings `init_args_keep_first`, `init_args_from_self`, and
   `init_kwargs_from_self`.
1. By directly providing the necessary arguments to the
   `dynconfig.inject_components` function.

The following code snippet shows both approaches.

``` py
class A:
    def __init__(self, a, b, kw=None):
        print(f"Initializing `A` with {a=}, {b=}, and {kw=}")


@dynconfig(component_attr="comp")
class Base:
    @dynconfig({"option1": ClassConfig(
            component_class=A,
            init_args_keep_first=1,
            init_args_from_self="self_b",
            init_kwargs_from_self={"kw": "self_kw"},
            add_components_after_method=True
    )})
    def __init__(self, *args):
        print(f"Initializing `Base` with {args=}")
        self.self_b = "y.self"
        self.self_kw = "z.self"

    @dynconfig({"option2": ClassConfig(component_class=A)})
    def injection_method(self, a):
        dynconfig.inject_components(a, self.self_b, kw="z.hardcoded")


BuiltClass = buildclass(Base, option1=True, option2=True)
built_class = BuiltClass("x.passed", "y.passed")
# Initializing `Base` with args=('x.passed', 'y.passed')
# Initializing `A` with a='x.passed', b='y.self', and kw='z.self'

built_class.injection_method("x.re-passed")
# Initializing `A` with a='x.re-passed', b='y.self', and kw='z.hardcoded'
```

The "A" component is instantiated twice: the first time after the `__init__`
constructor is executed (since "option1" is True), and the second time in the
middle of the "injection_method" method's execution (given that "option2" is
True).

On the first instantiation, the arguments forwarded to the constructor of "A" are
modified as following:

- Initially, the first positional argument ("x.passed") is retained, while the
  second ("y.passed") is discarded because `init_args_keep_first` is set to 1.
- Then, the value of the "self_b" property of the `self` object ("y.self") is
  appended to the positional arguments, utilizing `init_args_from_self`.
- Lastly, the keyword argument "kw" is assigned the value from the "self_kw"
  property of the `self` object ("z.self"), employing `init_kwargs_from_self`.

The argument substitution adopted in the second instantiation is easier to
understand and implement, but it does not allow for as much separation between the
core logic and the configuration. With this approach, the arguments are directly
passed to the constructor of "A" by `dynconfig.inject_components`. In the example,
the first positional argument "a" is taken from the one provided to the method,
the second argument is obtained from `self.self_b`, and the value of the keyword
argument "kw" is hardcoded.

### Injecting Components in Data Structures

Since DynDesign version 1.1, components can be injected into any type of data
structure that supports adding items, including lists, dictionaries,
SimpleNamespaces, and user-defined classes.

``` py
class Configurator:
    option1 = ClassConfig(component_class=A)
    option2 = ClassConfig(component_class=B)

    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(
        component_attr="comp_list",
        structured_component_type=list
    )

@dynconfig(Configurator)
class Base:
    def __init__(self):
        for comp in self.comp_list:
            comp.whoami()


BuiltClass = buildclass(Base, option1=True)
BuiltClass()
# I am component `A`

BuiltClass = buildclass(Base, option1=True, option2=True)
BuiltClass()
# I am component `A`
# I am component `B`
```

The above code shows that assigning `structured_component_type` to `list` is
enough to achieve the following behavior:

- When only "option1" is selected, a list containing a single element (the
  instance of the corresponding component "A") is injected in `comp_list`.
- When "option2" is selected as well, the "B" component is appended to `comp_list`
  alongside "A".

The next example modifies the code above to use two Configurators with the same
Base class: "Configurator2" is similar to Configurator, but it uses a dictionary
instead of a list as data structure.

``` py
...

class Configurator2:
    option1 = ClassConfig(component_class=C, structured_component_key="c")
    option2 = ClassConfig(component_class=D, structured_component_key="d")

    DYNDESIGN_LOCAL_CONFIG = LocalClassConfig(
        component_attr="comp_dict",
        structured_component_type=dict
    )

@dynconfig(Configurator, Configurator2)
class Base:
    def __init__(self):
        for ind, comp_list in enumerate(self.comp_list):
            print(f"List {ind=}   - ", end="")
            comp_list.whoami()
        for key, comp_dict in self.comp_dict.items():
            print(f"Dict {key=} - ", end="")
            comp_dict.whoami()


BuiltClass = buildclass(Base, option1=True)
BuiltClass()
# List ind=0   - I am component `A`
# Dict key='c' - I am component `C`

BuiltClass = buildclass(Base, option1=True, option2=True)
BuiltClass()
# List ind=0   - I am component `A`
# List ind=1   - I am component `B`
# Dict key='c' - I am component `C`
# Dict key='d' - I am component `D`
```

A significant distinction compared to the previous example is that dictionary
component types (similarly to other dictionary-like types) enable, for each
component to be injected, the specification of a unique key via the
`structured_component_key` setting.

## Advanced Parent Configuration

### Parents Added by Default

Similarly to component classes, parent dependent classes can also be configured
with a default class.

``` py
class P1:
    def method(self):
        print("I am `method` from `P1`")

class PDefault:
    def method(self):
        print("I am `method` from `PDefault`")


@dynconfig({
    "optionA": ClassConfig(inherit_from=P1, default_class=PDefault),
})
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True)
BuiltClass().method()
# I am `method` from of `P1`

BuiltClass = buildclass(Base)
BuiltClass().method()
# I am `method` from of `PDefault`
```

### Customizing MRO

The MRO of the parent classes dynamically added in the built class can be modified
by changing the order in which the Options are applied.

``` py
@dynconfig({
        "optionA": ClassConfig(inherit_from=P1),
        "optionB": ClassConfig(inherit_from=P2),
    },
    option_order=("optionB", "optionA")
)
class Base:
    pass


BuiltClass = buildclass(Base, optionA=True, optionB=True)
BuiltClass()
# I am the constructor of `P2`
```

In the above example, the first class added to the Base's superclass set is P2,
followed by P1. For this reason, the constructor of P2 is the one that is called
when the built class is instantiated.

## Recursive Building

One of the most remarkable features of the Class Builder is its ability to
recursively track the Class Dependencies of a class, enabling the **building of
classes configured using `@dynconfig` in a cascading manner**.

### Dependencies Built Recursively by Default

As the default behavior, Class Dependencies are built recursively, utilizing the
**same Building Options as the Base classes**. As shown in the table in the
[Unscoped Settings](#unscoped-settings) section, the following Class
Dependency types are built recursively: Parent Dependencies (both static and
dynamically added) and Component Dependencies (dynamically added).

In the example provided in this section, a 2-level hierarchy of Component and
Parent Dependencies is added to the Base class when it is built with "optionA" set
to True. The visual representation provided in the diagram below illustrates the
hierarchical relationships among these classes. At the bottom, the Base class
statically inherits from the Parent1 class (depicted as a solid line). When a new
class is built with "optionA" set, the Class Dependencies (indicated by dashed
lines) are recursively added as follows:

- The Parent1 class inherits from the Grandparent1 class.
- The Base class inherits from the Parent2 class.
- The Parent2 class inherits from the Grandparent2 class.
- The Component1 class is added as component to the Base class.
- The Component1 class inherits from the ParentComponent1 class.

![Class Dependency Diagram](https://github.com/amarula/dyndesign/blob/7664a4456271ccac2f0e27a276a754c2d7f7ec98/docs/img/build_recursive_example.png?raw=true)

The code snippet below implements the process of building the class.

``` py
class Grandparent1:
    def method1(self):
        print("I am `Grandparent1.method1`")

class Grandparent2:
    def method2(self):
        print("I am `Grandparent2.method2`")

class ParentOfComponent1:
    def method3(self):
        print("I am `ParentOfComponent1.method3`")


@dynconfig({"optionA": ClassConfig(inherit_from=Grandparent1)})
class Parent1:
    pass

@dynconfig({"optionA": ClassConfig(inherit_from=Grandparent2)})
class Parent2:
    pass

@dynconfig({"optionA": ClassConfig(inherit_from=ParentOfComponent1)})
class Component1:
    pass


class Configurator:
    optionA = (
        ClassConfig(inherit_from=Parent2),
        ClassConfig(component_class=Component1, component_attr="comp"),
    )

@dynconfig(Configurator)
class Base(Parent1):
    pass


built_class = buildclass(Base, optionA=True)()

built_class.method1()
# I am `Grandparent1.method1`

built_class.method2()
# I am `Grandparent2.method2`

built_class.comp.method3()
# I am `ParentOfComponent1.method3`
```

The "built_class" instance, built from Base with "optionA" set to True, inherits
"method1" from Grandparent1 and "method2" from Grandparent2, respectively, through
the Parent1 and Parent2 classes. Additionally, its dynamically-added component
"comp" inherits "method3" from the ParentOfComponent1 class.

### Building of Static Component Dependencies

To recursively build component classes that are statically defined in the class
code, the `dynconfig.buildcomponent` function must be used when instantiating
those components.

The example below is constructed based on the example provided in the previous
section, introducing an additional static component called Component2. When a
class is built from the Base class with "optionA" set to True, Component2
dynamically inherits from the ParentOfComponent2 class.

![Class Dependency Diagram](https://github.com/amarula/dyndesign/blob/7664a4456271ccac2f0e27a276a754c2d7f7ec98/docs/img/build_recursive_static_component_example.png?raw=true)

Below are the changes to the code of the previous section.

``` py
...

class ParentOfComponent2:
    def method4(self):
        print("I am `ParentOfComponent2.method4`")


@dynconfig({"optionA": ClassConfig(inherit_from=ParentOfComponent2)})
class Component2:
    pass

...

@dynconfig(Configurator)
class Base(Parent1):
    def __init__(self):
        self.comp2 = dynconfig.buildcomponent(Component2)()


base = Base()
assert hasattr(base, 'comp2')
assert not hasattr(base.comp2, 'method4')

built_class = buildclass(Base, optionA=True)()
...

built_class.comp2.method4()
# I am `ParentOfComponent2.method4`
```

The Base class's constructor statically instantiates the Component2 class as
"comp2" using the `dynconfig.buildcomponent` function. As results:

- When Base is instantiated directly, "comp2" is present, but it does not inherit
  from the ParentOfComponent2 class.
- When the "built_class" instance is built with "optionA" set to True, "comp2"
  does inherit the "method4" method of the ParentOfComponent2 class.

### Building of Forced Dependencies

Starting from DynDesign version 1.1, dependencies can be forced to be added
regardless of the value of the corresponding building option, as an alternative to
using `buildcomponent`. These dependencies retain their dynamic nature, undergoing
recursive configuration. The effect is similar to using static composition, if the
Base class does not need to be used directly (without being built).

For instance, if Component2 in the above code is changed from static to dynamic,
with `force_add` set to True, then the component will be recursively built.

``` py
...

class Configurator:
    optionA = (
        ClassConfig(inherit_from=Parent2),
        ClassConfig(component_class=Component1, component_attr="comp"),
    )
    optionForced = ClassConfig(
        component_class=Component2,
        component_attr="comp2",
        force_add=True
    )

@dynconfig(Configurator)
class Base(Parent1):
    pass


base = Base()
assert not hasattr(base, 'comp2')

built_class = buildclass(Base, optionA=True)()

...

built_class.comp2.method4()
# I am `ParentOfComponent2.method4`
```

In contrast to the previous example, Component2 is not instantiated in `comp2`
when the Base class is instantiated directly. However, the built class has
Component2 recursively built, just like in the previous example.

### Disabling Recursion

Recursion, which is enabled by default, can be turned off using the Unscoped
Setting `build_recursively`. For instance, if `build_recursively` is disabled in
the [Building of Static Component
Dependencies](#building-of-static-component-dependencies) example, only the
classes directly dependent from Base and the component classes instantiated using
`buildcomponent` will be recursively built.

![Class Dependency Diagram](https://github.com/amarula/dyndesign/blob/7664a4456271ccac2f0e27a276a754c2d7f7ec98/docs/img/build_disable_recursion_example.png?raw=true)

The result is shown in te modified code below.

``` py
...

@dynconfig(Configurator, build_recursively=False)
class Base(Parent1):
    def __init__(self):
        self.comp2 = dynconfig.buildcomponent(Component2)()


BuiltClass = buildclass(Base, optionA=True)
built_class = BuiltClass()

assert not hasattr(built_class, 'method1')

assert issubclass(BuiltClass, Parent2)
assert not hasattr(built_class, 'method2')

assert hasattr(built_class, 'comp')
assert not hasattr(built_class.comp, 'method3')

built_class.comp2.method4()
# I am `ParentOfComponent2.method4`
```

The provided code shows that:

- The Parent1 class is not recursively built, so "method1" is not inherited by the
  "built_class" object.
- The Parent2 class is dynamically added as a parent class of the "BuiltClass"
  object, but it is not recursively built either. As a result, "method2" is not
  inherited by "built_class".
- The Component1 class is instantiated as the "comp" object, but it is not
  recursively built. As a result, "method3" is not inherited by
  "built_class.comp".
- The Component2 class is instantiated as the "comp2" object, and it is still
  recursively built because it is instantiated using the
  `dynconfig.buildcomponent` function. As a result, "method4" is inherited by
  "built_class.comp2".

On the contrary, if `build_recursively` was disabled in the [Building of Forced
Dependencies](#building-of-forced-dependencies) example, Component2 would not be
built recursively, similar to how Component1 would also not be built.

## Integration with argparse

Building Options can be provided to `buildclass` in various alternative formats.
The following are all valid calls to the `buildclass` function:

``` py
buildclass(Base, option1=value1, option2=value2)
buildclass(Base, {"option1": value1, "option2": value2})
buildclass(Base, NameSpace(option1=value1, option2=value2))
```

An especially notable format accepted by `buildclass` is the object returned by
the `parse_args` method from the `argparse` package. This allows `buildclass` to
be directly piped to a script argument parser, establishing a **standardized
approach to create scripts using classes configured directly with the script
options**.

Below is an example of Python script that accepts "-a" and "-b" as optional
arguments and builds a class based on those arguments.

``` py
# classbuilder_argparse.py

import argparse
...

@dynconfig({
    "optionA": ClassConfig(inherit_from=P1),
    "optionB": ClassConfig(inherit_from=P2),
})
class Base:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store_true', dest='optionA')
    parser.add_argument('-b', action='store_true', dest='optionB')
    args = parser.parse_args()

    BuiltClass = buildclass(Base, args)
    BuiltClass()

    print("End of script `classbuilder_argparse.py`")
```

The script can be used as follows.

``` bash
$ python classbuilder_argparse.py
End of script `classbuilder_argparse.py`

$ python classbuilder_argparse.py -a
I am the constructor of `P1`
End of script `classbuilder_argparse.py`

$ python classbuilder_argparse.py -b
I am the constructor of `P2`
End of script `classbuilder_argparse.py`
```
<br/>

## Lazy Import of Dependency Modules

As the number of Class Dependencies increases, the prospect of employing **lazy
import of the modules** for these optional classes becomes increasingly appealing.
As explained in the [Syntax](#syntax) section, it is possible to provide both
Configurator and dependent classes by specifying them as paths to the classes
using the dot notation.

In the example below potential dependent classes can be organized into specific
directories and imported dynamically when needed.

```
.
├── lazy_import.py
└── class_builder_config
    ├── lazy_import_config.py
    └── optional_dependencies
        ├── comp1.py
        ├── comp2.py
        ├── ...
        ├── parent1.py
        ├── parent2.py
        └── ...
```

The contents of the files are as follows.

``` py
# class_builder_config/optional_dependencies/comp1.py

class Component1:
    def whoami(self):
        print("I am component `Component1`")
```

``` py
# class_builder_config/optional_dependencies/parent1.py

class Parent1:
    def __init__(self):
        print("I am the Constructor of `Parent1`")
```

...

``` py
# class_builder_config/lazy_import_config.py

from dyndesign import ClassConfig

class Configurator:
    optionA = (
        ClassConfig(inherit_from="parent1.Parent1"),
        ClassConfig(component_class="comp1.Component1", component_attr="comp"),
    )
    optionB = ClassConfig(inherit_from="parent2.Parent2"),
    optionC = ClassConfig(inherit_from="parent3.Parent3"),
    ...
```

``` py
# lazy_import.py

from dyndesign import buildclass, dynconfig
from class_builder_config.lazy_import_config import Configurator

dynconfig.set_global(
    class_builder_base_dir="class_builder_config.optional_dependencies"
)

@dynconfig(Configurator)
class Base:
    pass


built_class = buildclass(Base, optionA=True)()
# I am the Constructor of `Parent1`

built_class.comp.whoami()
# I am component `Component1`
```

**Advantages**: Class Dependencies are only imported when they are needed. This
can help to improve performance and memory usage. In the provided example, only
the Parent1 and Comp1 classes are imported because they are required by "optionA".
Other dependent classes, such as Parent2, Parent3, and so forth, are not imported.

**Disadvantages**: certain advanced code features provided by some IDEs
(Integrated Development Environments), such as source code navigation, are not
available for the classes provided as paths in dot notation.

## Best Practices

Class Builder is compatible with the most popular Python IDEs, such as **PyCharm**
and **Visual Studio Code**, as well as with popular linters including **Mypy**,
**Pylance**, and **Pylint**.

To optimize the experience with IDEs and, more generally, to improve code quality,
developers can adopt the following practices.

### Safely Using Methods from Parent Dependencies

Methods from parent classes that may or may not be dynamically added should be
handled according to the principles outlined in the [Extended Communication
Between Classes](../extended_class_communication) section. To ensure compliance
with requirements of code analyzers, it is advisable to access methods from
dynamically-built parent classes using DynDesign constructs such as
[decoratewith](../extended_class_communication#decoratewith),
[safeinvoke](../extended_class_communication#safeinvoke), or
[safezone](../extended_class_communication#safezone-context-manager), as shown in the example in
[Safely Using Methods From Dependent Classes as
Decorators](#safely-using-methods-from-dependent-classes-as-decorators) section
and in the example below.

``` py
from dyndesign import ..., safeinvoke

class Parent:
    def method(self):
        print("I am `Parent.method`")


@dynconfig({"optionA": ClassConfig(inherit_from=Parent)})
class Base:
    def __init__(self):
        safeinvoke("method", self)


built_class = buildclass(Base, optionA=True)()
# I am `Parent.method`
```

If "method" was invoked directly with `self.method()` in the provided code,
certain code analyzers like Pylint might raise a warning stating

    Cannot access member 'method' for type 'Base'

This warning is resolved when the method is called using `safeinvoke`.

### Type Hinting for Component Dependencies

Using Type Hinting for components that may or may not be dynamically added to the
built classes can help to achieve two goals:

1. **To avoid warnings from code analyzers:** By adding Type Hints to the
   attributes of dynamically added components, code analyzers can be informed of
   the expected type of the attribute. This can help to avoid warnings about
   unexpected types.
1. **To enable advanced code features:** By adding Type Hints for the attributes
   of dynamically added components, certain advanced IDE features, such as source
   code navigation, can be enabled. This can make it easier to find and understand
   the code that employs Class Builder.

If a component is configured to be instantiated exclusively from one specific
class, the Type Hint of the corresponding attribute can be set to that class
directly.

``` py
@dynconfig({"optionA": ClassConfig(component_attr="comp", component_class=A)})
class Base:
    def __init__(self):
        self.comp: A
        ...
```

Conversely, if a component can be instantiated from more than one class, a `Union`
of all the possible classes can be used instead.

``` py
from typing import Union

@dynconfig({
    "optionA": ClassConfig(component_attr="comp", component_class=A),
    "optionB": ClassConfig(component_attr="comp", component_class=B),
})
class Base:
    def __init__(self):
        self.comp: Union[A, B]
        ...
```

Another viable option is to utilize the generic `Type` Type Hint. Alternatively,
if it aligns with the intended class usage, the component can be declared as class
attribute.

``` py
class Base:
    comp: Type

    ...
```

<br/>
