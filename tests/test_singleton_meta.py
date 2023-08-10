from dyndesign import SingletonMeta
from .samples.sample_singletons import A, B
from .testing_results import SingletonsResults as Sr


def test_use_singleton():
    """Singleton class `A` is instantiated two times, and both the times the same instance is returned."""
    A(Sr.CLASS_A__P1)
    instance_A = A()
    assert instance_A.param1 == Sr.CLASS_A__P1, "Error instantiating singleton `A`"


def test_destroy_all_singletons():
    """All the singleton classes are correctly destroyed."""
    A(Sr.CLASS_A__P1)
    B(Sr.CLASS_B__P1)
    SingletonMeta.destroy()
    instance_A = A()
    instance_B = B()
    assert 'param1' not in dir(instance_A), "Error destroying singleton `A`"
    assert 'param1' not in dir(instance_B), "Error destroying singleton `B`"
    SingletonMeta.destroy()


def test_destroy_specific_singleton():
    """Only singleton class `A` is correctly destroyed, while class `B` is not."""
    A(Sr.CLASS_A__P1)
    B(Sr.CLASS_B__P1)
    A().destroy_singleton()
    instance_B = B()
    assert 'param1' in dir(instance_B), "Error: singleton `B` destroyed"
    SingletonMeta.destroy()


def test_destroy_specific_singleton_alternative():
    """Only singleton class `A` is correctly destroyed, by passing the class name to method `destroy`"""
    A(Sr.CLASS_A__P1)
    B(Sr.CLASS_B__P1)
    SingletonMeta.destroy('A')
    instance_B = B()
    assert 'param1' in dir(instance_B), "Error: singleton `B` destroyed"
    SingletonMeta.destroy()
