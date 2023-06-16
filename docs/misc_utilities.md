# Misc Utilities

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
    classes are destroyed.<br/>


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
