class ErrorClassNotFoundInModules(Exception):
    """Raised when a class cannot be found in any module.
    """


class ErrorMethodNotFound(Exception):
    """Raised when a dynamic method cannot be found.
    """


class BuildConfigWithoutOptions(Exception):
    """Raised when a `buildconfig` is called without options.
    """


class ClassConfigMissingDependency(Exception):
    """Raised when a `ClassConfig` node lacks either a `component_class` or an `inherit_from` field.
    """


class ClassConfigDependencyOverflow(Exception):
    """Raised when a `ClassConfig` node includes both the `component_class` and `inherit_from` fields.
    """


class ClassConfigMissingComponentAttr(Exception):
    """Raised when a `ClassConfig` node of a component class lacks the `component_attr` field.
    """


class ClassConfigMissingComponentInjectionMethod(Exception):
    """Raised when a `ClassConfig` node of a component class lacks the method specified in the
    `injection_method` field.
    """


class DynConfigSetOptionWrongContext(Exception):
    """Raised when `dynconfig.set_configuration` is used from outside the context of a configuration class.
    """


class DynConfigWrongClassType(Exception):
    """Raised when a class passed to `@dynconfig` decorator is neither a class nor a string (to be interpreted as a path
    to a class in dot notation).
    """
