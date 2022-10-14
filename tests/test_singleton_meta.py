from .sample_singletons import A
from .testing_results import SingletonsResults as sr


def test_use_singleton():
    """Singleton class `A` is instantiated two times, and both the times the same instance is returned."""
    A(sr.CLASS_A__P1)
    instance_A = A()
    assert instance_A.param1 == sr.CLASS_A__P1, "Error instantiating singleton `A`"


def test_destroy_singleton():
    """Singleton class `A` is correctly destroyed."""
    A(sr.CLASS_A__P1)
    A.destroy()
    instance_A = A()
    assert 'param1' not in dir(instance_A), "Error destroying singleton `A`"
