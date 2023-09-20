from dataclasses import dataclass
from typing import Dict, Optional, Type, Tuple, Union

from .class_importer import TypeClassOrPath

__all__ = ["ClassConfig", "LocalClassConfig"]


@dataclass
class BaseConfig:
    """
    The base configuration class that includes settings shared by both global and class configurations.
    """
    default_class: Optional[Type] = None
    component_attr: str = None  # type: ignore
    injection_method: Optional[str] = None
    add_components_after_method: Optional[bool] = None
    force_add: Optional[bool] = None
    structured_component_type: Optional[Type] = None
    structured_component_key: Optional[str] = None
    init_args_from_option: Optional[bool] = None
    init_args_from_self: Union[Tuple[str, ...], str, None] = None
    init_kwargs_from_self: Optional[Dict] = None
    init_args_keep_first: Optional[int] = None
    strict_missing_args: Optional[bool] = None


@dataclass
class LocalClassConfig(BaseConfig):
    """
    The configuration class that developers can utilize to set the global configuration applied when building a class.
    """
    build_recursively: Optional[bool] = None
    class_builder_base_dir: Optional[str] = None
    option_order: Optional[Tuple[str, ...]] = None


@dataclass
class ClassConfig(BaseConfig):
    """
    The configuration class that developers can utilize to set the configuration of the class dependencies applied
    when a specific option is enabled.
    """
    inherit_from: Union[Tuple[TypeClassOrPath, ...], TypeClassOrPath, None] = None
    component_class: Optional[TypeClassOrPath] = None
