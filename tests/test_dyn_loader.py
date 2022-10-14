from dyndesign.dynloader import importclass


def test_import_class_with_module_and_class():
    """Test class `A` is dynamically imported from a module."""
    class_1 = importclass('tests.sample_classes', 'A')
    assert class_1.__name__ == 'A', "Error importing class `A`"


def test_import_class_with_class_path():
    """Test class `C` is dynamically imported from a module with the same name of the class."""
    class_2 = importclass('tests.sample_classes_imported.C')
    assert class_2.__name__ == 'C', "Error importing class `C`"
