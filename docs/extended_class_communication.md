#  Extended Communication Between Classes

To complement the flexibility offered by the Dynamic Class Design tools, an
additional set of tools is required to **safely extend communication between
classes that may or may not be interconnected**.

For example, classes may be
interconnected through:
- (dynamic) inheritance form a hierarchical relationship;
- composition, where one class contains an instance of another class as a
  component or part of its implementation; or
- merging, where two or more classes are merged to create a new class using
  `mergeclasses`.

Considering the optional nature of the interconnect types, the communication
mechanism is designed to handle cases where a class may be not (yet)
interconnected, suppressing any "missing" exceptions that may occur.

## decoratewith

Meta decorator `decoratewith` can be used to decorate a class method with one or
more chained decorators from other interconnected classes. If any decorator is
not found at runtime, no exception is raised and the class method is executed.
Additionally, the syntax of the dynamic decorators aims to get rid of the
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
    in chain. All the decorator methods are executed as they were nested one
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

### Decorators from superclasses dynamically added

Arguments of `decoratewith` are loaded at runtime as properties of the variable
`self`, enabling dynamic decorators to be implemented using a method from a
parent class dynamically added, which is not possible with static decorators.

``` py
from dyndesign import decoratewith, DynInheritance

class Parent:
    def decorator(self, func):
        print("Beginning of method decoration from Parent.")
        func(self)
        print("End of method decoration from Parent.")

class Child(DynInheritance):
    @decoratewith("decorator")
    def mtd(self):
        print(f"Method `m` of class `Child`")

child = Child()
child.mtd()

# Method `m` of class `Child`

Child.dynparents_add(Parent)
child.mtd()

# Beginning of method decoration from Parent.
# Method `m` of class `Child`
# End of method decoration from Parent.
```
In the provided code snippet, the method "mtd" is initially called on the
"child" instance before it inherits from the "Parent" class. As a result, the
decoration with the "decorator" is silently skipped. In contrast, once the
"Parent" class is added as a superclass, the "mtd" method is decorated with the
"decorator".

### Chain of dynamic decorators

Multiple dynamic decorators are chained as the following:

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

### Decorators from merged classes

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
chain, as if they had different names. In the above example, passing
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

- **args** (*Optional*)  
    Positional arguments passed to "method_name".<br/><br/>

- **fallback**: Callable (*Optional*)  
    If "method_name" does not exists at runtime, then a "fallback" function is
    called with the same arguments passed to "method_name".<br/><br/>

- **kwargs** (*Optional*)  
    Keyword arguments passed to "method_name".<br/><br/>

- ***return*** (*Optional*)  
    Value optionally returned by "method_name" if "method_name" exists at
    runtime, `None` otherwise.<br/>


### Basic Example

Method "m" of class "Base" of the example in [Safe zone for
methods](#safe-zone-for-methods) can be rewritten using `safeinvoke`:

``` py
from dyndesign import safeinvoke

...

def m(self, class_desc):
    print(f"Method `m` of {class_desc}")
    safeinvoke("optional_method", self, fallback=self.fallback)
```

<br/>

## safesuper

When dynamic inheritance is utilized, the usage of the `super` builtin
function in a temporarily non-inheriting class might result in exceptions. To
prevent such exceptions, the alternative option of employing the `safesuper`
method can be utilized.

### Syntax

``` py
super_object = self.safesuper(
    type=None,
    object_or_type=None,
    mocked_attrs=("mocked_attr_1", "mocked_attr_2", ...),
    mocked_methods=("mocked_method_1", "mocked_method_2", ...)
)
```

**Arguments:**

- **type**: type (*Optional*)  
    Class optionally passed as first argument to `super` builtin function.
    <br/><br/>

- **object_or_type**: type or object (*Optional*)  
    Object or class optionally passed as second argument to `super` builtin
    function. <br/><br/>

- **mocked_attrs**: Tuple of str (*Optional*)  
    Attribute names that are mocked in case that the corresponding attributes
    are missing in the superclasses. <br/><br/>

- **mocked_methods**: Tuple of str (*Optional*)  
    Method names that are mocked in case that the corresponding attributes are
    missing in the superclasses. <br/><br/>

- ***return*** (*Optional*)  
    *super* proxy object returned by `super` builtin function if the requested
    superclasses are included in the superclass set, otherwise an object mocked
    with the `mocked_attrs`/`mocked_methods` if those attributes/methods are
    missing in the superclass set, otherwise `None`.<br/>


### Basic Example

Method `safesuper` must replace `super` function when a class, that is not yet
included in the superclass set, is to be passed as first argument of `super`:

``` py
from dyndesign import DynInheritance

class A:
    def __init__(self):
        print("Constructor of Class `A`")

class B:
    def __init__(self):
        print("Constructor of Class `B`")

class C(DynInheritance):
    def __init__(self):
        super().__init__()
        self.safesuper(A, self).__init__()
        # `super(A, self).__init__()` --> TypeError
        # because `C` does not inherit from `A` yet, at its first instantiation.
        print("Constructor of Class `C`")

C()

# Constructor of Class `A`

C.dynparents_add(A, B)
C()

# Constructor of Class `A`
# Constructor of Class `B`
# Constructor of Class `C`
```

<br/>

### Mocking methods

If a class is not yet included in the superclass set and the class methods have
to be accessed from the future child class, those methods can be mocked so as to
prevent `AttributeError` exceptions:

``` py
from dyndesign import DynInheritance

class A:
    def mtd(self):
        print("Method `mtd` of Class `A`")

class B(DynInheritance):
    def mtd(self):
        self.safesuper(mocked_methods=("mtd",)).mtd()
        print("Method `mtd` of Class `B`")

B().mtd()

# Method `mtd` of Class `B`

B.dynparents_add(A)
B().mtd()

# Method `mtd` of Class `A`
# Method `mtd` of Class `B`
```

<br/>
