DynDesign
=========

|Build Status| |PyPi Version Status| |Python Version Status| |License|

A set of tools for Dynamic Design in Python.


Documentation
-------------

DynDesign's full documentation can be found at
https://dyndesign.readthedocs.io/en/latest/


Install
-------

Dyndesign is on the Python Package Index (PyPI):

::

    pip install dyndesign


Overview
--------
Dyndesign is a toolkit that gives developers the ultimate flexibility in
dynamically designing class structures.

Here is an overview of DynDesign's tools.

* Dynamically build a class by adding parent and component classes to a Base class,
  based on selected Building Options:

.. code:: python

    from dyndesign import buildclass, dynconfig

    class Parent:
        ...

    class Component:
        ...

    @dynconfig({
        "OptionA": ClassConfig(inherit_from=Parent),
        "OptionB": ClassConfig(component_attr="comp", component_class=Component),
    })
    class Base:
        ...

    BuiltClass = buildclass(Base, OptionA=True, OptionB=True)
    b = BuiltClass()
    b.method_of_parent()
    b.comp.method_of_component()

* Dynamically add parent classes to a class:

.. code:: python

    from dyndesign import DynInheritance

    class Parent1:
        ...

    class Child(DynInheritance):
        ...

    Child.dynparents_add(Parent1)
    c = Child()
    c.method_of_parent1()

* Merge two or more classes:

.. code:: python

    from dyndesign import mergeclasses

    class Base:
        ...

    class Ext1:
        ...

    MergedClass = mergeclasses(Base, Ext1)
    m = MergedClass()
    m.method_of_Ext1()

* Decorate a method with one or more instance methods loaded at runtime:

.. code:: python

    from dyndesign import decoratewith

    @decoratewith("decorator_1", "component.decorator_2", ...)
    def decorated_method(self, ...):
        ...

* Safely invoke functions or methods from a ``safezone`` context manager or by
  using the ``safeinvoke`` API:

.. code:: python

    from dyndesign import safezone, safeinvoke

    with safezone():
        ...
        function_possibly_non_existent()

    ...

    def method(self):
        safeinvoke("method_possibly_non_existent", self)

* Create and destroy Singleton classes:

.. code:: python

    from dyndesign import SingletonMeta

    class Singleton(metaclass=SingletonMeta):
        ...

    singleton_instance = Singleton(...)
    same_singleton_instance = Singleton()
    Singleton().destroy_singleton()
    new_singleton_instance = Singleton(...)

* Import classes dynamically using the path:

.. code:: python

    from dyndesign import importclass

    ImportedClass = importclass("directory.module.class_name")


Class Builder
-------------

Class Builder is a powerful new tool from DynDesign that makes it easy to build
classes by configuring existing classes with selected options.

Building classes involves incorporating one or more Class Dependencies, including
**parent classes** and **component classes**. This can be achieved using two
essential tools: the ``dynconfig`` decorator, which allows the base class to be
configured with potential dependencies, and the ``buildclass`` function, which
builds new classes by seamlessly integrating selected class dependencies using a
specified set of building options.

Below is an example of building a class that optionally inherits from classes A
and B.

.. code:: python

    from dyndesign import buildclass, dynconfig, ClassConfig

    class A:
        def __init__(self):
            print("Inheriting from `A`")

    class B:
        def __init__(self):
            print("Inheriting from `B`")


    @dynconfig({
        "OptionA": ClassConfig(inherit_from=A),
        "OptionB": ClassConfig(inherit_from=B),
    })
    class Base:
        ...


    Built = buildclass(Base, OptionA=True)
    Built()
    # Inheriting from `A`

    Built = buildclass(Base, OptionB=True)
    Built()
    # Inheriting from `B`

Classes can be configured to enable the injection of component classes into
specific methods (or into the default ``__init__`` method).

.. code:: python

    from dyndesign import buildclass, dynconfig, ClassConfig

    class A:
        def whoami(self):
            print("Using component `A`")

    class Default:
        def whoami(self):
            print("Using component `Default`")

    class Configurator:
        OptionA = ClassConfig(
            component_class=A,
            component_attr="comp",
            default_class=Default
        )

    @dynconfig(Configurator)
    class Base:
        def __init__(self):
            self.comp.whoami()


    Built = buildclass(Base, OptionA=True)
    Built()
    # Using component `A`

    Built = buildclass(Base, OptionA=False)
    Built()
    # Using component `Default`

Another important point demonstrated in the example is that class configuration
can be encapsulated in a Configurator class. This helps to **separate** the code
that is responsible for **class configuration from the core logic** of the
classes.

Dynamic Inheritance
-------------------

With Dynamic Inheritance, it becomes possible to dynamically modify the
superclass set of classes that inherit from special class ``DynInheritance``. This
allows the addition of parent classes to those classes, and the modification is
also instantly reflected in all their instances.

.. code:: python

    from dyndesign import DynInheritance

    class Parent:
        def m1(self):
            print("Method `m1` from `Parent`")

    class Child(DynInheritance):
        def __init__(self):
            print("Constructor of `Child`")

    child_instance = Child()

    # Constructor of `Child`

    Child.dynparents_add(Parent)
    child_instance.m1()

    # Method `m1` from `Parent`

When the special class ``DynInheritanceLockedInstances`` is utilized instead of
``DynInheritance``, the superclass set is locked within each class instance,
meaning that it remains unchanged even when there are modifications to the
class's superclasses.

.. code:: python

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

Class Merging
-------------

Dyndesign provides API ``mergeclasses`` to merge two or more classes as if they
were dictionaries. As a result, the newly created class has the same properties
from both its base class and any added extensions. If two or more classes have
the same attributes/methods, the attributes/methods from the rightmost classes
(in the order in which the classes are passed to ``mergeclasses``) overload the
ones from the leftmost classes, similarly to what happens when merging
dictionaries.

.. code:: python

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


When a merged class is instantiated with arguments, the constructor of each
merging class is invoked, since constructors are excluded from being overloaded.
Also, arguments passed to each constructor are adaptively filtered based on the
constructor signature so that each constructor takes just the arguments it
requires, and no exception is raised for exceeding arguments passed:

.. code:: python

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

On the other hand, if any required positional argument is missing, an exception
is raised. If ``MergedClass`` of the above example is initialized with no
parameters, and exception is raised when the constructor of class ``B`` is
called:

.. code:: python

    ...
    MergedClass()

    # ...
    # TypeError: B.__init__() missing 1 required positional argument: 'a'

So as to have constructor instances with missing positional arguments silently
skipped, ``strict_merged_args`` can be set to False in ``mergeclasses``. In the
above example, constructors of class ``B`` and ``C`` are skipped:

.. code:: python

    ...
    MergedClass = mergeclasses(A, B, C, D, strict_merged_args=False)
    MergedClass()

    # No argument passed to class `A`
    # Argument kw2=None passed to class `D`


It is also possible to extend the same behavior of the constructor ``__init__``
(i.e., all the methods from all the merged classes are invoked rather than being
overloaded by the same name method from the rightmost class) to other methods. A
list of method names whose instances must be all invoked can be specified in
the ``invoke_all`` argument of ``mergeclasses``. Adaptive filtering of the
arguments of the method instances is performed as well.

.. code:: python

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


Dynamic Decorators
------------------

Meta decorator ``decoratewith`` can be used to decorate a class method with one
or more chained dynamic decorators, regardless whether they statically exist
or not. Additionally, the syntax of the dynamic decorators aims to get rid of
the boilerplate for wrapping and returning the decorator code, leaving just the
wrapper's code. For example, dynamic decorators can be used to decorate a method
of a base class with a method of an extension class:

.. code:: python

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

If a decorator name is passed in the ``invoke_all`` argument of
``mergeclasses``, then multiple decorator instances with the same name from
different extension classes may be used in chain:

.. code:: python

    class Ext2:
        def decorator(self, func):
            print("Beginning of method decoration from Ext2.")
            func(self)
            print("End of method decoration from Ext2.")

    merged = mergeclasses(Base, Ext, Ext2, invoke_all=["decorator"])()
    merged.m()

    # Beginning of method decoration from Ext.
    # Beginning of method decoration from Ext2.
    # Method `m` of class `Base`
    # End of method decoration from Ext2.
    # End of method decoration from Ext.


Arguments of ``decoratewith`` are loaded at runtime as properties of the
variable 'self': a dynamic decorator can be, for example, a method of a
component class. In case of dynamic decoration from a sub-instance of 'self',
the instance object of the decorated method is passed to the decorator as the
argument ``decorated_self``. If a dynamic decorator is not found at runtime
(e.g., because it is a method of an optional class that has not been merged),
then the code execution proceeds normally, as shown below with the decorator
``non_existent_decorator``:

.. code:: python

    class Base:
        def __init__(self):
            self.comp = Component()

        @decoratewith("comp.decorator1", "comp.decorator2", "non_existent_decorator")
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


Safezone Context Manager
------------------------

Any function or method that may or may not exist at runtime (e.g., methods of
merged classes) can be invoked from Context Manager ``safezone`` in order to
suppress the possible exceptions raised if the function or method is not found
at runtime. Optionally, a fallback function/method can be also passed. If no
function name(s) is passed as argument of ``safezone``, then each function in
the safe zone's code is protected; if any function name(s) is passed, the
protection is restricted to the functions having that/those name(s). For
example, ``safezone`` can be used to safely call functions that may or may not
exist at runtime:

.. code:: python

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


A further example shows that ``safezone`` can be used to safely invoke methods
of classes that may or may not be merged with other classes:

.. code:: python

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
    base = Base()
    base.m("class `Base` standalone")

    # Method `m` of merged class
    # Optional method from class `ExtOptional`
    # Method `m` of class `Base` standalone
    # Fallback method


Invoking methods safely
-----------------------

As an alternative to ``safezone`` context manager, ``safeinvoke`` API can be
used to safely invoke methods that may or may not exist at runtime. To this end,
method ``m`` of class ``Base`` of the example above can be replaced as follows:

.. code:: python

    from dyndesign import safeinvoke

    ...

        def m(self, class_desc):
            print(f"Method `m` of {class_desc}")
            safeinvoke("optional_method", self, fallback=self.fallback)


Singleton classes
-----------------

Singleton classes can be swiftly created with `SingletonMeta` metaclass and then
destroyed with `destroy_singleton`:

.. code:: python

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

The class method ``destroy`` of SingletonMeta can be invoked to destroy all the
Singleton classes at once. As a further alternative to the instance call
``destroy_singleton``, the names of the Singleton classes to destroy can be
passed to the class method ``destroy``:

.. code:: python

    Singleton().destroy_singleton() # Destroy only `Singleton`
    SingletonMeta.destroy() # Destroy all the singleton classes
    SingletonMeta.destroy('Singleton1', 'Singleton2', 'Singleton3') # Destroy selectively


Importing classes dynamically
-----------------------------

Classes can be imported dynamically using the package/class names or the path in
dot-notation as shown below:

.. code:: python

    from dyndesign import importclass

    ClassA = importclass('package_A', 'ClassA')
    ClassB = importclass('directory_B.package_B.ClassB')


Running tests
-------------

To run the tests using your default python interpreter:

::

    pip install -U pytest
    python -m pytest test


.. |Build Status| image:: https://github.com/amarula/dyndesign/actions/workflows/python-app.yml/badge.svg
    :target: https://github.com/amarula/dyndesign/actions
.. |Python Version Status| image:: https://img.shields.io/badge/python-3.8_3.9_3.10_3.11-blue.svg
    :target: https://github.com/amarula/dyndesign/actions
.. |PyPi Version Status| image:: https://badge.fury.io/py/dyndesign.svg
    :target: https://badge.fury.io/py/dyndesign
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
