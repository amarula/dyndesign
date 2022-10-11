from dyndee.dyn_loader import DynLoader

TEST_CLASS_1_MODULE = 'tests.sample_classes'
TEST_CLASS_1_NAME = 'A'
TEST_CLASS_2_MODULE = 'tests.DummyClass'
TEST_CLASS_2_NAME = 'DummyClass'


def test_import_class_1():
    """A test class #1 is dynamically imported from a module."""
    class_1 = DynLoader.import_class(TEST_CLASS_1_MODULE, TEST_CLASS_1_NAME)
    assert class_1.__name__ == TEST_CLASS_1_NAME, "Error importing class #1"


def test_import_class_2():
    """A test class #2 is dynamically imported from a module with the same name of the class."""
    class_2 = DynLoader.import_class(TEST_CLASS_2_MODULE)
    assert class_2.__name__ == TEST_CLASS_2_NAME, "Error importing class #2"
