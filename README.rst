DynDesign
=========

A set of tools to dynamically design patterns in Python.


Install
-------

Dyndesign is on the Python Package Index (PyPI):

::

    pip install dyndesign


Overview
--------

Merge two or more classes:

.. code:: python

    from dyndesign import mergeclasses

    MergedClass = mergeclasses(Base, Ext1, Ext2, ...)

Decorate a method easily with one or more instance methods:

.. code:: python

    from dyndesign import decoratewith

    @decoratewith("decorator_1", "component.decorator_2", ...)
    def decorated_method(self, ...):
        ...

Safely invoke functions or methods from the Context Manager ``safezone``:

.. code:: python

    from dyndesign import safezone

    with safezone():
        ...
        function_possibly_non_existent()
        ...

Create and destroy Singleton classes

.. code:: python

    from dyndesign import SingletonMeta

    class Singleton(metaclass=SingletonMeta):
        ...

    singleton_instance = Singleton(...)
    same_singleton_instance = Singleton()
    Singleton.destroy()
    new_singleton_instance = Singleton(...)

Import classes dynamically using the path:

.. code:: python

    from dyndesign import importclass

    ImportedClass = importclass("directory.module.class_name")


Merging Classes
---------------

Dyndesign provides API ``mergeclasses`` to merge two or more classes as if they
were dictionaries, so that the merged class has the attributes and methods of
the base class and of the extension classes. If two or more classes have the
same attributes/methods, the attributes/methods of the rightmost classes (in the
order in which they are passed to ``mergeclasses``) overwrite the leftmost,
similarly to what happens when merging dictionaries.

.. code:: python

    from dyndesign import mergeclasses

    class Base:
        def __init__(self, init_value):
            self.param = init_value

        def m1(self):
            print(f"I'm method `m1` of class `Base`, and {self.param=}")

        def m2(self):
            print(f"I'm method `m2` of class `Base`")

    class Ext:
        def m1(self):
            print(f"I'm method `m1` of class `Ext`, and {self.param=}")

    MergedClass = mergeclasses(Base, Ext)
    merged_instance = MergedClass("INITIAL VALUE")
    merged_instance.m1()
    merged_instance.m2()

    # I'm method `m1` of class `Ext`, and self.param='INITIAL VALUE'
    # I'm method `m2` of class `Base`


When a merged class is instantiated with arguments, the constructor of each
merging class takes just the arguments it needs (i.e., the arguments in its
signature):

.. code:: python

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


Dynamic Decorators
------------------

Meta decorator ``decoratewith`` decorates a class method with one or more
pipelined instance decorators (regardless whether they statically exist or not).
The syntax of the dynamic decorators aims to get rid of the boilerplate for
wrapping and returning the decorator code, leaving just the wrapper's code. For
example, dynamic decorators can be used to decorate a method from a base
class with a method from an extension class:

.. code:: python

    from dyndesign import decoratewith

    class Base:
        @decoratewith("decorator")
        def m(self):
            print(f"I'm method `m` of class `Base`")

    class Ext:
        def decorator(self, func):
            print("Beginning of method decoration.")
            func(self)
            print("End of method decoration.")

    merged = mergeclasses(Base, Ext)()
    merged.m()

    # Beginning of method decoration.
    # I'm method `m` of class `Base`
    # End of method decoration.


Arguments of ``decoratewith`` are evaluated at runtime as properties of the
variable 'self': a dynamic decorator can be, for example, a method of a
component class. In case of dynamic decoration from a sub-instance of 'self',
the instance object of the decorated method is passed to the decorator as the
argument ``decorated_self``, as shown below:

.. code:: python

    from dyndesign import decoratewith

    class Base:
        def __init__(self):
            self.comp = Component()

        @decoratewith("comp.decorator1", "comp.decorator2")
        def m(self):
            print("I'm method `m` of class `Base`")

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
    # I'm method `m` of class `Base`
    # End of method decoration #2
    # End of method decoration #1


Safezone Context Manager
------------------------

Any function or method that may or may not exist at runtime (e.g., methods of
merged classes) can be invoked from Context Manager ``safezone`` in order to
suppress the possible exceptions raised if the function or method is missing.
Optionally, a fallback function/method can be also passed. If no function
name(s) is passed as argument of ``safezone``, then each function in the safe zone's
code is protected; if any function name(s) is passed, the protection is
restricted to the functions having that/those name(s). For example, ``safezone``
can be used to safely call functions that may or may not be missing:

.. code:: python

    from dyndesign import safezone
    
    def fallback():
        print("I'm the fallback function")

    def function_a():
        print("I'm function `a`")

    with safezone(fallback=fallback):
        function_a()
        non_existent_function()

    # I'm function `a`
    # I'm the fallback function


A further example shows that ``safezone`` can be used to safely invoke methods
of classes that may or may not be merged with other classes:

.. code:: python

    from dyndesign import safezone

    class Base:
        def fallback(self):
            print("I'm the fallback method")

        def m(self, class_desc):
            print(f"I'm method `m` of {class_desc}")
            with safezone("optional_method", fallback=self.fallback):
                self.optional_method()

    class ExtOptional:
        def optional_method(self):
            print("I'm the optional method from class `ExtOptional`")

    merged = mergeclasses(Base, ExtOptional)()
    merged.m("merged class")
    base = Base()
    base.m("class `Base` standalone")

    # I'm method `m` of merged class
    # I'm the optional method from class `ExtOptional`
    # I'm method `m` of class `Base` standalone
    # I'm the fallback method


Invoking methods safely
-----------------------

As alternative to ``safezone`` context manager, ``safeinvoke`` can be used to
safely invoke methods that may or may not be missing. To this end, method ``m``
of class ``Base`` of the example above can be replaced as follows:

.. code:: python

    from dyndesign import safeinvoke

    ...

        def m(self, class_desc):
            print(f"I'm method `m` of {class_desc}")
            safeinvoke("optional_method", self, fallback=self.fallback)


Singleton classes
-----------------

Singleton classes may be swiftly created and destroyed:

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
    s_B = Singleton()
    s_B.where_points("s_B")
    Singleton.destroy()
    s_C = Singleton("second")
    s_C.where_points("s_C")

    # Created a first instance of `Singleton`
    # Object `s_A` points to the first instance
    # Object `s_B` points to the first instance
    # Created a second instance of `Singleton`
    # Object `s_C` points to the second instance


Importing classes dynamically
-----------------------------

Classes can be imported dynamically using the package/class names or the path in
dot-notation as shown below:

.. code:: python

    from dyndesign import importclass

    ClassA = importclass('package_A', 'ClassA')
    ClassB = importclass('directory_B.package_B.ClassB')


Running tests
--------------

To run the tests using your default python:

::

    pip install -U pytest
    python3 -m pytest test
