# Documentation


## mergeclasses

Dyndesign provides API `mergeclasses` to merge two or more classes as if they
were dictionaries. As a result, the newly created class has the same properties
of both its base class and any added extensions.

### Syntax

``` py
MergedClass = mergeclasses(
    Base | "path.to.Base",
    Ext1 | "path.to.Ext1",
    Ext2 | "path.to.Ext2",
    ...,
    invoke_all=None,
    strict_merged_args=True
)
```

**Arguments:**

- **Base**: type (*Class*) *or* str  
    Foundation class whose functionality is extended by one or more extension
    classes. Class Base can be either directly passed as the first argument,
    or alternatively a path to the class in dot notation (as outlined in the
    [importclass](#importclass) documentation) can be provided.<br/><br/>

- **Ext1**, **Ext2**, ...: type (*Class*) *or* str  
    One or more extension classes to extend the properties of the base class.
    <br/><br/>

- **invoke_all**: List (*Optional*)  
    By default, all the methods and attributes with the same name are
    overloaded. One exception applied by default to this rule is the constructor
    `__init__`, whose instances are invoked in all the component classes,  as
    outlined in the [Constructors](#constructors) documentation. Such a behavior
    can be extended to other methods by passing the method names in the
    `invoke_all` list. <br/><br/>

- **strict_merged_args**: bool (*Optional*)  
    Certain `__init__` instances may require more positional arguments than the
    ones passed when the class is instantiated: in that case, those `__init__`
    instances raise a "Missing arguments" exception. The same applies also when
    the method instances listed in `invoke_all` are called with less positional
    arguments than required. If `strict_merged_args` is set to False, the method
    instances invoked with missing positional arguments are silently skipped
    instead. <br/><br/>

- ***return***: type (*Class*)  
    Merged class that brings together the properties of the base and of the
    extension classes.<br/>


### Basic Examples

Two classes can be easily combined together as in the following example:

``` py
from dyndesign import mergeclasses

class Base:

    attr_base = "Attribute from Base"

    def method_base(self):
        return "Method from Base"

class Ext:

    attr_ext = "Attribute from Ext"

    def method_ext(self):
        return "Method from Ext"

MergedClass = mergeclasses(Base, Ext)
print(MergedClass.attr_base)
print(MergedClass.attr_ext)

merged = MergedClass()
print(merged.method_base())
print(merged.method_ext())

# Attribute from Base
# Attribute from Ext
# Method from Base
# Method from Ext
```

In the example below it is shown that arguments of mergeclasses can be
alternatively passed as path to classes in dot notation, following the syntax
outlined in the [importclass](#importclass) documentation. Additionally, it is
shown that merged classes can be merged in turn with other classes.  
Assuming that a package "directory/extensions.py" includes class "Ext2" (defined
analogously to "Ext"), the following lines can be appended to the example above:

``` py
...
MergedClass2 = mergeclasses(MergedClass, "directory.extensions.Ext2")
print(MergedClass2.attr_ext2)

merged2 = MergedClass2()
print(merged.method_ext2())

# Attribute Ext2
# Method Ext2
```

### Overloading of methods and attributes

If two or more classes have attributes/methods with the same name, then the
attributes/methods from the rightmost classes (in the order in which the classes
are passed to `mergeclasses`) overload the ones from the leftmost classes,
similarly to what happens when merging dictionaries.

``` py
from dyndesign import mergeclasses

class Base:
    def __init__(self, init_value):
        self.param = init_value

    def m1(self):
        print(f"Method `m1` of class `Base`, and {self.param=}")

    def m2(self):
        print(f"Method `m2` of class `Base`")

class Ext:
    def m1(self):
        print(f"Method `m1` of class `Ext`, and {self.param=}")

MergedClass = mergeclasses(Base, Ext)
merged_instance = MergedClass("INITIAL VALUE")
merged_instance.m1()
merged_instance.m2()

# Method `m1` of class `Ext`, and self.param='INITIAL VALUE'
# Method `m2` of class `Base`
```

### Constructors

When a merged class is instantiated with arguments, the constructor of each
merging class is invoked, since constructors are excluded from being overloaded.
Also, arguments passed to each constructor are adaptively filtered based on the
constructor signature so that each constructor takes just the arguments it
needs:

``` py
from dyndesign import mergeclasses

class A:
    def __init__(self):
        print("No argument passed to class `A`")

class B:
    def __init__(self, a):
        print(f"Argument {a=} passed to class `B`")

class C:
    def __init__(self, a, b, kw1=None):
        print(f"Argument {a=}, {b=} and {kw1=} passed to class `C`")

class D:
    def __init__(self, kw2=None):
        print(f"Argument {kw2=} passed to class `D`")

MergedClass = mergeclasses(A, B, C, D)
MergedClass("Alpha", "Beta", kw1="kwarg #1", kw2="kwarg #2")

# No argument passed to class `A`
# Argument a='Alpha' passed to class `B`
# Argument a='Alpha', b='Beta' and kw1='kwarg #1' passed to class `C`
# Argument kw2='kwarg #2' passed to class `D`
```

If a constructor signature includes N positional arguments and the merged class
is instantiated with less than N positional arguments, then a `TypeError`
exception is raised. For example, if `MergedClass` of the above example is
initialized with no parameters, the following exception is raised when the
constructor of class "B" is called:

``` py
...
MergedClass()

# ...
# TypeError: B.__init__() missing 1 required positional argument: 'a'
```

Sometimes this behavior needs to be reverted so that the constructor instances
invoked with missing positional arguments are silently skipped: to this end,
`strict_merged_args` can be set to False in `mergeclasses`. In the example
above, constructors of class "B" and "C" are skipped as `strict_merged_args` is
set to False:

``` py
...
MergedClass = mergeclasses(A, B, C, D, strict_merged_args=False)
MergedClass()

# No argument passed to class `A`
# Argument kw2=None passed to class `D`
```

### Invoking all the instances of a method

The same behavior of the constructor `__init__` can be extended to selected
methods as well. This means that when the selected methods are called, all the
instances of methods from all the merged classes are invoked rather than being
overloaded by the same-name methods from the rightmost classes. A list of method
names whose instances must be all invoked can be specified in the `invoke_all`
argument of `mergeclasses`. Adaptive filtering of the arguments of the method
instances is performed in the same way as for `__init__`. In the following
example, both the instances of "method" in classes "E" and "F" are executed:

``` py
from dyndesign import mergeclasses

class E:
    def method(self):
        print("No argument passed to `method` of class `E`")

class F:
    def method(self, a):
        print(f"Argument {a=} passed to `method` of class `F`")

MergedClass = mergeclasses(E, F, invoke_all=["method"])
MergedClass().method("Alpha")

# No argument passed to `method` of class `E`
# Argument a='Alpha' passed to `method` of class `F`
```

### Merged classes and inheritance

API `mergeclasses` is designed to merge classes that inherit from other classes
in a way that is intuitive and produces expected results:

``` py
from dyndesign import mergeclasses

class ParentA:
    def __init__(self) -> None:
        print("This is `__init__` of `ParentA`")

    def method_1(self):
        print("This is ParentA.method_1")

    def method_3(self):
        print("This is ParentA.method_3")


class ChildA(ParentA):
    def __init__(self) -> None:
        super().__init__()
        print("This is `__init__` of `ChildA`")

    def method_2(self):
        print("This is ChildA.method_2")


class ParentB:
    def __init__(self) -> None:
        print("This is `__init__` of `ParentB`")

    def method_2(self):
        print("This is ParentB.method_2")


class ChildB(ParentB):
    def __init__(self) -> None:
        super().__init__()
        print("This is `__init__` of `ChildB`")

    def method_1(self):
        super().method_1()
        print("This is ChildB.method_1")


merged = mergeclasses(ChildA, ChildB)()

# This is `__init__` of `ParentA`
# This is `__init__` of `ChildA`
# This is `__init__` of `ParentB`
# This is `__init__` of `ChildB`

merged.method_1()
merged.method_2()
merged.method_3()

# This is ParentA.method_1
# This is ChildB.method_1
# This is ParentB.method_2
# This is ParentA.method_3
```

It is observed that the merging of classes is carried out while maintaining the
ancestral hierarchical structure. This means that only classes that are at the
same level of inheritance are merged. In the example provided, "ParentA" is
merged with "ParentB", and "ChildA" is merged with "ChildB".

It is also important to note that all inheritance functionalities still work as
intended, meaning that "method_1" of "ParentA" can be accessed via cross-calling
with "super().method_1()" from "ChildB". However, attempting to call "method_1"
from a standalone instance of "ChildB" results in the exception
``` bash
AttributeError: 'super' object has no attribute 'method_1'
```
To ensure that "super().method_1" is skipped without generating an exception
when it is not found, [safeinvoke](#safeinvoke) can be used in
"ChildB.method_1":

``` py
from dyndesign import safeinvoke

...

class ChildB(ParentB):
    ...
    def method_1(self):
        safeinvoke("method_1", super())
        print("This is ChildB.method_1")


ChildB().method_1()

# This is `__init__` of `ParentB`
# This is `__init__` of `ChildB`
# This is ChildB.method_1
```

<br/>

## decoratewith

Meta decorator `decoratewith` can be used to decorate a class method with one or
more pipelined dynamic decorators, regardless whether they statically exist or
not. Additionally, the syntax of the dynamic decorators aims to get rid of the
boilerplate for wrapping and returning the decorator code, leaving just the
wrapper's code.

### Syntax

``` py
@decoratewith(
    "decorator1", "decorator2", ...,
    method_sub_instance=None,
    fallback=None,
    disable_property=None
)
def decorated_method(...):
    ...
```

**Arguments:**

- **decorator1**: str  
    Decorator method to decorate "decorated_method".  
    Decorator "decorator1" may or may not exist at "decorated_method" call time:
    in other words, if "decorator1" is a property of `self` when
    "decorated_method" is invoked, then it is used to decorate
    "decorated_method", otherwise the method is executed without any decoration.  
    **Note:** Any sub-property of `self`, such as methods of component classes,
    may be also used as decorator: in this case the **dot notation** can be used
    to select the path to the decorator method.<br/><br/>

- **decorator2**, ...: str (*Optional*)  
    Further decorator methods to optionally decorate method "decorated_method"
    in pipeline. All the decorator methods are executed as they were nested one
    into the other following the order in which they are passed to
    `decoratewith`. <br/><br/>

- **method_sub_instance**: str (*Optional*)  
    If all the decorator methods have the same initial path (typically if they
    are all methods of one component class), the initial path in common can be
    omitted and passed in `method_sub_instance` to avoid repetitions.<br/><br/>

- **fallback**: Callable (*Optional*)  
    If any decorator does not exists at the the "decorated_method" call time,
    then a "fallback" function is called with the same arguments passed to
    "decorated_method".<br/><br/>

- **disable_property**: str (*Optional*)  
    Class property name evaluated at "decorated_method" call time. If it is
    found to be True, then the application of the decorators is disabled.<br/>

If a decorator method is a property of `self`, then it must follow the syntax:

``` py
def decorator(self, func):
    ...
    func(self)
    ...
```

Otherwise, if it is a sub-property of a `self` (e.g., a property of a component
class), then the syntax will be:

``` py
def decorator(self, func, decorated_self):
    ...
    func(decorated_self)
    ...
```

wherein `self` refers to the sub-property instance, and `decorated_self` to the
main class instance.

### Basic Examples

Dynamic decorators can be used to decorate a method of a base class with a
method of an extension class:

``` py
from dyndesign import decoratewith, mergeclasses

class Base:
    @decoratewith("decorator")
    def m(self):
        print(f"Method `m` of class `Base`")

class Ext:
    def decorator(self, func):
        print("Beginning of method decoration from Ext.")
        func(self)
        print("End of method decoration from Ext.")

merged = mergeclasses(Base, Ext)()
merged.m()

# Beginning of method decoration from Ext.
# Method `m` of class `Base`
# End of method decoration from Ext.

base = Base()
base.m()
# Method `m` of class `Base`
```

It is noted that when method "m" is called directly in class "Base" without
extending it to "Ext", then the decoration is skipped and the method is executed
normally.


Additional parameters can be passed to the decorated and decorator methods:

``` py
from dyndesign import decoratewith, mergeclasses

class Base:
    @decoratewith("decorator")
    def m(self, param):
        print(f"Method `m` of class `Base` - {param=}.")

class Ext:
    def decorator(self, func, param):
        print(f"Beginning of method decoration from Ext - {param=}.")
        func(self, param)
        print("End of method decoration from Ext.")

merged = mergeclasses(Base, Ext)()
merged.m("BETA")

# Beginning of method decoration from Ext - param='BETA'.
# Method `m` of class `Base` - param='BETA'.
# End of method decoration from Ext.
```

### Pipeline of dynamic decorators

Multiple dynamic decorators are pipelined as the following:

``` py
from dyndesign import decoratewith

class Multi:
    @decoratewith("decorator1", "decorator2", "decorator3")
    def decorated(self):
        print(f"Method `decorated`")

    def decorator1(self, func):
        print("Beginning of decorator1.")
        func(self)
        print("End of decorator1.")

    def decorator2(self, func):
        print("Beginning of decorator2.")
        func(self)
        print("End of decorator2.")

    def decorator3(self, func):
        print("Beginning of decorator3.")
        func(self)
        print("End of decorator3.")

multi = Multi()
multi.decorated()

# Beginning of decorator1.
# Beginning of decorator2.
# Beginning of decorator3.
# Method `decorated`
# End of decorator3.
# End of decorator2.
# End of decorator1.
```
In this example, decorated and decorator methods share the same class. Python
builtin decorators could also be used in this case, but it must be considered
that dynamic decorators are easier to implement than builtin ones.

### Overloading dynamic decorators

When merging classes, dynamic decorators with the same name follow the same
overload rules as the normal methods, i.e. the rightmost decorators win. If for
example class "Ext2" including another instance of decorator "decorator" is
merged to the merge chain, the rightmost instance of "decorator" overloads the
leftmost:

``` py
from dyndesign import decoratewith, mergeclasses

class Base:
    @decoratewith("decorator")
    def m(self):
        print(f"Method `m` of class `Base`")

class Ext:
    def decorator(self, func):
        print("Beginning of method decoration from Ext.")
        func(self)
        print("End of method decoration from Ext.")

class Ext2:
    def decorator(self, func):
        print("Beginning of method decoration from Ext2.")
        func(self)
        print("End of method decoration from Ext2.")

merged = mergeclasses(Base, Ext, Ext2)()
merged.m()

# Beginning of method decoration from Ext2.
# Method `m` of class `Base`
# End of method decoration from Ext2.
```

### Using all the instances of a decorator

The overload behavior of dynamic decorators can be altered with `invoke_all` in
the same way as it works with methods. If a decorator name is passed in the
`invoke_all` list as argument of `mergeclasses`, then multiple decorator
instances with the same name from different extension classes are applied in
pipeline, as if they had different names. In the above example, passing
"decorator" in the `invoke_all` list of `mergeclasses` results in:

``` py
...

merged = mergeclasses(Base, Ext, Ext2, invoke_all=["decorator"])()
merged.m()

# Beginning of method decoration from Ext.
# Beginning of method decoration from Ext2.
# Method `m` of class `Base`
# End of method decoration from Ext2.
# End of method decoration from Ext.
```

### Decorators from ancestor classes

Arguments of `decoratewith` are loaded at runtime as properties of the variable
`self`, enabling dynamic decorators to be implemented using, for instance, a
method from a parent class, which is not possible with static decorators.

``` py
from dyndesign import decoratewith

class Parent:
    @staticmethod
    def decorator(func):
        print("Beginning of method decoration from Parent.")
        func()
        print("End of method decoration from Parent.")

class Child(Parent):
    @decoratewith("decorator")
    @staticmethod
    def m():
        print(f"Method `m` of class `Child`")

child = Child()
child.m()

# Beginning of method decoration from Parent.
# Method `m` of class `Child`
# End of method decoration from Parent.
```

The example above also shows that dynamic decorators can be combined with other
static decorators with other static decorators, such as `staticmethod`.

### Decorators from component classes

A dynamic decorator can be a method of a component class as well. In case of
dynamic decoration from a sub-instance of `self`, the instance object of the
decorated method is passed to the decorator as the argument `decorated_self`.

``` py
from dyndesign import decoratewith

class Base:
    def __init__(self):
        self.comp = Component()

    @decoratewith("comp.decorator1", "comp.decorator2")
    def m(self):
        print("Method `m` of class `Base`")

class Component:
    def __init__(self):
        self.value = "Initial"

    def decorator1(self, func, decorated_self):
        print(f"Beginning of method decoration #1 ({self.value=})")
        self.value = "Processed"
        func(decorated_self)
        print("End of method decoration #1")

    def decorator2(self, func, decorated_self):
        print(f"Beginning of method decoration #2 ({self.value=})")
        func(decorated_self)
        print("End of method decoration #2")

base = Base()
base.m()

# Beginning of method decoration #1 (self.value='Initial')
# Beginning of method decoration #2 (self.value='Processed')
# Method `m` of class `Base`
# End of method decoration #2
# End of method decoration #1
```

### Building decorators at runtime

Dynamic decorators can be also built at runtime. In the example below, decorator
"deco" exists nowhere statically, but it is programmatically built by the
function "build_decorator":

``` py
from dyndesign import decoratewith

def build_decorator(instance):
    def decorator(func):
        print("Start Decoration")
        func(instance)
        print("End Decoration")
    return decorator

class DecoratedClass:
    @decoratewith("deco")
    def main_method(self):
        print("Main Method")

decorated_class = DecoratedClass()
decorated_class.deco = build_decorator(decorated_class)
decorated_class.main_method()

# Start Decoration
# Main Method
# End Decoration
```

### Decorators with fallback

If a fallback method is provided, then it is executed when a decorator does not
exist at the call time of decorated method. For example:

``` py
from dyndesign import decoratewith

class Base:
    def fallback_method(self):
        print(f"Fallback method")

    @decoratewith("decorator", fallback=fallback_method)
    def m(self):
        print(f"Method `m` of class `Base`")

class Ext:
    def decorator(self, func):
        print("Beginning of method decoration from Ext.")
        func(self)
        print("End of method decoration from Ext.")

merged = mergeclasses(Base, Ext)()
merged.m()

# Beginning of method decoration from Ext.
# Method `m` of class `Base`
# End of method decoration from Ext.

Base().m()

# Fallback function
# Method `m` of class `Base`
```

<br/>

## safezone Context Manager

Any function or method that may or may not exist at runtime (e.g., methods from
merged classes) can be invoked from Context Manager `safezone` in order to
selectively suppress the exceptions possibly raised if the function or method is
not found.

### Syntax

``` py
with safezone("callable_name1", "callable_name2", ..., fallback=fallback):
    ...
```

**Arguments:**

- **callable_name1**, **callable_name2**, ...: str (*Optional*)  
    If one or more callable names are passed as arguments, then the exceptions
    raised when specific callables are not available at runtime are suppressed in
    the context. If no callable names are passed, then those exceptions are
    suppressed for all the callables.<br/><br/>

- **fallback**: Callable (*Optional*)  
    If any callable invoked within the `safezone` context does not exists at the
    call time, then a "fallback" function is called with the same arguments
    passed to the missing callable.<br/>

### Safe zone for functions

If no function name is passed as argument of `safezone`, then each function in
the safe zone's context is protected; if any function name is passed, the
protection is restricted to the functions having that name. For example,
`safezone` can be used to safely call functions that may or may not exist at
runtime:

``` py
from dyndesign import safezone

def fallback():
    print("Fallback function")

def function_a():
    print("Function `a`")

with safezone(fallback=fallback):
    function_a()
    non_existent_function()

# Function `a`
# Fallback function
```

### Safe zone for methods

A further example shows that `safezone` can be used to safely invoke methods
of classes that may or may not be merged with other classes:

``` py
from dyndesign import mergeclasses, safezone

class Base:
    def fallback(self):
        print("Fallback method")

    def m(self, class_desc):
        print(f"Method `m` of {class_desc}")
        with safezone("optional_method", fallback=self.fallback):
            self.optional_method()

class ExtOptional:
    def optional_method(self):
        print("Optional method from class `ExtOptional`")

merged = mergeclasses(Base, ExtOptional)()
merged.m("merged class")

# Method `m` of merged class
# Optional method from class `ExtOptional`

Base().m("class `Base` standalone")

# Method `m` of class `Base` standalone
# Fallback method
```

<br/>

## safeinvoke

As an alternative to `safezone` context manager, `safeinvoke` API can be used to
safely invoke methods that may or may not exist at runtime.

### Syntax

``` py
returned_value = safeinvoke("method_name", instance, fallback=fallback, *args, **kwargs)
```

**Arguments:**

- **method_name**: str  
    If method "method_name" exists at runtime in "instance", then it is invoked
    with instance "instance" and further arguments optionally passed. Otherwise,
    execution proceeds normally without any exception raised.<br/><br/>

- **instance**: object  
    Class instance that may or may not include the method referenced to with
    "method_name".<br/><br/>

- **fallback**: Callable (*Optional*)  
    If "method_name" does not exists at runtime, then a "fallback" function is
    called with the same arguments passed to "method_name".<br/><br/>

- **args** (*Optional*)  
    Positional arguments passed to "method_name".<br/><br/>

- **kwargs** (*Optional*)  
    Keyword arguments passed to "method_name".<br/><br/>

- ***return*** (*Optional*)  
    Value optionally returned by "method_name" if "method_name" exists at
    runtime, `None` otherwise.<br/>


### Basic Example

Method `m` of class `Base` of the example in [Safe zone for
methods](#safe-zone-for-methods) can be rewritten using `safeinvoke`:

``` py
from dyndesign import safeinvoke

...

    def m(self, class_desc):
        print(f"Method `m` of {class_desc}")
        safeinvoke("optional_method", self, fallback=self.fallback)
```

<br/>

## SingletonMeta Metaclass

Singleton classes can be swiftly created with `SingletonMeta` metaclass and then
destroyed with `destroy_singleton` or `SingletonMeta.destroy`.

### Syntax

To create a singleton class, metaclass `SingletonMeta` can be used:

``` py
class SingletonClass(..., metaclass=SingletonMeta):
    ...
```

Target singleton classes can be destroyed by calling method `destroy_singleton`
(automatically injected in the singleton instance):

``` py
...
singleton_instance = SingletonClass(...)
singleton_instance.destroy_singleton()
```

Alternatively, singleton classes can be destroyed by using the metaclass method
`destroy`

``` py
SingletonMeta.destroy("ClassName1", "ClassName2", ...)
SingletonMeta.destroy()
```

**Arguments:**

- **ClassName1**, **ClassName2**, ...: str (*Optional*)

    Class names to destroy. If no class name is provided, **ALL** the singleton
    classes are destroyed.



### Basic Example

In the example below, class "Singleton" is created the first time with parameter
"instance_id" equal to "first". Further instances of "Singleton" still point to
the same "first" instance, regardless of the value of "instance_id" passed.
After that "Singleton" is destroyed with `destroy_singleton`, a instance is
created with "instance_id" equal to "second".

``` py
from dyndesign import SingletonMeta

class Singleton(metaclass=SingletonMeta):
    def __init__(self, instance_id = None):
        if instance_id:
            self.instance_id = instance_id
        print(f"Created a {instance_id} instance of `Singleton`")

    def where_points(self, object_name):
        print(f"Object `{object_name}` points to the {self.instance_id} instance")

s_A = Singleton("first")
s_A.where_points("s_A")

# Created a first instance of `Singleton`
# Object `s_A` points to the first instance

s_B = Singleton("second")
s_B.where_points("s_B")

# Object `s_B` points to the first instance

Singleton().destroy_singleton()

s_C = Singleton("second")
s_C.where_points("s_C")

# Created a second instance of `Singleton`
# Object `s_C` points to the second instance
```

### Merging singleton classes

If a singleton class is merged with other classes using `mergeclasses`, the
merged class "inherits" the singleteness property. For instance, class
"Singleton" from the above example can be extended with class "T" as shown
below:

``` py
from dyndesign import SingletonMeta, mergeclasses

...

class T:
    def who_am_i(self):
        print(f"I am the {self.instance_id} instance")

SingletonMerged = mergeclasses(Singleton, T)
sm_A = SingletonMerged("first")
sm_A.who_am_i()

# I am the first instance

sm_B = SingletonMerged()
sm_B.who_am_i()

# I am the first instance
```

<br/>

## importclass

Classes can be imported dynamically using either the package/class names or the path in
dot notation.

### Syntax

``` py
Class = importclass("path", "ClassName")
```

**Arguments:**

- **path**: str  
    If no class name is passed as the second argument, `path` is the path (in
    dot notation) to a class of a target package. Otherwise, if a class name is
    provided, `path` selects the package only, and the class name passed is
    used to select the class in the package.<br/><br/>

- **ClassName**: str (*Optional*)  
    Class name to import.<br/><br/>

- ***return***: type (*Class*)  
    Imported class.<br/>


### Basic Example

Assuming that `ClassA` is in `package_A` and `ClassB` is in
`directory_B.package_B`, said classes can be imported as shown below:

``` py
from dyndesign import importclass

ClassA = importclass('package_A', 'ClassA')
ClassB = importclass('directory_B.package_B.ClassB')
```

<br/>
