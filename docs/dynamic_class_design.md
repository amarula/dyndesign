# Dynamic Class Design

Dynamic Class Design is a powerful package that offers developers two essential
features for flexible and dynamic class manipulation: dynamic inheritance and
class merging. With these capabilities, developers gain unprecedented control
over the structure and behavior of their classes, enabling them to adapt and
evolve their software systems with ease.

Python developers now have the ability to **dynamically change the superclass
set** of a class at runtime. Most importantly, developers have the choice to
determine whether class instances should be **live-updated** with the changes
made to the superclass set of the class or **locked** to the superclasses they
had at the time of instantiation. This flexibility allows developers to tailor
the behavior of class instances based on their specific requirements.

## Dynamic Inheritance with live-updating instances

By opting for live-updates, **class instances will dynamically reflect any
modifications to the superclass set**, providing a dynamic and adaptable runtime
environment.

To enable dynamic inheritance for a class, it is necessary for the class to
inherit from the special class `DynInheritance`. This special class provides a
set of methods that allow the modification of the superclass set in the
inheriting class.

### Syntax

``` py
class Child(DynInheritance):
    ...

Child.dynparents_add(Parent1, Parent2, ...)
Child.dynparents_replace(Parent1, Parent2, ...)
Child.dynparents_remove(Parent_to_remove_1, Parent_to_remove_2, ...)
Child.dynparents_restore()

# or, alternatively
Child.dynparents_add("path.to.Parent1", "path.to.Parent2", ...)
...
```
Parent classes can be dynamically added to the superclass set of a Child class
in two ways. Firstly, they can be directly passed as arguments to the
`dynparents_add` method inherited from `DynInheritance` special class.
Alternatively, the paths to the parent classes can be provided in dot notation
format, as described in the [importclass](misc_utilities#importclass) utility
documentation. In this case, the classes are imported and then appended to the
superclass set of the Child class.

Similarly, the superclass set of a Child class can be completely replaced by one
or more parent classes provided as arguments to the `dynparents_replace` method.

The `dynparents_remove` method can be utilized to remove one or more
superclasses from the superclass set the Child class to allow developers to
selectively eliminate specific superclass dependencies.

Lastly, the `dynparents_restore` method provides the capability to restore the
initial superclass set of the Child class as it existed before any
DynInheritance operations were performed. This can be useful when there is a
need to revert back to the original class structure and discard any
modifications made through dynamic inheritance.

### Basic Examples

A parent class "Parent" can be dynamically added to "Child" using the
`dynparents_add` method:

``` py
from dyndesign import DynInheritance

class Parent:
    def __init__(self):
        print("Constructor of `Parent`")

class Child(DynInheritance):
    def __init__(self):
        super().__init__()
        print("Constructor of `Child`")

Child()

# Constructor of `Child`

Child.dynparents_add(Parent)
Child()

# Constructor of `Parent`
# Constructor of `Child`
```

Dually, "Parent" can be dynamically removed from "Child" using the
`dynparents_remove` method:

``` py
...
Child.dynparents_remove(Parent)
Child()

# Constructor of `Child`
```

In another scenario, a superclass "A" of class "C" can be replaced with "B"
after the instantiation of the "c_instance":

``` py
from dyndesign import DynInheritance

class A:
    def mtd(self):
        print("Method `mtd` of Class `A`")

class B:
    def mtd(self):
        print("Method `mtd` of Class `B`")

class C(DynInheritance, A):
    def mtd(self):
        super().mtd()
        print("Method `mtd` of Class `C`")

c_instance = C()
c_instance.mtd()

# Method `mtd` of Class `A`
# Method `mtd` of Class `C`

C.dynparents_replace(B)
c_instance.mtd()

# Method `mtd` of Class `B`
# Method `mtd` of Class `C`
```

This example demonstrates how such a change in the superclass set dynamically
affects the existing instances of the class: after the superclass replacement,
the "c_instance" and any other existing instances of class "C" reflects the
updated superclass set.

Finally, the initial superclass set of "C" can be restored using the
`dynparents_restore` method:

``` py
...
C.dynparents_restore()
c_instance.mtd()

# Method `mtd` of Class `A`
# Method `mtd` of Class `C`
```

### Self-modifying instances

Superclass set of a Dynamically Inheriting class can be also self-modified from
an instance of the class itself:

``` py
from dyndesign import DynInheritance

class Parent:
    def mtd(self):
        print("Method `mtd` of `Parent`")

class Child(DynInheritance):
    def mtd(self):
        super().mtd()
        print("Method `mtd` of `Child`")

    def self_add_A(self):
        self.dynparents_add(Parent)

child_instance = Child()
child_instance.self_add_A()
child_instance.mtd()

# Method `mtd` of `Parent`
# Method `mtd` of `Child`
```

It is worth noting that, although performed within a "Child" instance, this
change also affects the "Child" class and all its other instances, if any.

### Safely access to superclasses from the class

In certain situations, there may arise a need to use a class that is not
currently included in the superclass set as an argument of the `super` function,
which can lead to a runtime exception. For instance, using `super(A, self)`
inside class "B" before that "B" inherits from "A" would result in a
"TypeError".

To safely access superclass's resources, the
[safesuper](extended_class_communication#safesuper) method can be used instead
of `super`.

## Dynamic Inheritance with locked instances

By choosing to lock the class instances to their initial superclass set,
developers ensure consistency and stability in the behavior and characteristics
of the instances. This approach **preserves the state of the instances as they are
initially instantiated** and prevents any unintended changes that might occur due
to dynamic modifications to the superclass set.

It is also possible to retain both the original class and the class updated with
the modified superclass set is by assigning a new name to the updated class.
This approach allows developers to have both versions coexist in the codebase,
providing additional flexibility and compatibility.

The special class that enables classes to have dynamic inheritance with locked
instances is `DynInheritanceLockedInstances`.

### Syntax

``` py
class Child(DynInheritanceLockedInstances):
    ...

Child.dynparents_add(
    Parent1, Parent2, ...,
    rename_to="New Name"
)
Child.dynparents_replace(
    Parent1, Parent2, ...,
    rename_to="New Name"
)
Child.dynparents_remove(
    Parent_to_remove_1, Parent_to_remove_2, ...,
    rename_to="New Name"
)
Child.dynparents_restore()
```

**Arguments:**

- **Parent1**, **Parent2**, ...: type (*Class*) *or* str  
    One or more parent classes that are used to update the superclass set in the
    instances of the "Child" class that will be instantiated thereafter. Parent
    classes can be either passed directly, or alternatively as paths to the
    classes in dot notation. <br/><br/>

- **rename_to**: str (*Optional*)  
    New name for the class with updated superclass set.<br/>


### Basic Example

In the following example, even after the class "Parent" is added to the class
"Child", instance "orphan_child" remains without any parent classes.

``` py
from dyndesign import DynInheritanceLockedInstances

class Parent:
    def __init__(self):
        print("Constructor of `Parent`")

    def mtd(self):
        print("Method `mtd` of `Parent`")

class Child(DynInheritanceLockedInstances):
    def __init__(self):
        super(DynInheritanceLockedInstances, self).__init__()
        print("Constructor of `Child`")

orphan_child = Child()

# Constructor of `Child`

Child.dynparents_add(Parent)
child_with_parent = Child()

# Constructor of `Parent`
# Constructor of `Child`

child_with_parent.mtd()

# Method `mtd` of `Parent`

orphan_child.mtd()

# AttributeError: 'Child' object has no attribute 'mtd'
```

**Note:** When utilizing dynamic inheritance with locked instances, invoking the
`super` function without any arguments may result in a TypeError exception. To
avoid this, it is recommended to use `super(DynInheritanceLockedInstances,
self)` instead, as shown in the above example. An alternative is to utilize the
[safesuper](extended_class_communication#safesuper) method inherited from
`DynInheritanceLockedInstances` by invoking it as

``` py
self.safesuper()
```

### Assigning a new name to the class

In this example, the class "Child" is given a new name, "ChildWithParent", when
the parent class "Parent" is added. This approach allows for the simultaneous
use of both the "Child" class (without parents) and the "ChildWithParent" class:

``` py
from dyndesign import DynInheritanceLockedInstances, safeinvoke

class Parent:
    def parent_method(self):
        print("Method `parent_method`")

class Child(DynInheritanceLockedInstances):
    def child_method(self):
        safeinvoke("parent_method",  self)
        print("Method `child_method`")

Child.dynparents_add(Parent, rename_to="ChildWithParent")
orphan = Child()
child_with_parent = ChildWithParent()

orphan.child_method()

# Method `child_method`

child_with_parent.child_method()

# Method `parent_method`
# Method `child_method`
```

It is important to highlight that in this example, the method "parent_method"
can be securely accessed from the "child_method" by utilizing the
[safeinvoke](extended_class_communication#safeinvoke) function. As an
alternative approach, the method "parent_method" could have been chained to a
`safesuper` call, where the method is mocked as shown in [this
example](extended_class_communication#mocking-methods).

## Class Merging

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
    classes. Class "Base" can be either directly passed as the first argument,
    or alternatively a path to the class in dot notation can be
    provided.<br/><br/>

- **Ext1**, **Ext2**, ...: type (*Class*) *or* str  
    One or more extension classes to extend the properties of the base class.
    <br/><br/>

- **invoke_all**: List of str (*Optional*)  
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
outlined in the [importclass](misc_utilities#importclass) documentation.
Additionally, it is shown that merged classes can be merged in turn with other
classes. Assuming that a package "directory/extensions.py" includes class "Ext2"
(defined analogously to "Ext"), the following lines can be appended to the
example above:

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
when it is not found, [safeinvoke](extended_class_communication#safeinvoke) can
be used in "ChildB.method_1":

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
