# Class Builder

Class Builder is an impressive module that makes it easy to **build classes by
simply providing a set of configuration settings**.

The primary objective of the Class Builder is to completely **separate** the code
responsible for **class configuration from the core logic** of the classes. Thanks
to a set of ad hoc tools, Python developers can now define a set of possible
configurations for a Base class in terms of **Parent** and **Component** Class
Dependencies. They can then build classes based on the Base class by selecting one
or more Building Options.

The first step involves configuring a Base class with a comprehensive set of
configurations, grouped by Building Options. These Options include **Boolean
Options**, which can result in either a true or false value, and **Switch
Options**, which enable the selection of one of a set of alternative choices.

The class configuration is achieved through the `dynconfig` decorator, offering
three distinct levels of separation between class configuration and core logic:

1. the class configuration can be encapsulated within a Configurator class that
   can be seamlessly associated with the Base class using `dynconfig` as a class
   decorator,
1. the class configuration can be passed to `dynconfig` class decorator as
   argument, or
1. `dynconfig` can also function as method decorator to configure component
   injection within specific methods.

The second and final step involves building a class with the selected Class
Dependencies using the `buildclass` function.

## Getting Started

A Configurator class can be linked to a Base class through the `dynconfig`
decorator. Once the Base class is configured, a new class can be built by passing
the Base class and one or more Building Options to `buildclass`. The Building
Options will determine which Class Dependencies are added to the newly built
class.

``` py
@dynconfig(Configurator)
class Base:
    pass

BuiltClass = buildclass(Base, bool_option=True, switch="switch_option1")
```

The Configurator class defines the building configurations for any possible value
of the Building Options. To achieve this, the Option names are used as a class
attribute names to which the corresponding `ClassConfig` instances are assigned as
values. Each `ClassConfig` instance defines a Class Dependency of either
**Parent** or **Component** type.

``` py
class Configurator:
    bool_option = ClassConfig(component_attr="comp", component_class=Component)

    switch = {
        'switch_option1': ClassConfig(inherit_from=ParentA),
        'switch_option2': ClassConfig(inherit_from=ParentB),
    }
```
In the provided example, if "bool_option" is set to True a Component class is
injected into the built class. Furthermore, if a "switch" selector is selected as
"switch_option1" the built class inherits from a ParentA class. Conversely, if
"switch" is set to "switch_option2" the built class inherits from a ParentB class.

Considering the Options passed to `buildclass` in the first code snippet, the
resulting BuiltClass incorporates the Component class in the "comp" attribute and
inherits from the ParentA class.

## Syntax

### buildclass

The syntax of `buildclass` function is defined as following.

``` py
BuiltClass = buildclass(
    BaseClass,
    option1=val1, option2=val2, ... | {"option1": val1, ...} | obj_with_dict
)
```

The Base class can be provided as the first argument, while the Building Options
can be provided as keyword arguments or as dictionaries passed as the second
arguments. It is worth noting that any object with a `__dict__` attribute can be
used as the second argument to the function. This broadens the scope to include
various classes or instances, including the outcomes of parsing arguments using
`argparse` in a script as shown in the [Using argparse
Output](#using-argparse-output) section.

### Using a Configurator Class

Configurator classes can be associated with the Base class using the `dynconfig`
class decorator. The Configurator class can be provided either directly or as a
string with a dot-notation path to the Configurator class, as described in the
[importclass](../misc_utilities#importclass) utility documentation.

``` py
@dynconfig(ConfiguratorClass | 'path.to.ConfiguratorClass')
class BaseClass:
    ...
```

Below is the complete syntax for Configurator classes.

``` py
class ConfiguratorClass:
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

    GLOBAL_DYNCONFIG = GlobalClassConfig(
        # Unscoped Configuration
        build_recursively = True | False
        class_builder_base_dir = 'path.to.BaseDir'
        option_order = (option1, option2, ...)

        # Dependency Configuration
        default_class = DefaultClass | 'path.to.DefaultClass'
        component_attr = 'component_attribure'
        injection_method = 'injection_method'
        add_components_after_method = True | False
        strict_missing_args = True | False
    )
```
The Configurator is made up of two parts: the Class Dependency configuration and
the Global Configuration.

The Class Dependency configuration associates all potential Class Dependencies
that can be integrated into the Base class with their respective Building Options.
To this end, each potential Building Option is associated with a `ClassConfig`
instance or with a tuple of `ClassConfig` instances, where the `ClassConfig`
instance serves as a foundational configuration unit that allows the addition of
either a Parent or a Component Dependency.

Building Options can be of different types:
- **Boolean Option** that enables the addition of Class Dependencies based on a
  boolean value,
- **Conditional Option** that specifies a condition that must be met in order for
  the Class Dependencies to be added, and
- **Switch Option** that allows the addition of Class Dependencies based on the
  selection of one alternative from a range of choices.

NOTE: *In Configurator classes, configurations with Conditional Options are set up
via `dynconfig.set_configuration`, which can be also employed to programmatically
set configurations of any types. Conditional Options can be provided through the
first argument of `set_configuration` in the form of any callable object,
including lambdas and methods*.

The [Global Configuration](#global-configuration), defined through a
`GlobalClassConfig` instance assigned to the `GLOBAL_DYNCONFIG` attribute,
establishes Global Settings that are applied when building the classes.

### ClassConfig Syntax for Parent Dependencies

For the Parent Dependency configuration, `ClassConfig` has the following syntax:

``` py
ClassConfig(
    inherit_from = ParentClass | 'path.to.Parent' | (Parent1, Parent2, ...),
    default_class = DefaultParentClass | 'path.to.DefaultParentClass'
)
```

**Arguments for Parent Dependencies:**

- **inherit_from**: Type, str *or* Tuple[Type *or* str]  
    The class(es) that the Base class will inherit from if the corresponding Option
    is selected.<br/><br/>

- **default_class**: Type *or* str (*Optional*)  
    The class that the Base class will inherit from if the corresponding Option
    is NOT selected.<br/>

Each dependent class can be provided either directly or as a string with a
dot-notation path to the class, as described in
[importclass](../misc_utilities#importclass).

### ClassConfig Syntax for Component Dependencies

The syntax for the Component Dependency configuration is as following:

``` py
ClassConfig(
    component_class = ComponentClass | 'path.to.ComponentClass',
    component_attr = 'component_attribure'
    default_class = DefaultComponentClass | 'path.to.DefaultComponentClass'
    add_components_after_method = True | False
    injection_method = 'injection_method'
    init_args_keep_first = 0 | 1 | 2 | ...
    init_args_from_self = 'attr' | ('attr1', 'attr2', ...)
    init_kwargs_from_self = {'key1': 'attr1', 'key2': 'attr2', ...}
    strict_missing_args = True | False
)
```

**Arguments for Component Dependencies:**

- **component_class**: Type *or* str  
    The class to be instantiated as component and injected into the Base class
    if the corresponding Option is selected.<br/><br/>

- **component_attr**: str (*Optional*)  
    The class attribute to be initialized with the component class.

    NOTE: *`component_attr` must be provided in any case through one of the four
    methods outlined in the [Global Configuration](#global-configuration)
    section.*<br/><br/>

- **default_class**: Type *or* str (*Optional*)  
    The class to be instantiated as component and injected into the Base class
    if the corresponding Option is NOT selected.<br/><br/>

- **add_components_after_method**: bool (*Optional*)  
    Whether to add the component before or after the injection method. The default
    value is **False**. <br/><br/>

- **injection_method**: str (*Optional*)  
    The method into which the component is to be injected. By default, components
    are injected in the constructor **\_\_init\_\_**. <br/><br/>

- **init_args_keep_first**: int (*Optional*)  
    By default, arguments to be passed to the constructor of the component are
    adapted from the arguments of the injection method, in a manner similar to
    that described for [mergeclass
    constructors](../dynamic_class_design#constructors). If certain or all of the
    positional arguments from the injection method need to be excluded from those
    passed to the constructor of the component, this parameter can be utilized to
    specify how many positional parameters passed to the injection method are to
    be retained. If no positional parameter of the injection method is needed to
    initialize the component, `init_args_keep_first` must be set to zero.
    <br/><br/>

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

### Configuration Passed as dynconfig Arguments

In alternative to using a Configurator class, the configuration settings can be
directly passed to `dynconfig` as following.

``` py
@dynconfig(
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
    },
    build_recursively = True | False
    class_builder_base_dir = 'path.to.BaseDir'
    option_order = (switch_selector1, bool_option2, ...)
    default_class = DefaultClass | 'path.to.DefaultClass'
    component_attr = 'component_attribure'
    injection_method = 'injection_method'
    add_components_after_method = True | False
    strict_missing_args = True | False
)
class Base:
    pass
```

The syntax closely resembles that of the Class configuration, with one notable
distinction: Options are configured using a **dictionary** provided as the first
positional argument to the `dynconfig` decorator. In this scenario, conditions can
be directly defined as dictionary keys in the form of lambda functions or any
other callable object, eliminating the need for `dynconfig.set_configuration`.

With this syntax, the Global Settings (described in the [Global
Configuration](#global-configuration) section) are passed as keyword arguments to
the `dynconfig` decorator.

### dynconfig as Method Decorator

If a component must be configured to be potentially injected into a particular
method, an alternative approach is to use `dynconfig` as a decorator for that
method. Clearly, this syntax only applies to Component Dependencies.

``` py
@dynconfig(...)
class Base:
    pass

    @dynconfig({
        "option1": ClassConfig(...),
        "option2": ClassConfig(...),
        ...
        lambda opt1, opt2, ...: <condition-on-opts>:
            ClassConfig(c...),
        ...
        'switch_selector': {
            'switch_option1': ClassConfig(...),
            'switch_option2': ClassConfig(...),
            ...
            dynconfig.SWITCH_DEFAULT: ClassConfig(...)
        },
        ...
    })
    def method_in_which_to_inject(self, ...):
        ...
```

In the above syntax, all the `ClassConfig` instances do not require specifying an
`injection_method` setting, as the injection method is set to
"method_in_which_to_inject" by default.

## Global Configuration

The Global Configuration settings can apply to either Unscoped Configuration or
Dependency Configuration. The former encompasses settings that globally affect how
a class is built, while the latter comprises settings that specifically govern the
addition of Class Dependencies.

Each Global Setting can be configured using one of four methods:
- **Globally**: This means that the setting will be applied to all classes that
  are configured using dynconfig from the point where the setting is set using
  `dynconfig.set_global`. For example
``` py
dynconfig.set_global(build_recursively=False, add_components_after_method=True)
```
- **Through the `GLOBAL_DYNCONFIG` attribute of a Configurator**: This means that
  the setting will only apply to the settings defined in the Configurator class.
- **As a keyword argument of `dynconfig`**: This means that the setting will only
  apply to the class that is being configured.
- **As a field of `ClassConfig`**: This means that the setting will only apply to
  the Class Dependencies that is added using that `ClassConfig` object. It is
  important to note that only Dependency Configuration settings can be configured
  using this method.

### Unscoped Configuration

The following Global Settings affect the global behavior of Class Builder.

**Unscoped Global Settings:**

- **build_recursively**: bool  
    Whether the classes dependent to the Base class have to be built recursively
    or not. When set to **True** (the Default setting), both the statically
    defined Class Dependencies and those added dynamically are built recursively
    in accordance with the table below.

    |                       | Parent Dependencies |      Component Dependencies       |
    |-----------------------|:-------------------:|:---------------------------------:|
    | **Static**            |    Automatically    | Manually (via **buildcomponent**) |
    | **Added Dynamically** |    Automatically    |           Automatically           |

    If a dependency added dynamically by Class Builder is also dynamically
    configurable, it will be automatically configured with the same Options as
    the Base class. This also applies to static parent classes of base classes.
    However, if a static component class requires recursive configuration, it
    needs to be explicitly configured using `buildcomponent`, as explained in
    details in [this section](#building-of-static-component-dependencies).<br/><br/>

- **class_builder_base_dir**: str  
    The base directory from which the Configurator and Dependent Classes are
    dynamically imported. <br/><br/>

- **option_order**: Type *or* str  
    The order in which Building Options must be assessed for applying the
    corresponding `ConfigClass` instances. If multiple Options are enabled, this
    sequence could impact the Method Resolution Order (MRO) of dynamically
    inherited classes or the instantiation of components within a class
    attribute.<br/>

### Dependency Configuration

Described in details in the [ClassConfig
Syntax](#classconfig-syntax-for-parent-dependencies).

## Basic Examples

### Component Class

A basic example of a Boolean Option that can be used to control the instantiation
of the component class "A" and to assign it to the "self.comp" attribute can be
found below.

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

If the Base class is built with "optionA" set to True, the "A" class is assigned
to "self.comp", otherwise the "comp" attribute remains unassigned.

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

NOTE: *From this point onwards, the bodies of component classes such as "A", "B",
"C", ..., and Default, along with those of parent classes P1, P2, ..., and
PDefault, will be assumed to have the same form as in the previous examples and
will therefore be omitted from the following code snippets unless otherwise
specified. Import statements of `buildclass`, `dynconfig`, `ClassConfig`, and
`GlobalClassConfig` will be implied as well.*

## Switches

Switches are a powerful construct for managing Options that have values other than
True or False.

``` py
class Configurator:
    switch = {
        "optionA": ClassConfig(component_class=A),
        "optionB": ClassConfig(component_class=B),
        dynconfig.SWITCH_DEFAULT: ClassConfig(component_class=Default)
    }
    GLOBAL_DYNCONFIG = GlobalClassConfig(component_attr="comp")


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
"optionB", the corresponding component classes are injected into the
"self.comp" attribute. Otherwise, the Default class, set up through the
`dynconfig.SWITCH_DEFAULT` fixed key, is injected by default.

The code also shows how to use the `GLOBAL_DYNCONFIG` fixed attribute. This
attribute can be used to set Dependency Configuration settings that are applied to
all `ClassConfig` nodes. In this case, the "comp" setting is globally assigned to
`component_attr`: this means that all `ClassConfig` nodes use "comp" as attribute
to instantiate the components, unless it is overridden in a specific node.

## Multiple Dependencies per Option

In the code below, some modifications are applied to the previous example to
demonstrate how complex functionalities can be easily implemented.

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

    GLOBAL_DYNCONFIG = GlobalClassConfig(component_attr="comp")


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
"bool_option", has been introduced to illustrate the handling of Building Options
with varying types. Components "A", "B", "D", and Default are instantiated by
default in the "comp" attribute, thanks to the Global Setting
`component_attr="comp"`, while "C" is instantiated in "comp2".

As results:

- When a class is built with "switch" set to "optionA", "A" is instantiated in
  "comp".
- When "switch" is set to "optionB", "B" is instantiated in "comp" and "C" is
  instantiated in "comp2".
- When "bool_option" is set to True, "D" is instantiated in "comp".
- When a class is built with no Option, Default class is instantiated in "comp".

## Conditional Options

To allow for enhanced flexibility, conditional functions are also permitted as
Building Options.

### Boolean Functions of other Building Options

In the code snippet below, a lambda function is employed from a dictionary
provided as the first argument to the `dynconfig` class decorator.

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
The lambda function checks if the 'optionA' setting is set to True and the
'optionB' setting is set to False or not set. If both of these conditions are met,
the 'A' component is added as a dependency.

NOTE: *The arguments' names in the conditional function must match the Building
Options used in `buildclass`.*

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
  the Base class attributes.*
- *When using class configurators, the Conditional Options must be defined using
  `dynconfig.set_configuration`.*

## Safe Communication with Dependent Classes

### Safely Calling Methods from Components

If the Base class of the preceding composition examples was instantiated as a
standalone class, without being built, an error would occur when the "self.comp"
attribute is invoked. To silently ignore the error, the
[safeinvoke](../extended_class_communication#safeinvoke) or the
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
section so that both the constructors of the parent classes are called when both
the Options "optionA" and "optionB" are set to True. To achieve this, both
dynamically added superclasses need to be accessed from within the Base's
constructor when both Options are True.

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
True, it is necessary to employ the `super` function with parameters, with the
initial parameter being the first parent class (P1). However, employing `super(P1,
self)` directly would lead to a `TypeError` whenever the class is built without
P1. To seamlessly bypass the error, the [safesuper
function](../extended_class_communication#safesuper-function) is utilized instead.

It is worth noting that the above implementation raises no exception even if the
Base class is directly instantiated without building it.

### Safely Using Methods from Dependent Classes as Decorators

Class Builder's capabilities shine when combined with the
[decoratewith](../extended_class_communication#decoratewith) meta decorator.
Through this combination, both dynamically added Parent and Component Dependencies
can be seamlessly utilized to decorate methods of the base classes. Even if any or
all of the parent or component classes are not added, the execution continues
without errors.

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

In the example below, if the Base class is built with "optionA" set to True, the
"A" class is injected in "self.comp", otherwise the Default class is injected.

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

By default, the components are injected before the `__init__` constructor is
called. To inject the components in a custom method, the `injection_method`
setting can be used.

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
instantiated yet when the constructor of the Base class is executed.

### Using dynconfig as Method Decorator to Configure Components

For convenience, `dynconfig` can be directly used as a method decorator to
configure component injection into specific methods, including `__init__`.

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

By default, components are injected **before** the method is called. This behavior
can be changed to inject the components **after** or in the **middle** of the
method.

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

In the example provided, the "A" component is injected after the constructor
`__init__`, while the "B" component is injected within the execution of
"injection_method".

NOTE: *To inject components at specific points within a method, the
`dynconfig.inject_components` fixed method is used*.

### Argument Adaptation

To initialize a component, specific arguments can be used. By default, the
arguments passed to the injection method are adapted to match the parameters of
the component constructor. Specifically, any excessive positional arguments from
the signature of the injection method are filtered out, and non-positional
arguments are passed to the component constructor by matching their names.

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
  components "A" and is filtered out when components "B" is initialized;
- the second positional argument "b" of `__init__` is filtered out when
  initializing both components "A" and "B";
- the keyword argument "kw1" is used to initialize "A", based on the name
  matching; and
- the keyword argument "kw2" is used to initialize "B".

### Altering Behavior with Missing Required Arguments

As previously mentioned, excessive positional arguments are filtered out before
being transferred to the component constructors. However, what occurs when the
component constructors lack the required positional arguments? By default, a
`TypeError` exception is raised, as shown in the modified code below.

``` py
...

@dynconfig(Configurator)
class Base:
    pass


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
raise an exception, and the execution proceeds to add the "B" component.

NOTE: *The example above also shows a hybrid way to configure the Global Settings.
Instead of defining them using the `GLOBAL_DYNCONFIG` variable in the Configurator
class, they can be passed directly as keyword arguments to the `dynconfig`
function, in the same way as when passing the configuration settings explicitly.*

### Component Initialization Parameters

The arguments that are passed to component constructors can be customized to
achieve any desired result. This can be accomplished through two distinct
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
constructor is called (as "option1" is True), and the second time in the middle of
the "injection_method" method (given that "option2" is True).

On the first instantiation, the following argument modifications take place within
the `__init__` method: initially, the first positional argument ("x.passed") is
retained, while the second ("y.passed") is discarded by using
`init_args_keep_first`. Then, the value of the "self_b" property of the `self`
object ("y.self") is appended to the positional arguments, utilizing
`init_args_from_self`. Lastly, the keyword argument "kw" is assigned the value
from the "self_kw" property of the `self` object ("z.self"), employing
`init_kwargs_from_self`.

The argument substitution adopted in the second instantiation is easier to
understand and implement, but it does not allow for as much separation between the
core logic and the configuration. The arguments are directly passed to
`inject_components`, which then forwards them to the constructor of "A". In the
example, the first positional argument "a" is taken from the one provided to the
method, the second argument is obtained from `self.self_b`, and the value of the
keyword argument "kw" is hardcoded.

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

In the above example, the first class to be added in the Base's superclass set is
P2, followed by P1. For this reason, the constructor of P2 is the one that is
called when the built class is instantiated.

## Recursive Building

One of the most remarkable features of the Class Builder is its ability to
recursively track the Class Dependencies of a class, enabling the building of
classes configured using `@dynconfig` in a cascading manner.

### Dependencies Built Recursively by Default

As shown in the table in the [Unscoped Configuration](#unscoped-configuration)
section, the following Class Dependency types are built recursively by default
using the same Building Options as the base classes: Parent Dependencies (both
static and dynamically added) and Component Dependencies (dynamically added).

In this example, an entire hierarchy of Component and Parent Dependencies is added
to the Base class when it is built with "optionA" set to True. The visual
representation provided in the diagram below illustrates the hierarchical
relationships among these classes. At the bottom, the Base class statically
inherits from the Parent1 class (depicted as a solid line). When a new class is
built with "optionA" set, the Class Dependencies (indicated by dashed lines) are
recursively added as follows:

- The Parent1 class inherits from the Grandparent1 class.
- The Base class inherits from the Parent2 class.
- The Parent2 class inherits from the Grandparent2 class.
- The Component1 class is added to the Base class.
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
"comp2" using the `dynconfig.buildcomponent` function. Therefore, when Base is
instantiated directly, "comp2" is present, but it does not inherit from the
ParentOfComponent2 class. On the other hand, when the "built_class" class is built
with "optionA" set to True, "comp2" does inherit the "method4" method of the
ParentOfComponent2 class.

### Disabling Recursion

Recursion, which is enabled by default, can be turned off using the Unscoped
Global Setting `build_recursively`. For instance, if `build_recursively` is
disabled in the previous example, only the classes directly dependent from Base
and the component classes built using `dynconfig.buildcomponent` will be
recursively configured.

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
- The Component2 class is instantiated as the "comp2" object, and it is
  recursively built using the "dynconfig.buildcomponent" function. As a result,
  "method4" is inherited by "built_class.comp2".

## Using argparse Output

Options for configuration can be provided to `buildclass` in various alternative
formats. The following are all valid calls to the `buildclass` function:

``` py
buildclass(Base, option1=value1, option2=value2)
buildclass(Base, {"option1": value1, "option2": value2})
buildclass(Base, NameSpace(option1=value1, option2=value2))
```

An especially notable format is the output generated by the `parse_args` method
from the `argparse` package. This allows a Class Builder to be directly piped to a
script argument parser, establishing a **standardized approach for crafting
scripts driven by custom options**.

Below is a Python script that accepts "-a" and "-b" as options and constructs a
class based on those options.

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

## Lazy Import of Optional Modules

As the number of optional dependencies and their corresponding classes increases,
the prospect of employing **deferred (lazy) import of the modules** for these
optional classes becomes increasingly appealing. As explained in the
[Syntax](#syntax) section, it is possible to provide both Configurators and
Dynamic Class Dependencies by specifying them as paths to classes using dot
notation.

In the example below optional Class Dependencies can be organized into specific
directories and loaded dynamically when needed.

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
# I am the Constructor of `Parent`

built_class.comp.whoami()
# I am component `Component`
```

**Advantages**: Class Dependencies are only imported when they are needed. This
can help to improve performance and memory usage. In the provided example, only
the Parent1 and Comp1 classes are imported because they are required by "optionA".
Other Dependencies, such as Parent2, Parent3, and so forth, are not imported.

**Disadvantages**: certain advanced code features provided by some IDEs
(Integrated Development Environments), such as source code navigation, are not
available for the classes provided as paths in dot notation.

## Best Practices

Class Builder is compatible with the most popular Python IDEs, such as **PyCharm**
and **Visual Studio Code**, as well as with popular linters including **mypy**,
**pylance**, and **pylint**.

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

### Type Hinting for Component Dependencies

Using Type Hinting for components that may or may not be dynamically added to the
built classes can help to achieve two goals:

1. **Avoid warnings from code analyzers:** By adding Type Hints to the attributes
   of dynamically added components, the code analyzer can be informed of the
   expected type of the attribute. This can help to avoid warnings about
   unexpected types.
1. **Enable advanced code features:** Some IDEs offer advanced code features, such
   as source code navigation. By adding Type Hints to the attributes of
   dynamically added components, these features can be enabled. This can make it
   easier to find and understand the code developed using Class Builder.

If a component is configured to be instantiated exclusively from one specific
class, the Type Hint of the corresponding attribute can be set to that class
directly.

``` py
@dynconfig({"optionA": ClassConfig(component_attr="comp", component_class=A)})
class Base:
    def __init__(self):
        self.comp: A
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
```

Another viable option is to utilize the generic `Type` Type Hint. Additionally, if
it aligns with the intended class usage, the component can be declared as class
attribute.

``` py
class Base:
    comp: Type
```

<br/>
